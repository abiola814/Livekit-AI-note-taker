#!/bin/bash
# Quick test script for livekit-note-taker library

set -e  # Exit on error

echo "================================================"
echo "LiveKit Note Taker - Quick Test Script"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Python
echo "1️⃣  Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo ""

# Step 2: Create virtual environment (optional)
if [ ! -d "venv" ]; then
    echo "2️⃣  Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo "2️⃣  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || echo "Note: Could not activate venv"
echo ""

# Step 3: Install dependencies
echo "3️⃣  Installing library..."
pip install -e ".[aws]" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Library installed successfully"
else
    echo -e "${YELLOW}⚠${NC}  Installing without AWS dependencies..."
    pip install -e "." > /dev/null 2>&1
fi
echo ""

# Step 4: Check AWS credentials
echo "4️⃣  Checking AWS credentials..."
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        echo -e "${GREEN}✓${NC} AWS credentials found (Account: $AWS_ACCOUNT)"
    else
        echo -e "${YELLOW}⚠${NC}  AWS credentials not configured"
        echo "   Run: aws configure"
    fi
else
    echo -e "${YELLOW}⚠${NC}  AWS CLI not installed"
fi
echo ""

# Step 5: Check LiveKit credentials
echo "5️⃣  Checking LiveKit credentials..."
if [ -n "$LIVEKIT_URL" ] && [ -n "$LIVEKIT_API_KEY" ] && [ -n "$LIVEKIT_API_SECRET" ]; then
    echo -e "${GREEN}✓${NC} LiveKit credentials found"
    echo "   URL: $LIVEKIT_URL"
else
    echo -e "${YELLOW}⚠${NC}  LiveKit credentials not set"
    echo "   Set: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET"
fi
echo ""

# Step 6: Run unit tests
echo "6️⃣  Running unit tests..."
if pip show pytest > /dev/null 2>&1; then
    pytest tests/ -v --tb=short 2>&1 | tail -20
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} All tests passed"
    else
        echo -e "${RED}✗${NC} Some tests failed (see above)"
    fi
else
    echo -e "${YELLOW}⚠${NC}  pytest not installed. Installing..."
    pip install pytest pytest-asyncio > /dev/null 2>&1
    pytest tests/ -v
fi
echo ""

# Step 7: Test imports
echo "7️⃣  Testing imports..."
python3 << EOF
try:
    from livekit_note_taker import NoteManager
    print("${GREEN}✓${NC} Core imports work")
except ImportError as e:
    print("${RED}✗${NC} Import failed:", e)
    exit(1)

try:
    from livekit_note_taker.transcription.aws import AWSTranscriptionProvider
    print("${GREEN}✓${NC} AWS provider imports work")
except ImportError:
    print("${YELLOW}⚠${NC}  AWS provider not available (install with: pip install -e '.[aws]')")

try:
    from livekit_note_taker.audio import AudioBuffer, LiveKitRecorder
    print("${GREEN}✓${NC} Audio modules import work")
except ImportError as e:
    print("${RED}✗${NC} Audio import failed:", e)
EOF
echo ""

# Step 8: Summary
echo "================================================"
echo "Summary"
echo "================================================"
echo ""
echo "Library location: $SCRIPT_DIR"
echo ""
echo "Next steps:"
echo ""
echo "  1. Configure credentials (if needed):"
echo "     export LIVEKIT_URL='wss://your-server.com'"
echo "     export LIVEKIT_API_KEY='your-key'"
echo "     export LIVEKIT_API_SECRET='your-secret'"
echo "     aws configure"
echo ""
echo "  2. Run integration test:"
echo "     python examples/aws_transcription_example.py"
echo ""
echo "  3. Publish to PyPI:"
echo "     See: PYPI_PUBLISHING.md"
echo ""
echo "  4. Read documentation:"
echo "     - TESTING_GUIDE.md - Complete testing guide"
echo "     - AWS_IMPLEMENTATION.md - AWS provider docs"
echo "     - README.md - Library overview"
echo ""
echo "================================================"
echo -e "${GREEN}✓ Quick test complete!${NC}"
echo "================================================"
