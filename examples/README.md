# Examples

## basic_worker.py

Run the summarizer agent using your environment variables.

```bash
pip install .  # or pip install livekit-ai-note-taker once published
export LIVEKIT_URL=...
export LIVEKIT_API_KEY=...
export LIVEKIT_API_SECRET=...
export DEEPGRAM_API_KEY=...
export PROVIDER=groq
export GROQ_API_KEY=...
# optional: SUMMARY_INTERVAL, PROMPT_TYPE, BACKEND_URL, AGENT_NAME, etc.

python examples/basic_worker.py
```

You should see the worker connect to LiveKit and handle jobs as they arrive. Press `CTRL+C` to stop. Adjust logging in the script as needed.
