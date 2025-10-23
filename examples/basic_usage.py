"""
Basic usage example for AI Note library.

This example shows how to:
1. Create a meeting
2. Transcribe audio
3. Generate AI summary
4. Export notes
"""

import asyncio
from ainote import AINoteClient, ExportFormat
from ainote.models import TranscriptSegment


async def main():
    # Initialize client with OpenAI
    client = AINoteClient(
        aws_region="us-east-1",
        ai_provider="openai",
        openai_api_key="sk-your-openai-key-here",
    )

    # Create a meeting
    print("Creating meeting...")
    meeting = client.create_meeting(
        room_id="team-standup-001",
        title="Daily Team Standup",
        description="Daily sync meeting for the engineering team",
        language="en-US",
    )
    print(f"Meeting created: {meeting.id}")

    # Option 1: Add transcript segments manually
    print("\nAdding transcript segments...")
    segments = [
        TranscriptSegment(
            text="Good morning everyone! Let's start our daily standup.",
            speaker="Alice",
            confidence=0.95,
            start_time=0.0,
            end_time=3.5,
        ),
        TranscriptSegment(
            text="I finished the API integration yesterday and today I'll work on the frontend.",
            speaker="Bob",
            confidence=0.92,
            start_time=4.0,
            end_time=8.2,
        ),
        TranscriptSegment(
            text="Great! Let's make sure to add tests for that.",
            speaker="Alice",
            confidence=0.94,
            start_time=8.5,
            end_time=11.0,
        ),
    ]

    for segment in segments:
        meeting.add_transcript_segment(segment)

    # Option 2: Transcribe from audio file (uncomment to use)
    # print("\nTranscribing audio file...")
    # await client.transcribe_audio(meeting, "meeting_recording.mp3")

    # Generate AI summary and action items
    print("\nGenerating AI summary...")
    summary = await client.generate_summary(meeting, include_action_items=True)
    print(f"\nSummary:\n{summary.content}")

    # Print action items
    if meeting.action_items:
        print("\nAction Items:")
        for idx, item in enumerate(meeting.action_items, 1):
            print(f"{idx}. {item.title}")
            if item.assigned_to:
                print(f"   Assigned to: {item.assigned_to}")
            print(f"   Priority: {item.priority.value}")

    # Export to different formats
    print("\nExporting notes...")

    # Export to Markdown
    md_path = await client.export_meeting(meeting, format=ExportFormat.MARKDOWN)
    print(f"Markdown exported to: {md_path}")

    # Export to JSON
    json_path = await client.export_meeting(meeting, format=ExportFormat.JSON)
    print(f"JSON exported to: {json_path}")

    # Export to PDF (requires reportlab)
    try:
        pdf_path = await client.export_meeting(meeting, format=ExportFormat.PDF)
        print(f"PDF exported to: {pdf_path}")
    except ImportError:
        print("PDF export requires reportlab: pip install reportlab")

    # Complete the meeting
    print("\nCompleting meeting...")
    meeting.complete()
    print(f"Meeting completed. Duration: {meeting.duration_minutes():.1f} minutes")


if __name__ == "__main__":
    asyncio.run(main())
