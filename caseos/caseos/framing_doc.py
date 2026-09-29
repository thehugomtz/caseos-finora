"""The current framing: structured state (framing/current.yaml + entities) and its document (framing/current.md).

The document is the Shaping document (caseos/shaping.py): the portable artifact that gets approved, snapshotted and
read by other agents — problem, executive question, storyline guide, hypotheses, research plan and limits — with the
epistemic ledger (facts, intuitions, assumptions, questions…) as an appendix.
"""
from __future__ import annotations

from .model import KIND_LABELS, title_of
from .store import CaseStore
from .util import clip, now_iso


def state(store: CaseStore) -> dict:
    fr = store.read_data("framing/current.yaml", {}) or {}
    ents = store.all()

    def live(e):
        return (e.get("review") or {}).get("state") != "rejected" and e.get("status") not in ("superseded",)

    notes = [e for e in ents.values() if e.get("type") == "note" and live(e)]
    by_kind: dict[str, list[dict]] = {}
    for n in sorted(notes, key=lambda e: e["id"]):
        by_kind.setdefault(n.get("kind", "OBSERVATION"), []).append(_row(n))
    hyps = [_row(h) for h in sorted(ents.values(), key=lambda e: e["id"])
            if h.get("type") == "hypothesis" and live(h)]
    qs = [_row(q) for q in sorted(ents.values(), key=lambda e: e["id"])
          if q.get("type") == "question" and live(q) and q.get("status", "open") == "open"]
    decisions = [_row(d) for d in sorted(ents.values(), key=lambda e: e["id"])
                 if d.get("type") == "decision" and d.get("kind") in ("framing", "framework", "scope") and d.get("status") in ("active", "proposed")]
    dual = [{"id": e["id"], "hugo_wording": e.get("hugo_wording"), "structured": e.get("structured") or title_of(e),
             "verbatim": e.get("verbatim", True), "kind": e.get("kind") or e.get("type")}
            for e in sorted(ents.values(), key=lambda e: e.get("created_at", ""), reverse=True)
            if live(e) and (e.get("hugo_wording") or "").strip() and e.get("type") in ("note", "hypothesis", "question")]
    return {**fr, "ledger": by_kind, "hypotheses": hyps, "open_questions": qs, "framing_decisions": decisions,
            "dual": dual[:40]}


def _row(e: dict) -> dict:
    return {"id": e["id"], "type": e.get("type"), "kind": e.get("kind"), "text": title_of(e),
            "hugo_wording": e.get("hugo_wording"), "structured": e.get("structured"),
            "status": e.get("status"), "review": (e.get("review") or {}).get("state"), "stale": bool(e.get("stale")),
            "falsifier": e.get("falsifier"), "confidence": e.get("confidence"), "basis": e.get("basis"),
            "priority": e.get("priority"), "alias": e.get("alias"), "links": e.get("links") or []}


def save(store: CaseStore, fr: dict, *, actor: str, summary: str, material: bool = True) -> dict:
    fr["updated_at"] = now_iso()
    fr["version"] = int(fr.get("version") or 0) + 1
    prev = store.read_data("framing/current.yaml")
    if prev:
        store.write_data(f"framing/versions/v{prev.get('version', 0)}.yaml", prev)
    store.write_data("framing/current.yaml", fr)
    render_md(store)
    store.log(actor, "framing", ["framing"], summary, material=material)
    return fr


def render_md(store: CaseStore) -> str:
    """framing/current.md is the Shaping document: the structured output of Framing that Hugo approves and every later
    agent reads — problem, executive question, storyline guide, hypotheses, research plan, limits — with the full
    epistemic ledger as an appendix."""
    s = state(store)
    fr = store.read_data("framing/current.yaml", {}) or {}
    from .shaping import KINDS

    def items(rows, empty="—"):
        if not rows:
            return f"_{empty}_\n"
        out = []
        for r in rows:
            flag = " _(propuesto)_" if r.get("review") == "proposed" else ""
            stale = " ⚠ needs_review" if r.get("stale") else ""
            line = f"- **{r['id']}** {r['text']}{flag}{stale}"
            if r.get("falsifier"):
                line += f"\n  - _Se debilita si:_ {r['falsifier']}"
            out.append(line)
        return "\n".join(out) + "\n"

    def plain(xs, empty="—"):
        if not xs:
            return f"_{empty}_\n"
        return "\n".join(f"- {x if isinstance(x, str) else (x.get('text') or x.get('name') or x.get('question') or x)}" for x in xs) + "\n"

    pr = fr.get("problem") or {}
    md = ["# FRAMING & SHAPING", f"> Versión {s.get('version', 1)} · actualizado {str(s.get('updated_at', ''))[:16]}"
          + (f" · {len(fr.get('pending') or {})} propuesta(s) esperando a Hugo" if fr.get("pending") else ""), "",
          "## 1. Problema"]
    if pr:
        md += [pr.get("statement") or "_Sin enunciado._", ""]
        if pr.get("situation"):
            md += [f"**Situación.** {pr['situation']}", ""]
        if pr.get("why_it_matters"):
            md += [f"**Por qué importa.** {pr['why_it_matters']}", ""]
        md += ["**Dentro del alcance**", plain(pr.get("in_scope")), "**Fuera del alcance (no-gos, rabbit holes)**", plain(pr.get("out_of_scope"))]
    else:
        md += ["_Sin aprobar todavía._", ""]
    md += ["## 2. Pregunta ejecutiva", s.get("executive_question") or "_Sin definir todavía._", "", "## 3. Guion de la historia"]
    guide = fr.get("storyline_guide") or []
    if guide:
        for sec in guide:
            md.append(f"### {sec['id']} · {sec.get('title') or '—'}")
            if sec.get("purpose"):
                md += [f"_{ln.strip()}_" for ln in sec["purpose"].splitlines() if ln.strip()] + [""]
            for sl in sec.get("slides") or []:
                md.append(f"- **{sl['id']} {sl.get('title') or ''}**" + (f" — {sl['question']}" if sl.get("question") else ""))
                if sl.get("intent"):
                    md.append(f"  - Debe mostrar: {sl['intent']}")
                if sl.get("notes"):
                    md.append(f"  - Notas de Hugo: {sl['notes']}")
                if sl.get("links"):
                    md.append(f"  - Enlaza: {', '.join(sl['links'])}")
            md.append("")
    else:
        md += ["_Sin guion aprobado todavía._", ""]
        if s.get("initial_storyline"):
            md += ["Storyline provisional anterior:", plain(s.get("initial_storyline"))]
    md += ["## 4. Hipótesis", items(s["hypotheses"]), "## 5. Plan de investigación"]
    plan = fr.get("research_plan") or []
    if plan:
        md += [f"- **{t['id']}** [{KINDS.get(t['kind'], {}).get('label', t['kind'])} · {KINDS.get(t['kind'], {}).get('agent', '')}"
               f"{' · ' + t['intensity'] if t.get('intensity') and t['intensity'] != 'analytics' else ''}] {t['question']}"
               + (f" → **{t['research_id']}**" if t.get("research_id") else "")
               + (f"\n  - Por qué: {t['why']}" if t.get("why") else "")
               + (f"\n  - Sirve a: {', '.join(t.get('links', []) + t.get('slides', []))}" if t.get("links") or t.get("slides") else "")
               for t in plan]
        md.append("")
    else:
        md += ["_Sin tareas aprobadas todavía._", ""]
    md += ["## 6. Lo que no afirmamos todavía", plain(s.get("should_not_claim")), "## 7. Decisiones necesarias",
           plain(s.get("decisions_needed")), "## 8. Riesgos", plain(s.get("risks")), "---", "## Anexo · lo capturado en la conversación",
           "### Lo que Hugo piensa"]
    md += [f"- “{d['hugo_wording']}” ({d['id']}){'' if d.get('verbatim', True) else ' _(paráfrasis)_'}" for d in s["dual"][:12]] or ["_—_"]
    led = s.get("ledger", {})
    md += ["", "### Hechos", items(led.get("FACT", [])), "### Observaciones", items(led.get("OBSERVATION", [])),
           "### Intuiciones de Hugo", items(led.get("USER_INTUITION", [])), "### Supuestos", items(led.get("ASSUMPTION", [])),
           "### Preguntas abiertas", items(s["open_questions"]), "### Desconocidos", items(led.get("UNKNOWN", [])),
           "### Propuestas", items(led.get("PROPOSAL", [])), "### Frames candidatos"]
    frames = s.get("candidate_frames") or []
    md += [(f"- **{f.get('name')}**{' ✓ elegido' if f.get('chosen') else ''} — {f.get('description', '')}") for f in frames] or ["_—_"]
    md += ["", "### Notas de lenguaje", plain(s.get("language_notes"))]
    text = "\n".join(md)
    store.write_text("framing/current.md", text)
    return text


def ledger_counts(store: CaseStore) -> dict:
    s = state(store)
    out = {KIND_LABELS.get(k, k): len(v) for k, v in s["ledger"].items()}
    out["Hipótesis"] = len(s["hypotheses"])
    out["Preguntas"] = len(s["open_questions"])
    return out


def clip_row(r: dict, n: int = 120) -> str:
    return clip(r.get("text", ""), n)
