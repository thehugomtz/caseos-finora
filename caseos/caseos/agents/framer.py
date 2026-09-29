"""Framer — Problem Framing & Initial Storytelling (agents/framer.md).

One turn: Hugo's message + mode → skills selected (core + mode + 0–2 lenses) → structured FramerTurn →
code guards (epistemic reclassification, limits) → proposed entities (N/H/Q/D) + framing patch + language profile →
framing/current.md re-rendered → conversation logged. Nothing is accepted here: Hugo accepts at the gate or per item.
"""
from __future__ import annotations

import uuid

from .. import cases, decisions, framing_doc, jobs, language, phases, skills
from ..llm import AgentError, RunSpec, get_llm
from ..model import EPISTEMIC_KINDS, KIND_LABELS, title_of, type_of
from ..store import CaseStore
from ..util import append_jsonl, clip, norm, now_iso, read_jsonl, write_jsonl_replace
from . import base

MODES = ["organize", "advise", "challenge"]
MODE_LABELS = {"organize": "Organize", "advise": "Advise", "challenge": "Challenge"}
MODE_HINT = {
    "organize": "MODO ORGANIZE — «ayúdame a ordenar lo que estoy pensando». Captura, clasifica y refleja la estructura. "
                "Como mucho una pregunta aclaratoria. Sin challenge agresivo. `alternatives` y `challenge` vacíos.",
    "advise": "MODO ADVISE — «ahora dime cómo lo abordarías». Máximo 2–3 alternativas útiles en `alternatives`, cada una con "
              "cuándo gana y qué cuesta. `challenge` vacío.",
    "challenge": "MODO CHALLENGE — «ahora intenta romper esto». Llena `challenge` (supuestos ocultos, contraargumento más "
                 "fuerte, explicación alternativa, evidencia que lo invalidaría, claim de mayor riesgo). Tono tranquilo. "
                 "`alternatives` vacío salvo que ayude a salir del problema.",
}

_S = {"type": "string"}
_SA = {"type": "array", "items": {"type": "string"}}


def _obj(props: dict) -> dict:
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


ITEM = _obj({"kind": {"type": "string", "enum": EPISTEMIC_KINDS}, "structured": _S, "hugo_wording": _S, "basis": _S,
             "confidence": {"type": "string", "enum": ["high", "medium", "low", "n/a"]}, "falsifier": _S,
             "links": _SA, "updates": _S})
FRAME = _obj({"name": _S, "description": _S, "when_it_wins": _S, "cost": _S})
RESEARCH_NEEDED = _obj({"question": _S, "links": _SA, "why": _S})
SCHEMA = _obj({
    "reply": _S,
    "items": {"type": "array", "items": ITEM},
    "framing_patch": _obj({"executive_question": _S, "candidate_frames": {"type": "array", "items": FRAME},
                           "initial_storyline": _SA, "research_needed": {"type": "array", "items": RESEARCH_NEEDED},
                           "decisions_needed": _SA, "should_not_claim": _SA, "language_notes": _SA, "risks": _SA}),
    "advisors": {"type": "array", "items": _obj({"lens": {"type": "string", "enum": ["ceo", "cro", "cfo", "cpo", "cdo"]},
                                                 "why": _S, "contribution": _S})},
    "alternatives": {"type": "array", "items": _obj({"name": _S, "approach": _S, "when_it_wins": _S, "cost": _S})},
    "challenge": _obj({"hidden_assumptions": _SA, "strongest_counterargument": _S, "alternative_explanation": _S,
                       "invalidating_evidence": _SA, "highest_risk_claim": _S}),
    "language": _obj({"register": _S, "technical_level": _S, "formality": _S, "preserved_terms": _SA,
                      "introduced_terms": {"type": "array", "items": _obj({"term": _S, "plain": _S})}}),
    "next_steps": _SA,
})

CONV = "framing/conversation.jsonl"


# ------------------------------------------------------------------------------------------ context
def ledger_lines(store: CaseStore, limit: int = 140) -> list[str]:
    out = []
    for e in store.list():
        t = e.get("type")
        if t not in ("note", "hypothesis", "question", "decision"):
            continue
        rv = (e.get("review") or {}).get("state", "proposed")
        if rv == "rejected" or e.get("status") in ("superseded", "reverted"):
            continue
        kind = e.get("kind") if t == "note" else {"hypothesis": "HYPOTHESIS", "question": "QUESTION", "decision": "DECISION"}[t]
        extra = []
        if t == "hypothesis":
            extra.append(f"estado {e.get('status', 'open')}")
            if e.get("falsifier"):
                extra.append(f"se debilita si: {clip(e['falsifier'], 140)}")
        if t == "question" and e.get("kind") == "executive":
            extra.append("pregunta ejecutiva")
        if t == "decision":
            extra.append(e.get("status", ""))
        hw = f' · Hugo: "{clip(e["hugo_wording"], 120)}"' if e.get("hugo_wording") else ""
        alias = f" ({e['alias']})" if e.get("alias") else ""
        out.append(f"- {e['id']}{alias} [{kind} · {rv}{' · ' + '; '.join(x for x in extra if x) if extra else ''}] "
                   f"{clip(title_of(e), 220)}{hw}")
    return out[-limit:]


def build_prompt(store: CaseStore, message: str, mode: str, lenses: list[dict]) -> str:
    meta = store.meta()
    brief = store.read_data("brief/brief.yaml", {}) or {}
    fr = store.read_data("framing/current.yaml", {}) or {}
    ev = [f for f in store.list("finding") if (f.get("review") or {}).get("state") == "accepted"][:15]
    conv = [t for t in read_jsonl(store.root / CONV, limit=12) if t.get("status") == "done"][-6:]
    aud = brief.get("audience") or meta.get("audience") or []
    lines = ["## Brief (resumen)",
             f"Objetivo: {clip(brief.get('objective') or meta.get('objective', ''), 500)}",
             f"Audiencia: {', '.join(aud) if isinstance(aud, list) else aud}",
             f"Contexto: {clip(brief.get('context', ''), 1200)}",
             "Entregables: " + "; ".join(clip(str(x), 160) for x in (brief.get("deliverables") or [])),
             "Restricciones: " + "; ".join(clip(str(x), 160) for x in (brief.get("constraints") or [])),
             "Vacíos declarados: " + "; ".join(clip(str(x), 160) for x in (brief.get("gaps") or [])),
             "", "## Framing vivo",
             f"Pregunta ejecutiva: {fr.get('executive_question') or '(sin definir)'}",
             "Frames candidatos: " + ("; ".join(f"{f.get('name')}{' (elegido)' if f.get('chosen') else ''}" for f in fr.get("candidate_frames") or []) or "—"),
             "Storyline inicial: " + (" / ".join(fr.get("initial_storyline") or []) or "—"),
             "Research necesario: " + ("; ".join(clip(r.get("question", ""), 140) for r in fr.get("research_needed") or []) or "—"),
             "Decisiones necesarias: " + ("; ".join(fr.get("decisions_needed") or []) or "—"),
             "No afirmar todavía: " + ("; ".join(fr.get("should_not_claim") or []) or "—"),
             "", "## Ledger del caso (usa estos IDs; no dupliques)", *(ledger_lines(store) or ["(vacío)"]),
             "", "## Evidencia aceptada (hechos con base evidence:<ID>)",
             *([f"- {f['id']} {clip(title_of(f), 200)}" for f in ev] or ["(ninguna todavía)"]),
             "", "## Conversación reciente"]
    for t in conv:
        lines.append(f"Hugo ({t.get('mode')}): {clip(t.get('message', ''), 600)}")
        lines.append(f"Framer: {clip(t.get('reply', ''), 600)}")
    if not conv:
        lines.append("(primer turno)")
    lines += ["", "## Modo", MODE_HINT[mode]]
    if lenses:
        lines.append("Lentes de advisor cargadas para este turno: " + ", ".join(
            f"{skills.LENS_LABELS.get(l['lens'], l['lens'])} ({l['why']})" for l in lenses) +
                     ". Úsalas como lentes; tú conservas la síntesis.")
    else:
        lines.append("Sin lentes de advisor en este turno.")
    lines += ["", "## Mensaje de Hugo", message.strip(),
              "", "Devuelve el FramerTurn. Reglas del patch: executive_question vacío = sin cambio; candidate_frames e "
                  "initial_storyline vacíos = sin cambio (si los envías, envía la lista completa, máx. 3 frames); "
                  "research_needed, decisions_needed, should_not_claim, language_notes y risks = SOLO lo nuevo de este turno."]
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------ guards + apply
def guard(out: dict, mode: str, existing: dict[str, dict]) -> tuple[dict, list[str]]:
    """Code-level epistemic guards. Returns the cleaned turn and the list of corrections made."""
    notes: list[str] = []
    items = []
    for it in out.get("items") or []:
        txt = (it.get("structured") or "").strip()
        if not txt:
            continue
        kind = it.get("kind") if it.get("kind") in EPISTEMIC_KINDS else "OBSERVATION"
        basis = (it.get("basis") or "").strip()
        if kind == "FACT":
            ok_basis = basis.startswith(("brief", "case_material", "enunciado")) or (
                basis.startswith("evidence:") and (existing.get(basis.split(":", 1)[1].strip()) or {}).get("review", {}).get("state") == "accepted")
            if not ok_basis:
                new_kind = "USER_INTUITION" if (it.get("hugo_wording") or "").strip() else "OBSERVATION"
                notes.append(f"«{clip(txt, 70)}» se reclasificó de FACT a {new_kind}: no tiene base en el brief ni en evidencia aceptada ({basis or 'sin base'}).")
                it = {**it, "reclassified_from": "FACT"}
                kind = new_kind
        if kind == "HYPOTHESIS" and not (it.get("falsifier") or "").strip():
            notes.append(f"Hipótesis sin falsificador: «{clip(txt, 70)}» (queda marcada).")
        links = [l for l in it.get("links") or [] if l in existing]
        upd = (it.get("updates") or "").strip()
        if upd and upd not in existing:
            notes.append(f"Referencia inexistente {upd} ignorada.")
            upd = ""
        items.append({**it, "kind": kind, "structured": txt, "links": links, "updates": upd})
    out["items"] = items
    adv = out.get("advisors") or []
    if len(adv) > 2:
        notes.append(f"El Framer consultó {len(adv)} advisors; se conservan 2 (regla: advisors son lentes, máx. 2).")
        out["advisors"] = adv[:2]
    alts = out.get("alternatives") or []
    if mode == "organize":
        out["alternatives"] = []
    elif len(alts) > 3:
        notes.append("Más de 3 alternativas; se conservan 3.")
        out["alternatives"] = alts[:3]
    if mode != "challenge":
        out["challenge"] = {"hidden_assumptions": [], "strongest_counterargument": "", "alternative_explanation": "",
                            "invalidating_evidence": [], "highest_risk_claim": ""}
    patch = out.get("framing_patch") or {}
    if len(patch.get("candidate_frames") or []) > 3:
        notes.append("Más de 3 frames candidatos; se conservan 3.")
        patch["candidate_frames"] = patch["candidate_frames"][:3]
    out["framing_patch"] = patch
    return out, notes


def apply_turn(store: CaseStore, out: dict, *, message: str, mode: str, run_id: str) -> dict:
    existing = store.all()
    created, updated = [], []
    actor = "framer"
    with store.batch():
        for it in out["items"]:
            kind = it["kind"]
            common = {"hugo_wording": it.get("hugo_wording", "").strip(), "structured": it["structured"],
                      "basis": it.get("basis", ""), "confidence": it.get("confidence", "n/a"), "links": it["links"],
                      "source_turn": run_id}
            if it.get("reclassified_from"):
                common["reclassified_from"] = it["reclassified_from"]
            target = existing.get(it["updates"]) if it["updates"] else None
            if kind == "HYPOTHESIS":
                data = {**common, "statement": it["structured"], "falsifier": it.get("falsifier", ""), "status": "open"}
                if not data["falsifier"]:
                    data["flags"] = ["sin_falsificador"]
                etype = "hypothesis"
            elif kind == "QUESTION":
                data = {**common, "text": it["structured"], "kind": "framing", "status": "open"}
                etype = "question"
            elif kind == "DECISION":
                d = decisions.record_decision(store, title=it["structured"], context=f"Surgió en la conversación de framing: «{clip(message, 300)}»",
                                              options={}, agent_recommendation="", user_choice="", user_rationale="",
                                              affected_items=it["links"], downstream_impact="", kind="framing",
                                              phase="framing", actor=actor, run_id=run_id,
                                              origin={"hugo_wording": common["hugo_wording"]})
                store.update(d["id"], {"hugo_wording": common["hugo_wording"], "phase": "framing"}, actor=actor, material=False)
                created.append(d["id"])
                continue
            else:
                data = {**common, "kind": kind, "text": it["structured"], "status": "active"}
                etype = "note"
            if target and target.get("type") == etype:
                patch = {k: v for k, v in data.items() if v not in ("", None, []) and k not in ("status",)}
                patch["links"] = list(dict.fromkeys((target.get("links") or []) + data["links"]))
                old_words = (target.get("hugo_wording") or "").strip()
                if patch.get("hugo_wording") and old_words and norm(old_words) != norm(patch["hugo_wording"]):
                    # Hugo's earlier words are never replaced silently: they stay visible as history.
                    patch["hugo_wording_history"] = list(target.get("hugo_wording_history") or []) + [{
                        "text": old_words, "verbatim": target.get("verbatim", True), "until": now_iso(),
                        "source": (target.get("origin") or {}).get("source") or target.get("source_turn") or ""}]
                    patch["verbatim"] = True
                store.update(target["id"], patch, actor=actor, run_id=run_id,
                             summary=f"Framer refinó {target['id']}: {clip(it['structured'], 90)}")
                updated.append(target["id"])
            else:
                e = store.create(etype, data, actor=actor, run_id=run_id,
                                 summary=f"Framer capturó {KIND_LABELS.get(kind, kind).lower()}: {clip(it['structured'], 90)}")
                created.append(e["id"])
        fr = store.read_data("framing/current.yaml", {}) or cases.empty_framing()
        p = out["framing_patch"]
        changed = []
        eq = (p.get("executive_question") or "").strip()
        if eq and norm(eq) != norm(fr.get("executive_question") or ""):
            if fr.get("executive_question"):
                fr.setdefault("executive_question_history", []).append({"text": fr["executive_question"], "until": now_iso()})
            fr["executive_question"] = eq
            changed.append("pregunta ejecutiva")
        if p.get("candidate_frames"):
            chosen = {norm(f.get("name", "")) for f in fr.get("candidate_frames") or [] if f.get("chosen")}
            fr["candidate_frames"] = [{**f, "chosen": norm(f.get("name", "")) in chosen} for f in p["candidate_frames"]]
            changed.append("frames candidatos")
        if p.get("initial_storyline"):
            fr["initial_storyline"] = p["initial_storyline"][:7]
            changed.append("storyline inicial")
        for key in ("decisions_needed", "should_not_claim", "language_notes", "risks"):
            cur = fr.get(key) or []
            seen = {norm(x) for x in cur}
            add = [x for x in p.get(key) or [] if x and norm(x) not in seen]
            if add:
                fr[key] = cur + add
                changed.append(key)
        rn = fr.get("research_needed") or []
        seen = {norm(r.get("question", "")) for r in rn}
        for r in p.get("research_needed") or []:
            if r.get("question") and norm(r["question"]) not in seen:
                rn.append({"id": f"RN-{uuid.uuid4().hex[:6]}", "question": r["question"], "why": r.get("why", ""),
                           "links": [l for l in r.get("links") or [] if l in existing or l in created], "status": "pending",
                           "proposed_by": "framer", "at": now_iso()})
                changed.append("research necesario")
        fr["research_needed"] = rn
        fr["mode"] = mode
        framing_doc.save(store, fr, actor=actor, summary=f"Framing actualizado ({', '.join(dict.fromkeys(changed)) or 'ideas capturadas'})",
                         material=bool(created or updated or changed))
        _update_language(store, out.get("language") or {})
        phases.touch(store, "framing", actor=actor)
        if store.meta()["phases"]["framing"].get("status") == "ready" and (created or changed):
            phases.set_status(store, "framing", "needs_review", actor=actor, note="el framing cambió después de aprobarse")
    return {"created": created, "updated": updated, "framing_changed": list(dict.fromkeys(changed))}


def _update_language(store: CaseStore, lang_out: dict) -> None:
    meta = store.meta()
    lang = meta.setdefault("language", {})
    obs = lang.setdefault("observed", {})
    changed = False
    for k in ("register", "technical_level", "formality"):
        v = (lang_out.get(k) or "").strip()
        if v and v != obs.get(k):
            obs[k] = v
            changed = True
    terms = obs.get("preserved_terms") or []
    have = {norm(t) for t in terms}
    for t in lang_out.get("preserved_terms") or []:
        if t and norm(t) not in have:
            terms.append(t)
            have.add(norm(t))
            changed = True
    obs["preserved_terms"] = terms[-40:]
    intro = obs.get("introduced_terms") or []
    for t in lang_out.get("introduced_terms") or []:
        if t.get("term") and norm(t["term"]) not in {norm(x.get("term", "")) for x in intro}:
            intro.append({"term": t["term"], "plain": t.get("plain", ""), "at": now_iso()})
            changed = True
    obs["introduced_terms"] = intro[-40:]
    if changed:
        store.save_meta(meta)


# ------------------------------------------------------------------------------------------ turn
def start_turn(store: CaseStore, message: str, mode: str) -> dict:
    if mode not in MODES:
        raise ValueError(f"Modo desconocido: {mode}")
    msg = (message or "").strip()
    if not msg:
        raise ValueError("Mensaje vacío")
    turn = {"turn_id": f"T{now_iso()[:19].replace(':', '').replace('-', '')}-{uuid.uuid4().hex[:4]}", "ts": now_iso(),
            "mode": mode, "message": msg[:8000], "status": "pending"}
    append_jsonl(store.root / CONV, turn)
    store.log("hugo", "said", ["framing"], f"Hugo al Framer ({MODE_LABELS[mode]}): {clip(msg, 110)}", material=False)
    try:
        job = jobs.submit(store.id, "framer_turn", f"Framer · {MODE_LABELS[mode]}", {"turn_id": turn["turn_id"]}, agent="framer")
    except Exception as e:  # noqa: BLE001 - the message is kept; the turn can be retried
        _patch_turn(store, turn["turn_id"], {"status": "failed", "error": f"No se pudo lanzar el turno: {e}"})
        raise
    _patch_turn(store, turn["turn_id"], {"job_id": job.id})
    return {**turn, "job_id": job.id}


def recover_turns(store: CaseStore) -> int:
    """Turns left pending/running by a previous server process become failed-but-retriable."""
    rows = read_jsonl(store.root / CONV)
    n = 0
    for r in rows:
        if r.get("status") in ("pending", "running") and not (r.get("job_id") in jobs.LIVE):
            r.update({"status": "failed", "error": "El servidor se reinició antes de responder; tu mensaje se conservó.", "error_kind": "interrupted"})
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


@jobs.handler("framer_turn")
async def _job(job, params):
    store = cases.get(job.case_id)
    turn = next((t for t in conversation(store, 400) if t.get("turn_id") == params["turn_id"]), None)
    if not turn:
        raise AgentError("unknown", "Turno no encontrado")
    mode, message = turn["mode"], turn["message"]
    lenses = skills.route_lenses(message, mode=mode)
    selected = skills.select("framer", mode=mode, text=message, lenses=lenses)
    meta = store.meta()
    system = base.system_prompt("framer", selected, meta.get("language"))
    prompt = build_prompt(store, message, mode, lenses)
    _patch_turn(store, turn["turn_id"], {"status": "running", "skills": skills.record(selected), "lenses": lenses})
    await job.event("skills", {"skills": [s["id"] for s in skills.record(selected)], "lenses": [l["lens"] for l in lenses]})
    spec = RunSpec(agent="framer", role="framer", system=system, prompt=prompt, schema=SCHEMA, max_turns=4,
                   skills=skills.record(selected), lenses=lenses, purpose=f"Turno de framing ({mode})",
                   case_id=store.id, case_root=store.root)

    async def on_event(kind, data):
        await job.event(kind, data)
    try:
        res = await get_llm().run(spec, on_event)
    except AgentError as e:
        _patch_turn(store, turn["turn_id"], {"status": "failed", "error": str(e), "error_kind": e.kind})
        raise
    out, corrections = guard(dict(res.output), mode, store.all())
    applied = apply_turn(store, out, message=message, mode=mode, run_id=res.run_id)
    lang_check = language.assess(out.get("reply", ""), store.meta().get("language"), message)
    if not lang_check["ok"]:
        corrections = corrections + [f"Disciplina de lenguaje: {i}" for i in lang_check["issues"]]
    rec = {"status": "done", "error": None, "error_kind": None, "language_check": lang_check,
           "reply": out.get("reply", ""), "created": applied["created"], "updated": applied["updated"],
           "framing_changed": applied["framing_changed"], "advisors": out.get("advisors") or [],
           "alternatives": out.get("alternatives") or [], "challenge": out.get("challenge") if mode == "challenge" else None,
           "language": out.get("language") or {}, "next_steps": (out.get("next_steps") or [])[:3],
           "corrections": corrections, "run_id": res.run_id, "usage": res.usage, "cost_usd": res.cost_usd,
           "auth": res.auth, "finished_at": now_iso()}
    _patch_turn(store, turn["turn_id"], rec)
    store.log("framer", "replied", applied["created"] + applied["updated"],
              f"Framer respondió ({MODE_LABELS[mode]}): {len(applied['created'])} nuevos, {len(applied['updated'])} refinados"
              + (f" · lentes {', '.join(skills.LENS_LABELS[a['lens']] for a in rec['advisors'])}" if rec["advisors"] else ""),
              material=False, run_id=res.run_id)
    return {"turn_id": turn["turn_id"], **{k: rec[k] for k in ("created", "updated", "framing_changed")}}


def retry_turn(store: CaseStore, turn_id: str) -> dict:
    t = next((t for t in conversation(store, 400) if t.get("turn_id") == turn_id), None)
    if not t:
        raise ValueError("Turno no encontrado")
    job = jobs.submit(store.id, "framer_turn", f"Framer · {MODE_LABELS[t['mode']]} (reintento)", {"turn_id": turn_id}, agent="framer")
    _patch_turn(store, turn_id, {"status": "pending", "job_id": job.id, "error": None})
    return {"job_id": job.id}


def kinds_of(eid: str) -> str:
    return type_of(eid) or ""
