import os
import json
import re
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import timedelta

from pipeline.script.models import Storyboard, Scene

logger = logging.getLogger("qoneqt.pipeline.captions")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_CAPTIONS_DIR = WORKSPACE_ROOT / "generated" / "captions"
GENERATED_AUDIO_DIR = WORKSPACE_ROOT / "generated" / "audio"
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"
GENERATED_CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)

def _format_srt_timestamp(seconds: float) -> str:
    """Convert float seconds to SRT timestamp HH:MM:SS,mmm"""
    td = timedelta(seconds=max(0.0, seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def _format_vtt_timestamp(seconds: float) -> str:
    """Convert float seconds to WebVTT timestamp HH:MM:SS.mmm"""
    td = timedelta(seconds=max(0.0, seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def _format_ass_timestamp(seconds: float) -> str:
    """Convert float seconds to ASS timestamp H:MM:SS.cc"""
    td = timedelta(seconds=max(0.0, seconds))
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    centis = int((seconds - int(seconds)) * 100)
    return f"{hours:01d}:{minutes:02d}:{secs:02d}.{centis:02d}"

def _get_audio_duration() -> float:
    """Probe narration audio duration if available."""
    audio_path = GENERATED_AUDIO_DIR / "narration.mp3"
    if not audio_path.exists():
        audio_path = GENERATED_AUDIO_DIR / "narration.wav"
    if not audio_path.exists():
        return 0.0

    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [exe, "-i", str(audio_path)]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        m = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", proc.stderr)
        if m:
            h, m_val, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + m_val * 60 + s
    except Exception:
        pass
    return 0.0

def generate_captions(storyboard: Optional[Storyboard] = None) -> Dict[str, Any]:
    """
    Phase 6: Direct SRT generation using scene durations and captions.
    Produces:
      - generated/captions/captions.srt (standard SubRip)
      - generated/captions/captions.vtt (HTML5 web video track)
      - generated/captions/captions.ass (Reels-style styled subtitles)
    """
    if storyboard is None:
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
        target_file = approved_file if approved_file.exists() else latest_file

        if not target_file.exists():
            raise FileNotFoundError("No storyboard available to generate captions.")

        with open(target_file, "r", encoding="utf-8") as f:
            storyboard = Storyboard.model_validate_json(f.read())

    # Check for actual audio duration to ensure perfect voice-to-caption synchronization
    audio_duration = _get_audio_duration()
    planned_duration = sum(s.duration for s in storyboard.scenes)
    scale_ratio = (audio_duration / planned_duration) if (audio_duration > 5.0 and planned_duration > 0) else 1.0

    srt_lines = []
    vtt_lines = ["WEBVTT", ""]
    cues_data = []

    # ASS header for ultra-clean vertical mobile captions
    ass_header = """[Script Info]
Title: Qoneqt Dynamic Vertical Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,54,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,80,80,260,1
Style: Highlight,Arial,58,&H0000E5FF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,3,2,80,80,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_events = []

    current_time = 0.0
    for idx, scene in enumerate(storyboard.scenes, start=1):
        scene_dur = float(scene.duration) * scale_ratio
        start_sec = current_time
        end_sec = current_time + scene_dur
        text = scene.caption.strip() if scene.caption.strip() else scene.narration.strip()

        # SRT format
        srt_lines.append(str(idx))
        srt_lines.append(f"{_format_srt_timestamp(start_sec)} --> {_format_srt_timestamp(end_sec)}")
        srt_lines.append(text)
        srt_lines.append("")

        # VTT format
        vtt_lines.append(str(idx))
        vtt_lines.append(f"{_format_vtt_timestamp(start_sec)} --> {_format_vtt_timestamp(end_sec)}")
        vtt_lines.append(text)
        vtt_lines.append("")

        # ASS event
        ass_events.append(
            f"Dialogue: 0,{_format_ass_timestamp(start_sec)},{_format_ass_timestamp(end_sec)},Highlight,,0,0,0,,{text}"
        )

        cues_data.append({
            "index": idx,
            "scene_id": scene.id,
            "start": start_sec,
            "end": end_sec,
            "start_formatted": _format_srt_timestamp(start_sec),
            "end_formatted": _format_srt_timestamp(end_sec),
            "duration": round(scene_dur, 2),
            "text": text
        })

        current_time = end_sec

    # Write SRT
    srt_content = "\n".join(srt_lines)
    srt_path = GENERATED_CAPTIONS_DIR / "captions.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    # Write VTT
    vtt_content = "\n".join(vtt_lines)
    vtt_path = GENERATED_CAPTIONS_DIR / "captions.vtt"
    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write(vtt_content)

    # Write ASS
    ass_content = ass_header + "\n".join(ass_events)
    ass_path = GENERATED_CAPTIONS_DIR / "captions.ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    manifest = {
        "status": "completed",
        "total_cues": len(cues_data),
        "total_duration": round(current_time, 2),
        "synchronized_with_audio": audio_duration > 0,
        "files": {
            "srt": str(srt_path),
            "vtt": str(vtt_path),
            "ass": str(ass_path)
        },
        "cues": cues_data
    }

    manifest_path = GENERATED_CAPTIONS_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    logger.info("Generated captions successfully (%d cues, %s, %s, synchronized=%s)", len(cues_data), srt_path.name, vtt_path.name, audio_duration > 0)
    return manifest

def get_captions_status() -> Optional[Dict[str, Any]]:
    """Return status and cues of generated captions."""
    manifest_path = GENERATED_CAPTIONS_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    srt_path = GENERATED_CAPTIONS_DIR / "captions.srt"
    if srt_path.exists():
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "status": "completed",
            "content": content,
            "path": str(srt_path)
        }
    return None
