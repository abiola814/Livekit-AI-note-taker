"""Tests for data models."""

import pytest
from datetime import datetime, timedelta
from ainote.models import (
    TranscriptSegment,
    Transcript,
    MeetingNote,
    ActionItem,
    NoteType,
    Priority,
    ActionItemStatus,
    ExportFormat,
    ExportOptions,
)


def test_transcript_segment_creation():
    """Test creating a transcript segment."""
    segment = TranscriptSegment(
        text="Hello world",
        speaker="Alice",
        confidence=0.95,
        start_time=0.0,
        end_time=2.5,
    )

    assert segment.text == "Hello world"
    assert segment.speaker == "Alice"
    assert segment.confidence == 0.95
    assert segment.duration() == 2.5


def test_transcript_segment_to_dict():
    """Test converting segment to dictionary."""
    segment = TranscriptSegment(text="Test", speaker="Bob")
    segment_dict = segment.to_dict()

    assert segment_dict["text"] == "Test"
    assert segment_dict["speaker"] == "Bob"
    assert "timestamp" in segment_dict


def test_transcript_add_segment():
    """Test adding segments to transcript."""
    transcript = Transcript(meeting_id="meeting-1")

    segment1 = TranscriptSegment(text="First", speaker="Alice")
    segment2 = TranscriptSegment(text="Second", speaker="Bob")

    transcript.add_segment(segment1)
    transcript.add_segment(segment2)

    assert len(transcript.segments) == 2


def test_transcript_full_text():
    """Test getting full transcript text."""
    transcript = Transcript(meeting_id="meeting-1")

    transcript.add_segment(TranscriptSegment(text="Hello"))
    transcript.add_segment(TranscriptSegment(text="World"))

    full_text = transcript.get_full_text()
    assert full_text == "Hello\nWorld"

    full_text_space = transcript.get_full_text(separator=" ")
    assert full_text_space == "Hello World"


def test_transcript_by_speaker():
    """Test getting segments by speaker."""
    transcript = Transcript(meeting_id="meeting-1")

    transcript.add_segment(TranscriptSegment(text="Hello", speaker="Alice"))
    transcript.add_segment(TranscriptSegment(text="Hi", speaker="Bob"))
    transcript.add_segment(TranscriptSegment(text="How are you?", speaker="Alice"))

    alice_segments = transcript.get_segments_by_speaker("Alice")
    assert len(alice_segments) == 2
    assert all(seg.speaker == "Alice" for seg in alice_segments)


def test_meeting_note_creation():
    """Test creating a meeting note."""
    note = MeetingNote(
        meeting_id="meeting-1",
        note_type=NoteType.SUMMARY,
        content="This is a summary",
        ai_generated=True,
        confidence_score=0.9,
    )

    assert note.note_type == NoteType.SUMMARY
    assert note.content == "This is a summary"
    assert note.ai_generated is True


def test_action_item_creation():
    """Test creating an action item."""
    due_date = datetime.now() + timedelta(days=7)

    action = ActionItem(
        meeting_id="meeting-1",
        title="Complete report",
        description="Finish quarterly report",
        assigned_to="Alice",
        priority=Priority.HIGH,
        due_date=due_date,
    )

    assert action.title == "Complete report"
    assert action.priority == Priority.HIGH
    assert action.status == ActionItemStatus.OPEN


def test_action_item_status_changes():
    """Test changing action item status."""
    action = ActionItem(meeting_id="meeting-1", title="Task")

    assert action.status == ActionItemStatus.OPEN

    action.mark_in_progress()
    assert action.status == ActionItemStatus.IN_PROGRESS

    action.mark_completed()
    assert action.status == ActionItemStatus.COMPLETED


def test_action_item_overdue():
    """Test checking if action item is overdue."""
    # Past due date
    past_date = datetime.now() - timedelta(days=1)
    overdue_action = ActionItem(
        meeting_id="meeting-1", title="Overdue", due_date=past_date
    )
    assert overdue_action.is_overdue() is True

    # Future due date
    future_date = datetime.now() + timedelta(days=7)
    future_action = ActionItem(
        meeting_id="meeting-1", title="Future", due_date=future_date
    )
    assert future_action.is_overdue() is False

    # Completed items are not overdue
    overdue_action.mark_completed()
    assert overdue_action.is_overdue() is False


def test_export_options():
    """Test export options."""
    options = ExportOptions(
        format=ExportFormat.PDF,
        include_transcripts=True,
        include_summary=True,
        title="My Meeting",
    )

    assert options.format == ExportFormat.PDF
    assert options.include_transcripts is True
    assert options.title == "My Meeting"

    options_dict = options.to_dict()
    assert options_dict["format"] == "pdf"
    assert options_dict["title"] == "My Meeting"
