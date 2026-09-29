"""Core: persistence, IDs and lineage, phase gates, reopen with impact radius."""
import pytest

from caseos import brain, cases, phases
from caseos.store import CaseStore


def _framing_ready(case):
    fr = case.read_data("framing/current.yaml")
    fr["executive_question"] = "¿Por qué cae el ingreso por cliente activo?"
    fr["problem"] = {"statement": "Entender si la caída del ingreso por cliente es mezcla o precio.", "situation": "",
                     "why_it_matters": "", "in_scope": [], "out_of_scope": []}
    case.write_data("framing/current.yaml", fr)
    q = case.create("question", {"text": "¿Qué cambió en los clientes nuevos?", "status": "open"}, actor="framer")
    h = case.create("hypothesis", {"statement": "La caída es de mezcla, no de precio", "falsifier": "El efecto precio domina",
                                   "status": "open", "links": [q["id"]]}, actor="framer")
    return q, h


def test_persistence_survives_reload(case, cases_root):
    q = case.create("question", {"text": "¿Qué podemos comparar?", "status": "open"}, actor="hugo")
    case.update(q["id"], {"status": "answered"}, actor="hugo")
    cases.forget("prueba")
    fresh = CaseStore(cases_root / "prueba")
    got = fresh.get(q["id"])
    assert got["status"] == "answered" and got["version"] == 2
    assert fresh.history(q["id"])[0]["entity"]["status"] == "open"          # previous version preserved
    assert any(a["targets"] == [q["id"]] for a in fresh.activity())         # operational trace persisted
    assert (cases_root / "prueba" / "brain.md").exists()


def test_ids_are_sequential_and_never_reused(case):
    a = case.create("hypothesis", {"statement": "a"}, actor="framer")
    b = case.create("hypothesis", {"statement": "b"}, actor="framer")
    assert (a["id"], b["id"]) == ("H-001", "H-002")
    case.update(b["id"], {"statement": "b2"}, actor="hugo")
    assert case.next_id("hypothesis") == "H-003"


def test_only_hugo_marks_ready(case):
    with pytest.raises(phases.GateError):
        phases.mark_ready(case, "briefing", actor="framer")


def test_mark_ready_snapshot_decision_brain_unlock(case):
    res = phases.mark_ready(case, "briefing", actor="hugo", note="brief claro")
    assert (case.root / res["snapshot"] / "case.yaml").exists()
    assert (case.root / res["approved_artifact"]).exists()
    d = case.get(res["decision"])
    assert d["kind"] == "phase_gate" and d["status"] == "active"
    meta = case.meta()
    assert meta["phases"]["briefing"]["status"] == "ready" and meta["phases"]["briefing"]["ready_at"]
    assert phases.unlocked(meta, "framing") and not phases.unlocked(meta, "research")
    assert "v1 aprobada" in case.read_text("brain.md")
    # second approval keeps v1
    phases.mark_ready(case, "briefing", actor="hugo", note="otra vez")
    assert (case.root / "brief" / "approved" / "brief.v1.yaml").exists()
    assert (case.root / "brief" / "approved" / "brief.v2.yaml").exists()


def test_framing_gate_requires_question_and_hypothesis(case):
    phases.mark_ready(case, "briefing", actor="hugo")
    chk = phases.readiness(case, "framing")
    assert not chk["ok"] and any("pregunta ejecutiva" in b for b in chk["blockers"])
    _framing_ready(case)
    chk = phases.readiness(case, "framing")
    assert chk["ok"], chk
    res = phases.mark_ready(case, "framing", actor="hugo")
    assert all((e.get("review") or {}).get("state") == "accepted" for e in case.all().values() if e.get("phase") == "framing")
    assert res["version"] == 1


def test_reopen_flags_downstream_without_deleting(case):
    phases.mark_ready(case, "briefing", actor="hugo")
    q, h = _framing_ready(case)
    phases.mark_ready(case, "framing", actor="hugo")
    r = case.create("research", {"research_question": "¿Mezcla o precio?", "status": "completed", "links": [h["id"]]}, actor="research")
    f = case.create("finding", {"headline": "El ticket de entrada bajó", "links": [r["id"]]}, actor="analytics")
    c = case.create("claim", {"headline": "La caída es de mezcla", "links": [f["id"]]}, actor="cos")
    before = set(case.all())
    imp = phases.impact(case, "framing")
    assert set(imp["affected"]) == {r["id"], f["id"], c["id"]}
    assert "1 research items" in imp["headline"] and "1 story claims" in imp["headline"]
    res = phases.reopen(case, "framing", actor="hugo", reason="nuevo dato cambia la pregunta")
    after = case.all()
    assert before <= set(after)                                  # nothing deleted
    for eid in (r["id"], f["id"], c["id"]):
        assert after[eid]["stale"]["phase"] == "framing"
    assert case.meta()["phases"]["framing"]["status"] == "reopened"
    assert case.get(res["decision"])["affected_items"] == sorted([r["id"], f["id"], c["id"]])


def test_brain_sections_present(case):
    text = brain.render(case)
    for sec in ["## Case", "## Objective", "## Audience", "## Current Phase", "## Current Status", "## Approved Briefing",
                "## Approved Framing", "## Governing Question", "## Executive Questions", "## Current Story",
                "## Decisions", "## Active Hypotheses", "## Evidence We Trust", "## Things We Cannot Claim",
                "## Open Questions", "## Research Queue", "## Accepted Frameworks", "## Key Tables",
                "## Contradictions", "## Risks", "## Artifacts", "## Language Profile", "## Recent Material Changes"]:
        assert sec in text, sec
