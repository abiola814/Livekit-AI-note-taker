"""Export format models and options."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ExportFormat(Enum):
    """Supported export formats."""

    PDF = "pdf"
    MARKDOWN = "markdown"
    DOCX = "docx"
    JSON = "json"
    TXT = "txt"
    HTML = "html"


@dataclass
class ExportOptions:
    """Options for exporting meeting notes."""

    format: ExportFormat = ExportFormat.PDF
    include_transcripts: bool = True
    include_summary: bool = True
    include_action_items: bool = True
    include_metadata: bool = True
    title: Optional[str] = None
    author: Optional[str] = None
    template: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "format": self.format.value,
            "include_transcripts": self.include_transcripts,
            "include_summary": self.include_summary,
            "include_action_items": self.include_action_items,
            "include_metadata": self.include_metadata,
            "title": self.title,
            "author": self.author,
            "template": self.template,
        }
