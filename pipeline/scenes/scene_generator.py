import os
import json
import time
import math
import random
import urllib.parse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from pipeline.script.models import Storyboard, Scene

logger = logging.getLogger("qoneqt.pipeline.scenes")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_IMAGES_DIR = WORKSPACE_ROOT / "generated" / "images"
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"
GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Curated high-resolution photorealistic 9:16 vertical images
CURATED_PHOTO_IDS = [
    "photo-1516321318423-f06f85e504b3", # AI student digital learning
    "photo-1522202176988-66273c2fd55f", # Modern students collaborative studying
    "photo-1531482615713-2afd69097998", # High-tech education & teamwork
    "photo-1581091226825-a6a2a5aee158", # Futuristic AI & robotics interface
    "photo-1526374965328-7f61d4dc18c5", # Digital cyber code & data streams
    "photo-1451187580459-43490279c0fa", # Global connected neural networks
    "photo-1485827404703-89b55fcc595e", # Futuristic autonomous AI
    "photo-1519389950473-47ba0277781c", # Inspired digital productivity
]

# Color palettes for synthetic high-fidelity 9:16 vertical scenes
SCENE_PALETTES = [
    ((10, 15, 30), (99, 102, 241), (168, 85, 247)),    # Deep Slate to Indigo to Purple
    ((12, 18, 35), (14, 165, 233), (59, 130, 246)),    # Deep Navy to Cyan to Blue
    ((18, 12, 26), (236, 72, 153), (244, 63, 94)),     # Deep Plum to Pink to Rose
    ((8, 20, 28), (16, 185, 129), (6, 182, 212)),      # Deep Emerald to Teal to Cyan
    ((22, 14, 14), (245, 158, 11), (239, 68, 68)),     # Deep Carbon to Amber to Flame
    ((14, 10, 28), (139, 92, 246), (192, 132, 252)),   # Midnight Violet to Amethyst
]

def _generate_synthetic_visual(scene: Scene, output_path: Path) -> Path:
    """
    High-aesthetic, cinematic PIL visual generator.
    Produces clean, stunning, broadcast-grade vertical visuals:
      - Smooth atmospheric gradients & volumetric lighting
      - Glowing 3D concentric holographic nodes and orbital rings
      - Particle constellation network
      - Sleek unobtrusive top header badge
      - ZERO ugly debug/wireframe boxes!
    """
    width, height = 1080, 1920
    palette_idx = (scene.id - 1) % len(SCENE_PALETTES)
    bg_dark, primary_color, accent_color = SCENE_PALETTES[palette_idx]

    img = Image.new("RGB", (width, height), bg_dark)
    draw = ImageDraw.Draw(img)

    # 1. Atmospheric Vertical Gradient
    for y in range(height):
        ratio = y / height
        # Smooth organic gradient
        curve = math.sin(ratio * math.pi * 0.5)
        r = int(bg_dark[0] * (1 - curve) + accent_color[0] * (curve * 0.65))
        g = int(bg_dark[1] * (1 - curve) + accent_color[1] * (curve * 0.65))
        b = int(bg_dark[2] * (1 - curve) + accent_color[2] * (curve * 0.65))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Glowing Concentric 3D Focal Ring Centerpiece
    center_x, center_y = width // 2, 850
    for radius in range(420, 40, -35):
        alpha_ratio = (420 - radius) / 380.0
        glow_r = int(primary_color[0] * alpha_ratio + bg_dark[0] * (1 - alpha_ratio))
        glow_g = int(primary_color[1] * alpha_ratio + bg_dark[1] * (1 - alpha_ratio))
        glow_b = int(primary_color[2] * alpha_ratio + bg_dark[2] * (1 - alpha_ratio))
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=(glow_r, glow_g, glow_b),
            width=2 if radius > 200 else 4
        )

    # 3. Dynamic Orbital Rings (3D tilted perspective)
    for angle_offset in [0, 45, 90, 135]:
        rad = math.radians(angle_offset + scene.id * 30)
        rx = int(280 * math.cos(rad))
        ry = int(140 * math.sin(rad))
        draw.ellipse(
            [center_x - 300 + rx, center_y - 180 + ry, center_x + 300 + rx, center_y + 180 + ry],
            outline=(primary_color[0], primary_color[1], primary_color[2]),
            width=2
        )

    # 4. Constellation Nodes & Connecting Neural Lines
    random.seed(scene.id * 42)
    node_points = []
    for _ in range(18):
        nx = random.randint(120, width - 120)
        ny = random.randint(300, 1400)
        node_points.append((nx, ny))

    for i in range(len(node_points)):
        for j in range(i + 1, min(i + 4, len(node_points))):
            p1 = node_points[i]
            p2 = node_points[j]
            dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
            if dist < 400:
                line_alpha = max(20, int(255 * (1 - dist / 400.0) * 0.4))
                draw.line([p1, p2], fill=(primary_color[0], primary_color[1], primary_color[2]), width=1)

    for nx, ny in node_points:
        draw.ellipse([nx - 5, ny - 5, nx + 5, ny + 5], fill=accent_color)
        draw.ellipse([nx - 2, ny - 2, nx + 2, ny + 2], fill=(255, 255, 255))

    # 5. Core Holographic Energy Sphere
    core_rad = 110
    draw.ellipse(
        [center_x - core_rad, center_y - core_rad, center_x + core_rad, center_y + core_rad],
        fill=(bg_dark[0] + 15, bg_dark[1] + 20, bg_dark[2] + 40),
        outline=accent_color,
        width=3
    )
    # Inner energy pulse
    draw.ellipse(
        [center_x - 45, center_y - 45, center_x + 45, center_y + 45],
        fill=(255, 255, 255),
        outline=primary_color,
        width=2
    )

    # 6. Sleek Top Status Pill (Broadcast Branding)
    badge_w, badge_h = 320, 52
    bx1, by1 = (width - badge_w) // 2, 100
    draw.rounded_rectangle([bx1, by1, bx1 + badge_w, by1 + badge_h], radius=26, fill=(15, 20, 35), outline=primary_color, width=2)
    draw.text((bx1 + 35, by1 + 16), f"QONEQT  •  SCENE {scene.id:02d}", fill=(255, 255, 255))

    # 7. Subtle Vignette Edge Shadows
    for i in range(50):
        alpha = int((50 - i) * 1.5)
        draw.rectangle([i, i, width - i, height - i], outline=(0, 0, 0), width=1)

    img.save(output_path, "JPEG", quality=95)
    return output_path

def _fetch_curated_stock_photo(scene: Scene, output_path: Path) -> bool:
    """
    Downloads high-resolution photorealistic 1080x1920 vertical photography
    from verified fast CDN collections.
    """
    photo_idx = (scene.id - 1) % len(CURATED_PHOTO_IDS)
    photo_id = CURATED_PHOTO_IDS[photo_idx]
    url = f"https://images.unsplash.com/{photo_id}?w=1080&h=1920&fit=crop&q=85"

    try:
        logger.info("Fetching photorealistic vertical asset for Scene %d (%s)...", scene.id, photo_id)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200 and len(res.content) > 20000:
                with open(output_path, "wb") as f:
                    f.write(res.content)

                # Ensure exact 1080x1920
                with Image.open(output_path) as img:
                    if img.size != (1080, 1920):
                        resized = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                        resized.save(output_path, "JPEG", quality=95)

                logger.info("Successfully saved curated photorealistic image for Scene %d (%d bytes)", scene.id, len(res.content))
                return True
    except Exception as e:
        logger.warning("Photo fetch failed for Scene %d: %s", scene.id, e)
    return False

def generate_scene_visual(scene: Scene, output_path: Optional[Path] = None, provider: str = "auto") -> Dict[str, Any]:
    """
    Modular abstraction for Phase 4: generate_scene_visual(scene)
    Reliability sequence:
      1. High-resolution photorealistic 1080x1920 vertical photography (Unsplash verified CDN)
      2. High-aesthetic atmospheric PIL vertical generator (Zero network dependency fallback)
    Guarantees clean, broadcast-grade visuals with ZERO ugly debug boxes!
    """
    if output_path is None:
        output_path = GENERATED_IMAGES_DIR / f"scene_{scene.id}.jpg"

    provider_used = "curated_photo"
    success = False
    error_msg = None

    if provider in ["auto", "curated", "photo"]:
        success = _fetch_curated_stock_photo(scene, output_path)

    # Fallback to sleek atmospheric PIL visual
    if not success:
        logger.info("Rendering cinematic atmospheric visual for Scene %d...", scene.id)
        _generate_synthetic_visual(scene, output_path)
        provider_used = "cinematic_canvas"
        success = True

    return {
        "scene_id": scene.id,
        "status": "completed",
        "provider": provider_used,
        "path": str(output_path),
        "filename": output_path.name,
        "file_size": output_path.stat().st_size if output_path.exists() else 0,
        "duration": scene.duration,
        "caption": scene.caption,
        "visual_prompt": scene.visual_prompt,
        "error": error_msg
    }

def generate_all_scenes(storyboard: Optional[Storyboard] = None, provider: str = "auto") -> List[Dict[str, Any]]:
    """
    Generate all scenes from storyboard.
    Preserves existing scene images and isolates failures.
    """
    if storyboard is None:
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
        target_file = approved_file if approved_file.exists() else latest_file

        if not target_file.exists():
            raise FileNotFoundError("No storyboard available to generate scenes.")

        with open(target_file, "r", encoding="utf-8") as f:
            storyboard = Storyboard.model_validate_json(f.read())

    results = []
    logger.info("Starting visual generation for %d scenes...", len(storyboard.scenes))
    for scene in storyboard.scenes:
        res = generate_scene_visual(scene, provider=provider)
        results.append(res)

    manifest_path = GENERATED_IMAGES_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

def retry_single_scene(scene_id: int, provider: str = "auto") -> Dict[str, Any]:
    """
    Independent retry for a single scene without touching other scenes.
    """
    approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
    latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
    target_file = approved_file if approved_file.exists() else latest_file

    if not target_file.exists():
        raise FileNotFoundError("No storyboard available to retry scene.")

    with open(target_file, "r", encoding="utf-8") as f:
        storyboard = Storyboard.model_validate_json(f.read())

    target_scene = next((s for s in storyboard.scenes if s.id == scene_id), None)
    if not target_scene:
        raise ValueError(f"Scene with id {scene_id} not found in storyboard.")

    out_file = GENERATED_IMAGES_DIR / f"scene_{scene_id}.jpg"
    result = generate_scene_visual(target_scene, output_path=out_file, provider=provider)

    manifest_path = GENERATED_IMAGES_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            updated = False
            for i, item in enumerate(manifest):
                if item.get("scene_id") == scene_id:
                    manifest[i] = result
                    updated = True
                    break
            if not updated:
                manifest.append(result)
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            logger.warning("Could not update manifest: %s", e)

    return result

def get_scenes_status() -> List[Dict[str, Any]]:
    """Return status and preview paths of all generated scene images."""
    manifest_path = GENERATED_IMAGES_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    items = []
    for img_path in sorted(GENERATED_IMAGES_DIR.glob("scene_*.jpg")):
        try:
            sid = int(img_path.stem.split("_")[1])
            items.append({
                "scene_id": sid,
                "status": "completed",
                "filename": img_path.name,
                "path": str(img_path),
                "file_size": img_path.stat().st_size
            })
        except Exception:
            continue
    return items
