"""Phase system and human gates.

Only Hugo marks a phase Ready. Marking Ready: snapshot → approved artifact → brain.md → decision → timestamp →
next phase unlocked → previous versions preserved. Reopening computes the impact radius first and never deletes:
downstream work is flagged needs_review.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from . import lineage
from .model import PHASE_LABELS, PHASES, phase_index, title_of
from .store import CaseStore, StoreError
from .util import now_iso, stamp, write_yaml, yaml_dump

HUMAN = "hugo"


class GateError(StoreError):
    pass


def phases_view(store: CaseStore) -> list[dict]:
    meta = store.meta()
    out = []
    for i, p in enumerate(PHASES):
        st = meta["phases"][p]
        out.append({"id": p, "n": f"{i + 1:02d}", "label": PHASE_LABELS[p], "status": st.get("status", "not_started"),
                    "unlocked": unlocked(meta, p), "ready_count": st.get("ready_count", 0),
                    "ready_at": st.get("ready_at"), "note": st.get("note"), "snapshot": st.get("snapshot"),
                    "approved_artifact": st.get("approved_artifact")})
    return out


def unlocked(meta: dict, phase: str) -> bool:
    """A phase is unlocked once every earlier phase has been marked Ready at least once."""
    i = phase_index(phase)
    return all((meta["phases"][p].get("ready_count") or 0) > 0 for p in PHASES[:i])


def current_phase(meta: dict) -> str:
    for p in PHASES:
        if meta["phases"][p].get("status") != "ready":
            return p
    return PHASES[-1]


def set_status(store: CaseStore, phase: str, status: str, *, actor: str, note: str = "", log: bool = True) -> dict:
    meta = store.meta()
    rec = meta["phases"][phase]
    prev = rec.get("status", "not_started")
    if prev == status:
        return rec
    rec["status"] = status
    rec.setdefault("history", []).append({"at": now_iso(), "from": prev, "to": status, "by": actor, "note": note})
    store.save_meta(meta)
    if log:
        store.log(actor, "phase", [phase], f"{PHASE_LABELS[phase]}: {prev} → {status}" + (f" ({note})" if note else ""),
                  material=True, data={"phase": phase, "from": prev, "to": status})
    return rec


def touch(store: CaseStore, phase: str, *, actor: str) -> None:
    """Work started in a phase: not_started → in_progress (never moves a phase backwards)."""
    meta = store.meta()
    if meta["phases"][phase].get("status", "not_started") == "not_started":
        set_status(store, phase, "in_progress", actor=actor, note="trabajo iniciado")


def propose_review(store: CaseStore, phase: str, *, actor: str, note: str) -> None:
    meta = store.meta()
    if meta["phases"][phase].get("status") in ("not_started", "in_progress"):
        set_status(store, phase, "review", actor=actor, note=note)


# ------------------------------------------------------------------------------------------ readiness checks
def readiness(store: CaseStore, phase: str) -> dict:
    """Blockers stop Mark Ready; warnings are shown to Hugo, who decides."""
    meta = store.meta()
    ents = store.all()
    blockers, warnings = [], []
    i = phase_index(phase)
    for p in PHASES[:i]:
        st = meta["phases"][p].get("status")
        if (meta["phases"][p].get("ready_count") or 0) == 0:
            blockers.append(f"{PHASE_LABELS[p]} todavía no se ha marcado Ready.")
        elif st in ("reopened", "needs_review"):
            blockers.append(f"{PHASE_LABELS[p]} está {'reabierta' if st == 'reopened' else 'en revisión'}: ciérrala antes.")

    def of(t, **kw):
        return [e for e in ents.values() if e.get("type") == t and all(e.get(k) == v for k, v in kw.items())]

    def rv(e):
        return (e.get("review") or {}).get("state")

    if phase == "briefing":
        brief = store.read_data("brief/brief.yaml", {}) or {}
        for k, label in (("objective", "objetivo"), ("audience", "audiencia"), ("deliverables", "entregables")):
            if not brief.get(k):
                blockers.append(f"El brief no tiene {label}.")
        if brief.get("gaps"):
            warnings.append(f"El brief declara {len(brief['gaps'])} vacío(s) de información.")
    elif phase == "framing":
        fr = store.read_data("framing/current.yaml", {}) or {}
        if not (fr.get("executive_question") or "").strip():
            blockers.append("Falta la pregunta ejecutiva del framing.")
        hyps = [h for h in of("hypothesis") if rv(h) != "rejected"]
        if not hyps:
            blockers.append("No hay hipótesis activas.")
        nofals = [h["id"] for h in hyps if not (h.get("falsifier") or "").strip()]
        if nofals:
            warnings.append(f"Hipótesis sin falsificador: {', '.join(nofals[:6])}{'…' if len(nofals) > 6 else ''}.")
        pend = [e["id"] for e in ents.values() if e.get("phase") == "framing" and rv(e) == "proposed"]
        if pend:
            warnings.append(f"{len(pend)} elemento(s) del framing siguen propuestos; al aprobar quedan aceptados.")
    elif phase == "research":
        done = [r for r in of("research") if r.get("status") == "completed"]
        if not done:
            blockers.append("No hay investigación completada.")
        if not [r for r in done if rv(r) == "accepted"]:
            warnings.append("Ninguna investigación ha sido aceptada todavía.")
        running = [r["id"] for r in of("research") if r.get("status") in ("queued", "running")]
        if running:
            warnings.append(f"Investigación en curso: {', '.join(running)}.")
        orphan = [r["id"] for r in of("research") if not r.get("purpose_ok", True)]
        if orphan:
            warnings.append(f"Research sin propósito de caso: {', '.join(orphan)}.")
        unrev = [r["id"] for r in done if rv(r) == "proposed"]
        if unrev:
            warnings.append(f"Resultados por revisar: {', '.join(unrev[:8])}{'…' if len(unrev) > 8 else ''}.")
    elif phase == "synthesis":
        openx = [x["id"] for x in of("alert", status="open")]
        if openx:
            warnings.append(f"Alertas abiertas del COS: {', '.join(openx)}.")
        opend = [d["id"] for d in of("decision", status="proposed")]
        if opend:
            warnings.append(f"Decisiones propuestas sin confirmar: {', '.join(opend)}.")
    elif phase == "story":
        pkg = store.read_data("story/package.yaml")
        if not pkg:
            blockers.append("No hay Story Package generado.")
        else:
            from .story import validate_package  # late import: story depends on phases for gates
            errs, warns = validate_package(store, pkg)
            blockers += errs
            warnings += warns
    elif phase == "slides":
        decks = store.read_data("slides/decks.yaml", {}) or {}
        if not [d for d in (decks.get("decks") or []) if d.get("status") == "completed"]:
            blockers.append("No hay un deck terminado por el Visual Storyteller.")
    stale = [e["id"] for e in ents.values() if e.get("phase") == phase and e.get("stale")]
    if stale:
        warnings.append(f"Elementos marcados needs_review: {', '.join(stale[:8])}{'…' if len(stale) > 8 else ''}.")
    return {"phase": phase, "ok": not blockers, "blockers": blockers, "warnings": warnings}


# ------------------------------------------------------------------------------------------ mark ready
_SNAPSHOT_IGNORE = shutil.ignore_patterns("snapshots", "versions", "renders", "fonts", "*.png", "*.pdf", ".DS_Store")


def mark_ready(store: CaseStore, phase: str, *, actor: str, note: str = "") -> dict:
    if actor != HUMAN:
        raise GateError("Solo Hugo puede marcar una fase como Ready.")
    check = readiness(store, phase)
    if not check["ok"]:
        raise GateError("No se puede marcar Ready: " + " ".join(check["blockers"]))
    meta = store.meta()
    rec = meta["phases"][phase]
    version = (rec.get("ready_count") or 0) + 1
    ts = stamp()
    with store.batch():
        # 1. snapshot of the whole case (small YAML; heavy renders excluded)
        snap = store.root / "snapshots" / phase / f"v{version}-{ts}"
        snap.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(store.root, snap, ignore=_SNAPSHOT_IGNORE)
        # 2. approved artifact for the phase (previous versions stay in place)
        approved_rel = _write_approved(store, phase, version)
        # 2b. framing approval accepts what is still proposed inside the framing
        if phase == "framing":
            for e in store.all().values():
                if e.get("phase") == "framing" and (e.get("review") or {}).get("state") == "proposed":
                    store.set_review(e["id"], "accepted", actor=actor, note="aceptado al aprobar el framing")
        # 4. decision
        from .decisions import record_decision
        dec = record_decision(store, title=f"{PHASE_LABELS[phase]} marcada Ready (v{version})",
                              context=note or f"Hugo aprobó {PHASE_LABELS[phase]}.",
                              options={}, agent_recommendation="", user_choice="Ready", user_rationale=note,
                              affected_items=[], downstream_impact=_unlock_text(phase), kind="phase_gate",
                              phase=phase, actor=actor)
        # 5–6. timestamp and unlock (status of later phases is derived; needs_review stays until re-marked)
        meta = store.meta()
        rec = meta["phases"][phase]
        prev = rec.get("status")
        rec.update({"status": "ready", "ready_count": version, "ready_at": now_iso(), "ready_by": actor,
                    "note": note, "snapshot": str(snap.relative_to(store.root)), "approved_artifact": approved_rel,
                    "decision": dec["id"]})
        rec.setdefault("history", []).append({"at": now_iso(), "from": prev, "to": "ready", "by": actor, "note": note,
                                             "version": version, "snapshot": str(snap.relative_to(store.root))})
        store.save_meta(meta)
        for e in store.all().values():
            if e.get("phase") == phase and e.get("stale"):
                store.update(e["id"], {"stale": None}, actor=actor, summary=f"{e['id']} revisado al marcar Ready",
                             material=False, verb="cleared")
        store.log(actor, "ready", [phase, dec["id"]], f"{PHASE_LABELS[phase]} marcada Ready (v{version})", material=True,
                  data={"phase": phase, "version": version, "snapshot": str(snap.relative_to(store.root))})
    return {"phase": phase, "version": version, "snapshot": str(snap.relative_to(store.root)),
            "approved_artifact": approved_rel, "decision": dec["id"], "warnings": check["warnings"]}


def _unlock_text(phase: str) -> str:
    i = phase_index(phase)
    return f"Desbloquea {PHASE_LABELS[PHASES[i + 1]]}." if i + 1 < len(PHASES) else "Cierra el caso."


def _write_approved(store: CaseStore, phase: str, version: int) -> str:
    """Copy of the phase's approved artifact, versioned; earlier versions are preserved."""
    src = {"briefing": ["brief/brief.md", "brief/brief.yaml"], "framing": ["framing/current.md", "framing/current.yaml"],
           "story": ["story/current.md", "story/package.yaml"], "slides": ["slides/decks.yaml"]}.get(phase)
    base = {"briefing": "brief", "framing": "framing", "research": "research", "synthesis": "cos",
            "story": "story", "slides": "slides"}[phase]
    out_dir = store.root / base / "approved"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    if src:
        for rel in src:
            p = store.root / rel
            if p.exists():
                dst = out_dir / f"{Path(rel).stem}.v{version}{Path(rel).suffix}"
                shutil.copy2(p, dst)
                written.append(str(dst.relative_to(store.root)))
    else:
        # research / synthesis: a summary of what was accepted at this gate
        ents = store.all()
        acc = lambda t: [e for e in ents.values() if e.get("type") == t and (e.get("review") or {}).get("state") == "accepted"]  # noqa: E731
        summary = {"phase": phase, "version": version, "approved_at": now_iso(),
                   "research": [{"id": e["id"], "question": title_of(e), "short_answer": e.get("short_answer")} for e in acc("research")],
                   "findings": [{"id": e["id"], "headline": title_of(e)} for e in acc("finding")],
                   "tables": [{"id": e["id"], "table_key": e.get("table_key"), "title": e.get("title")} for e in acc("table")],
                   "decisions": [{"id": e["id"], "title": e.get("title")} for e in ents.values() if e.get("type") == "decision" and e.get("status") == "active"],
                   "alerts_open": [e["id"] for e in ents.values() if e.get("type") == "alert" and e.get("status") == "open"]}
        dst = out_dir / f"{phase}.v{version}.yaml"
        write_yaml(dst, summary)
        written.append(str(dst.relative_to(store.root)))
    return written[0] if written else ""


# ------------------------------------------------------------------------------------------ reopen
def impact(store: CaseStore, phase: str) -> dict:
    ents = store.all()
    rad = lineage.impact_radius(ents, phase)
    meta = store.meta()
    later_ready = [p for p in rad["later_phases"] if meta["phases"][p].get("status") in ("ready", "review")]
    labels = {"research": "research items", "finding": "findings", "table": "tablas", "claim": "story claims",
              "slide": "slide specs", "decision": "decisiones", "alert": "alertas", "question": "preguntas",
              "hypothesis": "hipótesis", "note": "ideas", "artifact": "artefactos"}
    lines = []
    for t, ids in rad["by_type"].items():
        acc = [i for i in ids if i in rad["accepted"]]
        lines.append({"type": t, "label": labels.get(t, t), "count": len(ids), "accepted": len(acc), "ids": ids})
    return {**rad, "later_ready_phases": later_ready, "lines": lines,
            "headline": f"Reabrir {PHASE_LABELS[phase]} puede afectar: " +
                        (", ".join(f"{ln['count']} {ln['label']}" for ln in lines) if lines else "nada aguas abajo todavía")}


def reopen(store: CaseStore, phase: str, *, actor: str, reason: str) -> dict:
    if actor != HUMAN:
        raise GateError("Solo Hugo puede reabrir una fase.")
    meta = store.meta()
    if (meta["phases"][phase].get("ready_count") or 0) == 0 and meta["phases"][phase].get("status") != "ready":
        raise GateError(f"{PHASE_LABELS[phase]} nunca se marcó Ready: no hay nada que reabrir.")
    imp = impact(store, phase)
    with store.batch():
        set_status(store, phase, "reopened", actor=actor, note=reason)
        for p in imp["later_phases"]:
            st = store.meta()["phases"][p].get("status")
            if st in ("ready", "review"):
                set_status(store, p, "needs_review", actor=actor, note=f"reapertura de {PHASE_LABELS[phase]}")
        for eid in imp["affected"]:
            store.mark_stale(eid, reason=f"Reapertura de {PHASE_LABELS[phase]}: {reason}", actor=actor, phase=phase)
        from .decisions import record_decision
        dec = record_decision(store, title=f"Reabrir {PHASE_LABELS[phase]}", context=reason, options={},
                              agent_recommendation="", user_choice="Reabrir", user_rationale=reason,
                              affected_items=imp["affected"], downstream_impact=imp["headline"], kind="phase_gate",
                              phase=phase, actor=actor)
        store.log(actor, "reopened", [phase, dec["id"]], f"{PHASE_LABELS[phase]} reabierta: {reason}", material=True,
                  data={"affected": len(imp["affected"])})
    return {**imp, "decision": dec["id"]}


def snapshot_list(store: CaseStore) -> list[dict]:
    root = store.root / "snapshots"
    out = []
    if root.exists():
        for ph in sorted(root.iterdir()):
            if ph.is_dir():
                for s in sorted(ph.iterdir(), reverse=True):
                    if s.is_dir():
                        out.append({"phase": ph.name, "name": s.name, "path": str(s.relative_to(store.root))})
    return out


def dump_state_yaml(store: CaseStore) -> str:  # debugging helper
    return yaml_dump({"phases": store.meta()["phases"]})
