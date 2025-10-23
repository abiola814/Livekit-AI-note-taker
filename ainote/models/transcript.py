"""Transcript data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class TranscriptSegment:
    """Represents a single segment of transcribed text."""

    text: str
    speaker: Optional[str] = None
    confidence: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    language: str = "en-US"
    is_final: bool = True

    def duration(self) -> Optional[float]:
        """Calculate duration of this segment in seconds."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "speaker": self.speaker,
            "confidence": self.confidence,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "language": self.language,
            "is_final": self.is_final,
            "duration": self.duration(),
        }


@dataclass
class Transcript:
    """Represents a complete transcript for a meeting."""

    meeting_id: str
    segments: List[TranscriptSegment] = field(default_factory=list)
    language: str = "en-US"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_segment(self, segment: TranscriptSegment) -> None:
        """Add a transcript segment."""
        self.segments.append(segment)

    def get_full_text(self, separator: str = "\n") -> str:
        """Get complete transcript as text."""
        return separator.join(seg.text for seg in self.segments)

    def get_segments_by_speaker(self, speaker: str) -> List[TranscriptSegment]:
        """Get all segments for a specific speaker."""
        return [seg for seg in self.segments if seg.speaker == speaker]

    def total_duration(self) -> float:
        """Calculate total duration of all segments."""
        durations = [seg.duration() for seg in self.segments if seg.duration() is not None]
        return sum(durations) if durations else 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "meeting_id": self.meeting_id,
            "segments": [seg.to_dict() for seg in self.segments],
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_segments": len(self.segments),
            "total_duration": self.total_duration(),
            "full_text": self.get_full_text(),
        }
