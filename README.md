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


## Raspberry Pi

Once you have connected your Raspberry Pi to your monitor and hooked up a keyboard through the USB-port, try running this command to see
if an instance of chromium will pop up. Make sure that you have configured wifi properly and you have installed all the necessary dependencies:

```bash
sudo apt update
sudo apt install xorg chromium
```

Command to run your server
```bash
uvicorn display.server:app --host 0.0.0.0 --port 8000
```

Build the frontend before kiosk/server runs
```bash
cd display/frontend
npm run build
```

### Launching the kiosk with xinit

The recommended way to start the full kiosk (xrandr setup, frontend build, uvicorn server, and Chromium in kiosk mode) is via [start-kiosk.sh](start-kiosk.sh):

```bash
xinit ./start-kiosk.sh -- :0
```

`xinit` boots a minimal X server on display `:0` and runs `start-kiosk.sh` as the X client. The script handles:
- Activating the project `venv` if present
- Rotating `HDMI-2` and disabling `HDMI-1` via `xrandr`
- Disabling screen blanking / DPMS and hiding the cursor with `unclutter`
- Building the React frontend (`npm run build` in [display/frontend/](display/frontend/))
- Starting the FastAPI backend (`uvicorn server:app` on port `8000`)
- Waiting for the server to come up, then launching Chromium in `--kiosk` mode pointed at the splash page

Logs are appended to `/tmp/kiosk.log`.

If you only want a bare-bones launch without the helper script:
```bash
xinit /bin/bash -c "chromium-browser --kiosk http://localhost:8000" -- :0
```

### Validation mode

Validation mode lets you demo the pipeline end-to-end with a known expected match. The webcam preview and thumbs-up gesture detection still run normally, but the frame fed into the face model is replaced with a noisy version of a reference image from [model/data/raw_images/](model/data/raw_images/). See [display/validation_loop.py](display/validation_loop.py) for the noise pipeline.

Launch via `start-kiosk.sh` with the `--validate` flag and the figure's name (matched against `<name>.jpg` in the raw images directory, with spaces and underscores interchangeable):

```bash
xinit ./start-kiosk.sh --validate "Avery Broderick" -- :0
```

Noise level defaults to `harsh`; override with the `VALIDATE_NOISE` env var (`mild` or `harsh`):

```bash
VALIDATE_NOISE=mild xinit ./start-kiosk.sh --validate "Avery Broderick" -- :0
```

You can also run validation mode without the kiosk wrapper by exporting `VALIDATE_NAME` before starting the server:

```bash
export VALIDATE_NAME="Avery Broderick"
export VALIDATE_NOISE=harsh   # optional: mild | harsh
uvicorn display.server:app --host 0.0.0.0 --port 8000
```

Unset `VALIDATE_NAME` (or omit `--validate`) to return to normal operation.

## Hardware

- Raspberry Pi 4 Model B (4GB RAM) — runs the backend pipeline
- Logitech C270 HD Webcam — captures user face images via USB
- ESP32 WROOM-32 — handles button input, foot pedal, and LED control; communicates with the Pi over Bluetooth
- 21.5" IPS Monitor — displays the matched result behind the mirror
- WS2812B LED Strip — visual feedback during activation and result display
- 18x24" Tempered Two-Way Mirror Glass (70% reflective)
- Thin Film Foot Pressure Sensor — triggers system activation
- 1TB USB External Storage — stores database images, embeddings, and model files
