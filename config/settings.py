"""
settings.py — Central configuration for the Facial Quantum Matching Mirror.

Paths:
  - ASSETS_DIR: Famous figures' images, checked into the repo under assets/
  - STORAGE_ROOT: External drive on the Pi for model weights and embeddings.
                  Override with MIRROR_STORAGE_ROOT env var for local dev.
"""

import os

# ──────────────────────────────────────────────
# Project root (auto-detected from this file's location)
# ──────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ──────────────────────────────────────────────
# Assets — images of famous figures (in repo)
# ──────────────────────────────────────────────
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets", "database")

# ──────────────────────────────────────────────
# External storage — model + embeddings (on USB drive or local_data/)
# ──────────────────────────────────────────────
STORAGE_ROOT = os.environ.get("MIRROR_STORAGE_ROOT", "/mnt/storage")

MODEL_DIR = os.path.join(STORAGE_ROOT, "models")
DATABASE_DIR = ASSETS_DIR  # Images come from the repo

ONNX_MODEL_PATH = os.path.join(MODEL_DIR, "mobilefacenet.onnx")

# ──────────────────────────────────────────────
# Categories available for matching
# ──────────────────────────────────────────────
CATEGORIES = ["scientists", "engineers", "entrepreneurs"]

# ──────────────────────────────────────────────
# Camera settings
# ──────────────────────────────────────────────
CAMERA_INDEX = 0            # /dev/video0 — Logitech C270
CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720

# ──────────────────────────────────────────────
# Face detection
# ──────────────────────────────────────────────
FACE_DETECT_CONFIDENCE = 0.7

# Input size expected by MobileFaceNet
EMBEDDING_INPUT_SIZE = (112, 112)

# ──────────────────────────────────────────────
# Display
# ──────────────────────────────────────────────
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
DISPLAY_TIMEOUT_SEC = 15    # Seconds to show result before returning to idle

# ──────────────────────────────────────────────
# Bluetooth
# ──────────────────────────────────────────────
BT_UUID = "00001101-0000-1000-8000-00805F9B34FB"  # Standard SPP UUID
BT_DEVICE_NAME = "QuantumMirror_ESP32"

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_LEVEL = "INFO"