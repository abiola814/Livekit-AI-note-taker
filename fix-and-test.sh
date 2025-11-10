#!/bin/bash
# Quick fix and test script

echo "🔧 Fixing installation and running tests..."
echo ""

# Upgrade pip
echo "1️⃣  Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install with dev and AWS dependencies
echo "2️⃣  Installing library with dev + AWS dependencies..."
pip install -e ".[dev,aws]" --quiet

# Run tests
echo "3️⃣  Running tests..."
echo ""
pytest -v

echo ""
echo "✅ Done!"
