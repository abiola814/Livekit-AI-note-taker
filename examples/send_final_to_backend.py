"""
Example: Listen for final summary generation and post to a custom backend endpoint.
"""

import asyncio
import logging
import os

from livekit_ai_note_taker import FinalSummarySender, NoteTakerAgent, config, run_worker


class BackendAwareFinalSender(FinalSummarySender):
    def send_summary(self, summary: str, room_name: str) -> None:
        import requests

        backend_url = os.getenv("BACKEND_URL", config.BACKEND_URL)
        try:
            response = requests.post(
                backend_url,
                json={"summary": summary, "room_sid": room_name},
                timeout=10,
            )
            logging.info("Sent summary to backend (%s): %s", backend_url, response.status_code)
        except Exception as exc:
            logging.error("Error sending summary: %s", exc, exc_info=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # We reuse run_worker; the subclass hooks are used internally when the room disconnects.
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
