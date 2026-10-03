"""
Phase 1 Test Script
Verifies:
1. FastAPI app imports and loads successfully
2. /api/health returns 200 OK
3. POST /api/generate receives { "topic": "AI in student life" } and responds with status "received"
"""
import sys
import io

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("status") == "ok"
    print("[OK] Health check passed:", data)

def test_generate_phase1():
    payload = {
        "topic": "AI in student life",
        "style": "Educational",
        "language": "English"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("status") == "received", f"Expected 'received', got {data.get('status')}"
    assert data.get("topic") == "AI in student life"
    print("[OK] POST /api/generate passed:", data)

if __name__ == "__main__":
    try:
        print("Running Phase 1 Backend Verification...")
        test_health()
        test_generate_phase1()
        print("\nAll Phase 1 Backend tests passed successfully!")
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
