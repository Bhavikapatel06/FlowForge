import os
import json
import re
import time
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from pipeline.script.models import Storyboard, Scene

load_dotenv()
logger = logging.getLogger("qoneqt.pipeline.script")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"
GENERATED_SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_TEMPLATE = """You are an elite short-form video producer and viral storyteller specializing in vertical video (9:16 format for Reels, Shorts, and the Qoneqt Global Feed).

Generate a captivating, tightly-paced vertical video storyboard for the following topic:
Topic: {topic}
Content Style: {style}
Language: {language}

STRICT INSTRUCTIONS:
1. Target duration: 30 to 45 seconds total.
2. Structure: 5 to 6 scenes.
3. Hook: A punchy, scroll-stopping opening hook (under 3 seconds).
4. Narration: Clear, concise voiceover for each scene matching its individual duration (approx 2.5 words per second).
5. Visual Prompts: Detailed, vivid, cinematic visual descriptions formatted for 9:16 vertical ratio. Avoid text on the image.
6. Captions: Engaging on-screen caption text for each scene.
7. Keywords: 4-6 trending, relevant hashtags or keywords.

Return ONLY a valid JSON object matching this exact schema:
{{
  "title": "Clear and punchy title",
  "hook": "Attention-grabbing opening line",
  "duration": 35,
  "language": "{language}",
  "script": "Full concatenated narration text from scene 1 through scene N",
  "keywords": ["tag1", "tag2", "tag3", "tag4"],
  "scenes": [
    {{
      "id": 1,
      "duration": 5,
      "narration": "Voiceover line for scene 1",
      "visual_prompt": "Cinematic 9:16 vertical view, photorealistic, dramatic lighting...",
      "caption": "Punchy subtitle for scene 1"
    }}
  ]
}}
"""

def _clean_json_response(raw_text: str) -> str:
    """Strip markdown code fence backticks and whitespace."""
    raw = raw_text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()

def _generate_fallback_storyboard(topic: str, style: str, language: str) -> Storyboard:
    """
    Intelligent fallback generator ensuring 100% pipeline reliability
    even when API keys or network calls are unavailable during hackathons.
    """
    clean_topic = topic.strip()
    return Storyboard(
        title=f"The Truth About {clean_topic}",
        hook=f"{clean_topic} isn't what you think. Here is how it's changing everything.",
        duration=35,
        language=language,
        script=(
            f"{clean_topic} isn't what you think. Here is how it's changing everything. "
            f"Every single day, breakthroughs in {clean_topic} are redefining our daily routines. "
            f"The real power lies in how accessible and intelligent the tools have become. "
            f"From automated workflows to instant personal insights, the barrier to entry has vanished. "
            f"Those who master {clean_topic} right now will lead the next decade. "
            f"Are you ready for the next shift? Follow for more future insights."
        ),
        keywords=[clean_topic.lower().replace(" ", ""), "innovation", "future", "tech", "productivity"],
        scenes=[
            Scene(
                id=1,
                duration=5,
                narration=f"{clean_topic} isn't what you think. Here is how it's changing everything.",
                visual_prompt=f"A cinematic 9:16 vertical close-up of a modern person reacting with awe to a glowing holographic interface depicting {clean_topic}, moody cyberpunk neon lighting, photorealistic, 8k resolution, vertical composition.",
                caption=f"What you didn't know about {clean_topic}."
            ),
            Scene(
                id=2,
                duration=6,
                narration=f"Every single day, breakthroughs in {clean_topic} are redefining our daily routines.",
                visual_prompt=f"Vertical 9:16 view of a bustling futuristic workspace, dynamic camera angle, warm volumetric sunlight, clean minimalist aesthetic representing {clean_topic}, cinematic depth of field.",
                caption=f"Daily routines are transforming right now."
            ),
            Scene(
                id=3,
                duration=6,
                narration="The real power lies in how accessible and intelligent the tools have become.",
                visual_prompt="Close-up macro shot of sleek digital devices glowing with neural network data streams in 9:16 vertical format, soft pastel purple and indigo studio lighting, ultra-detailed.",
                caption="Intelligent tools are now at your fingertips."
            ),
            Scene(
                id=4,
                duration=6,
                narration="From automated workflows to instant personal insights, the barrier to entry has vanished.",
                visual_prompt="Vertical high-angle perspective of an inspired creator smiling while intuitive AI interfaces effortlessly organize high-dimensional data, clean aesthetics, 9:16 aspect ratio.",
                caption="Instant insights. Zero friction."
            ),
            Scene(
                id=5,
                duration=6,
                narration=f"Those who master {clean_topic} right now will lead the next decade.",
                visual_prompt=f"Epic vertical 9:16 portrait of a confident innovator standing on a sunlit city observation deck overlooking a thriving skyline, golden hour illumination, cinematic composition.",
                caption="Early adopters will lead the next decade."
            ),
            Scene(
                id=6,
                duration=6,
                narration="Are you ready for the next shift? Follow for more future insights.",
                visual_prompt="Sleek, glowing futuristic emblem pulsating with energy in vertical 9:16 frame, dark carbon fiber background, vibrant neon accents, ultra-crisp.",
                caption="Are you ready for the future?"
            )
        ]
    )

def generate_storyboard(topic: str, style: str = "Educational", language: str = "English") -> Storyboard:
    """
    Main entry point for Phase 2 AI Storyboard Engine.
    Uses Gemini LLM if GEMINI_API_KEY is configured, with robust JSON validation
    and an automatic reliable fallback.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    storyboard: Optional[Storyboard] = None

    if api_key and api_key != "YOUR_GEMINI_API_KEY":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Select model
            model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "response_mime_type": "application/json",
                }
            )

            prompt = PROMPT_TEMPLATE.format(topic=topic, style=style, language=language)
            logger.info("Calling Gemini API for topic: '%s'...", topic)
            response = model.generate_content(prompt)

            cleaned_json = _clean_json_response(response.text)
            parsed_dict = json.loads(cleaned_json)
            
            # Validate with Pydantic
            storyboard = Storyboard.model_validate(parsed_dict)
            logger.info("Successfully generated and validated storyboard via Gemini for '%s'", topic)

        except Exception as err:
            logger.warning("Gemini generation failed or returned invalid JSON (%s). Falling back to reliable structured generator.", err)
            storyboard = None

    if storyboard is None:
        logger.info("Using built-in structured generator for topic: '%s'", topic)
        storyboard = _generate_fallback_storyboard(topic, style, language)

    # Save to generated/scripts
    timestamp = int(time.time())
    safe_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", topic.lower())[:30]
    out_file = GENERATED_SCRIPTS_DIR / f"storyboard_{safe_slug}_{timestamp}.json"
    latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"

    json_data = storyboard.model_dump_json(indent=2)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(json_data)
    with open(latest_file, "w", encoding="utf-8") as f:
        f.write(json_data)

    logger.info("Saved storyboard to %s and %s", out_file.name, latest_file.name)
    return storyboard
