"""Case Chief of Staff — the operational heart (agents/cos.md).

Deterministic layer (always on, no model): control room, next best actions, lineage-based impact detection,
readiness. Agent layer (Claude): classify the effect of new evidence and write alerts with options, answer Hugo's
questions about the case, keep a status note for brain.md, draft the Story Package (story.py).
The COS recommends; it never decides, accepts, or advances a phase.
"""
from __future__ import annotations

from . import cases, decisions, jobs, lineage, phases, skills
from .agents import base
from .llm import AgentError, RunSpec, get_llm
from .model import PHASE_LABELS, PHASES, title_of, type_of
from .store import CaseStore
from .util import clip, norm, now_iso

EFFECTS = ["supports", "weakens", "contradicts", "opens_new_hypothesis", "changes_framing", "changes_story",
           "requires_research", "no_material_impact"]
EFFECT_LABELS = {"supports": "apoya", "weakens": "debilita", "contradicts": "contradice",
                 "opens_new_hypothesis": "abre una hipótesis nueva", "changes_framing": "cambia el framing",
                 "changes_story": "cambia la historia", "requires_research": "requiere más investigación",
                 "no_material_impact": "sin impacto material"}
MATERIAL = {"weakens", "contradicts", "changes_framing", "changes_story", "opens_new_hypothesis", "requires_research"}


def _rv(e: dict) -> str:
    return (e.get("review") or {}).get("state", "proposed")


# ------------------------------------------------------------------------------------------ control room
def room(store: CaseStore) -> dict:
    ents = store.all()
    meta = store.meta()

    def of(t, **kw):
        return sorted([e for e in ents.values() if e.get("type") == t and all(e.get(k) == v for k, v in kw.items())],
                      key=lambda e: e["id"])

    claims = [c for c in of("claim") if _rv(c) != "rejected"]
    supported = [c for c in claims if claim_strength(store, c, ents)["level"] == "supported"]
    research = of("research")
    alerts = [x for x in of("alert") if x.get("status") == "open"]
    hyps = [h for h in of("hypothesis") if _rv(h) != "rejected"]
    graph = lineage.graph(ents)
    hyp_rows = []
    for h in hyps:
        nb = graph.get(h["id"], set())
        hyp_rows.append({"id": h["id"], "alias": h.get("alias"), "text": title_of(h), "status": h.get("status", "open"),
                         "assessed": h.get("assessed"), "review": _rv(h), "stale": bool(h.get("stale")),
                         "research": sorted(i for i in nb if type_of(i) == "research"),
                         "findings": sorted(i for i in nb if type_of(i) == "finding"),
                         "priority": h.get("priority")})
    readiness = {p: phases.readiness(store, p) for p in PHASES}
    acc_f = [f for f in of("finding") if _rv(f) == "accepted"]
    health = {
        "phase": phases.current_phase(meta),
        "phases": phases.phases_view(store),
        "claims_total": len(claims), "claims_supported": len(supported),
        "evidence_accepted": len(acc_f), "evidence_proposed": len([f for f in of("finding") if _rv(f) == "proposed"]),
        "tables_accepted": len([t for t in of("table") if _rv(t) == "accepted"]),
        "research_running": len([r for r in research if r.get("status") in ("queued", "running")]),
        "research_review": len([r for r in research if r.get("status") == "completed" and _rv(r) == "proposed"]),
        "research_blocked": len([r for r in research if r.get("status") == "blocked"]),
        "alerts_open": len(alerts), "contradictions_open": len([x for x in alerts if x.get("kind") == "contradiction"]),
        "decisions_open": len(of("decision", status="proposed")), "stale": len([e for e in ents.values() if e.get("stale")]),
    }
    fr = store.read_data("framing/current.yaml", {}) or {}
    pkg = store.read_data("story/package.yaml", {}) or {}
    return {
        "health": health,
        "next_best_actions": next_best_actions(store, ents=ents, meta=meta),
        "alerts": [_alert_row(x, ents) for x in alerts],
        "decisions_open": [_row(d) for d in of("decision", status="proposed")],
        "decisions_recent": [_row(d) for d in sorted(of("decision", status="active"), key=lambda d: d.get("created_at", ""), reverse=True)[:8]],
        "hypotheses": hyp_rows,
        "research_queue": [_research_row(r) for r in research if r.get("status") != "cancelled"],
        "open_questions": [_row(q) for q in of("question") if q.get("status", "open") == "open" and q.get("kind") in ("framing", "branch", "workplan") and _rv(q) != "rejected"][:30],
        "evidence": [_row(f) for f in acc_f][-20:],
        "tables": [_row(t) for t in of("table") if _rv(t) != "rejected"],
        "current_framing": {"executive_question": fr.get("executive_question"), "storyline": fr.get("initial_storyline") or [],
                            "frames": [f for f in fr.get("candidate_frames") or [] if f.get("chosen")]},
        "current_story": {"governing_thought": pkg.get("governing_thought"),
                          "claims": [{**_row(c), "strength": claim_strength(store, c, ents)} for c in claims]},
        "readiness": readiness,
        "status_note": (store.read_data("cos/state.yaml", {}) or {}).get("status_note"),
        "status_note_at": (store.read_data("cos/state.yaml", {}) or {}).get("updated_at"),
    }


def _row(e: dict) -> dict:
    return {"id": e["id"], "type": e.get("type"), "alias": e.get("alias"), "text": title_of(e), "status": e.get("status"),
            "review": _rv(e), "stale": bool(e.get("stale")), "kind": e.get("kind"), "confidence": e.get("confidence"),
            "table_key": e.get("table_key"), "created_at": e.get("created_at")}


def _research_row(r: dict) -> dict:
    return {**_row(r), "specialty": r.get("specialty"), "intensity": r.get("intensity"),
            "question": r.get("research_question"), "short_answer": clip(r.get("short_answer", ""), 260),
            "purpose_ok": r.get("purpose_ok", True), "job_id": r.get("job_id"), "shaping_task": r.get("shaping_task")}


def _alert_row(x: dict, ents: dict) -> dict:
    return {**_row(x), "severity": x.get("severity"), "effect": x.get("effect"), "finding": x.get("finding_text"),
            "why": x.get("why"), "options": x.get("options") or [], "recommended": x.get("recommended"),
            "recommended_why": x.get("recommended_why"), "source": x.get("source"), "target": x.get("target"),
            "target_text": title_of(ents.get(x.get("target"), {})) if x.get("target") in ents else ""}


# ------------------------------------------------------------------------------------------ claim strength
def claim_strength(store: CaseStore, c: dict, ents: dict | None = None) -> dict:
    ents = ents or store.all()
    ev = [i for i in (c.get("evidence_ids") or []) + [l for l in c.get("links") or [] if type_of(l) == "finding"] if i in ents]
    tb = [i for i in (c.get("table_ids") or []) + [l for l in c.get("links") or [] if type_of(l) == "table"] if i in ents]
    acc = [i for i in ev if _rv(ents[i]) == "accepted"]
    stale = [i for i in ev + tb if ents[i].get("stale")] + (["self"] if c.get("stale") else [])
    from .evidence import unsupported_numbers
    text = f"{c.get('headline', '')} {c.get('answer', '')}"
    unsup = unsupported_numbers(text, [ents[t] for t in tb])
    pend = [i for i in ev if _rv(ents[i]) not in ("accepted", "rejected")]
    if c.get("role_in_story") in ("recommendation", "limitation") and not ev:
        level = "proposal"
    elif not acc and pend:
        level = "pending"                     # it has evidence, but Hugo has not accepted it yet
    elif not acc:
        level = "unsupported"
    elif unsup or stale:
        level = "weak"
    else:
        level = "supported"
    return {"level": level, "evidence": ev, "accepted": acc, "pending": pend, "tables": tb, "unsupported_numbers": unsup, "stale": stale}


# ------------------------------------------------------------------------------------------ next best actions
def next_best_actions(store: CaseStore, *, ents: dict | None = None, meta: dict | None = None, limit: int = 8) -> list[dict]:
    ents = ents or store.all()
    meta = meta or store.meta()
    ph = meta["phases"]
    out: list[dict] = []

    def add(title, why, ids=(), action=None, prio=5):
        out.append({"title": title, "why": why, "ids": list(ids), "action": action or {}, "priority": prio})

    for p in PHASES:
        st = ph[p].get("status")
        rd = phases.readiness(store, p)
        if st in ("review", "needs_review", "reopened") and rd["ok"]:
            add(f"Revisar y marcar {PHASE_LABELS[p]} Ready", "La fase está lista para tu aprobación." if st == "review"
                else "La fase cambió después de aprobarse: vuelve a revisarla.", [p],
                {"kind": "mark_ready", "phase": p}, 1)
            break
        if st != "ready":
            break
    for x in sorted([e for e in ents.values() if e.get("type") == "alert" and e.get("status") == "open"],
                    key=lambda e: ({"high": 0, "medium": 1, "low": 2}.get(e.get("severity"), 3), e["id"])):
        verb = EFFECT_LABELS.get(x.get("effect"), "afecta")
        add(f"{x.get('source', '')} {verb} {x.get('target', '')}".strip(), clip(x.get("why", ""), 160),
            [x["id"], x.get("source"), x.get("target")], {"kind": "open", "id": x["id"]}, 2)
    for d in [e for e in ents.values() if e.get("type") == "decision" and e.get("status") == "proposed"][:3]:
        add(f"Confirmar o descartar {d['id']}: {clip(d.get('title', ''), 70)}", d.get("confirm_note") or "Decisión propuesta, no activa.",
            [d["id"]], {"kind": "open", "id": d["id"]}, 3)
    rev = [e for e in ents.values() if e.get("type") == "research" and e.get("status") == "completed" and _rv(e) == "proposed"]
    for r in sorted(rev, key=lambda e: e["id"])[:3]:
        add(f"Revisar {r['id']}{' (' + r['alias'] + ')' if r.get('alias') else ''}: {clip(r.get('research_question', ''), 70)}",
            "Resultado completo esperando tu Accept / Challenge.", [r["id"]], {"kind": "open", "id": r["id"]}, 3)
    failed = [e for e in ents.values() if e.get("type") == "research" and e.get("status") == "failed"]
    for r in failed[:2]:
        add(f"Reintentar {r['id']}", clip(r.get("error", "La investigación falló; la solicitud se conservó."), 140), [r["id"]],
            {"kind": "open", "id": r["id"]}, 4)
    fr = store.read_data("framing/current.yaml", {}) or {}
    pend = [r for r in fr.get("research_needed") or [] if r.get("status") == "pending"]
    if pend:
        add(f"Enviar a Research: {clip(pend[0]['question'], 80)}", "Research necesario del framing, todavía sin lanzar.",
            [i for i in pend[0].get("links", [])[:3]], {"kind": "research_needed", "rn": pend[0]["id"]}, 5)
    claims = [c for c in ents.values() if c.get("type") == "claim" and _rv(c) != "rejected"]
    weak = [(c, claim_strength(store, c, ents)) for c in claims]
    for c, s in [(c, s) for c, s in weak if s["level"] in ("unsupported", "weak")][:2]:
        why = ("sin evidencia aceptada" if s["level"] == "unsupported" else
               ("cifras sin tabla: " + ", ".join(s["unsupported_numbers"][:3]) if s["unsupported_numbers"] else "depende de algo marcado needs_review"))
        add(f"{c['id']} está débil: {why}", clip(title_of(c), 120), [c["id"]], {"kind": "open", "id": c["id"]}, 4)
    graph = lineage.graph(ents)
    orphan = [h for h in ents.values() if h.get("type") == "hypothesis" and _rv(h) != "rejected" and h.get("status") == "open"
              and not any(type_of(n) == "research" for n in graph.get(h["id"], ()))
              and _priority_value(h) != 0]
    if orphan:
        h = sorted(orphan, key=lambda e: e["id"])[0]
        add(f"{h['id']}{' (' + h['alias'] + ')' if h.get('alias') else ''} no tiene investigación asignada", clip(title_of(h), 120),
            [h["id"]], {"kind": "open", "id": h["id"]}, 6)
    if ph["research"].get("ready_count") and not ph["synthesis"].get("ready_count") and not [x for x in ents.values() if x.get("type") == "alert"]:
        add("Pedir al COS la síntesis del caso", "Research aprobado: toca consolidar qué cambió en las hipótesis.", [],
            {"kind": "cos_ask", "text": "¿Qué cambió en las hipótesis con la evidencia aceptada y qué falta para la story?"}, 5)
    if ph["synthesis"].get("ready_count") and not store.read_data("story/package.yaml"):
        add("Preparar el Story Package", "La síntesis está aprobada.", [], {"kind": "story_package"}, 4)
    out.sort(key=lambda a: a["priority"])
    for i, a in enumerate(out[:limit], 1):
        a["n"] = i
    return out[:limit]


# ------------------------------------------------------------------------------------------ impact (deterministic)
def impact_candidates(store: CaseStore, source_id: str) -> dict:
    """Which hypotheses, questions, claims and framing elements new evidence touches, by lineage alone."""
    ents = store.all()
    src = ents.get(source_id)
    if not src:
        return {"hypotheses": [], "claims": [], "questions": []}
    seeds = {source_id} | {f for f in src.get("findings") or [] if f in ents}
    graph = lineage.graph(ents)
    near = set()
    for s in seeds:
        near |= graph.get(s, set())
    hyps = sorted(i for i in near if type_of(i) == "hypothesis")
    qs = sorted(i for i in near if type_of(i) == "question")
    claims = set(i for i in near if type_of(i) == "claim")
    for h in hyps:  # claims standing on the same hypotheses
        claims |= {i for i in graph.get(h, set()) if type_of(i) == "claim"}
    return {"hypotheses": hyps, "questions": qs, "claims": sorted(claims)}


def flag_impact(store: CaseStore, source_id: str, *, actor: str = "cos") -> list[dict]:
    """Deterministic alerts: every claim that stands on the same lineage as new evidence gets a review alert."""
    cand = impact_candidates(store, source_id)
    created = []
    open_pairs = {(x.get("source"), x.get("target")) for x in store.list("alert") if x.get("status") == "open"}
    src = store.require(source_id)
    for cid in cand["claims"]:
        if (source_id, cid) in open_pairs:
            continue
        x = store.create("alert", {
            "kind": "story_review", "status": "open", "severity": "medium", "effect": "requires_research",
            "source": source_id, "target": cid, "title": f"{source_id} toca {cid}: revisar el claim",
            "finding_text": clip(title_of(src), 300),
            "why": "La nueva evidencia comparte linaje (misma hipótesis o finding) con este claim de la story.",
            "options": [{"key": "A", "label": "Revisar el claim con la nueva evidencia", "consequence": "El claim queda needs_review hasta que lo confirmes."},
                        {"key": "B", "label": "Pedir al COS que evalúe el efecto", "consequence": "Clasificación supports / weakens / contradicts con opciones."},
                        {"key": "C", "label": "Sin impacto material", "consequence": "Se registra la decisión y se cierra la alerta."}],
            "recommended": "B", "recommended_why": "La relación existe por linaje; su efecto necesita lectura.",
            "detected_by": "lineage", "links": [source_id, cid]},
            actor=actor, summary=f"COS: {source_id} podría afectar {cid}")
        created.append(x)
    return created


# ------------------------------------------------------------------------------------------ digest for prompts
def digest(store: CaseStore, *, focus: list[str] | None = None, max_findings: int = 70) -> str:
    ents = store.all()
    meta = store.meta()
    fr = store.read_data("framing/current.yaml", {}) or {}
    brief = store.read_data("brief/brief.yaml", {}) or {}

    def of(t):
        return sorted([e for e in ents.values() if e.get("type") == t], key=lambda e: e["id"])

    def a(e):
        return f" ({e['alias']})" if e.get("alias") else ""

    L = [f"# Caso {meta.get('name')} — {meta.get('title', '')}", f"Objetivo: {clip(brief.get('objective', ''), 400)}",
         f"Audiencia: {', '.join(brief.get('audience') or [])}",
         "Fases: " + " · ".join(f"{PHASE_LABELS[p]}={meta['phases'][p].get('status')}" for p in PHASES),
         f"Pregunta ejecutiva del framing: {fr.get('executive_question') or '—'}",
         "No afirmar todavía: " + "; ".join(clip(x, 140) for x in (fr.get("should_not_claim") or [])[:8]),
         "", "## Preguntas ejecutivas"]
    L += [f"- {q['id']}{a(q)} {title_of(q)}" for q in of("question") if q.get("kind") == "executive"]
    L += ["", "## Hipótesis (id · estado · evaluación importada)"]
    for h in of("hypothesis"):
        if _rv(h) == "rejected":
            continue
        asd = h.get("assessed") or {}
        L.append(f"- {h['id']}{a(h)} [{h.get('status', 'open')}{' · agente: ' + asd.get('state', '') if asd else ''}] {clip(title_of(h), 170)}")
    L += ["", "## Research (id · estado · revisión)"]
    for r in of("research"):
        L.append(f"- {r['id']}{a(r)} [{r.get('status')} · {_rv(r)} · {r.get('specialty')}] {clip(r.get('research_question', ''), 120)}"
                 + (f" → {clip(r.get('short_answer', ''), 220)}" if r.get("short_answer") else ""))
    finds = of("finding")
    acc = [f for f in finds if _rv(f) == "accepted"]
    prop = [f for f in finds if _rv(f) == "proposed"]
    L += ["", f"## Findings aceptados ({len(acc)})"] + [f"- {f['id']}{a(f)} [{f.get('confidence', '')}] {clip(title_of(f), 200)}" for f in acc[:max_findings]]
    if focus:
        L += ["", "## Findings en foco"] + [f"- {f['id']}{a(f)} [{_rv(f)}] {clip(title_of(f), 260)}" for f in finds if f["id"] in focus]
    L += ["", f"## Findings propuestos sin revisar: {len(prop)} (IDs: {', '.join(f['id'] for f in prop[:40])}{'…' if len(prop) > 40 else ''})"]
    L += ["", "## Tablas"] + [f"- {t['id']} `{t.get('table_key')}` [{_rv(t)}] {clip(t.get('title', ''), 120)}" for t in of("table")]
    L += ["", "## Decisiones activas"] + [f"- {d['id']} {clip(d.get('title', ''), 150)} → {clip(d.get('user_choice', ''), 120)}" for d in of("decision") if d.get("status") == "active"]
    L += ["", "## Decisiones propuestas"] + [f"- {d['id']} {clip(d.get('title', ''), 150)}" for d in of("decision") if d.get("status") == "proposed"]
    L += ["", "## Alertas abiertas"] + [f"- {x['id']} {x.get('source')} → {x.get('target')}: {clip(x.get('why', ''), 150)}" for x in of("alert") if x.get("status") == "open"]
    done = [x for x in of("alert") if x.get("status") in ("resolved", "dismissed")]
    if done:
        L += ["", "## Alertas resueltas por Hugo (alerta → decisión: opción elegida)"] + [
            f"- {x['id']} → {(x.get('resolution') or {}).get('decision', '—')}: {clip((x.get('resolution') or {}).get('label', ''), 140)}"
            for x in done[-25:]]
    L += ["", "## Claims de la story"] + [f"- {c['id']} [{c.get('status', 'draft')}] {clip(title_of(c), 150)} · evidencia: {', '.join(c.get('evidence_ids') or [])} · tablas: {', '.join(c.get('table_ids') or [])}" for c in of("claim")]
    dnr = decisions.do_not_resurface(store)
    if dnr:
        L += ["", "## No volver a proponer (do_not_resurface)"] + [f"- {x}" for x in dnr[:20]]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------ agent: impact assessment
_S = {"type": "string"}


def _obj(props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


IMPACT_SCHEMA = _obj({
    "summary": _S,
    "impacts": {"type": "array", "items": _obj({
        "target": _S, "effect": {"type": "string", "enum": EFFECTS}, "why": _S,
        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
        "options": {"type": "array", "items": _obj({"key": _S, "label": _S, "consequence": _S})},
        "recommended": _S, "recommended_why": _S})},
    "new_hypotheses": {"type": "array", "items": _obj({"statement": _S, "falsifier": _S})},
    "new_questions": {"type": "array", "items": _S},
    "status_note": _S,
})

ASK_SCHEMA = _obj({
    "answer": _S,
    "referenced_ids": {"type": "array", "items": _S},
    "next_best_actions": {"type": "array", "items": _obj({"title": _S, "why": _S, "ids": {"type": "array", "items": _S}})},
    "status_note": _S,
})


def submit_assessment(store: CaseStore, source_id: str, *, reason: str = "") -> dict:
    job = jobs.submit(store.id, "cos_impact", f"COS evalúa el impacto de {source_id}", {"source_id": source_id, "reason": reason},
                      agent="cos")
    store.log("cos", "queued", [source_id], f"COS evaluará el impacto de {source_id}")
    return {"job_id": job.id}


@jobs.handler("cos_impact")
async def _impact_job(job, params):
    store = cases.get(job.case_id)
    sid = params["source_id"]
    src = store.require(sid)
    cand = impact_candidates(store, sid)
    selected = skills.select("cos", text=params.get("reason", ""))
    system = base.system_prompt("cos", selected, store.meta().get("language"))
    detail = [f"# Nueva evidencia a evaluar: {sid}{' (' + src['alias'] + ')' if src.get('alias') else ''}",
              f"Tipo: {src.get('type')} · revisión: {_rv(src)}", f"Texto: {clip(title_of(src), 800)}"]
    if src.get("type") == "research":
        detail += [f"Respuesta corta: {clip(src.get('short_answer', ''), 1500)}",
                   "Establecido: " + " | ".join(clip(x, 300) for x in (src.get("what_is_established") or [])[:4]),
                   "No podemos concluir: " + " | ".join(clip(x, 300) for x in (src.get("what_remains_unknown") or [])[:4])]
    ents0 = store.all()
    cand_ids = [i for i in cand["hypotheses"] + cand["claims"] + cand["questions"] if i in ents0]
    detail += ["", "Candidatos por linaje (evalúa estos primero; puedes añadir otros IDs existentes si el efecto es claro):",
               *([f"- {i}{' (' + ents0[i]['alias'] + ')' if ents0[i].get('alias') else ''} [{ents0[i].get('type')}] "
                  f"{clip(title_of(ents0[i]), 260)}" for i in cand_ids] or ["—"]),
               f"Motivo de Hugo: {params.get('reason') or '—'}",
               "", "Para cada elemento afectado da un efecto. Solo efectos materiales necesitan opciones (2–3, A/B/C) y recomendación. "
                   "No dupliques alertas abiertas existentes. Target debe ser un ID existente o 'framing'."]
    prompt = "\n".join(detail) + "\n\n" + digest(store, focus=src.get("findings") or [])
    spec = RunSpec(agent="cos", role="cos_impact", system=system, prompt=prompt, schema=IMPACT_SCHEMA, max_turns=4,
                   skills=skills.record(selected), purpose=f"Impacto de {sid}", case_id=store.id, case_root=store.root)
    res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    out = res.output or {}
    ents = store.all()
    created = []
    open_pairs = {(x.get("source"), x.get("target")) for x in store.list("alert") if x.get("status") == "open"}
    with store.batch():
        for imp in out.get("impacts") or []:
            tgt = imp.get("target", "")
            if tgt not in ents and tgt != "framing":
                continue
            if imp.get("effect") not in MATERIAL:
                store.log("cos", "assessed", [sid, tgt], "COS: " + _impact_title(sid, imp.get('effect'), tgt),
                          run_id=res.run_id, data={"why": imp.get("why")})
                continue
            if (sid, tgt) in open_pairs:
                continue
            kind = {"contradicts": "contradiction", "weakens": "weakening", "changes_story": "story_change",
                    "changes_framing": "framing_change", "opens_new_hypothesis": "new_hypothesis",
                    "requires_research": "research_needed"}[imp["effect"]]
            x = store.create("alert", {
                "kind": kind, "status": "open", "severity": imp.get("severity", "medium"), "effect": imp["effect"],
                "source": sid, "target": tgt, "title": _impact_title(sid, imp['effect'], tgt),
                "finding_text": clip(title_of(src), 300), "why": imp.get("why", ""),
                "options": (imp.get("options") or [])[:3], "recommended": imp.get("recommended", ""),
                "recommended_why": imp.get("recommended_why", ""), "detected_by": "cos",
                "links": [i for i in (sid, tgt) if i in ents]},
                actor="cos", run_id=res.run_id, summary="COS: " + _impact_title(sid, imp['effect'], tgt))
            created.append(x["id"])
            if imp["effect"] in ("contradicts", "weakens") and type_of(tgt) in ("claim", "hypothesis"):
                # flagged, never rewritten: the content stays until Hugo picks an option
                store.mark_stale(tgt, reason=f"{x['id']}: {sid} {EFFECT_LABELS[imp['effect']]} {tgt}", actor="cos", phase="synthesis")
        for nh in (out.get("new_hypotheses") or [])[:3]:
            h = store.create("hypothesis", {"statement": nh["statement"], "falsifier": nh.get("falsifier", ""), "status": "open",
                                            "phase": "synthesis", "links": [sid]},
                             actor="cos", run_id=res.run_id, summary=f"COS propone hipótesis: {clip(nh['statement'], 80)}")
            created.append(h["id"])
        for q in (out.get("new_questions") or [])[:3]:
            e = store.create("question", {"text": q, "kind": "research", "status": "open", "phase": "synthesis", "links": [sid]},
                             actor="cos", run_id=res.run_id, summary=f"COS propone pregunta: {clip(q, 80)}", material=False)
            created.append(e["id"])
        if out.get("status_note"):
            store.write_data("cos/state.yaml", {"status_note": out["status_note"], "updated_at": now_iso(), "run_id": res.run_id})
        phases.touch(store, "synthesis", actor="cos")
        store.update(sid, {"cos_assessment": {"summary": out.get("summary", ""), "run_id": res.run_id, "at": now_iso(),
                                              "impacts": [{"target": i.get("target"), "effect": i.get("effect"), "why": i.get("why")}
                                                          for i in out.get("impacts") or []]}},
                     actor="cos", material=True, summary=f"COS evaluó {sid}: {clip(out.get('summary', ''), 100)}", verb="assessed")
    return {"created": created, "summary": out.get("summary", "")}


# ------------------------------------------------------------------------------------------ agent: ask the COS
def submit_ask(store: CaseStore, question: str, *, context_id: str | None = None) -> dict:
    q = (question or "").strip()
    if not q:
        raise ValueError("Pregunta vacía")
    job = jobs.submit(store.id, "cos_ask", f"COS: {clip(q, 60)}", {"question": q, "context_id": context_id}, agent="cos")
    store.log("hugo", "asked", ["cos"] + ([context_id] if context_id else []), f"Hugo al COS: {clip(q, 110)}")
    return {"job_id": job.id}


@jobs.handler("cos_ask")
async def _ask_job(job, params):
    store = cases.get(job.case_id)
    q = params["question"]
    selected = skills.select("cos", text=q)
    system = base.system_prompt("cos", selected, store.meta().get("language"))
    nba = next_best_actions(store)
    ctx = ""
    if params.get("context_id") and store.get(params["context_id"]):
        e = store.get(params["context_id"])
        ctx = f"\nHugo está mirando {e['id']}: {clip(title_of(e), 600)}\n"
    prompt = (f"Pregunta de Hugo: {q}\n{ctx}\nAcciones que el código ya detectó (reglas):\n" +
              "\n".join(f"- {a['title']} ({a['why']})" for a in nba) + "\n\n" + digest(store) +
              "\n\nResponde en el registro de Hugo, con IDs. Si la respuesta depende de algo que no está en el estado, dilo.")
    spec = RunSpec(agent="cos", role="cos", system=system, prompt=prompt, schema=ASK_SCHEMA, max_turns=4,
                   skills=skills.record(selected), purpose=f"Pregunta al COS: {clip(q, 80)}", case_id=store.id,
                   case_root=store.root)
    res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    out = res.output or {}
    ents = store.all()
    refs = [i for i in out.get("referenced_ids") or [] if i in ents]
    rec = {"ts": now_iso(), "question": q, "answer": out.get("answer", ""), "referenced_ids": refs,
           "next_best_actions": out.get("next_best_actions") or [], "run_id": res.run_id, "context_id": params.get("context_id")}
    from .util import append_jsonl
    append_jsonl(store.root / "cos" / "conversation.jsonl", rec)
    if out.get("status_note"):
        store.write_data("cos/state.yaml", {"status_note": out["status_note"], "updated_at": now_iso(), "run_id": res.run_id})
    store.log("cos", "answered", refs[:6], f"COS respondió: {clip(out.get('answer', ''), 120)}", run_id=res.run_id,
              material=bool(out.get("status_note")))
    return rec


def conversation(store: CaseStore, limit: int = 30) -> list[dict]:
    from .util import read_jsonl
    return read_jsonl(store.root / "cos" / "conversation.jsonl", limit=limit)


# ------------------------------------------------------------------------------------------ Hugo resolves an alert
def resolve_alert(store: CaseStore, xid: str, *, choice: str, rationale: str = "", actor: str = "hugo") -> dict:
    """Hugo picks an option (A/B/C) or one of discuss · research · update · ignore. Always recorded as a decision.

    Everything that can fail is checked before anything is written, so a resolution is never half-applied."""
    if actor != "hugo":
        raise ValueError("Solo Hugo resuelve alertas.")
    x = store.require(xid)
    if x.get("status") != "open":
        raise ValueError(f"{xid} ya está {x.get('status')}.")
    opts = {o["key"]: o for o in x.get("options") or []}
    label = opts[choice]["label"] if choice in opts else {"discuss": "Discutirlo con el Framer", "research": "Investigar más",
                                                           "update": "Actualizar el elemento afectado",
                                                           "ignore": "Sin impacto material"}.get(choice, choice)
    tgt = x.get("target") or ""
    te = store.get(tgt) if tgt and type_of(tgt) else None          # "framing" is a target without an entity
    on_framing = tgt == "framing"
    d = decisions.record_decision(store, title=f"{x.get('title', xid)}: {label}", context=x.get("why", ""),
                                  options={o["key"]: o["label"] for o in x.get("options") or []},
                                  agent_recommendation=f"{x.get('recommended', '')} — {x.get('recommended_why', '')}".strip(" —"),
                                  user_choice=label, user_rationale=rationale,
                                  affected_items=[i for i in (x.get("source"), tgt) if i],
                                  downstream_impact=opts.get(choice, {}).get("consequence", ""), kind="synthesis",
                                  phase="synthesis", actor=actor)
    status = "dismissed" if choice == "ignore" else "resolved"
    store.update(xid, {"status": status, "resolution": {"choice": choice, "label": label, "decision": d["id"], "at": now_iso()}},
                 actor=actor, summary=f"Hugo resolvió {xid}: {label}", verb="resolved")
    follow = {}
    if choice == "ignore" and te and str((te.get("stale") or {}).get("reason", "")).startswith(f"{xid}:"):
        store.update(tgt, {"stale": None}, actor=actor, summary=f"{tgt}: sin impacto material ({xid}); vuelve a su estado",
                     material=False, verb="cleared")
    elif choice in ("update", "A"):
        if te:
            store.mark_stale(tgt, reason=f"{xid}: {label}", actor=actor, phase="synthesis")
            follow["flagged"] = tgt
        elif on_framing:
            # the framing changes through the Framer (and Hugo's approval), never by the COS directly
            if store.meta()["phases"]["framing"].get("status") == "ready":
                phases.set_status(store, "framing", "needs_review", actor=actor, note=f"{xid}: {label}")
                follow["phase_flagged"] = "framing"
            follow["framer_prefill"] = f"Aplicar al framing lo que decidí en {xid}: {label}"
    if choice == "research":
        follow["research_prefill"] = {"question": f"Profundizar: {x.get('finding_text', '')}",
                                      "links": [i for i in (x.get("source"), tgt) if i and type_of(i)]}
    if choice == "discuss":
        follow["framer_prefill"] = f"El COS detectó: {x.get('title')}. {x.get('why', '')} ¿Cómo lo reencuadramos?"
    return {"decision": d["id"], "status": status, **follow}


def _impact_title(sid: str, effect: str | None, tgt: str) -> str:
    label = EFFECT_LABELS.get(effect or "", "")
    return f"{sid} {label}" if tgt == "framing" and "framing" in label else f"{sid} {label} {tgt}"


def _priority_value(e: dict) -> int | None:
    """'3 × 2 = 6 · P1' → 6; None when the priority has no product (e.g. 'Aparcada por defecto')."""
    import re
    m = re.search(r"=\s*(\d+)", str(e.get("priority") or ""))
    return int(m.group(1)) if m else None


def dedupe_text(xs: list[str]) -> list[str]:
    seen, out = set(), []
    for x in xs:
        k = norm(x)
        if k and k not in seen:
            seen.add(k)
            out.append(x)
    return out
