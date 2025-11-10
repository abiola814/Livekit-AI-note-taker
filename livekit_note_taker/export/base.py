"""
Base classes for export functionality.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from pathlib import Path


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    DOCX = "docx"
    JSON = "json"
    HTML = "html"


class ExportService(ABC):
    """
    Abstract base class for export services.

    Subclasses should implement specific export formats.
    """

    @abstractmethod
    async def export(
        self,
        session_data: Dict[str, Any],
        format: ExportFormat,
        output_path: Optional[Path] = None,
        include_transcripts: bool = True,
        include_summaries: bool = True,
        include_action_items: bool = True,
        **kwargs
    ) -> Path:
        """
        Export session data to a file.

        Args:
            session_data: The session data to export
            format: Export format
            output_path: Optional output path
            include_transcripts: Include raw transcripts
            include_summaries: Include AI summaries
            include_action_items: Include action items
            **kwargs: Format-specific options

        Returns:
            Path to the exported file
        """
        pass

    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass
