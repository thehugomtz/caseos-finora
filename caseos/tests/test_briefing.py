"""Briefing with the Briefer (scripted runtime): a blank case, proposals that never overwrite what Hugo approved, the
statement stored verbatim by code, section-by-section approval and the Mark Ready gate."""
import asyncio

import pytest

from caseos import briefing, cases, llm, phases
from caseos.agents import briefer
from caseos.util import append_jsonl, now_iso


class FakeJob:
    def __init__(self, case_id):
        self.case_id, self.agent = case_id, "briefer"

    async def event(self, kind, data=None):
        pass


LANG = {"register": "directo", "technical_level": "business", "formality": "tú", "preserved_terms": ["peloncito"],
        "introduced_terms": []}


def _turn(case, message, out):
    llm.set_llm(llm.FakeLLM({"briefer": lambda spec: out}))
    tid = f"B-test-{len(briefer.conversation(case))}"
    append_jsonl(case.root / briefer.CONV, {"turn_id": tid, "ts": now_iso(), "message": message, "status": "pending"})
    try:
        asyncio.run(briefer._job(FakeJob(case.id), {"turn_id": tid}))
    finally:
        llm.set_llm(None)
    return briefer.conversation(case)[-1]


def _p(section, value, basis="hugo", hugo_wording="", why=""):
    return {"section": section, "value": value, "hugo_wording": hugo_wording, "basis": basis, "why": why}


@pytest.fixture()
def blank(cases_root):
    return cases.create_case(name="Finora reencuadre", case_id="blank")


def test_blank_case_starts_with_only_its_name(blank):
    v = briefing.view(blank)
    states = {s["key"]: s["state"] for s in v["sections"]}
    assert states["title"] == "approved" and states["objective"] == "empty"
    r = phases.readiness(blank, "briefing")
    assert not r["ok"] and any("objetivo" in b for b in r["blockers"])


def test_briefer_proposes_and_hugo_approves_section_by_section(blank):
    msg = "Quiero probar esto peloncito: que el CFO entienda si la caída es precio o mezcla. Entrego un video de 5 min."
    rec = _turn(blank, msg, {
        "reply": "Anoté objetivo, audiencia y entregable. ¿Hay algo que no debamos tocar?", "question": "¿Algo fuera de alcance?",
        "proposals": [_p("objective", ["Que el CFO entienda si la caída del monto por cliente es precio o mezcla."], hugo_wording=msg),
                      _p("audience", ["CFO — decide si es precio, mezcla o medición"]),
                      _p("deliverables", ["Video ejecutivo ≤ 5 min"]),
                      _p("timeline", ["Dos semanas"], basis="inferido"),
                      _p("brief_text", ["texto inventado por el modelo"]),          # never from the model
                      _p("audience", ["duplicado"])],
        "message_is_source_text": False, "language": LANG})
    assert rec["status"] == "done" and set(rec["proposed"]) == {"objective", "audience", "deliverables", "timeline"}
    assert any("Inferido" in c for c in rec["corrections"])
    b = briefing.get(blank)
    assert b["objective"] == "" and b["pending"]["objective"]["hugo_wording"] == msg      # nothing approved by the agent
    assert "brief_text" not in b["pending"]
    for k in ("objective", "audience", "deliverables"):
        briefing.approve(blank, k)
    briefing.discard(blank, "timeline")
    b = briefing.get(blank)
    assert b["audience"] == ["CFO — decide si es precio, mezcla o medición"] and not b["pending"]
    assert b["sections"]["objective"]["state"] == "approved" and b["sections"]["objective"]["by"] == "hugo"
    assert phases.readiness(blank, "briefing")["ok"]
    with pytest.raises(ValueError):
        briefing.approve(blank, "objective", actor="briefer")                               # only Hugo approves


def test_reframe_is_a_revision_not_an_overwrite(blank):
    briefing.set_section(blank, "objective", "Entender la caída del ingreso por cliente.")
    _turn(blank, "Reencuadro: más bien quiero separar lo que podemos afirmar de lo que sigue siendo posibilidad.", {
        "reply": "Te propongo el objetivo nuevo.", "question": "", "message_is_source_text": False, "language": LANG,
        "proposals": [_p("objective", ["Separar lo que podemos afirmar ante el CFO de lo que sigue siendo posibilidad."],
                         why="Reencuadre de Hugo: de entender la caída a separar afirmable de posible.")]})
    b = briefing.get(blank)
    assert b["objective"] == "Entender la caída del ingreso por cliente."                  # approved stays until Hugo decides
    assert b["pending"]["objective"]["revises"] is True
    briefing.approve(blank, "objective")
    assert briefing.get(blank)["objective"].startswith("Separar lo que podemos afirmar")
    assert briefing.get(blank)["sections"]["objective"]["version"] == 2


def test_pasted_statement_is_stored_verbatim_by_code(blank):
    statement = "Finora es un SaaS para PyMEs.\nEl CRO dice que entran más leads pero no crecen los clientes nuevos."
    _turn(blank, statement, {"reply": "Guardé el enunciado.", "question": "", "message_is_source_text": True, "language": LANG,
                             "proposals": [_p("context", ["SaaS para PyMEs; el CRO ve más leads sin más clientes nuevos."], basis="enunciado")]})
    b = briefing.get(blank)
    assert b["pending"]["brief_text"]["value"] == statement and b["pending"]["brief_text"]["basis"] == "enunciado"
    assert b["pending"]["context"]["basis"] == "enunciado"


def test_editing_an_approved_brief_sends_it_back_to_review(blank):
    for k, v in (("objective", "x"), ("audience", ["CFO"]), ("deliverables", ["Deck"])):
        briefing.set_section(blank, k, v)
    phases.mark_ready(blank, "briefing", actor="hugo")
    briefing.set_section(blank, "constraints", ["Sin datos de funnel"])
    assert blank.meta()["phases"]["briefing"]["status"] == "needs_review"
    assert "Sin datos de funnel" in blank.read_text("brief/brief.md")
