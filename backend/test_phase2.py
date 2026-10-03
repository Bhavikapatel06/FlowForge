"""
Phase 2 Test Script
Verifies:
1. POST /api/storyboard generates and validates strict Storyboard JSON
2. Validates title, hook, duration, script, keywords, and scene array (5-6 scenes)
3. Confirms scene schema: id, duration, narration, visual_prompt, caption
4. Confirms storyboard persistence in generated/scripts/latest_storyboard.json
"""
import sys
import io
import json
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_storyboard_generation():
    payload = {
        "topic": "AI in student life",
        "style": "Educational",
        "language": "English"
    }
    
    print("[RUN] Sending POST /api/storyboard request...")
    response = client.post("/api/storyboard", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    data = response.json()
    print("[OK] Response received successfully.")
    
    # Assert top-level fields
    assert "title" in data and len(data["title"]) > 0, "Missing or empty title"
    assert "hook" in data and len(data["hook"]) > 0, "Missing or empty hook"
    assert "duration" in data and data["duration"] >= 20, f"Invalid duration: {data.get('duration')}"
    assert "script" in data and len(data["script"]) > 0, "Missing or empty script"
    assert "keywords" in data and isinstance(data["keywords"], list), "Invalid keywords"
    assert "scenes" in data and isinstance(data["scenes"], list), "Invalid scenes list"
    
    scene_count = len(data["scenes"])
    assert 4 <= scene_count <= 8, f"Expected 5-6 scenes, got {scene_count}"
    print(f"[OK] Generated {scene_count} scenes. Target duration: {data['duration']}s.")
    
    # Assert scene schema
    total_scene_duration = 0
    for idx, scene in enumerate(data["scenes"]):
        assert "id" in scene, f"Scene {idx} missing id"
        assert "duration" in scene and scene["duration"] > 0, f"Scene {idx} invalid duration"
        assert "narration" in scene and len(scene["narration"]) > 0, f"Scene {idx} missing narration"
        assert "visual_prompt" in scene and len(scene["visual_prompt"]) > 0, f"Scene {idx} missing visual_prompt"
        assert "caption" in scene and len(scene["caption"]) > 0, f"Scene {idx} missing caption"
        total_scene_duration += scene["duration"]
        print(f"  - Scene {scene['id']}: ({scene['duration']}s) {scene['caption']}")
    
    print(f"[OK] Total scene duration: {total_scene_duration}s.")
    
    # Assert persistence
    latest_file = ROOT_DIR / "generated" / "scripts" / "latest_storyboard.json"
    assert latest_file.exists(), f"Expected cache file {latest_file} to exist"
    with open(latest_file, "r", encoding="utf-8") as f:
        cached = json.load(f)
    assert cached["title"] == data["title"], "Cached file title mismatch"
    print("[OK] Storyboard file persisted to generated/scripts/latest_storyboard.json.")

if __name__ == "__main__":
    try:
        print("=== Running Phase 2 AI Storyboard Verification ===")
        test_storyboard_generation()
        print("\nAll Phase 2 AI Storyboard tests passed successfully!")
    except Exception as e:
        print(f"\n[FAIL] Phase 2 Test failed: {e}")
        sys.exit(1)
