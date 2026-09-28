"""Servidor local de la slice (arquitectura v1.2 §8, app/api): workspace + investigaciones en vivo.

    .venv/bin/python -m uvicorn app.server:app --host 127.0.0.1 --port 8765

Solo escucha en 127.0.0.1. Corre una investigación en vivo a la vez (usa tu sesión de Claude Code).
"""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from agent import caso
from agent import narrative as nar
from agent.config import DB_PATH, GOLDEN, ROOT, RUNS
from agent.orchestrator import run
from agent.state import Investigation
from agent.warehouse import build

GOLDEN_Q = {"Q2": "¿Por qué disminuyó el MRR por cliente?"}
LIVE: dict[str, Investigation] = {}
TASKS: set = set()
BUSY_NARRATIVES: set = set()


@asynccontextmanager
async def lifespan(_app):
    if not DB_PATH.exists():
        build()
    yield


app = FastAPI(title="Finora · workspace agentic (local)", lifespan=lifespan)


class NewInvestigation(BaseModel):
    pregunta_id: str | None = None
    pregunta: str | None = None
    contexto: dict | None = None          # pieza de narrativa desde la que se profundiza


class NewNarrative(BaseModel):
    titulo: str
    audiencia: str | None = None
    objetivo: str = ""
    contexto: str = ""


class NarrativePatch(BaseModel):
    titulo: str | None = None
    audiencia: str | None = None
    objetivo: str | None = None
    contexto: str | None = None
    orden: list[str] | None = None
    piezas: list[dict] | None = None


class MergeNarratives(BaseModel):
    ids: list[str]
    titulo: str = ""


@app.get("/", response_class=HTMLResponse)
def workspace():
    html = (ROOT / "finora_eda.html").read_text(encoding="utf-8")
    flag = '<script>window.FINORA_LIVE = {"api": "/api", "preguntas": ["Q2"], "libre": true, "narrativas": true, "caso": true};</script>\n'
    return html.replace("<script>\nconst DATA", flag + "<script>\nconst DATA", 1)


@app.post("/api/investigations")
async def start(body: NewInvestigation):
    if any(i.status not in ("publicada", "error") for i in LIVE.values()):
        raise HTTPException(409, "Ya hay una investigación en curso; espera a que termine.")
    if body.pregunta_id in caso.QUESTIONS:
        # pregunta del caso: las bloqueadas no se investigan (no hay sustituto válido); su respuesta dice qué falta
        cq = caso.QUESTIONS[body.pregunta_id]
        if not caso.can_investigate(body.pregunta_id):
            raise HTTPException(409, f"{body.pregunta_id} está bloqueada: no se investiga con sustitutos. Abre la pregunta para ver qué evidencia falta.")
        inv = Investigation(pregunta=cq["pregunta"], pregunta_id=cq["id"], caso_id=cq["id"], playbook_id="libre", lente=caso.lens(cq))
        return _launch(inv)
    qid = body.pregunta_id if body.pregunta_id in GOLDEN_Q else None
    q = GOLDEN_Q[qid] if qid else (body.pregunta or "").strip()
    if not q:
        raise HTTPException(400, "Falta la pregunta.")
    if len(q) > 3000:
        raise HTTPException(400, "La pregunta es demasiado larga (máximo 3.000 caracteres).")
    # preguntas libres: el agente elige el playbook en el encuadre (arpa_decline o libre)
    ctx = None
    if body.contexto:
        c = body.contexto
        ctx = {"titulo": str(c.get("titulo") or "")[:300], "texto": str(c.get("texto") or "")[:4000],
               "nota": str(c.get("nota") or "")[:1000],
               "claim_ids": [str(x)[:40] for x in (c.get("claim_ids") or [])][:20],
               "narrativa_id": str(c.get("narrativa_id") or "")[:40], "pieza_id": str(c.get("pieza_id") or "")[:10]}
    inv = Investigation(pregunta=q, pregunta_id=qid, playbook_id="arpa_decline" if qid == "Q2" else "libre", contexto=ctx)
    return _launch(inv)


def _launch(inv: Investigation) -> dict:
    LIVE[inv.id] = inv
    task = asyncio.create_task(run(inv))
    TASKS.add(task)
    task.add_done_callback(TASKS.discard)
    return {"id": inv.id}


def _load(inv_id: str) -> dict:
    # en curso: el estado vivo en memoria; terminada: el archivo guardado (refleja revisual/recompose posteriores)
    p = RUNS / f"{inv_id}.json"
    if inv_id in LIVE and (LIVE[inv_id].status not in ("publicada", "error") or not p.exists()):
        return LIVE[inv_id].to_dict()
    if not p.exists():
        raise HTTPException(404, "Investigación no encontrada.")
    return json.loads(p.read_text(encoding="utf-8"))


@app.get("/api/investigations")
def list_runs():
    out = []
    for p in sorted(RUNS.glob("INV-*.json"), reverse=True)[:20]:
        d = json.loads(p.read_text(encoding="utf-8"))
        out.append({"id": d["id"], "pregunta": d["pregunta"], "status": d["status"], "finished_ms": d.get("finished_ms")})
    return out


@app.get("/api/investigations/{inv_id}")
def get_one(inv_id: str):
    return _load(inv_id)


@app.get("/api/investigations/{inv_id}/stream")
async def stream(inv_id: str):
    inv = LIVE.get(inv_id)
    if inv is None:
        raise HTTPException(404, "Solo se puede seguir en vivo una investigación iniciada en esta sesión del servidor.")

    async def events():
        sent = 0
        while True:
            while sent < len(inv.events):
                yield f"data: {json.dumps(inv.events[sent], ensure_ascii=False, default=str)}\n\n"
                sent += 1
            if inv.status in ("publicada", "error") and sent >= len(inv.events):
                return
            await asyncio.sleep(0.3)

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ------------------------------------------------------------------ preguntas del caso (W0–W7)
@app.get("/api/caso")
def caso_list():
    return {"preguntas": caso.statuses(LIVE)}


@app.get("/api/caso/{qid}")
def caso_get(qid: str):
    if qid not in caso.QUESTIONS:
        raise HTTPException(404, "Pregunta del caso desconocida.")
    if not caso.can_investigate(qid):
        return {"caso_id": qid, "bloqueada": True, "respuesta_caso": caso.blocked_answer(caso.QUESTIONS[qid])}
    d = caso.load_answer(qid)
    if not d:
        raise HTTPException(404, "Esta pregunta todavía no tiene respuesta.")
    return d


@app.get("/api/golden/{qid}")
def golden(qid: str):
    p = GOLDEN / f"{qid}.json"
    if not p.exists():
        raise HTTPException(404, "No hay investigación dorada para esa pregunta.")
    return json.loads(p.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ narrativas (preparar narrativa)
def _nar(fn, *a):
    try:
        return fn(*a)
    except KeyError:
        raise HTTPException(404, "Narrativa no encontrada.")
    except nar.NarrativeError as e:
        raise HTTPException(400, str(e))


@app.get("/api/narratives")
def narratives_list():
    return nar.list_all()


@app.post("/api/narratives")
def narratives_create(body: NewNarrative):
    return _nar(nar.create, body.titulo, body.audiencia, body.objetivo, body.contexto)


@app.post("/api/narratives/merge")
def narratives_merge(body: MergeNarratives):
    return _nar(nar.merge, body.ids, body.titulo)


@app.get("/api/narratives/{nid}")
def narratives_get(nid: str):
    return _nar(nar.load, nid)


@app.patch("/api/narratives/{nid}")
def narratives_patch(nid: str, body: NarrativePatch):
    return _nar(nar.update, nid, body.model_dump(exclude_none=True))


@app.delete("/api/narratives/{nid}")
def narratives_delete(nid: str):
    _nar(nar.delete, nid)
    return {"ok": True}


@app.post("/api/narratives/{nid}/piezas")
def narratives_add_piece(nid: str, body: dict):
    return _nar(nar.add_piece, nid, body)


@app.delete("/api/narratives/{nid}/piezas/{pid}")
def narratives_remove_piece(nid: str, pid: str):
    return _nar(nar.remove_piece, nid, pid)


async def _agent_step(nid: str, fn):
    if nid in BUSY_NARRATIVES:
        raise HTTPException(409, "El agente ya está trabajando en esta narrativa.")
    _nar(nar.load, nid)
    BUSY_NARRATIVES.add(nid)
    try:
        return await fn(nid)
    except nar.NarrativeError as e:
        raise HTTPException(400, str(e))
    finally:
        BUSY_NARRATIVES.discard(nid)


@app.post("/api/narratives/{nid}/esqueleto")
async def narratives_plan(nid: str):
    return await _agent_step(nid, nar.plan)


@app.post("/api/narratives/{nid}/consolidar")
async def narratives_consolidate(nid: str):
    return await _agent_step(nid, nar.consolidate)
