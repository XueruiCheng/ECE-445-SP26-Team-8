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
├── setup.sh                     # One-time Raspberry Pi setup script
├── .gitignore
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
└── database/
    ├── scientists/
    │   ├── embeddings.npy       # Precomputed 512-D vectors
    │   ├── metadata.json        # Names, titles, image filenames
    │   └── images/              # Full-res display images
    ├── engineers/
    │   ├── embeddings.npy
    │   ├── metadata.json
    │   └── images/
    └── entrepreneurs/
        ├── embeddings.npy
        ├── metadata.json
        └── images/
```

## Software Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Camera Capture | OpenCV (`cv2.VideoCapture`) |
| Face Detection | OpenCV DNN with lightweight SSD |
| Face Embedding | MobileFaceNet via ONNX Runtime |
| Database | Precomputed `.npy` embeddings + `metadata.json` per category |
| Matching | Cosine similarity (NumPy) |
| Display | Pygame (fullscreen) |
| Bluetooth | PyBluez (Bluetooth SPP) |
| Testing | pytest |

## Prerequisites

### All Platforms

- Python 3.11 or newer
- Git
- A webcam (any USB webcam works for local testing)

### macOS

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and SDL2 (needed by Pygame)
brew install python@3.11 sdl2 sdl2_image sdl2_mixer sdl2_ttf
```

### Windows

- Install Python 3.11+ from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation
- Install Git from https://git-scm.com/downloads

### Ubuntu / Debian (including Raspberry Pi OS)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

## Local Development Setup (Laptop / Desktop)

Use this to develop and test the facial recognition pipeline on your own machine before deploying to the Pi. You do NOT need the Pi, ESP32, or any mirror hardware for local development.

### 1. Clone the repo

```bash
git clone https://github.com/<your-org>/quantum-mirror.git
cd quantum-mirror
```

### 2. Create a virtual environment

```bash
python3 -m venv venv

# Activate it:
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

> **Note on PyBluez:** PyBluez requires Bluetooth system libraries. On your laptop you may get an install error — this is fine. Bluetooth is only needed on the Pi. To skip it locally, install everything else manually:
> ```bash
> pip install opencv-python-headless Pillow onnxruntime numpy pygame scipy
> ```

### 4. Download the MobileFaceNet model

```bash
python scripts/download_model.py
```

This downloads `mobilefacenet.onnx` into a local `models/` directory for testing.

### 5. Create a local test database

For local testing, create a small test database instead of using the full external drive:

```bash
mkdir -p local_data/database/scientists/images
mkdir -p local_data/database/engineers/images
mkdir -p local_data/database/entrepreneurs/images
mkdir -p local_data/models
```

Then update `config/settings.py` temporarily:

```python
STORAGE_ROOT = "./local_data"   # Change from "/mnt/storage" for local dev
```

Or set it via an environment variable (recommended so you don't accidentally commit the change):

```bash
export MIRROR_STORAGE_ROOT="./local_data"
```

### 6. Precompute embeddings for your test images

Drop a few reference photos into `local_data/database/scientists/images/`, then:

```bash
python scripts/precompute_embeddings.py --category scientists --images-dir ./local_data/database/scientists/images/
```

### 7. Run tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a single test
python -m pytest tests/test_capture.py -v
```

### 8. Run the pipeline locally

```bash
python -m src.main --local
```

The `--local` flag skips Bluetooth and uses keyboard input to simulate the ESP32 signal.

## Raspberry Pi Setup (Production)

### 1. Flash Raspberry Pi OS

Use the Raspberry Pi Imager to flash **Raspberry Pi OS (64-bit)** onto your microSD card. Enable SSH and set your WiFi during imaging.

### 2. Clone the repo onto the Pi

```bash
ssh pi@<PI_IP>
git clone https://github.com/<your-org>/quantum-mirror.git
cd quantum-mirror
```

### 3. Run the setup script

```bash
sudo bash setup.sh
```

This handles:
- System package updates
- Installing OS-level dependencies (OpenCV, Bluetooth, SDL2, etc.)
- Installing Python dependencies from `requirements.txt`
- Mounting the 1TB external USB drive at `/mnt/storage`
- Creating the database folder structure on the drive
- Enabling Bluetooth service

### 4. Mount external storage (if setup.sh skipped it)

```bash
# Find your drive
lsblk

# Mount it
sudo mkdir -p /mnt/storage
sudo mount /dev/sda1 /mnt/storage

# Make it permanent (add to /etc/fstab)
echo '/dev/sda1  /mnt/storage  ext4  defaults,nofail  0  2' | sudo tee -a /etc/fstab
```

> **Tip:** Format the drive as ext4 for best Linux performance. If it's NTFS or exFAT, install drivers: `sudo apt install exfat-fuse exfat-utils` or `ntfs-3g`.

### 5. Copy model and database to external drive

From your laptop:

```bash
scp models/mobilefacenet.onnx pi@<PI_IP>:/mnt/storage/models/
scp -r local_data/database/ pi@<PI_IP>:/mnt/storage/database/
```

### 6. Pair the ESP32 over Bluetooth

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

### 7. Run

```bash
cd ~/quantum-mirror
python3 -m src.main
```

The system starts in idle mode (black screen) and waits for a Bluetooth signal from the ESP32.

### 8. Auto-start on boot (optional)

Create a systemd service so the mirror starts automatically when the Pi powers on:

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

Enable it:

```bash
sudo systemctl enable quantum-mirror
sudo systemctl start quantum-mirror
```

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
- Use an SSD (not HDD) for the external drive — USB 3.0 reads at 100+ MB/s with no seek delay.
- Plug the drive into a **blue USB 3.0 port** on the Pi, not the black USB 2.0 ports.

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