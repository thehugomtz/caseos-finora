"""Research Hub: routing by specialty and intensity, the case-purpose check, citation discipline, and a specialist run
(scripted runtime) that persists proposed findings with lineage."""
import asyncio

from caseos import config, llm, research


class FakeJob:
    def __init__(self, case_id, agent):
        self.case_id, self.agent = case_id, agent

    async def event(self, kind, data=None):
        pass


def test_routing_by_intensity_and_specialty(case):
    r = research.heuristic_route(case, "¿Qué significa NRR?")
    assert (r["specialty"], r["intensity"]) == ("business", "L1")
    r = research.heuristic_route(case, "¿Qué eventos y métricas necesitamos para medir el funnel sin forzar un embudo lineal?")
    assert r["specialty"] == "measurement" and r["intensity"] == "L2"
    r = research.heuristic_route(case, "¿Cuál sería el modelo de datos y el grano para separar suscripción, tarifa y descuento?")
    assert r["specialty"] == "data_engineering"
    r = research.heuristic_route(case, "Investiga a fondo qué estrategia de pricing con descuentos temporales hace más sentido "
                                       "para decidir bajo tres escenarios")
    assert (r["specialty"], r["intensity"]) == ("business", "L3")


def test_analytics_route_requires_a_workspace(case):
    q = "¿Cuánto cayó el monto por cliente por industria en Transactions?"
    assert research.heuristic_route(case, q)["specialty"] != "analytics"
    meta = case.meta()
    meta["workspace"] = {"type": "finora-eda"}
    case.save_meta(meta)
    r = research.heuristic_route(case, q)
    assert (r["specialty"], r["intensity"]) == ("analytics", "analytics")


def test_research_without_case_purpose_waits_for_hugo(case):
    out = research.create_request(case, "¿Cuál es la capital de Australia y qué clima tiene?", launch=True)
    assert out["launched"] is False and out["research"]["status"] == "draft"
    assert any("WITHOUT CASE PURPOSE" in a["summary"] for a in case.activity())


def test_citations_must_come_from_retrieved_urls():
    out = {"_seen_urls": ["https://www.example.org/report-2025"],
           "sources": [{"id": "S1", "url": "https://example.org/report-2025/", "source_type": "industry"},
                       {"id": "S2", "url": "https://invented.example.com/paper", "source_type": "academic"}],
           "claims": [{"claim": "a", "source_id": "S1", "confidence": "high"},
                      {"claim": "b", "source_id": "S2", "confidence": "high"},
                      {"claim": "c", "source_id": "", "confidence": "medium"}]}
    v = research.verify_citations(out)
    assert v["unverified_sources"] == ["S2"] and not v["ok"]
    assert not out["claims"][0].get("unverified")
    assert out["claims"][1]["unverified"] and out["claims"][1]["confidence"] == "low"
    assert out["claims"][2]["unverified"]


def _result(h_id):
    src = lambda i, url, t: {"id": i, "title": f"Fuente {i}", "url": url, "publisher": "p", "date": "2025", "source_type": t,
                             "quality": "B", "note": ""}
    claim = lambda text, sid: {"claim": text, "source_id": sid, "source_type": "industry", "confidence": "high", "freshness": "2025",
                               "supports_or_contests": "supports", "notes": ""}
    return {
        "research_question": "q", "case_question": "", "why_it_matters": "", "short_answer": "Los descuentos de entrada son comunes.",
        "findings": [{"headline": "Los descuentos de entrada son práctica común en SaaS B2B", "evidence": "…", "claim_indexes": [0],
                      "confidence": "medium", "limitation": "Contexto externo, no evidencia de esta empresa"},
                     {"headline": "Un estudio atribuye 30% de caída de ticket a descuentos", "evidence": "…", "claim_indexes": [1],
                      "confidence": "high", "limitation": ""}],
        "claims": [claim("Descuentos de entrada comunes", "S1"), claim("30% de caída", "S2")],
        "sources": [src("S1", "https://good.example.org/a", "industry"), src("S2", "https://made-up.example.net/x", "academic")],
        "alternative_explanations": [], "what_is_established": [], "what_is_contested": [], "what_remains_unknown": [],
        "case_implication": "", "changes_current_story": {"value": "maybe", "why": ""},
        "affected_hypotheses": [{"id": h_id, "effect": "supports", "why": ""}, {"id": "H-999", "effect": "weakens", "why": ""}],
        "affected_claims": [], "suggested_action": "", "new_questions": [],
        "handoff_to_cos": {"summary": "", "recommended_next": ""},
        "confidence_buckets": {"high_confidence": [], "plausible": [], "contested": [], "unknown": []},
        "__seen_urls": ["https://good.example.org/a"],
    }


def test_specialist_run_persists_proposed_findings_with_lineage(case, monkeypatch):
    monkeypatch.setattr(config, "AUTO_COS", False)
    h = case.create("hypothesis", {"statement": "Los descuentos de entrada bajan el ticket", "falsifier": "…", "status": "open"},
                    actor="framer")
    r = research.create_request(case, "¿Qué dicen los benchmarks de SaaS B2B sobre descuentos de entrada y el ticket?",
                                links=[h["id"]], route={"specialty": "business", "intensity": "L2"}, launch=False)["research"]
    assert r["route"]["source"] == "hugo"                                           # Hugo's route skips the router agent
    llm.set_llm(llm.FakeLLM({"business_research": lambda spec: _result(h["id"])}))
    try:
        asyncio.run(research._research_job(FakeJob(case.id, "business_research"), {"research_id": r["id"]}))
    finally:
        llm.set_llm(None)
    done = case.get(r["id"])
    assert done["status"] == "completed" and done["review"]["state"] == "proposed"   # nothing is accepted by an agent
    assert done["validation"]["unverified_sources"] == ["S2"]
    f1, f2 = (case.get(i) for i in done["findings"])
    assert f1["links"][0] == r["id"] and h["id"] in f1["links"] and "H-999" not in f1["links"]
    assert f2["unverified"] and f2["confidence"] == "low"                          # invented citation → low confidence
    research.accept(case, r["id"], note="ok")
    assert case.get(f1["id"])["review"]["state"] == "accepted"
