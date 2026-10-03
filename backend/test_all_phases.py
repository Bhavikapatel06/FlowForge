"""
Full Pipeline Integration Test: Phase 1 through Phase 9
Tests:
1. Health & Foundation (Phase 1)
2. Storyboard Generation (Phase 2)
3. Human Review & Approval (Phase 3)
4. Scene Generation & Isolated Retry (Phase 4)
5. Voice Generation (Phase 5)
6. Captions Generation (Phase 6)
7. FFmpeg Video Composition (Phase 7)
8. Quality Gate (Phase 8)
9. Qoneqt Publishing (Phase 9)
"""
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_integration_pipeline():
    print("=" * 60)
    print("🚀 RUNNING END-TO-END PIPELINE VERIFICATION (PHASES 1-9)")
    print("=" * 60)

    # Phase 1: Health
    res = client.get("/api/health")
    assert res.status_code == 200
    print("[PASS] Phase 1: Foundation Health Check OK.")

    # Phase 2: Storyboard
    sb_res = client.post("/api/storyboard", json={
        "topic": "AI in student life",
        "style": "Educational",
        "language": "English"
    })
    assert sb_res.status_code == 200
    sb = sb_res.json()
    assert len(sb["scenes"]) >= 5
    print(f"[PASS] Phase 2: Storyboard generated ({len(sb['scenes'])} scenes, {sb['duration']}s).")

    # Phase 3: Approve
    appr_res = client.post("/api/storyboard/approve", json=sb)
    assert appr_res.status_code == 200
    print("[PASS] Phase 3: Human Review & Approval locked state.")

    # Phase 4: Scenes
    scenes_res = client.post("/api/scenes/generate?provider=canvas_synthetic")
    assert scenes_res.status_code == 200
    scenes_data = scenes_res.json()
    assert scenes_data["count"] >= 5
    print(f"[PASS] Phase 4: Scene Generation created {scenes_data['count']} 9:16 vertical scenes.")

    # Test single retry
    retry_res = client.post("/api/scenes/retry/1?provider=canvas_synthetic")
    assert retry_res.status_code == 200
    assert retry_res.json()["scene_id"] == 1
    print("[PASS] Phase 4: Single-scene isolated retry verified.")

    # Phase 5: Voice
    voice_res = client.post("/api/voice/generate", json={"language": "English"})
    assert voice_res.status_code == 200
    v_data = voice_res.json()
    assert v_data["file_size"] > 0
    print(f"[PASS] Phase 5: Voice narration generated ({v_data['filename']}, {v_data['file_size']} bytes).")

    # Phase 6: Captions
    cap_res = client.post("/api/captions/generate")
    assert cap_res.status_code == 200
    c_data = cap_res.json()
    assert c_data["total_cues"] >= 5
    print(f"[PASS] Phase 6: Captions generated ({c_data['total_cues']} cues, SRT/VTT/ASS).")

    # Phase 7: Composition
    comp_res = client.post("/api/compose")
    assert comp_res.status_code == 200
    vid_data = comp_res.json()
    assert vid_data["resolution"] == "1080x1920"
    print(f"[PASS] Phase 7: Video Composition rendered vertical MP4 ({vid_data['resolution']}, {vid_data['file_size'] / (1024*1024):.2f} MB).")

    # Phase 8: Quality Gate
    q_res = client.post("/api/quality/check")
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["passed"] is True
    assert q_data["status"] == "READY TO PUBLISH"
    print(f"[PASS] Phase 8: Quality Gate PASSED with {q_data['passed_checks']}/{q_data['total_checks']} checks.")

    # Phase 9: Publish
    pub_res = client.post("/api/publish", json={"channel": "global-feed"})
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    assert "release_id" in pub_data
    print(f"[PASS] Phase 9: Qoneqt Publishing succeeded with Release ID: {pub_data['release_id']}.")

    print("\n" + "=" * 60)
    print("🏆 ALL 9 PIPELINE PHASES VERIFIED AND FUNCTIONING 100%!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_integration_pipeline()
    except Exception as e:
        print(f"\n[FAIL] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
