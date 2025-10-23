"""Tests for AINoteClient."""

import pytest
from ainote import AINoteClient
from ainote.core.meeting import MeetingStatus


def test_client_initialization():
    """Test client initialization."""
    client = AINoteClient(
        aws_region="us-east-1",
        ai_provider="openai",
        openai_api_key="test-key",
    )
    assert client.aws_region == "us-east-1"
    assert client.ai_service.provider == "openai"


def test_create_meeting():
    """Test creating a meeting."""
    client = AINoteClient(ai_provider="openai", openai_api_key="test-key")

    meeting = client.create_meeting(
        room_id="test-room",
        title="Test Meeting",
        description="Test Description",
    )

    assert meeting.room_id == "test-room"
    assert meeting.title == "Test Meeting"
    assert meeting.description == "Test Description"
    assert meeting.status == MeetingStatus.ACTIVE


def test_get_meeting():
    """Test retrieving a meeting."""
    client = AINoteClient(ai_provider="openai", openai_api_key="test-key")

    created = client.create_meeting(room_id="test-room")
    retrieved = client.get_meeting("test-room")

    assert retrieved is not None
    assert retrieved.room_id == created.room_id
    assert retrieved.id == created.id


def test_list_meetings():
    """Test listing meetings."""
    client = AINoteClient(ai_provider="openai", openai_api_key="test-key")

    # Create multiple meetings
    client.create_meeting(room_id="room1", title="Meeting 1")
    client.create_meeting(room_id="room2", title="Meeting 2")
    client.create_meeting(room_id="room3", title="Meeting 3")

    # List all meetings
    all_meetings = client.list_meetings()
    assert len(all_meetings) == 3

    # Complete one meeting
    client.complete_meeting("room1")

    # List only active meetings
    active_meetings = client.list_meetings(status=MeetingStatus.ACTIVE)
    assert len(active_meetings) == 2

    # List completed meetings
    completed_meetings = client.list_meetings(status=MeetingStatus.COMPLETED)
    assert len(completed_meetings) == 1


def test_complete_meeting():
    """Test completing a meeting."""
    client = AINoteClient(ai_provider="openai", openai_api_key="test-key")

    meeting = client.create_meeting(room_id="test-room")
    assert meeting.status == MeetingStatus.ACTIVE
    assert meeting.end_time is None

    completed = client.complete_meeting("test-room")
    assert completed.status == MeetingStatus.COMPLETED
    assert completed.end_time is not None


def test_client_repr():
    """Test client string representation."""
    client = AINoteClient(ai_provider="openai", openai_api_key="test-key")
    client.create_meeting(room_id="test1")
    client.create_meeting(room_id="test2")

    repr_str = repr(client)
    assert "AINoteClient" in repr_str
    assert "meetings=2" in repr_str
    assert "ai_provider=openai" in repr_str
