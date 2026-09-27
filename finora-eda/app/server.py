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

from agent.config import DB_PATH, GOLDEN, ROOT, RUNS
from agent.orchestrator import run
from agent.state import Investigation
from agent.warehouse import build

GOLDEN_Q = {"Q2": "¿Por qué disminuyó el MRR por cliente?"}
LIVE: dict[str, Investigation] = {}
TASKS: set = set()


@asynccontextmanager
async def lifespan(_app):
    if not DB_PATH.exists():
        build()
    yield


app = FastAPI(title="Finora · workspace agentic (local)", lifespan=lifespan)


class NewInvestigation(BaseModel):
    pregunta_id: str | None = None
    pregunta: str | None = None


@app.get("/", response_class=HTMLResponse)
def workspace():
    html = (ROOT / "finora_eda.html").read_text(encoding="utf-8")
    flag = '<script>window.FINORA_LIVE = {"api": "/api", "preguntas": ["Q2"]};</script>\n'
    return html.replace("<script>\nconst DATA", flag + "<script>\nconst DATA", 1)


@app.post("/api/investigations")
async def start(body: NewInvestigation):
    if any(i.status not in ("publicada", "error") for i in LIVE.values()):
        raise HTTPException(409, "Ya hay una investigación en curso; espera a que termine.")
    if body.pregunta_id and body.pregunta_id not in GOLDEN_Q:
        raise HTTPException(400, f"En esta slice solo la pregunta Q2 corre en vivo (recibí {body.pregunta_id}).")
    q = GOLDEN_Q.get(body.pregunta_id or "", body.pregunta or "")
    if not q.strip():
        raise HTTPException(400, "Falta la pregunta.")
    inv = Investigation(pregunta=q, pregunta_id=body.pregunta_id)
    LIVE[inv.id] = inv
    task = asyncio.create_task(run(inv))
    TASKS.add(task)
    task.add_done_callback(TASKS.discard)
    return {"id": inv.id}


def _load(inv_id: str) -> dict:
    if inv_id in LIVE:
        return LIVE[inv_id].to_dict()
    p = RUNS / f"{inv_id}.json"
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


@app.get("/api/golden/{qid}")
def golden(qid: str):
    p = GOLDEN / f"{qid}.json"
    if not p.exists():
        raise HTTPException(404, "No hay investigación dorada para esa pregunta.")
    return json.loads(p.read_text(encoding="utf-8"))
