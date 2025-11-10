# LiveKit Note Taker

A modular, extensible Python library for building AI-powered meeting note-taking applications with LiveKit.

## Features

- **Real-time Audio Capture**: Connect to LiveKit meetings and capture audio from multiple participants
- **Cost-Optimized Batch Transcription**: Reduce transcription costs by up to 96% using intelligent batching
- **Multi-participant Audio Mixing**: Automatically mix audio from all participants
- **AI-Powered Summaries**: Generate meeting summaries and extract action items using OpenAI, Anthropic, or other providers
- **Pluggable Architecture**: Swap out transcription services, AI providers, and storage backends
- **Multiple Export Formats**: Export to PDF, Markdown, DOCX, JSON
- **Event-Driven**: React to real-time events without coupling to specific frameworks
- **Framework Agnostic**: Use with FastAPI, Flask, or any async Python framework

## Installation

### Basic Installation

```bash
pip install livekit-note-taker
```

### With AWS Transcribe Support

```bash
pip install livekit-note-taker[aws]
```

### With AI Providers

```bash
pip install livekit-note-taker[ai]
```

### With Storage Backends

```bash
pip install livekit-note-taker[storage]
```

### With Export Functionality

```bash
pip install livekit-note-taker[export]
```

### With FastAPI Integration

```bash
pip install livekit-note-taker[fastapi]
```

### Complete Installation (All Features)

```bash
pip install livekit-note-taker[all]
```

## Quick Start

### Basic Usage

```python
import asyncio
from livekit_note_taker import NoteManager
from livekit_note_taker.audio import LiveKitRecorder
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
from livekit_note_taker.ai.openai import OpenAIProvider

async def main():
    # Initialize components
    recorder = LiveKitRecorder(
        livekit_url="wss://your-livekit-server.com",
        api_key="your-api-key",
        api_secret="your-api-secret"
    )

    transcription = AWSTranscriptionProvider(
        region="us-east-1"
    )

    ai_provider = OpenAIProvider(
        api_key="your-openai-key"
    )

    # Create note manager
    manager = NoteManager(
        audio_recorder=recorder,
        transcription_provider=transcription,
        ai_provider=ai_provider
    )

    # Start a session
    session = await manager.start_session(
        room_id="my-room",
        title="Team Standup"
    )

    # Add participants
    await manager.add_participant(
        session.session_id,
        participant_id="user-123",
        participant_name="John Doe"
    )

    # Start recording
    await manager.start_recording(
        session.session_id,
        started_by="user-123"
    )

    # ... meeting happens ...
    await asyncio.sleep(300)  # 5 minutes

    # Stop recording
    await manager.stop_recording(session.session_id)

    # End session
    summary = await manager.end_session(session.session_id)
    print(f"Meeting summary: {summary}")

    # Cleanup
    await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Event-Driven Usage

```python
from livekit_note_taker import NoteManager
from livekit_note_taker.core.events import EventType

async def main():
    manager = NoteManager(...)

    # Listen to events
    @manager.event_emitter.on(EventType.TRANSCRIPTION_BATCH)
    async def on_transcription(event):
        print(f"New transcription: {event.data['text']}")

    @manager.event_emitter.on(EventType.SUMMARY_GENERATED)
    async def on_summary(event):
        print(f"Summary: {event.data['summary']}")

    # Start session
    session = await manager.start_session("my-room")
    await manager.start_recording(session.session_id, "user-123")
```

## Architecture

The library is organized into modular components:

```
livekit_note_taker/
├── core/                  # Core abstractions (NoteManager, Events, Sessions)
├── audio/                 # Audio capture and buffering
├── transcription/         # Transcription provider interfaces
├── ai/                    # AI provider interfaces
├── storage/               # Storage backend interfaces
├── export/                # Export format implementations
└── adapters/              # Framework-specific adapters
```

### Core Components

- **NoteManager**: Main orchestrator for meeting sessions
- **MeetingSession**: Represents a meeting with participants and state
- **EventEmitter**: Framework-agnostic event system
- **AudioBuffer**: Efficient multi-participant audio mixing
- **LiveKitRecorder**: Audio capture from LiveKit rooms

### Plugin Architecture

All major components use abstract base classes for easy extension:

- **TranscriptionProvider**: Implement custom transcription services
- **AIProvider**: Implement custom AI/LLM services
- **StorageBackend**: Implement custom storage solutions
- **ExportService**: Implement custom export formats

## Cost Optimization

The library uses **batch transcription** instead of real-time streaming, which reduces costs dramatically:

**Real-time Transcription Cost:**
- 5 participants × 60 minutes = 300 minutes of streaming
- AWS Transcribe: $0.02/min = **$6.00**

**Batch Transcription Cost:**
- Batch every 15 minutes = 4 batches/hour
- Mixed audio (1 stream) × 4 batches = 4 minutes of transcription
- AWS Transcribe: $0.02/min = **$0.08**

**Savings: 96% cost reduction!**

## Examples

See the [examples/](examples/) directory for complete working examples:

- `simple_recorder.py` - Minimal recording example
- `fastapi_server.py` - Full FastAPI integration
- `custom_provider.py` - Implementing custom providers

## Documentation

Full documentation available at: https://livekit-note-taker.readthedocs.io

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/livekit-note-taker.git
cd livekit-note-taker
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black livekit_note_taker/
ruff check livekit_note_taker/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Built on top of:
- [LiveKit](https://livekit.io/) - Real-time audio/video infrastructure
- [AWS Transcribe](https://aws.amazon.com/transcribe/) - Speech-to-text
- [OpenAI](https://openai.com/) / [Anthropic](https://anthropic.com/) - AI summarization
