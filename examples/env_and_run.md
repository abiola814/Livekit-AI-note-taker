# Example: Run with `.env` file

1) Create a `.env` at the repo root:

```
LIVEKIT_URL=wss://your.livekit.host
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
DEEPGRAM_API_KEY=your_deepgram_key
PROVIDER=groq
GROQ_API_KEY=your_groq_key
SUMMARY_INTERVAL=120
PROMPT_TYPE=small
AGENT_NAME=ai_note_taker
```

2) Install and run:
```bash
pip install .
python examples/basic_worker.py
```

Use `livekit-ai-note-taker` if installed as a package from PyPI.

# Example: Override prompt type at runtime

You can export environment overrides before starting:
```bash
export PROMPT_TYPE=big
export SUMMARY_INTERVAL=60
python examples/basic_worker.py
```

# Example: Custom logging level

In `basic_worker.py`, change:
```python
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
```
to see verbose logs while developing.
