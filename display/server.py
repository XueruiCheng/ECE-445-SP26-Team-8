from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import os
import queue

import cv2
import numpy as np
import insightface

# globals
WARMUP_FRAMES = 60
MIN_DET_SCORE = 0.7
FRAMES_TO_COLLECT = 6
INFERENCE_EVERY_N_FRAMES = 3

DIST_DIR = "display/frontend/dist/frontend/browser"

# list of events to send to our frontend
event_queue : queue.Queue = queue.Queue()
active_websocket = WebSocket | None = None


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

# maybe add unique identifier into 
@app.websocket("/ws/camera")
async def websocket_camera(websocket : WebSocket):
    global active_websocket
    await websocket.accept()
    active_websocket = websocket
    try:
        while True:
            data = await websocket.receive_bytes()
            if data:
                # do somethiing with the data from websocket
                continue
            # add to the queue
    except WebSocketDisconnect:
        active_websocket = None
        raise ConnectionError()

def camera_loop():
    cap = cv2.VideoCapture('/dev/video0')
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    face_model = insightface.app.FaceAnalysis(name="buffalo_l")
    face_model.prepare(ctx_id=0, det_size=(320, 320))

    collected_embeddings = []

    while True:
        ret, frame = cap.read()
        if not ret:
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

def find_top_matches(live_embedding, db_embeddings, db_names, n=3):
    """
    Find the top-N most similar faces in the database to the live embedding
    """
    live_norm = live_embedding / (np.linalg.norm(live_embedding) + 1e-10)
    db_norms = db_embeddings / (np.linalg.norm(db_embeddings, axis=1, keepdims=True) + 1e-10)

    scores = db_norms @ live_norm
    top_indices = np.argsort(scores)[::-1][:n]

    return [(db_names[i], float(scores[i])) for i in top_indices]