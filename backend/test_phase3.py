"""
Phase 3 Test Script
Verifies:
1. Simulates user edits to title, hook, and scene captions
2. Calls POST /api/storyboard/approve with edited Storyboard model
3. Validates response: status 'approved' and matching approved storyboard
4. Confirms persistence to generated/scripts/approved_storyboard.json
5. Verifies GET /api/storyboard/approved returns the locked approved storyboard
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

def test_human_review_and_approval():
    # 1. Fetch latest or generate a storyboard first
    res = client.get("/api/storyboard/latest")
    if res.status_code == 200 and res.json() is not None:
        storyboard_data = res.json()
    else:
        gen_res = client.post("/api/storyboard", json={"topic": "AI in student life"})
        assert gen_res.status_code == 200
        storyboard_data = gen_res.json()

    print("[OK] Loaded storyboard:", storyboard_data["title"])

    # 2. Simulate human review edits
    edited_data = dict(storyboard_data)
    edited_data["title"] = "AI in Student Life: The Ultimate 2026 Guide [Edited by Human]"
    edited_data["hook"] = "Stop studying the old way. Here is the AI workflow that changes everything. [Approved]"
    
    # Modify scene 1 caption & visual prompt
    edited_data["scenes"][0]["caption"] = "The old study method is officially dead."
    edited_data["scenes"][0]["visual_prompt"] = (
        "Cinematic 9:16 vertical view of a modern student studying with futuristic glowing holographic notes."
    )

    print("[RUN] Submitting human-approved storyboard to POST /api/storyboard/approve...")
    approve_res = client.post("/api/storyboard/approve", json=edited_data)
    assert approve_res.status_code == 200, f"Expected 200, got {approve_res.status_code}: {approve_res.text}"
    
    resp_json = approve_res.json()
    assert resp_json["status"] == "approved"
    assert resp_json["storyboard"]["title"] == edited_data["title"]
    assert resp_json["storyboard"]["scenes"][0]["caption"] == "The old study method is officially dead."
    print("[OK] Approval response confirmed with status 'approved'.")

    # 3. Check disk file
    approved_file = ROOT_DIR / "generated" / "scripts" / "approved_storyboard.json"
    assert approved_file.exists(), "approved_storyboard.json does not exist on disk"
    with open(approved_file, "r", encoding="utf-8") as f:
        disk_data = json.load(f)
    assert disk_data["title"] == edited_data["title"]
    print("[OK] Approved storyboard verified on disk in generated/scripts/approved_storyboard.json.")

    # 4. Check GET /api/storyboard/approved
    get_approved = client.get("/api/storyboard/approved")
    assert get_approved.status_code == 200
    assert get_approved.json()["title"] == edited_data["title"]
    print("[OK] GET /api/storyboard/approved successfully retrieved the locked approved storyboard.")

if __name__ == "__main__":
    try:
        print("=== Running Phase 3 Human Review Verification ===")
        test_human_review_and_approval()
        print("\nAll Phase 3 Human Review tests passed successfully!")
    except Exception as e:
        print(f"\n[FAIL] Phase 3 Test failed: {e}")
        sys.exit(1)
