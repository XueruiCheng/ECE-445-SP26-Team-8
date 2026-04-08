from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# Serve Angular build output
app.mount("/static", StaticFiles(directory="display/frontend/dist/frontend/browser"), name="static")

@app.get("/")
async def root():
    return FileResponse("display/frontend/dist/frontend/browser/index.html")

# SPA catch-all: serve index.html for any non-API, non-static route
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("display/frontend/dist/frontend/browser/index.html")
