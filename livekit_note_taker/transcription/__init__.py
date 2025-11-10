"""Transcription provider modules."""

from livekit_note_taker.transcription.base import TranscriptionProvider, Transcript

try:
    from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
    _has_aws = True
except ImportError:
    _has_aws = False

__all__ = [
    "TranscriptionProvider",
    "Transcript",
]

if _has_aws:
    __all__.append("AWSTranscriptionProvider")
