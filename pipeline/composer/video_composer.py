import os
import sys
import re
import json
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from pipeline.script.models import Storyboard

logger = logging.getLogger("qoneqt.pipeline.composer")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_VIDEOS_DIR = WORKSPACE_ROOT / "generated" / "videos"
GENERATED_IMAGES_DIR = WORKSPACE_ROOT / "generated" / "images"
GENERATED_AUDIO_DIR = WORKSPACE_ROOT / "generated" / "audio"
GENERATED_CAPTIONS_DIR = WORKSPACE_ROOT / "generated" / "captions"
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"

GENERATED_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

def get_ffmpeg_executable() -> str:
    """Find available FFmpeg executable path."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).exists():
            return str(exe)
    except Exception:
        pass

    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg

    raise RuntimeError("FFmpeg executable not found. Please install imageio-ffmpeg or ffmpeg.")

def probe_duration(file_path: Path, ffmpeg_exe: str) -> float:
    """Return media duration in seconds via FFmpeg probe."""
    try:
        cmd = [ffmpeg_exe, "-i", str(file_path)]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        m = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", proc.stderr)
        if m:
            h, m_val, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + m_val * 60 + s
    except Exception as e:
        logger.warning("Could not probe duration for %s: %s", file_path, e)
    return 0.0

def compose_video(
    storyboard: Optional[Storyboard] = None,
    output_filename: str = "final.mp4",
    burn_subtitles: bool = True
) -> Dict[str, Any]:
    """
    Phase 7: Video Composition via FFmpeg
    Combines:
      - 9:16 vertical scene images (1080x1920)
      - Scene durations dynamically matched to narration voiceover length
      - Narration voiceover audio (with apad safety)
      - Burned-in + synchronized captions
    Outputs browser-playable 1080x1920 vertical MP4.
    """
    ffmpeg_exe = get_ffmpeg_executable()
    logger.info("Using FFmpeg binary: %s", ffmpeg_exe)

    # 1. Resolve Storyboard
    if storyboard is None:
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
        target_file = approved_file if approved_file.exists() else latest_file

        if not target_file.exists():
            raise FileNotFoundError("No storyboard available for composition.")

        with open(target_file, "r", encoding="utf-8") as f:
            storyboard = Storyboard.model_validate_json(f.read())

    # 2. Collect Scene Images
    scene_items = []
    for scene in storyboard.scenes:
        img_path = GENERATED_IMAGES_DIR / f"scene_{scene.id}.jpg"
        if not img_path.exists():
            raise FileNotFoundError(f"Missing image for Scene {scene.id}: {img_path}")
        scene_items.append({
            "id": scene.id,
            "duration": float(scene.duration),
            "path": img_path
        })

    # 3. Audio Narration
    audio_path = GENERATED_AUDIO_DIR / "narration.mp3"
    if not audio_path.exists():
        wav_path = GENERATED_AUDIO_DIR / "narration.wav"
        if wav_path.exists():
            audio_path = wav_path
        else:
            raise FileNotFoundError(f"Missing narration audio: {audio_path}")

    # Measure exact audio duration
    audio_dur = probe_duration(audio_path, ffmpeg_exe)
    planned_total = sum(item["duration"] for item in scene_items)

    # Distribute scene timing so video and voice narration match 1:1
    if audio_dur > 5.0 and planned_total > 0:
        ratio = audio_dur / planned_total
        for item in scene_items:
            item["actual_duration"] = round(item["duration"] * ratio, 3)
        target_video_duration = audio_dur
    else:
        for item in scene_items:
            item["actual_duration"] = item["duration"]
        target_video_duration = planned_total

    # 4. Captions
    srt_path = GENERATED_CAPTIONS_DIR / "captions.srt"
    has_captions = srt_path.exists()

    output_path = GENERATED_VIDEOS_DIR / output_filename
    temp_concat_file = GENERATED_VIDEOS_DIR / "concat_scenes.txt"

    concat_lines = []
    for item in scene_items:
        clean_path = str(item["path"]).replace("\\", "/")
        concat_lines.append(f"file '{clean_path}'")
        concat_lines.append(f"duration {item['actual_duration']}")

    # Repeat last image per FFmpeg concat requirement
    last_clean_path = str(scene_items[-1]["path"]).replace("\\", "/")
    concat_lines.append(f"file '{last_clean_path}'")

    with open(temp_concat_file, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_lines))

    # Base filters for strict 1080x1920 vertical canvas
    vf_filters = [
        "scale=1080:1920:force_original_aspect_ratio=decrease",
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "fps=30",
        "format=yuv420p"
    ]

    # Try burning in captions if requested and available
    relative_ass = "generated/captions/captions.ass"
    relative_srt = "generated/captions/captions.srt"
    burn_in_success = False
    if burn_subtitles and (Path(relative_ass).exists() or Path(relative_srt).exists()):
        vf_with_subs = list(vf_filters)
        if Path(relative_ass).exists():
            # captions.ass has strict 1080x1920 resolution, lower-third alignment & yellow highlight styles
            vf_with_subs.append(f"subtitles={relative_ass}")
        else:
            # Fallback to SRT with explicit 1080x1920 coordinate bounds
            vf_with_subs.append(
                f"subtitles={relative_srt}:force_style='PlayResX=1080,PlayResY=1920,FontSize=48,Bold=1,PrimaryColour=&H0000E5FF,OutlineColour=&H00000000,BorderStyle=1,Outline=4,Alignment=2,MarginV=220'"
            )
        cmd_try = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(temp_concat_file),
            "-i", str(audio_path),
            "-t", f"{target_video_duration:.3f}",
            "-vf", ",".join(vf_with_subs),
            "-af", f"apad=whole_dur={target_video_duration:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-profile:v", "high", "-level:v", "4.1",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart",
            str(output_path)
        ]
        logger.info("Composing video with cleanly styled lower-third subtitles...")
        start_time = time.time()
        p = subprocess.run(cmd_try, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if p.returncode == 0:
            burn_in_success = True
            elapsed = time.time() - start_time
            logger.info("Composed video with lower-third captions in %.2fs", elapsed)


    if not burn_in_success:
        cmd_clean = [
            ffmpeg_exe, "-y",
            "-f", "concat", "-safe", "0", "-i", str(temp_concat_file),
            "-i", str(audio_path),
            "-t", f"{target_video_duration:.3f}",
            "-vf", ",".join(vf_filters),
            "-af", f"apad=whole_dur={target_video_duration:.3f}",
            "-c:v", "libx264", "-preset", "fast", "-profile:v", "high", "-level:v", "4.1",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
            "-movflags", "+faststart",
            str(output_path)
        ]
        logger.info("Executing FFmpeg composition without subtitle filter...")
        start_time = time.time()
        proc = subprocess.run(cmd_clean, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elapsed = time.time() - start_time
        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stderr)
            raise RuntimeError(f"FFmpeg composition failed: {proc.stderr[-500:]}")
        logger.info("FFmpeg composition finished in %.2fs. Created %s", elapsed, output_path.name)

    temp_concat_file.unlink(missing_ok=True)
    file_size = output_path.stat().st_size if output_path.exists() else 0

    manifest = {
        "status": "completed",
        "filename": output_path.name,
        "path": str(output_path),
        "file_size": file_size,
        "resolution": "1080x1920",
        "aspect_ratio": "9:16",
        "target_duration": round(target_video_duration, 2),
        "actual_audio_duration": round(audio_dur, 2),
        "scenes_count": len(scene_items),
        "audio_track": audio_path.name,
        "has_captions": has_captions,
        "burned_subtitles": burn_in_success,
        "render_time_sec": round(elapsed, 2),
        "timestamp": int(time.time())
    }

    manifest_path = GENERATED_VIDEOS_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest

def get_video_status() -> Optional[Dict[str, Any]]:
    """Return status and metadata of the composed video."""
    manifest_path = GENERATED_VIDEOS_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    final_mp4 = GENERATED_VIDEOS_DIR / "final.mp4"
    if final_mp4.exists():
        return {
            "status": "completed",
            "filename": final_mp4.name,
            "path": str(final_mp4),
            "file_size": final_mp4.stat().st_size,
            "resolution": "1080x1920",
            "aspect_ratio": "9:16"
        }
    return None
