# Facial Quantum Matching Mirror — Backend

**ECE 445 Spring 2026 | Team #8**
Akhil Morisetty, Alex Cheng, Ethan Zhang

## Overview

The Facial Quantum Matching Mirror is an interactive display that uses a one-way mirror and facial recognition to match a user's face with well-known figures in selected categories (scientists, engineers, entrepreneurs, etc.). When activated, the system captures the user's photo, computes a facial embedding, and finds the closest visual match from a precomputed database. The matched figure is then displayed on a monitor behind the mirror, creating the illusion of a face-to-face encounter.

## Hardware

- **Raspberry Pi 4 Model B (4GB RAM)** — runs the backend pipeline
- **Logitech C270 HD Webcam** — captures user face images via USB
- **ESP32 WROOM-32** — handles button input, foot pedal, and LED control; communicates with the Pi over Bluetooth
- **21.5" IPS Monitor (350+ cd/m²)** — displays matched result behind one-way mirror
- **WS2812B LED Strip** — visual feedback during activation and processing
- **1TB USB External Storage** — stores database images, embeddings, and model files (mounted at `/mnt/storage`)
- **18x24" Two-Way Mirror Glass (70% reflective)** — acts as a mirror when idle, transparent when display is active

## Software Stack

| Component | Technology |
|---|---|
| Language | Python 3 |
| Camera Capture | OpenCV (`cv2.VideoCapture`) |
| Face Detection | OpenCV DNN (lightweight SSD) or Haar Cascade |
| Face Embedding | MobileFaceNet via ONNX Runtime |
| Database | Precomputed embeddings stored as `.npy` / JSON, organized by category |
| Matching | Cosine similarity (NumPy) |
| Display | Pygame fullscreen or Chromium kiosk mode |
| Bluetooth Comms | PyBluez or Bleak (BLE) |

## Project Structure

```
mirror-backend/                    # On microSD (Pi boot drive)
├── main.py                  # Main loop — listens for ESP32 signal, runs pipeline
├── capture.py               # Camera capture utilities
├── face_detect.py           # Face detection and cropping
├── embedding.py             # ONNX model loading and embedding extraction
├── matcher.py               # Cosine similarity matching against database
├── display.py               # Fullscreen display of matched result
├── bluetooth_listener.py    # Bluetooth communication with ESP32
├── precompute_embeddings.py # Offline script to generate database embeddings
├── config.py                # Paths, mount points, and settings
└── requirements.txt

/mnt/storage/                      # 1TB USB external drive
├── models/
│   └── mobilefacenet.onnx   # Pretrained MobileFaceNet model
└── database/
    ├── scientists/
    │   ├── embeddings.npy   # Precomputed embedding vectors
    │   ├── metadata.json    # Name, image path, etc.
    │   └── images/          # Display images for each figure
    ├── engineers/
    └── entrepreneurs/
```

## Setup

### 1. Mount External Storage

Plug in the 1TB USB drive. Find the device name and mount it:

```bash
# Identify the drive
lsblk

# Create mount point and mount (replace sdX1 with your device)
sudo mkdir -p /mnt/storage
sudo mount /dev/sdX1 /mnt/storage

# Auto-mount on boot — add this line to /etc/fstab:
# /dev/sdX1  /mnt/storage  ext4  defaults,nofail  0  2
echo '/dev/sdX1  /mnt/storage  ext4  defaults,nofail  0  2' | sudo tee -a /etc/fstab
```

> **Tip:** If the drive is NTFS or exFAT, install the appropriate driver (`sudo apt install exfat-fuse exfat-utils` or `ntfs-3g`). We recommend formatting as **ext4** for best performance on Linux.

### 2. Install Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-opencv python3-pip libatlas-base-dev
pip3 install onnxruntime numpy pygame pybluez --break-system-packages
```

### 3. Precompute Database Embeddings (Run on Laptop)

Collect a high-quality reference photo for each famous figure. Then run:

```bash
python3 precompute_embeddings.py --category scientists --images-dir ./raw_images/scientists/
```

This generates `embeddings.npy` and `metadata.json` for each category. Copy the `database/` folder to the Pi.

### 4. Transfer to Raspberry Pi

```bash
# Code goes on the microSD
scp -r mirror-backend/ pi@<PI_IP>:~/mirror-backend/

# Database and models go on the external drive
scp -r database/ pi@<PI_IP>:/mnt/storage/database/
scp -r models/ pi@<PI_IP>:/mnt/storage/models/
```

### 5. Run

```bash
cd ~/mirror-backend
python3 main.py
```

The system will start in idle mode (black screen) and wait for a Bluetooth signal from the ESP32.

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

## Performance Notes

- All database embeddings must be precomputed offline on a faster machine — do NOT generate them on the Pi at runtime.
- The ONNX model is loaded once at startup and kept in memory.
- Only the selected category's embeddings are compared, keeping the search space small.
- NumPy vectorized operations handle the similarity computation in a single pass.
- The Pi 4 with 4GB RAM comfortably handles MobileFaceNet + OpenCV + Pygame simultaneously.
- **Storage:** Embeddings and model files are loaded from the USB drive into RAM at boot. The 1TB drive stores all images, but since display images are read one at a time, USB 3.0 read speeds (~100+ MB/s) add negligible latency. For best results, use an SSD over an HDD to avoid seek time delays.

## Bluetooth Protocol

The ESP32 sends a simple string message over Bluetooth Serial:

| Message | Meaning |
|---|---|
| `START:scientists` | Begin capture, match against scientists category |
| `START:engineers` | Begin capture, match against engineers category |
| `START:entrepreneurs` | Begin capture, match against entrepreneurs category |

The Pi responds with:

| Message | Meaning |
|---|---|
| `ACK` | Signal received, processing started |
| `DONE:<match_id>` | Match complete, result displayed |

## High-Level Requirements

- Full interaction cycle completes within **20 seconds** of user activation
- Mirror achieves **70% reflectivity** in idle state; monitor visible through **30% transmittance** when active
- Facial recognition achieves **≥85% accuracy** against a baseline validation set

## License

For academic use — ECE 445, University of Illinois at Urbana-Champaign.