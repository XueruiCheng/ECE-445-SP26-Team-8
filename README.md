## Overview

An interactive display that uses a two-way mirror and facial recognition to match a user's face with a well-known figure from a selected category (scientists, engineers, or entrepreneurs). When a user steps up and activates the system, a webcam captures their face, computes a facial embedding, finds the closest visual match from a precomputed database, and displays the result on a monitor behind the mirror.


## Running the Pipeline


```bash
python -m model.dataset_builder
```
- You only need to build the image dataset and precompute embeddings once locally unless you make changes to the base image dataset


```bash
python -m model.embed_dataset
```
- Re-run this step any time you add or remove images from the database


```bash
python main.py
```
- Webcam index defaults to `0` to use your computers default camera
- Press `ESC` at any point to cancel


## Hardware

- Raspberry Pi 4 Model B (4GB RAM) — runs the backend pipeline
- Logitech C270 HD Webcam — captures user face images via USB
- ESP32 WROOM-32 — handles button input, foot pedal, and LED control; communicates with the Pi over Bluetooth
- 21.5" IPS Monitor — displays the matched result behind the mirror
- WS2812B LED Strip — visual feedback during activation and result display
- 18x24" Tempered Two-Way Mirror Glass (70% reflective)
- Thin Film Foot Pressure Sensor — triggers system activation
- 1TB USB External Storage — stores database images, embeddings, and model files
