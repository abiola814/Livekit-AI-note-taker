"""
Audio buffer for collecting and mixing audio from multiple participants.

This module provides efficient audio buffering and mixing capabilities for
multi-participant meetings, with automatic memory management and batch processing.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AudioBuffer:
    """
    Buffer for collecting and mixing audio from multiple participants.

    This class handles:
    - Per-participant audio buffering
    - Automatic audio mixing (averaging to prevent clipping)
    - Memory-efficient windowed storage (keeps only recent audio)
    - Batch processing triggers based on duration or silence

    Example:
        buffer = AudioBuffer(
            sample_rate=16000,
            channels=1,
            buffer_duration_minutes=15
        )

        # Add audio from participants
        await buffer.add_audio_frame("participant-1", audio_bytes)
        await buffer.add_audio_frame("participant-2", audio_bytes)

        # Check if ready to process
        if buffer.should_process_batch():
            mixed_audio = await buffer.get_mixed_audio()
            # Send to transcription service
            await buffer.clear()
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        buffer_duration_minutes: int = 15,
        silence_threshold_seconds: int = 120,
    ):
        """
        Initialize the audio buffer.

        Args:
            sample_rate: Audio sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            buffer_duration_minutes: How long to buffer before processing (default: 15)
            silence_threshold_seconds: Silence duration that triggers processing (default: 120)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_duration_seconds = buffer_duration_minutes * 60
        self.silence_threshold_seconds = silence_threshold_seconds
        self.max_samples = self.sample_rate * self.buffer_duration_seconds

        # Audio data storage - one buffer per participant
        self.participant_buffers: Dict[str, List[np.ndarray]] = {}
        self.participant_timestamps: Dict[str, List[float]] = {}
        self.mixed_audio: List[np.ndarray] = []
        self.start_time: Optional[datetime] = None
        self.last_activity_time: Optional[datetime] = None

        self._lock = asyncio.Lock()

    async def add_audio_frame(self, participant_id: str, audio_data: bytes):
        """
        Add an audio frame from a participant.

        Args:
            participant_id: Unique identifier for the participant
            audio_data: Raw audio data as bytes (int16 format)
        """
        async with self._lock:
            if self.start_time is None:
                self.start_time = datetime.utcnow()

            self.last_activity_time = datetime.utcnow()

            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Initialize participant buffer if needed
            if participant_id not in self.participant_buffers:
                self.participant_buffers[participant_id] = []
                self.participant_timestamps[participant_id] = []

            # Add to participant buffer
            self.participant_buffers[participant_id].append(audio_array)
            self.participant_timestamps[participant_id].append(time.time())

            # Keep only recent audio (within buffer duration)
            cutoff_time = time.time() - self.buffer_duration_seconds
            while (
                self.participant_timestamps[participant_id]
                and self.participant_timestamps[participant_id][0] < cutoff_time
            ):
                self.participant_buffers[participant_id].pop(0)
                self.participant_timestamps[participant_id].pop(0)

    async def get_mixed_audio(self) -> Optional[bytes]:
        """
        Get mixed audio from all participants.

        This method mixes audio from all participants by:
        1. Concatenating all frames per participant
        2. Finding the minimum length across all participants
        3. Normalizing and averaging audio to prevent clipping
        4. Converting back to int16 format

        Returns:
            Mixed audio as bytes (int16 format), or None if no audio available
        """
        async with self._lock:
            if not self.participant_buffers:
                return None

            # Find the minimum length across all participants
            min_length = float("inf")
            participant_arrays = {}

            for participant_id, buffers in self.participant_buffers.items():
                if buffers:
                    # Concatenate all buffers for this participant
                    participant_arrays[participant_id] = np.concatenate(buffers)
                    min_length = min(min_length, len(participant_arrays[participant_id]))

            if min_length == float("inf") or min_length == 0:
                return None

            # Mix audio from all participants
            mixed = np.zeros(min_length, dtype=np.float32)
            participant_count = len(participant_arrays)

            for participant_id, audio_array in participant_arrays.items():
                # Normalize and add to mix
                normalized = audio_array[:min_length].astype(np.float32) / 32768.0
                mixed += normalized / participant_count  # Average to prevent clipping

            # Convert back to int16
            mixed_int16 = (mixed * 32767).astype(np.int16)
            return mixed_int16.tobytes()

    async def clear(self):
        """
        Clear all audio buffers and free memory.

        This method explicitly deletes numpy arrays to ensure memory is freed,
        which is important for long-running sessions.
        """
        async with self._lock:
            # Clear and explicitly delete large arrays to free memory
            for participant_id in list(self.participant_buffers.keys()):
                buffers = self.participant_buffers[participant_id]
                for buffer in buffers:
                    del buffer  # Delete numpy arrays
                buffers.clear()

            self.participant_buffers.clear()
            self.participant_timestamps.clear()

            # Clear mixed audio
            for audio_chunk in self.mixed_audio:
                del audio_chunk
            self.mixed_audio.clear()

            self.start_time = None
            self.last_activity_time = None

            logger.debug("Audio buffer cleared and memory freed")

    def should_process_batch(self) -> bool:
        """
        Check if it's time to process the batch.

        Processing is triggered when:
        - Buffer duration has been reached (e.g., 15 minutes)
        - OR silence threshold has been exceeded (e.g., 2 minutes of silence)

        Returns:
            True if batch should be processed, False otherwise
        """
        if self.start_time is None:
            return False

        now = datetime.utcnow()
        duration = (now - self.start_time).total_seconds()

        # Trigger on buffer duration
        if duration >= self.buffer_duration_seconds:
            return True

        # Trigger on silence
        if self.last_activity_time:
            silence_duration = (now - self.last_activity_time).total_seconds()
            if silence_duration >= self.silence_threshold_seconds:
                return True

        return False

    def get_participant_count(self) -> int:
        """Get the number of participants currently in the buffer."""
        return len(self.participant_buffers)

    def get_buffer_info(self) -> Dict:
        """
        Get information about the current buffer state.

        Returns:
            Dictionary containing buffer statistics
        """
        info = {
            "participant_count": len(self.participant_buffers),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_activity_time": (
                self.last_activity_time.isoformat() if self.last_activity_time else None
            ),
            "should_process": self.should_process_batch(),
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "buffer_duration_seconds": self.buffer_duration_seconds,
        }

        # Calculate buffer duration
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            info["current_duration_seconds"] = duration

        # Calculate total audio samples
        total_samples = 0
        for buffers in self.participant_buffers.values():
            for buffer in buffers:
                total_samples += len(buffer)
        info["total_samples"] = total_samples
        info["total_duration_seconds"] = total_samples / self.sample_rate if total_samples > 0 else 0

        return info

    async def get_participant_audio(self, participant_id: str) -> Optional[bytes]:
        """
        Get audio for a specific participant (without mixing).

        Args:
            participant_id: The participant to get audio for

        Returns:
            Audio bytes for the participant, or None if not found
        """
        async with self._lock:
            if participant_id not in self.participant_buffers:
                return None

            buffers = self.participant_buffers[participant_id]
            if not buffers:
                return None

            # Concatenate all buffers for this participant
            audio_array = np.concatenate(buffers)
            return audio_array.tobytes()

    def __repr__(self) -> str:
        return (
            f"AudioBuffer(sample_rate={self.sample_rate}, "
            f"participants={len(self.participant_buffers)}, "
            f"duration={self.buffer_duration_seconds}s)"
        )
