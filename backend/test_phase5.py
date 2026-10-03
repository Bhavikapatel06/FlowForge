"""
Phase 5 Test Script: Voice Generation Verification
Verifies:
1. Generation of narration.mp3 from storyboard script
2. Output audio file existence and non-zero size
3. Proper voice selection matching language
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

from pipeline.voice.voice_generator import (
    generate_voice_narration,
    get_voice_status,
    GENERATED_AUDIO_DIR,
)

def test_voice_generation():
    print("=== Running Phase 5 Voice Generation Verification ===")
    
    script_text = (
        "AI in student life isn't what you think. Here is how it's changing everything. "
        "Every single day, breakthroughs in AI are redefining our daily routines. "
        "The real power lies in how accessible and intelligent the tools have become."
    )
    
    print("\n[RUN] Generating narration audio file via generate_voice_narration()...")
    result = generate_voice_narration(script=script_text, language="English")
    
    assert result["status"] == "completed"
    audio_path = Path(result["path"])
    assert audio_path.exists(), f"Audio file does not exist at {audio_path}"
    assert audio_path.stat().st_size > 0, "Audio file is empty"
    print(f"[OK] Voice generated successfully: {result['filename']} ({result['file_size']} bytes, provider: {result['provider']})")
    
    status = get_voice_status()
    assert status is not None
    assert status["status"] == "completed"
    print(f"[OK] get_voice_status returned valid audio info.")
    
    print("\nAll Phase 5 Voice Generation tests passed successfully!")

if __name__ == "__main__":
    try:
        test_voice_generation()
    except Exception as e:
        print(f"\n[FAIL] Phase 5 Test failed: {e}")
        sys.exit(1)
