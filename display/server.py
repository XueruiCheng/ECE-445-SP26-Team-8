from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Quantum Mirror")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="display/frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("display/frontend/index.html")