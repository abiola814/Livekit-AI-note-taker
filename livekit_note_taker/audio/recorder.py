"""
Audio recorder interfaces and implementations.

This module provides abstract base classes for audio recording and a concrete
LiveKit implementation for capturing audio from LiveKit meetings.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable, Awaitable, Any
from pathlib import Path
import wave

from livekit import rtc, api

from livekit_note_taker.audio.buffer import AudioBuffer

logger = logging.getLogger(__name__)


class AudioRecorder(ABC):
    """
    Abstract base class for audio recording implementations.

    Subclasses should implement the specific audio capture mechanism
    (LiveKit, WebRTC, local file, etc.).
    """

    @abstractmethod
    async def start_recording(
        self,
        room_id: str,
        session_id: str,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start recording audio for a room.

        Args:
            room_id: The room to record
            session_id: The session ID for this recording
            config: Optional configuration

        Returns:
            Recording status information
        """
        pass

    @abstractmethod
    async def stop_recording(self, room_id: str) -> Dict[str, Any]:
        """
        Stop recording audio for a room.

        Args:
            room_id: The room to stop recording

        Returns:
            Recording summary information
        """
        pass

    @abstractmethod
    async def get_recording_status(self, room_id: str) -> Dict[str, Any]:
        """
        Get the current recording status for a room.

        Args:
            room_id: The room to check

        Returns:
            Recording status information
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """Clean up all resources."""
        pass


class LiveKitRecorder(AudioRecorder):
    """
    LiveKit-based audio recorder.

    This implementation connects to LiveKit rooms, subscribes to participant
    audio tracks, and buffers audio for batch transcription.

    Example:
        recorder = LiveKitRecorder(
            livekit_url="wss://your-livekit-server.com",
            api_key="your-api-key",
            api_secret="your-api-secret"
        )

        # Set up audio frame callback
        async def on_audio_batch(room_id: str, audio_data: bytes):
            # Send to transcription service
            pass

        recorder.on_audio_batch = on_audio_batch

        # Start recording
        await recorder.start_recording(
            room_id="my-room",
            session_id="session-123"
        )
    """

    def __init__(
        self,
        livekit_url: str,
        api_key: str,
        api_secret: str,
        buffer_duration_minutes: int = 15,
        temp_audio_dir: Optional[Path] = None,
    ):
        """
        Initialize the LiveKit recorder.

        Args:
            livekit_url: LiveKit server URL (e.g., wss://your-server.com)
            api_key: LiveKit API key
            api_secret: LiveKit API secret
            buffer_duration_minutes: How long to buffer audio before processing
            temp_audio_dir: Directory for temporary audio files
        """
        self.livekit_url = livekit_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.buffer_duration_minutes = buffer_duration_minutes
        self.temp_audio_dir = temp_audio_dir or Path("./temp_audio")
        self.temp_audio_dir.mkdir(exist_ok=True)

        # Room tracking
        self.room_connections: Dict[str, rtc.Room] = {}
        self.audio_buffers: Dict[str, AudioBuffer] = {}
        self.recording_active: Dict[str, bool] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}

        # Callbacks
        self.on_audio_batch: Optional[Callable[[str, bytes], Awaitable[None]]] = None
        self.on_participant_connected: Optional[Callable[[str, str], Awaitable[None]]] = None
        self.on_participant_disconnected: Optional[Callable[[str, str], Awaitable[None]]] = None

        self._lock = asyncio.Lock()

    def generate_token(
        self,
        room_id: str,
        participant_id: str,
        participant_name: str
    ) -> str:
        """
        Generate a LiveKit access token.

        Args:
            room_id: The room to join
            participant_id: Unique participant identifier
            participant_name: Display name for the participant

        Returns:
            JWT token string
        """
        token = (
            api.AccessToken(self.api_key, self.api_secret)
            .with_identity(participant_id)
            .with_name(participant_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_id,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )
            .to_jwt()
        )
        return token

    async def start_recording(
        self,
        room_id: str,
        session_id: str,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Start recording audio from a LiveKit room.

        Args:
            room_id: The LiveKit room to record
            session_id: Session ID for tracking
            config: Optional configuration (language, buffer_duration, etc.)

        Returns:
            Recording status information
        """
        async with self._lock:
            if room_id in self.recording_active and self.recording_active[room_id]:
                raise ValueError(f"Recording already active for room {room_id}")

            # Initialize audio buffer
            buffer_duration = config.get("buffer_duration_minutes", self.buffer_duration_minutes) if config else self.buffer_duration_minutes
            self.audio_buffers[room_id] = AudioBuffer(
                buffer_duration_minutes=buffer_duration
            )

            # Connect to LiveKit room
            room = rtc.Room()

            # Set up event handlers
            @room.on("track_subscribed")
            def on_track_subscribed(track, publication, participant):
                if track.kind == rtc.TrackKind.KIND_AUDIO:
                    asyncio.create_task(
                        self._handle_audio_track(track, participant, room_id)
                    )

            @room.on("participant_connected")
            def on_participant_connected(participant):
                logger.info(f"Participant {participant.identity} connected to {room_id}")
                if self.on_participant_connected:
                    asyncio.create_task(
                        self.on_participant_connected(room_id, participant.identity)
                    )

            @room.on("participant_disconnected")
            def on_participant_disconnected(participant):
                logger.info(f"Participant {participant.identity} disconnected from {room_id}")
                if self.on_participant_disconnected:
                    asyncio.create_task(
                        self.on_participant_disconnected(room_id, participant.identity)
                    )

            # Generate bot token and connect
            import uuid
            import time
            bot_identity = f"recorder_bot_{room_id}_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            token = self.generate_token(room_id, bot_identity, "Recording Bot")

            await room.connect(
                self.livekit_url,
                token,
                options=rtc.RoomOptions(auto_subscribe=True)
            )

            self.room_connections[room_id] = room
            self.recording_active[room_id] = True

            # Start batch processing loop
            self.processing_tasks[room_id] = asyncio.create_task(
                self._batch_processing_loop(room_id)
            )

            logger.info(f"Started recording for room {room_id}")

            return {
                "status": "recording_started",
                "room_id": room_id,
                "session_id": session_id,
                "buffer_duration_minutes": buffer_duration,
            }

    async def stop_recording(self, room_id: str) -> Dict[str, Any]:
        """
        Stop recording audio for a room.

        Args:
            room_id: The room to stop recording

        Returns:
            Recording summary
        """
        async with self._lock:
            if room_id not in self.recording_active or not self.recording_active[room_id]:
                raise ValueError(f"No active recording for room {room_id}")

            # Stop recording
            self.recording_active[room_id] = False

            # Process final batch
            if room_id in self.audio_buffers:
                buffer = self.audio_buffers[room_id]
                mixed_audio = await buffer.get_mixed_audio()
                if mixed_audio and self.on_audio_batch:
                    await self.on_audio_batch(room_id, mixed_audio)

            # Cancel processing task
            if room_id in self.processing_tasks:
                task = self.processing_tasks[room_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del self.processing_tasks[room_id]

            # Disconnect from LiveKit
            if room_id in self.room_connections:
                room = self.room_connections[room_id]
                await room.disconnect()
                del self.room_connections[room_id]

            # Clean up buffer
            if room_id in self.audio_buffers:
                await self.audio_buffers[room_id].clear()
                del self.audio_buffers[room_id]

            logger.info(f"Stopped recording for room {room_id}")

            return {
                "status": "recording_stopped",
                "room_id": room_id,
            }

    async def get_recording_status(self, room_id: str) -> Dict[str, Any]:
        """
        Get the current recording status for a room.

        Args:
            room_id: The room to check

        Returns:
            Recording status information
        """
        is_recording = self.recording_active.get(room_id, False)
        buffer_info = {}

        if room_id in self.audio_buffers:
            buffer_info = self.audio_buffers[room_id].get_buffer_info()

        return {
            "room_id": room_id,
            "is_recording": is_recording,
            "has_connection": room_id in self.room_connections,
            "buffer_info": buffer_info,
        }

    async def _handle_audio_track(
        self,
        track: rtc.AudioTrack,
        participant: rtc.Participant,
        room_id: str
    ):
        """
        Handle an audio track from a participant.

        Args:
            track: The audio track
            participant: The participant
            room_id: The room ID
        """
        try:
            if not self.recording_active.get(room_id, False):
                return

            audio_stream = rtc.AudioStream(
                track=track,
                sample_rate=16000,
                num_channels=1,
                capacity=100
            )

            participant_id = participant.identity
            logger.info(f"Capturing audio from {participant_id} in {room_id}")

            async for frame_event in audio_stream:
                # Check if still recording
                if not self.recording_active.get(room_id, False):
                    break

                if room_id not in self.audio_buffers:
                    break

                # Add audio frame to buffer
                await self.audio_buffers[room_id].add_audio_frame(
                    participant_id,
                    frame_event.frame.data
                )

            logger.info(f"Audio capture ended for {participant_id} in {room_id}")

        except Exception as e:
            logger.error(f"Error handling audio track: {e}", exc_info=True)

    async def _batch_processing_loop(self, room_id: str):
        """
        Background loop that processes audio batches.

        Args:
            room_id: The room to process batches for
        """
        try:
            while self.recording_active.get(room_id, False):
                await asyncio.sleep(30)  # Check every 30 seconds

                if room_id not in self.audio_buffers:
                    continue

                buffer = self.audio_buffers[room_id]

                # Check if batch should be processed
                if buffer.should_process_batch():
                    logger.info(f"Processing audio batch for room {room_id}")

                    # Get mixed audio
                    mixed_audio = await buffer.get_mixed_audio()

                    if mixed_audio and self.on_audio_batch:
                        # Call the callback with the audio data
                        await self.on_audio_batch(room_id, mixed_audio)

                    # Clear buffer for next batch
                    await buffer.clear()

        except asyncio.CancelledError:
            logger.info(f"Batch processing loop cancelled for room {room_id}")
        except Exception as e:
            logger.error(f"Error in batch processing loop: {e}", exc_info=True)

    async def save_audio_to_file(
        self,
        audio_data: bytes,
        room_id: str,
        suffix: str = ""
    ) -> Path:
        """
        Save audio data to a WAV file.

        Args:
            audio_data: Raw audio bytes (int16)
            room_id: Room identifier for naming
            suffix: Optional suffix for filename

        Returns:
            Path to the saved file
        """
        import time
        filename = f"audio_{room_id}_{int(time.time())}{suffix}.wav"
        file_path = self.temp_audio_dir / filename

        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes (int16)
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(audio_data)

        logger.info(f"Saved audio to {file_path}")
        return file_path

    async def cleanup(self):
        """Clean up all resources and stop all recordings."""
        logger.info("Cleaning up LiveKitRecorder...")

        # Stop all recordings
        for room_id in list(self.recording_active.keys()):
            try:
                await self.stop_recording(room_id)
            except Exception as e:
                logger.error(f"Error stopping recording for {room_id}: {e}")

        logger.info("LiveKitRecorder cleanup complete")
