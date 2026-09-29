"""Background jobs for agent work (framer turns, research, COS assessments, story package, slides).

A job keeps its request (kind + params) on disk before it runs, so a failure or a server restart never loses the
request: failed/interrupted jobs can be retried with the same params. Progress events stream to the UI.
"""
from __future__ import annotations

import asyncio
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Awaitable, Callable

from . import bus, cases
from .llm import AgentError
from .util import now_iso, read_json, stamp, write_json

Handler = Callable[["Job", Any], Awaitable[Any]]
HANDLERS: dict[str, Handler] = {}
LIVE: dict[str, "Job"] = {}
TASKS: set[asyncio.Task] = set()


def handler(kind: str):
    def deco(fn: Handler):
        HANDLERS[kind] = fn
        return fn
    return deco


@dataclass
class Job:
    id: str
    case_id: str
    kind: str
    title: str
    params: dict
    agent: str = ""
    status: str = "queued"            # queued · running · succeeded · failed · interrupted · cancelled
    created_at: str = field(default_factory=now_iso)
    started_at: str | None = None
    finished_at: str | None = None
    attempts: int = 0
    progress: list = field(default_factory=list)
    result: Any = None
    error: str | None = None
    error_kind: str | None = None
    retry_of: str | None = None

    def public(self) -> dict:
        d = asdict(self)
        d["progress"] = self.progress[-60:]
        return d

    def path(self):
        return cases.get(self.case_id).root / "audit" / "jobs" / f"{self.id}.json"

    def save(self):
        write_json(self.path(), self.public() | {"progress": self.progress[-200:]})

    async def event(self, kind: str, data: dict | None = None):
        ev = {"t": now_iso(), "kind": kind, **(data or {})}
        self.progress.append(ev)
        bus.publish(self.case_id, {"kind": "job", "job": {"id": self.id, "kind": self.kind, "title": self.title,
                                                          "agent": self.agent, "status": self.status}, "event": ev})


def submit(case_id: str, kind: str, title: str, params: dict, *, agent: str = "", retry_of: str | None = None) -> Job:
    if kind not in HANDLERS:
        raise ValueError(f"No hay handler para jobs de tipo {kind}")
    job = Job(id=f"JOB-{stamp()}-{uuid.uuid4().hex[:4]}", case_id=case_id, kind=kind, title=title, params=params,
              agent=agent, retry_of=retry_of)
    job.save()                               # the request is on disk before anything runs
    LIVE[job.id] = job
    _spawn(job)
    bus.publish(case_id, {"kind": "job", "job": {"id": job.id, "kind": kind, "title": title, "agent": agent,
                                                 "status": job.status}, "event": {"kind": "queued"}})
    return job


def _spawn(job: Job) -> None:
    """Start the job on the server's event loop, whether we are called from the loop or from a worker thread
    (FastAPI runs sync endpoints in a threadpool)."""
    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None
    loop = bus._loop or running

    def start():
        task = loop.create_task(_run(job))
        TASKS.add(task)
        task.add_done_callback(TASKS.discard)

    if loop is None:
        raise RuntimeError("No hay event loop del servidor para lanzar trabajos.")
    if running is loop:
        start()
    else:
        loop.call_soon_threadsafe(start)


async def _run(job: Job):
    store = cases.get(job.case_id)
    job.status, job.started_at = "running", now_iso()
    job.attempts += 1
    await job.event("running")
    job.save()
    try:
        job.result = await HANDLERS[job.kind](job, job.params)
        job.status = "succeeded"
        await job.event("succeeded")
    except asyncio.CancelledError:
        job.status, job.error, job.error_kind = "interrupted", "El servidor se detuvo durante el trabajo; la solicitud se conservó.", "interrupted"
        await job.event("interrupted")
        job.finished_at = now_iso()
        job.save()
        raise
    except AgentError as e:
        job.status, job.error, job.error_kind = "failed", str(e), e.kind
        store.log(job.agent or "system", "failed", [job.id], f"{job.title}: falló ({e.kind}) — la solicitud se conservó para reintentar",
                  data={"error": str(e)[:500], "run_id": e.run_id})
        await job.event("failed", {"error": str(e)[:500], "error_kind": e.kind})
    except Exception as e:  # noqa: BLE001 - any failure is preserved with the request
        job.status, job.error, job.error_kind = "failed", f"{type(e).__name__}: {e}", "unknown"
        store.log(job.agent or "system", "failed", [job.id], f"{job.title}: falló — la solicitud se conservó para reintentar",
                  data={"error": traceback.format_exc()[-1500:]})
        await job.event("failed", {"error": str(e)[:500]})
    job.finished_at = now_iso()
    job.save()


def get(case_id: str, job_id: str) -> dict | None:
    if job_id in LIVE:
        return LIVE[job_id].public()
    return read_json(cases.get(case_id).root / "audit" / "jobs" / f"{job_id}.json")


def list_jobs(case_id: str, limit: int = 40) -> list[dict]:
    d = cases.get(case_id).root / "audit" / "jobs"
    out = {}
    if d.exists():
        for p in sorted(d.glob("JOB-*.json"), reverse=True)[:limit]:
            j = read_json(p)
            if j:
                out[j["id"]] = j
    for j in LIVE.values():
        if j.case_id == case_id:
            out[j.id] = j.public()
    return sorted(out.values(), key=lambda j: j["created_at"], reverse=True)[:limit]


def retry(case_id: str, job_id: str) -> Job:
    old = get(case_id, job_id)
    if not old:
        raise ValueError("Job no encontrado")
    if old["status"] in ("queued", "running"):
        raise ValueError("Ese trabajo sigue en curso")
    return submit(case_id, old["kind"], old["title"], old["params"], agent=old.get("agent", ""), retry_of=job_id)


def running(case_id: str) -> list[dict]:
    return [j.public() for j in LIVE.values() if j.case_id == case_id and j.status in ("queued", "running")]


def mark_interrupted_on_boot() -> int:
    """Jobs left as queued/running by a previous process are interrupted (their request stays retriable)."""
    n = 0
    for c in cases.list_cases():
        d = cases.get(c["id"]).root / "audit" / "jobs"
        if not d.exists():
            continue
        for p in d.glob("JOB-*.json"):
            j = read_json(p)
            if j and j.get("status") in ("queued", "running"):
                j["status"], j["error"], j["error_kind"] = "interrupted", "El servidor se reinició durante el trabajo; la solicitud se conservó.", "interrupted"
                j["finished_at"] = now_iso()
                write_json(p, j)
                n += 1
    return n
