# Quick Fix for Test Errors

## Issue

Tests are failing with:
```
Failed: async def functions are not natively supported.
Unknown pytest.mark.asyncio
```

## Solution

Install the development dependencies which include `pytest-asyncio`:

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Install with dev dependencies
pip install -e ".[dev,aws]"
```

Or just install pytest-asyncio:

```bash
pip install pytest-asyncio
```

Then run tests again:

```bash
pytest
```

## Complete Setup Commands

Here's the complete sequence:

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# 1. Upgrade pip (if needed)
python -m pip install --upgrade pip

# 2. Install library with dev and AWS dependencies
pip install -e ".[dev,aws]"

# 3. Run tests
pytest

# 4. Run with verbose output
pytest -v

# 5. Run with coverage
pytest --cov=livekit_note_taker
```

## What's Installed

With `[dev,aws]`:
- ✅ Library core (`livekit_note_taker`)
- ✅ AWS dependencies (`boto3`, `amazon-transcribe`)
- ✅ Testing tools (`pytest`, `pytest-asyncio`, `pytest-cov`)
- ✅ Code quality tools (`black`, `ruff`, `mypy`)

## Expected Output After Fix

```
tests/test_audio_buffer.py::test_audio_buffer_creation PASSED     [ 14%]
tests/test_audio_buffer.py::test_add_audio_frame PASSED           [ 28%]
tests/test_audio_buffer.py::test_mixed_audio PASSED               [ 42%]
tests/test_audio_buffer.py::test_buffer_clear PASSED              [ 57%]
tests/test_audio_buffer.py::test_should_process_batch PASSED      [ 71%]
tests/test_audio_buffer.py::test_buffer_info PASSED               [ 85%]
tests/test_session.py::test_session_creation PASSED               [100%]
...

======================== 17 passed in 0.45s ========================
```
