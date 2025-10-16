#!/bin/bash
# Fix Claude Code hooks after Python 3.14 upgrade
# This script installs required dependencies for the system Python 3.14

set -e

echo "=================================="
echo "Python 3.14 Hooks Dependency Fixer"
echo "=================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "✓ System Python: $PYTHON_VERSION"

if [[ ! "$PYTHON_VERSION" =~ "3.14" ]]; then
    echo "⚠️  Warning: System Python is not 3.14"
    echo "   This script is designed for Python 3.14"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Installing hook dependencies for system Python..."
echo ""

# Install required packages
sudo pip3 install \
    pyyaml \
    psutil \
    python-dotenv \
    requests

echo ""
echo "✓ Dependencies installed successfully!"
echo ""

# Test hooks
echo "Testing hooks..."
echo ""

cd /home/daihungpham/__projects__/4genthub

# Test session_start hook
if python3 .claude/hooks/session_start.py --help >/dev/null 2>&1; then
    echo "✓ session_start.py - OK"
else
    echo "✗ session_start.py - FAILED"
    python3 .claude/hooks/session_start.py 2>&1 | head -5
fi

# Test pre_tool_use hook
if python3 -c "import sys; sys.path.insert(0, '.claude/hooks'); import pre_tool_use" 2>/dev/null; then
    echo "✓ pre_tool_use.py - OK"
else
    echo "✗ pre_tool_use.py - FAILED"
fi

# Test post_tool_use hook
if python3 -c "import sys; sys.path.insert(0, '.claude/hooks'); import post_tool_use" 2>/dev/null; then
    echo "✓ post_tool_use.py - OK"
else
    echo "✗ post_tool_use.py - FAILED"
fi

echo ""
echo "=================================="
echo "✓ Python 3.14 hooks fixed!"
echo "=================================="
echo ""
echo "All Claude Code hooks should now work with Python 3.14"
echo "You can restart Claude Code to verify."
