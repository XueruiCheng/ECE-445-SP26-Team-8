#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== ECE 445 Team 8 - Setup ==="
echo "Project root: $REPO_DIR"

# Check whether Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

# look at the current python version installed
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Using Python $PYTHON_VERSION"

# Create virtual environment
VENV_DIR="$REPO_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists"
fi

source "$VENV_DIR/bin/activate"

# Install dependencies
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"

# Crawling and downloading images
echo ""
python3 -m model.dataset_builder

# Generate embeddings
echo ""
python3 -m model.embed_dataset
