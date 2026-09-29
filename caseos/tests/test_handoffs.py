"""Handoffs: analytics finding → EvidenceTable, number discipline, COS impact detection, the Story Package contract and
the Visual Storyteller handoff."""
import asyncio
import shutil

import pytest
import yaml

from caseos import analytics, cases, cos, evidence, llm, story, storyteller
from caseos.store import StoreError
from caseos.workspaces import finora_eda


class FakeJob:
    def __init__(self, case_id, agent="cos"):
        self.case_id, self.agent = case_id, agent

    async def event(self, kind, data=None):
        pass


# ------------------------------------------------------------------------------------------ numbers and tables
def test_numbers_in_spanish_formats():
    vals = {n.value for n in evidence.numbers_in("Cayó −38% a COP 92,8 mil; 4,5× más; 1.678 clientes; COP 404 millones")}
    assert {-38.0, 92800.0, 4.5, 1678.0, 404000000.0} <= vals


def _table(**over):
    return {**evidence.make_table(table_key="FIN-ENTRY-01", title="Monto de entrada por cohorte", question="¿Bajó?",
                                  columns=["Cohorte", "Monto de entrada (COP mil)", "Cambio"],
                                  rows=[["2023", 120.5, ""], ["2024", 74.7, "-38%"]], message="El monto de entrada bajó",
                                  source={"dataset": "transactions"}, limitations=["Monto observado, no MRR contractual"],
                                  preferred_visual="bar"), **over}


def test_table_contract_and_unsupported_numbers():
    t = _table()
    assert evidence.validate_table(t) == []
    assert evidence.unsupported_numbers("El monto de entrada pasó de 120,5 a 74,7 (−38%)", [t]) == []
    assert evidence.unsupported_numbers("El monto de entrada cayó 52%", [t]) == ["52%"]
    errs = evidence.validate_table(_table(rows=[["2023"]], source={}, preferred_visual="pie"))
    assert any("fila" in e for e in errs) and any("fuente" in e for e in errs) and any("preferred_visual" in e for e in errs)


@pytest.mark.skipif(not finora_eda.adapter({}).available, reason="finora-eda no está junto a caseos")
def test_analytics_finding_becomes_a_canonical_evidence_table(cases_root):
    s = cases.create_case(name="WS", objective="x", audience=["CFO"], case_id="ws", workspace={"type": "finora-eda"})
    ws = analytics.adapter_or_fail(s)
    canon = next(h for h in ws.canonical() if ws.canonical_table(h, table_key="probe")["rows"])
    f = s.create("finding", {"headline": canon.get("texto") or canon["id"], "kind": "analytics",
                             "source_ref": {"canonical_id": canon["id"]}}, actor="analytics")
    t = analytics.to_table(s, f["id"])
    assert t["status"] == "valid" and evidence.validate_table(t) == []
    assert t["finding"] == f["id"] and t["id"] in s.get(f["id"])["links"]                  # lineage both ways
    assert analytics.to_table(s, f["id"])["id"] == t["id"]                                   # idempotent
    ext = s.create("finding", {"headline": "benchmark externo", "kind": "external"}, actor="business_research")
    with pytest.raises(StoreError):
        analytics.to_table(s, ext["id"])


# ------------------------------------------------------------------------------------------ COS
def test_cos_flags_claims_on_the_same_lineage(case):
    h = case.create("hypothesis", {"statement": "La caída es mezcla", "status": "open"}, actor="framer")
    c = case.create("claim", {"key": "mix", "headline": "El promedio cae por mezcla", "links": [h["id"]]}, actor="cos")
    f = case.create("finding", {"headline": "Los clientes antiguos también bajaron", "links": [h["id"]]}, actor="analytics")
    cand = cos.impact_candidates(case, f["id"])
    assert cand["hypotheses"] == [h["id"]] and cand["claims"] == [c["id"]]
    alerts = cos.flag_impact(case, f["id"])
    assert [a["target"] for a in alerts] == [c["id"]] and alerts[0]["status"] == "open"
    assert cos.flag_impact(case, f["id"]) == []                                              # no duplicate alerts


def test_cos_contradiction_flags_claim_and_waits_for_hugo(case):
    h = case.create("hypothesis", {"statement": "La caída es mezcla", "status": "open"}, actor="framer")
    c = case.create("claim", {"key": "mix", "headline": "El promedio cae por mezcla", "links": [h["id"]]}, actor="cos")
    f = case.create("finding", {"headline": "Los antiguos bajaron su monto 12%", "links": [h["id"]]}, actor="analytics")
    out = {"summary": "Contradice la lectura de mezcla", "status_note": "",
           "impacts": [{"target": c["id"], "effect": "contradicts", "why": "los antiguos también bajan", "severity": "high",
                        "options": [{"key": "A", "label": "Revisar el claim", "consequence": ""},
                                    {"key": "B", "label": "Investigar más", "consequence": ""}],
                        "recommended": "A", "recommended_why": ""},
                       {"target": h["id"], "effect": "supports", "why": "", "severity": "low", "options": [],
                        "recommended": "", "recommended_why": ""}],
           "new_hypotheses": [], "new_questions": []}
    llm.set_llm(llm.FakeLLM({"cos": lambda spec: out}))
    try:
        res = asyncio.run(cos._impact_job(FakeJob(case.id), {"source_id": f["id"], "reason": "test"}))
    finally:
        llm.set_llm(None)
    x = case.get(res["created"][0])
    assert x["effect"] == "contradicts" and x["status"] == "open" and x["recommended"] == "A"
    claim = case.get(c["id"])
    assert claim["stale"] and claim["headline"] == "El promedio cae por mezcla"             # flagged, never rewritten
    assert not case.get(h["id"]).get("stale")                                                # "supports" is not an alert
    r = cos.resolve_alert(case, x["id"], choice="ignore", rationale="ruido de un mes")
    assert case.get(r["decision"])["status"] == "active" and not case.get(c["id"]).get("stale")
    with pytest.raises(ValueError):
        cos.resolve_alert(case, x["id"], choice="A", actor="cos")                            # only Hugo resolves


# ------------------------------------------------------------------------------------------ Story Package
def _accepted_evidence(case):
    t = case.create("table", {**_table(), "status": "valid"}, actor="analytics")
    f = case.create("finding", {"headline": "El monto de entrada cayó 38%", "links": [t["id"]]}, actor="analytics")
    case.set_review(f["id"], "accepted", actor="hugo")
    return f, t


def _package(f, t, **claim):
    return {"audience": ["CFO"], "objective": "Explicar la caída del monto por cliente", "from_to": {"from": "", "to": ""},
            "governing_thought": "El promedio baja por quién entra, no por lo que pagan los de siempre",
            "executive_questions": [], "story_arc": {"archetype": "", "logic": ""},
            "sections": [{"name": "Hallazgo", "purpose": "", "claim_keys": ["entry"]}],
            "claims": [{"key": "entry", "question": "", "headline": "El monto de entrada cayó 38%", "answer": "De 120,5 a 74,7",
                        "role_in_story": "evidence", "evidence_ids": [f["id"]], "table_ids": [t["id"]], "research_ids": [],
                        "framework_ids": [], "confidence": "high", "limitations": [], "visual_intent": "bar", "hugo_wording": "",
                        **claim}],
            "recommendations": [], "appendix_candidates": [], "unresolved_questions": [], "visual_references": [],
            "language_profile": {"primary": "es"}}


def test_story_package_validation(case):
    f, t = _accepted_evidence(case)
    errors, _ = story.validate_package(case, _package(f, t))
    assert errors == []
    errors, _ = story.validate_package(case, _package(f, t, headline="El monto de entrada cayó 52%"))
    assert any("sin tabla" in e for e in errors)                                            # numbers travel in tables
    errors, _ = story.validate_package(case, _package(f, t, evidence_ids=[]))
    assert any("unsupported claim" in e for e in errors)
    _, warnings = story.validate_package(case, _package(f, t, answer="Cayó porque entran clientes más chicos"))
    assert any("causal" in w for w in warnings)
    case.mark_stale(t["id"], reason="reabierto", actor="hugo")
    errors, _ = story.validate_package(case, _package(f, t))
    assert any("needs_review" in e for e in errors)


def test_story_package_is_versioned_and_proposed_for_review(case):
    f, t = _accepted_evidence(case)
    res = story.apply_package(case, _package(f, t), actor="cos")
    assert res["errors"] == [] and res["version"] == 1
    pkg = case.read_data("story/package.yaml")
    assert pkg["claims"][0]["claim_id"] == res["claims"][0] and pkg["validation"]["ok"]
    assert case.meta()["phases"]["story"]["status"] == "review"
    res2 = story.apply_package(case, _package(f, t, headline="El monto de entrada bajó 38%"), actor="cos")
    assert res2["version"] == 2 and res2["claims"] == res["claims"]                          # stable claim IDs
    assert (case.root / "story" / "versions" / "package.v1.yaml").exists()


@pytest.mark.skipif(not ((storyteller.renderer_dir() / "scripts" / "new-deck.mjs").exists() and shutil.which("node")),
                    reason="Executive Visual Storyteller no instalado en ~/.claude/skills")
def test_visual_storyteller_accepts_the_story_package(case):
    f, t = _accepted_evidence(case)
    story.apply_package(case, _package(f, t), actor="cos")
    with pytest.raises(StoreError):
        storyteller.prepare(case)                                                            # Story must be Ready first
    meta = case.meta()
    meta["phases"]["story"]["status"] = "ready"
    case.save_meta(meta)
    rec = storyteller.prepare(case, direction="editorial", title="Prueba", critic=False)
    deck = case.root / rec["path"]
    for rel in ("deck.json", "assets/theme.css", "storyline.md", "caseos-handoff.yaml", "data/FIN-ENTRY-01.yaml"):
        assert (deck / rel).exists(), rel
    handoff = yaml.safe_load((deck / "caseos-handoff.yaml").read_text())
    assert handoff["claims"][0]["claim_id"] and handoff["tables"] == {t["id"]: "data/FIN-ENTRY-01.yaml"}
    data = yaml.safe_load((deck / "data" / "FIN-ENTRY-01.yaml").read_text())
    assert data["rows"] == t["rows"]
    assert "El monto de entrada cayó 38%" in (deck / "storyline.md").read_text()


def test_alert_on_the_framing_itself_resolves_cleanly(case):
    from caseos import phases
    q = case.create("question", {"text": "¿Qué cambió?", "status": "open"}, actor="framer")
    case.create("hypothesis", {"statement": "mezcla", "falsifier": "precio domina", "status": "open", "links": [q["id"]]},
                actor="framer")
    fr = case.read_data("framing/current.yaml")
    fr["executive_question"] = "¿Por qué cae el ingreso por cliente?"
    case.write_data("framing/current.yaml", fr)
    phases.mark_ready(case, "briefing", actor="hugo")
    phases.mark_ready(case, "framing", actor="hugo")
    x = case.create("alert", {"kind": "framing_change", "status": "open", "effect": "changes_framing", "source": q["id"],
                              "target": "framing", "title": "cambia el framing",
                              "options": [{"key": "A", "label": "Renombrar la métrica", "consequence": ""}]}, actor="cos")
    r = cos.resolve_alert(case, x["id"], choice="A", rationale="ok")
    assert r["phase_flagged"] == "framing" and "Renombrar la métrica" in r["framer_prefill"]
    assert case.meta()["phases"]["framing"]["status"] == "needs_review"
    assert case.get(x["id"])["status"] == "resolved"
    with pytest.raises(ValueError):
        cos.resolve_alert(case, x["id"], choice="A")                                           # no double resolution
