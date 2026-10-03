from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)
API = "/api/v1"


def create(**over):
    payload = {"title": "Startup traction claim", "input_text": "The company has 50,000 active users and grew revenue 180%.", **over}
    r = client.post(f"{API}/investigations", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_health():
    r = client.get(f"{API}/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"
    assert client.get("/health").status_code == 200


def test_full_pipeline_and_report():
    inv = create()
    # TestClient runs background tasks before returning, so the run has finished
    got = client.get(f"{API}/investigations/{inv['id']}").json()
    assert got["status"] == "completed", got
    assert got["current_stage"] == "done" and got["stage_group"] == "done"
    assert got["final_verdict"]["label"] in {"true", "mostly_true", "mixed", "mostly_false", "false", "unverified"}

    report = client.get(f"{API}/reports/{inv['id']}").json()
    assert len(report["claims"]) == 2
    assert report["sources"] and report["evidence"]
    assert {"supporting", "contradicting"} <= {e["stance"] for e in report["evidence"]}
    assert report["evidence"][0]["source_url"]
    assert report["verdict"]["label"] and 0 <= report["verdict"]["confidence"] <= 1


def test_frontend_field_aliases():
    inv = create(input_text=None, claim="Claim sent as 'claim'", input_type="text")
    assert client.get(f"{API}/investigations/{inv['id']}").json()["input_text"] == "Claim sent as 'claim'"


def test_rerun_replaces_previous_results():
    inv = create()
    r = client.post(f"{API}/investigations/{inv['id']}/run")
    assert r.status_code == 202
    report = client.get(f"{API}/reports/{inv['id']}").json()
    assert len(report["claims"]) == 2        # not duplicated


def test_pipeline_failure_is_recorded(monkeypatch):
    from backend.app.integrations.tavily_client import TavilyClient

    monkeypatch.setattr(TavilyClient, "configured", property(lambda self: False))
    inv = create()
    got = client.get(f"{API}/investigations/{inv['id']}").json()
    assert got["status"] == "failed" and "TAVILY" in got["error"]


def test_chat_and_404s():
    inv = create()
    r = client.post(f"{API}/reports/{inv['id']}/chat", json={"question": "Why is this rated mixed?"})
    assert r.status_code == 200 and r.json()["answer"]
    assert client.get(f"{API}/reports/nope").status_code == 404
    assert client.get(f"{API}/investigations/nope").status_code == 404
    assert client.post(f"{API}/reports/nope/chat", json={"question": "hi"}).status_code == 404


def test_list_filter():
    create()
    assert len(client.get(f"{API}/investigations?status=completed").json()) == 1
    assert client.get(f"{API}/investigations?status=failed").json() == []
