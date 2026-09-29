"""Lineage: the graph behind every ID.

Question → Hypothesis → Research → Evidence (finding/table) → Decision → Story claim → Slide.
Links are stored as outgoing references on each entity; the graph is read undirected and ordered by type.
"""
from __future__ import annotations

from collections import defaultdict, deque

from .model import LINEAGE_ORDER, PHASES, phase_index, title_of, type_of


def graph(entities: dict[str, dict]) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = defaultdict(set)
    for eid, e in entities.items():
        for ref in e.get("links") or []:
            if ref in entities and ref != eid:
                adj[eid].add(ref)
                adj[ref].add(eid)
    return adj


def neighbours(entities: dict[str, dict], eid: str) -> list[str]:
    return sorted(graph(entities).get(eid, set()))


def lineage(entities: dict[str, dict], eid: str, depth: int = 3) -> dict:
    """Connected entities up to `depth` hops, grouped in lineage order, plus the direct edges."""
    adj = graph(entities)
    seen = {eid: 0}
    q = deque([eid])
    while q:
        cur = q.popleft()
        if seen[cur] >= depth:
            continue
        for n in adj.get(cur, ()):
            if n not in seen:
                seen[n] = seen[cur] + 1
                q.append(n)
    groups: dict[str, list[dict]] = {t: [] for t in LINEAGE_ORDER}
    for oid, dist in seen.items():
        if oid == eid:
            continue
        e = entities.get(oid) or {}
        t = e.get("type") or type_of(oid)
        groups.setdefault(t, []).append({"id": oid, "title": title_of(e), "distance": dist,
                                          "review": (e.get("review") or {}).get("state"),
                                          "status": e.get("status"), "stale": bool(e.get("stale"))})
    for t in groups:
        groups[t].sort(key=lambda x: (x["distance"], x["id"]))
    edges = [[a, b] for a in seen for b in adj.get(a, ()) if b in seen and a < b]
    return {"id": eid, "groups": {k: v for k, v in groups.items() if v}, "edges": edges}


def downstream(entities: dict[str, dict], seeds: set[str], after_phase: str) -> set[str]:
    """Entities in phases after `after_phase` reachable from `seeds` walking only forward in phase order."""
    adj = graph(entities)
    start = phase_index(after_phase)
    out: set[str] = set()
    q = deque(seeds)
    visited = set(seeds)
    while q:
        cur = q.popleft()
        for n in adj.get(cur, ()):
            if n in visited:
                continue
            visited.add(n)
            ph = phase_index((entities.get(n) or {}).get("phase"))
            if ph > start:
                out.add(n)
                q.append(n)
    return out


def phase_entities(entities: dict[str, dict], phase: str) -> set[str]:
    return {eid for eid, e in entities.items() if e.get("phase") == phase}


def impact_radius(entities: dict[str, dict], phase: str) -> dict:
    """What reopening `phase` may affect: downstream entities linked to it, counted by type."""
    seeds = phase_entities(entities, phase)
    affected = downstream(entities, seeds, phase)
    # accepted downstream work matters most; proposals are listed too
    by_type: dict[str, list[str]] = defaultdict(list)
    for eid in sorted(affected):
        by_type[(entities[eid].get("type") or type_of(eid))].append(eid)
    later = PHASES[phase_index(phase) + 1:]
    return {"phase": phase, "later_phases": later, "affected": sorted(affected),
            "by_type": dict(by_type), "counts": {k: len(v) for k, v in by_type.items()},
            "accepted": sorted(e for e in affected if (entities[e].get("review") or {}).get("state") == "accepted")}
