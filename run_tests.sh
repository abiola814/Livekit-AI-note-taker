#!/bin/bash
# Test runner script for AI Note library

set -e

echo "================================"
echo "AI Note Library - Test Runner"
echo "================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-cov
fi

# Run tests
echo "Running tests..."
echo ""

pytest tests/ -v

echo ""
echo "================================"
echo "✅ All tests passed!"
echo "================================"
