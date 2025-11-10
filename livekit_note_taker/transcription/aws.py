"""
AWS Transcribe implementation for speech-to-text.

This module provides batch transcription using AWS Transcribe Streaming API
for cost-effective meeting transcription.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Awaitable
from pathlib import Path
import wave

import boto3
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

from livekit_note_taker.transcription.base import TranscriptionProvider, Transcript

logger = logging.getLogger(__name__)


class AWSTranscriptHandler(TranscriptResultStreamHandler):
    """
    Handler for AWS Transcribe streaming results.

    This handler processes transcription results from AWS Transcribe and
    converts them into Transcript objects.
    """

    def __init__(
        self,
        output_stream,
        batch_start_time: datetime,
        on_transcript: Optional[Callable[[Transcript], Awaitable[None]]] = None,
    ):
        """
        Initialize the transcript handler.

        Args:
            output_stream: AWS Transcribe output stream
            batch_start_time: When the audio batch started
            on_transcript: Optional callback for each transcript
        """
        super().__init__(output_stream)
        self.batch_start_time = batch_start_time
        self.segment_start_time = batch_start_time
        self.on_transcript = on_transcript
        self.transcripts: List[Transcript] = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        """
        Handle transcription results from AWS Transcribe.

        Args:
            transcript_event: Event from AWS Transcribe
        """
        try:
            results = transcript_event.transcript.results

            for result in results:
                # Skip partial results for batch processing
                if result.is_partial:
                    continue

                for alt in result.alternatives:
                    text = alt.transcript.strip()
                    if not text:
                        continue

                    # Create transcript object
                    transcript = Transcript(
                        text=text,
                        confidence=getattr(alt, "confidence", 0.9),
                        speaker_id="batch_audio",  # Batch processing doesn't identify speakers
                        speaker_name="Mixed Audio",
                        timestamp=self.segment_start_time,
                        is_final=True,
                        language="en-US",
                        metadata={
                            "batch_start": self.batch_start_time.isoformat(),
                            "word_count": len(text.split()),
                        }
                    )

                    self.transcripts.append(transcript)

                    # Call callback if provided
                    if self.on_transcript:
                        await self.on_transcript(transcript)

                    logger.info(f"Transcribed: {text[:50]}...")

                    # Update segment time for next piece
                    # Rough estimate: 0.5 seconds per word
                    estimated_duration = len(text.split()) * 0.5
                    self.segment_start_time += timedelta(seconds=estimated_duration)

        except Exception as e:
            logger.error(f"Error handling transcript event: {e}", exc_info=True)


class AWSTranscriptionProvider(TranscriptionProvider):
    """
    AWS Transcribe provider for speech-to-text.

    This implementation uses AWS Transcribe Streaming API for cost-effective
    batch transcription of meeting audio.

    Example:
        provider = AWSTranscriptionProvider(
            region="us-east-1",
            language_code="en-US"
        )

        # Transcribe audio file
        transcripts = await provider.transcribe_audio(
            audio_data=audio_bytes,
            language="en-US",
            sample_rate=16000
        )

        # Or use streaming
        async def audio_generator():
            # Yield audio chunks
            yield chunk1
            yield chunk2

        async for transcript in provider.transcribe_streaming(
            audio_stream=audio_generator(),
            language="en-US"
        ):
            print(transcript.text)
    """

    def __init__(
        self,
        region: str = "us-east-1",
        language_code: str = "en-US",
        sample_rate: int = 16000,
        temp_audio_dir: Optional[Path] = None,
    ):
        """
        Initialize the AWS Transcribe provider.

        Args:
            region: AWS region (default: us-east-1)
            language_code: Language for transcription (default: en-US)
            sample_rate: Audio sample rate in Hz (default: 16000)
            temp_audio_dir: Directory for temporary audio files
        """
        self.region = region
        self.language_code = language_code
        self.sample_rate = sample_rate
        self.temp_audio_dir = temp_audio_dir or Path("./temp_audio")
        self.temp_audio_dir.mkdir(exist_ok=True)

        self.transcribe_client: Optional[TranscribeStreamingClient] = None
        self._lock = asyncio.Lock()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en-US",
        sample_rate: int = 16000,
        **kwargs
    ) -> List[Transcript]:
        """
        Transcribe audio data using AWS Transcribe.

        This method saves the audio to a temporary WAV file and then streams
        it to AWS Transcribe for transcription.

        Args:
            audio_data: Raw audio bytes (int16 PCM format)
            language: Language code (e.g., "en-US")
            sample_rate: Audio sample rate in Hz
            **kwargs: Additional options
                - on_transcript: Callback for each transcript
                - chunk_size: Size of chunks to send (default: 8000)

        Returns:
            List of Transcript objects

        Raises:
            Exception: If transcription fails
        """
        async with self._lock:
            try:
                # Save audio to temporary WAV file
                import time
                temp_file = self.temp_audio_dir / f"batch_{int(time.time())}.wav"

                with wave.open(str(temp_file), 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 2 bytes (int16)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(audio_data)

                logger.info(f"Saved audio to {temp_file} ({len(audio_data)} bytes)")

                # Create transcribe client
                if not self.transcribe_client:
                    self.transcribe_client = TranscribeStreamingClient(region=self.region)

                # Read audio file (skip WAV header)
                with open(temp_file, 'rb') as audio_file:
                    audio_file.seek(44)  # Skip WAV header (44 bytes)
                    pcm_data = audio_file.read()

                # Start streaming transcription
                stream = await self.transcribe_client.start_stream_transcription(
                    language_code=language or self.language_code,
                    media_sample_rate_hz=sample_rate,
                    media_encoding="pcm",
                )

                if not stream or not stream.input_stream:
                    raise Exception("Failed to initialize transcription stream")

                # Create handler
                batch_start_time = datetime.utcnow()
                on_transcript_callback = kwargs.get("on_transcript")

                handler = AWSTranscriptHandler(
                    stream.output_stream,
                    batch_start_time,
                    on_transcript=on_transcript_callback
                )

                # Start handler task
                handler_task = asyncio.create_task(handler.handle_events())

                # Send audio data in chunks
                chunk_size = kwargs.get("chunk_size", 8000)  # 0.5 seconds at 16kHz

                for i in range(0, len(pcm_data), chunk_size):
                    chunk = pcm_data[i:i + chunk_size]
                    if chunk:
                        await stream.input_stream.send_audio_event(audio_chunk=chunk)
                        await asyncio.sleep(0.1)  # Small delay to simulate real-time

                # End stream
                await stream.input_stream.end_stream()
                await handler_task

                logger.info(f"Batch transcription completed: {len(handler.transcripts)} transcripts")

                # Clean up temp file
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")

                return handler.transcripts

            except Exception as e:
                logger.error(f"Error transcribing audio: {e}", exc_info=True)
                raise

    async def transcribe_streaming(
        self,
        audio_stream,
        language: str = "en-US",
        sample_rate: int = 16000,
        **kwargs
    ):
        """
        Transcribe audio in streaming mode (async generator).

        This method allows real-time transcription by streaming audio chunks
        directly to AWS Transcribe without buffering.

        Args:
            audio_stream: Async generator yielding audio chunks (bytes)
            language: Language code
            sample_rate: Audio sample rate in Hz
            **kwargs: Additional options
                - include_partial: Include partial results (default: False)

        Yields:
            Transcript objects as they become available

        Example:
            async def audio_generator():
                for chunk in audio_chunks:
                    yield chunk

            async for transcript in provider.transcribe_streaming(audio_generator()):
                print(transcript.text)
        """
        try:
            # Create transcribe client
            if not self.transcribe_client:
                self.transcribe_client = TranscribeStreamingClient(region=self.region)

            # Start streaming transcription
            stream = await self.transcribe_client.start_stream_transcription(
                language_code=language or self.language_code,
                media_sample_rate_hz=sample_rate,
                media_encoding="pcm",
            )

            if not stream or not stream.input_stream:
                raise Exception("Failed to initialize transcription stream")

            batch_start_time = datetime.utcnow()
            include_partial = kwargs.get("include_partial", False)

            # Create a queue for transcripts
            transcript_queue = asyncio.Queue()

            async def transcript_callback(transcript: Transcript):
                """Callback to put transcripts in the queue."""
                await transcript_queue.put(transcript)

            handler = AWSTranscriptHandler(
                stream.output_stream,
                batch_start_time,
                on_transcript=transcript_callback
            )

            # Start handler task
            handler_task = asyncio.create_task(handler.handle_events())

            # Start sender task
            async def send_audio():
                """Send audio chunks to the stream."""
                try:
                    async for audio_chunk in audio_stream:
                        if audio_chunk:
                            await stream.input_stream.send_audio_event(audio_chunk=audio_chunk)
                except Exception as e:
                    logger.error(f"Error sending audio: {e}")
                finally:
                    await stream.input_stream.end_stream()

            sender_task = asyncio.create_task(send_audio())

            # Yield transcripts as they arrive
            while not handler_task.done() or not transcript_queue.empty():
                try:
                    transcript = await asyncio.wait_for(
                        transcript_queue.get(),
                        timeout=0.5
                    )
                    yield transcript
                except asyncio.TimeoutError:
                    continue

            # Wait for tasks to complete
            await sender_task
            await handler_task

        except Exception as e:
            logger.error(f"Error in streaming transcription: {e}", exc_info=True)
            raise

    async def transcribe_file(
        self,
        audio_file_path: Path,
        language: str = "en-US",
        **kwargs
    ) -> List[Transcript]:
        """
        Transcribe an audio file.

        This is a convenience method that reads an audio file and transcribes it.

        Args:
            audio_file_path: Path to the audio file (WAV format)
            language: Language code
            **kwargs: Additional options

        Returns:
            List of Transcript objects
        """
        try:
            # Read audio file
            with wave.open(str(audio_file_path), 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                audio_data = wav_file.readframes(wav_file.getnframes())

            logger.info(f"Read audio file: {audio_file_path} ({len(audio_data)} bytes)")

            # Transcribe
            return await self.transcribe_audio(
                audio_data=audio_data,
                language=language,
                sample_rate=sample_rate,
                **kwargs
            )

        except Exception as e:
            logger.error(f"Error transcribing file: {e}", exc_info=True)
            raise

    async def close(self):
        """Close the transcribe client and clean up resources."""
        logger.info("Closing AWS Transcribe provider")

        # Clean up temporary audio files
        try:
            import glob
            import os
            temp_files = glob.glob(str(self.temp_audio_dir / "batch_*.wav"))
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                    logger.debug(f"Removed temp file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not remove temp file {temp_file}: {e}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")

        self.transcribe_client = None
        logger.info("AWS Transcribe provider closed")

    def __repr__(self) -> str:
        return (
            f"AWSTranscriptionProvider(region={self.region}, "
            f"language={self.language_code}, "
            f"sample_rate={self.sample_rate})"
        )
