from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: int
    duration: int = Field(..., description="Duration in seconds, typically 4-8 seconds")
    narration: str = Field(..., description="Spoken voiceover text for this scene")
    visual_prompt: str = Field(..., description="Detailed image or video generation prompt")
    caption: str = Field(..., description="On-screen caption / subtitle text")

class Storyboard(BaseModel):
    title: str = Field(..., description="Punchy video title")
    hook: str = Field(..., description="Attention-grabbing opening hook")
    duration: int = Field(..., description="Total target duration in seconds (30-45s)")
    language: str = Field(default="English", description="Target language")
    script: str = Field(..., description="Full combined spoken script")
    keywords: List[str] = Field(default_factory=list, description="Topic hashtags and keywords")
    scenes: List[Scene] = Field(..., description="Sequential scenes (typically 5-6 scenes)")

class GenerateStoryboardRequest(BaseModel):
    topic: str
    style: Optional[str] = "Educational"
    language: Optional[str] = "English"
