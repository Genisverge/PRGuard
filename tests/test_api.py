from fastapi.testclient import TestClient
import app.api as api

client = TestClient(api.app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_response(monkeypatch):
    monkeypatch.setattr(api, "run_analysis", lambda: "Test report")
    response = client.post("/analyze")
    assert response.status_code == 200
    assert response.json() == {"report": "Test report"}
