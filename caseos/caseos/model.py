"""The case model: entity types, their ID prefixes, folders, owning phase and allowed statuses.

Every relevant element of a case is an entity with an ID and lineage (`links`). Entities are YAML files on disk
(one file per entity) so the repository itself shows the case: questions/, hypotheses/, research/, evidence/, ...
"""
from __future__ import annotations

PHASES = ["briefing", "framing", "research", "synthesis", "story", "slides"]
PHASE_LABELS = {"briefing": "Briefing", "framing": "Framing", "research": "Research", "synthesis": "Synthesis",
                "story": "Story", "slides": "Slides"}
PHASE_STATUSES = ["not_started", "in_progress", "review", "ready", "reopened", "needs_review"]

TYPES: dict[str, dict] = {
    "question":   {"prefix": "Q", "dir": "questions", "phase": "framing",
                   "statuses": ["open", "answered", "parked"], "label": "Pregunta"},
    "hypothesis": {"prefix": "H", "dir": "hypotheses", "phase": "framing",
                   "statuses": ["open", "supported", "weakened", "contested", "rejected"], "label": "Hipótesis"},
    "note":       {"prefix": "N", "dir": "framing/items", "phase": "framing",
                   "statuses": ["active", "superseded"], "label": "Idea"},
    "research":   {"prefix": "R", "dir": "research", "phase": "research",
                   "statuses": ["queued", "running", "completed", "failed", "blocked", "cancelled"], "label": "Research"},
    "finding":    {"prefix": "F", "dir": "evidence/findings", "phase": "research",
                   "statuses": ["active", "superseded"], "label": "Finding"},
    "table":      {"prefix": "T", "dir": "evidence/tables", "phase": "research",
                   "statuses": ["valid", "invalid"], "label": "Tabla"},
    "decision":   {"prefix": "D", "dir": "decisions", "phase": "synthesis",
                   "statuses": ["proposed", "active", "superseded", "reverted"], "label": "Decisión"},
    "alert":      {"prefix": "X", "dir": "cos/alerts", "phase": "synthesis",
                   "statuses": ["open", "resolved", "dismissed"], "label": "Alerta"},
    "claim":      {"prefix": "C", "dir": "story/claims", "phase": "story",
                   "statuses": ["draft", "supported", "weak", "unsupported"], "label": "Claim"},
    "slide":      {"prefix": "S", "dir": "slides/specs", "phase": "slides",
                   "statuses": ["draft", "rendered", "passed", "escalated"], "label": "Slide"},
    "artifact":   {"prefix": "A", "dir": "artifacts", "phase": None,
                   "statuses": ["draft", "approved", "superseded"], "label": "Artefacto"},
}
PREFIX_TO_TYPE = {v["prefix"]: k for k, v in TYPES.items()}

# Framing items (notes) and the epistemic kinds the Framer separates. Hypotheses, questions and decisions
# become their own entity types; the rest stay as notes with a kind.
EPISTEMIC_KINDS = ["FACT", "OBSERVATION", "USER_INTUITION", "ASSUMPTION", "HYPOTHESIS", "QUESTION", "PROPOSAL",
                   "DECISION", "UNKNOWN"]
KIND_LABELS = {"FACT": "Hecho", "OBSERVATION": "Observación", "USER_INTUITION": "Intuición de Hugo",
               "ASSUMPTION": "Supuesto", "HYPOTHESIS": "Hipótesis", "QUESTION": "Pregunta", "PROPOSAL": "Propuesta",
               "DECISION": "Decisión", "UNKNOWN": "Desconocido"}

REVIEW_STATES = ["proposed", "accepted", "rejected"]

# Lineage reading order (Question → Hypothesis → Research → Evidence → Decision → Story claim → Slide)
LINEAGE_ORDER = ["question", "note", "hypothesis", "research", "finding", "table", "alert", "decision", "claim",
                 "slide", "artifact"]


def type_of(eid: str) -> str | None:
    if not eid or "-" not in eid:
        return None
    return PREFIX_TO_TYPE.get(eid.split("-", 1)[0])


def phase_index(phase: str | None) -> int:
    return PHASES.index(phase) if phase in PHASES else -1


def title_of(e: dict) -> str:
    for k in ("title", "headline", "statement", "text", "short_answer", "research_question", "question"):
        v = e.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return e.get("id", "")
