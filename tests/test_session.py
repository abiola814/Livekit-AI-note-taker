"""Tests for MeetingSession class."""

import pytest
from livekit_note_taker.core.session import (
    MeetingSession,
    Participant,
    SessionStatus
)


def test_session_creation():
    """Test creating a MeetingSession."""
    session = MeetingSession(
        room_id="test-room",
        title="Test Meeting"
    )

    assert session.room_id == "test-room"
    assert session.title == "Test Meeting"
    assert session.status == SessionStatus.PENDING


def test_session_start():
    """Test starting a session."""
    session = MeetingSession(room_id="test-room")

    session.start()

    assert session.status == SessionStatus.ACTIVE
    assert session.started_at is not None


def test_add_participant():
    """Test adding participants."""
    session = MeetingSession(room_id="test-room")

    participant = Participant(
        id="user-1",
        name="John Doe"
    )

    session.add_participant(participant)

    assert len(session.participants) == 1
    assert "user-1" in session.participants
    assert session.stats["total_participants"] == 1


def test_remove_participant():
    """Test removing participants."""
    session = MeetingSession(room_id="test-room")

    participant = Participant(id="user-1", name="John")
    session.add_participant(participant)

    session.remove_participant("user-1")

    assert "user-1" not in session.active_participant_ids
    assert not session.participants["user-1"].is_active


def test_recording_lifecycle():
    """Test recording start/stop."""
    session = MeetingSession(room_id="test-room")
    session.start()

    # Start recording
    session.start_recording("user-1")

    assert session.recording.is_recording
    assert session.recording.started_by == "user-1"
    assert session.status == SessionStatus.RECORDING

    # Stop recording
    session.stop_recording()

    assert not session.recording.is_recording
    assert session.recording.duration_seconds > 0
    assert session.status == SessionStatus.ACTIVE


def test_transcript_buffer():
    """Test transcript buffering."""
    session = MeetingSession(room_id="test-room")

    # Add transcripts
    session.add_transcript({"text": "Hello", "confidence": 0.9})
    session.add_transcript({"text": "World", "confidence": 0.95})

    assert len(session.transcript_buffer) == 2
    assert session.stats["total_transcripts"] == 2

    # Clear buffer
    transcripts = session.clear_transcript_buffer()

    assert len(transcripts) == 2
    assert len(session.transcript_buffer) == 0


def test_session_to_dict():
    """Test converting session to dictionary."""
    session = MeetingSession(
        room_id="test-room",
        title="Test Meeting"
    )
    session.start()

    data = session.to_dict()

    assert data["room_id"] == "test-room"
    assert data["title"] == "Test Meeting"
    assert data["status"] == "active"
    assert "session_id" in data


def test_get_duration():
    """Test getting session duration."""
    session = MeetingSession(room_id="test-room")

    # Before start
    assert session.get_duration() is None

    # After start
    session.start()
    duration = session.get_duration()

    assert duration is not None
    assert duration >= 0
