# Examples

This directory contains example implementations using the LiveKit Note Taker library.

## Examples

### 1. Simple Recorder (`simple_recorder.py`)

Minimal example showing basic recording functionality.

**Features:**
- Connect to LiveKit room
- Capture and buffer audio
- Basic event handling

**Usage:**
```bash
# Update configuration in the file first
python examples/simple_recorder.py
```

### 2. Full FastAPI Server (`fastapi_server.py`)

Complete implementation with FastAPI, WebSockets, and all features.

**Features:**
- Full REST API
- WebSocket real-time updates
- AI summarization
- Database storage
- Export functionality

**Usage:**
```bash
pip install livekit-note-taker[all]
python examples/fastapi_server.py
```

### 3. Custom Provider (`custom_provider.py`)

Example showing how to implement custom providers.

**Features:**
- Custom transcription provider
- Custom AI provider
- Custom storage backend

**Usage:**
```bash
python examples/custom_provider.py
```

## Configuration

All examples require LiveKit credentials. You can set them via:

1. **Environment Variables:**
```bash
export LIVEKIT_URL="wss://your-server.com"
export LIVEKIT_API_KEY="your-key"
export LIVEKIT_API_SECRET="your-secret"
```

2. **Direct Configuration:**
Edit the example files and update the configuration constants.

## Testing

To test the examples:

1. Set up a LiveKit server (or use LiveKit Cloud)
2. Configure your credentials
3. Run the example
4. Join the room with LiveKit's example client to generate audio
5. Watch the logs for transcription and events

## More Examples

For more advanced usage, check out:
- [Original Implementation](../../ai-note-take/) - The full application this library was extracted from
- [Documentation](https://livekit-note-taker.readthedocs.io) - Complete API documentation
