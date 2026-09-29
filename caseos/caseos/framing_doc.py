"""The current framing: structured state (framing/current.yaml + entities) and its document (framing/current.md).

The UI never shows this markdown raw; it is the portable artifact that gets approved, snapshotted and read by
other agents. The structure follows CaseOS §21: executive question, Hugo's thinking next to its structured
interpretation, the epistemic ledger, candidate frames, initial storyline, research and decisions needed, what we
should not claim yet and language notes.
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
    s = state(store)

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
        return "\n".join(f"- {x if isinstance(x, str) else (x.get('text') or x.get('name') or x)}" for x in xs) + "\n"

    led = s.get("ledger", {})
    md = ["# CURRENT FRAMING", f"> Versión {s.get('version', 1)} · actualizado {str(s.get('updated_at', ''))[:16]}", "",
          "## Executive Question", s.get("executive_question") or "_Sin definir todavía._", "",
          "## Hugo's Current Thinking"]
    md += [f"- “{d['hugo_wording']}” ({d['id']}){'' if d.get('verbatim', True) else ' _(paráfrasis)_'}" for d in s["dual"][:12]] or ["_—_"]
    md += ["", "## Structured Interpretation"]
    md += [f"- **{d['id']}** {d['structured']}" for d in s["dual"][:12]] or ["_—_"]
    md += ["", "## Facts", items(led.get("FACT", [])), "## Observations", items(led.get("OBSERVATION", [])),
           "## Hugo's Intuitions", items(led.get("USER_INTUITION", [])),
           "## Assumptions", items(led.get("ASSUMPTION", [])), "## Hypotheses", items(s["hypotheses"]),
           "## Open Questions", items(s["open_questions"]), "## Unknowns", items(led.get("UNKNOWN", [])),
           "## Proposals", items(led.get("PROPOSAL", [])), "## Candidate Frames"]
    frames = s.get("candidate_frames") or []
    md += [(f"- **{f.get('name')}**{' ✓ elegido' if f.get('chosen') else ''} — {f.get('description', '')}"
            + (f"\n  - _Cuándo gana:_ {f['when_it_wins']}" if f.get("when_it_wins") else "")) for f in frames] or ["_—_"]
    md += ["", "## Initial Storyline", plain(s.get("initial_storyline")), "## Research Needed", plain(s.get("research_needed")),
           "## Decisions Needed", plain(s.get("decisions_needed")), "## Things We Should Not Claim Yet",
           plain(s.get("should_not_claim")), "## Language Notes", plain(s.get("language_notes"))]
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
