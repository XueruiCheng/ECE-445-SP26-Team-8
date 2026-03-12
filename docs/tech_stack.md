# Tech Stack — Facial Recognition Pipeline

A reference of every technology used in the facial recognition backend, what it does, and why we chose it.

## Python (3.11+)

Python is the primary language for the entire Raspberry Pi backend. It has the strongest ecosystem for computer vision and machine learning on ARM devices and is the most well-supported language on the Raspberry Pi. Every module in `src/` and `scripts/` is written in Python.

**Used in:** All backend code

## OpenCV (cv2) — version 4.9+

OpenCV (Open Source Computer Vision Library) handles two jobs in our project. First, it interfaces with the Logitech C270 webcam over USB to capture frames using `cv2.VideoCapture`. Second, its DNN (Deep Neural Network) module runs a lightweight face detection model that locates the user's face in the captured image and crops it to the 112x112 pixel region that the embedding model expects. We use the headless build (`opencv-python-headless`) since the display is handled by Pygame, not OpenCV GUI windows.

**Used in:** `src/capture.py`, `src/face_detect.py`

**Install:** `pip install opencv-python-headless`

**System dependencies (Pi):** `sudo apt install python3-opencv libatlas-base-dev`

## ONNX Runtime — version 1.17+

ONNX Runtime is a high-performance inference engine for running machine learning models in the ONNX (Open Neural Network Exchange) format. It runs our MobileFaceNet model to extract a 512-dimensional face embedding vector from a cropped face image. We use ONNX Runtime instead of heavier frameworks like PyTorch or TensorFlow because it is significantly faster on ARM CPUs and has a much smaller memory footprint. It loads the `.onnx` model file once at startup and keeps it in memory, so each inference call takes roughly 200–500ms on the Pi 4 with 4GB RAM.

**Used in:** `src/embedding.py`, `scripts/precompute_embeddings.py`

**Install:** `pip install onnxruntime`

## MobileFaceNet (ONNX model file)

MobileFaceNet is a lightweight convolutional neural network specifically designed for face verification on mobile and embedded devices. It uses under 1 million parameters and produces a 512-dimensional vector (called an embedding) that numerically represents a face. Two faces that look similar will have embeddings that are close together in vector space, which is how we find the best match. We use a pretrained model exported to ONNX format. The model file is approximately 4MB and is stored on the external USB drive, not in the git repo.

**Used in:** `src/embedding.py` (runtime inference), `scripts/precompute_embeddings.py` (offline database generation)

**Stored at:** `/mnt/storage/models/mobilefacenet.onnx`

## NumPy — version 1.24+

NumPy is a numerical computing library that provides fast array and matrix operations. We use it for three things: storing precomputed face embeddings as `.npy` files (NumPy's binary array format), performing vectorized cosine similarity calculations to compare the user's embedding against all embeddings in a category in a single operation, and image array manipulation when preprocessing frames for the detection and embedding models.

**Used in:** `src/matcher.py`, `src/embedding.py`, `src/face_detect.py`, `scripts/precompute_embeddings.py`

**Install:** `pip install numpy`

## SciPy — version 1.11+

SciPy is a scientific computing library built on NumPy. We use it specifically for `scipy.spatial.distance.cosine`, which computes the cosine distance between two vectors. This is the core of our matching algorithm — the database face with the smallest cosine distance to the user's face embedding is the match. SciPy's implementation is optimized in C, making it faster than writing cosine similarity by hand in pure Python.

**Used in:** `src/matcher.py`

**Install:** `pip install scipy`

## Pillow (PIL) — version 10.0+

Pillow is an imaging library for opening, manipulating, and saving image files. We use it to load the display images (famous figures' photos) from disk and handle image format conversions when preprocessing input photos for the embedding model. While OpenCV handles camera capture, Pillow handles image I/O tasks where we need standard JPEG/PNG loading without OpenCV's BGR color ordering.

**Used in:** `src/display.py`, `scripts/precompute_embeddings.py`

**Install:** `pip install Pillow`

## Pygame — version 2.5+

Pygame is a multimedia library used to control the fullscreen display output on the monitor behind the one-way mirror. When idle, Pygame renders a black screen so the monitor produces no light and the mirror stays reflective. When a match is found, Pygame displays the matched figure's image fullscreen. It also handles the loading animation shown during processing. We chose Pygame over Tkinter or a web browser because it gives direct, low-level control over fullscreen rendering with minimal overhead.

**Used in:** `src/display.py`

**Install:** `pip install pygame`

**System dependencies (Pi):** `sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev`

## PyBluez — version 0.23

PyBluez is a Python wrapper around the Linux Bluetooth stack. It establishes a Bluetooth Serial Port Profile (SPP) connection between the Raspberry Pi and the ESP32 microcontroller. The ESP32 sends messages like `START:scientists` when the user selects a category and activates the system. The Pi listens on this Bluetooth serial channel, parses the message, and kicks off the capture-match-display pipeline. PyBluez only runs on the Pi — on your laptop, Bluetooth is skipped and keyboard input simulates the ESP32 signal.

**Used in:** `src/bluetooth_listener.py`

**Install:** `pip install PyBluez`

**System dependencies (Pi):** `sudo apt install libbluetooth-dev bluetooth bluez`

## pytest — version 7.0+

pytest is a testing framework used to run unit tests for each module and integration tests for the full pipeline. The integration test `test_pipeline.py` measures end-to-end timing to verify we meet the 10-second matching requirement. Test files map one-to-one with the verification procedures in the ECE 445 design document.

**Used in:** `tests/`

**Install:** `pip install pytest`

**Run:** `python -m pytest tests/ -v`

## Summary

| Technology | Version | Purpose | Runs On |
|---|---|---|---|
| Python | 3.11+ | Backend language | Pi + Laptop |
| OpenCV | 4.9+ | Camera capture and face detection | Pi + Laptop |
| ONNX Runtime | 1.17+ | Runs MobileFaceNet inference | Pi + Laptop |
| MobileFaceNet | — | Generates 512-D face embeddings (~4MB model) | Pi + Laptop |
| NumPy | 1.24+ | Embedding storage, vectorized cosine similarity | Pi + Laptop |
| SciPy | 1.11+ | Optimized cosine distance computation | Pi + Laptop |
| Pillow | 10.0+ | Image loading and format conversion | Pi + Laptop |
| Pygame | 2.5+ | Fullscreen monitor display | Pi |
| PyBluez | 0.23 | Bluetooth serial communication with ESP32 | Pi only |
| pytest | 7.0+ | Unit and integration testing | Pi + Laptop |