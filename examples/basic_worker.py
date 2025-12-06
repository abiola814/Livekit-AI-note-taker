"""
Minimal example that starts the LiveKit meeting summarizer worker.

Prereqs:
- Install this package (`pip install .` or `pip install livekit-meeting-summarizer` once published)
- Set environment variables or create a .env file (see README.md)
"""

import asyncio
import logging

from livekit_ai_note_taker import run_worker


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
