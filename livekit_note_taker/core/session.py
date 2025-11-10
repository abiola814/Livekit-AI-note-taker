"""
Meeting session management.

This module handles the lifecycle of a meeting session, including participants,
recording state, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
import uuid


class SessionStatus(str, Enum):
    """Status of a meeting session."""
    PENDING = "pending"
    ACTIVE = "active"
    RECORDING = "recording"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Participant:
    """
    Represents a participant in a meeting session.

    Attributes:
        id: Unique participant ID
        name: Display name
        identity: LiveKit identity
        joined_at: When the participant joined
        left_at: When the participant left (if applicable)
        is_active: Whether the participant is currently in the session
        metadata: Additional participant metadata
    """
    id: str
    name: str
    identity: str = field(default="")
    joined_at: datetime = field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)

    def leave(self):
        """Mark the participant as having left the session."""
        self.is_active = False
        self.left_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "identity": self.identity,
            "joined_at": self.joined_at.isoformat(),
            "left_at": self.left_at.isoformat() if self.left_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata,
        }


@dataclass
class RecordingState:
    """
    Tracks the recording state of a session.

    Attributes:
        is_recording: Whether recording is currently active
        started_at: When recording started
        stopped_at: When recording stopped
        started_by: Participant who started the recording
        total_batches_processed: Number of transcription batches processed
        duration_seconds: Total recording duration in seconds
    """
    is_recording: bool = False
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    started_by: Optional[str] = None
    total_batches_processed: int = 0
    duration_seconds: float = 0.0

    def start(self, started_by: str):
        """Start recording."""
        self.is_recording = True
        self.started_at = datetime.utcnow()
        self.started_by = started_by

    def stop(self):
        """Stop recording and calculate duration."""
        self.is_recording = False
        self.stopped_at = datetime.utcnow()
        if self.started_at:
            self.duration_seconds = (self.stopped_at - self.started_at).total_seconds()

    def increment_batch_count(self):
        """Increment the batch counter."""
        self.total_batches_processed += 1

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "is_recording": self.is_recording,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "started_by": self.started_by,
            "total_batches_processed": self.total_batches_processed,
            "duration_seconds": self.duration_seconds,
        }


class MeetingSession:
    """
    Represents a meeting session with participants, recording state, and metadata.

    This class manages the lifecycle of a meeting, including:
    - Participant management (join/leave)
    - Recording state tracking
    - Session metadata and configuration
    - Transcript and note accumulation

    Example:
        session = MeetingSession(
            room_id="my-room",
            title="Team Standup",
            config={"language": "en-US", "auto_summarize": True}
        )

        await session.add_participant(Participant(
            id="user-123",
            name="John Doe"
        ))

        session.start_recording(started_by="user-123")
    """

    def __init__(
        self,
        room_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        config: Optional[Dict] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize a new meeting session.

        Args:
            room_id: Unique room identifier
            title: Optional meeting title
            description: Optional meeting description
            config: Optional configuration dictionary
            session_id: Optional explicit session ID (generates UUID if not provided)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.room_id = room_id
        self.title = title or f"Meeting {room_id}"
        self.description = description
        self.config = config or {}

        self.status = SessionStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None

        # Participant tracking
        self.participants: Dict[str, Participant] = {}
        self.active_participant_ids: Set[str] = set()

        # Recording state
        self.recording = RecordingState()

        # Transcript buffer for temporary storage
        self.transcript_buffer: List[Dict] = []

        # Statistics
        self.stats = {
            "total_participants": 0,
            "total_transcripts": 0,
            "total_notes": 0,
            "total_action_items": 0,
        }

    def start(self):
        """Start the meeting session."""
        if self.status == SessionStatus.PENDING:
            self.status = SessionStatus.ACTIVE
            self.started_at = datetime.utcnow()

    def end(self):
        """End the meeting session."""
        if self.status != SessionStatus.COMPLETED:
            self.status = SessionStatus.COMPLETED
            self.ended_at = datetime.utcnow()
            if self.recording.is_recording:
                self.recording.stop()

    def add_participant(self, participant: Participant):
        """
        Add a participant to the session.

        Args:
            participant: The participant to add
        """
        self.participants[participant.id] = participant
        self.active_participant_ids.add(participant.id)
        self.stats["total_participants"] = len(self.participants)

    def remove_participant(self, participant_id: str):
        """
        Remove/deactivate a participant from the session.

        Args:
            participant_id: The ID of the participant to remove
        """
        if participant_id in self.participants:
            self.participants[participant_id].leave()
            self.active_participant_ids.discard(participant_id)

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get a participant by ID."""
        return self.participants.get(participant_id)

    def get_active_participants(self) -> List[Participant]:
        """Get all currently active participants."""
        return [
            p for p in self.participants.values()
            if p.is_active
        ]

    def start_recording(self, started_by: str):
        """
        Start recording for this session.

        Args:
            started_by: Participant ID who started the recording
        """
        self.recording.start(started_by)
        if self.status == SessionStatus.ACTIVE:
            self.status = SessionStatus.RECORDING

    def stop_recording(self):
        """Stop recording for this session."""
        self.recording.stop()
        if self.status == SessionStatus.RECORDING:
            self.status = SessionStatus.ACTIVE

    def add_transcript(self, transcript: Dict):
        """
        Add a transcript to the buffer.

        Args:
            transcript: Transcript data dictionary
        """
        self.transcript_buffer.append(transcript)
        self.stats["total_transcripts"] += 1

    def clear_transcript_buffer(self) -> List[Dict]:
        """
        Clear and return the transcript buffer.

        Returns:
            List of buffered transcripts
        """
        buffer = self.transcript_buffer.copy()
        self.transcript_buffer.clear()
        return buffer

    def get_duration(self) -> Optional[float]:
        """
        Get the session duration in seconds.

        Returns:
            Duration in seconds, or None if session hasn't started
        """
        if not self.started_at:
            return None

        end_time = self.ended_at or datetime.utcnow()
        return (end_time - self.started_at).total_seconds()

    def to_dict(self) -> Dict:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "room_id": self.room_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.get_duration(),
            "participants": [p.to_dict() for p in self.participants.values()],
            "active_participant_count": len(self.active_participant_ids),
            "recording": self.recording.to_dict(),
            "stats": self.stats,
            "config": self.config,
        }

    def __repr__(self) -> str:
        return (
            f"MeetingSession(session_id={self.session_id}, "
            f"room_id={self.room_id}, status={self.status.value}, "
            f"participants={len(self.participants)})"
        )
