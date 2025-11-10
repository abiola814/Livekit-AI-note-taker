# Contributing to LiveKit Note Taker

Thank you for your interest in contributing! This document provides guidelines and instructions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/livekit-note-taker/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Code samples or error messages

### Suggesting Features

1. Check [existing feature requests](https://github.com/yourusername/livekit-note-taker/issues?q=is%3Aissue+label%3Aenhancement)
2. Create a new issue labeled "enhancement" with:
   - Clear use case description
   - Proposed solution or API
   - Examples of how it would be used

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Update documentation
7. Commit with clear messages
8. Push and create a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/livekit-note-taker.git
cd livekit-note-taker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,all]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## Code Style

We follow PEP 8 and use automated formatting:

```bash
# Format code
black livekit_note_taker/

# Lint
ruff check livekit_note_taker/

# Type checking
mypy livekit_note_taker/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=livekit_note_taker --cov-report=html

# Run specific test
pytest tests/test_audio_buffer.py::test_audio_buffer_creation
```

## Documentation

- Update docstrings for all public APIs
- Follow Google docstring style
- Update README.md if adding user-facing features
- Add examples for new functionality

## Commit Messages

Use clear, descriptive commit messages:

```
Add AWS Transcribe streaming support

- Implement streaming transcription method
- Add async generator for real-time results
- Update documentation with examples
```

## Adding New Providers

### Transcription Provider

1. Create new file in `livekit_note_taker/transcription/`
2. Subclass `TranscriptionProvider`
3. Implement required methods
4. Add tests
5. Update documentation

Example:
```python
from livekit_note_taker.transcription.base import TranscriptionProvider, Transcript

class MyTranscriptionProvider(TranscriptionProvider):
    async def transcribe_audio(self, audio_data, language, sample_rate, **kwargs):
        # Implementation
        return [Transcript(...)]

    async def transcribe_streaming(self, audio_stream, language, sample_rate, **kwargs):
        # Implementation
        async for chunk in audio_stream:
            yield Transcript(...)

    async def close(self):
        # Cleanup
        pass
```

### AI Provider

Similar process in `livekit_note_taker/ai/`:

```python
from livekit_note_taker.ai.base import AIProvider, SummaryResult

class MyAIProvider(AIProvider):
    async def generate_summary(self, transcripts, is_final=False, **kwargs):
        # Implementation
        return SummaryResult(...)

    async def extract_action_items(self, transcripts, **kwargs):
        # Implementation
        return [...]

    async def close(self):
        pass
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Commit: `git commit -m "Bump version to 0.2.0"`
4. Tag: `git tag v0.2.0`
5. Push: `git push origin v0.2.0`
6. Create GitHub release
7. CI automatically publishes to PyPI

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## Questions?

- Open a [Discussion](https://github.com/yourusername/livekit-note-taker/discussions)
- Join our community chat (if available)
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
