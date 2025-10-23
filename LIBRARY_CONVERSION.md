# AI Note-Take to Library Conversion

This document explains the conversion of the AI Note-Take application into a reusable Python library.

## Overview

The original `ai-note-take` project was a full-stack application with:
- FastAPI/SocketIO server
- LiveKit integration for audio capture
- WebSocket-based real-time updates
- Database persistence (SQLAlchemy)
- Web-based client interface

The new `ainote` library is a **Python-only library** that can be integrated into any Python project.

## What Changed

### Architecture

**Before (Application):**
```
Web Client ←→ WebSocket Server ←→ LiveKit ←→ AWS Transcribe
                      ↓
                  Database
                      ↓
                 AI Services
```

**After (Library):**
```
Your Python Code → AINoteClient → AWS Transcribe → AI Services
                                       ↓
                                  Export Files
```

### Key Differences

| Feature | Application | Library |
|---------|------------|---------|
| Architecture | Server-based | Client library |
| API | WebSocket/HTTP | Python API |
| Real-time | Yes (WebSocket) | No (batch processing) |
| Audio Capture | LiveKit | File-based |
| Database | Built-in (SQLAlchemy) | Optional (not included) |
| Deployment | Server deployment | pip install |
| Integration | Web clients | Python code |

## Migration Guide

### From Application to Library

If you were using the application:

**Before (Application):**
```javascript
// JavaScript client
socket.emit('join_meeting', {
    room_id: "meeting-123",
    title: "Team Meeting"
});

socket.on('note_update', (data) => {
    console.log(data);
});
```

**After (Library):**
```python
# Python library
import asyncio
from ainote import AINoteClient

async def main():
    client = AINoteClient(
        ai_provider="openai",
        openai_api_key="sk-..."
    )

    meeting = client.create_meeting(
        room_id="meeting-123",
        title="Team Meeting"
    )

    # Process audio
    await client.transcribe_audio(meeting, "recording.mp3")

    # Generate notes
    await client.generate_summary(meeting)

asyncio.run(main())
```

## What's Included

### Core Features Preserved

✅ **Transcription**
- AWS Transcribe integration
- Batch processing for cost savings
- Multiple language support

✅ **AI Analysis**
- Summary generation
- Action item extraction
- Support for OpenAI and Anthropic

✅ **Export Functionality**
- PDF export
- Markdown export
- DOCX export
- JSON export
- TXT export

✅ **Data Models**
- Transcript segments
- Meeting notes
- Action items

### Features Not Included

❌ **Real-time Features**
- WebSocket support (can be added)
- Live audio streaming
- Real-time updates

❌ **Server Components**
- FastAPI server
- SocketIO handlers
- HTTP endpoints

❌ **LiveKit Integration**
- Audio capture
- Multi-participant mixing
- Real-time streaming

❌ **Database Layer**
- SQLAlchemy models (included as reference in docs)
- Database persistence
- Query functionality

❌ **Web Interface**
- HTML/JavaScript client
- WebSocket connection management

## Adding Missing Features

### Database Persistence

You can add database support:

```python
from ainote import AINoteClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Your existing database models
from your_app.models import Meeting, Transcript

client = AINoteClient(...)
meeting = client.create_meeting(...)

# Save to database
db_meeting = Meeting(
    room_id=meeting.room_id,
    title=meeting.title,
    # ... other fields
)
session.add(db_meeting)
session.commit()
```

### WebSocket Support

You can wrap the library in a WebSocket server:

```python
import socketio
from ainote import AINoteClient

sio = socketio.AsyncServer()
client = AINoteClient(...)

@sio.on('create_meeting')
async def on_create_meeting(sid, data):
    meeting = client.create_meeting(**data)
    await sio.emit('meeting_created', meeting.to_dict(), room=sid)

# Continue with your WebSocket handlers...
```

### Real-time Transcription

For live transcription, you'll need to implement:

```python
class LiveTranscriptionHandler:
    def __init__(self, client: AINoteClient):
        self.client = client

    async def handle_audio_stream(self, meeting, audio_stream):
        # Implement streaming logic
        # This would integrate with LiveKit or similar service
        pass
```

## Use Cases

### Best For

✅ Offline transcription processing
✅ Batch audio file processing
✅ Integration into existing Python apps
✅ CLI tools and scripts
✅ Backend services
✅ Data processing pipelines

### Not Ideal For

❌ Real-time live transcription (without additional work)
❌ Browser-based applications (use original app)
❌ Multi-user concurrent sessions (without additional work)
❌ WebSocket-based real-time updates (without wrapper)

## Example Integration

### Django Integration

```python
# views.py
from django.http import JsonResponse
from ainote import AINoteClient
import asyncio

client = AINoteClient(...)

def transcribe_meeting(request, meeting_id):
    meeting = client.create_meeting(
        room_id=meeting_id,
        title=request.POST['title']
    )

    # Run async code
    asyncio.run(client.transcribe_audio(
        meeting,
        request.FILES['audio'].temporary_file_path()
    ))

    return JsonResponse(meeting.to_dict())
```

### Flask Integration

```python
# app.py
from flask import Flask, request, jsonify
from ainote import AINoteClient
import asyncio

app = Flask(__name__)
client = AINoteClient(...)

@app.route('/meetings', methods=['POST'])
def create_meeting():
    meeting = client.create_meeting(
        room_id=request.json['room_id'],
        title=request.json['title']
    )
    return jsonify(meeting.to_dict())

@app.route('/meetings/<room_id>/transcribe', methods=['POST'])
def transcribe(room_id):
    meeting = client.get_meeting(room_id)
    audio_file = request.files['audio']

    asyncio.run(client.transcribe_audio(meeting, audio_file))
    return jsonify(meeting.to_dict())
```

### FastAPI Integration

```python
# main.py
from fastapi import FastAPI, UploadFile
from ainote import AINoteClient

app = FastAPI()
client = AINoteClient(...)

@app.post("/meetings")
async def create_meeting(room_id: str, title: str):
    meeting = client.create_meeting(room_id=room_id, title=title)
    return meeting.to_dict()

@app.post("/meetings/{room_id}/transcribe")
async def transcribe(room_id: str, audio: UploadFile):
    meeting = client.get_meeting(room_id)
    await client.transcribe_audio(meeting, audio.file)
    return meeting.to_dict()
```

## Performance Considerations

### Memory Usage
- The library keeps meetings in memory
- For production, consider persisting to database
- Clear completed meetings periodically

### Async Operations
- All transcription and AI operations are async
- Use `asyncio.run()` in synchronous contexts
- Consider using task queues for background processing

### Cost Optimization
- Batch transcription reduces AWS costs
- Consider caching AI summaries
- Implement rate limiting for AI API calls

## Future Roadmap

Potential enhancements:

1. **Database Backend** - Optional SQLAlchemy integration
2. **Real-time Support** - WebSocket wrapper
3. **LiveKit Plugin** - Direct LiveKit integration
4. **Streaming API** - Live transcription support
5. **Caching Layer** - Redis/Memcached support
6. **Event System** - Callbacks for transcription events
7. **Plugin System** - Custom exporters and processors

## Getting Help

- Check [README.md](README.md) for basic usage
- See [QUICKSTART.md](QUICKSTART.md) for quick start
- Review [examples/](examples/) for code samples
- Open issues on GitHub for bugs/questions

## Contributing

The library is designed to be extended. Contributions welcome!

Areas for contribution:
- New export formats
- Additional AI providers
- Performance optimizations
- Documentation improvements
- More examples
