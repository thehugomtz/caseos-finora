"""Decision log. Every material decision is an entity (D-xxx) with options, the agent's recommendation, Hugo's choice
and rationale, affected items and downstream impact.

Two layers (adapted from alirezarezvani/claude-skills decision-logger, MIT): agents may only *propose* decisions
(status: proposed); only Hugo makes them active. Rejected options are remembered (`do_not_resurface`) so agents do
not re-propose what Hugo already turned down. Decisions are never deleted: they are superseded or reverted.
"""
from __future__ import annotations

from .store import CaseStore, StoreError
from .util import now_iso

HUMAN = "hugo"


def record_decision(store: CaseStore, *, title: str, context: str, options: dict | None, agent_recommendation: str,
                    user_choice: str, user_rationale: str, affected_items: list[str], downstream_impact: str,
                    kind: str = "other", phase: str | None = None, actor: str = HUMAN, supersedes: str | None = None,
                    do_not_resurface: list[str] | None = None, run_id: str | None = None,
                    origin: dict | None = None) -> dict:
    status = "active" if actor == HUMAN else "proposed"
    ents = store.all()
    affected = [i for i in affected_items or [] if i in ents or i in ("briefing", "framing", "research", "synthesis",
                                                                        "story", "slides")]
    data = {"title": title, "date": now_iso()[:10], "context": context, "options": options or {},
            "agent_recommendation": agent_recommendation, "user_choice": user_choice if actor == HUMAN else "",
            "user_rationale": user_rationale if actor == HUMAN else "", "affected_items": affected,
            "downstream_impact": downstream_impact, "status": status, "kind": kind,
            "links": [i for i in affected if i in ents]}
    if phase:
        data["decided_in_phase"] = phase
    if supersedes:
        data["supersedes"] = supersedes
    if do_not_resurface:
        data["do_not_resurface"] = do_not_resurface
    if actor == HUMAN:
        data["review"] = {"state": "accepted", "by": HUMAN, "at": now_iso()}
    d = store.create("decision", data, actor=actor, origin=origin,
                     summary=(f"Hugo decidió: {title}" if actor == HUMAN else f"{actor} propone decisión: {title}"),
                     run_id=run_id)
    if supersedes:
        prev = store.get(supersedes)
        if prev and prev.get("status") == "active":
            store.update(supersedes, {"status": "superseded", "superseded_by": d["id"]}, actor=actor,
                         summary=f"{supersedes} reemplazada por {d['id']}", verb="superseded")
    return d


def confirm(store: CaseStore, did: str, *, choice: str, rationale: str = "", actor: str = HUMAN) -> dict:
    if actor != HUMAN:
        raise StoreError("Solo Hugo confirma decisiones.")
    d = store.require(did)
    opts = d.get("options") or {}
    rejected = [k for k in opts if k != choice]
    patch = {"status": "active", "user_choice": choice, "user_rationale": rationale,
             "review": {"state": "accepted", "by": HUMAN, "at": now_iso()}}
    if rejected:
        patch["do_not_resurface"] = sorted(set((d.get("do_not_resurface") or []) + [f"{k}: {opts[k]}" if isinstance(opts[k], str) else k for k in rejected]))
    return store.update(did, patch, actor=actor, summary=f"Hugo confirmó {did}: {choice}", verb="decided")


def revert(store: CaseStore, did: str, *, rationale: str, actor: str = HUMAN) -> dict:
    if actor != HUMAN:
        raise StoreError("Solo Hugo revierte decisiones.")
    return store.update(did, {"status": "reverted", "reverted_reason": rationale}, actor=actor,
                        summary=f"Hugo revirtió {did}: {rationale}", verb="reverted")


def active(store: CaseStore) -> list[dict]:
    return [d for d in store.list("decision") if d.get("status") == "active"]


def do_not_resurface(store: CaseStore) -> list[str]:
    out: list[str] = []
    for d in store.list("decision"):
        out += d.get("do_not_resurface") or []
    return out
