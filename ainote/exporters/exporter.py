"""Base exporter class and factory."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.meeting import Meeting
    from ..models.export import ExportOptions, ExportFormat


class BaseExporter(ABC):
    """Base class for all exporters."""

    @abstractmethod
    async def export(self, meeting: "Meeting", output_path: str, options: "ExportOptions") -> None:
        """
        Export meeting to a file.

        Args:
            meeting: Meeting to export
            output_path: Path to output file
            options: Export options
        """
        pass


class ExporterFactory:
    """Factory for creating exporters."""

    @staticmethod
    def create_exporter(format: "ExportFormat") -> BaseExporter:
        """
        Create an exporter for the specified format.

        Args:
            format: Export format

        Returns:
            Exporter instance
        """
        from ..models.export import ExportFormat
        from .pdf_exporter import PDFExporter
        from .markdown_exporter import MarkdownExporter
        from .json_exporter import JSONExporter
        from .docx_exporter import DOCXExporter
        from .txt_exporter import TXTExporter

        exporters = {
            ExportFormat.PDF: PDFExporter,
            ExportFormat.MARKDOWN: MarkdownExporter,
            ExportFormat.JSON: JSONExporter,
            ExportFormat.DOCX: DOCXExporter,
            ExportFormat.TXT: TXTExporter,
        }

        exporter_class = exporters.get(format)
        if not exporter_class:
            raise ValueError(f"Unsupported export format: {format}")

        return exporter_class()
