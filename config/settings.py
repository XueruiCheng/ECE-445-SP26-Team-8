"""
settings.py — Central configuration for the Facial Quantum Matching Mirror.

Update STORAGE_ROOT if your external drive mounts somewhere other than /mnt/storage.
"""

import os

# ──────────────────────────────────────────────
# Storage paths
# ──────────────────────────────────────────────
STORAGE_ROOT = os.environ.get("MIRROR_STORAGE_ROOT", "/mnt/storage")

MODEL_DIR = os.path.join(STORAGE_ROOT, "models")
DATABASE_DIR = os.path.join(STORAGE_ROOT, "database")

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