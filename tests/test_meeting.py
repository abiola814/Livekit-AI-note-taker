"""Tests for Meeting class."""

import pytest
from datetime import datetime
from ainote.core.meeting import Meeting, MeetingStatus
from ainote.models import TranscriptSegment, MeetingNote, ActionItem, NoteType, Priority


def test_meeting_creation():
    """Test creating a meeting."""
    meeting = Meeting(
        room_id="test-room",
        title="Test Meeting",
        description="Test Description",
    )

    assert meeting.room_id == "test-room"
    assert meeting.title == "Test Meeting"
    assert meeting.description == "Test Description"
    assert meeting.status == MeetingStatus.ACTIVE
    assert meeting.language == "en-US"
    assert meeting.participant_count == 0


def test_meeting_transcript():
    """Test adding transcript segments."""
    meeting = Meeting(room_id="test-room")

    segment1 = TranscriptSegment(text="Hello", speaker="Alice")
    segment2 = TranscriptSegment(text="World", speaker="Bob")

    meeting.add_transcript_segment(segment1)
    meeting.add_transcript_segment(segment2)

    assert len(meeting.transcript.segments) == 2
    assert meeting.transcript.segments[0].text == "Hello"
    assert meeting.transcript.segments[1].speaker == "Bob"


def test_meeting_notes():
    """Test adding meeting notes."""
    meeting = Meeting(room_id="test-room")

    note = MeetingNote(
        meeting_id=meeting.id,
        note_type=NoteType.SUMMARY,
        content="This is a summary",
        ai_generated=True,
    )

    meeting.add_note(note)

    assert len(meeting.notes) == 1
    assert meeting.notes[0].content == "This is a summary"
    assert meeting.notes[0].ai_generated is True


def test_meeting_action_items():
    """Test adding action items."""
    meeting = Meeting(room_id="test-room")

    action = ActionItem(
        meeting_id=meeting.id,
        title="Complete task",
        assigned_to="Alice",
        priority=Priority.HIGH,
    )

    meeting.add_action_item(action)

    assert len(meeting.action_items) == 1
    assert meeting.action_items[0].title == "Complete task"
    assert meeting.action_items[0].assigned_to == "Alice"


def test_meeting_complete():
    """Test completing a meeting."""
    meeting = Meeting(room_id="test-room")
    assert meeting.status == MeetingStatus.ACTIVE
    assert meeting.end_time is None

    meeting.complete()

    assert meeting.status == MeetingStatus.COMPLETED
    assert meeting.end_time is not None
    assert isinstance(meeting.end_time, datetime)


def test_meeting_pause_resume():
    """Test pausing and resuming a meeting."""
    meeting = Meeting(room_id="test-room")

    meeting.pause()
    assert meeting.status == MeetingStatus.PAUSED

    meeting.resume()
    assert meeting.status == MeetingStatus.ACTIVE


def test_meeting_duration():
    """Test calculating meeting duration."""
    meeting = Meeting(room_id="test-room")

    # Active meeting should have some duration
    duration = meeting.duration_minutes()
    assert duration is not None
    assert duration >= 0

    # Completed meeting should have duration
    meeting.complete()
    duration_completed = meeting.duration_minutes()
    assert duration_completed is not None
    assert duration_completed >= duration


def test_meeting_to_dict():
    """Test converting meeting to dictionary."""
    meeting = Meeting(
        room_id="test-room",
        title="Test Meeting",
        description="Description",
    )

    meeting_dict = meeting.to_dict()

    assert meeting_dict["room_id"] == "test-room"
    assert meeting_dict["title"] == "Test Meeting"
    assert meeting_dict["description"] == "Description"
    assert meeting_dict["status"] == "active"
    assert "duration_minutes" in meeting_dict
    assert "transcript" in meeting_dict
