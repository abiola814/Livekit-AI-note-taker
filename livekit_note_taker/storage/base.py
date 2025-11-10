"""
Base classes for storage backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.

    Subclasses should implement specific storage solutions like
    SQLAlchemy (SQL databases), MongoDB, Redis, etc.
    """

    @abstractmethod
    async def save_session(self, session) -> str:
        """
        Save a meeting session.

        Args:
            session: MeetingSession object

        Returns:
            Session ID
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: str):
        """
        Retrieve a meeting session.

        Args:
            session_id: The session ID

        Returns:
            MeetingSession object or None
        """
        pass

    @abstractmethod
    async def save_transcript(
        self,
        session_id: str,
        transcript: Dict[str, Any]
    ) -> str:
        """
        Save a transcript.

        Args:
            session_id: The session this transcript belongs to
            transcript: Transcript data

        Returns:
            Transcript ID
        """
        pass

    @abstractmethod
    async def get_transcripts(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get transcripts for a session.

        Args:
            session_id: The session ID
            limit: Optional limit on number of transcripts

        Returns:
            List of transcript dictionaries
        """
        pass

    @abstractmethod
    async def save_note(
        self,
        session_id: str,
        note: Dict[str, Any]
    ) -> str:
        """
        Save a note (summary, action items, etc.).

        Args:
            session_id: The session this note belongs to
            note: Note data

        Returns:
            Note ID
        """
        pass

    @abstractmethod
    async def get_notes(
        self,
        session_id: str,
        note_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get notes for a session.

        Args:
            session_id: The session ID
            note_type: Optional filter by note type

        Returns:
            List of note dictionaries
        """
        pass

    @abstractmethod
    async def close(self):
        """Close connections and clean up resources."""
        pass
