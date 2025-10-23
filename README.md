# AI Note - Python Library for Meeting Transcription

A cost-effective Python library for meeting transcription, AI-powered summaries, and multi-format export capabilities.

## Features

- **Easy-to-use API**: Simple, intuitive interface for meeting transcription
- **Multiple AI Providers**: Support for OpenAI and Anthropic Claude
- **Batch Transcription**: Cost-effective batch processing using AWS Transcribe
- **AI-Powered Analysis**: Automatic summaries and action item extraction
- **Multiple Export Formats**: PDF, Markdown, Word, JSON, and plain text
- **Async Support**: Built with async/await for efficient processing
- **Type Hints**: Full type hint support for better IDE integration

## Installation

### Basic Installation

```bash
pip install ainote
```

### With OpenAI Support

```bash
pip install ainote[openai]
```

### With Anthropic Support

```bash
pip install ainote[anthropic]
```

### With All Features

```bash
pip install ainote[all]
```

### For Development

```bash
pip install ainote[dev]
```

## Quick Start

```python
import asyncio
from ainote import AINoteClient, ExportFormat

# Initialize the client
client = AINoteClient(
    aws_region="us-east-1",
    ai_provider="openai",
    openai_api_key="sk-..."
)

# Create a meeting
meeting = client.create_meeting(
    room_id="meeting-123",
    title="Team Standup",
    description="Daily team sync",
    language="en-US"
)

# Transcribe audio file
async def main():
    # Transcribe audio
    await client.transcribe_audio(meeting, "recording.mp3")

    # Generate AI summary and action items
    await client.generate_summary(meeting, include_action_items=True)

    # Export to PDF
    pdf_path = await client.export_meeting(meeting, format=ExportFormat.PDF)
    print(f"Notes exported to: {pdf_path}")

    # Export to Markdown
    md_path = await client.export_meeting(meeting, format=ExportFormat.MARKDOWN)
    print(f"Markdown exported to: {md_path}")

asyncio.run(main())
```

## Usage Examples

### Creating and Managing Meetings

```python
from ainote import AINoteClient

client = AINoteClient(
    aws_region="us-east-1",
    ai_provider="openai",
    openai_api_key="sk-..."
)

# Create a meeting
meeting = client.create_meeting(
    room_id="standup-001",
    title="Daily Standup",
    language="en-US"
)

# Get meeting by room ID
meeting = client.get_meeting("standup-001")

# List all active meetings
active_meetings = client.list_meetings(status=MeetingStatus.ACTIVE)

# Complete a meeting
client.complete_meeting("standup-001")
```

### Transcribing Audio

```python
import asyncio

async def transcribe_meeting():
    # Transcribe with progress callback
    def progress_callback(segment):
        print(f"New segment: {segment.text}")

    await client.transcribe_audio(
        meeting,
        audio_file_path="meeting.mp3",
        callback=progress_callback
    )

    # Access transcript
    full_text = meeting.transcript.get_full_text()
    print(full_text)

asyncio.run(transcribe_meeting())
```

### Generating AI Summaries

```python
import asyncio

async def generate_notes():
    # Generate summary and action items
    summary = await client.generate_summary(
        meeting,
        include_action_items=True
    )

    # Access summary
    print(summary.content)

    # Access action items
    for item in meeting.action_items:
        print(f"- {item.title}")
        if item.assigned_to:
            print(f"  Assigned to: {item.assigned_to}")
        if item.due_date:
            print(f"  Due: {item.due_date}")

asyncio.run(generate_notes())
```

### Exporting Notes

```python
import asyncio
from ainote import ExportFormat, ExportOptions

async def export_notes():
    # Export to PDF
    pdf_path = await client.export_meeting(meeting, format=ExportFormat.PDF)

    # Export to Markdown
    md_path = await client.export_meeting(meeting, format=ExportFormat.MARKDOWN)

    # Export with custom options
    options = ExportOptions(
        format=ExportFormat.PDF,
        include_transcripts=True,
        include_summary=True,
        include_action_items=True,
        title="Q1 Planning Meeting",
        author="John Doe"
    )
    custom_pdf = await client.export_meeting(meeting, options=options)

asyncio.run(export_notes())
```

### Working with Transcript Segments

```python
from ainote.models import TranscriptSegment

# Manually add transcript segments
segment = TranscriptSegment(
    text="Let's discuss the quarterly goals.",
    speaker="John Doe",
    confidence=0.95,
    start_time=0.0,
    end_time=3.5,
    language="en-US"
)

meeting.add_transcript_segment(segment)

# Get segments by speaker
john_segments = meeting.transcript.get_segments_by_speaker("John Doe")

# Calculate total duration
total_duration = meeting.transcript.total_duration()
```

### Using Multiple AI Providers

```python
# With OpenAI
client_openai = AINoteClient(
    ai_provider="openai",
    openai_api_key="sk-..."
)

# With Anthropic
client_anthropic = AINoteClient(
    ai_provider="anthropic",
    anthropic_api_key="sk-ant-..."
)
```

## Configuration

### Environment Variables

You can also configure the library using environment variables:

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# OpenAI Configuration
export OPENAI_API_KEY=sk-your-key

# Anthropic Configuration
export ANTHROPIC_API_KEY=sk-ant-your-key
```

Then initialize without explicit keys:

```python
from ainote import AINoteClient

client = AINoteClient(ai_provider="openai")
```

## API Reference

### AINoteClient

Main client class for interacting with the library.

#### Methods

- `create_meeting(room_id, title=None, description=None, language="en-US")` - Create a new meeting
- `get_meeting(room_id)` - Get a meeting by room ID
- `list_meetings(status=None)` - List all meetings
- `complete_meeting(room_id)` - Mark a meeting as completed
- `transcribe_audio(meeting, audio_file_path, callback=None)` - Transcribe audio file
- `generate_summary(meeting, include_action_items=True)` - Generate AI summary
- `export_meeting(meeting, format, options=None)` - Export meeting notes

### Meeting

Represents a meeting session.

#### Properties

- `transcript` - Meeting transcript
- `notes` - List of meeting notes
- `action_items` - List of action items
- `status` - Meeting status

#### Methods

- `add_transcript_segment(segment)` - Add a transcript segment
- `add_note(note)` - Add a note
- `add_action_item(item)` - Add an action item
- `complete()` - Mark meeting as completed
- `duration_minutes()` - Get meeting duration

### Export Formats

- `ExportFormat.PDF` - PDF format
- `ExportFormat.MARKDOWN` - Markdown format
- `ExportFormat.DOCX` - Microsoft Word format
- `ExportFormat.JSON` - JSON format
- `ExportFormat.TXT` - Plain text format

## Requirements

- Python 3.8+
- boto3 (for AWS Transcribe)
- openai or anthropic (for AI features)
- reportlab (for PDF export)
- python-docx (for DOCX export)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
