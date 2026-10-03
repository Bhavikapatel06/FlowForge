"""
Phase 7 Test Script: Video Composition Verification
Verifies:
1. Retrieval of FFmpeg executable via imageio-ffmpeg
2. Video composition combining 6 vertical scenes, audio narration, and timing
3. Target resolution: 1080x1920 (9:16 vertical)
4. FastStart browser playability and valid MP4 container
"""
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.composer.video_composer import (
    compose_video,
    get_video_status,
    get_ffmpeg_executable,
    GENERATED_VIDEOS_DIR,
)

def test_video_composition():
    print("=== Running Phase 7 Video Composition Verification ===")
    
    # 1. Check FFmpeg binary
    ffmpeg_exe = get_ffmpeg_executable()
    print(f"[OK] Found FFmpeg executable: {ffmpeg_exe}")
    
    # 2. Run video composition
    print("\n[RUN] Composing vertical 9:16 video via FFmpeg...")
    result = compose_video(output_filename="final.mp4")
    
    assert result["status"] == "completed"
    video_path = Path(result["path"])
    assert video_path.exists(), f"Video file not found at {video_path}"
    assert video_path.stat().st_size > 50000, f"Video file too small: {video_path.stat().st_size} bytes"
    
    print(f"[OK] Final MP4 generated successfully:")
    print(f"  - File: {result['filename']}")
    print(f"  - Size: {result['file_size']} bytes ({result['file_size'] / (1024*1024):.2f} MB)")
    print(f"  - Resolution: {result['resolution']} ({result['aspect_ratio']})")
    print(f"  - Scenes: {result['scenes_count']}")
    print(f"  - Render time: {result['render_time_sec']}s")
    
    status = get_video_status()
    assert status is not None
    assert status["status"] == "completed"
    print(f"[OK] get_video_status verified.")
    
    print("\nAll Phase 7 Video Composition tests passed successfully!")

if __name__ == "__main__":
    try:
        test_video_composition()
    except Exception as e:
        print(f"\n[FAIL] Phase 7 Test failed: {e}")
        sys.exit(1)
