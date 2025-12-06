"""
Example: Customize prompts and run the note taker with a shorter summary interval.
"""

import asyncio
import logging
import os

from livekit_ai_note_taker import config, run_worker


def tweak_settings():
    # Adjust interval and prompt type before starting
    config.SUMMARY_INTERVAL = 60
    config.PROMPT_TYPE = "big"
    os.environ["SUMMARY_INTERVAL"] = "60"
    os.environ["PROMPT_TYPE"] = "big"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    tweak_settings()
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
