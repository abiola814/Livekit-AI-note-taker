# Testing Guide

This guide will help you test the LiveKit Note Taker library, especially the AWS Transcribe integration.

## Prerequisites

### 1. Install the Library

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Install in development mode with all dependencies
pip install -e ".[all]"

# Or just AWS dependencies for testing
pip install -e ".[aws]"
```

### 2. Set Up LiveKit

You need a LiveKit server. Choose one option:

#### Option A: LiveKit Cloud (Easiest)
1. Go to https://cloud.livekit.io/
2. Create a free account
3. Create a new project
4. Get your credentials from the project settings

#### Option B: Local Docker (For Testing)
```bash
# Run LiveKit server locally
docker run --rm -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  -e LIVEKIT_KEYS="devkey: secret" \
  livekit/livekit-server \
  --dev
```

### 3. Set Up AWS Credentials

You need AWS credentials with Transcribe permissions:

#### Check if AWS is configured:
```bash
aws sts get-caller-identity
```

#### If not configured, set up credentials:

**Option A: AWS CLI (Recommended)**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
```

**Option B: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"
```

**Option C: IAM Role (if running on EC2/ECS)**
- Attach an IAM role with `transcribe:*` permissions to your instance

### 4. Configure Environment

Create a `.env` file in the library root:

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

cat > .env << 'EOF'
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
# OR for local: ws://localhost:7880
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# AWS Configuration
AWS_REGION=us-east-1
# AWS credentials should be in ~/.aws/credentials or env vars

# Test Room
ROOM_ID=test-room-123
EOF
```

## Testing Methods

### Method 1: Run the Example Script (Quickest)

```bash
# Make sure you're in the library directory
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Load environment variables
export $(cat .env | xargs)

# Run the AWS transcription example
python examples/aws_transcription_example.py
```

**What to expect:**
```
================================================================================
AWS Transcribe Integration Example
================================================================================
✅ AWS credentials found
Created AWS Transcribe provider: AWSTranscriptionProvider(region=us-east-1, language=en-US, sample_rate=16000)
Created LiveKit recorder
Created NoteManager

📌 Starting session for room: test-room-123
Session ID: abc-123-def-456
🎬 Session started: abc-123-def-456

🎙️  Starting recording...
🔴 Recording started for room: test-room-123

================================================================================
RECORDING IN PROGRESS
================================================================================
Room: test-room-123
LiveKit URL: wss://your-project.livekit.cloud

To test:
1. Join the room using LiveKit's example app
2. Speak into your microphone
3. Watch the console for transcriptions

Recording for 5 minutes (or press Ctrl+C to stop)...
================================================================================
```

### Method 2: Join the Room to Generate Audio

You need to join the LiveKit room to generate audio for transcription.

#### Option A: Use LiveKit Meet Demo
1. Go to https://meet.livekit.io/
2. Enter your room name (e.g., `test-room-123`)
3. Click "Join Room"
4. Speak into your microphone
5. Watch the console for transcriptions

#### Option B: Use Custom Client
Create a simple client:

```bash
# Create a test client
cat > test_client.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>LiveKit Test Client</title>
    <script src="https://unpkg.com/livekit-client/dist/livekit-client.umd.min.js"></script>
</head>
<body>
    <h1>LiveKit Test Client</h1>
    <button id="connect">Connect & Speak</button>
    <div id="status"></div>

    <script>
        const roomName = 'test-room-123';
        const livekitUrl = 'wss://your-project.livekit.cloud';

        document.getElementById('connect').onclick = async () => {
            const room = new LivekitClient.Room();

            // Generate token (you'll need to implement this server-side)
            const token = prompt('Enter participant token:');

            await room.connect(livekitUrl, token);

            // Enable microphone
            await room.localParticipant.enableCameraAndMicrophone();

            document.getElementById('status').innerHTML = 'Connected! Start speaking...';
        };
    </script>
</body>
</html>
EOF

# Open in browser
open test_client.html  # macOS
# or
xdg-open test_client.html  # Linux
```

### Method 3: Manual Testing with Python

Create a test script:

```bash
cat > test_manual.py << 'EOF'
import asyncio
import os
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider

async def test_transcription():
    """Test AWS transcription with a sample audio file."""

    # Create provider
    provider = AWSTranscriptionProvider(
        region=os.getenv("AWS_REGION", "us-east-1"),
        language_code="en-US"
    )

    print("✅ AWS provider created")

    # For this test, you need an audio file
    # You can record one or download a sample
    import wave
    import numpy as np

    # Generate a simple test audio (1 second of silence)
    sample_rate = 16000
    duration = 1  # seconds
    audio_data = np.zeros(sample_rate * duration, dtype=np.int16)

    # Save to WAV file
    with wave.open('test_audio.wav', 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio_data.tobytes())

    print("📝 Testing transcription...")

    try:
        # Transcribe
        transcripts = await provider.transcribe_audio(
            audio_data=audio_data.tobytes(),
            language="en-US",
            sample_rate=sample_rate
        )

        print(f"✅ Transcription complete: {len(transcripts)} segments")

        for i, transcript in enumerate(transcripts, 1):
            print(f"  [{i}] {transcript.text} (confidence: {transcript.confidence:.2f})")

        if len(transcripts) == 0:
            print("⚠️  No transcripts (expected for silence)")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

    finally:
        await provider.close()
        print("🧹 Cleanup complete")

if __name__ == "__main__":
    asyncio.run(test_transcription())
EOF

python test_manual.py
```

### Method 4: Integration Test with Your Original App

If you want to test with your original `ai-note-take` app:

```bash
# In your original app directory
cd /Users/abiolamoses/Downloads/ai-project/ai-note-take

# Install the library
pip install -e ../livekit-note-taker[aws]

# Modify your code to use the library
# (See migration guide in AWS_IMPLEMENTATION.md)
```

## Verification Checklist

After running the tests, verify:

- [ ] Library installs without errors
- [ ] AWS credentials are recognized
- [ ] LiveKit connection succeeds
- [ ] Audio recording starts
- [ ] Audio batches are captured (check logs)
- [ ] AWS Transcribe is called
- [ ] Transcripts are returned
- [ ] Confidence scores are present
- [ ] Timestamps are correct
- [ ] Cleanup happens properly
- [ ] No memory leaks (for longer tests)

## Expected Output

When successful, you should see:

```
🎵 Received audio batch: 15.0s of audio
📝 Starting transcription with AWS Transcribe...
Transcribed: Hello world...
Transcribed: This is a test...
✅ Transcription complete: 2 segments
  [1] Hello world (confidence: 0.95)
  [2] This is a test (confidence: 0.92)
```

## Common Issues & Solutions

### Issue 1: "Unable to locate credentials"

**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# If not configured, run:
aws configure
```

### Issue 2: "Connection refused" to LiveKit

**Solution:**
```bash
# Check if LiveKit is running
curl http://localhost:7880

# Or test the URL
curl https://your-project.livekit.cloud

# Make sure LIVEKIT_URL is correct (wss:// for cloud, ws:// for local)
```

### Issue 3: No audio captured

**Solution:**
- Make sure you actually joined the room
- Check that your microphone is enabled
- Verify the room name matches
- Look for "Capturing audio from participant-123" in logs

### Issue 4: No transcripts returned

**Solution:**
- Check that audio contains speech (not silence)
- Verify AWS region is correct
- Check AWS Transcribe service is available in your region
- Make sure language code matches audio ("en-US" for English)

### Issue 5: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -e ".[aws]"

# Or manually install
pip install boto3 amazon-transcribe livekit livekit-api numpy
```

## Testing with Real Audio

To test with a real audio file:

```python
import asyncio
import wave
from pathlib import Path
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider

async def test_real_audio():
    provider = AWSTranscriptionProvider(region="us-east-1")

    # Use a real audio file (WAV format, 16kHz, mono)
    audio_file = Path("your_audio.wav")

    transcripts = await provider.transcribe_file(audio_file)

    for transcript in transcripts:
        print(transcript.text)

    await provider.close()

asyncio.run(test_real_audio())
```

## Performance Testing

To test with longer sessions:

```bash
# Run for longer duration
python examples/aws_transcription_example.py

# In another terminal, join the room and speak for 10-15 minutes
# Watch for batch processing every 15 minutes
# Check memory usage: ps aux | grep python
```

## Debugging

Enable debug logging:

```python
import logging

# In your test script
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Or via environment:
```bash
export LOGLEVEL=DEBUG
python examples/aws_transcription_example.py
```

## Next Steps

After successful testing:

1. ✅ Verify all features work
2. 📝 Write unit tests (see `tests/` directory)
3. 🚀 Publish to PyPI (see PYPI_PUBLISHING.md)
4. 📚 Update documentation with your findings
5. 🎉 Use in production!

## Getting Help

If you encounter issues:

1. Check the logs carefully
2. Verify all credentials are correct
3. Test each component individually
4. Check AWS CloudWatch logs for Transcribe errors
5. Review the troubleshooting section in `livekit_note_taker/transcription/README.md`

## Quick Test Command

For a quick sanity check:

```bash
# One-liner to test everything
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker && \
  source .env 2>/dev/null || true && \
  python -c "
import asyncio
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider

async def test():
    provider = AWSTranscriptionProvider(region='us-east-1')
    print('✅ AWS provider initialized successfully')
    await provider.close()

asyncio.run(test())
"
```

If this succeeds, your installation is correct!
