import os
import json
import time
import asyncio
import logging
import wave
import struct
import math
from pathlib import Path
from typing import Optional, Dict, Any

from pipeline.script.models import Storyboard

logger = logging.getLogger("qoneqt.pipeline.voice")
logging.basicConfig(level=logging.INFO)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
GENERATED_AUDIO_DIR = WORKSPACE_ROOT / "generated" / "audio"
GENERATED_SCRIPTS_DIR = WORKSPACE_ROOT / "generated" / "scripts"
GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Recommended neural voices matching slide 5 (English, Hindi, Gujarati, etc.)
VOICE_MAP = {
    "English": "en-US-ChristopherNeural",
    "Spanish": "es-ES-AlvaroNeural",
    "French": "fr-FR-HenriNeural",
    "German": "de-DE-KillianNeural",
    "Hindi": "hi-IN-MadhurNeural",
    "Gujarati": "gu-IN-DhwaniNeural",
}

def _generate_synthetic_tone_narration(output_path: Path, duration_seconds: int = 35) -> Path:
    """
    Zero-network fallback: generates a pleasant speech-paced rhythmic audio track
    using standard python library wave + struct when network TTS is unreachable.
    Guarantees that Phase 5 and Phase 7 composition never fail offline.
    """
    sample_rate = 24000
    total_samples = int(sample_rate * duration_seconds)
    
    # Generate speech-like modulated hum and cadence
    wav_path = output_path.with_suffix(".wav")
    with wave.open(str(wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            # Fundamental speech frequency ~150Hz modulated by syllable cadence (~3Hz)
            cadence = 0.6 + 0.4 * math.sin(2 * math.pi * 3.2 * t)
            # Syllable bursts and breath pauses
            burst = 1.0 if (int(t * 3.5) % 7 != 0) else 0.1
            f0 = 160.0 + 20.0 * math.sin(2 * math.pi * 0.8 * t)
            f1 = f0 * 2
            
            sample = int(
                (0.4 * math.sin(2 * math.pi * f0 * t) + 0.2 * math.sin(2 * math.pi * f1 * t))
                * cadence * burst * 14000
            )
            # Clamp to 16-bit range
            sample = max(-32768, min(32767, sample))
            frames.extend(struct.pack("<h", sample))
            
        wav_file.writeframes(frames)
    
    # If output_path was .mp3, convert or rename
    # In ffmpeg or direct playback, .wav or .mp3 works smoothly
    if output_path.suffix.lower() == ".mp3":
        # Copy to output_path or keep as mp3
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            import subprocess
            subprocess.run([
                ffmpeg_exe, "-y", "-i", str(wav_path),
                "-codec:a", "libmp3lame", "-b:a", "128k", str(output_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            wav_path.unlink(missing_ok=True)
        except Exception:
            # Fallback rename
            wav_path.replace(output_path)
    return output_path

async def _async_generate_edge_tts(text: str, voice_name: str, output_path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(str(output_path))

def generate_voice_narration(
    script: Optional[str] = None,
    language: str = "English",
    voice: Optional[str] = None,
    output_filename: str = "narration.mp3"
) -> Dict[str, Any]:
    """
    Phase 5: Voice Generation
    Generates narration audio file using edge-tts with automatic fallback.
    Saves to generated/audio/narration.mp3
    """
    output_path = GENERATED_AUDIO_DIR / output_filename
    
    # 1. Retrieve script from approved or latest storyboard if not provided
    storyboard: Optional[Storyboard] = None
    target_duration = 35
    if not script:
        approved_file = GENERATED_SCRIPTS_DIR / "approved_storyboard.json"
        latest_file = GENERATED_SCRIPTS_DIR / "latest_storyboard.json"
        target_file = approved_file if approved_file.exists() else latest_file
        
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                storyboard = Storyboard.model_validate_json(f.read())
                script = storyboard.script
                language = storyboard.language or language
                target_duration = storyboard.duration

    if not script or not script.strip():
        script = "Welcome to Qoneqt. Transforming ideas into vertical content."

    # Select voice
    voice_name = voice or VOICE_MAP.get(language, "en-US-ChristopherNeural")
    provider_used = "edge-tts"
    success = False
    error_msg = None

    # Try high-quality Edge TTS
    try:
        logger.info("Generating voice narration with voice '%s'...", voice_name)
        asyncio.run(_async_generate_edge_tts(script, voice_name, output_path))
        if output_path.exists() and output_path.stat().st_size > 1000:
            success = True
            logger.info("Successfully generated voice narration via edge-tts (%d bytes)", output_path.stat().st_size)
    except Exception as e:
        logger.warning("edge-tts generation failed (%s). Falling back to synthetic narration.", e)
        error_msg = str(e)

    # Fallback to rhythmic synthetic audio
    if not success:
        logger.info("Rendering synthetic fallback voice track...")
        _generate_synthetic_tone_narration(output_path, duration_seconds=target_duration)
        provider_used = "synthetic_cadence"
        success = True

    # Compute or estimate duration
    file_size = output_path.stat().st_size if output_path.exists() else 0
    
    result = {
        "status": "completed",
        "provider": provider_used,
        "voice": voice_name,
        "language": language,
        "path": str(output_path),
        "filename": output_path.name,
        "file_size": file_size,
        "estimated_duration": target_duration,
        "error": error_msg,
        "timestamp": int(time.time())
    }

    # Save manifest
    manifest_path = GENERATED_AUDIO_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result

def get_voice_status() -> Optional[Dict[str, Any]]:
    """Return status and metadata of the generated narration file."""
    manifest_path = GENERATED_AUDIO_DIR / "manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    out_file = GENERATED_AUDIO_DIR / "narration.mp3"
    if out_file.exists():
        return {
            "status": "completed",
            "filename": out_file.name,
            "path": str(out_file),
            "file_size": out_file.stat().st_size
        }
    return None
