"""
Simple recording example.

This example shows the minimal code needed to record a LiveKit meeting
and capture audio for transcription.
"""

import asyncio
import logging
from livekit_note_taker import NoteManager
from livekit_note_taker.audio import LiveKitRecorder
from livekit_note_taker.core.events import EventType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main recording function."""

    # Configuration (replace with your actual values)
    LIVEKIT_URL = "wss://your-livekit-server.com"
    LIVEKIT_API_KEY = "your-api-key"
    LIVEKIT_API_SECRET = "your-api-secret"
    ROOM_ID = "my-test-room"

    # Create audio recorder
    recorder = LiveKitRecorder(
        livekit_url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
        buffer_duration_minutes=1,  # Short duration for testing
    )

    # Set up audio batch callback
    async def on_audio_batch(room_id: str, audio_data: bytes):
        """Called when an audio batch is ready."""
        duration_seconds = len(audio_data) / (16000 * 2)  # 16kHz, 16-bit
        logger.info(f"Received audio batch for {room_id}: {duration_seconds:.1f}s of audio")

        # Here you would send audio_data to transcription service
        # For this example, we just log it

    recorder.on_audio_batch = on_audio_batch

    # Create note manager (minimal setup without AI/storage)
    manager = NoteManager(
        audio_recorder=recorder,
    )

    # Set up event listeners
    @manager.event_emitter.on(EventType.SESSION_STARTED)
    async def on_session_started(event):
        logger.info(f"Session started: {event.session_id}")

    @manager.event_emitter.on(EventType.RECORDING_STARTED)
    async def on_recording_started(event):
        logger.info(f"Recording started for room: {event.room_id}")

    @manager.event_emitter.on(EventType.RECORDING_STOPPED)
    async def on_recording_stopped(event):
        logger.info(f"Recording stopped. Duration: {event.data.get('duration_seconds')}s")

    try:
        # Start a session
        logger.info(f"Starting session for room: {ROOM_ID}")
        session = await manager.start_session(
            room_id=ROOM_ID,
            title="Test Recording Session"
        )

        # Add a participant
        await manager.add_participant(
            session.session_id,
            participant_id="test-user",
            participant_name="Test User"
        )

        # Start recording
        logger.info("Starting recording...")
        await manager.start_recording(
            session.session_id,
            started_by="test-user"
        )

        # Record for 5 minutes
        logger.info("Recording for 5 minutes. Join the LiveKit room to test!")
        logger.info(f"Room URL: {LIVEKIT_URL}/{ROOM_ID}")
        await asyncio.sleep(300)

        # Stop recording
        logger.info("Stopping recording...")
        await manager.stop_recording(session.session_id)

        # End session
        logger.info("Ending session...")
        summary = await manager.end_session(session.session_id)
        logger.info(f"Session ended. Duration: {summary.get('duration_seconds')}s")

    except Exception as e:
        logger.error(f"Error during recording: {e}", exc_info=True)

    finally:
        # Cleanup
        logger.info("Cleaning up...")
        await manager.cleanup()

    logger.info("Done!")


if __name__ == "__main__":
    asyncio.run(main())
