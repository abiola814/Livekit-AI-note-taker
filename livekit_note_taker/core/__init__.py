"""Core abstractions and interfaces for the LiveKit Note Taker library."""

from livekit_note_taker.core.manager import NoteManager
from livekit_note_taker.core.session import MeetingSession
from livekit_note_taker.core.events import EventEmitter, Event, EventType

__all__ = [
    "NoteManager",
    "MeetingSession",
    "EventEmitter",
    "Event",
    "EventType",
]
