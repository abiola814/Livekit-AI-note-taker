# Installation Fix

## Issue

You're seeing this error:
```
ERROR: File "setup.py" or "setup.cfg" not found. Directory cannot be installed in editable mode
```

This happens because your pip version is too old (21.2.4) and doesn't support modern `pyproject.toml`-based editable installs.

## Solution

### Step 1: Upgrade pip

```bash
cd /Users/abiolamoses/Downloads/ai-project/livekit-note-taker

# Upgrade pip
python -m pip install --upgrade pip

# Or if using your venv
/Users/abiolamoses/Downloads/ai-project/venv/bin/python3 -m pip install --upgrade pip
```

### Step 2: Install the library

```bash
# Now install with AWS support
pip install -e ".[aws]"

# Or without extras first
pip install -e .
```

## Complete Fresh Install (Recommended)

If you want a clean start:

```bash
cd /Users/abiolamoses/Downloads/ai-project

# Deactivate current venv
deactivate

# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate new venv
source venv/bin/activate

# Upgrade pip immediately
pip install --upgrade pip

# Install the library
cd livekit-note-taker
pip install -e ".[aws]"
```

## Verify Installation

```bash
# Check pip version (should be 25.x)
pip --version

# Try importing
python -c "from livekit_note_taker import NoteManager; print('✅ Success!')"

# Run tests
pytest
```

## Alternative: Install without Editable Mode

If upgrading pip doesn't work, you can install without editable mode:

```bash
# Build and install
pip install ".[aws]"
```

But you'll lose the ability to edit code and see changes immediately.
