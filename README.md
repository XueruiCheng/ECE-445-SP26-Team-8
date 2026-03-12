# Facial Quantum Matching Mirror

**ECE 445 Spring 2026 | Team #8**
Akhil Morisetty, Alex Cheng, Ethan Zhang | TA: Wesley Pang

## Overview

An interactive display that uses a one-way mirror and facial recognition to match a user's face with well-known figures in selected categories (scientists, engineers, entrepreneurs). When activated, the system captures the user's photo, computes a facial embedding, finds the closest visual match from a precomputed database, and displays the result on a monitor behind the mirror — creating the illusion of a face-to-face encounter with a famous figure who resembles them.

## Hardware

- Raspberry Pi 4 Model B (4GB RAM) — runs the backend pipeline
- Logitech C270 HD Webcam — captures user face images via USB
- ESP32 WROOM-32 — handles button input, foot pedal, and LED control; communicates with Pi over Bluetooth
- 21.5" IPS Monitor (350+ cd/m²) — displays matched result behind one-way mirror
- WS2812B LED Strip (5V, 60 LED/m) — visual feedback during activation and processing
- 1TB USB External Storage — stores database images, embeddings, and model files
- 18x24" Tempered Two-Way Mirror Glass (70% reflective)
- Thin Film Foot Pressure Sensor — triggers system activation

## Repository Structure

```
quantum-mirror/
├── README.md
├── requirements.txt             # Python dependencies (all platforms)
├── requirements-pi.txt          # Additional Pi-only deps (includes Bluetooth)
├── setup.sh                     # One-time Raspberry Pi setup script
├── .gitignore
│
├── assets/                      # Famous figures' images (checked into repo)
│   └── database/
│       ├── scientists/
│       │   └── images/          # e.g., einstein.jpg, curie.jpg
│       ├── engineers/
│       │   └── images/
│       └── entrepreneurs/
│           └── images/
│
├── src/                         # Runtime code (runs on the Pi)
│   ├── __init__.py
│   ├── main.py                  # Entry point — main loop
│   ├── capture.py               # Webcam image capture
│   ├── face_detect.py           # Face detection and cropping
│   ├── embedding.py             # ONNX model loading + embedding extraction
│   ├── matcher.py               # Cosine similarity matching
│   ├── display.py               # Fullscreen Pygame display output
│   └── bluetooth_listener.py    # Bluetooth serial comms with ESP32
│
├── config/
│   ├── __init__.py
│   └── settings.py              # All paths, constants, thresholds
│
├── scripts/                     # Utility scripts (run on laptop or Pi)
│   ├── precompute_embeddings.py # Generate embeddings from reference photos
│   ├── download_model.py        # Fetch MobileFaceNet ONNX weights
│   └── validate_accuracy.py     # Run accuracy test against validation set
│
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── test_capture.py
│   ├── test_face_detect.py
│   ├── test_embedding.py
│   ├── test_matcher.py
│   ├── test_bluetooth.py
│   └── test_pipeline.py         # End-to-end timing test
│
├── docs/                        # Design documents and diagrams
│   └── Design_Document.docx
│
└── esp32/                       # ESP32 Arduino firmware
    ├── main.ino
    ├── bluetooth_comm.h
    ├── button_handler.h
    └── led_controller.h
```

Data that lives on the 1TB external drive (NOT in the repo):

```
/mnt/storage/
├── models/
│   └── mobilefacenet.onnx       # ~4MB pretrained model
└── embeddings/
    ├── scientists/
    │   ├── embeddings.npy       # Precomputed 512-D vectors
    │   └── metadata.json        # Maps embedding index → image filename
    ├── engineers/
    │   ├── embeddings.npy
    │   └── metadata.json
    └── entrepreneurs/
        ├── embeddings.npy
        └── metadata.json
```

## Software Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Camera Capture | OpenCV (`cv2.VideoCapture`) |
| Face Detection | OpenCV DNN with lightweight SSD |
| Face Embedding | MobileFaceNet via ONNX Runtime |
| Database | Precomputed `.npy` embeddings + `metadata.json` per category |
| Matching | Cosine similarity (NumPy / SciPy) |
| Display | Pygame (fullscreen) |
| Bluetooth | PyBluez (Bluetooth SPP) — Pi only |
| Testing | pytest |

---

## Local Development Setup (Laptop / Desktop)

Use this to develop and test the facial recognition pipeline on your own machine. You do **not** need the Pi, ESP32, or any mirror hardware for local development.

### Prerequisites

**All platforms:**
- Python 3.11 or newer — check with `python3 --version`
- Git
- A webcam (any USB webcam works, or you can test with static images)

**macOS:**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and SDL2 (SDL2 is needed by Pygame)
brew install python@3.11 sdl2 sdl2_image sdl2_mixer sdl2_ttf

# Verify
python3 --version   # Should show 3.11+
```

**Windows:**
1. Install Python 3.11+ from https://www.python.org/downloads/
2. **Check "Add Python to PATH"** during installation
3. Install Git from https://git-scm.com/downloads
4. Verify in Command Prompt: `python --version`

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Verify
python3 --version
```

### Step 1 — Clone the repo

```bash
git clone https://github.com/<your-org>/quantum-mirror.git
cd quantum-mirror
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv
```

Activate it (you need to do this every time you open a new terminal):

```bash
# macOS / Linux:
source venv/bin/activate

# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal prompt.

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

Verify everything installed:

```bash
python -c "import cv2; print('OpenCV', cv2.__version__)"
python -c "import onnxruntime; print('ONNX Runtime', onnxruntime.__version__)"
python -c "import numpy; print('NumPy', numpy.__version__)"
python -c "import pygame; print('Pygame', pygame.__version__)"
python -c "import scipy; print('SciPy', scipy.__version__)"
python -c "from PIL import Image; print('Pillow OK')"
```

All six should print without errors. If any fail, install them individually:

```bash
pip install opencv-python-headless Pillow onnxruntime numpy pygame scipy pytest
```

> **Note:** `PyBluez` is NOT in `requirements.txt` — it's Pi-only and would fail on macOS/Windows. You don't need Bluetooth for local development.

### Step 4 — Set up local data directory

The famous figures' images are already in the repo under `assets/`. You only need a local folder for the model and precomputed embeddings:

```bash
mkdir -p local_data/models
mkdir -p local_data/embeddings/scientists
mkdir -p local_data/embeddings/engineers
mkdir -p local_data/embeddings/entrepreneurs
```

Tell the app to use this folder for model/embeddings:

```bash
# macOS / Linux:
export MIRROR_STORAGE_ROOT="./local_data"

# Windows (Command Prompt):
set MIRROR_STORAGE_ROOT=./local_data

# Windows (PowerShell):
$env:MIRROR_STORAGE_ROOT="./local_data"
```

> **Tip:** Add the export line to your shell profile (`~/.bashrc`, `~/.zshrc`) so you don't have to set it every time.

### Step 5 — Download the MobileFaceNet model

```bash
python scripts/download_model.py
```

This downloads `mobilefacenet.onnx` (~4MB) into `local_data/models/`. If the script isn't implemented yet, download the model manually and place it at `local_data/models/mobilefacenet.onnx`.

### Step 6 — Add images to the database

Drop clear, front-facing portrait photos of famous figures into the category folders under `assets/`:

```
assets/database/scientists/images/
├── einstein.jpg
├── curie.jpg
├── hawking.jpg
└── tesla.jpg
```

Image requirements:
- JPEG or PNG format
- At least 200x200 pixels
- Clear, front-facing photo with one visible face
- Filename becomes the figure's ID (e.g., `einstein.jpg` → id `einstein`)

These images are checked into the repo so all teammates have them after cloning.

### Step 7 — Precompute embeddings

Generate the embedding vectors and metadata for a category:

```bash
python scripts/precompute_embeddings.py --category scientists
```

This reads images from `assets/database/scientists/images/` and creates two files in `local_data/embeddings/scientists/`:
- `embeddings.npy` — NumPy array of 512-D vectors, one per figure
- `metadata.json` — names, titles, and image paths for each figure

Repeat for each category you want to test.

### Step 8 — Run tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_capture.py -v

# Run a specific test function
python -m pytest tests/test_matcher.py::test_cosine_similarity -v
```

### Step 9 — Run the pipeline locally

```bash
python -m src.main --local
```

The `--local` flag does two things:
- Skips Bluetooth and uses keyboard input to simulate the ESP32 signal
- Uses a windowed Pygame display instead of fullscreen

You should see a prompt to select a category. Press a key, and the system will capture from your webcam, run the matching pipeline, and display the result.

### Troubleshooting (Local)

**"No module named cv2"** — Run `pip install opencv-python-headless`

**"No module named onnxruntime"** — Run `pip install onnxruntime`. On Apple Silicon Macs, you may need `pip install onnxruntime-silicon` instead.

**Camera not found** — Check that your webcam is connected. Run `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"` — it should print `True`. If it prints `False`, try index 1: your built-in camera may be at index 0 and the USB webcam at index 1.

**Pygame window doesn't appear** — On macOS, Pygame may need to run from the system Python, not from a venv. Try `pip install pygame --pre` for the latest build.

**MIRROR_STORAGE_ROOT not set** — The app defaults to `/mnt/storage` which doesn't exist on your laptop. Make sure you set the environment variable (Step 4).

---

## Raspberry Pi Setup (Production)

### Step 1 — Flash Raspberry Pi OS

Use the Raspberry Pi Imager to flash **Raspberry Pi OS (64-bit, Debian Bookworm)** onto your microSD card. During imaging, click the gear icon and:
- Enable SSH
- Set username to `pi`
- Set your WiFi credentials

### Step 2 — Clone the repo onto the Pi

```bash
ssh pi@<PI_IP>
git clone https://github.com/<your-org>/quantum-mirror.git
cd quantum-mirror
```

### Step 3 — Run the setup script

```bash
sudo bash setup.sh
```

This handles:
- System package updates
- Installing OS-level dependencies: OpenCV, Bluetooth libs, SDL2, etc.
- Installing Python dependencies from `requirements-pi.txt` (includes PyBluez)
- Mounting the 1TB external USB drive at `/mnt/storage`
- Creating the database folder structure on the drive
- Enabling the Bluetooth service

### Step 4 — Mount external storage (if setup.sh skipped it)

```bash
# Find your drive
lsblk

# Mount it (replace sda1 with your actual device)
sudo mkdir -p /mnt/storage
sudo mount /dev/sda1 /mnt/storage

# Make it permanent
echo '/dev/sda1  /mnt/storage  ext4  defaults,nofail  0  2' | sudo tee -a /etc/fstab
```

> **Important:** Plug the drive into a **blue USB 3.0 port** on the Pi (not the black USB 2.0 ports). Format as ext4 for best performance. If the drive is NTFS or exFAT: `sudo apt install exfat-fuse exfat-utils` or `ntfs-3g`.

### Step 5 — Copy model and embeddings to external drive

From your laptop (images are already in the repo, so only model + embeddings need to go on the drive):

```bash
scp local_data/models/mobilefacenet.onnx pi@<PI_IP>:/mnt/storage/models/
scp -r local_data/embeddings/* pi@<PI_IP>:/mnt/storage/embeddings/
```

Verify on the Pi:

```bash
ls /mnt/storage/models/
# Should show: mobilefacenet.onnx

ls /mnt/storage/embeddings/scientists/
# Should show: embeddings.npy  metadata.json
```

### Step 6 — Pair the ESP32 over Bluetooth

```bash
bluetoothctl
> power on
> agent on
> scan on
# Wait for "QuantumMirror_ESP32" to appear
> pair <ESP32_MAC_ADDRESS>
> trust <ESP32_MAC_ADDRESS>
> quit
```

### Step 7 — Run

```bash
cd ~/quantum-mirror
python3 -m src.main
```

The system starts in idle mode (black screen) and waits for a Bluetooth signal from the ESP32.

### Step 8 — Auto-start on boot (optional)

Create a systemd service so the mirror starts automatically:

```bash
sudo nano /etc/systemd/system/quantum-mirror.service
```

Paste:

```ini
[Unit]
Description=Facial Quantum Matching Mirror
After=bluetooth.target

[Service]
User=pi
WorkingDirectory=/home/pi/quantum-mirror
ExecStart=/usr/bin/python3 -m src.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable quantum-mirror
sudo systemctl start quantum-mirror

# Check status
sudo systemctl status quantum-mirror

# View logs
journalctl -u quantum-mirror -f
```

---

## Pipeline Flow

1. **Idle** — Monitor off, mirror is reflective, system waits for Bluetooth signal
2. **Activated** — ESP32 sends category + start signal over Bluetooth
3. **Capture** — Pi triggers webcam, captures a single frame (~1s)
4. **Detect** — Face is detected and cropped to 112x112 (~50ms)
5. **Embed** — MobileFaceNet generates a 512-D face embedding (~400ms)
6. **Match** — Cosine similarity against precomputed category embeddings (~30ms)
7. **Display** — Matched figure shown fullscreen on monitor behind mirror
8. **Reset** — After timeout, returns to idle state

**Expected total time: ~1.5–2 seconds** (well under the 10s requirement)

## Bluetooth Protocol

The ESP32 sends a simple string over Bluetooth Serial (SPP):

| Message | Meaning |
|---|---|
| `START:scientists` | Capture + match against scientists |
| `START:engineers` | Capture + match against engineers |
| `START:entrepreneurs` | Capture + match against entrepreneurs |

The Pi responds with:

| Message | Meaning |
|---|---|
| `ACK` | Signal received, processing started |
| `DONE:<match_id>` | Match complete, result displayed |
| `ERR:<message>` | Something went wrong |

## metadata.json Format

Each category folder contains a `metadata.json`:

```json
{
  "figures": [
    {
      "id": "einstein",
      "name": "Albert Einstein",
      "title": "Theoretical Physicist",
      "image": "einstein.jpg",
      "embedding_index": 0
    },
    {
      "id": "curie",
      "name": "Marie Curie",
      "title": "Physicist & Chemist",
      "image": "curie.jpg",
      "embedding_index": 1
    }
  ]
}
```

The `embedding_index` maps to the corresponding row in `embeddings.npy`.

## Performance Notes

- Precompute all database embeddings offline (on your laptop) — never on the Pi at runtime.
- The ONNX model is loaded once at startup and kept in memory.
- Only the selected category's embeddings are searched, keeping comparisons small.
- NumPy vectorized cosine similarity handles matching in a single pass.
- Pi 4 with 4GB RAM comfortably runs MobileFaceNet + OpenCV + Pygame simultaneously.
- Use an SSD (not HDD) for the external drive to avoid seek delays.

## High-Level Requirements

- Full interaction cycle (LED → capture → match → display) within **20 seconds**
- Mirror has **70% reflectivity** when idle; monitor visible through **30% transmittance** when active
- Facial recognition achieves **≥85% top-match accuracy** against validation set

## Team Responsibilities

| Member | Primary Focus |
|---|---|
| Akhil | ESP32 firmware, Bluetooth integration, PCB |
| Alex | Power subsystem, LED control, PCB |
| Ethan | Camera pipeline, facial recognition backend, display |

## License

For academic use — ECE 445, University of Illinois at Urbana-Champaign.