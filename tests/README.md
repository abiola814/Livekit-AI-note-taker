# Tests

This directory contains unit tests for the livekit-note-taker library.

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=livekit_note_taker --cov-report=html

# Run specific test file
pytest tests/test_audio_buffer.py

# Run specific test
pytest tests/test_session.py::test_session_creation

# Run with verbose output
pytest -v

# Run async tests only
pytest -k async
```

### Run Tests with Different Python Versions

```bash
# Using tox (if configured)
tox

# Or manually
python3.8 -m pytest
python3.9 -m pytest
python3.10 -m pytest
python3.11 -m pytest
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_audio_buffer.py     # AudioBuffer tests
├── test_session.py          # MeetingSession tests
├── test_events.py           # Event system tests (TODO)
├── test_transcription.py    # Transcription tests (TODO)
└── README.md               # This file
```

## Writing Tests

### Example Test

```python
import pytest
from livekit_note_taker.audio.buffer import AudioBuffer

@pytest.mark.asyncio
async def test_my_feature():
    """Test description."""
    buffer = AudioBuffer()
    # ... test code ...
    assert expected == actual
```

### Using Fixtures

```python
def test_with_audio(sample_audio_data):
    """Test using fixture."""
    assert len(sample_audio_data) > 0
```

## Test Coverage

View coverage report:

```bash
# Generate HTML report
pytest --cov=livekit_note_taker --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## TODO Tests

Tests that should be added:

- [ ] test_events.py - Event system tests
- [ ] test_manager.py - NoteManager tests
- [ ] test_transcription_aws.py - AWS provider tests (requires mocking)
- [ ] test_recorder.py - LiveKitRecorder tests (requires mocking)
- [ ] Integration tests
- [ ] Performance tests

## Mocking External Services

For tests that require AWS or LiveKit:

```python
from unittest.mock import Mock, patch

@pytest.mark.asyncio
@patch('livekit_note_taker.transcription.aws.TranscribeStreamingClient')
async def test_with_mock_aws(mock_transcribe):
    """Test with mocked AWS."""
    mock_transcribe.return_value = Mock()
    # ... test code ...
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Before releases

See `.github/workflows/test.yml` for CI configuration.
