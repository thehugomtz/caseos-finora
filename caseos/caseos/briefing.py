"""Briefing: the structured brief (brief/brief.yaml) and its readable rendering (brief/brief.md)."""
from __future__ import annotations

from .store import CaseStore

FIELDS = ["title", "objective", "audience", "context", "brief_text", "deliverables", "constraints", "gaps", "sources",
          "success_criteria", "timeline", "stakeholders", "data_available"]


def get(store: CaseStore) -> dict:
    return store.read_data("brief/brief.yaml", {}) or {}


def update(store: CaseStore, patch: dict, *, actor: str) -> dict:
    b = get(store)
    for k, v in patch.items():
        if k in FIELDS:
            b[k] = v
    store.write_data("brief/brief.yaml", b)
    render_md(store)
    from . import phases
    phases.touch(store, "briefing", actor=actor)
    meta = store.meta()
    if meta["phases"]["briefing"].get("status") == "ready":
        phases.set_status(store, "briefing", "needs_review", actor=actor, note="brief editado después de aprobarse")
    store.log(actor, "updated", ["brief"], "Brief actualizado", material=True)
    return b


def render_md(store: CaseStore) -> str:
    b = get(store)

    def lst(k):
        v = b.get(k) or []
        if isinstance(v, str):
            return v + "\n"
        return "\n".join(f"- {x if isinstance(x, str) else x.get('text') or x.get('title') or x}" for x in v) + "\n" if v else "_—_\n"

    aud = b.get("audience") or []
    md = [f"# Brief — {b.get('title', store.id)}", "",
          "## Objetivo", b.get("objective") or "_—_", "",
          "## Audiencia", (", ".join(aud) if isinstance(aud, list) else str(aud)) or "_—_", "",
          "## Contexto", b.get("context") or "_—_", "",
          "## Entregables", lst("deliverables"),
          "## Restricciones", lst("constraints"),
          "## Datos disponibles", lst("data_available"),
          "## Criterios de éxito", lst("success_criteria"),
          "## Vacíos de información declarados", lst("gaps"),
          "## Fuentes", lst("sources")]
    if b.get("brief_text"):
        md += ["## Texto del brief", b["brief_text"], ""]
    text = "\n".join(md)
    store.write_text("brief/brief.md", text)
    return text
