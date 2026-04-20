from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from face_match import find_top_matches
from thumbs_up_detect import ThumbsUpDetector
from hand_detect import HandGameDetector

import os
import json
import time
import queue
import asyncio
import threading
from pathlib import Path
from contextlib import asynccontextmanager

import cv2
import numpy as np
import insightface

# --------------------------------------------------------------------------- #
# Config                                                                      #
# --------------------------------------------------------------------------- #
WARMUP_FRAMES = 60
MIN_DET_SCORE = 0.7
FRAMES_TO_COLLECT = 6
INFERENCE_EVERY_N_FRAMES = 3
LOGITECH_RASP_CAMERA_IDX = '/dev/video0'
LOCAL_CAMERA_IDX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Anchor all paths to the repo root (parent of display/) so the server can be
# launched from any working directory.
REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "display" / "frontend" / "dist" / "frontend" / "browser"
RAW_IMAGES_DIR = REPO_ROOT / "model" / "data" / "raw_images"

DB_DIR = REPO_ROOT / "model" / "data"
DB_EMBEDDINGS_PATH = DB_DIR / "embeddings.npy"
DB_NAMES_PATH = DB_DIR / "names.json"
DB_PROFILES_PATH = DB_DIR / "profiles.json"

# --------------------------------------------------------------------------- #
# Shared state                                                                #
# --------------------------------------------------------------------------- #
event_queue: queue.Queue = queue.Queue()
active_websocket: WebSocket | None = None

# Mutated only by the WebSocket handler (single writer); read by camera_loop.
current_state: str = "idle"

# Detectors are instantiated at lifespan startup. camera_loop is the only
# thread that ever calls process_frame() on these.
thumbs_detector: ThumbsUpDetector | None = None
hand_detector: HandGameDetector | None = None
face_collector = None  # type: FaceCollector | None


# --------------------------------------------------------------------------- #
# Face matching                                                               #
# --------------------------------------------------------------------------- #
class FaceCollector:
    """Collects FRAMES_TO_COLLECT face embeddings, averages them, and emits a
    match_result event with profile metadata enriched from profiles.json."""

    def __init__(self, db_embeddings: np.ndarray, db_names: list[str], profiles: dict):
        self.face_model = insightface.app.FaceAnalysis(name="buffalo_l")
        self.face_model.prepare(ctx_id=0, det_size=(320, 320))
        self.db_embeddings = db_embeddings
        self.db_names = db_names
        self.profiles = profiles
        self.collected: list[np.ndarray] = []
        self._frame_count = 0

    def reset(self):
        self.collected = []
        self._frame_count = 0

    def _enrich(self, name: str, score: float) -> dict:
        profile = self.profiles.get(name, {})
        return {
            "name": name,
            "similarity": float(score),
            "role": profile.get("role", ""),
            "position": profile.get("position", ""),
            "research_areas": profile.get("research_areas", []),
            "image_url": f"/images/{name}.jpg",
            "profile_url": profile.get("profile_url", ""),
        }

    def process_frame(self, frame) -> dict | None:
        self._frame_count += 1
        if self._frame_count % INFERENCE_EVERY_N_FRAMES != 0:
            return None

        faces = self.face_model.get(frame)

        if len(faces) != 1:
            return {
                "type": "face_error",
                "reason": "no_face" if len(faces) == 0 else "multiple_faces",
                "count": len(faces),
            }

        face = faces[0]
        if face.det_score <= MIN_DET_SCORE or face.embedding is None:
            return None

        self.collected.append(face.embedding)

        if len(self.collected) < FRAMES_TO_COLLECT:
            return {
                "type": "collecting",
                "progress": len(self.collected),
                "total": FRAMES_TO_COLLECT,
            }

        avg_embedding = np.mean(self.collected, axis=0)
        self.collected = []

        if len(self.db_embeddings) == 0:
            return {"type": "match_result", "matches": []}

        raw = find_top_matches(avg_embedding, self.db_embeddings, self.db_names, n=3)
        return {
            "type": "match_result",
            "matches": [self._enrich(name, score) for name, score in raw],
        }


def load_face_database() -> tuple[np.ndarray, list[str], dict]:
    if not (DB_EMBEDDINGS_PATH.exists() and DB_NAMES_PATH.exists()):
        print(f"WARN: face DB not found at {DB_DIR}; matching will return empty.")
        return np.zeros((0, 512), dtype=np.float32), [], {}

    embeddings = np.load(DB_EMBEDDINGS_PATH)
    with open(DB_NAMES_PATH, "r", encoding="utf-8") as f:
        names = json.load(f)

    profiles: dict = {}
    if DB_PROFILES_PATH.exists():
        with open(DB_PROFILES_PATH, "r", encoding="utf-8") as f:
            profiles = json.load(f)

    print(f"Loaded face DB: {len(names)} identities, {len(profiles)} profiles.")
    return embeddings, names, profiles


# --------------------------------------------------------------------------- #
# Camera loop                                                                 #
# --------------------------------------------------------------------------- #
def camera_loop():
    cap = cv2.VideoCapture(LOCAL_CAMERA_IDX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Mirror so on-screen movement matches the user's perspective.
        frame = cv2.flip(frame, 1)

        frame_count += 1
        if frame_count % 3 != 0:
            continue

        ts_ms = int(time.monotonic() * 1000)
        state = current_state

        # Run the detector for the current state. Detectors that draw overlays
        # (hand_detector) mutate `frame` in place so the overlay is baked into
        # the JPEG that gets streamed.
        if state == "idle" and thumbs_detector is not None:
            if thumbs_detector.process_frame(frame, ts_ms):
                event_queue.put({"type": "thumbs_up_detected"})
                thumbs_detector.reset()
        elif state == "startup" and hand_detector is not None:
            progress = hand_detector.process_frame(frame, ts_ms)
            event_queue.put({"type": "startup_progress", **progress})
            if progress["system_ready"]:
                event_queue.put({"type": "startup_complete"})
                hand_detector.reset()
        elif state == "camera" and face_collector is not None:
            event = face_collector.process_frame(frame)
            if event is not None:
                event_queue.put(event)
        # state == "output": no detector runs; camera just streams.

        ok, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
        if ok:
            event_queue.put(buffer.tobytes())


# --------------------------------------------------------------------------- #
# WebSocket broadcast                                                         #
# --------------------------------------------------------------------------- #
async def broadcast_event():
    while True:
        try:
            event = event_queue.get_nowait()
            if active_websocket is not None:
                if isinstance(event, bytes):
                    await active_websocket.send_bytes(event)
                else:
                    await active_websocket.send_json(event)
        except queue.Empty:
            pass
        except Exception as exc:
            # Don't kill the broadcast task on a stale websocket.
            print(f"broadcast_event: {exc}")
        await asyncio.sleep(0.01)


def _apply_state_change(new_state: str):
    """Reset the detector for the state we're entering, then update current_state.
    Reset before the swap so camera_loop never sees a stale detector."""
    global current_state
    if new_state == "idle" and thumbs_detector is not None:
        thumbs_detector.reset()
    elif new_state == "startup" and hand_detector is not None:
        hand_detector.reset()
    elif new_state == "camera" and face_collector is not None:
        face_collector.reset()
    current_state = new_state


# --------------------------------------------------------------------------- #
# FastAPI app                                                                 #
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    global thumbs_detector, hand_detector, face_collector
    db_embeddings, db_names, profiles = load_face_database()
    face_collector = FaceCollector(db_embeddings, db_names, profiles)
    thumbs_detector = ThumbsUpDetector()
    hand_detector = HandGameDetector()

    threading.Thread(target=camera_loop, daemon=True).start()
    asyncio.create_task(broadcast_event())
    yield


app = FastAPI(title="Quantum Mirror", lifespan=lifespan)
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


@app.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    global active_websocket
    await websocket.accept()
    active_websocket = websocket
    try:
        while True:
            msg = await websocket.receive_json()
            if not isinstance(msg, dict):
                continue
            if msg.get("type") == "state_change":
                new_state = msg.get("state")
                if new_state in ("idle", "startup", "camera", "output"):
                    _apply_state_change(new_state)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        print(f"websocket_camera: {exc}")
    finally:
        if active_websocket is websocket:
            active_websocket = None


# --------------------------------------------------------------------------- #
# Static assets / SPA                                                         #
# --------------------------------------------------------------------------- #
if RAW_IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(RAW_IMAGES_DIR)), name="images")
else:
    print(f"WARN: {RAW_IMAGES_DIR} not found; /images route disabled.")

_media_dir = DIST_DIR / "media"
if _media_dir.exists():
    app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")
else:
    print(f"WARN: {_media_dir} not found; /media route disabled (run `ng build` first).")


@app.get("/")
async def root():
    return FileResponse(str(DIST_DIR / "index.html"))


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = DIST_DIR / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))
    return FileResponse(str(DIST_DIR / "index.html"))
