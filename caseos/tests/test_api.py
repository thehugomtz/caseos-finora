"""HTTP API end to end with a scripted runtime: case creation, human gates, a Framer turn running as a background job
launched from a worker thread (the path that once returned 500), commands and search."""
import time

import pytest
from fastapi.testclient import TestClient

from caseos import llm


def _turn(spec):
    return {"reply": "Anotado como tu lectura.", "items": [
        {"kind": "USER_INTUITION", "structured": "Hugo cree que los nuevos pagan menos", "hugo_wording": "Creo que los nuevos pagan menos",
         "basis": "", "confidence": "n/a", "falsifier": "", "links": [], "updates": ""},
        {"kind": "HYPOTHESIS", "structured": "El ticket de entrada bajó", "hugo_wording": "", "basis": "", "confidence": "low",
         "falsifier": "Se debilita si el ticket de entrada es estable", "links": [], "updates": ""}],
        "framing_patch": {"executive_question": "¿Por qué cae el ingreso por cliente?", "candidate_frames": [], "initial_storyline": [],
                          "research_needed": [], "decisions_needed": [], "should_not_claim": [], "language_notes": [], "risks": []},
        "advisors": [], "alternatives": [], "challenge": {"hidden_assumptions": [], "strongest_counterargument": "",
                                                         "alternative_explanation": "", "invalidating_evidence": [],
                                                         "highest_risk_claim": ""},
        "language": {"register": "", "technical_level": "", "formality": "", "preserved_terms": [], "introduced_terms": []},
        "next_steps": []}


@pytest.fixture()
def client(cases_root):
    from caseos import server
    llm.set_llm(llm.FakeLLM({"framer": _turn, "cos": lambda spec: {"answer": "Falta research.", "referenced_ids": [],
                                                                    "next_best_actions": [], "status_note": ""}}))
    with TestClient(server.app) as c:
        yield c
    llm.set_llm(None)


def test_api_flow(client):
    assert client.get("/api/health").json()["ok"]
    cid = client.post("/api/cases", json={"name": "Caso API", "objective": "Entender la caída", "audience": ["CEO"]}).json()["id"]
    assert any(c["id"] == cid for c in client.get("/api/cases").json()["cases"])
    phases = {p["id"]: p for p in client.get(f"/api/cases/{cid}/phases").json()["phases"]}
    assert phases["briefing"]["status"] in ("not_started", "in_progress", "review")

    # human gates: out of order is refused; reopening needs a reason
    assert client.post(f"/api/cases/{cid}/phases/research/ready", json={}).status_code == 409
    r = client.post(f"/api/cases/{cid}/phases/briefing/ready", json={"note": "brief claro"})
    assert r.status_code == 409 and "entregables" in r.json()["detail"]                    # blockers stop Mark Ready
    assert client.patch(f"/api/cases/{cid}/brief", json={"fields": {"deliverables": ["Deck ejecutivo"]}}).status_code == 200
    r = client.post(f"/api/cases/{cid}/phases/briefing/ready", json={"note": "brief claro"})
    assert r.status_code == 200 and r.json()["decision"].startswith("D-")
    assert client.post(f"/api/cases/{cid}/phases/briefing/reopen", json={"reason": ""}).status_code == 400

    # a Framer turn: sync endpoint (worker thread) → job on the server loop → result in the conversation
    t = client.post(f"/api/cases/{cid}/framer", json={"message": "Creo que los nuevos pagan menos", "mode": "organize"})
    assert t.status_code == 200
    turn = None
    for _ in range(100):
        turn = next(x for x in client.get(f"/api/cases/{cid}/framing").json()["conversation"] if x["turn_id"] == t.json()["turn_id"])
        if turn["status"] in ("done", "failed"):
            break
        time.sleep(0.05)
    assert turn["status"] == "done", turn
    fr = client.get(f"/api/cases/{cid}/framing").json()
    assert fr["framing"]["executive_question"] == "¿Por qué cae el ingreso por cliente?"
    ids = turn["created"]
    h = client.get(f"/api/cases/{cid}/entities/{next(i for i in ids if i.startswith('H-'))}").json()
    assert h["entity"]["falsifier"] and h["entity"]["review"]["state"] == "proposed"
    assert client.post(f"/api/cases/{cid}/phases/framing/ready", json={}).status_code == 200

    # command layer and search
    cmd = lambda text, **kw: client.post(f"/api/cases/{cid}/command", json={"text": text, **kw}).json()
    out = cmd("guarda como decisión: comparar solo meses completos")
    assert out["intent"] == "save_decision"
    d = client.get(f"/api/cases/{cid}/entities/{out['action']['id']}").json()["entity"]
    assert d["status"] == "active" and d["user_choice"] == "comparar solo meses completos"
    assert cmd("qué falta para cerrar")["intent"] == "ask_cos"
    assert cmd("reabre framing")["action"]["confirm"] == "reopen"                           # reopen asks first, shows impact
    assert client.get(f"/api/cases/{cid}/phases").json()["phases"][1]["status"] == "ready"
    res = client.get(f"/api/cases/{cid}/search", params={"q": "ticket"}).json()
    assert res["results"][0]["type"] == "hypothesis"
    assert client.get(f"/api/cases/{cid}/entities/Q-999").status_code == 404
