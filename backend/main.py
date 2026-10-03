import os
import sys
import time
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure workspace root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.script.models import Storyboard, Scene, GenerateStoryboardRequest
from pipeline.script.storyboard_generator import generate_storyboard, GENERATED_SCRIPTS_DIR

load_dotenv()

app = FastAPI(
    title="Qoneqt AI Content Pipeline API",
    version="1.0.0",
    description="Backend API powering the Qoneqt AI Content Pipeline"
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateResponse(BaseModel):
    status: str
    topic: str
    style: Optional[str] = "Educational"
    language: Optional[str] = "English"
    storyboard: Optional[Storyboard] = None

class ApproveResponse(BaseModel):
    status: str
    storyboard: Storyboard
    message: str
    timestamp: int

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Qoneqt AI Pipeline"}

@app.post("/api/storyboard", response_model=Storyboard)
def create_storyboard(req: GenerateStoryboardRequest):
    """Phase 2: Generate strict structured Storyboard JSON for topic"""
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        storyboard = generate_storyboard(
            topic=req.topic.strip(),
            style=req.style or "Educational",
            language=req.language or "English"
        )
        return storyboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate storyboard: {str(e)}")

@app.get("/api/storyboard/latest", response_model=Optional[Storyboard])
def get_latest_storyboard():
    """Retrieve the most recently generated storyboard from cache"""
    latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
    if not latest_file.exists():
        return None
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            data = f.read()
        return Storyboard.model_validate_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read latest storyboard: {str(e)}")

@app.post("/api/storyboard/approve", response_model=ApproveResponse)
def approve_storyboard(storyboard: Storyboard):
    """
    Phase 3: Human Review & Approval
    Validates, locks, and stores user-reviewed storyboard prior to expensive media generation.
    """
    if not storyboard.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not storyboard.scenes:
        raise HTTPException(status_code=400, detail="Storyboard must contain at least one scene")
    
    timestamp = int(time.time())
    approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
    history_file = GENERATED_SCRIPTS_DIR / f"approved_storyboard_{timestamp}.json"
    
    json_data = storyboard.model_dump_json(indent=2)
    with open(approved_file, "w", encoding="utf-8") as f:
        f.write(json_data)
    with open(history_file, "w", encoding="utf-8") as f:
        f.write(json_data)
    
    return ApproveResponse(
        status="approved",
        storyboard=storyboard,
        message="Storyboard approved and locked for production pipeline.",
        timestamp=timestamp
    )

@app.get("/api/storyboard/approved", response_model=Optional[Storyboard])
def get_approved_storyboard():
    """Retrieve the active approved storyboard"""
    approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
    if not approved_file.exists():
        return None
    try:
        with open(approved_file, "r", encoding="utf-8") as f:
            data = f.read()
        return Storyboard.model_validate_json(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read approved storyboard: {str(e)}")

@app.post("/api/generate", response_model=GenerateResponse)
def generate_content(req: GenerateStoryboardRequest):
    """
    Main generate endpoint.
    """
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    storyboard = generate_storyboard(
        topic=req.topic.strip(),
        style=req.style or "Educational",
        language=req.language or "English"
    )

    return GenerateResponse(
        status="received",
        topic=req.topic.strip(),
        style=req.style,
        language=req.language,
        storyboard=storyboard
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
