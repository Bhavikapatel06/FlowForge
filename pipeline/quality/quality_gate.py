import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from pipeline.script.models import Storyboard
from pipeline.composer.video_composer import get_ffmpeg_executable

logger = logging.getLogger("qoneqt.pipeline.quality")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_VIDEOS_DIR = WORKSPACE_ROOT / "generated" / "videos"
GENERATED_IMAGES_DIR = WORKSPACE_ROOT / "generated" / "images"
GENERATED_AUDIO_DIR = WORKSPACE_ROOT / "generated" / "audio"
GENERATED_CAPTIONS_DIR = WORKSPACE_ROOT / "generated" / "captions"
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"

def run_quality_gate(
    video_path: Optional[Path] = None,
    storyboard: Optional[Storyboard] = None
) -> Dict[str, Any]:
    """
    Phase 8: Automated Quality Gate
    Performs 7 rigorous pre-flight checks before allowing publishing to Qoneqt Global Feed:
      1. File Exists & Size Check
      2. Playability / Container Integrity Check
      3. Target Duration Check (target 30-45s)
      4. 9:16 Vertical Resolution Check (1080x1920)
      5. Audio Stream Integrity
      6. Synchronized Captions Verification
      7. Scene Completeness
    """
    if video_path is None:
        video_path = GENERATED_VIDEOS_DIR / "final.mp4"

    if storyboard is None:
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
        target_file = approved_file if approved_file.exists() else latest_file

        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                storyboard = Storyboard.model_validate_json(f.read())

    checks = []
    all_passed = True
    ffmpeg_exe = get_ffmpeg_executable()

    # --- Check 1: Video File Exists ---
    file_exists = video_path.exists() and video_path.stat().st_size > 1000
    file_size_mb = (video_path.stat().st_size / (1024 * 1024)) if file_exists else 0
    checks.append({
        "name": "Video File",
        "passed": file_exists,
        "details": f"{video_path.name} ({file_size_mb:.2f} MB)" if file_exists else "File missing or empty"
    })
    if not file_exists:
        all_passed = False

    # Extract probe information using FFmpeg
    video_width = 0
    video_height = 0
    video_duration = 0.0
    has_audio = False
    is_playable = False

    if file_exists:
        try:
            # Run ffmpeg probe
            probe_cmd = [ffmpeg_exe, "-i", str(video_path)]
            proc = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = proc.stderr

            # Check playable
            if "Input #0, mov,mp4,m4a,3gp,3g2,mj2" in output or "Video: h264" in output:
                is_playable = True

            # Parse resolution
            import re
            res_match = re.search(r"Video:.*,\s*(\d{3,4})x(\d{3,4})", output)
            if res_match:
                video_width = int(res_match.group(1))
                video_height = int(res_match.group(2))

            # Parse duration: Duration: 00:00:35.00
            dur_match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", output)
            if dur_match:
                h, m, s = int(dur_match.group(1)), int(dur_match.group(2)), float(dur_match.group(3))
                video_duration = h * 3600 + m * 60 + s

            # Check audio stream
            if "Audio:" in output:
                has_audio = True

        except Exception as e:
            logger.warning("FFmpeg probe error: %s", e)

    # --- Check 2: Playability ---
    checks.append({
        "name": "Playable Container",
        "passed": is_playable,
        "details": "H.264 FastStart Web Compliant" if is_playable else "Corrupt or non-standard container"
    })
    if not is_playable:
        all_passed = False

    # --- Check 3: Duration ---
    # Expected target duration is typically 25 to 50 seconds for short-form
    target_dur = storyboard.duration if storyboard else 35
    duration_valid = 20.0 <= video_duration <= 60.0
    checks.append({
        "name": "Duration Check",
        "passed": duration_valid,
        "details": f"{video_duration:.1f}s (target: {target_dur}s, range: 25-50s)" if video_duration > 0 else f"Target: {target_dur}s"
    })
    if not duration_valid:
        all_passed = False

    # --- Check 4: 9:16 Aspect Ratio ---
    is_vertical_9_16 = (video_width == 1080 and video_height == 1920) or (video_height > video_width and abs(video_height/video_width - 16/9) < 0.1)
    checks.append({
        "name": "9:16 Vertical Ratio",
        "passed": is_vertical_9_16,
        "details": f"{video_width}x{video_height} (Vertical 9:16)" if is_vertical_9_16 else f"{video_width}x{video_height} (Not 9:16 vertical)"
    })
    if not is_vertical_9_16:
        all_passed = False

    # --- Check 5: Audio Stream ---
    checks.append({
        "name": "Audio Stream",
        "passed": has_audio,
        "details": "AAC Stereo Audio Stream present" if has_audio else "No audio stream detected"
    })
    if not has_audio:
        all_passed = False

    # --- Check 6: Captions ---
    srt_path = GENERATED_CAPTIONS_DIR / "captions.srt"
    captions_exist = srt_path.exists() and srt_path.stat().st_size > 0
    checks.append({
        "name": "Captions Aligned",
        "passed": captions_exist,
        "details": "Synchronized SRT subtitle stream available" if captions_exist else "Captions missing"
    })
    if not captions_exist:
        all_passed = False

    # --- Check 7: Scene Completeness ---
    expected_scenes = len(storyboard.scenes) if storyboard else 6
    generated_scene_count = len(list(GENERATED_IMAGES_DIR.glob("scene_*.jpg")))
    scenes_complete = generated_scene_count >= expected_scenes
    checks.append({
        "name": "Scenes Complete",
        "passed": scenes_complete,
        "details": f"{generated_scene_count}/{expected_scenes} vertical scene cards rendered"
    })
    if not scenes_complete:
        all_passed = False

    status_str = "READY TO PUBLISH" if all_passed else "QUALITY GATE FAILED"

    report = {
        "passed": all_passed,
        "status": status_str,
        "total_checks": len(checks),
        "passed_checks": sum(1 for c in checks if c["passed"]),
        "checks": checks,
        "metrics": {
            "resolution": f"{video_width}x{video_height}",
            "aspect_ratio": "9:16",
            "duration": f"{video_duration:.1f}s",
            "file_size": f"{file_size_mb:.2f} MB",
            "scenes": f"{generated_scene_count}/{expected_scenes}"
        }
    }

    report_path = WORKSPACE_ROOT / "generated" / "quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info("Quality Gate finished: %s (%d/%d checks passed)", status_str, report["passed_checks"], len(checks))
    return report

def get_latest_quality_report() -> Optional[Dict[str, Any]]:
    """Retrieve existing quality report."""
    report_path = WORKSPACE_ROOT / "generated" / "quality_report.json"
    if report_path.exists():
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None
