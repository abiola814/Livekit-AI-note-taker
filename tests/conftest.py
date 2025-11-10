"""Pytest configuration and fixtures."""

import pytest
import asyncio


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_audio_data():
    """Provide sample audio data for testing."""
    import numpy as np
    # Generate 1 second of audio at 16kHz
    sample_rate = 16000
    duration = 1  # seconds
    audio_array = np.random.randint(-1000, 1000, size=sample_rate * duration, dtype=np.int16)
    return audio_array.tobytes()


@pytest.fixture
def sample_transcript():
    """Provide sample transcript data."""
    return {
        "text": "This is a test transcript",
        "confidence": 0.95,
        "speaker_id": "user-1",
        "speaker_name": "Test User",
        "timestamp": "2024-01-01T00:00:00Z"
    }
