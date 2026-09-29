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
        "framing_patch": {"executive_question": "¿Por qué cae el ingreso por cliente?", "candidate_frames": [],
                          "problem": {"statement": "Entender si la caída del ingreso por cliente es mezcla o precio.", "situation": "",
                                      "why_it_matters": "", "in_scope": [], "out_of_scope": []},
                          "storyline_guide": [], "research_plan": [],
                          "decisions_needed": [], "should_not_claim": [], "language_notes": [], "risks": []},
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
    assert client.post(f"/api/cases/{cid}/phases/framing/ready", json={}).status_code == 409   # problem not approved yet
    sh = client.get(f"/api/cases/{cid}/framing").json()["shaping"]
    assert sh["problem"]["pending"]["value"]["statement"].startswith("Entender si la caída")
    assert client.post(f"/api/cases/{cid}/shaping/problem/approve").status_code == 200
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


def test_shaping_endpoints(client, monkeypatch):
    from caseos import config, research
    monkeypatch.setattr(config, "AUTO_COS", False)
    launched = []
    monkeypatch.setattr(research, "launch_job", lambda store, rid: launched.append(rid) or type("J", (), {"id": "JOB-x"})())
    cid = client.post("/api/cases", json={"name": "Caso Shaping", "objective": "Entender la caída", "audience": ["CFO"]}).json()["id"]
    k = lambda key: key.replace(":", "%3A")                                            # what encodeURIComponent sends
    assert client.put(f"/api/cases/{cid}/shaping/{k('guion:new')}", json={"title": "Overview", "slides": [{"title": "Entradas vs monto"}]}).status_code == 200
    r = client.put(f"/api/cases/{cid}/shaping/{k('plan:new')}", json={"question": "¿Qué descuentos usan otras SaaS B2B?", "kind": "research", "intensity": "L1"})
    assert r.status_code == 200 and r.json()["plan"][0]["approved"]["status"] == "approved"
    assert client.put(f"/api/cases/{cid}/shaping/{k('plan:new')}", json={"question": ""}).status_code == 400
    sh = client.get(f"/api/cases/{cid}/shaping").json()
    assert sh["progress"] == {**sh["progress"], "guion_sections": 1, "slides": 1, "tasks_approved": 1}
    out = client.post(f"/api/cases/{cid}/shaping/tasks/RT-001/send").json()
    assert out["research_id"].startswith("R-") and launched == [out["research_id"]]
    r = client.get(f"/api/cases/{cid}/entities/{out['research_id']}").json()["entity"]
    assert (r["specialty"], r["intensity"], r["shaping_task"], r["purpose_ok"]) == ("business", "L1", "RT-001", True)
    assert client.delete(f"/api/cases/{cid}/shaping/{k('plan:RT-001')}").status_code == 400   # already in Research
    assert client.post(f"/api/cases/{cid}/shaping/{k('guion:S1')}/approve").status_code == 400  # nothing pending
    fr = client.get(f"/api/cases/{cid}/framing").json()
    assert "## 3. Guion de la historia" in fr["document"] and "R-" in fr["document"]
