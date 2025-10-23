"""
Example: Transcribing audio files with AI Note.

This example shows how to:
1. Transcribe an audio file
2. Monitor transcription progress
3. Access and work with transcript results
"""

import asyncio
from ainote import AINoteClient


async def main():
    # Initialize client
    client = AINoteClient(
        aws_region="us-east-1",
        ai_provider="openai",
        openai_api_key="sk-your-key-here",
    )

    # Create a meeting
    meeting = client.create_meeting(
        room_id="webinar-001",
        title="Product Launch Webinar",
        language="en-US",
    )

    # Define a progress callback
    async def on_transcript_update(segment):
        """Called when a new transcript segment is available."""
        speaker = segment.speaker or "Unknown"
        confidence = segment.confidence * 100
        print(f"[{speaker}] ({confidence:.1f}%): {segment.text}")

    # Transcribe audio file with progress updates
    print("Transcribing audio file...")
    print("-" * 60)

    audio_file = "webinar_recording.mp3"  # Replace with your audio file

    try:
        await client.transcribe_audio(
            meeting, audio_file_path=audio_file, callback=on_transcript_update
        )
        print("-" * 60)
        print("Transcription complete!")

        # Access full transcript
        print("\nFull Transcript:")
        print("=" * 60)
        print(meeting.transcript.get_full_text())

        # Get transcript statistics
        print("\n\nTranscript Statistics:")
        print(f"Total segments: {len(meeting.transcript.segments)}")
        print(f"Total duration: {meeting.transcript.total_duration():.2f} seconds")

        # Get segments by speaker (if available)
        speakers = set(seg.speaker for seg in meeting.transcript.segments if seg.speaker)
        if speakers:
            print("\nSegments by speaker:")
            for speaker in speakers:
                speaker_segments = meeting.transcript.get_segments_by_speaker(speaker)
                print(f"  {speaker}: {len(speaker_segments)} segments")

        # Generate AI summary from transcript
        print("\nGenerating AI summary...")
        await client.generate_summary(meeting, include_action_items=True)

        print("\nSummary:")
        for note in meeting.notes:
            if note.note_type.value == "summary":
                print(note.content)

        # Export transcript
        from ainote.models import ExportFormat

        print("\nExporting transcript...")
        md_path = await client.export_meeting(meeting, format=ExportFormat.MARKDOWN)
        print(f"Exported to: {md_path}")

    except FileNotFoundError:
        print(f"\nError: Audio file '{audio_file}' not found.")
        print("Please provide a valid audio file path.")
    except Exception as e:
        print(f"\nError during transcription: {e}")


if __name__ == "__main__":
    asyncio.run(main())
