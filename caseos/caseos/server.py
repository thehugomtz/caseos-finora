"""CaseOS server — a modular monolith: REST + SSE + the web app + the existing workspace mounted in-process.

    .venv/bin/python -m caseos serve     →  http://127.0.0.1:8780

Only listens on 127.0.0.1. Agent work runs as background jobs in this process (Claude Agent SDK on the local
Claude Code session). The Business Exploration Workspace is mounted at /ws/finora (its own UI and API, unchanged).
"""
from __future__ import annotations

import asyncio
import json
import mimetypes
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import (actions, analytics, brain, briefing, bus, cases, commands, config, cos, datamodels, decisions, deckedit, framing_doc, jobs, shaping, slidestyle,
               lineage, phases, research, search, skills, story, storyteller)
from .agents import base as agents_base
from .agents import briefer, framer, planner
from .model import PHASES, TYPES, title_of, type_of
from .phases import GateError
from .store import StoreError
from .util import now_iso, read_json, read_jsonl, yaml_load

WS_MOUNTED = {"finora": False}


@asynccontextmanager
async def lifespan(_app):
    bus.bind_loop(asyncio.get_running_loop())
    n = jobs.mark_interrupted_on_boot()
    for c in cases.list_cases():
        framer.recover_turns(cases.get(c["id"]))
        planner.recover(cases.get(c["id"]))
        briefer.recover_turns(cases.get(c["id"]))
        storyteller.recover_decks(cases.get(c["id"]))
    if n:
        print(f"[caseos] {n} trabajo(s) interrumpido(s) en la sesión anterior; sus solicitudes siguen disponibles para reintentar.")
    try:
        storyteller.ensure_links()
    except Exception as e:  # noqa: BLE001
        print(f"[caseos] no se pudieron enlazar las skills del Storyteller: {e}")
    yield
    for t in list(jobs.TASKS):
        t.cancel()


app = FastAPI(title="CaseOS", lifespan=lifespan)


@app.middleware("http")
async def _no_stale_assets(request: Request, call_next):
    """The web app is served as ES modules without a build step: revalidate them on every load."""
    resp = await call_next(request)
    if request.url.path.startswith("/static/") or request.url.path == "/":
        resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.exception_handler(StoreError)
async def _store_error(_req: Request, exc: StoreError):
    code = 409 if isinstance(exc, GateError) else (404 if "no existe" in str(exc) or "no encontrad" in str(exc).lower() else 400)
    return JSONResponse({"detail": str(exc)}, status_code=code)


@app.exception_handler(ValueError)
async def _value_error(_req: Request, exc: ValueError):
    return JSONResponse({"detail": str(exc)}, status_code=400)


def _mount_workspaces():
    from .workspaces.finora_eda import adapter
    ws = adapter({"path": str(config.FINORA_EDA_PATH)})
    if ws.available and not WS_MOUNTED["finora"]:
        WS_MOUNTED["finora"] = ws.mount(app)


_mount_workspaces()


def S(cid: str):
    return cases.get(cid)


# ------------------------------------------------------------------------------------------ web app
BOOT = str(int(__import__("time").time()))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    # module URLs carry the boot id, so a restarted server never serves stale ES modules from the browser cache
    return (config.WEB_DIR / "index.html").read_text(encoding="utf-8").replace("/static/", f"/static/v{BOOT}/")


@app.get("/static/v{ver}/{path:path}", include_in_schema=False)
def static_versioned(ver: str, path: str):
    p = (config.WEB_DIR / path).resolve()
    if config.WEB_DIR.resolve() not in p.parents or not p.is_file():
        raise HTTPException(404, "No encontrado")
    return FileResponse(p, media_type=mimetypes.guess_type(str(p))[0] or "application/octet-stream")


app.mount("/static", StaticFiles(directory=str(config.WEB_DIR)), name="static")


# ------------------------------------------------------------------------------------------ system
@app.get("/api/health")
def health():
    import os
    return {"ok": True, "cases": len(cases.list_cases()), "workspace_finora": WS_MOUNTED["finora"],
            "auth": "API key" if os.environ.get("ANTHROPIC_API_KEY") else "suscripción de Claude (sesión local de Claude Code)",
            "model": config.DEFAULT_MODEL, "storyteller_links": storyteller.ensure_links(), "auto_cos": config.AUTO_COS}


@app.get("/api/skills")
def skills_manifest():
    return {"skills": [s.public() for s in skills.registry().values()], "policy": skills.policy()}


@app.get("/api/agents")
def agents_list():
    return {"agents": [agents_base.card(a) for a in agents_base.AGENTS]}


@app.get("/api/agents/{aid}")
def agent_card(aid: str):
    if aid not in agents_base.AGENTS:
        raise HTTPException(404, "Agente desconocido")
    return agents_base.card(aid)


# ------------------------------------------------------------------------------------------ cases
class NewCase(BaseModel):
    name: str
    objective: str = ""
    audience: list[str] = []
    data_model: str = ""
    brief_text: str = ""
    context: str = ""
    deliverables: list[str] = []
    constraints: list[str] = []
    language: str = "es"
    title: str = ""
    client: str = ""


@app.get("/api/cases")
def cases_list():
    return {"cases": cases.list_cases()}


@app.post("/api/cases")
def cases_create(body: NewCase):
    s = cases.create_case(name=body.name, objective=body.objective, audience=body.audience, brief_text=body.brief_text,
                          context=body.context, deliverables=body.deliverables, constraints=body.constraints,
                          language={"primary": body.language, "structured_language": body.language}, title=body.title,
                          client=body.client)
    if body.data_model:
        datamodels.bind(s, body.data_model, actor="hugo")
    return {"id": s.id}


@app.get("/api/cases/{cid}")
def case_summary(cid: str):
    s = S(cid)
    m = s.meta()
    counts = {}
    for e in s.all().values():
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    return {"id": s.id, "meta": {k: m.get(k) for k in ("name", "title", "client", "objective", "audience", "language", "workspace",
                                                       "data_model", "created_at", "updated_at")},
            "phases": phases.phases_view(s), "current_phase": phases.current_phase(m), "counts": counts,
            "running": jobs.running(cid), "analytics": analytics.info(s)}


def _compact(e: dict) -> dict:
    return {"id": e["id"], "type": e.get("type"), "title": title_of(e), "status": e.get("status"),
            "review": (e.get("review") or {}).get("state", "proposed"), "stale": bool(e.get("stale")), "alias": e.get("alias"),
            "kind": e.get("kind"), "confidence": e.get("confidence"), "phase": e.get("phase"), "links": e.get("links") or [],
            "created_at": e.get("created_at"), "updated_at": e.get("updated_at"), "actor": (e.get("origin") or {}).get("actor"),
            "table_key": e.get("table_key"), "specialty": e.get("specialty"), "intensity": e.get("intensity"),
            "hugo_wording": e.get("hugo_wording")}


@app.get("/api/cases/{cid}/state")
def case_state(cid: str):
    s = S(cid)
    return {"entities": [_compact(e) for e in s.list()], "phases": phases.phases_view(s)}


@app.get("/api/cases/{cid}/entities/{eid}")
def entity(cid: str, eid: str):
    s = S(cid)
    e = s.get(eid)
    if not e:
        raise HTTPException(404, f"{eid} no existe")
    ents = s.all()
    extra = {}
    if e.get("type") == "claim":
        extra["strength"] = cos.claim_strength(s, e, ents)
    if e.get("type") == "finding":
        extra["tables"] = [ents[l] for l in e.get("links") or [] if type_of(l) == "table" and l in ents]
    if e.get("type") == "research":
        extra["findings_full"] = [ents[f] for f in e.get("findings") or [] if f in ents]
        extra["job"] = jobs.get(cid, e["job_id"]) if e.get("job_id") else None
        extra["process"] = research.process(s, e) if e.get("status") == "completed" else None
    if e.get("type") in ("claim", "finding"):
        extra["paths"] = research.paths_for(s, eid)
    return {"entity": e, "lineage": lineage.lineage(ents, eid), "history": [{"version": h["version"], "updated_at": h["updated_at"]}
                                                                             for h in s.history(eid)],
            "actions": [{"id": a, "label": actions.ACTIONS[a]} for a in actions.available(e)], **extra}


@app.get("/api/cases/{cid}/research-proposals")
def research_proposals(cid: str):
    return {"proposals": research.proposals(S(cid))}


@app.get("/api/cases/{cid}/entities/{eid}/history/{version}")
def entity_version(cid: str, eid: str, version: int):
    h = next((h for h in S(cid).history(eid) if h["version"] == version), None)
    if not h:
        raise HTTPException(404, "Versión no encontrada")
    return h


class EntityPatch(BaseModel):
    fields: dict


EDITABLE = {"text", "statement", "headline", "answer", "falsifier", "structured", "title", "question", "limitations",
            "visual_intent", "confidence", "status", "priority", "note", "research_question"}


@app.patch("/api/cases/{cid}/entities/{eid}")
def entity_patch(cid: str, eid: str, body: EntityPatch):
    s = S(cid)
    patch = {k: v for k, v in body.fields.items() if k in EDITABLE}
    if not patch:
        raise HTTPException(400, "Ningún campo editable")
    return s.update(eid, patch, actor="hugo", summary=f"Hugo editó {eid}: {', '.join(patch)}", verb="edited")


class ActionBody(BaseModel):
    payload: dict = {}


@app.post("/api/cases/{cid}/entities/{eid}/actions/{action}")
def entity_action(cid: str, eid: str, action: str, body: ActionBody):
    return actions.run(S(cid), eid, action, body.payload)


# ------------------------------------------------------------------------------------------ brief & framing
@app.get("/api/cases/{cid}/brief")
def brief_get(cid: str):
    s = S(cid)
    dm = s.meta().get("data_model")
    bound = None
    if dm:
        try:
            bound = datamodels.get(dm["id"]).summary() | {"bound_at": dm.get("bound_at")}
        except ValueError as e:
            bound = {**dm, "available": False, "note": str(e)}
    return {"brief": briefing.get(s), "view": briefing.view(s), "conversation": briefer.conversation(s),
            "phase": next(p for p in phases.phases_view(s) if p["id"] == "briefing"), "readiness": phases.readiness(s, "briefing"),
            "data_model": bound, "data_models": datamodels.available()}


@app.patch("/api/cases/{cid}/brief")
def brief_patch(cid: str, body: EntityPatch):
    return briefing.update(S(cid), body.fields, actor="hugo")


class BrieferTurn(BaseModel):
    message: str


@app.post("/api/cases/{cid}/briefer")
def briefer_turn(cid: str, body: BrieferTurn):
    return briefer.start_turn(S(cid), body.message)


@app.post("/api/cases/{cid}/briefer/{turn_id}/retry")
def briefer_retry(cid: str, turn_id: str):
    return briefer.retry_turn(S(cid), turn_id)


class SectionBody(BaseModel):
    value: list[str] | str


@app.put("/api/cases/{cid}/brief/sections/{key}")
def brief_section_set(cid: str, key: str, body: SectionBody):
    return briefing.set_section(S(cid), key, body.value, actor="hugo")


@app.post("/api/cases/{cid}/brief/sections/{key}/approve")
def brief_section_approve(cid: str, key: str):
    return briefing.approve(S(cid), key, actor="hugo")


@app.post("/api/cases/{cid}/brief/sections/{key}/discard")
def brief_section_discard(cid: str, key: str):
    return briefing.discard(S(cid), key, actor="hugo")


@app.post("/api/cases/{cid}/brief/approve-all")
def brief_approve_all(cid: str):
    return briefing.approve_all(S(cid), actor="hugo")


# ------------------------------------------------------------------------------------------ data models
@app.get("/api/datamodels")
def datamodels_list():
    return {"models": datamodels.available()}


@app.get("/api/datamodels/{mid}")
def datamodel_detail(mid: str):
    m = datamodels.get(mid)
    return {"catalog": m.catalog(), "checks": m.checks(), "summary": m.summary()}


@app.get("/api/datamodels/{mid}/sample")
def datamodel_sample(mid: str, table: str, limit: int = 20):
    return datamodels.get(mid).sample(table, limit=limit)


class QueryBody(BaseModel):
    sql: str
    limit: int = 500


@app.post("/api/datamodels/{mid}/query")
def datamodel_query(mid: str, body: QueryBody):
    return datamodels.get(mid).query(body.sql, limit=body.limit)


class BindBody(BaseModel):
    model_id: str


@app.post("/api/cases/{cid}/datamodel")
def case_datamodel_bind(cid: str, body: BindBody):
    return datamodels.bind(S(cid), body.model_id, actor="hugo")


@app.delete("/api/cases/{cid}/datamodel")
def case_datamodel_unbind(cid: str):
    datamodels.unbind(S(cid), actor="hugo")
    return {"ok": True}


@app.post("/api/cases/{cid}/entities/{eid}/verify")
def entity_verify(cid: str, eid: str):
    s = S(cid)
    e = s.require(eid)
    if e.get("type") != "table":
        raise HTTPException(400, "Solo las tablas de evidencia se comprueban contra el modelo de datos.")
    m = datamodels.for_case(s)
    if m is None and (s.meta().get("workspace") or {}).get("type") == "finora-eda":
        m = datamodels.get("finora")
    if m is None:
        raise HTTPException(400, "El caso no tiene modelo de datos: elígelo en Briefing.")
    res = m.verify_table(e)
    s.update(eid, {"verification": {**res, "model": m.id, "at": now_iso()}},
             actor="hugo", material=False, verb="verified", summary=f"{eid} comprobada contra {m.label}: {res['detail']}")
    return res


@app.get("/api/cases/{cid}/framing")
def framing_get(cid: str):
    s = S(cid)
    return {"framing": framing_doc.state(s), "shaping": shaping.state(s), "conversation": framer.conversation(s),
            "counts": framing_doc.ledger_counts(s), "document": s.read_text("framing/current.md"),
            "phase": next(p for p in phases.phases_view(s) if p["id"] == "framing"), "readiness": phases.readiness(s, "framing"),
            "language": s.meta().get("language") or {}, "modes": framer.MODES, "data_model": s.meta().get("data_model")}


class FramingPatch(BaseModel):
    executive_question: str | None = None
    choose_frame: str | None = None
    remove: dict | None = None      # {"list": "should_not_claim", "index": 2}


@app.patch("/api/cases/{cid}/framing")
def framing_patch(cid: str, body: FramingPatch):
    s = S(cid)
    fr = s.read_data("framing/current.yaml", {}) or cases.empty_framing()
    changed = []
    if body.executive_question is not None and body.executive_question.strip() != (fr.get("executive_question") or ""):
        if fr.get("executive_question"):
            fr.setdefault("executive_question_history", []).append({"text": fr["executive_question"], "by": "hugo"})
        fr["executive_question"] = body.executive_question.strip()
        changed.append("pregunta ejecutiva")
    if body.choose_frame:
        for f in fr.get("candidate_frames") or []:
            if f.get("name") == body.choose_frame:
                f["chosen"] = not f.get("chosen")
                changed.append(f"frame «{f['name']}» {'elegido' if f['chosen'] else 'descartado'}")
                if f["chosen"]:
                    decisions.record_decision(s, title=f"Frame elegido: {f['name']}", context=f.get("description", ""), options={},
                                              agent_recommendation="", user_choice=f["name"], user_rationale="",
                                              affected_items=[], downstream_impact="", kind="framework", phase="framing", actor="hugo")
    if body.remove:
        lst = fr.get(body.remove.get("list")) or []
        i = int(body.remove.get("index", -1))
        if 0 <= i < len(lst):
            lst.pop(i)
            changed.append(f"quitado de {body.remove.get('list')}")
    framing_doc.save(s, fr, actor="hugo", summary="Hugo editó el framing: " + ", ".join(changed or ["sin cambios"]))
    if s.meta()["phases"]["framing"].get("status") == "ready" and changed:
        phases.set_status(s, "framing", "needs_review", actor="hugo", note="el framing cambió después de aprobarse")
    return framing_doc.state(s)


class FramerTurn(BaseModel):
    message: str
    mode: str = "organize"


@app.get("/api/cases/{cid}/shaping")
def shaping_get(cid: str):
    return shaping.state(S(cid))


@app.post("/api/cases/{cid}/shaping/{key}/approve")
def shaping_approve(cid: str, key: str):
    return shaping.approve(S(cid), key, actor="hugo")


@app.post("/api/cases/{cid}/shaping/{key}/discard")
def shaping_discard(cid: str, key: str):
    return shaping.discard(S(cid), key, actor="hugo")


@app.put("/api/cases/{cid}/shaping/{key}")
def shaping_set(cid: str, key: str, body: dict):
    return shaping.set_section(S(cid), key, body, actor="hugo")


@app.delete("/api/cases/{cid}/shaping/{key}")
def shaping_remove(cid: str, key: str):
    return shaping.remove(S(cid), key, actor="hugo")


@app.post("/api/cases/{cid}/shaping/plan")
def shaping_plan(cid: str):
    return planner.start(S(cid), actor="hugo")


@app.post("/api/cases/{cid}/shaping/approve-all")
def shaping_approve_all(cid: str):
    return shaping.approve_all(S(cid), actor="hugo")


@app.post("/api/cases/{cid}/shaping/migrate")
def shaping_migrate(cid: str):
    return shaping.migrate(S(cid), actor="hugo")


class SendBody(BaseModel):
    via: str = ""          # when Hugo delegated the click (e.g. "delegado a Claude en el chat"): recorded on the research


@app.post("/api/cases/{cid}/shaping/tasks/{task_id}/send")
def shaping_send(cid: str, task_id: str, body: SendBody | None = None):
    return shaping.send_task(S(cid), task_id, actor="hugo", via=(body.via if body else ""))


@app.post("/api/cases/{cid}/shaping/tasks/send-all")
def shaping_send_all(cid: str, body: SendBody | None = None):
    return {"sent": shaping.send_all(S(cid), actor="hugo", via=(body.via if body else ""))}


@app.post("/api/cases/{cid}/framer")
def framer_turn(cid: str, body: FramerTurn):
    return framer.start_turn(S(cid), body.message, body.mode)


@app.post("/api/cases/{cid}/framer/{turn_id}/retry")
def framer_retry(cid: str, turn_id: str):
    return framer.retry_turn(S(cid), turn_id)


@app.post("/api/cases/{cid}/framing/research-needed/{rn}/send")
def research_needed_send(cid: str, rn: str):
    s = S(cid)
    fr = s.read_data("framing/current.yaml", {}) or {}
    item = next((r for r in fr.get("research_needed") or [] if r.get("id") == rn), None)
    if not item:
        raise HTTPException(404, "Research necesario no encontrado")
    res = research.create_request(s, item["question"], links=item.get("links") or [], actor="hugo", force_purpose=bool(item.get("links")))
    item.update({"status": "sent", "research_id": res["research"]["id"]})
    framing_doc.save(s, fr, actor="hugo", summary=f"{rn} enviado a Research como {res['research']['id']}", material=False)
    return res


# ------------------------------------------------------------------------------------------ phases (human gates)
class GateBody(BaseModel):
    note: str = ""
    reason: str = ""


@app.get("/api/cases/{cid}/phases")
def phases_get(cid: str):
    s = S(cid)
    return {"phases": phases.phases_view(s), "readiness": {p: phases.readiness(s, p) for p in PHASES}}


@app.get("/api/cases/{cid}/phases/{phase}/impact")
def phase_impact(cid: str, phase: str):
    return phases.impact(S(cid), phase)


@app.post("/api/cases/{cid}/phases/{phase}/ready")
def phase_ready(cid: str, phase: str, body: GateBody):
    return phases.mark_ready(S(cid), phase, actor="hugo", note=body.note)


@app.post("/api/cases/{cid}/phases/{phase}/reopen")
def phase_reopen(cid: str, phase: str, body: GateBody):
    if not body.reason.strip():
        raise HTTPException(400, "Reabrir requiere una razón.")
    return phases.reopen(S(cid), phase, actor="hugo", reason=body.reason)


@app.get("/api/cases/{cid}/snapshots")
def snapshots(cid: str):
    return {"snapshots": phases.snapshot_list(S(cid))}


# ------------------------------------------------------------------------------------------ chief of staff
@app.get("/api/cases/{cid}/cos/room")
def cos_room(cid: str):
    return cos.room(S(cid))


class Ask(BaseModel):
    question: str
    context_id: str | None = None


@app.post("/api/cases/{cid}/cos/ask")
def cos_ask(cid: str, body: Ask):
    return cos.submit_ask(S(cid), body.question, context_id=body.context_id)


class DismissBody(BaseModel):
    ids: list[str] = []                # empty = every open alert
    note: str = ""


@app.post("/api/cases/{cid}/cos/alerts/dismiss")
def cos_dismiss(cid: str, body: DismissBody):
    return cos.dismiss_alerts(S(cid), ids=body.ids or None, rationale=body.note)


@app.get("/api/cases/{cid}/cos/conversation")
def cos_conv(cid: str):
    return {"conversation": cos.conversation(S(cid))}


class DecisionBody(BaseModel):
    title: str
    context: str = ""
    options: dict = {}
    choice: str = ""
    rationale: str = ""
    affected: list[str] = []
    kind: str = "other"


@app.post("/api/cases/{cid}/decisions")
def decision_create(cid: str, body: DecisionBody):
    return decisions.record_decision(S(cid), title=body.title, context=body.context, options=body.options, agent_recommendation="",
                                     user_choice=body.choice or body.title, user_rationale=body.rationale,
                                     affected_items=body.affected, downstream_impact="", kind=body.kind, actor="hugo")


# ------------------------------------------------------------------------------------------ research
class RouteBody(BaseModel):
    question: str
    links: list[str] = []


@app.post("/api/cases/{cid}/research/route")
def research_route(cid: str, body: RouteBody):
    return research.heuristic_route(S(cid), body.question, body.links)


class ResearchBody(BaseModel):
    question: str
    links: list[str] = []
    route: dict | None = None
    force: bool = False
    via: str = ""                     # launched for Hugo by someone he asked (the log says so)


@app.post("/api/cases/{cid}/research")
def research_create(cid: str, body: ResearchBody):
    out = research.create_request(S(cid), body.question, links=body.links, route=body.route, actor="hugo", force_purpose=body.force,
                                  via=body.via)
    if body.via:
        S(cid).update(out["research"]["id"], {"requested_via": body.via}, actor="system", material=False)
    return out


# ------------------------------------------------------------------------------------------ analytics
@app.get("/api/cases/{cid}/analytics")
def analytics_info(cid: str):
    s = S(cid)
    return {"workspace": analytics.info(s), "runs": analytics.runs(s)}


@app.get("/api/cases/{cid}/analytics/runs/{inv}")
def analytics_run(cid: str, inv: str):
    return analytics.run_detail(S(cid), inv)


@app.post("/api/cases/{cid}/analytics/runs/{inv}/claims/{claim}/promote")
def analytics_promote(cid: str, inv: str, claim: str):
    return {"finding": analytics.promote_claim(S(cid), inv, claim)}


# ------------------------------------------------------------------------------------------ story
@app.get("/api/cases/{cid}/story")
def story_get(cid: str):
    s = S(cid)
    pkg = s.read_data("story/package.yaml")
    ents = s.all()
    claims = [{**e, "strength": cos.claim_strength(s, e, ents)} for e in s.list("claim") if e.get("status") != "superseded"]
    return {"package": pkg, "claims": claims, "phase": next(p for p in phases.phases_view(s) if p["id"] == "story"),
            "readiness": phases.readiness(s, "story"), "current_md": s.read_text("story/current.md")}


class PackageBody(BaseModel):
    instructions: str = ""
    draft: bool = False
    via: str = ""                     # who wrote the instructions when Hugo delegated it (never passed off as his words)


@app.post("/api/cases/{cid}/story/package")
def story_package(cid: str, body: PackageBody):
    return story.submit_package(S(cid), instructions=body.instructions, draft=body.draft, via=body.via)


class AcceptStoryBody(BaseModel):
    claim_ids: list[str] = []          # empty = every claim of the package
    note: str = ""


@app.post("/api/cases/{cid}/story/accept")
def story_accept(cid: str, body: AcceptStoryBody):
    s = S(cid)
    ids = body.claim_ids or [c["claim_id"] for c in (s.read_data("story/package.yaml") or {}).get("claims") or []]
    return story.accept_with_evidence(s, ids, note=body.note)


@app.post("/api/cases/{cid}/story/validate")
def story_validate(cid: str):
    return story.revalidate(S(cid))


# ------------------------------------------------------------------------------------------ slides (Visual Storyteller)
@app.get("/api/cases/{cid}/slides")
def slides_get(cid: str):
    s = S(cid)
    return {"decks": storyteller.decks(s), "directions": storyteller.DIRECTIONS, "links": storyteller.ensure_links(),
            "style": s.meta().get("slides_style") or {}, "fonts": {"vendored": slidestyle.VENDORED, "suggested": slidestyle.SUGGESTED},
            "color_keys": slidestyle.COLOR_KEYS,
            "phase": next(p for p in phases.phases_view(s) if p["id"] == "slides"), "slides": [_compact(e) | {
                "claim_id": e.get("claim_id"), "deck": e.get("deck"), "render": e.get("render"), "qa_verdict": e.get("qa_verdict"),
                "composition": e.get("composition")} for e in s.list("slide")]}


class HandoffBody(BaseModel):
    direction: str = "editorial"
    critic: bool = True
    run: bool = True
    style: dict | None = None
    reuse_from: str = ""               # a previous deck whose unchanged slides the Storyteller reuses
    via: str = ""


@app.put("/api/cases/{cid}/slides/style")
def slides_style_save(cid: str, body: dict):
    s = S(cid)
    st = slidestyle.normalize(body)
    meta = s.meta()
    meta["slides_style"] = {**st, "saved_at": now_iso()}
    s.save_meta(meta)
    s.log("hugo", "updated", [], "Guía de formato de slides actualizada", material=False)
    return meta["slides_style"]


@app.post("/api/cases/{cid}/slides/handoff")
def slides_handoff(cid: str, body: HandoffBody):
    s = S(cid)
    rec = storyteller.prepare(s, direction=body.direction, critic=body.critic, style=body.style, reuse_from=body.reuse_from)
    out = {"deck": rec}
    if body.run:
        out.update(storyteller.submit_run(s, rec["id"], via=body.via))
    return out


class RunBody(BaseModel):
    via: str = ""


@app.post("/api/cases/{cid}/slides/{deck_id}/run")
def slides_run(cid: str, deck_id: str, body: RunBody | None = None):
    return storyteller.submit_run(S(cid), deck_id, via=(body.via if body else ""))


@app.post("/api/cases/{cid}/slides/{deck_id}/import")
def slides_import(cid: str, deck_id: str):
    return storyteller.import_deck(S(cid), deck_id)


@app.get("/api/cases/{cid}/slides/{deck_id}/files")
def deck_slide_files(cid: str, deck_id: str):
    return {"files": deckedit.files(S(cid), deck_id)}


class OrderBody(BaseModel):
    order: list[str]
    via: str = ""


@app.post("/api/cases/{cid}/slides/{deck_id}/order")
def deck_order(cid: str, deck_id: str, body: OrderBody):
    return deckedit.reorder(S(cid), deck_id, body.order, via=body.via)


class RevisionBody(BaseModel):
    changes: list                      # [{file: "NN.html", request: "what Hugo wants changed"}]
    via: str = ""


@app.post("/api/cases/{cid}/slides/{deck_id}/revise")
def deck_revise(cid: str, deck_id: str, body: RevisionBody):
    return storyteller.submit_revision(S(cid), deck_id, body.changes, via=body.via)


class SlideTextBody(BaseModel):
    file: str
    edits: list                        # {k, html} for text in the markup · {old, new, id} for text a script paints
    source: str = ""                   # the hash of the slide the editor opened (a stale editor cannot overwrite)


@app.put("/api/cases/{cid}/slides/{deck_id}/text")
def deck_text(cid: str, deck_id: str, body: SlideTextBody):
    return deckedit.save_text(S(cid), deck_id, body.file, body.edits, source=body.source)


class LocateBody(BaseModel):
    file: str
    texts: list


@app.post("/api/cases/{cid}/slides/{deck_id}/locate")
def deck_locate(cid: str, deck_id: str, body: LocateBody):
    return {"found": deckedit.locate(S(cid), deck_id, body.file, body.texts)}


class DividerBody(BaseModel):
    title: str
    color: str
    after: str = ""                    # the slide file it goes after; empty = at the end
    via: str = ""


@app.post("/api/cases/{cid}/slides/{deck_id}/divider")
def deck_divider(cid: str, deck_id: str, body: DividerBody):
    return deckedit.add_divider(S(cid), deck_id, body.title, body.color, after=body.after, via=body.via)


class CopySlideBody(BaseModel):
    from_deck: str                     # another deck of the case
    file: str                          # its slide file
    after: str = ""                    # the slide file it goes after in this deck; empty = at the end
    via: str = ""


@app.post("/api/cases/{cid}/slides/{deck_id}/copy")
def deck_copy(cid: str, deck_id: str, body: CopySlideBody):
    return deckedit.copy_slide(S(cid), deck_id, body.from_deck, body.file, after=body.after, via=body.via)


@app.post("/api/cases/{cid}/slides/{deck_id}/pdf")
def deck_pdf(cid: str, deck_id: str):
    return deckedit.rebuild_pdf(S(cid), deck_id)


@app.get("/case-files/{cid}/decks/{slug}/{path:path}", include_in_schema=False)
def deck_files(cid: str, slug: str, path: str):
    m = re.fullmatch(r"slides/(\d{2})\.edit\.html", path or "")
    if m:                              # the slide with its editable text marked, served next to it so relative paths hold
        return HTMLResponse(deckedit.preview(S(cid), slug, f"{m.group(1)}.html"), headers={"Cache-Control": "no-store"})
    p = storyteller.deck_file(S(cid), slug, path or "index.html")
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(p, media_type=mimetypes.guess_type(str(p))[0] or "application/octet-stream")


@app.get("/case-files/{cid}/sources/{name}", include_in_schema=False)
def brief_source(cid: str, name: str):
    s = S(cid)
    p = (s.root / "brief" / "sources" / name).resolve()
    if (s.root / "brief" / "sources").resolve() not in p.parents or not p.exists():
        raise HTTPException(404, "No encontrado")
    return FileResponse(p)


# ------------------------------------------------------------------------------------------ artifacts / files
ARTIFACT_ROOTS = ["brain.md", "case.yaml", "README.md", "brief", "framing", "questions", "hypotheses", "research", "evidence",
                  "decisions", "cos", "story", "slides", "artifacts", "audit", "snapshots"]


@app.get("/api/cases/{cid}/tree")
def tree(cid: str):
    s = S(cid)
    out = []
    for name in ARTIFACT_ROOTS:
        p = s.root / name
        if not p.exists():
            continue
        if p.is_file():
            out.append({"path": name, "type": "file", "size": p.stat().st_size})
            continue
        children = []
        for c in sorted(p.rglob("*")):
            rel = str(c.relative_to(s.root))
            if c.is_dir() or "/decks/" in rel and ("/assets/" in rel or "/renders/" in rel or "/directions/" in rel):
                continue
            if rel.startswith("snapshots/") and rel.count("/") > 2:
                continue
            if rel.startswith("audit/versions/") or rel.startswith("audit/prompts/"):
                continue
            children.append({"path": rel, "size": c.stat().st_size})
        out.append({"path": name, "type": "dir", "children": children[:600], "count": len(children)})
    return {"tree": out}


@app.get("/api/cases/{cid}/files")
def file_get(cid: str, path: str):
    s = S(cid)
    p = s.path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(404, "Archivo no encontrado")
    if p.stat().st_size > 3_000_000:
        raise HTTPException(413, "Archivo demasiado grande para la vista previa")
    text = p.read_text(encoding="utf-8", errors="replace")
    data = None
    if p.suffix in (".yaml", ".yml"):
        try:
            data = yaml_load(text)
        except Exception:  # noqa: BLE001
            data = None
    elif p.suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
    elif p.suffix == ".jsonl":
        data = read_jsonl(p, limit=300)
    return {"path": path, "suffix": p.suffix, "text": text if p.suffix not in (".json",) or data is None else None, "data": data}


@app.get("/api/cases/{cid}/runs/{run_id}")
def run_get(cid: str, run_id: str):
    s = S(cid)
    r = read_json(s.root / "audit" / "runs" / f"{run_id}.json")
    if not r:
        raise HTTPException(404, "Corrida no encontrada")
    if r.get("system_prompt"):
        pp = s.root / r["system_prompt"]
        r["system_prompt_text"] = pp.read_text(encoding="utf-8") if pp.exists() else None
    return r


@app.get("/api/cases/{cid}/runs")
def runs_list(cid: str, agent: str | None = None, limit: int = 20):
    s = S(cid)
    d = s.root / "audit" / "runs"
    out = []
    if d.exists():
        for p in sorted(d.glob("RUN-*.json"), reverse=True):
            r = read_json(p) or {}
            if agent and r.get("agent") != agent:
                continue
            out.append({k: r.get(k) for k in ("run_id", "agent", "role", "purpose", "started_at", "duration_ms", "status", "cost_usd",
                                               "model", "effort", "skills", "lenses", "tools", "error")})
            if len(out) >= limit:
                break
    return {"runs": out}


# ------------------------------------------------------------------------------------------ activity, jobs, SSE
@app.get("/api/cases/{cid}/activity")
def activity(cid: str, limit: int = 120):
    return {"activity": list(reversed(S(cid).activity(limit)))}


@app.get("/api/cases/{cid}/jobs")
def jobs_list(cid: str):
    return {"jobs": jobs.list_jobs(cid)}


@app.get("/api/cases/{cid}/jobs/{jid}")
def job_get(cid: str, jid: str):
    j = jobs.get(cid, jid)
    if not j:
        raise HTTPException(404, "Trabajo no encontrado")
    return j


@app.post("/api/cases/{cid}/jobs/{jid}/retry")
def job_retry(cid: str, jid: str):
    return {"job": jobs.retry(cid, jid).public()}


@app.get("/api/cases/{cid}/events")
async def events(cid: str, request: Request):
    S(cid)
    q = bus.subscribe(cid)

    async def gen():
        try:
            yield "retry: 3000\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    ev = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            bus.unsubscribe(cid, q)

    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ------------------------------------------------------------------------------------------ command layer & search
class CommandBody(BaseModel):
    text: str
    context_id: str | None = None


@app.post("/api/cases/{cid}/command")
async def command(cid: str, body: CommandBody):
    s = S(cid)
    out = commands.route(s, body.text, context_id=body.context_id)
    if out["action"].get("kind") == "classify":
        out = await commands.classify(s, body.text, context_id=body.context_id)
    return out


@app.get("/api/cases/{cid}/search")
def search_ep(cid: str, q: str = ""):
    return {"results": search.search(S(cid), q), "commands": [c for c in commands.COMMANDS
                                                              if not q or q.lower() in (c["label"] + " " + c["hint"]).lower()]}


@app.get("/api/cases/{cid}/agents")
def case_agents(cid: str):
    s = S(cid)
    acts = s.activity(400)
    running = jobs.running(cid)
    js = jobs.list_jobs(cid, limit=60)
    alerts_open = len([x for x in s.list("alert") if x.get("status") == "open"])
    out = {}
    for a in agents_base.AGENTS:
        mine = [x for x in acts if x.get("actor") == a or (a == "analytics" and x.get("actor") in ("analytics",))]
        run = [j for j in running if j.get("agent") == a]
        out[a] = {"status": "running" if run else ("waiting" if a == "cos" and alerts_open else "idle"),
                  "current_task": run[0]["title"] if run else None,
                  "recent": list(reversed(mine[-8:])),
                  "artifacts": sorted({t for x in mine for t in x.get("targets") or [] if type_of(t)})[-12:],
                  "jobs": [j for j in js if j.get("agent") == a][:5]}
    return {"agents": out}


@app.post("/api/cases/{cid}/brain/refresh")
def brain_refresh(cid: str):
    brain.update(S(cid), "regeneración manual")
    return {"ok": True}
