"""
Base classes for AI providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class SummaryResult:
    """
    Result from AI summarization.

    Attributes:
        summary: The generated summary text
        key_points: List of key points
        action_items: List of action items
        is_final: Whether this is a final or interval summary
        metadata: Additional provider-specific data
    """
    summary: str
    key_points: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    is_final: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "summary": self.summary,
            "key_points": self.key_points,
            "action_items": self.action_items,
            "is_final": self.is_final,
            "metadata": self.metadata,
        }


class AIProvider(ABC):
    """
    Abstract base class for AI service providers.

    Subclasses should implement specific AI services like
    OpenAI, Anthropic, OpenRouter, etc.
    """

    @abstractmethod
    async def generate_summary(
        self,
        transcripts: List[Dict[str, Any]],
        is_final: bool = False,
        **kwargs
    ) -> SummaryResult:
        """
        Generate a summary from transcripts.

        Args:
            transcripts: List of transcript dictionaries
            is_final: Whether this is the final summary
            **kwargs: Provider-specific options

        Returns:
            SummaryResult object
        """
        pass

    @abstractmethod
    async def extract_action_items(
        self,
        transcripts: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Extract action items from transcripts.

        Args:
            transcripts: List of transcript dictionaries
            **kwargs: Provider-specific options

        Returns:
            List of action item dictionaries
        """
        pass

    @abstractmethod
    async def close(self):
        """Close any connections and clean up resources."""
        pass
