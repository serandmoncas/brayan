from fastapi.testclient import TestClient

import src.orchestrator as orchestrator
from src.orchestrator import app


def test_health():
    c = TestClient(app)
    r = c.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "buscar_web" in body["tools"]


def test_webhook_empty_body():
    c = TestClient(app)
    r = c.post("/webhook", json={})
    assert r.status_code == 400


def test_webhook_authorized_sender_is_processed(monkeypatch):
    monkeypatch.setenv("AUTHORIZED_WHATSAPP_ID", "5215500000000@c.us")
    monkeypatch.setattr(orchestrator, "run_agent", lambda msg, history: "ok-reply")
    monkeypatch.setattr(orchestrator, "_HISTORY", [])
    c = TestClient(orchestrator.app)
    r = c.post("/webhook", json={"from": "5215500000000@c.us", "body": "hola"})
    assert r.status_code == 200
    assert r.json()["reply"] == "ok-reply"


def test_webhook_unauthorized_sender_is_ignored(monkeypatch):
    monkeypatch.setenv("AUTHORIZED_WHATSAPP_ID", "5215500000000@c.us")
    called = []
    monkeypatch.setattr(
        orchestrator, "run_agent", lambda msg, history: called.append(1) or "no-deberia-verse"
    )
    monkeypatch.setattr(orchestrator, "_HISTORY", [])
    c = TestClient(orchestrator.app)
    r = c.post("/webhook", json={"from": "otronumero@c.us", "body": "hola"})
    assert r.status_code == 200
    assert not r.json().get("reply")
    assert called == []


def test_webhook_fails_closed_when_unset(monkeypatch):
    monkeypatch.setenv("AUTHORIZED_WHATSAPP_ID", "")
    called = []
    monkeypatch.setattr(orchestrator, "run_agent", lambda msg, history: called.append(1) or "x")
    monkeypatch.setattr(orchestrator, "_HISTORY", [])
    c = TestClient(orchestrator.app)
    r = c.post("/webhook", json={"from": "cualquiera@c.us", "body": "hola"})
    assert r.status_code == 200
    assert not r.json().get("reply")
    assert called == []


def test_webhook_passes_previous_turn_as_history(monkeypatch):
    monkeypatch.setenv("AUTHORIZED_WHATSAPP_ID", "5215500000000@c.us")
    monkeypatch.setattr(orchestrator, "_HISTORY", [])
    seen_histories = []

    def fake_run_agent(msg, history):
        seen_histories.append(list(history))
        return f"respuesta a: {msg}"

    monkeypatch.setattr(orchestrator, "run_agent", fake_run_agent)
    c = TestClient(orchestrator.app)
    c.post("/webhook", json={"from": "5215500000000@c.us", "body": "primero"})
    c.post("/webhook", json={"from": "5215500000000@c.us", "body": "segundo"})

    assert seen_histories[0] == []
    assert {"role": "user", "content": "primero"} in seen_histories[1]
    assert {"role": "assistant", "content": "respuesta a: primero"} in seen_histories[1]
