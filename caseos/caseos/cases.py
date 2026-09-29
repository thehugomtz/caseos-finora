"""Case registry: every folder under cases/ with a case.yaml is a case. CaseOS is not tied to any case."""
from __future__ import annotations

import threading
from pathlib import Path

from . import brain, config
from .model import PHASES
from .store import CaseStore, StoreError
from .util import now_iso, slugify, write_yaml

_stores: dict[str, CaseStore] = {}
_lock = threading.Lock()

DEFAULT_LANGUAGE = {
    "primary": "es",
    "tone": "direct, conversational",
    "technical_level": "adaptive",
    "preserve_user_vocabulary": True,
    "avoid_unnecessary_jargon": True,
    "structured_language": "es",
    "observed": {"register": "", "technical_level": "", "formality": "", "preserved_terms": [], "notes": []},
}

CASE_FOLDERS = ["brief", "framing/items", "decisions", "hypotheses", "questions", "research", "evidence/findings",
                "evidence/tables", "evidence/artifacts", "cos/alerts", "story/claims", "slides/specs", "artifacts",
                "audit", "snapshots"]


def cases_dir() -> Path:
    config.CASES_DIR.mkdir(parents=True, exist_ok=True)
    return config.CASES_DIR


def list_cases() -> list[dict]:
    out = []
    for d in sorted(cases_dir().iterdir()):
        if (d / "case.yaml").exists():
            s = get(d.name)
            m = s.meta()
            out.append({"id": d.name, "name": m.get("name", d.name), "title": m.get("title", ""),
                        "client": m.get("client", ""), "updated_at": m.get("updated_at"),
                        "phases": {p: m["phases"][p].get("status") for p in PHASES}})
    return out


def get(case_id: str) -> CaseStore:
    with _lock:
        s = _stores.get(case_id)
        if s is None:
            root = cases_dir() / case_id
            if not (root / "case.yaml").exists():
                raise StoreError(f"El caso '{case_id}' no existe.")
            s = CaseStore(root)
            brain.install(s)
            _stores[case_id] = s
        return s


def forget(case_id: str) -> None:
    with _lock:
        _stores.pop(case_id, None)


def create_case(*, name: str, objective: str = "", audience: list[str] | None = None, brief_text: str = "", context: str = "",
                deliverables: list[str] | None = None, constraints: list[str] | None = None,
                language: dict | None = None, title: str = "", client: str = "", case_id: str | None = None,
                workspace: dict | None = None, actor: str = "hugo") -> CaseStore:
    cid = case_id or slugify(name)
    root = cases_dir() / cid
    if (root / "case.yaml").exists():
        raise StoreError(f"Ya existe un caso con id '{cid}'.")
    for f in CASE_FOLDERS:
        (root / f).mkdir(parents=True, exist_ok=True)
    lang = {**DEFAULT_LANGUAGE, **(language or {})}
    meta = {"id": cid, "name": name, "title": title or name, "client": client, "objective": objective,
            "audience": audience, "created_at": now_iso(), "created_by": actor, "language": lang,
            "workspace": workspace or {"type": "none"},
            "phases": {p: {"status": "not_started", "ready_count": 0, "history": []} for p in PHASES}}
    write_yaml(root / "case.yaml", meta)
    audience = audience or []
    brief = {"title": title or name, "objective": objective, "audience": audience, "context": context,
             "brief_text": brief_text, "deliverables": deliverables or [], "constraints": constraints or [],
             "gaps": [], "sources": [], "created_at": now_iso()}
    # whatever Hugo typed when creating the case is his: those sections start approved; the rest is built in Briefing
    brief["sections"] = {k: {"state": "approved", "by": actor, "at": now_iso(), "basis": "alta del caso", "version": 1}
                         for k in ("title", "objective", "audience", "context", "brief_text", "deliverables", "constraints")
                         if brief.get(k) not in (None, "", [])}
    brief["pending"] = {}
    write_yaml(root / "brief" / "brief.yaml", brief)
    write_yaml(root / "framing" / "current.yaml", empty_framing())
    (root / "README.md").write_text(case_readme(meta), encoding="utf-8")
    s = get(cid)
    from . import briefing, phases
    briefing.render_md(s)
    from .framing_doc import render_md as render_framing
    render_framing(s)
    phases.set_status(s, "briefing", "in_progress", actor=actor, note="caso creado", log=False)
    s.log(actor, "created", [cid], f"Caso creado: {name}", material=True)
    brain.update(s, "caso creado")
    return s


def empty_framing() -> dict:
    return {"version": 1, "executive_question": "", "executive_question_history": [], "hugo_thinking": [],
            "structured_interpretation": [], "candidate_frames": [], "initial_storyline": [], "research_needed": [],
            "decisions_needed": [], "should_not_claim": [], "language_notes": [], "risks": [], "mode": "organize",
            "updated_at": now_iso()}


def case_readme(meta: dict) -> str:
    return f"""# {meta.get('name')}

Caso de CaseOS. Todo el estado vive en estos archivos (YAML/Markdown), con ID y linaje:

| Carpeta | Qué contiene |
|---|---|
| `brain.md` | Memoria ejecutiva viva (se regenera ante cada cambio material) |
| `case.yaml` | Metadatos, fases, perfil de lenguaje, workspace analítico |
| `brief/` | Brief y sus versiones aprobadas |
| `framing/` | Framing vivo (`current.yaml` / `current.md`), conversación con el Framer, ideas (N-xxx) |
| `questions/` `hypotheses/` | Preguntas (Q-xxx) e hipótesis (H-xxx) |
| `research/` | Investigaciones (R-xxx) con fuentes, claims y síntesis para el caso |
| `evidence/` | Findings (F-xxx) y tablas canónicas (T-xxx) con linaje de datos |
| `decisions/` | Decision log (D-xxx) |
| `cos/` | Alertas del Chief of Staff (X-xxx) y su estado |
| `story/` | Claims (C-xxx), `current.md` y `package.yaml` (Story Package) |
| `slides/` | Handoff al Executive Visual Storyteller y decks generados |
| `audit/` | Traza de actividad, corridas de agentes, versiones previas de cada entidad |
| `snapshots/` | Copias del caso en cada Mark Ready |
"""
