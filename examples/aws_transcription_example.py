"""
AWS Transcribe Integration Example.

This example demonstrates how to use the AWS Transcribe provider with
the LiveKit Note Taker library for automated meeting transcription.
"""

import asyncio
import logging
import os
from datetime import datetime

from livekit_note_taker import NoteManager
from livekit_note_taker.audio import LiveKitRecorder
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
from livekit_note_taker.core.events import EventType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function demonstrating AWS Transcribe integration."""

    # Configuration from environment variables
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.com")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "your-api-key")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "your-api-secret")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    ROOM_ID = os.getenv("ROOM_ID", "test-room")

    logger.info("=" * 60)
    logger.info("AWS Transcribe Integration Example")
    logger.info("=" * 60)

    # Create AWS Transcribe provider
    transcription_provider = AWSTranscriptionProvider(
        region=AWS_REGION,
        language_code="en-US",
        sample_rate=16000
    )
    logger.info(f"Created AWS Transcribe provider: {transcription_provider}")

    # Create audio recorder
    recorder = LiveKitRecorder(
        livekit_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
        buffer_duration_minutes=1,  # Short duration for testing
    )
    logger.info("Created LiveKit recorder")

    # Set up audio batch callback to trigger transcription
    async def on_audio_batch(room_id: str, audio_data: bytes):
        """Called when an audio batch is ready for transcription."""
        duration_seconds = len(audio_data) / (16000 * 2)  # 16kHz, 16-bit
        logger.info(f"🎵 Received audio batch: {duration_seconds:.1f}s of audio")

        try:
            # Transcribe the audio
            logger.info("📝 Starting transcription with AWS Transcribe...")
            transcripts = await transcription_provider.transcribe_audio(
                audio_data=audio_data,
                language="en-US",
                sample_rate=16000
            )

            # Log the transcripts
            logger.info(f"✅ Transcription complete: {len(transcripts)} segments")
            for i, transcript in enumerate(transcripts, 1):
                logger.info(
                    f"  [{i}] {transcript.text} "
                    f"(confidence: {transcript.confidence:.2f})"
                )

                # Here you would normally save to database or emit events
                # For this example, we just log

        except Exception as e:
            logger.error(f"❌ Error transcribing audio: {e}", exc_info=True)

    recorder.on_audio_batch = on_audio_batch

    # Create note manager
    manager = NoteManager(
        audio_recorder=recorder,
        transcription_provider=transcription_provider,
    )
    logger.info("Created NoteManager")

    # Set up event listeners
    @manager.event_emitter.on(EventType.SESSION_STARTED)
    async def on_session_started(event):
        logger.info(f"🎬 Session started: {event.session_id}")

    @manager.event_emitter.on(EventType.RECORDING_STARTED)
    async def on_recording_started(event):
        logger.info(f"🔴 Recording started for room: {event.room_id}")

    @manager.event_emitter.on(EventType.RECORDING_STOPPED)
    async def on_recording_stopped(event):
        duration = event.data.get('duration_seconds', 0)
        logger.info(f"⏹️  Recording stopped. Duration: {duration:.1f}s")

    @manager.event_emitter.on(EventType.PARTICIPANT_JOINED)
    async def on_participant_joined(event):
        logger.info(
            f"👤 Participant joined: {event.data.get('participant_name')} "
            f"({event.data.get('participant_id')})"
        )

    try:
        # Start a session
        logger.info(f"\n📌 Starting session for room: {ROOM_ID}")
        session = await manager.start_session(
            room_id=ROOM_ID,
            title="AWS Transcribe Test Session",
            description=f"Testing AWS Transcribe integration at {datetime.utcnow().isoformat()}"
        )
        logger.info(f"Session ID: {session.session_id}")

        # Add a test participant
        await manager.add_participant(
            session.session_id,
            participant_id="test-user",
            participant_name="Test User"
        )

        # Start recording
        logger.info("\n🎙️  Starting recording...")
        await manager.start_recording(
            session.session_id,
            started_by="test-user"
        )

        # Recording instructions
        logger.info("\n" + "=" * 60)
        logger.info("RECORDING IN PROGRESS")
        logger.info("=" * 60)
        logger.info(f"Room: {ROOM_ID}")
        logger.info(f"LiveKit URL: {LIVEKIT_URL}")
        logger.info("")
        logger.info("To test:")
        logger.info("1. Join the room using LiveKit's example app")
        logger.info("2. Speak into your microphone")
        logger.info("3. Watch the console for transcriptions")
        logger.info("")
        logger.info("Recording for 5 minutes (or press Ctrl+C to stop)...")
        logger.info("=" * 60 + "\n")

        # Record for 5 minutes
        await asyncio.sleep(300)

        # Stop recording
        logger.info("\n⏹️  Stopping recording...")
        await manager.stop_recording(session.session_id)

        # End session
        logger.info("🏁 Ending session...")
        summary = await manager.end_session(session.session_id)

        logger.info("\n" + "=" * 60)
        logger.info("SESSION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Duration: {summary.get('duration_seconds', 0):.1f}s")
        logger.info(f"Participants: {summary.get('stats', {}).get('total_participants', 0)}")
        logger.info(f"Transcripts: {summary.get('stats', {}).get('total_transcripts', 0)}")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        try:
            await manager.stop_recording(session.session_id)
            await manager.end_session(session.session_id)
        except:
            pass

    except Exception as e:
        logger.error(f"❌ Error during recording: {e}", exc_info=True)

    finally:
        # Cleanup
        logger.info("\n🧹 Cleaning up...")
        await manager.cleanup()
        await transcription_provider.close()

    logger.info("\n✅ Done!")


if __name__ == "__main__":
    # Check for AWS credentials
    import boto3
    try:
        # This will raise an exception if credentials are not configured
        boto3.client('sts').get_caller_identity()
        logger.info("✅ AWS credentials found")
    except Exception as e:
        logger.error(
            "❌ AWS credentials not configured. "
            "Please configure AWS credentials using one of these methods:\n"
            "  1. AWS CLI: aws configure\n"
            "  2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY\n"
            "  3. IAM role (if running on EC2/ECS)\n"
        )
        exit(1)

    # Run the example
    asyncio.run(main())
