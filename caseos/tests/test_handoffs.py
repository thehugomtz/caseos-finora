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
    fr["problem"] = {"statement": "Separar mezcla de precio.", "situation": "", "why_it_matters": "", "in_scope": [], "out_of_scope": []}
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


def test_quantities_in_words_must_match_the_data():
    t = evidence.make_table(table_key="G", title="g", question="q", columns=["mes", "clientes", "monto"],
                            rows=[["ene-22", 377, 92839.0], ["oct-24", 1678, 57811.0]], message="m",
                            source={"dataset": "d"}, limitations=["l"])
    # the case the Visual Storyteller caught live: 92,8 → 57,8 mil is ×0.62, not "a la mitad"
    errs, _ = evidence.verbal_ratio_issues("El monto cayó a la mitad: de COP 92,8 mil a COP 57,8 mil", [t])
    assert errs and "a la mitad" in errs[0]
    errs, _ = evidence.verbal_ratio_issues("Los clientes se multiplicaron por cuatro: de 377 a 1.678", [t])
    assert errs == []                                                                       # ×4.45 is "por cuatro"
    errs, warns = evidence.verbal_ratio_issues("Las altas se duplicaron", [])
    assert errs == [] and warns                                                             # nothing to check it against


def test_story_package_rejects_a_headline_the_data_does_not_support(case):
    f, t = _accepted_evidence(case)
    errors, _ = story.validate_package(case, _package(f, t, headline="El monto de entrada cayó a la mitad"))
    assert any("a la mitad" in e for e in errors)                                          # 120,5 → 74,7 is ×0.62


def test_storyteller_run_is_confined_to_its_deck(tmp_path):
    deck = tmp_path / "deck"
    deck.mkdir()
    denied = []

    async def on_deny(msg):
        denied.append(msg)
    guard = storyteller._guard(deck, on_deny)
    renderer = storyteller.renderer_dir() / "scripts" / "render.mjs"

    async def check():
        return [type(await guard(tool, inp, None)).__name__ for tool, inp in [
            ("Write", {"file_path": str(deck / "slides" / "01.html")}),
            ("Write", {"file_path": str(tmp_path / "fuera.txt")}),
            ("Bash", {"command": f'node "{renderer}" "{deck}"'}),
            ("Bash", {"command": "node -e \"require('fs').writeFileSync('/tmp/x', '')\""}),
            ("Bash", {"command": f'rm -rf "{deck}"'}),
            ("WebFetch", {"url": "https://example.com"})]]
    assert asyncio.run(check()) == ["PermissionResultAllow", "PermissionResultDeny", "PermissionResultAllow",
                                    "PermissionResultDeny", "PermissionResultDeny", "PermissionResultDeny"]
    assert len(denied) == 4                                                                 # every denial is reported



def test_a_multiple_written_next_to_its_backed_figures_is_backed():
    from caseos.evidence import unsupported_numbers
    t = {"columns": ["mes", "clientes", "mrr"], "rows": [["ene-22", 377, 35.0e6], ["oct-24", 1678, 97.0e6]]}
    text = "Los clientes pasan de 377 a 1.678 (4,5×) y el MRR pagado de COP 35,0 millones a COP 97,0 millones (2,8×)."
    assert unsupported_numbers(text, [t]) == []
    assert unsupported_numbers("Los clientes pasan de 377 a 1.678 (5,2×).", [t]) == ["5,2×"]        # a wrong multiple still fails
    assert unsupported_numbers("Crecieron 3,1×.", [t]) == ["3,1×"]                                    # no figures next to it: not backed
    t2 = {"columns": ["mes", "mrr_por_cliente"], "rows": [["ene-22", 92.8e3], ["oct-24", 57.8e3]]}
    assert unsupported_numbers("Baja de COP 92,8 mil a COP 57,8 mil (−38%).", [t2]) == []


def test_the_case_statement_figures_are_an_example_not_unsupported_data(case):
    b = case.read_data("brief/brief.yaml", {}) or {}
    case.write_data("brief/brief.yaml", {**b, "brief_text": "Si un cliente pagaba 100 y ahora paga 80, ¿contrajo 20 o recibió un descuento?"})
    f, t = _accepted_evidence(case)
    q = "Si un cliente pagaba 100 y ahora paga 80, ¿contrajo 20 o recibió un descuento?"
    ok = _package(f, t, key="cfo", question=q, headline="Pagar 80 con la lista en 100 es un descuento de 20",
                  answer="Si la lista sigue en 100, los 20 son descuento nuevo; si bajó la lista, es contracción.")
    errors, _ = story.validate_package(case, ok)
    assert not any("cifra" in e for e in errors)                       # the question's own figures, used as its example
    bad = _package(f, t, key="cfo", question=q, headline="Pagar 80 con la lista en 100 es un descuento de 20",
                   answer="En Finora, 45 clientes están en ese caso.")
    errors, _ = story.validate_package(case, bad)
    assert any("45" in e for e in errors)                               # anything else still needs a table
    loose = _package(f, t, key="cfo", question="¿Qué pasó con 100 clientes?", headline="Pagar 80 es un descuento",
                     answer="De 100 a 80.")
    errors, _ = story.validate_package(case, loose)
    assert any("cifra" in e for e in errors)                            # only figures the statement poses, not any the COS writes


def test_a_step_label_is_not_a_figure():
    assert evidence.numbers_in("El paso 1 ya se hizo con los pagos; en el caso 2 cambia la lista") == []
    assert [n.value for n in evidence.numbers_in("Pasan 1.476 altas en 2 pasos")] == [1476.0, 2.0]    # counts still count


def test_a_claim_edit_hugo_asked_for_in_the_chat_does_not_accept_it_for_him(case):
    from caseos import actions
    f, t = _accepted_evidence(case)
    story.apply_package(case, _package(f, t, key="entry"), actor="cos")
    cid = case.read_data("story/package.yaml")["claims"][0]["claim_id"]
    chart = case.create("finding", {"headline": "MRR por cliente activo", "visual": {"tipo": "linea", "x": ["ene-22"], "series": []},
                                    "links": [t["id"]]}, actor="analytics")
    out = actions.run(case, cid, "update_story", {"visual_finding": chart["id"], "visual_intent": "Línea en COP",
                                                   "via": "vía Claude (Hugo lo pidió en el chat)"})
    c = case.get(cid)
    assert c["visual_finding"] == chart["id"] and (c.get("review") or {}).get("state") != "accepted"   # still his to accept
    assert case.read_data("story/package.yaml")["claims"][0]["visual_finding"] == chart["id"] and out["validation"]
    with pytest.raises(StoreError):
        actions.run(case, cid, "update_story", {"visual_finding": f["id"], "via": "vía Claude"})         # no chart, no swap
