"""Framer with a scripted runtime: messy text → classified items, epistemic guards, Hugo's words preserved, language
discipline. The real model is exercised in tests/test_live.py (opt-in: CASEOS_LIVE=1)."""
import asyncio

from caseos import language, llm
from caseos.agents import framer
from caseos.util import append_jsonl, now_iso


class FakeJob:
    def __init__(self, case_id, agent="framer"):
        self.case_id, self.agent, self.events = case_id, agent, []

    async def event(self, kind, data=None):
        self.events.append(kind)


MESSY = ("Creo que están metiendo más leads pero esa madre no está convirtiendo. El MRR por cliente cayó 20%. "
         "Hay que decidir si cortamos los descuentos. ¿Cuánto pesa la mezcla de clientes nuevos?")


def _item(**k):
    return {"kind": "OBSERVATION", "structured": "", "hugo_wording": "", "basis": "", "confidence": "n/a", "falsifier": "",
            "links": [], "updates": "", **k}


def _turn(existing_note: str) -> dict:
    return {
        "reply": "Lo separo en tres: tu lectura del funnel, el dato del MRR y una decisión pendiente. ¿El 20% lo viste en los pagos?",
        "items": [
            _item(kind="FACT", structured="El MRR por cliente cayó 20%.", hugo_wording="El MRR por cliente cayó 20%."),  # no basis
            _item(kind="USER_INTUITION", structured="Entra más volumen arriba del funnel que no se convierte.",
                  hugo_wording="Creo que están metiendo más leads pero esa madre no está convirtiendo.", updates=existing_note),
            _item(kind="HYPOTHESIS", structured="La caída del promedio es mezcla de nuevos, no precio.",
                  falsifier="Se debilita si los clientes antiguos también bajan su monto."),
            _item(kind="HYPOTHESIS", structured="Los descuentos explican la caída."),                                   # no falsifier
            _item(kind="QUESTION", structured="¿Cuánto pesa la mezcla de clientes nuevos en el promedio?",
                  hugo_wording="¿Cuánto pesa la mezcla de clientes nuevos?"),
            _item(kind="DECISION", structured="Cortar los descuentos temporales.",
                  hugo_wording="Hay que decidir si cortamos los descuentos."),
            _item(kind="FACT", structured="El caso habla de introducir descuentos.", basis="brief"),
            _item(kind="ASSUMPTION", structured="Los montos están en la misma moneda.", links=["H-999"], updates="N-999"),
        ],
        "framing_patch": {"executive_question": "¿Por qué cae el ingreso por cliente?", "candidate_frames": [],
                          "problem": {"statement": "", "situation": "", "why_it_matters": "", "in_scope": [], "out_of_scope": []},
                          "storyline_guide": [],
                          "research_plan": [{"id": "", "question": "¿El monto de entrada bajó?", "kind": "data", "intensity": "auto",
                                             "why": "premisa", "links": [], "slides": []}],
                          "decisions_needed": ["Qué es adquirir un cliente"],
                          "should_not_claim": ["Que hubo descuentos en el histórico"], "language_notes": [], "risks": []},
        "advisors": [{"lens": l, "why": "", "contribution": ""} for l in ("cfo", "cro", "ceo")],
        "alternatives": [{"name": "A", "approach": "", "when_it_wins": "", "cost": ""}] * 2,
        "challenge": {"hidden_assumptions": ["x"], "strongest_counterargument": "y", "alternative_explanation": "",
                      "invalidating_evidence": [], "highest_risk_claim": ""},
        "language": {"register": "directo", "technical_level": "business", "formality": "tú",
                     "preserved_terms": ["MRR", "leads"],
                     "introduced_terms": [{"term": "mezcla", "plain": "el promedio baja porque cambia quién entra"}]},
        "next_steps": ["Confirmar el 20%"],
    }


def _run_turn(case, message, mode, out_fn):
    llm.set_llm(llm.FakeLLM({"framer": out_fn}))
    tid = f"T-test-{len(framer.conversation(case))}"
    append_jsonl(case.root / framer.CONV, {"turn_id": tid, "ts": now_iso(), "mode": mode, "message": message, "status": "pending"})
    try:
        res = asyncio.run(framer._job(FakeJob(case.id), {"turn_id": tid}))
    finally:
        llm.set_llm(None)
    return res, framer.conversation(case)[-1]


def test_messy_text_is_classified_guarded_and_keeps_hugo_words(case):
    old = case.create("note", {"kind": "USER_INTUITION", "text": "Entraron muchos leads no calificados",
                               "hugo_wording": "Tu lectura fue que creció una máquina de leads", "verbatim": False},
                      actor="import")
    res, rec = _run_turn(case, MESSY, "organize", lambda spec: _turn(old["id"]))
    ents = case.all()
    created = [ents[i] for i in res["created"]]
    assert rec["status"] == "done" and rec["error"] is None

    # FACT without basis is not a fact: Hugo said it, so it is his intuition until evidence exists
    unfounded = next(e for e in created if e.get("text") == "El MRR por cliente cayó 20%.")
    assert unfounded["kind"] == "USER_INTUITION" and unfounded["reclassified_from"] == "FACT"
    assert next(e for e in created if e.get("text") == "El caso habla de introducir descuentos.")["kind"] == "FACT"

    hyps = [e for e in created if e["type"] == "hypothesis"]
    assert any("sin_falsificador" in (h.get("flags") or []) for h in hyps)
    assert any(h.get("falsifier") for h in hyps)
    assert next(e for e in created if e["type"] == "decision")["status"] == "proposed"      # agents never decide
    q = next(e for e in created if e["type"] == "question")
    assert q["hugo_wording"] == "¿Cuánto pesa la mezcla de clientes nuevos?"                 # dual representation

    # a refined item keeps Hugo's earlier words visible
    n = case.get(old["id"])
    assert old["id"] in res["updated"]
    assert n["hugo_wording"].startswith("Creo que están metiendo")
    assert n["hugo_wording_history"][0]["text"].startswith("Tu lectura fue") and n["verbatim"] is True

    corrections = " ".join(rec["corrections"])
    assert "FACT" in corrections and "máx. 2" in corrections and "N-999" in corrections
    assert len(rec["advisors"]) == 2 and rec["alternatives"] == [] and rec["challenge"] is None

    fr = case.read_data("framing/current.yaml")
    assert fr["executive_question"] == "¿Por qué cae el ingreso por cliente?"
    task = fr["pending"]["plan:RT-001"]["value"]
    # a data task needs a data model: this case has none, so it becomes research and the turn says why
    assert task["question"] == "¿El monto de entrada bajó?" and task["kind"] == "research" and task["agent"] == "business"
    assert "modelo de datos" in corrections
    assert "Que hubo descuentos en el histórico" in fr["should_not_claim"]
    assert "MRR" in case.meta()["language"]["observed"]["preserved_terms"]
    assert "¿Por qué cae el ingreso por cliente?" in case.read_text("framing/current.md")
    assert rec["language_check"]["ok"]


def test_challenge_mode_keeps_the_challenge_block(case):
    def out(spec):
        o = _turn("")
        o["items"] = []
        return o
    _, rec = _run_turn(case, "Intenta romper esto.", "challenge", out)
    assert rec["challenge"]["strongest_counterargument"] == "y"
    assert len(rec["alternatives"]) == 2


def test_fact_needs_accepted_evidence(case):
    f = case.create("finding", {"headline": "El monto de entrada bajó"}, actor="analytics")
    item = {"kind": "FACT", "structured": "Bajó el monto de entrada", "basis": f"evidence:{f['id']}", "hugo_wording": "",
            "links": [], "updates": ""}
    cleaned, notes = framer.guard({"items": [dict(item)]}, "organize", case.all())
    assert cleaned["items"][0]["kind"] == "OBSERVATION" and notes
    case.set_review(f["id"], "accepted", actor="hugo")
    cleaned, notes = framer.guard({"items": [dict(item)]}, "organize", case.all())
    assert cleaned["items"][0]["kind"] == "FACT" and not notes


def test_mode_limits_on_alternatives():
    many = [{"name": str(i)} for i in range(5)]
    assert framer.guard({"items": [], "alternatives": list(many)}, "organize", {})[0]["alternatives"] == []
    assert len(framer.guard({"items": [], "alternatives": list(many)}, "advise", {})[0]["alternatives"]) == 3


# ------------------------------------------------------------------------------------------ language discipline
PROFILE = {"primary": "es", "observed": {"preserved_terms": ["MRR", "leads", "funnel"]}}


def test_performative_jargon_is_flagged():
    r = language.assess("Necesitamos decompose top-of-funnel throughput elasticity y ver la downstream conversion "
                        "degradation.", PROFILE, "")
    assert not r["ok"] and r["performative"]


def test_hugo_terms_and_explained_terms_are_fine():
    r = language.assess("Separemos dos cosas: cuántos leads entran y cuántos terminan pagando. El MRR por cliente lo vemos "
                        "aparte.", PROFILE, "")
    assert r["ok"] and r["unexplained"] == []
    r = language.assess("Veamos el payback (cuántos meses tarda un cliente en pagar lo que costó conseguirlo), la cohorte "
                        "(grupo que entró el mismo mes) y el LTV.", {"primary": "es"}, "¿cómo va el LTV?")
    assert r["ok"]


def test_english_reply_in_a_spanish_case_is_flagged():
    r = language.assess("We need to look at the numbers and the drivers of this change in the base.", {"primary": "es"}, "")
    assert not r["ok"]


def test_a_quote_of_this_turn_points_to_its_note_and_a_sent_task_is_not_rewritten(case):
    from caseos import shaping
    shaping.set_section(case, "plan:new", {"question": "¿Qué hipótesis ToFu y BoFu explican la brecha?", "kind": "measurement"})
    fr = case.read_data("framing/current.yaml")
    fr["research_plan"][0].update(status="sent", research_id="R-001")                   # already in Research
    case.write_data("framing/current.yaml", fr)
    words = "hay que generar más causas potenciales, por lo menos 3-5 más"

    def out(spec):
        o = _turn("")
        o["items"] = [_item(kind="USER_INTUITION", structured="Sumar causas a las cuatro del caso.", hugo_wording=words)]
        o["framing_patch"]["research_plan"] = [{"id": "RT-001", "question": "¿Qué otras causas explican la brecha?",
                                                "kind": "measurement", "intensity": "L2", "why": "", "links": ["#1"], "slides": [],
                                                "hugo_said": [{"text": words, "ref": "este turno"}]}]
        return o
    res, rec = _run_turn(case, f"Faltan 2 cosas: {words} y qué datos las validan", "challenge", out)
    pend = case.read_data("framing/current.yaml")["pending"]
    assert "plan:RT-001" not in pend                                                     # the researched task is not rewritten…
    task = pend["plan:RT-002"]["value"]                                                  # …the new version is new work
    assert task["why"].startswith("Reformula RT-001")
    assert task["hugo_said"] == [{"text": words, "ref": res["created"][0]}]              # his words, pointed to the note of this turn
    assert task["links"] == [res["created"][0]]                                          # "#1" = the first item of this turn
