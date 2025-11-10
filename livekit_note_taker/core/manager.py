"""
Main NoteManager class - the primary interface for the library.

This module provides the high-level API for managing meeting note-taking sessions,
coordinating between audio capture, transcription, and AI processing.
"""

import asyncio
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime

from livekit_note_taker.core.session import MeetingSession, Participant, SessionStatus
from livekit_note_taker.core.events import EventEmitter, Event, EventType

logger = logging.getLogger(__name__)


class NoteManagerConfig:
    """
    Configuration for the NoteManager.

    Attributes:
        auto_summarize: Enable automatic periodic summarization
        summary_interval_minutes: How often to generate auto-summaries
        buffer_duration_minutes: Audio buffer duration before processing
        max_session_duration_hours: Maximum allowed session duration
        language: Default language code for transcription
        enable_real_time_events: Enable real-time event emissions
    """

    def __init__(
        self,
        auto_summarize: bool = True,
        summary_interval_minutes: int = 15,
        buffer_duration_minutes: int = 15,
        max_session_duration_hours: int = 8,
        language: str = "en-US",
        enable_real_time_events: bool = True,
    ):
        self.auto_summarize = auto_summarize
        self.summary_interval_minutes = summary_interval_minutes
        self.buffer_duration_minutes = buffer_duration_minutes
        self.max_session_duration_hours = max_session_duration_hours
        self.language = language
        self.enable_real_time_events = enable_real_time_events


class NoteManager:
    """
    Main orchestrator for meeting note-taking functionality.

    This class coordinates between:
    - Audio recording and buffering
    - Transcription services
    - AI summarization and action item extraction
    - Storage backends
    - Event emission for real-time updates

    Example:
        from livekit_note_taker import NoteManager
        from livekit_note_taker.audio import AudioRecorder
        from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
        from livekit_note_taker.ai.openai import OpenAIProvider
        from livekit_note_taker.storage.sqlalchemy import SQLAlchemyStorage

        manager = NoteManager(
            audio_recorder=AudioRecorder(livekit_url="ws://localhost:7880"),
            transcription_provider=AWSTranscriptionProvider(),
            ai_provider=OpenAIProvider(api_key="sk-..."),
            storage=SQLAlchemyStorage(database_url="postgresql://..."),
            config=NoteManagerConfig(auto_summarize=True)
        )

        # Start a session
        session = await manager.start_session(
            room_id="my-room",
            title="Team Meeting"
        )

        # Start recording
        await manager.start_recording(session.session_id, started_by="user-123")

        # Stop recording
        await manager.stop_recording(session.session_id)

        # End session
        await manager.end_session(session.session_id)
    """

    def __init__(
        self,
        audio_recorder=None,
        transcription_provider=None,
        ai_provider=None,
        storage=None,
        export_service=None,
        config: Optional[NoteManagerConfig] = None,
        event_emitter: Optional[EventEmitter] = None,
    ):
        """
        Initialize the NoteManager.

        Args:
            audio_recorder: Audio recording implementation (e.g., LiveKitRecorder)
            transcription_provider: Transcription service provider (e.g., AWS, Deepgram)
            ai_provider: AI service for summaries and action items
            storage: Storage backend for persisting data
            export_service: Service for exporting notes to various formats
            config: Configuration options
            event_emitter: Event emitter for real-time updates
        """
        self.audio_recorder = audio_recorder
        self.transcription_provider = transcription_provider
        self.ai_provider = ai_provider
        self.storage = storage
        self.export_service = export_service
        self.config = config or NoteManagerConfig()
        self.event_emitter = event_emitter or EventEmitter()

        # Session tracking
        self.active_sessions: Dict[str, MeetingSession] = {}
        self.session_tasks: Dict[str, List[asyncio.Task]] = {}

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

        logger.info("NoteManager initialized")

    async def start_session(
        self,
        room_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict] = None,
    ) -> MeetingSession:
        """
        Start a new meeting session.

        Args:
            room_id: Unique identifier for the room
            title: Optional meeting title
            description: Optional meeting description
            config: Optional session-specific configuration

        Returns:
            The created MeetingSession

        Raises:
            ValueError: If a session is already active for this room
        """
        async with self._lock:
            if room_id in self.active_sessions:
                # Reactivate existing session if it was completed
                session = self.active_sessions[room_id]
                if session.status == SessionStatus.COMPLETED:
                    session.status = SessionStatus.ACTIVE
                    logger.info(f"Reactivated session for room {room_id}")
                    return session
                else:
                    logger.warning(f"Session already active for room {room_id}")
                    return session

            # Create new session
            session = MeetingSession(
                room_id=room_id,
                title=title,
                description=description,
                config=config or {},
            )
            session.start()

            self.active_sessions[room_id] = session
            self.session_tasks[room_id] = []

            logger.info(f"Started session {session.session_id} for room {room_id}")

            # Emit event
            await self.event_emitter.emit(Event(
                type=EventType.SESSION_STARTED,
                room_id=room_id,
                session_id=session.session_id,
                data={
                    "session_id": session.session_id,
                    "title": title,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ))

            # Start auto-summary task if enabled
            if self.config.auto_summarize:
                task = asyncio.create_task(
                    self._auto_summary_loop(session.session_id)
                )
                self.session_tasks[room_id].append(task)

            # Persist to storage if available
            if self.storage:
                await self.storage.save_session(session)

            return session

    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a meeting session.

        Args:
            session_id: The session ID to end

        Returns:
            Session summary data

        Raises:
            ValueError: If session not found
        """
        session = self._get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        async with self._lock:
            # Stop recording if active
            if session.recording.is_recording:
                await self.stop_recording(session_id)

            # Cancel all background tasks
            if session.room_id in self.session_tasks:
                for task in self.session_tasks[session.room_id]:
                    if not task.done():
                        task.cancel()
                del self.session_tasks[session.room_id]

            # Mark session as completed
            session.end()

            # Generate final summary if AI provider is available
            final_summary = None
            if self.ai_provider and session.transcript_buffer:
                try:
                    final_summary = await self._generate_final_summary(session)
                except Exception as e:
                    logger.error(f"Error generating final summary: {e}")

            # Persist final state
            if self.storage:
                await self.storage.save_session(session)
                if final_summary:
                    await self.storage.save_note(session_id, final_summary)

            logger.info(f"Ended session {session_id} for room {session.room_id}")

            # Emit event
            await self.event_emitter.emit(Event(
                type=EventType.SESSION_ENDED,
                room_id=session.room_id,
                session_id=session_id,
                data={
                    "session_id": session_id,
                    "duration_seconds": session.get_duration(),
                    "stats": session.stats,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ))

            return session.to_dict()

    async def start_recording(self, session_id: str, started_by: str) -> Dict[str, Any]:
        """
        Start recording for a session.

        Args:
            session_id: The session ID to start recording for
            started_by: Participant ID who initiated recording

        Returns:
            Recording status information

        Raises:
            ValueError: If session not found or recording already active
        """
        session = self._get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if session.recording.is_recording:
            raise ValueError("Recording already in progress")

        # Start recording
        session.start_recording(started_by)

        # Initialize audio recorder if available
        if self.audio_recorder:
            await self.audio_recorder.start_recording(
                room_id=session.room_id,
                session_id=session_id,
                config={
                    "language": self.config.language,
                    "buffer_duration_minutes": self.config.buffer_duration_minutes,
                }
            )

        logger.info(f"Started recording for session {session_id}")

        # Emit event
        await self.event_emitter.emit(Event(
            type=EventType.RECORDING_STARTED,
            room_id=session.room_id,
            session_id=session_id,
            data={
                "started_by": started_by,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ))

        return {
            "status": "recording_started",
            "session_id": session_id,
            "started_at": session.recording.started_at.isoformat(),
            "started_by": started_by,
        }

    async def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """
        Stop recording for a session.

        Args:
            session_id: The session ID to stop recording for

        Returns:
            Recording summary information

        Raises:
            ValueError: If session not found or recording not active
        """
        session = self._get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        if not session.recording.is_recording:
            raise ValueError("Recording not active")

        # Stop audio recorder if available
        if self.audio_recorder:
            await self.audio_recorder.stop_recording(session.room_id)

        # Stop recording
        session.stop_recording()

        logger.info(f"Stopped recording for session {session_id}")

        # Emit event
        await self.event_emitter.emit(Event(
            type=EventType.RECORDING_STOPPED,
            room_id=session.room_id,
            session_id=session_id,
            data={
                "duration_seconds": session.recording.duration_seconds,
                "total_batches": session.recording.total_batches_processed,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ))

        return {
            "status": "recording_stopped",
            "session_id": session_id,
            "duration_seconds": session.recording.duration_seconds,
            "total_batches_processed": session.recording.total_batches_processed,
        }

    async def add_participant(
        self,
        session_id: str,
        participant_id: str,
        participant_name: str,
        metadata: Optional[Dict] = None,
    ) -> Participant:
        """
        Add a participant to a session.

        Args:
            session_id: The session to add the participant to
            participant_id: Unique participant identifier
            participant_name: Display name for the participant
            metadata: Optional additional metadata

        Returns:
            The created Participant

        Raises:
            ValueError: If session not found
        """
        session = self._get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        participant = Participant(
            id=participant_id,
            name=participant_name,
            metadata=metadata or {},
        )
        session.add_participant(participant)

        logger.info(f"Added participant {participant_id} to session {session_id}")

        # Emit event
        await self.event_emitter.emit(Event(
            type=EventType.PARTICIPANT_JOINED,
            room_id=session.room_id,
            session_id=session_id,
            data={
                "participant_id": participant_id,
                "participant_name": participant_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ))

        return participant

    async def remove_participant(self, session_id: str, participant_id: str):
        """
        Remove a participant from a session.

        Args:
            session_id: The session to remove the participant from
            participant_id: The participant to remove

        Raises:
            ValueError: If session not found
        """
        session = self._get_session_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.remove_participant(participant_id)

        logger.info(f"Removed participant {participant_id} from session {session_id}")

        # Emit event
        await self.event_emitter.emit(Event(
            type=EventType.PARTICIPANT_LEFT,
            room_id=session.room_id,
            session_id=session_id,
            data={
                "participant_id": participant_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        ))

    async def _auto_summary_loop(self, session_id: str):
        """
        Background task that generates periodic summaries.

        Args:
            session_id: The session to generate summaries for
        """
        try:
            while True:
                await asyncio.sleep(self.config.summary_interval_minutes * 60)

                session = self._get_session_by_id(session_id)
                if not session or session.status == SessionStatus.COMPLETED:
                    break

                if session.recording.is_recording and self.ai_provider:
                    try:
                        await self._generate_interval_summary(session)
                    except Exception as e:
                        logger.error(f"Error generating auto-summary: {e}")

        except asyncio.CancelledError:
            logger.info(f"Auto-summary loop cancelled for session {session_id}")

    async def _generate_interval_summary(self, session: MeetingSession):
        """Generate an interval summary for ongoing recording."""
        if not self.ai_provider or not session.transcript_buffer:
            return

        transcripts = session.clear_transcript_buffer()
        summary = await self.ai_provider.generate_summary(transcripts, is_final=False)

        if self.storage:
            await self.storage.save_note(session.session_id, summary)

        # Emit event
        await self.event_emitter.emit(Event(
            type=EventType.SUMMARY_GENERATED,
            room_id=session.room_id,
            session_id=session.session_id,
            data={"summary": summary, "is_final": False}
        ))

        logger.info(f"Generated interval summary for session {session.session_id}")

    async def _generate_final_summary(self, session: MeetingSession) -> Dict[str, Any]:
        """Generate the final summary for a completed session."""
        if not self.ai_provider:
            return {}

        # Get all transcripts from storage
        transcripts = []
        if self.storage:
            transcripts = await self.storage.get_transcripts(session.session_id)

        summary = await self.ai_provider.generate_summary(transcripts, is_final=True)

        logger.info(f"Generated final summary for session {session.session_id}")

        return summary

    def _get_session_by_id(self, session_id: str) -> Optional[MeetingSession]:
        """Find a session by its session_id."""
        for session in self.active_sessions.values():
            if session.session_id == session_id:
                return session
        return None

    def get_session(self, room_id: str) -> Optional[MeetingSession]:
        """
        Get the active session for a room.

        Args:
            room_id: The room ID to look up

        Returns:
            The MeetingSession if found, None otherwise
        """
        return self.active_sessions.get(room_id)

    def get_all_sessions(self) -> List[MeetingSession]:
        """Get all active sessions."""
        return list(self.active_sessions.values())

    async def cleanup(self):
        """Clean up all resources and end all active sessions."""
        logger.info("Cleaning up NoteManager...")

        # End all active sessions
        for session in list(self.active_sessions.values()):
            try:
                await self.end_session(session.session_id)
            except Exception as e:
                logger.error(f"Error ending session {session.session_id}: {e}")

        # Clean up audio recorder
        if self.audio_recorder:
            await self.audio_recorder.cleanup()

        logger.info("NoteManager cleanup complete")
