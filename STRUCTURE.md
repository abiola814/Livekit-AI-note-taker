# AI Note Library - Project Structure

This document provides an overview of the AI Note library structure and organization.

## Directory Layout

```
ai-note-library/
├── ainote/                      # Main package
│   ├── __init__.py             # Package initialization and exports
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── client.py           # Main AINoteClient class
│   │   └── meeting.py          # Meeting management
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── transcript.py       # Transcript and segment models
│   │   ├── note.py             # Meeting notes and action items
│   │   └── export.py           # Export format options
│   ├── services/               # External service integrations
│   │   ├── __init__.py
│   │   ├── transcription.py    # AWS Transcribe integration
│   │   └── ai_service.py       # OpenAI/Anthropic integration
│   ├── exporters/              # File format exporters
│   │   ├── __init__.py
│   │   ├── exporter.py         # Base exporter and factory
│   │   ├── pdf_exporter.py     # PDF export
│   │   ├── markdown_exporter.py # Markdown export
│   │   ├── docx_exporter.py    # Word document export
│   │   ├── json_exporter.py    # JSON export
│   │   └── txt_exporter.py     # Plain text export
│   └── utils/                  # Utility functions
│       └── __init__.py
├── examples/                   # Usage examples
│   ├── basic_usage.py          # Basic example
│   ├── advanced_usage.py       # Advanced features
│   └── transcribe_audio.py     # Audio transcription example
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_client.py          # Client tests
│   ├── test_meeting.py         # Meeting tests
│   └── test_models.py          # Model tests
├── docs/                       # Documentation
├── setup.py                    # Package setup (setuptools)
├── pyproject.toml              # Modern package configuration
├── requirements.txt            # Core dependencies
├── requirements-dev.txt        # Development dependencies
├── MANIFEST.in                 # Package manifest
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```

## Core Components

### 1. Client (`ainote/core/client.py`)

The `AINoteClient` is the main entry point for the library:

```python
client = AINoteClient(
    aws_region="us-east-1",
    ai_provider="openai",
    openai_api_key="sk-..."
)
```

**Key Methods:**
- `create_meeting()` - Create a new meeting
- `get_meeting()` - Retrieve a meeting
- `list_meetings()` - List all meetings
- `transcribe_audio()` - Transcribe audio files
- `generate_summary()` - Generate AI summaries
- `export_meeting()` - Export notes to files

### 2. Meeting (`ainote/core/meeting.py`)

The `Meeting` class represents a meeting session:

```python
meeting = Meeting(
    room_id="meeting-123",
    title="Team Standup",
    language="en-US"
)
```

**Properties:**
- `transcript` - Meeting transcript
- `notes` - Meeting notes
- `action_items` - Action items
- `status` - Meeting status

### 3. Data Models (`ainote/models/`)

#### Transcript Models
- `TranscriptSegment` - Single piece of transcribed text
- `Transcript` - Complete meeting transcript

#### Note Models
- `MeetingNote` - Summaries, key points, etc.
- `ActionItem` - Extracted action items
- `NoteType` - Types of notes (summary, action_items, etc.)
- `Priority` - Action item priorities
- `ActionItemStatus` - Action item status

#### Export Models
- `ExportFormat` - Supported export formats
- `ExportOptions` - Export configuration

### 4. Services (`ainote/services/`)

#### TranscriptionService
Handles audio transcription via AWS Transcribe:

```python
segments = await transcription_service.transcribe_file(
    "audio.mp3",
    language="en-US"
)
```

#### AIService
AI-powered analysis using OpenAI or Anthropic:

```python
summary = await ai_service.generate_summary(transcript_text)
action_items = await ai_service.extract_action_items(transcript_text)
```

### 5. Exporters (`ainote/exporters/`)

Multiple export format support:

- **PDFExporter** - Professional PDF documents (requires `reportlab`)
- **MarkdownExporter** - Markdown format
- **DOCXExporter** - Microsoft Word (requires `python-docx`)
- **JSONExporter** - Machine-readable JSON
- **TXTExporter** - Plain text

All exporters implement the `BaseExporter` interface.

## Usage Flow

```
1. Initialize Client
   ↓
2. Create Meeting
   ↓
3. Add Transcript
   ├─→ Transcribe Audio File
   └─→ Add Segments Manually
   ↓
4. Generate AI Analysis
   ├─→ Summary
   └─→ Action Items
   ↓
5. Export Notes
   ├─→ PDF
   ├─→ Markdown
   ├─→ DOCX
   ├─→ JSON
   └─→ TXT
   ↓
6. Complete Meeting
```

## Dependencies

### Core Dependencies
- `boto3` - AWS SDK for transcription

### Optional Dependencies
- `openai` - For OpenAI GPT models
- `anthropic` - For Anthropic Claude models
- `reportlab` - For PDF export
- `python-docx` - For DOCX export

### Development Dependencies
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## Testing

Run tests:
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=ainote
```

## Building and Publishing

```bash
# Build distribution
python -m build

# Install locally
pip install -e .

# Publish to PyPI
python -m twine upload dist/*
```

## Design Principles

1. **Simple API** - Easy to use, hard to misuse
2. **Type Safety** - Full type hints throughout
3. **Async First** - Built with async/await
4. **Extensible** - Easy to add new features
5. **Well Tested** - Comprehensive test coverage
6. **Well Documented** - Examples and docs

## Future Enhancements

Potential additions for future versions:

- Live streaming transcription
- WebSocket support for real-time updates
- Database persistence layer
- More AI providers (Azure OpenAI, etc.)
- Additional export formats (HTML, etc.)
- Audio file processing utilities
- Speaker diarization improvements
- Multi-language support enhancements

## Contributing

See the main README for contribution guidelines.

## License

MIT License - see LICENSE file for details.
