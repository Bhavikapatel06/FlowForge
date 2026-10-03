import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure workspace root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.script.models import Storyboard, Scene, GenerateStoryboardRequest
from pipeline.script.storyboard_generator import generate_storyboard, GENERATED_SCRIPTS_DIR
from pipeline.scenes.scene_generator import (
    generate_all_scenes,
    retry_single_scene,
    get_scenes_status,
    GENERATED_IMAGES_DIR,
)
from pipeline.voice.voice_generator import (
    generate_voice_narration,
    get_voice_status,
    GENERATED_AUDIO_DIR,
)
from pipeline.captions.caption_generator import (
    generate_captions,
    get_captions_status,
    GENERATED_CAPTIONS_DIR,
)
from pipeline.composer.video_composer import (
    compose_video,
    get_video_status,
    GENERATED_VIDEOS_DIR,
)
from pipeline.quality.quality_gate import (
    run_quality_gate,
    get_latest_quality_report,
)
from pipeline.publish.publisher import (
    publish_to_qoneqt,
    get_publish_receipt,
)

load_dotenv()

app = FastAPI(
    title="Qoneqt AI Content Pipeline API",
    version="1.0.0",
    description="Production-grade AI Video Pipeline powering Qoneqt Global Feed"
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount generated directory for direct static streaming (images, audio, video)
GENERATED_DIR = ROOT_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(GENERATED_DIR)), name="generated")

# Models
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

class VoiceRequest(BaseModel):
    script: Optional[str] = None
    language: Optional[str] = "English"
    voice: Optional[str] = None

class PublishRequest(BaseModel):
    channel: Optional[str] = "global-feed"

# ----------------- Phase 1: Foundation -----------------
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Qoneqt AI Pipeline", "phases": "1-10 ready"}

@app.post("/api/generate", response_model=GenerateResponse)
def generate_content(req: GenerateStoryboardRequest):
    """Phase 1 & 2: Generate topic storyboard"""
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

# ----------------- Phase 2: AI Storyboard -----------------
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

# ----------------- Phase 3: Human Review & Approval -----------------
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

# ----------------- Phase 4: Scene Generation -----------------
@app.post("/api/scenes/generate")
def create_scenes(provider: str = Query("auto", description="Image provider: auto, pollinations, canvas_synthetic")):
    """Phase 4: Generate visual assets for each approved scene"""
    try:
        results = generate_all_scenes(provider=provider)
        return {"status": "completed", "scenes": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scene generation failed: {str(e)}")

@app.post("/api/scenes/retry/{scene_id}")
def retry_scene(scene_id: int, provider: str = Query("auto")):
    """Phase 4: Retry generating a single scene without affecting others"""
    try:
        result = retry_single_scene(scene_id=scene_id, provider=provider)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retry Scene {scene_id}: {str(e)}")

@app.get("/api/scenes")
def list_scenes():
    """Phase 4: Get status of all generated scenes"""
    scenes = get_scenes_status()
    return {"scenes": scenes, "total": len(scenes)}

# ----------------- Phase 5: Voice Generation -----------------
@app.post("/api/voice/generate")
def create_voice(req: Optional[VoiceRequest] = None):
    """Phase 5: Generate narration audio file from script"""
    try:
        script = req.script if req else None
        language = req.language if req and req.language else "English"
        voice = req.voice if req else None
        res = generate_voice_narration(script=script, language=language, voice=voice)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")

@app.get("/api/voice")
def get_voice():
    """Phase 5: Get current voice status"""
    status = get_voice_status()
    if not status:
        raise HTTPException(status_code=404, detail="No voice audio generated yet")
    return status

# ----------------- Phase 6: Captions Generation -----------------
@app.post("/api/captions/generate")
def create_captions():
    """Phase 6: Generate SRT and VTT captions from storyboard"""
    try:
        res = generate_captions()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Caption generation failed: {str(e)}")

@app.get("/api/captions")
def get_captions():
    """Phase 6: Get current captions status and cue cards"""
    status = get_captions_status()
    if not status:
        raise HTTPException(status_code=404, detail="No captions generated yet")
    return status

# ----------------- Phase 7: Video Composition -----------------
@app.post("/api/compose")
def run_composition():
    """Phase 7: Compose 9:16 vertical video using FFmpeg"""
    try:
        res = compose_video()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video composition failed: {str(e)}")

@app.get("/api/compose/status")
def get_composition_status():
    """Phase 7: Get current composition video status"""
    status = get_video_status()
    if not status:
        raise HTTPException(status_code=404, detail="No video composed yet")
    return status

# ----------------- Phase 8: Quality Gate -----------------
@app.post("/api/quality/check")
@app.get("/api/quality/check")
def execute_quality_gate():
    """Phase 8: Automated pre-flight quality check"""
    try:
        report = run_quality_gate()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality gate error: {str(e)}")

@app.get("/api/quality/report")
def get_quality_report():
    """Phase 8: Get latest quality report"""
    report = get_latest_quality_report()
    if not report:
        raise HTTPException(status_code=404, detail="No quality report available")
    return report

# ----------------- Phase 9: Qoneqt Publishing -----------------
@app.post("/api/publish")
def publish_video(req: Optional[PublishRequest] = None):
    """
    Phase 9: Publish quality-verified video to Qoneqt Global Feed
    Enforces quality gate before allowing publication.
    """
    try:
        channel = req.channel if req and req.channel else "global-feed"
        receipt = publish_to_qoneqt(channel=channel)
        return receipt
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/publish/receipt")
def get_receipt():
    """Phase 9: Retrieve published receipt"""
    receipt = get_publish_receipt()
    if not receipt:
        raise HTTPException(status_code=404, detail="Video has not been published yet")
    return receipt

# ----------------- End-to-End Orchestrator -----------------
@app.post("/api/pipeline/run-all")
def run_full_pipeline(req: GenerateStoryboardRequest):
    """
    Convenience orchestrator: runs the complete pipeline end-to-end
    from topic to Qoneqt publish-ready video!
    """
    try:
        # Step 1: Storyboard
        sb = generate_storyboard(topic=req.topic, style=req.style or "Educational", language=req.language or "English")
        
        # Step 2: Auto-approve for automated flow
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        with open(approved_file, "w", encoding="utf-8") as f:
            f.write(sb.model_dump_json(indent=2))
            
        # Step 3: Scenes
        scenes_res = generate_all_scenes(storyboard=sb, provider="auto")
        
        # Step 4: Voice
        voice_res = generate_voice_narration(script=sb.script, language=sb.language)
        
        # Step 5: Captions
        captions_res = generate_captions(storyboard=sb)
        
        # Step 6: Compose Video
        video_res = compose_video(storyboard=sb)
        
        # Step 7: Quality Gate
        quality_res = run_quality_gate(storyboard=sb)
        
        return {
            "status": "success",
            "storyboard": sb,
            "scenes": scenes_res,
            "voice": voice_res,
            "captions": captions_res,
            "video": video_res,
            "quality_gate": quality_res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline run failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
