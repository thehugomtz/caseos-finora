"""Research Hub: Router → specialists → case-research-synthesis → COS.

Root rule: do not research topics; research uncertainties that matter to the case. Every request maps to at least
one Q/H/D/C or is flagged RESEARCH WITHOUT CASE PURPOSE. Intensity L1 lookup · L2 business research · L3 deep
research (depth + breadth + counter → peer review → synthesis, orchestrated in code). Specialists: analytics (the
existing workspace), business research (web), measurement, data engineering. Every citation must be a URL actually
retrieved in the run (checked against the tool trace); unverified claims are downgraded, never silently kept.
"""
from __future__ import annotations

import asyncio
import re

from . import cases, config, cos, jobs, phases, skills
from .agents import base
from .llm import AgentError, RunSpec, get_llm
from .model import title_of, type_of
from .store import CaseStore
from .util import read_json, clip, norm, now_iso

SPECIALTIES = {"analytics": "Analytics", "business": "Business Research", "measurement": "Measurement",
               "data_engineering": "Data Engineering"}
AGENT_OF = {"business": "business_research", "measurement": "measurement", "data_engineering": "data_engineering",
            "analytics": "analytics"}
INTENSITY_LABELS = {"L1": "L1 · Lookup", "L2": "L2 · Business research", "L3": "L3 · Deep research"}

_KW = {
    "measurement": ["medir", "medicion", "medición", "measure", "kpi", "metrica", "métrica", "funnel", "embudo", "journey",
                    "atribucion", "atribución", "attribution", "instrument", "evento", "tracking", "north star",
                    "experiment", "cohort design", "diseño de cohortes", "velocity", "velocidad", "lifecycle", "ciclo de vida",
                    "sin forzar un funnel", "acquisition motion", "motions"],
    "data_engineering": ["modelo de datos", "modelar", "data model", "grano", "grain", "fact table", "tabla de hechos",
                         "dimension", "dimensión", "scd", "fuente de verdad", "source of truth", "schema", "esquema", "join",
                         "data contract", "contrato de datos", "billing", "facturacion", "facturación", "subscription value",
                         "amount paid", "clasificacion", "clasificación", "calidad de datos", "identidad", "vigencia",
                         "effective dated", "campos", "field"],
    "analytics": ["cuanto", "cuánto", "cuantos", "cuántos", "evolucion", "evolución", "tendencia", "por industria",
                  "por cohorte", "por cosecha", "en los datos", "dataset", "transactions", "grafica", "gráfica", "scatter",
                  "distribucion", "distribución", "segmento", "crecio", "creció", "cayo", "cayó", "bajo el", "bajó", "subio",
                  "subió", "monto", "ticket", "clientes activos", "churn observado", "puente", "concentra"],
    "business": ["benchmark", "mercado", "market", "competencia", "competidor", "competitor", "practica", "práctica",
                 "best practice", "que significa", "qué significa", "definicion", "definición", "framework", "approach",
                 "como lo hacen", "cómo lo hacen", "pricing", "politica", "política", "industria saas", "estandar", "estándar",
                 "literatura", "estudios", "casos de", "empresas"],
}
_L1 = re.compile(r"^\s*(¿\s*)?(que|qué|what|cual|cuál)\s+(significa|es|is|son|means)\b|^\s*(define|definición de|definicion de)\b|\bcómo se calcula\b|\bcomo se calcula\b", re.I)
_L3 = re.compile(r"\b(arquitectura|architecture|estrategi|qué hace más sentido|que hace mas sentido|decidir|decision|decisión|"
                 r"recomend|trade-?off|bajo (tres|varios|distintos)|material|profund|deep)\b", re.I)


# ------------------------------------------------------------------------------------------ heuristic router
def heuristic_route(store: CaseStore | None, question: str, links: list[str] | None = None) -> dict:
    q = question or ""
    qn = norm(q)
    scores = {k: sum(1 for w in ws if norm(w) in qn) for k, ws in _KW.items()}
    has_ws = bool(store and (store.meta().get("workspace") or {}).get("type") not in (None, "none"))
    if not has_ws:
        scores["analytics"] = 0
    specialty = max(scores, key=lambda k: (scores[k], {"business": 1, "measurement": 2, "data_engineering": 3, "analytics": 0}[k]))
    if scores[specialty] == 0:
        specialty = "business"
    if _L1.search(q) and len(q) < 120:
        intensity = "L1"
    elif _L3.search(q) or len(q) > 260:
        intensity = "L3"
    else:
        intensity = "L2"
    if specialty == "analytics":
        intensity = "analytics"
    agent = AGENT_OF[specialty]
    sel = skills.select(agent if agent != "analytics" else "business_research", intensity=intensity, text=q) if agent != "analytics" else []
    purpose = map_purpose(store, q, links) if store else {"mapped": [], "ok": False, "suggested": []}
    return {"specialty": specialty, "intensity": intensity, "agent": agent, "scores": scores,
            "skills": [{"id": x["skill"].id, "mode": x["mode"], "why": x.get("why", "")} for x in sel],
            "purpose": purpose, "source": "heuristic",
            "rationale": f"Palabras clave → {SPECIALTIES[specialty]}; intensidad {intensity}."}


def map_purpose(store: CaseStore, question: str, links: list[str] | None = None) -> dict:
    ents = store.all()
    explicit = [i for i in links or [] if i in ents and type_of(i) in ("question", "hypothesis", "decision", "claim")]
    qtok = {t for t in re.findall(r"[a-záéíóúñ]{4,}", norm(question))}
    scored = []
    for e in ents.values():
        if e.get("type") not in ("question", "hypothesis", "decision", "claim"):
            continue
        if (e.get("review") or {}).get("state") == "rejected":
            continue
        tt = {t for t in re.findall(r"[a-záéíóúñ]{4,}", norm(title_of(e) + " " + str(e.get("question", ""))))}
        ov = len(qtok & tt)
        if ov >= 3:
            scored.append((ov, e["id"]))
    suggested = [i for _, i in sorted(scored, reverse=True)[:4] if i not in explicit]
    ok = bool(explicit)
    return {"mapped": explicit, "suggested": suggested, "ok": ok,
            "note": "" if ok else ("RESEARCH WITHOUT CASE PURPOSE: enlázala a una Q/H/D/C o decide si vale la pena."
                                   + (f" Sugerencias: {', '.join(suggested)}." if suggested else ""))}


# ------------------------------------------------------------------------------------------ schemas
_S = {"type": "string"}
_SA = {"type": "array", "items": _S}


def _obj(props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


ROUTE_SCHEMA = _obj({"intensity": {"type": "string", "enum": ["L1", "L2", "L3", "analytics"]},
                     "specialty": {"type": "string", "enum": list(SPECIALTIES)}, "skills": _SA, "rationale": _S,
                     "reformulated_question": _S, "evidence_needed": _S,
                     "purpose": _obj({"mapped_ids": _SA, "ok": {"type": "boolean"}, "note": _S})})

SOURCE = _obj({"id": _S, "title": _S, "url": _S, "publisher": _S, "date": _S,
               "source_type": {"type": "string", "enum": ["primary", "official", "regulatory", "academic", "industry", "company",
                                                          "expert", "journalism", "community", "marketing", "internal",
                                                          "data_model"]},
               "quality": {"type": "string", "enum": ["A", "B", "C", "D"]}, "note": _S})
CLAIM = _obj({"claim": _S, "source_id": _S, "source_type": _S, "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
              "freshness": _S, "supports_or_contests": {"type": "string", "enum": ["supports", "contests", "context"]}, "notes": _S})
FINDING = _obj({"headline": _S, "evidence": _S, "claim_indexes": {"type": "array", "items": {"type": "integer"}},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]}, "limitation": _S})
EFFECT = _obj({"id": _S, "effect": {"type": "string", "enum": cos.EFFECTS}, "why": _S})

BASE_RESULT = {
    "research_question": _S, "case_question": _S, "why_it_matters": _S, "short_answer": _S,
    "findings": {"type": "array", "items": FINDING}, "claims": {"type": "array", "items": CLAIM},
    "sources": {"type": "array", "items": SOURCE}, "alternative_explanations": _SA, "what_is_established": _SA,
    "what_is_contested": _SA, "what_remains_unknown": _SA, "case_implication": _S,
    "changes_current_story": _obj({"value": {"type": "string", "enum": ["yes", "no", "maybe"]}, "why": _S}),
    "affected_hypotheses": {"type": "array", "items": EFFECT}, "affected_claims": {"type": "array", "items": EFFECT},
    "suggested_action": _S, "new_questions": _SA, "handoff_to_cos": _obj({"summary": _S, "recommended_next": _S}),
    "confidence_buckets": _obj({"high_confidence": _SA, "plausible": _SA, "contested": _SA, "unknown": _SA}),
}
MEASUREMENT = _obj({
    "problem_interpretation": _S, "measurement_objective": _S,
    "recommended_framework": _obj({"name": _S, "structure": _S, "why": _S}),
    "alternative_frameworks": {"type": "array", "items": _obj({"name": _S, "when_better": _S, "tradeoff": _S})},
    "metric_definitions": {"type": "array", "items": _obj({"metric": _S, "definition": _S, "formula": _S, "grain": _S, "milestone": _S, "notes": _S})},
    "required_events": {"type": "array", "items": _obj({"event": _S, "trigger": _S, "properties": _SA})},
    "required_dimensions": {"type": "array", "items": _obj({"dimension": _S, "why": _S})},
    "decision_enabled": _S, "limitations": _SA, "implementation_implications": _SA})
DATA_MODEL = _obj({
    "conceptual_model": _S, "entities": {"type": "array", "items": _obj({"name": _S, "description": _S, "grain": _S, "primary_key": _S})},
    "grain": _S, "fields": {"type": "array", "items": _obj({"entity": _S, "field": _S, "type": _S, "definition": _S, "example": _S})},
    "temporal_behavior": _S, "business_definitions": {"type": "array", "items": _obj({"term": _S, "definition": _S})},
    "classification_logic": {"type": "array", "items": _obj({"case": _S, "rule": _S})},
    "example_records": {"type": "array", "items": _obj({"entity": _S, "columns": _SA, "rows": {"type": "array", "items": _SA}})},
    "edge_cases": _SA, "data_quality_rules": _SA, "implementation_considerations": _SA})


def result_schema(specialty: str) -> dict:
    props = dict(BASE_RESULT)
    if specialty == "measurement":
        props["specialist"] = _obj({"measurement": MEASUREMENT})
    elif specialty == "data_engineering":
        props["specialist"] = _obj({"data_model": DATA_MODEL})
    return _obj(props)


DOSSIER = _obj({"role": _S, "summary": _S, "findings": {"type": "array", "items": FINDING},
                "claims": {"type": "array", "items": CLAIM}, "sources": {"type": "array", "items": SOURCE},
                "gaps": _SA, "counter_hypothesis": _S})
PEER = _obj({"supported_claims": _SA, "bare_assertions": _SA, "contradictions": _SA, "corroborated": _SA, "contested": _SA,
             "hallucination_risks": _SA, "stale_sources": _SA, "false_balance": _SA, "scope_drift": _SA,
             "source_grades": {"type": "array", "items": _obj({"source_id": _S, "quality": _S, "why": _S})}, "verdict": _S})


# ------------------------------------------------------------------------------------------ create + launch
def create_request(store: CaseStore, question: str, *, links: list[str] | None = None, route: dict | None = None,
                   actor: str = "hugo", parent: str | None = None, relation: str | None = None, launch: bool = True,
                   force_purpose: bool = False) -> dict:
    q = (question or "").strip()
    if len(q) < 8:
        raise ValueError("La pregunta es demasiado corta.")
    r0 = heuristic_route(store, q, links)
    rt = {**r0, **(route or {})}
    if route:
        rt["source"] = "hugo"
    purpose = map_purpose(store, q, links)
    ok = purpose["ok"] or force_purpose
    data = {"research_question": q, "case_question": ", ".join(purpose["mapped"]) or "",
            "specialty": rt["specialty"], "intensity": rt["intensity"], "route": rt,
            "status": "queued" if (launch and ok) else "draft", "purpose_ok": purpose["ok"],
            "purpose_note": purpose.get("note", "") if not purpose["ok"] else "",
            "forced_without_purpose": bool(force_purpose and not purpose["ok"]),
            "links": list(dict.fromkeys((links or []) + ([parent] if parent else []))), "phase": "research"}
    if parent:
        data[relation or "follow_up_of"] = parent
    r = store.create("research", data, actor=actor,
                     summary=f"{'Hugo' if actor == 'hugo' else actor} pidió research ({rt['intensity']} · {SPECIALTIES[rt['specialty']]}): {clip(q, 90)}")
    if not purpose["ok"] and not force_purpose:
        store.log("router", "flagged", [r["id"]], f"{r['id']}: RESEARCH WITHOUT CASE PURPOSE — espera decisión de Hugo",
                  material=True)
        return {"research": r, "launched": False, "purpose": purpose}
    if launch:
        job = launch_job(store, r["id"])
        return {"research": store.get(r["id"]), "launched": True, "job_id": job.id, "purpose": purpose}
    return {"research": r, "launched": False, "purpose": purpose}


def launch_job(store: CaseStore, rid: str):
    r = store.require(rid)
    title = f"{SPECIALTIES[r['specialty']]} · {clip(r['research_question'], 60)}"
    job = jobs.submit(store.id, "research", title, {"research_id": rid}, agent=AGENT_OF[r["specialty"]])
    store.update(rid, {"status": "queued", "job_id": job.id, "error": None}, actor="system", material=False,
                 summary=f"{rid} en cola", verb="queued")
    phases.touch(store, "research", actor="router")
    return job


# ------------------------------------------------------------------------------------------ job
@jobs.handler("research")
async def _research_job(job, params):
    store = cases.get(job.case_id)
    rid = params["research_id"]
    r = store.require(rid)
    store.update(rid, {"status": "running", "started_at": now_iso()}, actor=job.agent, material=False, verb="running",
                 summary=f"{rid} en curso")
    try:
        if (r.get("route") or {}).get("source") != "hugo" and r["specialty"] != "analytics":
            route = await _route_with_agent(store, r, job)
            r = store.update(rid, {"route": {**(r.get("route") or {}), **route, "source": "router"},
                                   "specialty": route["specialty"], "intensity": route["intensity"]},
                             actor="router", material=False, verb="routed",
                             summary=f"Router: {rid} → {route['intensity']} · {SPECIALTIES[route['specialty']]}")
        if r["specialty"] == "analytics":
            out = await _analytics(store, r, job)
        elif r["specialty"] == "business" and r["intensity"] == "L3":
            out = await _deep(store, r, job)
        else:
            out = await _specialist(store, r, job)
    except AgentError as e:
        store.update(rid, {"status": "failed", "error": f"{e.kind}: {e}", "failed_at": now_iso()}, actor=job.agent,
                     summary=f"{rid} falló ({e.kind}); la solicitud se conservó", verb="failed")
        raise
    except Exception as e:  # noqa: BLE001
        store.update(rid, {"status": "failed", "error": f"{type(e).__name__}: {e}", "failed_at": now_iso()}, actor=job.agent,
                     summary=f"{rid} falló; la solicitud se conservó", verb="failed")
        raise
    try:
        created = _persist(store, rid, out, job)
    except Exception as e:  # noqa: BLE001 - the investigation ran; saving its result failed: say so, never stay "running"
        store.update(rid, {"status": "failed", "error": f"No se pudo guardar el resultado: {type(e).__name__}: {e}",
                           "failed_at": now_iso()}, actor=job.agent, summary=f"{rid}: el resultado no se pudo guardar", verb="failed")
        raise
    if config.AUTO_COS and store.get(rid).get("status") == "completed":
        cos.flag_impact(store, rid)
        try:
            cos.submit_assessment(store, rid, reason="research completado")
        except Exception:  # noqa: BLE001 - COS assessment is best effort; the research result is already saved
            pass
    return {"research_id": rid, "findings": created}


async def _route_with_agent(store: CaseStore, r: dict, job) -> dict:
    selected = skills.select("router", text=r["research_question"])
    system = base.system_prompt("router", selected, store.meta().get("language"))
    ents = store.all()
    cands = [e for e in ents.values() if e.get("type") in ("question", "hypothesis", "decision", "claim")
             and (e.get("review") or {}).get("state") != "rejected"]
    lines = [f"- {e['id']}{' (' + e['alias'] + ')' if e.get('alias') else ''} {clip(title_of(e), 150)}" for e in sorted(cands, key=lambda e: e["id"])][:160]
    avail = sorted({s.id for s in skills.registry().values() if any(a in s.bindings for a in ("business_research", "measurement", "data_engineering"))})
    prompt = (f"Solicitud: {r['research_question']}\nIDs sugeridos por Hugo: {', '.join(r.get('links') or []) or '—'}\n"
              f"Preclasificación heurística: {r.get('route', {}).get('intensity')} · {r.get('route', {}).get('specialty')}\n"
              f"¿El caso tiene workspace analítico? {'sí' if (store.meta().get('workspace') or {}).get('type') not in (None, 'none') else 'no'}\n"
              f"Skills disponibles para especialistas: {', '.join(avail)}\n\nQ/H/D/C del caso:\n" + "\n".join(lines))
    spec = RunSpec(agent="router", role="router", system=system, prompt=prompt, schema=ROUTE_SCHEMA, max_turns=3,
                   skills=skills.record(selected), purpose=f"Ruteo de {r['id']}", case_id=store.id, case_root=store.root)
    res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    out = res.output
    if out["specialty"] == "analytics" and (store.meta().get("workspace") or {}).get("type") in (None, "none"):
        out["specialty"] = "business"
    if out["specialty"] == "analytics":
        out["intensity"] = "analytics"
    elif out["intensity"] == "analytics":
        out["intensity"] = "L2"
    out["skills"] = [s for s in out.get("skills", []) if s in skills.registry()][:3]
    out["purpose"]["mapped_ids"] = [i for i in out["purpose"].get("mapped_ids", []) if i in ents]
    out["run_id"] = res.run_id
    return out


def _case_context(store: CaseStore, r: dict) -> str:
    ents = store.all()
    ids = (r.get("links") or []) + ((r.get("route") or {}).get("purpose") or {}).get("mapped_ids", [])
    linked = [ents[i] for i in dict.fromkeys(ids) if i in ents]
    brief = store.read_data("brief/brief.yaml", {}) or {}
    fr = store.read_data("framing/current.yaml", {}) or {}
    lines = [f"Caso: {store.meta().get('name')} — {brief.get('title', '')}", f"Objetivo: {clip(brief.get('objective', ''), 300)}",
             f"Pregunta ejecutiva: {fr.get('executive_question', '')}",
             "Datos disponibles: " + "; ".join(brief.get("data_available") or []),
             "No afirmar todavía: " + "; ".join(clip(x, 120) for x in (fr.get("should_not_claim") or [])[:6]),
             "", "Elementos del caso a los que sirve esta investigación:"]
    for e in linked:
        lines.append(f"- {e['id']}{' (' + e['alias'] + ')' if e.get('alias') else ''} [{e.get('type')}] {clip(title_of(e), 260)}"
                     + (f" · se debilita si: {clip(e.get('falsifier', ''), 160)}" if e.get("falsifier") else ""))
    return "\n".join(lines + task_lines(r))


def task_lines(r: dict) -> list[str]:
    """The plan task behind this research (Framing & Shaping): what must come out, the starting answer to validate or
    refute, Hugo's own words and the steps."""
    from .shaping import STEP_KINDS, WORK
    tk = r.get("task") or {}
    if not (tk.get("draft_answer") or tk.get("steps")):
        return []
    out = ["", f"## Tarea {r.get('shaping_task') or ''} del plan de investigación (aprobada por Hugo)",
           f"Qué debe salir: {(WORK.get(tk.get('work')) or {}).get('label', 'Investigación y propuesta')}"
           + (f" · láminas del guion: {', '.join(r.get('slides') or [])}" if r.get("slides") else "")]
    if tk.get("draft_answer"):
        out.append("Respuesta de arranque (hipótesis de trabajo del Framer: valídala, afínala o refútala con evidencia; "
                   f"no la des por buena): {tk['draft_answer']}")
    out += [f"Lo que Hugo ya dijo ({x.get('ref')}): “{x.get('text')}”" for x in tk.get("hugo_said") or []]
    for i, st in enumerate(tk.get("steps") or [], 1):
        out.append(f"Paso {i} · {STEP_KINDS.get(st.get('kind'), st.get('kind'))}: {st.get('what')}"
                   + (f" (tablas: {', '.join(st['where'])})" if st.get("where") else ""))
    return out


def _data_access(store: CaseStore, r: dict):
    """The data model a specialist may query: when the task has data steps, or the specialist designs measurement or
    data models (it has to know what exists before proposing)."""
    from .shaping import data_model
    has_data_step = any(st.get("kind") == "data" for st in (r.get("task") or {}).get("steps") or [])
    if not (has_data_step or r.get("specialty") in ("measurement", "data_engineering")):
        return None
    return data_model(store)


DATA_RULES = ("## Modelo de datos del caso (solo lectura)\nTienes `consultar_modelo` (una SELECT sobre raw.*, staging.*, "
              "mart.*; máx. 200 filas) y `catalogo_modelo`. Úsalas en los pasos de datos: comprueba qué existe antes de proponer, "
              "y si un dato no está en el modelo, dilo. Cada cifra que saques del modelo va en `sources` con source_type "
              "\"data_model\", url vacío, title = qué responde y note = el SQL exacto que corriste (si citas el catálogo, note = "
              "catalogo_modelo()); el claim cita ese source_id. Una cita del modelo solo cuenta si la consulta corrió en esta corrida.")


async def _specialist(store: CaseStore, r: dict, job) -> dict:
    spec_key = r["specialty"]
    agent = AGENT_OF[spec_key]
    route = r.get("route") or {}
    q = route.get("reformulated_question") or r["research_question"]
    selected = skills.select(agent, intensity=r["intensity"], text=r["research_question"], force=route.get("skills"))
    if spec_key == "business" and r["intensity"] == "L1":
        selected = [x for x in selected if x["mode"] != "lens"]
    system = base.system_prompt(agent, selected, store.meta().get("language"))
    intensity_rule = {"L1": "Nivel L1 · lookup: 1–3 fuentes autoritativas, respuesta corta y exacta. No más de 4 búsquedas.",
                      "L2": "Nivel L2 · business research: varias fuentes buenas, compara enfoques, sintetiza qué aplica a este caso.",
                      "L3": "Nivel L3: investiga a fondo con fuentes de calidad y contraargumentos."}.get(r["intensity"], "")
    prompt = (f"# Investigación {r['id']}\nPregunta: {q}\nPregunta original de Hugo: {r['research_question']}\n"
              f"{intensity_rule}\nEvidencia que la respondería: {route.get('evidence_needed', '—')}\n\n{_case_context(store, r)}\n\n"
              "Reglas: cita solo URLs que recuperaste en esta corrida; cada claim material referencia un `source_id` de tu lista "
              "de fuentes; si una afirmación no tiene fuente, no lleva cifras y va como inferencia. Los benchmarks son contexto, "
              "nunca evidencia sobre esta empresa. Termina con la síntesis para el caso (qué cambia para ESTE caso).")
    tools = ["WebSearch", "WebFetch"]
    turns = {"L1": 10, "L2": 24, "L3": 30}.get(r["intensity"], 20)
    dm = _data_access(store, r)
    if dm is not None:
        prompt += "\n\n" + DATA_RULES
        turns += 10
    spec = RunSpec(agent=agent, role=agent, system=system, prompt=prompt, schema=result_schema(spec_key), tools=tools,
                   max_turns=turns, skills=skills.record(selected), purpose=f"{r['id']} · {SPECIALTIES[spec_key]} {r['intensity']}",
                   case_id=store.id, case_root=store.root, timeout_s=1500 if dm is not None else 1200, data_model=dm)
    res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    out = dict(res.output)
    out["_run_ids"] = [res.run_id]
    out["_seen_urls"] = res.seen_urls
    out["_sql_runs"] = res.sql_runs
    out["_usage"] = {res.run_id: {"cost_usd": res.cost_usd, **(res.usage or {})}}
    out["_skills"] = skills.record(selected)
    return out


async def _deep(store: CaseStore, r: dict, job) -> dict:
    """deep-business-research: depth + breadth + counter (parallel) → peer review → case synthesis."""
    route = r.get("route") or {}
    q = route.get("reformulated_question") or r["research_question"]
    ctx = _case_context(store, r)
    roles = {
        "depth": "Rol DEPTH: ve a fondo en la pregunta principal. Varias búsquedas y lecturas; cita cada claim que sostiene el argumento.",
        "breadth": "Rol BREADTH: temas adyacentes, encuadres alternativos, contexto histórico y cómo lo hacen los practicantes.",
        "counter": "Rol COUNTER: construye la contra-hipótesis más fuerte y busca activamente evidencia que contradiga la respuesta "
                   "dominante, casos donde falla y críticas conocidas. Adversarial, no balanceado.",
    }
    selected = skills.select("business_research", intensity="L3", text=r["research_question"], force=route.get("skills"))
    base_system = base.system_prompt("business_research", selected, store.meta().get("language"))

    async def role_run(role, brief):
        await job.event("phase", {"phase": role})
        spec = RunSpec(agent="business_research", role="deep_research", system=base_system,
                       prompt=f"# {r['id']} · deep research · {role}\nPregunta: {q}\n{brief}\n\n{ctx}\n\nEntrega tu dossier "
                              "(findings, claims con source_id, fuentes calificadas, huecos). Cita solo URLs recuperadas.",
                       schema=DOSSIER, tools=["WebSearch", "WebFetch"], max_turns=26, skills=skills.record(selected),
                       purpose=f"{r['id']} · deep research ({role})", case_id=store.id, case_root=store.root, timeout_s=1200)
        return role, await get_llm().run(spec, lambda k, d: job.event(k, {**d, "role": role}))

    results = await asyncio.gather(*(role_run(k, v) for k, v in roles.items()), return_exceptions=True)
    dossiers, run_ids, seen, usage = {}, [], [], {}
    for item in results:
        if isinstance(item, Exception):
            await job.event("role_failed", {"error": str(item)[:300]})
            continue
        role, res = item
        dossiers[role] = res.output
        run_ids.append(res.run_id)
        seen += res.seen_urls
        usage[res.run_id] = {"cost_usd": res.cost_usd, **(res.usage or {})}
    if not dossiers:
        raise AgentError("unknown", "Los tres roles de deep research fallaron; la solicitud se conservó.")
    await job.event("phase", {"phase": "peer_review"})
    import json as _json
    peer_sel = skills.select("peer_review", text=q)
    peer_spec = RunSpec(agent="business_research", role="peer_review",
                        system=base.system_prompt("business_research", peer_sel, store.meta().get("language"),
                                                  extra="Actúas como PEER REVIEWER del método deep-business-research: no investigas de nuevo; "
                                                        "revisas los dossiers."),
                        prompt=f"Pregunta: {q}\nURLs realmente recuperadas en las corridas: {len(set(seen))}\n\nDossiers:\n"
                               + _json.dumps(dossiers, ensure_ascii=False)[:60000],
                        schema=PEER, max_turns=3, skills=skills.record(peer_sel), purpose=f"{r['id']} · peer review",
                        case_id=store.id, case_root=store.root)
    peer = await get_llm().run(peer_spec, lambda k, d: job.event(k, d))
    run_ids.append(peer.run_id)
    usage[peer.run_id] = {"cost_usd": peer.cost_usd, **(peer.usage or {})}
    await job.event("phase", {"phase": "synthesis"})
    syn_sel = skills.select("business_research", intensity="L3", text=q)
    syn_spec = RunSpec(agent="business_research", role="synthesis",
                       system=base.system_prompt("business_research", syn_sel, store.meta().get("language"),
                                                 extra="Ahora haces la SÍNTESIS PARA EL CASO a partir de los dossiers y la revisión de pares. "
                                                       "No inventes fuentes: usa solo las de los dossiers (conserva sus URLs)."),
                       prompt=f"# {r['id']} · síntesis\nPregunta: {q}\n\n{ctx}\n\nDossiers:\n" + _json.dumps(dossiers, ensure_ascii=False)[:60000]
                              + "\n\nRevisión de pares:\n" + _json.dumps(peer.output, ensure_ascii=False)[:20000],
                       schema=result_schema("business"), max_turns=3, skills=skills.record(syn_sel),
                       purpose=f"{r['id']} · síntesis", case_id=store.id, case_root=store.root)
    syn = await get_llm().run(syn_spec, lambda k, d: job.event(k, d))
    run_ids.append(syn.run_id)
    usage[syn.run_id] = {"cost_usd": syn.cost_usd, **(syn.usage or {})}
    out = dict(syn.output)
    out.update({"_run_ids": run_ids, "_seen_urls": sorted(set(seen)), "_usage": usage, "_skills": skills.record(selected),
                "peer_review": peer.output, "dossier_roles": list(dossiers)})
    return out


async def _analytics(store: CaseStore, r: dict, job) -> dict:
    from . import analytics
    return await analytics.investigate_for_research(store, r, job)


# ------------------------------------------------------------------------------------------ persist + validate
def _norm_url(u: str) -> str:
    u = (u or "").strip().rstrip("/").split("#")[0]
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u.lower()


def _norm_sql(q: str) -> str:
    return " ".join((q or "").replace(";", " ").split()).lower()


def model_source_ran(source: dict, ran: set[str]) -> bool:
    """A citation of the data model counts when its note starts with a query that ran in the run (a comment after
    the SQL is fine), or when it cites the catalog and the catalog was read."""
    note = _norm_sql(source.get("note"))
    if not note or not ran:
        return False
    if "catalogo_modelo" in note and "select " not in note:        # "catalogo_modelo() — …", "Herramienta catalogo_modelo…"
        return _norm_sql("catalogo_modelo()") in ran
    return any(note == q or note.startswith(q + " ") for q in ran)


def reverify_model_sources(store: CaseStore, rid: str, *, actor: str = "system") -> dict:
    """Re-check the data-model citations of a completed research with the current rule (its queries are kept in
    sql_runs). Only flags change: a claim cleared here keeps the confidence it had."""
    r = store.require(rid)
    ran = {_norm_sql(q) for q in r.get("sql_runs") or []}
    # runs before the catalog was logged: the run's own tool trace says whether the catalog was read
    for run_id in r.get("run_ids") or []:
        rec = read_json(store.root / "audit" / "runs" / f"{run_id}.json", {}) or {}
        if any(str(t.get("tool", "")).endswith("catalogo_modelo") for t in rec.get("tool_trace") or []):
            ran.add(_norm_sql("catalogo_modelo()"))
    sources = r.get("sources") or []
    fixed = [s["id"] for s in sources if s.get("source_type") == "data_model" and not s.get("verified") and model_source_ran(s, ran)]
    if not fixed:
        return {"research": rid, "fixed": []}
    for s in sources:
        if s.get("id") in fixed:
            s["verified"] = True
    bad = {s.get("id") for s in sources if not s.get("verified")}
    claims = r.get("claims") or []
    for c in claims:
        if c.get("source_id") in fixed and c.get("unverified"):
            c["unverified"] = False
            c["notes"] = (c.get("notes", "").replace(" · fuente no recuperada en la corrida (CaseOS)", "") +
                          " · cita del modelo re-verificada (CaseOS)").strip(" ·")
    v = {**(r.get("validation") or {}), "unverified_sources": [i for i in (r.get("validation") or {}).get("unverified_sources") or [] if i not in fixed]}
    v["ok"] = not v["unverified_sources"] and not v.get("bare_claims")
    store.update(rid, {"sources": sources, "claims": claims, "validation": v}, actor=actor, material=False,
                 summary=f"{rid}: {len(fixed)} cita(s) del modelo re-verificadas ({', '.join(fixed)})")
    for fid in r.get("findings") or []:
        f = store.get(fid)
        if f and f.get("unverified"):
            cl = f.get("claims") or []
            for c in cl:
                if c.get("source_id") in fixed:
                    c["unverified"] = False
            still = any(c.get("unverified") or c.get("source_id") in bad for c in cl)
            if not still:
                store.update(fid, {"claims": cl, "unverified": False}, actor=actor, material=False,
                             summary=f"{fid}: su cita del modelo quedó verificada")
    return {"research": rid, "fixed": fixed}


def verify_citations(out: dict) -> dict:
    """Citations must be URLs retrieved in the run — or, for the case's data model, a query that actually ran in the
    run (its exact SQL in the source's note). Returns validation info and mutates claims/sources."""
    seen = {_norm_url(u) for u in out.get("_seen_urls") or []}
    ran = {_norm_sql(q) for q in out.get("_sql_runs") or []}
    sources = out.get("sources") or []
    unverified = []
    for s in sources:
        url = s.get("url") or ""
        if s.get("source_type") == "internal":
            s["verified"] = True
            continue
        if s.get("source_type") == "data_model":
            s["verified"] = model_source_ran(s, ran)
            if not s["verified"]:
                unverified.append(s.get("id"))
            continue
        ok = bool(url) and (_norm_url(url) in seen or any(_norm_url(url).startswith(x) or x.startswith(_norm_url(url)) for x in seen if len(x) > 12))
        s["verified"] = ok
        if not ok:
            unverified.append(s.get("id"))
    ids = {s.get("id") for s in sources}
    bare = []
    for c in out.get("claims") or []:
        sid = c.get("source_id")
        if not sid or sid not in ids:
            c["unverified"] = True
            c["confidence"] = "low"
            bare.append(clip(c.get("claim", ""), 80))
        elif sid in unverified:
            c["unverified"] = True
            c["confidence"] = "low"
            c["notes"] = (c.get("notes", "") + " · fuente no recuperada en la corrida (CaseOS)").strip(" ·")
    return {"unverified_sources": [u for u in unverified if u], "bare_claims": bare,
            "seen_urls": len(seen), "ok": not unverified and not bare}


def _persist(store: CaseStore, rid: str, out: dict, job) -> list[str]:
    r = store.require(rid)
    ents = store.all()
    validation = verify_citations(out) if r["specialty"] != "analytics" else {"ok": True}
    created = []
    with store.batch():
        if r["specialty"] != "analytics":
            claims = out.get("claims") or []
            for f in (out.get("findings") or [])[:6]:
                cl = [claims[i] for i in f.get("claim_indexes") or [] if isinstance(i, int) and 0 <= i < len(claims)]
                unver = any(c.get("unverified") for c in cl)
                e = store.create("finding", {
                    "headline": f["headline"], "evidence_text": f.get("evidence", ""), "confidence": "low" if unver else f.get("confidence", "medium"),
                    "limitations": [f["limitation"]] if f.get("limitation") else [], "kind": "external" if r["specialty"] == "business" else r["specialty"],
                    "claims": cl, "unverified": unver, "source_ref": {"research": rid},
                    "links": [rid] + [i["id"] for i in out.get("affected_hypotheses") or [] if i.get("id") in ents][:3]},
                    actor=AGENT_OF[r["specialty"]], summary=f"{rid}: finding propuesto — {clip(f['headline'], 80)}")
                created.append(e["id"])
        else:
            created = out.pop("_finding_ids", [])
        aff_h = [x for x in out.get("affected_hypotheses") or [] if x.get("id") in ents]
        aff_c = [x for x in out.get("affected_claims") or [] if x.get("id") in ents]
        links = list(dict.fromkeys((r.get("links") or []) + [x["id"] for x in aff_h] + [x["id"] for x in aff_c] + created
                                   + ((r.get("route") or {}).get("purpose") or {}).get("mapped_ids", [])))
        # Hugo's question stays as he asked it; the specialist's working version is kept next to it
        patch = {k: v for k, v in out.items() if not k.startswith("_") and k not in ("findings", "research_question")}
        if out.get("research_question") and norm(out["research_question"]) != norm(r["research_question"]):
            patch["worked_question"] = out["research_question"]
        if out.get("_sql_runs"):
            patch["sql_runs"] = out["_sql_runs"]
        patch.update({"status": "completed", "completed_at": now_iso(), "findings": created, "links": [l for l in links if l != rid],
                      "affected_hypotheses": aff_h, "affected_claims": aff_c, "run_ids": out.get("_run_ids", []),
                      "usage": out.get("_usage", {}), "skills_loaded": out.get("_skills", []), "validation": validation,
                      "review": {"state": "proposed"}, "error": None})
        cost = sum((u or {}).get("cost_usd") or 0 for u in (out.get("_usage") or {}).values())
        store.update(rid, patch, actor=AGENT_OF[r["specialty"]], verb="completed",
                     summary=f"{rid} completada: {clip(out.get('short_answer', ''), 110)}"
                             + (f" · {len(validation.get('unverified_sources') or [])} fuente(s) sin verificar" if not validation.get("ok") else ""),
                     run_id=(out.get("_run_ids") or [None])[-1])
        if cost:
            store.log("system", "cost", [rid], f"{rid}: costo equivalente US${cost:.2f} (suscripción: no se factura por corrida)")
    return created


# ------------------------------------------------------------------------------------------ how a result was reached
_TRACE_FIELD = {"search": re.compile(r'"query":\s*"((?:[^"\\]|\\.)*)'), "read": re.compile(r'"url":\s*"((?:[^"\\]|\\.)*)'),
                "sql": re.compile(r'"sql":\s*"((?:[^"\\]|\\.)*)')}


def _step(tool: str, inp) -> tuple[str, str]:
    """One tool call of a run as (kind, text): what the agent looked at, in its own terms."""
    kind = ("search" if tool in ("WebSearch", "web_search") else "read" if tool in ("WebFetch", "web_fetch")
            else "sql" if tool.endswith("consultar_modelo") else "catalog" if tool.endswith("catalogo_modelo") else "tool")
    if kind == "catalog":
        return kind, "Leyó el catálogo del modelo de datos"
    if kind == "tool":
        return kind, tool
    key = {"search": "query", "read": "url", "sql": "sql"}[kind]
    if isinstance(inp, dict):
        return kind, " ".join(str(inp.get(key) or "").split())
    m = _TRACE_FIELD[kind].search(str(inp or ""))                  # long inputs are stored truncated, as text
    return kind, " ".join((m.group(1) if m else str(inp or "")).replace('\\"', '"').split())


def process(store: CaseStore, r: dict) -> dict | None:
    """How a specialist reached its result, from the run records: every search, reading and query of the data model,
    in order and timed from when it started working (not the model's private reasoning, which is never stored)."""
    runs = []
    for run_id in r.get("run_ids") or []:
        rec = read_json(store.root / "audit" / "runs" / f"{run_id}.json", {}) or {}
        if not rec:
            continue
        trace = rec.get("tool_trace") or []
        t0 = trace[0].get("t", 0) if trace else 0
        steps = []
        for t in trace:
            kind, text = _step(str(t.get("tool") or ""), t.get("input"))
            steps.append({"s": max(0, round((t.get("t", t0) - t0) / 1000)), "kind": kind, "text": clip(text, 400),
                          "error": bool(t.get("is_error"))})
        u = rec.get("usage") or {}
        runs.append({"run_id": run_id, "role": rec.get("role"), "purpose": rec.get("purpose"), "steps": steps,
                     "work_s": round((u.get("ms") or rec.get("duration_ms") or 0) / 1000), "turns": u.get("turns"),
                     "output_tokens": u.get("output_tokens"), "cost_usd": rec.get("cost_usd"), "model": rec.get("model"),
                     "effort": rec.get("effort")})
    if not runs:
        return None
    all_steps = [x for rn in runs for x in rn["steps"]]
    count = lambda k: sum(1 for x in all_steps if x["kind"] == k)
    return {"runs": runs, "counts": {"sql": count("sql"), "catalog": count("catalog"), "search": count("search"),
                                     "read": count("read"), "total": len(all_steps)},
            "work_s": sum(rn["work_s"] for rn in runs), "cost_usd": round(sum(rn["cost_usd"] or 0 for rn in runs), 2)}


def paths_for(store: CaseStore, eid: str) -> list[dict]:
    """The research behind an entity — a claim (its research and the research of its evidence), a finding or a research
    itself — each with how it got there, straight from the record."""
    ents = store.all()
    e = ents.get(eid) or {}
    t = e.get("type")
    rids: list[str] = []
    if t == "research":
        rids = [eid]
    else:
        fids = [eid] if t == "finding" else [i for i in e.get("evidence_ids") or [] if i in ents] if t == "claim" else []
        rids = [i for i in e.get("research_ids") or [] if i in ents] if t == "claim" else []
        for fid in fids:
            f = ents[fid]
            rid = (f.get("source_ref") or {}).get("research") or next((l for l in f.get("links") or [] if type_of(l) == "research"), None)
            if not rid and (f.get("source_ref") or {}).get("run"):
                rid = next((r["id"] for r in ents.values() if r.get("type") == "research"
                            and (r.get("workspace_run") or {}).get("run_id") == f["source_ref"]["run"]), None)
            if rid and rid in ents and rid not in rids:
                rids.append(rid)
    out = []
    for rid in rids:
        r = ents[rid]
        if r.get("status") == "completed" and r.get("specialty") != "analytics":
            out.append({"research": r, "process": process(store, r)})
    return out


def proposals(store: CaseStore) -> list[dict]:
    """Every completed research that answers with a proposal (not only with data), with how it got there."""
    out = []
    for r in sorted(store.list("research"), key=lambda e: e["id"]):
        work = (r.get("task") or {}).get("work")
        if r.get("status") != "completed" or r.get("specialty") == "analytics" or work == "datos":
            continue
        out.append({"research": r, "process": process(store, r)})
    return out


# ------------------------------------------------------------------------------------------ Hugo's actions on research
def accept(store: CaseStore, rid: str, *, note: str = "", actor: str = "hugo") -> dict:
    r = store.require(rid)
    with store.batch():
        store.set_review(rid, "accepted", actor=actor, note=note)
        for fid in r.get("findings") or []:
            f = store.get(fid)
            if f and (f.get("review") or {}).get("state") == "proposed":
                store.set_review(fid, "accepted", actor=actor, note=f"aceptado con {rid}")
        qs = [i for i in r.get("links") or [] if type_of(i) == "question"]
        for q in qs:
            e = store.get(q)
            if e and e.get("kind") == "workplan" and e.get("status") == "open":
                store.update(q, {"status": "answered", "answered_by": rid}, actor=actor, summary=f"{q} respondida por {rid}")
    return store.get(rid)


def reject(store: CaseStore, rid: str, *, note: str, actor: str = "hugo") -> dict:
    r = store.require(rid)
    with store.batch():
        store.set_review(rid, "rejected", actor=actor, note=note)
        for fid in r.get("findings") or []:
            f = store.get(fid)
            if f and (f.get("review") or {}).get("state") == "proposed":
                store.set_review(fid, "rejected", actor=actor, note=f"rechazado con {rid}")
    return store.get(rid)


def challenge(store: CaseStore, rid: str, *, objection: str, actor: str = "hugo") -> dict:
    r = store.require(rid)
    chal = (r.get("challenges") or []) + [{"by": actor, "at": now_iso(), "text": objection}]
    store.update(rid, {"challenges": chal}, actor=actor, summary=f"Hugo cuestionó {rid}: {clip(objection, 100)}", verb="challenged")
    spec = r.get("specialty")
    q = f"Contraste de {rid}: {objection}. Busca evidencia en contra y explicaciones alternativas a: {clip(r.get('short_answer', ''), 400)}"
    route = {"specialty": spec if spec != "analytics" else "business", "intensity": "L2" if r.get("intensity") in ("L1", "analytics") else r.get("intensity", "L2")}
    if spec == "analytics":
        route = {"specialty": "analytics", "intensity": "analytics"}
        q = f"{objection} (cuestiona {rid}: {clip(r.get('research_question', ''), 200)})"
    return create_request(store, q, links=[i for i in r.get("links") or [] if type_of(i) in ("question", "hypothesis", "decision", "claim")][:4],
                          route=route, actor=actor, parent=rid, relation="challenge_of", force_purpose=True)


def deeper(store: CaseStore, rid: str, *, note: str = "", actor: str = "hugo") -> dict:
    r = store.require(rid)
    nxt = {"L1": "L2", "L2": "L3", "L3": "L3", "analytics": "analytics"}.get(r.get("intensity"), "L2")
    q = (note.strip() + " — " if note.strip() else "") + f"Profundizar: {r.get('research_question')}"
    return create_request(store, q, links=[i for i in r.get("links") or [] if type_of(i) in ("question", "hypothesis", "decision", "claim")][:4],
                          route={"specialty": r.get("specialty", "business"), "intensity": nxt}, actor=actor, parent=rid,
                          relation="deeper_of", force_purpose=True)


def follow_up(store: CaseStore, rid: str, *, question: str, actor: str = "hugo", launch: bool = False) -> dict:
    r = store.require(rid)
    q = store.create("question", {"text": question, "kind": "research", "status": "open", "phase": "research", "links": [rid]},
                     actor=actor, summary=f"Pregunta de seguimiento de {rid}: {clip(question, 90)}")
    out = {"question": q}
    if launch:
        out.update(create_request(store, question, links=[q["id"]], actor=actor, parent=rid, relation="follow_up_of"))
    return out


def retry(store: CaseStore, rid: str) -> dict:
    job = launch_job(store, rid)
    return {"job_id": job.id}
