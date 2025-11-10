# Transcription Providers

This module provides abstraction for speech-to-text transcription services.

## Available Providers

### AWS Transcribe

**Status**: ✅ Implemented

The AWS Transcribe provider uses Amazon Transcribe Streaming API for cost-effective batch transcription.

**Installation:**
```bash
pip install livekit-note-taker[aws]
```

**Usage:**
```python
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider

# Create provider
provider = AWSTranscriptionProvider(
    region="us-east-1",
    language_code="en-US"
)

# Transcribe audio
transcripts = await provider.transcribe_audio(
    audio_data=audio_bytes,
    language="en-US",
    sample_rate=16000
)

# Process transcripts
for transcript in transcripts:
    print(f"{transcript.text} (confidence: {transcript.confidence})")

# Cleanup
await provider.close()
```

**Features:**
- Streaming transcription API
- Automatic batching for cost optimization
- Support for multiple languages
- Confidence scores
- Timestamp tracking

**Requirements:**
- AWS credentials configured (via AWS CLI, environment variables, or IAM role)
- `boto3` and `amazon-transcribe` packages
- Active AWS account with Transcribe permissions

**Configuration:**
- `region`: AWS region (default: "us-east-1")
- `language_code`: Language for transcription (default: "en-US")
- `sample_rate`: Audio sample rate in Hz (default: 16000)

### Other Providers

You can implement custom transcription providers by subclassing `TranscriptionProvider`:

```python
from livekit_note_taker.transcription.base import TranscriptionProvider, Transcript

class MyTranscriptionProvider(TranscriptionProvider):
    async def transcribe_audio(self, audio_data, language, sample_rate, **kwargs):
        # Your implementation
        transcripts = []
        # ... process audio ...
        return transcripts

    async def transcribe_streaming(self, audio_stream, language, sample_rate, **kwargs):
        # Your streaming implementation
        async for chunk in audio_stream:
            # ... process chunk ...
            yield Transcript(text="...", confidence=0.9)

    async def close(self):
        # Cleanup
        pass
```

## Supported Languages

AWS Transcribe supports many languages. Common ones:

- `en-US` - English (US)
- `en-GB` - English (UK)
- `es-US` - Spanish (US)
- `fr-FR` - French (France)
- `de-DE` - German (Germany)
- `ja-JP` - Japanese
- `zh-CN` - Chinese (Mandarin)

See [AWS Transcribe documentation](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html) for the full list.

## Cost Optimization

The library uses **batch transcription** to significantly reduce costs:

### Real-time Streaming (Expensive)
```
5 participants × 60 minutes = 300 minutes
AWS Transcribe: $0.02/min = $6.00/hour
```

### Batch Processing (Cost-Effective)
```
Mixed audio batch every 15 minutes = 4 batches/hour
AWS Transcribe: $0.02/min × 4 = $0.08/hour
```

**Savings: 96% cost reduction!**

## Examples

See `examples/aws_transcription_example.py` for a complete working example.

## Testing

To test the AWS provider:

```bash
# Set up AWS credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_REGION="us-east-1"

# Set up LiveKit
export LIVEKIT_URL="wss://your-server.com"
export LIVEKIT_API_KEY="your-key"
export LIVEKIT_API_SECRET="your-secret"

# Run the example
python examples/aws_transcription_example.py
```

## Troubleshooting

### "Unable to locate credentials"
Configure AWS credentials using one of these methods:
1. AWS CLI: `aws configure`
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. IAM role (if running on EC2/ECS)

### "Access Denied" errors
Ensure your AWS IAM user/role has the `transcribe:StartStreamTranscription` permission.

### No transcripts returned
Check that:
1. Audio data is valid PCM format
2. Sample rate matches the configuration
3. Audio contains speech (not silence)
4. Language code is correct

## Future Providers

Potential providers to implement:
- [ ] Deepgram
- [ ] Google Speech-to-Text
- [ ] Azure Speech Services
- [ ] AssemblyAI
- [ ] Whisper (OpenAI)
- [ ] Rev.ai

Contributions welcome!
