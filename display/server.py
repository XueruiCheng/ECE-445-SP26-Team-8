from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

DIST_DIR = "display/frontend/dist/frontend/browser"

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
