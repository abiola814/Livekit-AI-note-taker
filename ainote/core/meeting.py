"""Meeting management classes."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid

from ..models.transcript import Transcript, TranscriptSegment
from ..models.note import MeetingNote, ActionItem


class MeetingStatus(Enum):
    """Meeting status."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Meeting:
    """Represents a meeting session."""

    room_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    language: str = "en-US"
    auto_summarize: bool = True
    status: MeetingStatus = MeetingStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    participant_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Internal collections
    _transcript: Optional[Transcript] = field(default=None, init=False, repr=False)
    _notes: List[MeetingNote] = field(default_factory=list, init=False, repr=False)
    _action_items: List[ActionItem] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        """Initialize transcript."""
        if self._transcript is None:
            self._transcript = Transcript(meeting_id=self.id, language=self.language)

    @property
    def transcript(self) -> Transcript:
        """Get the meeting transcript."""
        if self._transcript is None:
            self._transcript = Transcript(meeting_id=self.id, language=self.language)
        return self._transcript

    @property
    def notes(self) -> List[MeetingNote]:
        """Get all meeting notes."""
        return self._notes

    @property
    def action_items(self) -> List[ActionItem]:
        """Get all action items."""
        return self._action_items

    def add_transcript_segment(self, segment: TranscriptSegment) -> None:
        """Add a transcript segment to the meeting."""
        self.transcript.add_segment(segment)

    def add_note(self, note: MeetingNote) -> None:
        """Add a note to the meeting."""
        self._notes.append(note)

    def add_action_item(self, action_item: ActionItem) -> None:
        """Add an action item to the meeting."""
        self._action_items.append(action_item)

    def complete(self) -> None:
        """Mark meeting as completed."""
        self.status = MeetingStatus.COMPLETED
        self.end_time = datetime.utcnow()

    def pause(self) -> None:
        """Pause the meeting."""
        self.status = MeetingStatus.PAUSED

    def resume(self) -> None:
        """Resume the meeting."""
        self.status = MeetingStatus.ACTIVE

    def duration_minutes(self) -> Optional[float]:
        """Get meeting duration in minutes."""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        else:
            delta = datetime.utcnow() - self.start_time
            return delta.total_seconds() / 60

    def to_dict(self) -> dict:
        """Convert meeting to dictionary."""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "title": self.title,
            "description": self.description,
            "language": self.language,
            "auto_summarize": self.auto_summarize,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes(),
            "participant_count": self.participant_count,
            "metadata": self.metadata,
            "transcript": self.transcript.to_dict() if self._transcript else None,
            "notes_count": len(self._notes),
            "action_items_count": len(self._action_items),
        }
