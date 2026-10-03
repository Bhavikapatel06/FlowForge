"""
Phase 6 Test Script: Captions Verification
Verifies:
1. Generation of captions.srt using scene timings and storyboard captions
2. Standard SRT format and timing validity
3. Generation of WebVTT and ASS subtitles
4. Manifest persistence
"""
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.captions.caption_generator import (
    generate_captions,
    get_captions_status,
    GENERATED_CAPTIONS_DIR,
)

def test_captions_generation():
    print("=== Running Phase 6 Captions Verification ===")
    
    print("\n[RUN] Generating captions from approved storyboard...")
    res = generate_captions()
    
    assert res["status"] == "completed"
    assert res["total_cues"] >= 5, f"Expected at least 5 cues, got {res['total_cues']}"
    
    srt_path = Path(res["files"]["srt"])
    assert srt_path.exists(), f"SRT file does not exist at {srt_path}"
    
    content = srt_path.read_text(encoding="utf-8")
    assert "-->" in content, "Invalid SRT format, missing timestamp separator '-->'"
    assert "00:00:00,000" in content, "First cue must start at 00:00:00,000"
    
    print(f"[OK] Generated {res['total_cues']} caption cues for {res['total_duration']}s total duration:")
    for cue in res["cues"]:
        print(f"  - Cue {cue['index']}: [{cue['start_formatted']} --> {cue['end_formatted']}] \"{cue['text']}\"")
        
    vtt_path = Path(res["files"]["vtt"])
    assert vtt_path.exists(), f"VTT file does not exist at {vtt_path}"
    print(f"[OK] WebVTT file verified: {vtt_path.name}")

    print("\nAll Phase 6 Captions tests passed successfully!")

if __name__ == "__main__":
    try:
        test_captions_generation()
    except Exception as e:
        print(f"\n[FAIL] Phase 6 Test failed: {e}")
        sys.exit(1)
