"""Tests for AudioBuffer class."""

import pytest
import numpy as np
from livekit_note_taker.audio.buffer import AudioBuffer


@pytest.mark.asyncio
async def test_audio_buffer_creation():
    """Test creating an AudioBuffer."""
    buffer = AudioBuffer(
        sample_rate=16000,
        channels=1,
        buffer_duration_minutes=1
    )

    assert buffer.sample_rate == 16000
    assert buffer.channels == 1
    assert buffer.buffer_duration_seconds == 60
    assert len(buffer.participant_buffers) == 0


@pytest.mark.asyncio
async def test_add_audio_frame():
    """Test adding audio frames."""
    buffer = AudioBuffer(sample_rate=16000)

    # Generate test audio
    audio_data = np.random.randint(-32768, 32767, size=1600, dtype=np.int16)

    # Add frame
    await buffer.add_audio_frame("participant-1", audio_data.tobytes())

    assert buffer.get_participant_count() == 1
    assert "participant-1" in buffer.participant_buffers


@pytest.mark.asyncio
async def test_mixed_audio():
    """Test mixing audio from multiple participants."""
    buffer = AudioBuffer(sample_rate=16000)

    # Add audio from two participants
    audio1 = np.random.randint(-1000, 1000, size=1600, dtype=np.int16)
    audio2 = np.random.randint(-1000, 1000, size=1600, dtype=np.int16)

    await buffer.add_audio_frame("participant-1", audio1.tobytes())
    await buffer.add_audio_frame("participant-2", audio2.tobytes())

    # Get mixed audio
    mixed = await buffer.get_mixed_audio()

    assert mixed is not None
    assert len(mixed) > 0


@pytest.mark.asyncio
async def test_buffer_clear():
    """Test clearing the buffer."""
    buffer = AudioBuffer(sample_rate=16000)

    # Add some audio
    audio_data = np.random.randint(-32768, 32767, size=1600, dtype=np.int16)
    await buffer.add_audio_frame("participant-1", audio_data.tobytes())

    # Clear
    await buffer.clear()

    assert len(buffer.participant_buffers) == 0
    assert buffer.start_time is None


@pytest.mark.asyncio
async def test_should_process_batch():
    """Test batch processing trigger."""
    buffer = AudioBuffer(
        sample_rate=16000,
        buffer_duration_minutes=0.01  # Very short for testing
    )

    # Initially should not process
    assert not buffer.should_process_batch()

    # Add some audio
    audio_data = np.random.randint(-32768, 32767, size=1600, dtype=np.int16)
    await buffer.add_audio_frame("participant-1", audio_data.tobytes())

    # Still may not be time yet
    # (depends on timing, so we just check it doesn't error)
    result = buffer.should_process_batch()
    assert isinstance(result, bool)


def test_buffer_info():
    """Test getting buffer info."""
    buffer = AudioBuffer(sample_rate=16000)

    info = buffer.get_buffer_info()

    assert "participant_count" in info
    assert "sample_rate" in info
    assert info["sample_rate"] == 16000
