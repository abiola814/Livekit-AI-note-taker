# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- OpenAI AI provider implementation
- Anthropic AI provider implementation
- Deepgram transcription provider
- SQLAlchemy storage backend
- PDF export functionality
- FastAPI adapter
- More comprehensive tests

## [0.1.0] - 2024-10-23

### Added
- Initial library structure and core abstractions
- `NoteManager` - Main orchestrator for meeting note-taking
- `MeetingSession` - Session management with participants and state tracking
- `EventEmitter` - Framework-agnostic event system
- `AudioBuffer` - Multi-participant audio buffering and mixing
- `LiveKitRecorder` - LiveKit audio capture implementation
- `AWSTranscriptionProvider` - AWS Transcribe integration with batch processing
- Abstract base classes for pluggable architecture:
  - `TranscriptionProvider` - For speech-to-text services
  - `AIProvider` - For AI summarization services
  - `StorageBackend` - For data persistence
  - `ExportService` - For document export
- Comprehensive documentation:
  - README with quick start guide
  - Testing guide
  - PyPI publishing guide
  - AWS implementation guide
- Example implementations:
  - Simple recorder example
  - AWS transcription example
- Unit tests for core components
- MIT License

### Features
- Real-time audio capture from LiveKit meetings
- Cost-optimized batch transcription (96% cost reduction vs real-time)
- Multi-participant audio mixing
- Event-driven architecture
- Async/await throughout
- Type hints for better IDE support
- Modular, pluggable design

### Documentation
- Complete README with installation and usage
- API documentation in docstrings
- Working examples in `examples/` directory
- Testing guide with troubleshooting
- PyPI publishing workflow
- Transcription provider documentation

## Version History

- **0.1.0** - Initial release with AWS Transcribe support
- **Future** - AI providers, storage backends, export formats

---

## How to Update

When releasing a new version:

1. Update version in `pyproject.toml`
2. Add entry to this CHANGELOG under the new version
3. Commit changes
4. Create git tag: `git tag v0.1.1`
5. Push tag: `git push origin v0.1.1`
6. Create GitHub release
7. Automated workflow publishes to PyPI
