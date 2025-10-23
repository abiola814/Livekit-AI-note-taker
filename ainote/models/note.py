"""Meeting note and action item models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class NoteType(Enum):
    """Types of meeting notes."""

    SUMMARY = "summary"
    ACTION_ITEMS = "action_items"
    KEY_POINTS = "key_points"
    DECISIONS = "decisions"
    QUESTIONS = "questions"
    FULL_TRANSCRIPT = "full_transcript"


class Priority(Enum):
    """Priority levels for action items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActionItemStatus(Enum):
    """Status of action items."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class MeetingNote:
    """Represents a meeting note (summary, key points, etc.)."""

    meeting_id: str
    note_type: NoteType
    content: str
    title: Optional[str] = None
    ai_generated: bool = False
    confidence_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "meeting_id": self.meeting_id,
            "note_type": self.note_type.value,
            "content": self.content,
            "title": self.title,
            "ai_generated": self.ai_generated,
            "confidence_score": self.confidence_score,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class ActionItem:
    """Represents an action item extracted from a meeting."""

    meeting_id: str
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    status: ActionItemStatus = ActionItemStatus.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_completed(self) -> None:
        """Mark this action item as completed."""
        self.status = ActionItemStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_in_progress(self) -> None:
        """Mark this action item as in progress."""
        self.status = ActionItemStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def is_overdue(self) -> bool:
        """Check if this action item is overdue."""
        if self.due_date and self.status not in [ActionItemStatus.COMPLETED, ActionItemStatus.CANCELLED]:
            return datetime.utcnow() > self.due_date
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_overdue": self.is_overdue(),
        }
