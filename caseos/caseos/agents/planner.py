"""Plan desde el guion — the Framer turns the questions of Hugo's storyline guide into the research plan.

Hugo (29-sep): a question of the guion such as "¿cómo definirías el funnel si no todos lo recorren igual?" is already a
task of investigation and proposal; the case has enough context to put a first answer on the table. So each task
carries what comes out, a starting answer written from the case context and his own words, and the steps — with
"investigar datos en el modelo" naming real tables. One run: context → PlanTurn → shaping.guard_tasks → the unapproved
task proposals are superseded → new proposals wait for Hugo. Nothing is approved here.
"""
from __future__ import annotations

import uuid

from .. import cases, framing_doc, jobs, shaping, skills
from ..llm import AgentError, RunSpec, get_llm
from ..model import title_of
from ..store import CaseStore
from ..util import append_jsonl, clip, now_iso, read_jsonl, write_jsonl_replace
from . import base

RUNS = shaping.PLAN_RUNS
_S = {"type": "string"}
_SA = {"type": "array", "items": _S}


def _obj(props: dict) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


TASK = _obj({
    "id": _S,                                     # "" = new task · RT-### = improve an approved task not launched yet
    "slides": _SA, "question": _S,
    "work": {"type": "string", "enum": list(shaping.WORK)},
    "kind": {"type": "string", "enum": list(shaping.KINDS)},
    "intensity": {"type": "string", "enum": ["L1", "L2", "L3", "auto"]},
    "draft_answer": _S,
    "hugo_said": {"type": "array", "items": _obj({"text": _S, "ref": _S})},
    "steps": {"type": "array", "items": _obj({"kind": {"type": "string", "enum": list(shaping.STEP_KINDS)}, "what": _S, "where": _SA})},
    "why": _S, "links": _SA})
SCHEMA = _obj({"tasks": {"type": "array", "items": TASK},
               "not_planned": {"type": "array", "items": _obj({"slides": _SA, "why": _S})},
               "summary": _S})


# ------------------------------------------------------------------------------------------ context
def _guion_lines(fr: dict) -> list[str]:
    pend = fr.get("pending") or {}
    secs = [(s, False) for s in fr.get("storyline_guide") or []]
    ids = {s["id"] for s, _ in secs}
    secs += [(p["value"], True) for k, p in pend.items() if k.startswith("guion:") and k.split(":", 1)[1] not in ids]
    secs.sort(key=lambda x: shaping._num(x[0]["id"]))
    out = []
    for sec, proposed in secs:
        out.append(f"### {sec['id']} · {sec.get('title') or '—'}" + (" (propuesta, falta que Hugo la apruebe)" if proposed else ""))
        if sec.get("purpose"):
            out.append("Para qué: " + " · ".join(x.strip() for x in sec["purpose"].splitlines() if x.strip()))
        for sl in sec.get("slides") or []:
            out.append(f"- {sl['id']} · {sl.get('title') or '—'}" + (f" | pregunta: {sl['question']}" if sl.get("question") else "")
                       + (f" | debe mostrar: {clip(sl['intent'], 500)}" if sl.get("intent") and sl["intent"] != sl.get("title") else "")
                       + (f" | notas: {clip(sl['notes'], 200)}" if sl.get("notes") else ""))
    return out or ["(sin guion: no hay preguntas que planear)"]


def _catalog_lines(store: CaseStore) -> list[str]:
    m = shaping.data_model(store)
    if not m:
        return ["El caso no tiene modelo de datos: no propongas pasos de datos con tablas; di qué dato habría que pedir."]
    out = [f"{m.label} — solo existen estas tablas (raw = archivos tal cual · staging = tipado · mart = lo que consulta Analytics):"]
    for t in m.catalog()["tables"]:
        cols = ", ".join(c["name"] for c in t["columns"])
        out.append(f"- {t['id']} (grano {t.get('grain') or '—'}; {t['rows']} filas): {clip(t.get('desc', ''), 140)} Columnas: {clip(cols, 520)}")
    return out


def build_prompt(store: CaseStore) -> str:
    b = store.read_data("brief/brief.yaml", {}) or {}
    fr = store.read_data("framing/current.yaml", {}) or {}
    ents = store.all()
    pr = fr.get("problem") or ((fr.get("pending") or {}).get("problem") or {}).get("value") or {}
    live = [e for e in ents.values() if (e.get("review") or {}).get("state") != "rejected" and e.get("status") not in ("superseded", "reverted")]
    said = sorted([e for e in live if (e.get("hugo_wording") or "").strip() and e.get("type") in ("note", "hypothesis", "question", "decision")],
                  key=lambda e: e["id"])
    hyps = sorted([e for e in live if e.get("type") == "hypothesis"], key=lambda e: e["id"])
    qs = sorted([e for e in live if e.get("type") == "question" and e.get("status", "open") == "open"], key=lambda e: e["id"])
    research = sorted([e for e in ents.values() if e.get("type") == "research" and e.get("status") != "cancelled"], key=lambda e: e["id"])
    accepted = [e for e in ents.values() if e.get("type") == "finding" and (e.get("review") or {}).get("state") == "accepted"]
    done = [t for t in fr.get("research_plan") or []]
    lines = ["# Plan de investigación desde el guion", "",
             "## El caso (brief aprobado)",
             f"Objetivo: {clip(b.get('objective', ''), 600)}",
             "Audiencia: " + "; ".join(clip(str(x), 160) for x in b.get("audience") or []),
             f"Contexto del negocio: {clip(b.get('context', ''), 2400)}",
             "Entregables: " + "; ".join(clip(str(x), 220) for x in b.get("deliverables") or []),
             "Restricciones: " + "; ".join(clip(str(x), 200) for x in b.get("constraints") or []),
             "Datos disponibles: " + "; ".join(clip(str(x), 200) for x in b.get("data_available") or []),
             "Vacíos declarados: " + "; ".join(clip(str(x), 200) for x in b.get("gaps") or []),
             "", "## Problema" + ("" if fr.get("problem") else " (propuesto, sin aprobar)"),
             clip(pr.get("statement", ""), 500) or "—",
             ("Fuera del alcance: " + "; ".join(pr.get("out_of_scope") or [])) if pr.get("out_of_scope") else "",
             "", f"## Pregunta ejecutiva\n{fr.get('executive_question') or '—'}",
             "", "## Guion de la historia de Hugo (cada lámina es una pregunta)", *_guion_lines(fr),
             "", "## Lo que Hugo ya dijo (sus palabras textuales; cítalas con el ID)"]
    lines += [f"- {e['id']} [{e.get('kind') or e.get('type')}] “{clip(e['hugo_wording'], 420)}”"
              + (" (paráfrasis del Framer, no son sus palabras: úsala como contexto, no la cites)" if e.get("verbatim") is False else "")
              for e in said[-60:]] or ["(nada todavía)"]
    lines += ["", "## Hipótesis del caso"]
    lines += [f"- {e['id']} {clip(title_of(e), 240)}" + (f" · se debilita si: {clip(e['falsifier'], 160)}" if e.get("falsifier") else "")
              for e in hyps] or ["(ninguna)"]
    lines += ["", "## Preguntas abiertas"] + ([f"- {e['id']} {clip(title_of(e), 200)}" for e in qs[:40]] or ["(ninguna)"])
    lines += ["", "## Lo que ya se investigó (no lo repitas; úsalo)"]
    lines += [f"- {e['id']} [{e.get('status')}] {clip(e.get('research_question', ''), 160)}"
              + (f" → {clip(e['short_answer'], 260)}" if e.get("short_answer") else "") for e in research] or ["(nada)"]
    lines += ["", "## Evidencia aceptada"] + ([f"- {e['id']} {clip(title_of(e), 220)}" for e in accepted] or ["(ninguna todavía)"])
    lines += ["", "## Modelo de datos del caso", *_catalog_lines(store)]
    lines += ["", "## Tareas que Hugo ya aprobó (no las dupliques)"]
    lines += [f"- {t['id']} [{'lanzada a Research, no se toca' if t.get('status') == 'sent' else 'aprobada, sin lanzar'}] "
              f"{clip(t['question'], 200)} · láminas {', '.join(t.get('slides') or []) or '—'}"
              + ("" if t.get("draft_answer") or t.get("steps") else " · sin respuesta de arranque ni pasos") for t in done] or ["(ninguna)"]
    lines += ["", "## No afirmar todavía"] + ([f"- {x}" for x in fr.get("should_not_claim") or []] or ["—"])
    lines += ["", "## Qué te toca",
              "Convierte las preguntas del guion en el plan de investigación. Una pregunta como «¿cómo definirías el funnel si "
              "no todos lo recorren igual?» ya es una tarea de investigación y propuesta: con el contexto del caso (el modelo de "
              "negocio, lo que Hugo ya dijo) se puede poner sobre la mesa una respuesta de arranque y después probarla o corregirla.",
              "1. Una tarea por pregunta del guion que haya que trabajar; `slides` = los ids de sus láminas (S2.2). Si dos láminas "
              "preguntan lo mismo, júntalas. Una lámina de contexto o que ya tiene evidencia aceptada va en `not_planned` con el porqué.",
              "2. `work`: \"propuesta\" cuando la pregunta pide definir, diseñar, proponer o decidir (cómo medir, qué métricas, cómo "
              "introducir descuentos, qué modelo de datos): es la mayoría de un guion. \"datos\" cuando la respuesta sale del modelo "
              "de datos (dónde se concentra, cuánto, cuándo). \"research\" solo cuando la respuesta depende de información de afuera.",
              "3. `draft_answer`: lo que responderías HOY con el contexto, en 2–4 frases, en el registro de Hugo (tú, directo, sin "
              "jerga que él no use). Es una hipótesis de trabajo, no un hecho: ninguna cifra que no esté arriba; si algo no se sabe, "
              "dilo. Si Hugo ya lo dijo, parte de ahí y afínalo. Tono de ejemplo: «Todo depende del punto de entrada: no hay un "
              "funnel sino uno por puerta, y cada puerta se mide en su propio orden. Primero hay que poder decir por dónde entró "
              "cada cliente.»",
              "4. `hugo_said`: las palabras de Hugo en las que te apoyas, TEXTUALES y con el ID donde las dijo (de «Lo que Hugo "
              "ya dijo»). Vacío si no dijo nada al respecto. Nunca le atribuyas algo que no dijo.",
              "5. `steps` (1–4, en orden): data = qué buscar en el modelo y en qué tablas (`where`: SOLO ids del catálogo de arriba); "
              "si el dato no existe en el modelo, dilo y nombra el proxy que sí hay · research = qué buscar afuera y por qué, solo si "
              "hace falta · proposal = qué se entrega (la definición, las métricas, el mecanismo, el modelo). En un paso data que no "
              "usa tablas, `where` vacío.",
              "6. `kind` = el agente que la lidera: data → Analytics (respuesta con datos del modelo) · measurement → Measurement "
              "(funnels, métricas, eventos, definiciones) · data_model → Data Engineering (modelo de datos, campos, clasificación) · "
              "research → Business Research (mercado, prácticas, pricing). Los especialistas consultan el modelo de datos en solo "
              "lectura cuando la tarea trae pasos de datos.",
              "7. `intensity`: L1 consulta puntual · L2 normal · L3 a fondo; \"auto\" en tareas de datos.",
              "8. `links`: IDs H/Q/N de arriba a los que sirve. `why`: qué cambia en la historia según lo que salga (una frase).",
              "9. `id`: vacío para una tarea nueva. Si una tarea aprobada y sin lanzar ya cubre esa pregunta, no la dupliques: "
              "propón su versión mejorada con su id (RT-###) — Hugo decide si la cambia. Las lanzadas no se tocan.",
              "10. `summary`: 1–2 frases para Hugo sobre cómo quedó el plan."]
    return "\n".join(x for x in lines if x is not None)


# ------------------------------------------------------------------------------------------ runs
def start(store: CaseStore, *, actor: str = "hugo") -> dict:
    running = [r for r in runs(store) if r.get("status") in ("pending", "running")]
    if running:
        raise ValueError("Ya se está armando un plan; espera a que termine.")
    rec = {"plan_id": f"P{now_iso()[:19].replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:4]}", "ts": now_iso(),
           "status": "pending", "requested_by": actor}
    append_jsonl(store.root / RUNS, rec)
    store.log(actor, "requested", ["framing"], "Plan de investigación desde el guion pedido al Framer", material=False)
    try:
        job = jobs.submit(store.id, "shaping_plan", "Framer · plan desde el guion", {"plan_id": rec["plan_id"]}, agent="framer")
    except Exception as e:  # noqa: BLE001
        _patch(store, rec["plan_id"], {"status": "failed", "error": f"No se pudo lanzar: {e}"})
        raise
    _patch(store, rec["plan_id"], {"job_id": job.id})
    return {**rec, "job_id": job.id}


def runs(store: CaseStore, limit: int = 20) -> list[dict]:
    return read_jsonl(store.root / RUNS, limit=limit)


def _patch(store: CaseStore, plan_id: str, patch: dict) -> None:
    rows = read_jsonl(store.root / RUNS)
    for r in rows:
        if r.get("plan_id") == plan_id:
            r.update(patch)
    write_jsonl_replace(store.root / RUNS, rows)


def recover(store: CaseStore) -> int:
    rows = read_jsonl(store.root / RUNS)
    n = 0
    for r in rows:
        if r.get("status") in ("pending", "running") and r.get("job_id") not in jobs.LIVE:
            r.update({"status": "failed", "error": "El servidor se reinició antes de terminar el plan; vuelve a pedirlo."})
            n += 1
    if n:
        write_jsonl_replace(store.root / RUNS, rows)
    return n


def apply_plan(store: CaseStore, out: dict, *, context: str, run_id: str, plan_id: str) -> dict:
    fr = store.read_data("framing/current.yaml", {}) or cases.empty_framing()
    tasks, notes = shaping.guard_tasks(store, out.get("tasks") or [], fr, context=context)
    superseded = shaping.supersede_pending_tasks(fr)
    proposed = []
    approved = {x["id"]: x for x in fr.get("research_plan") or []}
    for t in tasks:
        oid = (t.get("id") or "").strip()
        if oid in approved and approved[oid].get("status") == "sent":
            notes.append(f"{oid} ya está en Research ({approved[oid].get('research_id')}): no se cambia; la propuesta se descartó.")
            continue
        tid = oid if oid in approved else shaping.next_task_id(fr)
        if shaping.propose(store, f"plan:{tid}", t, basis="plan desde el guion", why=t.get("why") or "", turn_id=run_id, fr=fr, save=False):
            proposed.append(tid)
    framing_doc.save(store, fr, actor="framer",
                     summary=f"Plan desde el guion: {len(proposed)} tarea(s) propuestas"
                             + (f"; reemplazan {len(superseded)} propuesta(s) sin aprobar ({', '.join(superseded)})" if superseded else ""),
                     material=bool(proposed or superseded))
    return {"proposed": proposed, "superseded": superseded, "corrections": notes}


@jobs.handler("shaping_plan")
async def _job(job, params):
    store = cases.get(job.case_id)
    plan_id = params["plan_id"]
    prompt = build_prompt(store)
    selected = skills.select("framer", mode="organize", text=prompt[-4000:], force=["research-routing"])
    system = base.system_prompt("framer", selected, store.meta().get("language"),
                                extra="En esta corrida no conversas con Hugo: armas el plan de investigación desde su guion "
                                      "(PlanTurn). Todo lo que propones espera su aprobación.")
    _patch(store, plan_id, {"status": "running", "skills": skills.record(selected), "started_at": now_iso()})
    await job.event("skills", {"skills": [s["id"] for s in skills.record(selected)]})
    # its own role: a whole plan is a bigger answer than a conversation turn (more output, its own spend cap)
    spec = RunSpec(agent="framer", role="planner", system=system, prompt=prompt, schema=SCHEMA, max_turns=4,
                   skills=skills.record(selected), purpose="Plan de investigación desde el guion", case_id=store.id,
                   case_root=store.root, timeout_s=2400)
    try:
        res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    except AgentError as e:
        _patch(store, plan_id, {"status": "failed", "error": str(e), "error_kind": e.kind, "finished_at": now_iso()})
        raise
    out = dict(res.output)
    applied = apply_plan(store, out, context=prompt, run_id=res.run_id, plan_id=plan_id)
    _patch(store, plan_id, {"status": "done", "finished_at": now_iso(), "run_id": res.run_id, "summary": out.get("summary", ""),
                            "not_planned": out.get("not_planned") or [], "cost_usd": res.cost_usd, "usage": res.usage, **applied})
    store.log("framer", "proposed", ["framing"], f"Framer propuso {len(applied['proposed'])} tarea(s) desde el guion"
              + (f" · {len(applied['corrections'])} corrección(es) de las guardas" if applied["corrections"] else ""),
              material=bool(applied["proposed"]), run_id=res.run_id)
    return {"plan_id": plan_id, **applied}
