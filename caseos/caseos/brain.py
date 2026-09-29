"""brain.md — the case's living executive memory.

Rendered by code from the case state on every material change. It is deliberately selective: only what an
executive (or an agent picking up the case) needs — approved artifacts, active decisions, trusted evidence,
what we cannot claim, open loops. Everything else stays in its own file and is linked by ID.
"""
from __future__ import annotations

from .model import KIND_LABELS, PHASE_LABELS, PHASES, title_of
from .store import CaseStore
from .util import clip, now_iso, read_jsonl, yaml_dump

CAP = 10


def _acc(e: dict) -> bool:
    return (e.get("review") or {}).get("state") == "accepted"


def _live(e: dict) -> bool:
    return (e.get("review") or {}).get("state") != "rejected"


def _lines(items: list[str], empty: str, cap: int = CAP) -> str:
    if not items:
        return f"_{empty}_\n"
    more = f"\n- … y {len(items) - cap} más" if len(items) > cap else ""
    return "\n".join(f"- {x}" for x in items[:cap]) + more + "\n"


def render(store: CaseStore, reason: str = "") -> str:
    meta = store.meta()
    ents = store.all()
    fr = store.read_data("framing/current.yaml", {}) or {}
    brief = store.read_data("brief/brief.yaml", {}) or {}
    pkg = store.read_data("story/package.yaml", {}) or {}
    lang = meta.get("language") or {}

    def of(t):
        return sorted([e for e in ents.values() if e.get("type") == t], key=lambda e: e["id"])

    def ref(e, extra=""):
        stale = " ⚠ needs_review" if e.get("stale") else ""
        alias = f" ({e['alias']})" if e.get("alias") else ""
        return f"**{e['id']}**{alias} {clip(title_of(e), 180)}{extra}{stale}"

    out = [f"# CASE BRAIN — {meta.get('name', store.id)}", "",
           "> Memoria ejecutiva viva del caso. La genera CaseOS desde el estado del caso ante cada cambio material; "
           "no guarda todo, solo lo relevante. Cada ID enlaza a su archivo.",
           f"> Actualizado: {now_iso()}" + (f" · motivo: {clip(reason, 140)}" if reason else ""), ""]

    out += ["## Case", f"{meta.get('title') or meta.get('name', store.id)}" + (f" — {meta['client']}" if meta.get("client") else ""), ""]
    out += ["## Objective", (brief.get("objective") or meta.get("objective") or "_Sin objetivo definido._"), ""]
    aud = brief.get("audience") or meta.get("audience") or []
    out += ["## Audience", (", ".join(aud) if isinstance(aud, list) else str(aud)) or "_Sin audiencia definida._", ""]

    rows = ["| Fase | Estado | Ready |", "|---|---|---|"]
    for i, p in enumerate(PHASES):
        st = meta["phases"][p]
        rows.append(f"| {i + 1:02d} {PHASE_LABELS[p]} | {st.get('status', 'not_started')} | "
                    f"{('v' + str(st.get('ready_count')) + ' · ' + str(st.get('ready_at', ''))[:16]) if st.get('ready_count') else '—'} |")
    from .phases import current_phase
    out += ["## Current Phase", f"**{PHASE_LABELS[current_phase(meta)]}**", "", *rows, ""]

    res = of("research")
    status_line = (f"{len([r for r in res if r.get('status') == 'completed'])} investigaciones completadas "
                   f"({len([r for r in res if _acc(r)])} aceptadas), "
                   f"{len([r for r in res if r.get('status') in ('queued', 'running')])} en curso, "
                   f"{len([r for r in res if r.get('status') == 'blocked'])} bloqueadas · "
                   f"{len([f for f in of('finding') if _acc(f)])} findings aceptados · "
                   f"{len([d for d in of('decision') if d.get('status') == 'active'])} decisiones activas · "
                   f"{len([x for x in of('alert') if x.get('status') == 'open'])} alertas abiertas.")
    cos_note = (store.read_data("cos/state.yaml", {}) or {}).get("status_note")
    out += ["## Current Status", status_line, *( ["", f"COS: {cos_note}"] if cos_note else []), ""]

    bst = meta["phases"]["briefing"]
    out += ["## Approved Briefing",
            (f"v{bst['ready_count']} aprobada el {str(bst.get('ready_at', ''))[:10]} → `{bst.get('approved_artifact')}`"
             if bst.get("ready_count") else "_Pendiente de aprobación (brief en `brief/brief.md`)._"), ""]
    fst = meta["phases"]["framing"]
    out += ["## Approved Framing",
            (f"v{fst['ready_count']} aprobada el {str(fst.get('ready_at', ''))[:10]} → `{fst.get('approved_artifact')}`"
             if fst.get("ready_count") else "_Pendiente de aprobación (framing vivo en `framing/current.md`)._"), ""]
    out += ["## Governing Question", (fr.get("executive_question") or "_Sin pregunta ejecutiva todavía._"), ""]

    execq = [q for q in of("question") if q.get("kind") == "executive" and _live(q)]
    out += ["## Executive Questions", _lines([ref(q) for q in execq], "Sin preguntas ejecutivas.")]

    claims = [c for c in of("claim") if _live(c)]
    story_lines = []
    if pkg.get("governing_thought"):
        story_lines.append(f"**Governing thought:** {pkg['governing_thought']}")
    for c in claims[:CAP]:
        story_lines.append("- " + ref(c, " · " + str(c.get("status", "draft"))))
    out += ["## Current Story", ("\n".join(story_lines) if story_lines else
                                 ("\n".join(f"- {s}" for s in (fr.get("initial_storyline") or [])[:6]) or "_Sin story todavía._")), ""]

    decs = [d for d in of("decision") if d.get("status") == "active"]
    decs = sorted(decs, key=lambda d: d.get("created_at", ""), reverse=True)
    out += ["## Decisions", _lines([f"**{d['id']}** {clip(d.get('title', ''), 140)} · {d.get('date', '')}"
                                    + (f" → {clip(d.get('user_choice', ''), 60)}" if d.get("user_choice") else "") for d in decs],
                                   "Sin decisiones activas.")]
    pend = [d for d in of("decision") if d.get("status") == "proposed"]
    if pend:
        out += ["_Por confirmar:_ " + ", ".join(d["id"] for d in pend), ""]

    hyps = [h for h in of("hypothesis") if _live(h) and h.get("status") != "rejected"]
    out += ["## Active Hypotheses", _lines([ref(h, f" · {h.get('status', 'open')}") for h in hyps], "Sin hipótesis activas.")]

    trust = [f for f in of("finding") if _acc(f)]
    out += ["## Evidence We Trust", _lines([ref(f, f" · {f.get('confidence', '')}".rstrip(" ·")) for f in trust],
                                           "Todavía no hay evidencia aceptada.")]

    cannot = list(fr.get("should_not_claim") or [])
    for r in res:
        if _acc(r):
            cannot += [f"{x} ({r['id']})" for x in (r.get("cannot_claim") or [])[:2]]
    out += ["## Things We Cannot Claim", _lines(cannot, "Nada registrado.")]

    openq = [q for q in of("question") if q.get("status", "open") == "open" and _live(q) and q.get("kind") != "executive"]
    out += ["## Open Questions", _lines([ref(q) for q in openq], "Sin preguntas abiertas.")]

    queue = [r for r in res if r.get("status") in ("queued", "running", "blocked", "failed") or
             (r.get("status") == "completed" and (r.get("review") or {}).get("state") == "proposed")]
    out += ["## Research Queue", _lines([ref(r, f" · {r.get('status')}" + (" · por revisar" if r.get("status") == "completed" else ""))
                                         for r in queue], "Cola vacía.")]

    fw = [d for d in decs if d.get("kind") == "framework"]
    frames = [f"{c.get('name')}: {clip(c.get('description', ''), 100)}" for c in (fr.get("candidate_frames") or []) if c.get("chosen")]
    out += ["## Accepted Frameworks", _lines([f"**{d['id']}** {d.get('title')}" for d in fw] + frames, "Ningún framework aceptado todavía.")]

    tables = [t for t in of("table") if _acc(t)]
    out += ["## Key Tables", _lines([f"**{t['id']}** `{t.get('table_key', '')}` {clip(t.get('title', ''), 110)}" for t in tables],
                                    "Sin tablas aceptadas.")]

    contra = [x for x in of("alert") if x.get("status") == "open" and x.get("kind") == "contradiction"]
    out += ["## Contradictions", _lines([ref(x) for x in contra], "Sin contradicciones abiertas.")]

    risks = [x for x in of("alert") if x.get("status") == "open" and x.get("severity") == "high" and x.get("kind") != "contradiction"]
    risk_lines = [ref(x) for x in risks] + [f"{r}" for r in (fr.get("risks") or [])]
    out += ["## Risks", _lines(risk_lines, "Sin riesgos altos abiertos.")]

    arts = []
    for p in PHASES:
        st = meta["phases"][p]
        if st.get("approved_artifact"):
            arts.append(f"{PHASE_LABELS[p]} v{st.get('ready_count')}: `{st['approved_artifact']}`")
    arts += [f"**{a['id']}** {clip(title_of(a), 100)} (`{a.get('path', '')}`)" for a in of("artifact")][:CAP]
    out += ["## Artifacts", _lines(arts, "Sin artefactos aprobados todavía.")]

    prof = {k: lang.get(k) for k in ("primary", "tone", "technical_level", "preserve_user_vocabulary",
                                     "avoid_unnecessary_jargon") if k in lang}
    obs = lang.get("observed") or {}
    out += ["## Language Profile", "```yaml", yaml_dump({"language": prof}).strip(), "```"]
    if obs:
        terms = ", ".join((obs.get("preserved_terms") or [])[:14])
        out += [f"Registro observado: {obs.get('register', '—')} · nivel técnico: {obs.get('technical_level', '—')}"
                + (f" · vocabulario de Hugo: {terms}" if terms else "")]
    out += [""]

    acts = [a for a in read_jsonl(store.root / "audit" / "activity.jsonl", limit=400) if a.get("material")][-CAP:]
    out += ["## Recent Material Changes", _lines([f"{a['ts'][:16].replace('T', ' ')} · {a['summary']}" for a in reversed(acts)],
                                                 "Sin cambios todavía.")]
    kinds = {}
    for n in of("note"):
        if _live(n):
            kinds[n.get("kind")] = kinds.get(n.get("kind"), 0) + 1
    if kinds:
        out += ["", "<!-- ideas del framing por tipo: " + ", ".join(f"{KIND_LABELS.get(k, k)} {v}" for k, v in kinds.items()) + " -->"]
    return "\n".join(out).rstrip() + "\n"


def update(store: CaseStore, reason: str = "") -> None:
    store.write_text("brain.md", render(store, reason))


def install(store: CaseStore) -> None:
    """Register brain.md re-rendering on every material change of this store."""
    if update not in [getattr(h, "__wrapped__", h) for h in store.material_hooks]:
        store.material_hooks.append(update)
