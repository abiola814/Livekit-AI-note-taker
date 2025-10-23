"""AI service for generating summaries and extracting action items."""

import asyncio
import json
from typing import List, Optional
from datetime import datetime

from ..models.note import MeetingNote, ActionItem, NoteType, Priority, ActionItemStatus


class AIService:
    """
    Service for AI-powered meeting analysis.

    Supports multiple AI providers (OpenAI, Anthropic).
    """

    def __init__(
        self,
        provider: str = "openai",
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
    ):
        """
        Initialize AI service.

        Args:
            provider: AI provider ("openai" or "anthropic")
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
        """
        self.provider = provider.lower()

        if self.provider == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API key is required when provider='openai'")
            self._init_openai(openai_api_key)
        elif self.provider == "anthropic":
            if not anthropic_api_key:
                raise ValueError(
                    "Anthropic API key is required when provider='anthropic'"
                )
            self._init_anthropic(anthropic_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def _init_openai(self, api_key: str):
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI

            self.client = AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    def _init_anthropic(self, api_key: str):
        """Initialize Anthropic client."""
        try:
            from anthropic import AsyncAnthropic

            self.client = AsyncAnthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

    async def generate_summary(
        self, transcript_text: str, meeting_title: Optional[str] = None
    ) -> MeetingNote:
        """
        Generate a meeting summary.

        Args:
            transcript_text: Full transcript text
            meeting_title: Optional meeting title

        Returns:
            MeetingNote with summary
        """
        title_context = f" for '{meeting_title}'" if meeting_title else ""
        prompt = f"""Please analyze the following meeting transcript{title_context} and provide a concise summary.

Focus on:
- Main topics discussed
- Key decisions made
- Important points raised

Transcript:
{transcript_text}

Provide a well-structured summary in markdown format."""

        summary_text = await self._generate_text(prompt)

        return MeetingNote(
            meeting_id="",  # Will be set by caller
            note_type=NoteType.SUMMARY,
            content=summary_text,
            title=f"Summary{title_context}",
            ai_generated=True,
            confidence_score=0.9,
        )

    async def extract_action_items(
        self, transcript_text: str, meeting_id: str
    ) -> List[ActionItem]:
        """
        Extract action items from transcript.

        Args:
            transcript_text: Full transcript text
            meeting_id: Meeting identifier

        Returns:
            List of ActionItem objects
        """
        prompt = """Analyze the following meeting transcript and extract all action items.

For each action item, identify:
- Title: Brief description of the task
- Description: More detailed explanation if available
- Assigned to: Person responsible (if mentioned)
- Priority: low, medium, high, or urgent
- Due date: If mentioned (format: YYYY-MM-DD)

Return the action items as a JSON array with this structure:
[
  {
    "title": "Task title",
    "description": "Task description",
    "assigned_to": "Person name or null",
    "priority": "medium",
    "due_date": "2024-01-15 or null"
  }
]

Transcript:
""" + transcript_text

        response = await self._generate_text(prompt)

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()

            items_data = json.loads(json_str)

            action_items = []
            for item_data in items_data:
                # Parse due date if present
                due_date = None
                if item_data.get("due_date"):
                    try:
                        due_date = datetime.fromisoformat(item_data["due_date"])
                    except (ValueError, TypeError):
                        pass

                # Parse priority
                priority_str = item_data.get("priority", "medium").lower()
                priority = Priority.MEDIUM
                if priority_str == "low":
                    priority = Priority.LOW
                elif priority_str == "high":
                    priority = Priority.HIGH
                elif priority_str == "urgent":
                    priority = Priority.URGENT

                action_item = ActionItem(
                    meeting_id=meeting_id,
                    title=item_data["title"],
                    description=item_data.get("description"),
                    assigned_to=item_data.get("assigned_to"),
                    priority=priority,
                    due_date=due_date,
                    status=ActionItemStatus.OPEN,
                )
                action_items.append(action_item)

            return action_items

        except (json.JSONDecodeError, KeyError) as e:
            # If parsing fails, return empty list
            print(f"Warning: Failed to parse action items: {e}")
            return []

    async def extract_key_points(
        self, transcript_text: str, meeting_id: str
    ) -> MeetingNote:
        """
        Extract key points from the meeting.

        Args:
            transcript_text: Full transcript text
            meeting_id: Meeting identifier

        Returns:
            MeetingNote with key points
        """
        prompt = """Extract the key points from this meeting transcript.

List the most important points discussed, decisions made, and insights shared.

Format as a bulleted list in markdown.

Transcript:
""" + transcript_text

        key_points_text = await self._generate_text(prompt)

        return MeetingNote(
            meeting_id=meeting_id,
            note_type=NoteType.KEY_POINTS,
            content=key_points_text,
            title="Key Points",
            ai_generated=True,
            confidence_score=0.85,
        )

    async def _generate_text(self, prompt: str) -> str:
        """
        Generate text using the configured AI provider.

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        if self.provider == "openai":
            return await self._generate_openai(prompt)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_openai(self, prompt: str) -> str:
        """Generate text using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

    async def _generate_anthropic(self, prompt: str) -> str:
        """Generate text using Anthropic."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
