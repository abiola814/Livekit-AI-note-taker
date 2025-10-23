"""
AI Note - Python Library for Meeting Transcription and AI-Powered Note Taking

A cost-effective library for meeting transcription using batch processing,
AI-powered summaries, and multi-format export capabilities.
"""

__version__ = "0.1.0"
__author__ = "AI Note Contributors"

from .core.client import AINoteClient
from .core.meeting import Meeting
from .models.transcript import Transcript, TranscriptSegment
from .models.note import MeetingNote, ActionItem
from .models.export import ExportFormat, ExportOptions

__all__ = [
    "AINoteClient",
    "Meeting",
    "Transcript",
    "TranscriptSegment",
    "MeetingNote",
    "ActionItem",
    "ExportFormat",
    "ExportOptions",
]
