# Quick Start Guide

Get started with AI Note in 5 minutes!

## Installation

```bash
# Basic installation
pip install ainote

# With all features
pip install ainote[all]

# Or install from source
git clone https://github.com/yourusername/ainote.git
cd ainote
pip install -e .
```

## Setup

### 1. Get API Keys

You'll need:
- **AWS credentials** for transcription (AWS Transcribe)
- **OpenAI API key** OR **Anthropic API key** for AI features

### 2. Configure Environment (Optional)

Create a `.env` file or set environment variables:

```bash
# AWS
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

# OpenAI
export OPENAI_API_KEY=sk-your-key
```

## Your First Meeting

Create a file `my_first_meeting.py`:

```python
import asyncio
from ainote import AINoteClient, ExportFormat
from ainote.models import TranscriptSegment


async def main():
    # 1. Initialize client
    client = AINoteClient(
        aws_region="us-east-1",
        ai_provider="openai",
        openai_api_key="sk-your-key-here",
    )

    # 2. Create a meeting
    meeting = client.create_meeting(
        room_id="my-first-meeting",
        title="My First Meeting",
    )

    # 3. Add some transcript (in real use, this comes from audio)
    meeting.add_transcript_segment(
        TranscriptSegment(
            text="Welcome to the meeting! Let's discuss the project timeline.",
            speaker="Alice",
        )
    )
    meeting.add_transcript_segment(
        TranscriptSegment(
            text="We need to complete the design phase by next week.",
            speaker="Bob",
        )
    )

    # 4. Generate AI summary and action items
    print("Generating AI summary...")
    await client.generate_summary(meeting, include_action_items=True)

    # 5. Print results
    print("\nSummary:")
    for note in meeting.notes:
        print(note.content)

    print("\nAction Items:")
    for item in meeting.action_items:
        print(f"- {item.title}")

    # 6. Export to Markdown
    md_path = await client.export_meeting(meeting, format=ExportFormat.MARKDOWN)
    print(f"\nExported to: {md_path}")

    # 7. Complete the meeting
    client.complete_meeting(meeting.room_id)
    print(f"\nMeeting completed! Duration: {meeting.duration_minutes():.1f} minutes")


if __name__ == "__main__":
    asyncio.run(main())
```

## Run it

```bash
python my_first_meeting.py
```

## What's Next?

### Transcribe Audio Files

```python
# Instead of adding segments manually:
await client.transcribe_audio(meeting, "recording.mp3")
```

### Export to Different Formats

```python
# PDF
await client.export_meeting(meeting, format=ExportFormat.PDF)

# Word Document
await client.export_meeting(meeting, format=ExportFormat.DOCX)

# JSON
await client.export_meeting(meeting, format=ExportFormat.JSON)
```

### Use Anthropic Claude

```python
client = AINoteClient(
    ai_provider="anthropic",
    anthropic_api_key="sk-ant-your-key",
)
```

### Manage Multiple Meetings

```python
# Create multiple meetings
meeting1 = client.create_meeting(room_id="standup-001")
meeting2 = client.create_meeting(room_id="planning-002")

# List all meetings
all_meetings = client.list_meetings()

# List active meetings only
active = client.list_meetings(status=MeetingStatus.ACTIVE)
```

## Common Issues

### Missing Dependencies

If you get import errors:

```bash
# For PDF export
pip install reportlab

# For DOCX export
pip install python-docx

# For OpenAI
pip install openai

# For Anthropic
pip install anthropic
```

### AWS Credentials

If transcription fails, make sure AWS is configured:

```bash
aws configure
# OR set environment variables
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

## Examples

Check the `examples/` directory for more:

- `basic_usage.py` - Complete basic example
- `advanced_usage.py` - Multiple meetings, custom action items
- `transcribe_audio.py` - Audio file transcription

## Learn More

- [Full Documentation](README.md)
- [API Reference](docs/)
- [Examples](examples/)

## Get Help

- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation

Happy meeting note-taking! 🎉
