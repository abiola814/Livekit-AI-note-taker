"""
Base classes for transcription providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Transcript:
    """
    Represents a transcription result.

    Attributes:
        text: The transcribed text
        confidence: Confidence score (0-1)
        speaker_id: Speaker identifier
        speaker_name: Speaker display name
        timestamp: When this was spoken
        is_final: Whether this is a final or partial result
        language: Language code (e.g., "en-US")
        metadata: Additional provider-specific metadata
    """
    text: str
    confidence: float
    speaker_id: Optional[str] = None
    speaker_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_final: bool = True
    language: str = "en-US"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "speaker_id": self.speaker_id,
            "speaker_name": self.speaker_name,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "is_final": self.is_final,
            "language": self.language,
            "metadata": self.metadata,
        }


class TranscriptionProvider(ABC):
    """
    Abstract base class for transcription service providers.

    Subclasses should implement specific transcription services like
    AWS Transcribe, Deepgram, Google Speech-to-Text, etc.
    """

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en-US",
        sample_rate: int = 16000,
        **kwargs
    ) -> List[Transcript]:
        """
        Transcribe audio data.

        Args:
            audio_data: Raw audio bytes
            language: Language code
            sample_rate: Audio sample rate in Hz
            **kwargs: Provider-specific options

        Returns:
            List of Transcript objects
        """
        pass

    @abstractmethod
    async def transcribe_streaming(
        self,
        audio_stream,
        language: str = "en-US",
        sample_rate: int = 16000,
        **kwargs
    ):
        """
        Transcribe audio in streaming mode (async generator).

        Args:
            audio_stream: Async generator yielding audio chunks
            language: Language code
            sample_rate: Audio sample rate in Hz
            **kwargs: Provider-specific options

        Yields:
            Transcript objects as they become available
        """
        pass

    @abstractmethod
    async def close(self):
        """Close any connections and clean up resources."""
        pass
