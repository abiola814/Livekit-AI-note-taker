"""
Advanced usage example for AI Note library.

This example demonstrates:
1. Multiple meetings management
2. Custom export options
3. Working with action items
4. Using Anthropic Claude
"""

import asyncio
from datetime import datetime, timedelta
from ainote import AINoteClient
from ainote.models import (
    ExportFormat,
    ExportOptions,
    TranscriptSegment,
    ActionItem,
    Priority,
    MeetingStatus,
)


async def main():
    # Initialize client with Anthropic Claude
    client = AINoteClient(
        aws_region="us-east-1",
        ai_provider="anthropic",
        anthropic_api_key="sk-ant-your-key-here",
    )

    # Create multiple meetings
    print("Creating meetings...")
    planning_meeting = client.create_meeting(
        room_id="q1-planning",
        title="Q1 Planning Meeting",
        description="Quarterly planning session",
    )

    retrospective = client.create_meeting(
        room_id="sprint-retro",
        title="Sprint Retrospective",
        description="Sprint 42 retrospective",
    )

    # Add content to planning meeting
    print("\nAdding content to planning meeting...")
    planning_segments = [
        TranscriptSegment(
            text="Let's discuss our Q1 goals and objectives.",
            speaker="CEO",
            confidence=0.96,
        ),
        TranscriptSegment(
            text="We need to focus on customer acquisition and product improvements.",
            speaker="Product Manager",
            confidence=0.94,
        ),
        TranscriptSegment(
            text="I propose we increase our marketing budget by 20% and hire 2 more engineers.",
            speaker="CFO",
            confidence=0.93,
        ),
    ]

    for segment in planning_segments:
        planning_meeting.add_transcript_segment(segment)

    # Generate AI analysis
    print("\nGenerating AI summary...")
    await client.generate_summary(planning_meeting, include_action_items=True)

    # Manually add specific action items with deadlines
    print("\nAdding custom action items...")
    action_items = [
        ActionItem(
            meeting_id=planning_meeting.id,
            title="Increase marketing budget",
            description="Prepare proposal for 20% marketing budget increase",
            assigned_to="CFO",
            priority=Priority.HIGH,
            due_date=datetime.now() + timedelta(days=7),
        ),
        ActionItem(
            meeting_id=planning_meeting.id,
            title="Hire 2 engineers",
            description="Post job listings and start recruitment process",
            assigned_to="HR Manager",
            priority=Priority.URGENT,
            due_date=datetime.now() + timedelta(days=14),
        ),
    ]

    for item in action_items:
        planning_meeting.add_action_item(item)

    # Work with action items
    print("\nAction Items Summary:")
    for item in planning_meeting.action_items:
        status_icon = "🔴" if item.is_overdue() else "✅"
        print(f"{status_icon} {item.title}")
        print(f"   Priority: {item.priority.value} | Assigned: {item.assigned_to}")
        if item.due_date:
            print(f"   Due: {item.due_date.strftime('%Y-%m-%d')}")

    # Export with custom options
    print("\nExporting with custom options...")

    pdf_options = ExportOptions(
        format=ExportFormat.PDF,
        include_transcripts=True,
        include_summary=True,
        include_action_items=True,
        include_metadata=True,
        title="Q1 Planning Meeting - Official Minutes",
        author="AI Note System",
    )

    pdf_path = await client.export_meeting(
        planning_meeting, format=ExportFormat.PDF, options=pdf_options
    )
    print(f"Custom PDF exported to: {pdf_path}")

    # List all meetings
    print("\n\nAll Meetings:")
    all_meetings = client.list_meetings()
    for meeting in all_meetings:
        print(f"- {meeting.title} ({meeting.room_id}) - Status: {meeting.status.value}")

    # Filter active meetings
    active_meetings = client.list_meetings(status=MeetingStatus.ACTIVE)
    print(f"\nActive meetings: {len(active_meetings)}")

    # Complete meetings
    print("\nCompleting meetings...")
    client.complete_meeting(planning_meeting.room_id)
    client.complete_meeting(retrospective.room_id)

    # Export completed meeting info
    print("\nFinal meeting statistics:")
    for meeting in all_meetings:
        if meeting.end_time:
            print(f"{meeting.title}:")
            print(f"  Duration: {meeting.duration_minutes():.1f} minutes")
            print(f"  Transcript segments: {len(meeting.transcript.segments)}")
            print(f"  Notes: {len(meeting.notes)}")
            print(f"  Action items: {len(meeting.action_items)}")


if __name__ == "__main__":
    asyncio.run(main())
