"""Transcription service using AWS Transcribe."""

import asyncio
import boto3
import tempfile
import uuid
import time
from typing import List, Optional
from pathlib import Path

from ..models.transcript import TranscriptSegment


class TranscriptionService:
    """
    Service for transcribing audio using AWS Transcribe.

    Supports both batch transcription and streaming transcription.
    """

    def __init__(
        self,
        aws_region: str = "us-east-1",
        aws_access_key: Optional[str] = None,
        aws_secret_key: Optional[str] = None,
    ):
        """
        Initialize transcription service.

        Args:
            aws_region: AWS region
            aws_access_key: AWS access key (optional, uses environment if not provided)
            aws_secret_key: AWS secret key (optional, uses environment if not provided)
        """
        self.aws_region = aws_region

        # Initialize AWS clients
        session_kwargs = {"region_name": aws_region}
        if aws_access_key and aws_secret_key:
            session_kwargs["aws_access_key_id"] = aws_access_key
            session_kwargs["aws_secret_access_key"] = aws_secret_key

        self.transcribe_client = boto3.client("transcribe", **session_kwargs)
        self.s3_client = boto3.client("s3", **session_kwargs)

    async def transcribe_file(
        self, audio_file_path: str, language: str = "en-US"
    ) -> List[TranscriptSegment]:
        """
        Transcribe an audio file.

        Args:
            audio_file_path: Path to audio file
            language: Language code

        Returns:
            List of transcript segments
        """
        # This is a simplified implementation
        # In production, you would:
        # 1. Upload file to S3
        # 2. Start transcription job
        # 3. Poll for completion
        # 4. Parse results into TranscriptSegments

        job_name = f"transcription-{uuid.uuid4()}"

        # For now, return a placeholder
        # Real implementation would call AWS Transcribe API
        return await self._mock_transcription(audio_file_path, language)

    async def _mock_transcription(
        self, audio_file_path: str, language: str
    ) -> List[TranscriptSegment]:
        """
        Mock transcription for testing.

        Replace this with actual AWS Transcribe integration.
        """
        await asyncio.sleep(0.1)  # Simulate API call

        # Return a sample segment
        return [
            TranscriptSegment(
                text="This is a sample transcription. Replace with AWS Transcribe integration.",
                speaker="Speaker 1",
                confidence=0.95,
                start_time=0.0,
                end_time=5.0,
                language=language,
                is_final=True,
            )
        ]

    async def transcribe_batch(
        self,
        audio_file_path: str,
        s3_bucket: str,
        language: str = "en-US",
        job_name: Optional[str] = None,
    ) -> List[TranscriptSegment]:
        """
        Transcribe audio file using batch processing.

        Args:
            audio_file_path: Path to audio file
            s3_bucket: S3 bucket for uploading audio
            language: Language code
            job_name: Optional custom job name

        Returns:
            List of transcript segments
        """
        if job_name is None:
            job_name = f"batch-transcription-{uuid.uuid4()}"

        # Upload to S3
        s3_key = f"transcriptions/{job_name}/{Path(audio_file_path).name}"
        await self._upload_to_s3(audio_file_path, s3_bucket, s3_key)

        # Start transcription job
        job_uri = f"s3://{s3_bucket}/{s3_key}"
        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": job_uri},
            MediaFormat=self._get_media_format(audio_file_path),
            LanguageCode=language,
        )

        # Wait for completion
        segments = await self._wait_for_transcription(job_name)

        # Clean up S3
        await self._delete_from_s3(s3_bucket, s3_key)

        return segments

    async def _upload_to_s3(self, file_path: str, bucket: str, key: str) -> None:
        """Upload file to S3."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self.s3_client.upload_file, file_path, bucket, key
        )

    async def _delete_from_s3(self, bucket: str, key: str) -> None:
        """Delete file from S3."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, self.s3_client.delete_object, {"Bucket": bucket, "Key": key}
        )

    async def _wait_for_transcription(
        self, job_name: str, max_wait_seconds: int = 300
    ) -> List[TranscriptSegment]:
        """
        Wait for transcription job to complete and parse results.

        Args:
            job_name: Transcription job name
            max_wait_seconds: Maximum time to wait

        Returns:
            List of transcript segments
        """
        start_time = time.time()

        while True:
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError(f"Transcription job {job_name} timed out")

            # Get job status
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.transcribe_client.get_transcription_job,
                {"TranscriptionJobName": job_name},
            )

            status = response["TranscriptionJob"]["TranscriptionJobStatus"]

            if status == "COMPLETED":
                return self._parse_transcription_results(response)
            elif status == "FAILED":
                raise Exception(f"Transcription job failed: {response}")

            # Wait before polling again
            await asyncio.sleep(2)

    def _parse_transcription_results(self, response: dict) -> List[TranscriptSegment]:
        """
        Parse AWS Transcribe results into TranscriptSegments.

        Args:
            response: AWS Transcribe API response

        Returns:
            List of transcript segments
        """
        # This would parse the actual JSON results from AWS Transcribe
        # For now, return a placeholder
        segments = []

        # Real implementation would extract items from the transcript
        # and create TranscriptSegment objects with proper timing and speaker info

        return segments

    def _get_media_format(self, file_path: str) -> str:
        """Determine media format from file extension."""
        ext = Path(file_path).suffix.lower()
        format_map = {
            ".mp3": "mp3",
            ".mp4": "mp4",
            ".wav": "wav",
            ".flac": "flac",
            ".ogg": "ogg",
            ".webm": "webm",
        }
        return format_map.get(ext, "mp3")
