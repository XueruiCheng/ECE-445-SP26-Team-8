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
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"

# Create data directories
echo "Creating data directories..."
mkdir -p "$REPO_DIR/model/data/raw_images"
mkdir -p "$REPO_DIR/assets/database/scientists/images"
mkdir -p "$REPO_DIR/assets/database/engineers/images"
mkdir -p "$REPO_DIR/assets/database/entrepreneurs/images"

# Crawling and downloading images
echo ""
echo "Scraping profiles and downloading images..."
python3 -m model.dataset_builder

# Generate embeddings
echo ""
echo "This will download the InsightFace model on first run (~300MB)..."
python3 -m model.embed_dataset

echo ""
echo "To run the face matcher:"
echo "  source venv/bin/activate"
echo "  python3 main.py"
