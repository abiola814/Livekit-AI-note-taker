# AI Note Library - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Your Application                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AINoteClient                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  • create_meeting()                                      │   │
│  │  • transcribe_audio()                                    │   │
│  │  • generate_summary()                                    │   │
│  │  • export_meeting()                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                    │              │              │
        ┌───────────┘              │              └────────────┐
        ▼                          ▼                           ▼
┌──────────────┐        ┌──────────────────┐       ┌──────────────┐
│ Transcription│        │   AI Service     │       │  Exporters   │
│   Service    │        │                  │       │              │
└──────────────┘        └──────────────────┘       └──────────────┘
        │                        │                          │
        ▼                        ▼                          ▼
┌──────────────┐        ┌──────────────────┐       ┌──────────────┐
│ AWS Transcribe│       │ OpenAI / Claude  │       │ PDF / MD /   │
│              │        │                  │       │ DOCX / JSON  │
└──────────────┘        └──────────────────┘       └──────────────┘
```

## Component Architecture

### 1. Client Layer

```
AINoteClient
├── Meeting Management
│   ├── create_meeting()
│   ├── get_meeting()
│   ├── list_meetings()
│   └── complete_meeting()
├── Transcription
│   ├── transcribe_audio()
│   └── start_live_transcription()  [future]
├── AI Analysis
│   ├── generate_summary()
│   └── extract_action_items()
└── Export
    └── export_meeting()
```

### 2. Core Layer

```
Meeting
├── Properties
│   ├── transcript (Transcript)
│   ├── notes (List[MeetingNote])
│   ├── action_items (List[ActionItem])
│   └── status (MeetingStatus)
├── Methods
│   ├── add_transcript_segment()
│   ├── add_note()
│   ├── add_action_item()
│   ├── complete()
│   ├── pause()
│   └── resume()
└── Lifecycle
    ├── ACTIVE
    ├── PAUSED
    ├── COMPLETED
    └── ARCHIVED
```

### 3. Service Layer

```
Services
├── TranscriptionService
│   ├── AWS Client
│   ├── S3 Client
│   ├── transcribe_file()
│   ├── transcribe_batch()
│   └── wait_for_completion()
└── AIService
    ├── OpenAI Client
    ├── Anthropic Client
    ├── generate_summary()
    ├── extract_action_items()
    └── extract_key_points()
```

### 4. Model Layer

```
Data Models
├── Transcript Models
│   ├── TranscriptSegment
│   │   ├── text
│   │   ├── speaker
│   │   ├── confidence
│   │   └── timing
│   └── Transcript
│       ├── segments[]
│       ├── get_full_text()
│       └── get_by_speaker()
├── Note Models
│   ├── MeetingNote
│   │   ├── note_type (SUMMARY, KEY_POINTS, etc.)
│   │   ├── content
│   │   └── ai_generated
│   └── ActionItem
│       ├── title
│       ├── priority
│       ├── assigned_to
│       ├── due_date
│       └── status
└── Export Models
    ├── ExportFormat (PDF, MD, DOCX, JSON, TXT)
    └── ExportOptions
```

### 5. Exporter Layer

```
Exporters
├── BaseExporter (Abstract)
│   └── export(meeting, path, options)
├── PDFExporter
│   └── reportlab integration
├── MarkdownExporter
│   └── markdown formatting
├── DOCXExporter
│   └── python-docx integration
├── JSONExporter
│   └── json serialization
└── TXTExporter
    └── plain text formatting
```

## Data Flow

### Transcription Flow

```
1. Audio File
   ↓
2. TranscriptionService.transcribe_file()
   ↓
3. Upload to S3 (if batch)
   ↓
4. AWS Transcribe API
   ↓
5. Poll for completion
   ↓
6. Parse results
   ↓
7. Create TranscriptSegments
   ↓
8. Add to Meeting.transcript
   ↓
9. Return to caller
```

### AI Analysis Flow

```
1. Meeting.transcript.get_full_text()
   ↓
2. AIService.generate_summary()
   ↓
3. AI API Call (OpenAI/Anthropic)
   ↓
4. Parse response
   ↓
5. Create MeetingNote
   ↓
6. Extract action items
   ↓
7. Create ActionItem objects
   ↓
8. Add to Meeting
   ↓
9. Return summary
```

### Export Flow

```
1. Meeting + ExportOptions
   ↓
2. ExporterFactory.create_exporter(format)
   ↓
3. Specific Exporter (PDF/MD/etc.)
   ↓
4. Format meeting data
   ↓
5. Generate file
   ↓
6. Save to disk
   ↓
7. Return file path
```

## Design Patterns

### Factory Pattern
```python
# ExporterFactory creates appropriate exporter
exporter = ExporterFactory.create_exporter(ExportFormat.PDF)
```

### Strategy Pattern
```python
# Different AI providers, same interface
ai_service = AIService(provider="openai")  # or "anthropic"
```

### Builder Pattern
```python
# ExportOptions uses builder-like configuration
options = ExportOptions(
    format=ExportFormat.PDF,
    include_transcripts=True,
    include_summary=True,
)
```

### Async/Await Pattern
```python
# All I/O operations are async
await client.transcribe_audio(meeting, file)
await client.generate_summary(meeting)
```

## Class Relationships

```
AINoteClient
    ├── manages: Meeting[]
    ├── uses: TranscriptionService
    ├── uses: AIService
    └── uses: ExporterFactory

Meeting
    ├── contains: Transcript
    ├── contains: MeetingNote[]
    └── contains: ActionItem[]

Transcript
    └── contains: TranscriptSegment[]

TranscriptionService
    ├── uses: boto3.transcribe
    └── uses: boto3.s3

AIService
    ├── uses: OpenAI client (if provider=openai)
    └── uses: Anthropic client (if provider=anthropic)

ExporterFactory
    ├── creates: PDFExporter
    ├── creates: MarkdownExporter
    ├── creates: DOCXExporter
    ├── creates: JSONExporter
    └── creates: TXTExporter
```

## State Management

### Meeting State Machine

```
     ┌──────────┐
     │  ACTIVE  │ ← (default state)
     └──────────┘
          │
          │ pause()
          ▼
     ┌──────────┐
     │  PAUSED  │
     └──────────┘
          │
          │ resume()
          ▼
     ┌──────────┐
     │  ACTIVE  │
     └──────────┘
          │
          │ complete()
          ▼
     ┌──────────┐
     │COMPLETED │ → (can be archived)
     └──────────┘
          │
          │
          ▼
     ┌──────────┐
     │ ARCHIVED │
     └──────────┘
```

### Action Item State Machine

```
     ┌──────────┐
     │   OPEN   │ ← (default state)
     └──────────┘
          │
          │ mark_in_progress()
          ▼
     ┌─────────────┐
     │ IN_PROGRESS │
     └─────────────┘
          │
          │ mark_completed()
          ▼
     ┌──────────┐
     │COMPLETED │
     └──────────┘

          OR

          │ cancel()
          ▼
     ┌──────────┐
     │CANCELLED │
     └──────────┘
```

## Error Handling

```
AINoteClient
    │
    ├─► TranscriptionService
    │       └─► Handles: AWS errors, S3 errors, timeout
    │
    ├─► AIService
    │       └─► Handles: API errors, rate limits, parsing errors
    │
    └─► Exporters
            └─► Handles: File I/O errors, missing dependencies
```

## Extension Points

### Adding New AI Provider

```python
class AIService:
    def _init_custom_provider(self, api_key: str):
        # Add your provider initialization
        pass

    async def _generate_custom(self, prompt: str) -> str:
        # Add your provider logic
        pass
```

### Adding New Export Format

```python
class CustomExporter(BaseExporter):
    async def export(self, meeting, output_path, options):
        # Implement your export logic
        pass

# Register in ExporterFactory
ExportFormat.CUSTOM = "custom"
exporters[ExportFormat.CUSTOM] = CustomExporter
```

### Adding Database Persistence

```python
class DatabaseBackend:
    def save_meeting(self, meeting: Meeting):
        # Save to database
        pass

    def load_meeting(self, room_id: str) -> Meeting:
        # Load from database
        pass
```

## Performance Considerations

### Memory Usage
- Meetings stored in memory (AINoteClient._meetings dict)
- Transcripts can grow large for long meetings
- Consider clearing completed meetings

### Async Operations
- All I/O is async (transcription, AI, exports)
- Use `asyncio.gather()` for parallel operations
- Avoid blocking operations in async context

### Cost Optimization
- Batch transcription reduces AWS costs
- Cache AI responses when possible
- Use appropriate AI model tiers

## Security Considerations

### API Keys
- Never hardcode API keys
- Use environment variables
- Consider secrets management

### File Handling
- Validate file paths
- Clean up temporary files
- Handle file permissions

### Data Privacy
- Audio files contain sensitive data
- Transcripts may contain PII
- Consider encryption at rest

## Testing Strategy

```
Tests
├── Unit Tests
│   ├── test_client.py (Client functionality)
│   ├── test_meeting.py (Meeting management)
│   └── test_models.py (Data models)
├── Integration Tests
│   ├── AWS Transcribe integration
│   └── AI provider integration
└── End-to-End Tests
    └── Full workflow tests
```

## Future Architecture

Planned enhancements:

```
Future Features
├── Real-time Streaming
│   └── WebSocket support
├── Database Layer
│   └── SQLAlchemy integration
├── Caching Layer
│   └── Redis integration
├── Plugin System
│   ├── Custom exporters
│   └── Custom AI providers
└── Event System
    └── Callback hooks
```
