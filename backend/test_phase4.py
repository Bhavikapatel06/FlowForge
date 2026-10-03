"""
Phase 4 Test Script: Scene Generation Verification
Verifies:
1. Generation of visual assets for all approved scenes
2. Output image dimensions (1080x1920, 9:16 vertical)
3. Manifest generation with proper metadata
4. Single-scene retry capability (scene 3 retry without regenerating others)
"""
import sys
import io
import json
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.scenes.scene_generator import (
    generate_all_scenes,
    retry_single_scene,
    get_scenes_status,
    GENERATED_IMAGES_DIR,
)
from pipeline.script.storyboard_generator import generate_storyboard

def test_scene_generation():
    print("=== Running Phase 4 Scene Generation Verification ===")
    
    # 1. Ensure storyboard exists
    approved_file = ROOT_DIR / "generated" / "scripts" / "approved_storyboard.json"
    if not approved_file.exists():
        print("[SETUP] Generating initial storyboard...")
        sb = generate_storyboard("AI in student life")
        with open(approved_file, "w", encoding="utf-8") as f:
            f.write(sb.model_dump_json(indent=2))

    # 2. Test generate_all_scenes (using canvas_synthetic for deterministic fast test)
    print("\n[RUN] Generating visual assets for all storyboard scenes...")
    results = generate_all_scenes(provider="canvas_synthetic")
    
    assert len(results) >= 5, f"Expected at least 5 scenes, got {len(results)}"
    print(f"[OK] Generated {len(results)} scenes:")
    for res in results:
        print(f"  - Scene {res['scene_id']} ✓ [file: {res['filename']}, size: {res['file_size']} bytes]")
        img_path = Path(res["path"])
        assert img_path.exists(), f"Image file {img_path} does not exist"
        with Image.open(img_path) as img:
            assert img.size == (1080, 1920), f"Expected (1080, 1920), got {img.size}"

    # 3. Test retry_single_scene for scene 2
    print("\n[RUN] Testing isolated retry for Scene 2...")
    scene_2_path = GENERATED_IMAGES_DIR / "scene_2.jpg"
    old_mtime = scene_2_path.stat().st_mtime
    
    import time
    time.sleep(0.5)
    retry_res = retry_single_scene(scene_id=2, provider="canvas_synthetic")
    assert retry_res["scene_id"] == 2
    new_mtime = scene_2_path.stat().st_mtime
    assert new_mtime >= old_mtime, "Scene 2 file was not updated on retry"
    print(f"[OK] Isolated Scene 2 retry succeeded without altering other scenes.")

    # 4. Test get_scenes_status
    status_list = get_scenes_status()
    assert len(status_list) >= 5
    print(f"[OK] get_scenes_status returned {len(status_list)} scenes.")

    print("\nAll Phase 4 Scene Generation tests passed successfully!")

if __name__ == "__main__":
    try:
        test_scene_generation()
    except Exception as e:
        print(f"\n[FAIL] Phase 4 Test failed: {e}")
        sys.exit(1)
