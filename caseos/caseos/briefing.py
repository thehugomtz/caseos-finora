"""Briefing: the case contract, built section by section and approved by Hugo as it goes.

brief/brief.yaml keeps the APPROVED value of each section at the top level (what every agent reads), plus
  sections: {key: {state, by, at, basis, hugo_wording, version}}   state: approved · imported
  pending:  {key: {value, hugo_wording, basis, why, turn_id, by, at}}  proposals waiting for Hugo, never applied silently
The Briefer (agents/briefer.py) only proposes; Hugo approves, edits or discards each section. Mark Briefing Ready needs
objective, audience and deliverables approved (phases.readiness).
"""
from __future__ import annotations

from .store import CaseStore
from .util import clip, norm, now_iso

SECTIONS = [
    {"key": "title", "label": "Nombre del caso", "kind": "text", "hint": "Cómo le llamamos al caso."},
    {"key": "objective", "label": "Objetivo", "kind": "text", "required": True,
     "hint": "Qué entendimiento o decisión tiene que salir de aquí."},
    {"key": "audience", "label": "Audiencia", "kind": "list", "required": True,
     "hint": "Quién escucha y qué decide cada quien (uno por línea)."},
    {"key": "context", "label": "Contexto", "kind": "text", "hint": "La situación, en pocas líneas."},
    {"key": "deliverables", "label": "Entregables", "kind": "list", "required": True, "hint": "Qué hay que entregar (uno por línea)."},
    {"key": "constraints", "label": "Restricciones", "kind": "list", "hint": "Límites que los agentes deben respetar."},
    {"key": "success_criteria", "label": "Criterios de éxito", "kind": "list", "hint": "Cómo sabremos que quedó bien."},
    {"key": "data_available", "label": "Datos disponibles", "kind": "list",
     "hint": "Qué información hay. Si eliges un modelo de datos, se llena solo."},
    {"key": "stakeholders", "label": "Stakeholders y fuentes de contexto", "kind": "list", "hint": "Quién puede aportar contexto."},
    {"key": "timeline", "label": "Tiempos", "kind": "text", "hint": "Plazos o ritmo, si importan."},
    {"key": "gaps", "label": "Vacíos de información", "kind": "list",
     "hint": "Lo que no sabemos. Los agentes no los rellenan con supuestos."},
    {"key": "brief_text", "label": "Enunciado original", "kind": "text", "verbatim": True,
     "hint": "El texto del reto o del cliente, tal cual."},
]
BY_KEY = {s["key"]: s for s in SECTIONS}
REQUIRED = [s["key"] for s in SECTIONS if s.get("required")]
LEGACY_FIELDS = ["client", "company", "audience_note", "sources", "provenance", "created_at"]


def get(store: CaseStore) -> dict:
    return store.read_data("brief/brief.yaml", {}) or {}


def _empty(v) -> bool:
    return v in (None, "", []) or (isinstance(v, list) and not any(str(x).strip() for x in v))


def _clean(key: str, value):
    """Normalize a section value to its kind: text → str, list → list[str] without blanks."""
    kind = BY_KEY[key]["kind"]
    if kind == "list":
        if isinstance(value, str):
            value = value.split("\n")
        out = []
        for x in value or []:
            x = (x if isinstance(x, str) else (x.get("text") or x.get("title") or str(x)) if isinstance(x, dict) else str(x)).strip()
            if x and x not in out:
                out.append(x)
        return out
    if isinstance(value, list):
        value = "\n\n".join(str(x).strip() for x in value if str(x).strip())
    return (value or "").strip()


def _same(a, b) -> bool:
    if isinstance(a, list) or isinstance(b, list):
        return [norm(str(x)) for x in (a or [])] == [norm(str(x)) for x in (b or [])]
    return norm(str(a or "")) == norm(str(b or ""))


def _save(store: CaseStore, b: dict, *, actor: str, summary: str, targets: list | None = None, material: bool = True) -> None:
    b["updated_at"] = now_iso()
    store.write_data("brief/brief.yaml", b)
    render_md(store)
    from . import phases
    phases.touch(store, "briefing", actor=actor)
    if material and actor == "hugo" and store.meta()["phases"]["briefing"].get("status") == "ready":
        phases.set_status(store, "briefing", "needs_review", actor=actor, note="el brief cambió después de aprobarse")
    store.log(actor, "updated", targets or ["brief"], summary, material=material)


# ------------------------------------------------------------------------------------------ state view
def view(store: CaseStore) -> dict:
    b = get(store)
    secs, pend = b.get("sections") or {}, b.get("pending") or {}
    rows = []
    for s in SECTIONS:
        k = s["key"]
        val = b.get(k)
        meta = secs.get(k) or {}
        state = meta.get("state") or ("imported" if not _empty(val) else "empty")
        rows.append({**s, "value": val if not _empty(val) else ([] if s["kind"] == "list" else ""), "state": state,
                     "meta": meta, "pending": pend.get(k)})
    approved = [r for r in rows if r["state"] in ("approved", "imported")]
    return {"sections": rows, "pending": len(pend),
            "progress": {"approved": len(approved), "total": len(SECTIONS),
                         "required_ok": all(not _empty(b.get(k)) for k in REQUIRED),
                         "required_missing": [BY_KEY[k]["label"] for k in REQUIRED if _empty(b.get(k))]},
            "extra": {k: b.get(k) for k in LEGACY_FIELDS if b.get(k)}}


# ------------------------------------------------------------------------------------------ Hugo's actions
def set_section(store: CaseStore, key: str, value, *, actor: str = "hugo", basis: str = "hugo", hugo_wording: str = "") -> dict:
    """Hugo writes (or confirms) a section directly: it is approved as his."""
    if key not in BY_KEY:
        raise ValueError(f"Sección desconocida: {key}")
    b = get(store)
    val = _clean(key, value)
    secs = b.setdefault("sections", {})
    prev = secs.get(key) or {}
    b[key] = val
    secs[key] = {"state": "approved", "by": actor, "at": now_iso(), "basis": basis, "hugo_wording": hugo_wording or prev.get("hugo_wording", ""),
                 "version": int(prev.get("version") or 0) + 1}
    (b.get("pending") or {}).pop(key, None)
    _save(store, b, actor=actor, summary=f"Brief · {BY_KEY[key]['label']} aprobado" + (f" ({basis})" if basis != "hugo" else ""))
    return view(store)


def propose(store: CaseStore, key: str, value, *, hugo_wording: str = "", basis: str = "hugo", why: str = "",
            turn_id: str = "", actor: str = "briefer") -> bool:
    """An agent's proposal for a section: stored as pending, never applied. False when there is nothing new."""
    if key not in BY_KEY:
        return False
    val = _clean(key, value)
    if _empty(val):
        return False
    b = get(store)
    if _same(val, b.get(key)):
        (b.get("pending") or {}).pop(key, None)
        store.write_data("brief/brief.yaml", b)
        return False
    b.setdefault("pending", {})[key] = {"value": val, "hugo_wording": (hugo_wording or "").strip(), "basis": basis, "why": why,
                                        "turn_id": turn_id, "by": actor, "at": now_iso(), "revises": not _empty(b.get(key))}
    store.write_data("brief/brief.yaml", b)
    return True


def approve(store: CaseStore, key: str, *, actor: str = "hugo") -> dict:
    if actor != "hugo":
        raise ValueError("Solo Hugo aprueba secciones del brief.")
    b = get(store)
    p = (b.get("pending") or {}).get(key)
    if not p:
        raise ValueError(f"No hay propuesta pendiente para {BY_KEY.get(key, {}).get('label', key)}.")
    return set_section(store, key, p["value"], actor=actor, basis=p.get("basis") or "hugo", hugo_wording=p.get("hugo_wording", ""))


def approve_all(store: CaseStore, *, actor: str = "hugo") -> dict:
    if actor != "hugo":
        raise ValueError("Solo Hugo aprueba secciones del brief.")
    for key in list((get(store).get("pending") or {}).keys()):
        approve(store, key, actor=actor)
    return view(store)


def discard(store: CaseStore, key: str, *, actor: str = "hugo") -> dict:
    b = get(store)
    p = (b.get("pending") or {}).pop(key, None)
    if not p:
        raise ValueError("No hay propuesta pendiente.")
    store.write_data("brief/brief.yaml", b)
    store.log(actor, "discarded", ["brief"], f"Brief · Hugo descartó la propuesta para {BY_KEY[key]['label']}: "
              f"{clip(str(p.get('value')), 120)}", material=False)
    return view(store)


def update(store: CaseStore, patch: dict, *, actor: str) -> dict:
    """Legacy patch (several fields at once): each known section is set as approved by `actor`."""
    for k, v in patch.items():
        if k in BY_KEY:
            set_section(store, k, v, actor=actor)
    return get(store)


# ------------------------------------------------------------------------------------------ document
def render_md(store: CaseStore) -> str:
    """brief.md holds the APPROVED brief only: it is what Mark Ready snapshots and every agent reads."""
    b = get(store)
    md = [f"# Brief — {b.get('title') or store.id}", ""]
    for s in SECTIONS:
        if s["key"] == "title":
            continue
        v = b.get(s["key"])
        md.append(f"## {s['label']}")
        if _empty(v):
            md.append("_—_")
        elif isinstance(v, list):
            md += [f"- {x if isinstance(x, str) else x.get('text') or x.get('title') or x}" for x in v]
        else:
            md.append(str(v))
        md.append("")
    srcs = b.get("sources") or []
    if srcs:
        md += ["## Fuentes"] + [f"- {s.get('title') if isinstance(s, dict) else s}" for s in srcs] + [""]
    pend = b.get("pending") or {}
    if pend:
        md += ["---", f"_{len(pend)} propuesta(s) del agente esperando revisión: "
               + ", ".join(BY_KEY[k]["label"] for k in pend if k in BY_KEY) + "._", ""]
    text = "\n".join(md)
    store.write_text("brief/brief.md", text)
    return text
