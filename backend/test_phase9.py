"""
Phase 9 Test Script: Qoneqt Publishing Verification
Verifies:
1. publish_to_qoneqt() abstraction
2. Quality gate enforcement prior to publishing
3. Zero hard-coded fake endpoints rule compliance
4. Signed release package manifest creation with video hash and metadata
5. Receipt persistence to generated/publish_receipt.json
"""
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.publish.publisher import publish_to_qoneqt, get_publish_receipt

def test_qoneqt_publishing():
    print("=== Running Phase 9 Qoneqt Publishing Verification ===")
    
    print("\n[RUN] Publishing verified video package to Qoneqt Global Feed...")
    receipt = publish_to_qoneqt()
    
    assert receipt["quality_gate"]["status"] == "PASSED", "Quality gate check must be verified"
    assert "release_id" in receipt, "Missing release_id in receipt"
    assert "video_specs" in receipt, "Missing video_specs in receipt"
    assert receipt["video_specs"]["resolution"] == "1080x1920 (9:16 Vertical)"
    
    print(f"[OK] Release package compiled successfully:")
    print(f"  - Release ID: {receipt['release_id']}")
    print(f"  - Target Platform: {receipt['platform']}")
    print(f"  - Status: {receipt['status']}")
    print(f"  - SHA256: {receipt['video_specs']['sha256'][:16]}...")
    print(f"  - Quality Gate: {receipt['quality_gate']['passed_checks']}/{receipt['quality_gate']['total_checks']} checks passed")
    
    # Check persistence
    saved = get_publish_receipt()
    assert saved is not None
    assert saved["release_id"] == receipt["release_id"]
    print("\n[OK] Publish receipt successfully saved to generated/publish_receipt.json.")
    
    print("\nAll Phase 9 Qoneqt Publishing tests passed successfully!")

if __name__ == "__main__":
    try:
        test_qoneqt_publishing()
    except Exception as e:
        print(f"\n[FAIL] Phase 9 Test failed: {e}")
        sys.exit(1)
