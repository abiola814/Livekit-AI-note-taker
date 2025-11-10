"""
Event system for the LiveKit Note Taker library.

This module provides a generic event system that abstracts away specific
transport mechanisms (like Socket.IO) to make the library framework-agnostic.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types emitted by the note taker system."""

    # Session events
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"

    # Recording events
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"

    # Transcription events
    TRANSCRIPTION_BATCH = "transcription_batch"
    TRANSCRIPTION_PARTIAL = "transcription_partial"
    TRANSCRIPTION_FINAL = "transcription_final"

    # AI events
    SUMMARY_GENERATED = "summary_generated"
    ACTION_ITEMS_GENERATED = "action_items_generated"
    NOTE_UPDATED = "note_updated"

    # Processing events
    BATCH_PROCESSING_STARTED = "batch_processing_started"
    BATCH_PROCESSING_COMPLETED = "batch_processing_completed"
    BATCH_PROCESSING_FAILED = "batch_processing_failed"

    # Participant events
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"

    # Export events
    EXPORT_STARTED = "export_started"
    EXPORT_COMPLETED = "export_completed"
    EXPORT_FAILED = "export_failed"

    # Error events
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Event:
    """
    Event data structure.

    Attributes:
        type: The type of event
        room_id: The room ID associated with this event
        data: Event payload data
        timestamp: When the event occurred
        session_id: Optional session ID for tracking
    """
    type: EventType
    room_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "type": self.type.value,
            "room_id": self.room_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }


EventHandler = Callable[[Event], Awaitable[None]]


class EventEmitter:
    """
    Generic event emitter that can be adapted to different transport mechanisms.

    This class provides a framework-agnostic way to emit and listen to events.
    It can be integrated with Socket.IO, WebSockets, HTTP callbacks, or any other
    event delivery mechanism through adapters.

    Example:
        emitter = EventEmitter()

        @emitter.on(EventType.TRANSCRIPTION_BATCH)
        async def handle_transcription(event: Event):
            print(f"Received transcription: {event.data}")

        await emitter.emit(Event(
            type=EventType.TRANSCRIPTION_BATCH,
            room_id="room-123",
            data={"text": "Hello world"}
        ))
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._room_handlers: Dict[str, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._lock = asyncio.Lock()

    def on(self, event_type: EventType, handler: Optional[EventHandler] = None):
        """
        Register an event handler for a specific event type.

        Can be used as a decorator or called directly:
            @emitter.on(EventType.TRANSCRIPTION_BATCH)
            async def handler(event): ...

        Or:
            emitter.on(EventType.TRANSCRIPTION_BATCH, handler)
        """
        def decorator(func: EventHandler) -> EventHandler:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            logger.debug(f"Registered handler for {event_type.value}")
            return func

        if handler is None:
            return decorator
        else:
            return decorator(handler)

    def on_room(self, room_id: str, handler: EventHandler):
        """Register a handler for all events in a specific room."""
        if room_id not in self._room_handlers:
            self._room_handlers[room_id] = []
        self._room_handlers[room_id].append(handler)
        logger.debug(f"Registered room handler for {room_id}")

    def on_all(self, handler: EventHandler):
        """Register a global handler that receives all events."""
        self._global_handlers.append(handler)
        logger.debug("Registered global event handler")

    async def emit(self, event: Event):
        """
        Emit an event to all registered handlers.

        Args:
            event: The event to emit
        """
        handlers_to_call: List[EventHandler] = []

        # Collect type-specific handlers
        if event.type in self._handlers:
            handlers_to_call.extend(self._handlers[event.type])

        # Collect room-specific handlers
        if event.room_id in self._room_handlers:
            handlers_to_call.extend(self._room_handlers[event.room_id])

        # Collect global handlers
        handlers_to_call.extend(self._global_handlers)

        # Call all handlers concurrently
        if handlers_to_call:
            tasks = [handler(event) for handler in handlers_to_call]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Log any errors from handlers
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Error in event handler for {event.type.value}: {result}",
                        exc_info=result
                    )

    async def emit_to_room(self, room_id: str, event_type: EventType, data: Dict[str, Any]):
        """
        Convenience method to emit an event to a specific room.

        Args:
            room_id: The room ID to emit to
            event_type: The type of event
            data: Event payload data
        """
        event = Event(
            type=event_type,
            room_id=room_id,
            data=data,
        )
        await self.emit(event)

    def remove_handler(self, event_type: EventType, handler: EventHandler):
        """Remove a specific event handler."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Removed handler for {event_type.value}")
            except ValueError:
                pass

    def remove_room_handlers(self, room_id: str):
        """Remove all handlers for a specific room."""
        if room_id in self._room_handlers:
            del self._room_handlers[room_id]
            logger.debug(f"Removed all handlers for room {room_id}")

    def clear_all_handlers(self):
        """Remove all registered handlers."""
        self._handlers.clear()
        self._room_handlers.clear()
        self._global_handlers.clear()
        logger.debug("Cleared all event handlers")
