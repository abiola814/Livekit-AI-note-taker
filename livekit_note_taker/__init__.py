"""
LiveKit Note Taker - A library for building AI-powered meeting note-taking applications

This library provides a modular, extensible framework for capturing audio from LiveKit meetings,
transcribing with various providers (AWS Transcribe, etc.), and generating AI-powered summaries
and action items.

Key Features:
- Real-time audio capture from LiveKit meetings
- Cost-optimized batch transcription
- Multi-participant audio mixing
- AI-powered summaries and action items
- Multiple export formats (PDF, Markdown, DOCX, JSON)
- Pluggable architecture for transcription and AI providers

Example:
    from livekit_note_taker import NoteManager
    from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
    from livekit_note_taker.ai.openai import OpenAIProvider

    manager = NoteManager(
        transcription_provider=AWSTranscriptionProvider(),
        ai_provider=OpenAIProvider(api_key="your-key")
    )

    await manager.start_session(room_id="my-room")
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from livekit_note_taker.core.manager import NoteManager
from livekit_note_taker.core.session import MeetingSession
from livekit_note_taker.core.events import EventEmitter, Event

__all__ = [
    "NoteManager",
    "MeetingSession",
    "EventEmitter",
    "Event",
]
