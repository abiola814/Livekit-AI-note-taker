# Quick Start Guide

## Installation

### 1. Install the Package

```bash
# Basic installation
pip install livekit-note-taker

# Or with all features
pip install livekit-note-taker[all]
```

### 2. Set Up LiveKit

You need a LiveKit server. You can either:

**Option A: Use LiveKit Cloud**
- Sign up at https://cloud.livekit.io/
- Get your API key and secret

**Option B: Self-host LiveKit**
```bash
docker run --rm -p 7880:7880 \
  -e LIVEKIT_KEYS="your-api-key: your-api-secret" \
  livekit/livekit-server
```

### 3. Basic Usage

Create a file `test_recording.py`:

```python
import asyncio
import os
from livekit_note_taker import NoteManager
from livekit_note_taker.audio import LiveKitRecorder

async def main():
    # Create recorder
    recorder = LiveKitRecorder(
        livekit_url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )

    # Create manager
    manager = NoteManager(audio_recorder=recorder)

    # Start session
    session = await manager.start_session(
        room_id="test-room",
        title="My First Recording"
    )

    # Start recording
    await manager.start_recording(session.session_id, "user-1")

    print("Recording for 30 seconds...")
    await asyncio.sleep(30)

    # Stop and cleanup
    await manager.stop_recording(session.session_id)
    await manager.end_session(session.session_id)
    await manager.cleanup()

    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
export LIVEKIT_URL="wss://your-server.com"
export LIVEKIT_API_KEY="your-key"
export LIVEKIT_API_SECRET="your-secret"

python test_recording.py
```

## Next Steps

- [API Reference](API.md) - Full API documentation
- [Examples](../examples/) - Complete examples
- [Custom Providers](CUSTOM_PROVIDERS.md) - Implementing custom providers
- [Integration Guide](INTEGRATION.md) - Integrating with your app

## Common Issues

### "Connection refused" or "Connection timeout"

Check that:
1. Your LiveKit server is running
2. The URL is correct (use `wss://` for production, `ws://` for local)
3. Firewall allows connections

### "Invalid token"

Verify:
1. API key and secret are correct
2. No extra spaces in credentials
3. Credentials match your LiveKit server

### No audio captured

Ensure:
1. Participants are actually in the room
2. Participants have their microphones enabled
3. Audio tracks are being published

## Support

- GitHub Issues: https://github.com/yourusername/livekit-note-taker/issues
- Documentation: https://livekit-note-taker.readthedocs.io
- LiveKit Docs: https://docs.livekit.io
