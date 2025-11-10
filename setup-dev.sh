#!/bin/bash
# Development environment setup script

set -e

echo "================================================"
echo "LiveKit Note Taker - Development Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Setting up development environment..."
echo ""

# Step 1: Upgrade pip
echo "1️⃣  Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓${NC} pip upgraded"
echo ""

# Step 2: Install library in editable mode
echo "2️⃣  Installing library with AWS support..."
pip install -e ".[aws]"
echo -e "${GREEN}✓${NC} Library installed"
echo ""

# Step 3: Install development tools
echo "3️⃣  Installing development tools..."
pip install pytest pytest-asyncio pytest-cov
echo -e "${GREEN}✓${NC} Development tools installed"
echo ""

# Step 4: Verify installation
echo "4️⃣  Verifying installation..."
python << EOF
from livekit_note_taker import NoteManager
from livekit_note_taker.audio import AudioBuffer, LiveKitRecorder
from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
print("${GREEN}✓${NC} All imports successful")
EOF
echo ""

# Step 5: Show pip version
echo "5️⃣  Checking versions..."
echo -n "   pip: "
pip --version
echo -n "   Python: "
python --version
echo ""

echo "================================================"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Run tests:"
echo "     pytest"
echo ""
echo "  2. Run example:"
echo "     python examples/aws_transcription_example.py"
echo ""
echo "  3. Configure credentials (if needed):"
echo "     export LIVEKIT_URL='wss://your-server.com'"
echo "     export LIVEKIT_API_KEY='your-key'"
echo "     export LIVEKIT_API_SECRET='your-secret'"
echo "     aws configure"
echo ""
echo "================================================"
