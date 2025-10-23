"""JSON exporter."""

import json
from .exporter import BaseExporter


class JSONExporter(BaseExporter):
    """Export meeting notes to JSON format."""

    async def export(self, meeting, output_path: str, options) -> None:
        """Export meeting to JSON file."""
        data = self._generate_json_data(meeting, options)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _generate_json_data(self, meeting, options) -> dict:
        """Generate JSON data structure."""
        data = {
            "meeting": {
                "id": meeting.id,
                "room_id": meeting.room_id,
                "title": meeting.title,
                "description": meeting.description,
                "start_time": meeting.start_time.isoformat() if meeting.start_time else None,
                "end_time": meeting.end_time.isoformat() if meeting.end_time else None,
                "duration_minutes": meeting.duration_minutes(),
                "status": meeting.status.value,
                "language": meeting.language,
                "participant_count": meeting.participant_count,
            }
        }

        if options.include_metadata:
            data["meeting"]["metadata"] = meeting.metadata

        if options.include_summary:
            data["notes"] = [note.to_dict() for note in meeting.notes]

        if options.include_action_items:
            data["action_items"] = [item.to_dict() for item in meeting.action_items]

        if options.include_transcripts and meeting.transcript:
            data["transcript"] = meeting.transcript.to_dict()

        return data
