# Changelog

All notable changes to AI Note library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-10-23

### Added
- Initial release of AI Note library
- Core client API for meeting management
- Support for OpenAI and Anthropic AI providers
- AWS Transcribe integration for audio transcription
- Multiple export formats (PDF, Markdown, DOCX, JSON, TXT)
- Automatic summary generation
- Action item extraction
- Transcript management with speaker attribution
- Comprehensive test suite
- Usage examples and documentation
- Type hints throughout the codebase

### Features
- `AINoteClient` - Main client interface
- `Meeting` - Meeting management and lifecycle
- `TranscriptionService` - Audio transcription via AWS
- `AIService` - AI-powered summaries and action items
- Exporters for multiple file formats
- Data models for transcripts, notes, and action items
