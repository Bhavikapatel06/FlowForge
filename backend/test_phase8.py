"""
Phase 8 Test Script: Quality Gate Verification
Verifies:
1. Automated inspection of generated final.mp4
2. Resolution check (1080x1920, 9:16 vertical)
3. Duration validation
4. Audio stream and captions presence
5. Scene completeness
6. Expected return structure with checks list and status 'READY TO PUBLISH'
"""
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline.quality.quality_gate import run_quality_gate, get_latest_quality_report

def test_quality_gate():
    print("=== Running Phase 8 Quality Gate Verification ===")
    
    print("\n[RUN] Executing automated quality checks on final.mp4...")
    report = run_quality_gate()
    
    print(f"\n[REPORT] Quality Gate Status: {report['status']}")
    print(f"Passed Checks: {report['passed_checks']}/{report['total_checks']}")
    
    for check in report["checks"]:
        status_icon = "✓" if check["passed"] else "✗"
        print(f"  {status_icon} {check['name']}: {check['details']}")
        
    assert report["passed"] is True, f"Quality gate checks failed: {report}"
    assert report["status"] == "READY TO PUBLISH"
    assert report["passed_checks"] == 7
    
    # Check persistence
    saved = get_latest_quality_report()
    assert saved is not None
    assert saved["status"] == "READY TO PUBLISH"
    print("\n[OK] Quality report successfully saved to generated/quality_report.json.")
    
    print("\nAll Phase 8 Quality Gate tests passed successfully!")

if __name__ == "__main__":
    try:
        test_quality_gate()
    except Exception as e:
        print(f"\n[FAIL] Phase 8 Test failed: {e}")
        sys.exit(1)
