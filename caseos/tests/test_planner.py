"""Plan desde el guion: each question of Hugo's storyline guide becomes a task with what comes out, a starting answer
built from the case context and his own words, and steps that name real tables — all guarded before it becomes a
proposal. Specialists can query the data model read-only, and a citation of the model counts only if its query ran."""
import asyncio

from caseos import config, llm, research, shaping
from caseos.agents import planner
from caseos.util import append_jsonl, now_iso


class FakeJob:
    def __init__(self, case_id, agent="framer"):
        self.case_id, self.agent = case_id, agent

    async def event(self, kind, data=None):
        pass


def _guion(case):
    shaping.propose(case, "guion:S1", {"title": "Growth", "slides": [
        {"title": "Entradas por segmento", "question": "¿Dónde se concentra la pérdida de crecimiento?"},
        {"title": "Funnel no lineal", "question": "¿Cómo definir el funnel si no todos lo recorren igual?"}]})


def _task(**k):
    base = {"id": "", "slides": ["S1.2"], "question": "¿Cómo definir el funnel si no todos lo recorren igual?", "work": "propuesta",
            "kind": "measurement", "intensity": "L2", "draft_answer": "", "hugo_said": [], "steps": [], "why": "", "links": []}
    return {**base, **k}


def _run(case, out):
    pid = f"P-test-{now_iso()}"
    append_jsonl(case.root / shaping.PLAN_RUNS, {"plan_id": pid, "ts": now_iso(), "status": "pending"})
    llm.set_llm(llm.FakeLLM({"framer": lambda spec: out}))
    try:
        return asyncio.run(planner._job(FakeJob(case.id), {"plan_id": pid})), llm
    finally:
        llm.set_llm(None)


def test_the_guion_becomes_tasks_with_a_starting_answer_and_real_steps(case, monkeypatch):
    monkeypatch.setattr(shaping, "model_tables", lambda store: {"mart.new_customers", "mart.customer_month"})
    n = case.create("note", {"kind": "USER_INTUITION", "text": "El funnel se segmenta por punto de entrada",
                             "hugo_wording": "No todos entran igual: hay Assisted, Self Service y Executive, hay que segmentar por punto de entrada"},
                    actor="framer")
    para = case.create("note", {"kind": "OBSERVATION", "text": "Detectaste que no todos recorren el proceso igual",
                                "hugo_wording": "Detectaste que no todos recorren el proceso igual", "verbatim": False}, actor="import")
    _guion(case)
    shaping.propose(case, "plan:RT-001", {"question": "¿Qué información falta para contestar al CRO?", "kind": "research"})
    out = {"summary": "Dos preguntas del guion, dos tareas.", "not_planned": [{"slides": ["S1.1"], "why": "contexto"}], "tasks": [
        _task(draft_answer="Todo depende del punto de entrada: hay que segmentar por puerta y medir cada una en su orden.",
              hugo_said=[{"text": "hay que segmentar por punto de entrada", "ref": n["id"]},
                         {"text": "no todos recorren el proceso igual", "ref": para["id"]}],
              steps=[{"kind": "data", "what": "Ver si algo distingue la puerta de entrada; no hay canal, proxy: ticket de entrada",
                      "where": ["mart.new_customers", "mart.inventada"]},
                     {"kind": "proposal", "what": "Definición del funnel por puerta y sus métricas", "where": []}],
              links=[n["id"], "H-999"]),
        _task(slides=["S9.9", "S1.1"], question="¿Dónde se concentra la pérdida de crecimiento?", work="datos", kind="data",
              intensity="auto", draft_answer="Probablemente en industrias de ticket bajo, que ya son 42% de las altas.",
              hugo_said=[{"text": "el churn es culpa del precio", "ref": n["id"]}],
              steps=[{"kind": "data", "what": "Altas y bajas por industria", "where": ["mart.customer_month"]}])]}
    (res, _) = _run(case, out)
    assert res["superseded"] == ["RT-001"] and res["proposed"] == ["RT-002", "RT-003"]
    fr = case.read_data("framing/current.yaml")
    t2, t3 = fr["pending"]["plan:RT-002"]["value"], fr["pending"]["plan:RT-003"]["value"]
    assert t2["work"] == "propuesta" and t2["agent"] == "measurement" and t2["draft_answer"].startswith("Todo depende del punto de entrada")
    assert t2["hugo_said"] == [{"text": "hay que segmentar por punto de entrada", "ref": n["id"]}]      # his words, verbatim, with the ID
    assert t2["steps"][0]["where"] == ["mart.new_customers"] and t2["links"] == [n["id"]]             # invented table and ID dropped
    assert t3["hugo_said"] == [] and t3["slides"] == ["S1.1"]                                          # a quote he never said is removed
    assert any("42%" in f for f in t3["flags"])                                                        # a number with no source is flagged
    notes = " ".join(res["corrections"])
    assert "mart.inventada" in notes and "no coincide" in notes and "S9.9" in notes and "paráfrasis" in notes
    run = shaping.state(case)["plan_run"]
    assert run["status"] == "done" and run["summary"] and run["not_planned"][0]["slides"] == ["S1.1"]
    assert {x["id"] for x in shaping.state(case)["slide_tasks"]["S1.2"]} == {"RT-002"}
    assert "RT-001" in fr["retired_ids"]                                                               # ids are never reused


def test_a_launched_task_takes_its_starting_answer_and_the_model_to_the_specialist(case, monkeypatch):
    monkeypatch.setattr(config, "AUTO_COS", False)
    monkeypatch.setattr(research, "launch_job", lambda store, rid: type("J", (), {"id": "JOB-x"})())
    _guion(case)

    class Model:
        id = "fake"

        def catalog(self):
            return {"tables": []}

        def query(self, sql, limit=200):
            return {"columns": ["n"], "rows": [[1]], "truncated": False, "ms": 1, "sql": sql}

    monkeypatch.setattr(shaping, "data_model", lambda store: Model())
    shaping.set_section(case, "plan:new", _task(draft_answer="Depende del punto de entrada.", steps=[
        {"kind": "data", "what": "Qué distingue la puerta de entrada", "where": []}, {"kind": "proposal", "what": "Funnel por puerta", "where": []}]))
    rid = shaping.send_task(case, "RT-001")["research_id"]
    assert case.get(rid)["task"]["draft_answer"] == "Depende del punto de entrada."
    seen = {}

    def respond(spec):
        seen["spec"] = spec
        from tests.test_research import _result
        out = _result("H-000")
        out["sources"].append({"id": "S3", "title": "Altas por mes", "url": "", "publisher": "modelo", "date": "", "source_type": "data_model",
                               "quality": "A", "note": "SELECT COUNT(*) AS n FROM mart.new_customers"})
        out["claims"].append({"claim": "1 alta", "source_id": "S3", "source_type": "data_model", "confidence": "high", "freshness": "",
                              "supports_or_contests": "supports", "notes": ""})
        out["__sql_runs"] = ["SELECT COUNT(*) AS n\n FROM mart.new_customers;"]
        return out
    llm.set_llm(llm.FakeLLM({"measurement": respond}))
    try:
        asyncio.run(research._research_job(FakeJob(case.id, "measurement"), {"research_id": rid}))
    finally:
        llm.set_llm(None)
    spec = seen["spec"]
    assert spec.data_model is not None and "consultar_modelo" in spec.prompt and "Respuesta de arranque" in spec.prompt
    done = case.get(rid)
    assert "S3" not in done["validation"]["unverified_sources"] and done["sql_runs"]               # the query ran: the citation counts


def test_a_model_citation_counts_only_if_its_query_ran():
    out = {"_seen_urls": [], "_sql_runs": ["SELECT 1"],
           "sources": [{"id": "D1", "source_type": "data_model", "url": "", "note": "select 1;"},
                       {"id": "D2", "source_type": "data_model", "url": "", "note": "SELECT COUNT(*) FROM mart.x"}],
           "claims": [{"claim": "a", "source_id": "D1", "confidence": "high"}, {"claim": "b", "source_id": "D2", "confidence": "high"}]}
    v = research.verify_citations(out)
    assert v["unverified_sources"] == ["D2"] and out["claims"][1]["confidence"] == "low" and not out["claims"][0].get("unverified")


def test_data_tools_are_read_only_and_log_what_ran():
    class Model:
        def query(self, sql, limit=200):
            if not sql.lower().startswith("select"):
                raise ValueError("Solo consultas SELECT: el modelo es de solo lectura.")
            return {"columns": ["n"], "rows": [[5]], "truncated": False, "ms": 2, "sql": sql}

        def catalog(self):
            return {"tables": [{"id": "mart.x", "grain": "mes", "rows": 5, "desc": "d", "columns": [{"name": "n", "definition": "altas"}]}]}
    log = []
    tools = llm.data_tool_handlers(Model(), log)
    bad = asyncio.run(tools["consultar_modelo"]({"sql": "DELETE FROM mart.x"}))
    ok = asyncio.run(tools["consultar_modelo"]({"sql": "SELECT n FROM mart.x"}))
    cat = asyncio.run(tools["catalogo_modelo"]({}))
    assert bad["is_error"] and "solo lectura" in bad["content"][0]["text"] and log == ["SELECT n FROM mart.x"]
    assert '"rows": [[5]]' in ok["content"][0]["text"] and "mart.x" in cat["content"][0]["text"]


def test_a_new_plan_can_improve_an_approved_task_but_not_a_launched_one(case, monkeypatch):
    monkeypatch.setattr(shaping, "model_tables", lambda store: {"mart.new_customers"})
    monkeypatch.setattr(research, "launch_job", lambda store, rid: type("J", (), {"id": "JOB-x"})())
    _guion(case)
    shaping.set_section(case, "plan:new", _task(question="¿Cómo definir el funnel?"))                       # RT-001 approved
    shaping.set_section(case, "plan:new", _task(question="¿Qué pasa con las altas?", kind="research"))     # RT-002 → launched
    shaping.send_task(case, "RT-002")
    shaping.propose(case, "plan:RT-001", _task(question="¿Cómo definir el funnel? (cambio viejo)"))
    out = {"summary": "", "not_planned": [], "tasks": [
        _task(id="RT-001", draft_answer="Depende del punto de entrada.", steps=[{"kind": "proposal", "what": "Funnel por puerta", "where": []}]),
        _task(id="RT-002", question="¿Qué pasa con las altas? (otra vez)")]}
    (res, _) = _run(case, out)
    fr = case.read_data("framing/current.yaml")
    assert res["proposed"] == ["RT-001"] and fr["pending"]["plan:RT-001"]["revises"]                       # a change, waiting for Hugo
    assert fr["research_plan"][0]["draft_answer"] == ""                                                    # the approved task is untouched
    assert "RT-002" in " ".join(res["corrections"]) and "plan:RT-002" not in fr["pending"]
    assert "RT-001" not in (fr.get("retired_ids") or [])                                                   # an approved id is not retired
