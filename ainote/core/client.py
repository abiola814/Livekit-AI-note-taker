"""Main client class for AI Note library."""

from typing import Optional, Dict, List, Callable
import asyncio
from pathlib import Path

from .meeting import Meeting, MeetingStatus
from ..services.transcription import TranscriptionService
from ..services.ai_service import AIService
from ..exporters.exporter import ExporterFactory
from ..models.export import ExportFormat, ExportOptions
from ..models.note import MeetingNote, ActionItem


class AINoteClient:
    """
    Main client for AI Note library.

    This is the primary interface for creating meetings, managing transcriptions,
    generating AI summaries, and exporting notes.

    Example:
        ```python
        from ainote import AINoteClient

        # Initialize client
        client = AINoteClient(
            aws_region="us-east-1",
            ai_provider="openai",
            openai_api_key="sk-..."
        )

        # Create a meeting
        meeting = client.create_meeting(
            room_id="meeting-123",
            title="Team Standup",
            language="en-US"
        )

        # Add transcription
        meeting.add_transcript_segment(segment)

        # Generate AI summary
        await client.generate_summary(meeting)

        # Export notes
        pdf_path = await client.export_meeting(meeting, format=ExportFormat.PDF)
        ```
    """

    def __init__(
        self,
        aws_region: str = "us-east-1",
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
        ai_provider: str = "openai",
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        batch_duration_minutes: int = 5,
        auto_summarize_interval_minutes: int = 15,
        exports_dir: str = "./exports",
    ):
        """
        Initialize the AI Note client.

        Args:
            aws_region: AWS region for transcription service
            aws_access_key: AWS access key (optional, can use environment)
            aws_secret_key: AWS secret key (optional, can use environment)
            ai_provider: AI provider to use ("openai" or "anthropic")
            openai_api_key: OpenAI API key (required if ai_provider="openai")
            anthropic_api_key: Anthropic API key (required if ai_provider="anthropic")
            batch_duration_minutes: Duration for batch transcription
            auto_summarize_interval_minutes: Interval for automatic summaries
            exports_dir: Directory for exported files
        """
        self.aws_region = aws_region
        self.batch_duration_minutes = batch_duration_minutes
        self.auto_summarize_interval_minutes = auto_summarize_interval_minutes
        self.exports_dir = Path(exports_dir)
        self.exports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize services
        self.transcription_service = TranscriptionService(
            aws_region=aws_region,
            aws_access_key=aws_access_key,
            aws_secret_key=aws_secret_key,
        )

        self.ai_service = AIService(
            provider=ai_provider,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )

        # Active meetings
        self._meetings: Dict[str, Meeting] = {}

    def create_meeting(
        self,
        room_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        language: str = "en-US",
        auto_summarize: bool = True,
    ) -> Meeting:
        """
        Create a new meeting.

        Args:
            room_id: Unique identifier for the meeting room
            title: Meeting title
            description: Meeting description
            language: Language code (default: en-US)
            auto_summarize: Enable automatic summarization

        Returns:
            Meeting instance
        """
        meeting = Meeting(
            room_id=room_id,
            title=title,
            description=description,
            language=language,
            auto_summarize=auto_summarize,
        )
        self._meetings[room_id] = meeting
        return meeting

    def get_meeting(self, room_id: str) -> Optional[Meeting]:
        """
        Get a meeting by room ID.

        Args:
            room_id: Meeting room identifier

        Returns:
            Meeting instance or None if not found
        """
        return self._meetings.get(room_id)

    def list_meetings(self, status: Optional[MeetingStatus] = None) -> List[Meeting]:
        """
        List all meetings, optionally filtered by status.

        Args:
            status: Filter by meeting status (optional)

        Returns:
            List of meetings
        """
        meetings = list(self._meetings.values())
        if status:
            meetings = [m for m in meetings if m.status == status]
        return meetings

    def complete_meeting(self, room_id: str) -> Optional[Meeting]:
        """
        Mark a meeting as completed.

        Args:
            room_id: Meeting room identifier

        Returns:
            Completed meeting or None if not found
        """
        meeting = self.get_meeting(room_id)
        if meeting:
            meeting.complete()
        return meeting

    async def transcribe_audio(
        self,
        meeting: Meeting,
        audio_file_path: str,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Transcribe an audio file and add segments to the meeting.

        Args:
            meeting: Meeting instance
            audio_file_path: Path to audio file
            callback: Optional callback for progress updates
        """
        segments = await self.transcription_service.transcribe_file(
            audio_file_path, language=meeting.language
        )

        for segment in segments:
            meeting.add_transcript_segment(segment)
            if callback:
                await callback(segment)

    async def generate_summary(
        self, meeting: Meeting, include_action_items: bool = True
    ) -> MeetingNote:
        """
        Generate an AI summary for the meeting.

        Args:
            meeting: Meeting instance
            include_action_items: Also extract action items

        Returns:
            Generated summary note
        """
        transcript_text = meeting.transcript.get_full_text()

        # Generate summary
        summary = await self.ai_service.generate_summary(
            transcript_text, meeting_title=meeting.title
        )
        meeting.add_note(summary)

        # Generate action items if requested
        if include_action_items:
            action_items = await self.ai_service.extract_action_items(
                transcript_text, meeting_id=meeting.id
            )
            for item in action_items:
                meeting.add_action_item(item)

        return summary

    async def export_meeting(
        self,
        meeting: Meeting,
        format: ExportFormat = ExportFormat.PDF,
        options: Optional[ExportOptions] = None,
    ) -> str:
        """
        Export meeting notes to a file.

        Args:
            meeting: Meeting to export
            format: Export format
            options: Export options (optional)

        Returns:
            Path to exported file
        """
        if options is None:
            options = ExportOptions(format=format)
        else:
            options.format = format

        exporter = ExporterFactory.create_exporter(format)
        output_path = self.exports_dir / f"{meeting.room_id}.{format.value}"

        await exporter.export(meeting, str(output_path), options)
        return str(output_path)

    async def start_live_transcription(
        self,
        meeting: Meeting,
        audio_stream,
        callback: Optional[Callable] = None,
    ):
        """
        Start live transcription from an audio stream.

        Args:
            meeting: Meeting instance
            audio_stream: Audio stream object
            callback: Optional callback for transcript updates
        """
        # This would integrate with LiveKit or similar streaming service
        # Placeholder for now
        raise NotImplementedError("Live transcription will be implemented in next version")

    def __repr__(self) -> str:
        """String representation."""
        return f"AINoteClient(meetings={len(self._meetings)}, ai_provider={self.ai_service.provider})"
