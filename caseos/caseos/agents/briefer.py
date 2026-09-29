"""Briefer — Brief Partner (agents/briefer.md).

One turn: Hugo's message → skills (brief-builder + clarification-protocol, business-case-partner when he pastes the
statement or reframes) → structured BrieferTurn → code guards → proposals stored as PENDING sections (briefing.propose)
→ conversation logged. Nothing is approved here: Hugo approves, edits or discards each section in the Briefing view.
"""
from __future__ import annotations

import uuid

from .. import briefing, cases, datamodels, jobs, language, skills
from ..llm import AgentError, RunSpec, get_llm
from ..store import CaseStore
from ..util import append_jsonl, clip, now_iso, read_jsonl, write_jsonl_replace
from . import base

CONV = "brief/conversation.jsonl"
_S = {"type": "string"}
_SA = {"type": "array", "items": _S}


def _obj(props: dict) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


SCHEMA = _obj({
    "reply": _S,
    "proposals": {"type": "array", "items": _obj({
        "section": {"type": "string", "enum": [s["key"] for s in briefing.SECTIONS]},
        "value": _SA, "hugo_wording": _S,
        "basis": {"type": "string", "enum": ["hugo", "enunciado", "inferido"]}, "why": _S})},
    "message_is_source_text": {"type": "boolean"},
    "question": _S,
    "language": _obj({"register": _S, "technical_level": _S, "formality": _S, "preserved_terms": _SA,
                      "introduced_terms": {"type": "array", "items": _obj({"term": _S, "plain": _S})}}),
})


# ------------------------------------------------------------------------------------------ context
def build_prompt(store: CaseStore, message: str) -> str:
    v = briefing.view(store)
    lines = ["## Brief actual (lo aprobado es lo que leen los demás agentes)"]
    for s in v["sections"]:
        val = s["value"]
        shown = "; ".join(val) if isinstance(val, list) else val
        state = {"approved": "APROBADO", "imported": "importado", "empty": "vacío"}[s["state"]]
        lines.append(f"- {s['key']} ({s['label']}{', requerido' if s.get('required') else ''}) [{state}]: {clip(shown, 900) or '—'}")
        if s["pending"]:
            pv = s["pending"]["value"]
            lines.append(f"    · propuesta pendiente de Hugo: {clip('; '.join(pv) if isinstance(pv, list) else pv, 600)}")
    dm = store.meta().get("data_model")
    lines += ["", "## Modelo de datos del caso"]
    if dm:
        try:
            m = datamodels.get(dm["id"])
            lines += [f"Elegido por Hugo: {m.label}. data_available ya viene de él (no lo reescribas):"] + [f"- {x}" for x in m.brief_lines()]
        except ValueError as e:
            lines.append(f"{dm.get('label')} (no disponible ahora: {e})")
    else:
        avail = [m for m in datamodels.available() if m.get("available")]
        lines.append("Ninguno elegido todavía." + (f" Disponibles para que Hugo elija en la vista: {', '.join(m['label'] for m in avail)}." if avail else ""))
    conv = [t for t in read_jsonl(store.root / CONV, limit=14) if t.get("status") == "done"][-6:]
    lines += ["", "## Conversación reciente"]
    for t in conv:
        lines.append(f"Hugo: {clip(t.get('message', ''), 700)}")
        lines.append(f"Briefer: {clip(t.get('reply', ''), 500)}")
    if not conv:
        lines.append("(primer turno)")
    lines += ["", "## Mensaje de Hugo", message.strip(), "",
              "Devuelve el BrieferTurn: propuestas solo de secciones que cambian; listas completas; base en cada una; una pregunta "
              "como máximo; si el mensaje es el enunciado pegado, message_is_source_text = true."]
    return "\n".join(lines)


def guard(out: dict, message: str) -> tuple[list[dict], list[str]]:
    """Clean proposals: known sections, non-empty values, the statement copied verbatim by code (never by the model)."""
    notes, props, seen = [], [], set()
    for p in out.get("proposals") or []:
        key = p.get("section")
        if key not in briefing.BY_KEY or key in seen:
            continue
        if key == "brief_text":
            continue                                   # the verbatim statement is Hugo's message itself, below
        val = [str(x).strip() for x in p.get("value") or [] if str(x).strip()]
        if not val:
            continue
        seen.add(key)
        props.append({**p, "value": val})
    if out.get("message_is_source_text"):
        props.append({"section": "brief_text", "value": [message.strip()], "hugo_wording": "", "basis": "enunciado",
                      "why": "Texto fuente pegado por Hugo; se guarda literal."})
    inferred = [briefing.BY_KEY[p["section"]]["label"] for p in props if p.get("basis") == "inferido"]
    if inferred:
        notes.append("Inferido por el agente (confírmalo): " + ", ".join(inferred) + ".")
    return props, notes


# ------------------------------------------------------------------------------------------ turns
def start_turn(store: CaseStore, message: str) -> dict:
    msg = (message or "").strip()
    if not msg:
        raise ValueError("Mensaje vacío")
    turn = {"turn_id": f"B{now_iso()[:19].replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:4]}", "ts": now_iso(),
            "message": msg[:20000], "status": "pending"}
    append_jsonl(store.root / CONV, turn)
    store.log("hugo", "said", ["brief"], f"Hugo al Briefer: {clip(msg, 110)}", material=False)
    try:
        job = jobs.submit(store.id, "briefer_turn", "Briefer", {"turn_id": turn["turn_id"]}, agent="briefer")
    except Exception as e:  # noqa: BLE001 - the message is kept; the turn can be retried
        _patch_turn(store, turn["turn_id"], {"status": "failed", "error": f"No se pudo lanzar el turno: {e}"})
        raise
    _patch_turn(store, turn["turn_id"], {"job_id": job.id})
    return {**turn, "job_id": job.id}


def retry_turn(store: CaseStore, turn_id: str) -> dict:
    t = next((t for t in conversation(store, 400) if t.get("turn_id") == turn_id), None)
    if not t:
        raise ValueError("Turno no encontrado")
    job = jobs.submit(store.id, "briefer_turn", "Briefer (reintento)", {"turn_id": turn_id}, agent="briefer")
    _patch_turn(store, turn_id, {"status": "pending", "job_id": job.id, "error": None})
    return {"job_id": job.id}


def recover_turns(store: CaseStore) -> int:
    rows = read_jsonl(store.root / CONV)
    n = 0
    for r in rows:
        if r.get("status") in ("pending", "running") and r.get("job_id") not in jobs.LIVE:
            r.update({"status": "failed", "error": "El servidor se reinició antes de responder; tu mensaje se conservó.",
                      "error_kind": "interrupted"})
            n += 1
    if n:
        write_jsonl_replace(store.root / CONV, rows)
    return n


def _patch_turn(store: CaseStore, turn_id: str, patch: dict) -> dict | None:
    rows = read_jsonl(store.root / CONV)
    hit = None
    for r in rows:
        if r.get("turn_id") == turn_id:
            r.update(patch)
            hit = r
    write_jsonl_replace(store.root / CONV, rows)
    return hit


def conversation(store: CaseStore, limit: int = 80) -> list[dict]:
    return read_jsonl(store.root / CONV, limit=limit)


@jobs.handler("briefer_turn")
async def _job(job, params):
    store = cases.get(job.case_id)
    turn = next((t for t in conversation(store, 400) if t.get("turn_id") == params["turn_id"]), None)
    if not turn:
        raise AgentError("unknown", "Turno no encontrado")
    message = turn["message"]
    selected = skills.select("briefer", text=message)
    system = base.system_prompt("briefer", selected, store.meta().get("language"))
    _patch_turn(store, turn["turn_id"], {"status": "running", "skills": skills.record(selected)})
    await job.event("skills", {"skills": [s["id"] for s in skills.record(selected)]})
    spec = RunSpec(agent="briefer", role="briefer", system=system, prompt=build_prompt(store, message), schema=SCHEMA, max_turns=4,
                   skills=skills.record(selected), purpose="Turno de briefing", case_id=store.id, case_root=store.root)

    async def on_event(kind, data):
        await job.event(kind, data)
    try:
        res = await get_llm().run(spec, on_event)
    except AgentError as e:
        _patch_turn(store, turn["turn_id"], {"status": "failed", "error": str(e), "error_kind": e.kind})
        raise
    out = dict(res.output)
    props, notes = guard(out, message)
    proposed = []
    with store.batch():
        for p in props:
            if briefing.propose(store, p["section"], p["value"], hugo_wording=p.get("hugo_wording", ""), basis=p.get("basis", "hugo"),
                                why=p.get("why", ""), turn_id=turn["turn_id"]):
                proposed.append(p["section"])
        briefing.render_md(store)
        from .framer import _update_language
        _update_language(store, out.get("language") or {})
    check = language.assess(out.get("reply", ""), store.meta().get("language"), message)
    if not check["ok"]:
        notes += [f"Disciplina de lenguaje: {i}" for i in check["issues"]]
    rec = {"status": "done", "error": None, "error_kind": None, "reply": out.get("reply", ""), "question": out.get("question", ""),
           "proposed": proposed, "corrections": notes, "language_check": check, "run_id": res.run_id, "usage": res.usage,
           "cost_usd": res.cost_usd, "auth": res.auth, "finished_at": now_iso()}
    _patch_turn(store, turn["turn_id"], rec)
    store.log("briefer", "proposed", ["brief"], f"Briefer propuso {len(proposed)} sección(es): "
              + (", ".join(briefing.BY_KEY[k]["label"] for k in proposed) or "ninguna"), material=bool(proposed), run_id=res.run_id)
    return {"turn_id": turn["turn_id"], "proposed": proposed}
