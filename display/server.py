from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from face_match import find_top_matches

import os
import queue
import asyncio
import threading
from contextlib import asynccontextmanager

import cv2
import numpy as np
import insightface
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# globals
WARMUP_FRAMES = 60
MIN_DET_SCORE = 0.7
FRAMES_TO_COLLECT = 6
INFERENCE_EVERY_N_FRAMES = 3
LOGITECH_RASP_CAMERA_IDX = '/dev/video0'
LOCAL_CAMERA_IDX = '0'

DIST_DIR = "display/frontend/dist/frontend/browser"

# list of events to send to our frontend
event_queue : queue.Queue = queue.Queue()
active_websocket = WebSocket | None = None

# main thread
@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=camera_loop, daemon=True).start()
    asyncio.create_task(broadcast_event())
    yield


app = FastAPI(title="Quantum Mirror")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:4200",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# maybe add unique identifier into 
@app.websocket("/ws/camera")
async def websocket_camera(websocket : WebSocket):
    global active_websocket
    await websocket.accept()
    active_websocket = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websocket = None

def detect_right_hand_rule():



def camera_loop():
    # switch this based on what camera you are using
    cap = cv2.VideoCapture(LOCAL_CAMERA_IDX)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    face_model = insightface.app.FaceAnalysis(name="buffalo_l")
    face_model.prepare(ctx_id=0, det_size=(320, 320))

    collected_embeddings = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_count += 1
        if frame_count % 3 == 0:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            event_queue.put(buffer.tobytes())
        
        if frame_count % INFERENCE_EVERY_N_FRAMES != 0:
            continue

        faces = face_model.get(frame)

        if len(faces) != 1:
            event_queue.put({
                "type": "face_error",
                "reason": "no_face" if len(faces) == 0 else "multiple_faces",
                "count": len(faces)
            })
            continue

        face = faces[0]
        # should we do something if these conditiosn aren't met?
        if face.det_score > MIN_DET_SCORE and face.embedding is not None:
            collected_embeddings.append(face.embedding)

            event_queue.put({
                "type": "collecting",
                "progress": len(collected_embeddings),
                "total": FRAMES_TO_COLLECT
            })

            if len(collected_embeddings) >= FRAMES_TO_COLLECT:
                avg_embedding = np.mean(collected_embeddings, axis=0)
                # TODO: switch this to handle matching logic where 2nd and 3rd parameters are
                # embeddings of our dataset and db_names are the names we should output
                # need to store them locally and extract name array
                matches = find_top_matches(avg_embedding, [], [], n=1)

                event_queue.put({
                    "type": "match_result",
                    "matches": matches
                })
                collected_embeddings = []

async def broadcast_event():
    while True:
        try:
            event = event_queue.get_nowait()
            if active_websocket:
                if isinstance(event, bytes):
                    await active_websocket.send_bytes(event)
                else:
                    await active_websocket.send_json(event)
        except queue.Empty:
            pass
        await asyncio.sleep(0.01)


#------------------------------------#
#-----------Legacy Functions---------#
#------------------------------------#

# Serve scientist images from the dataset
app.mount("/images", StaticFiles(directory="model/data/raw_images"), name="images")

# Serve media files (fonts, etc.)
app.mount("/media", StaticFiles(directory=f"{DIST_DIR}/media"), name="media")

@app.get("/")
async def root():
    return FileResponse(f"{DIST_DIR}/index.html")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Serve actual files (JS, CSS, etc.) if they exist
    file_path = os.path.join(DIST_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    # Otherwise serve index.html for SPA routing
    return FileResponse(f"{DIST_DIR}/index.html")