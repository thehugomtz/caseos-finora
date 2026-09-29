"""⌘K search across the case: findings, questions, decisions, research, tables, slides, claims — by ID, alias or text."""
from __future__ import annotations

import re

from .model import TYPES, title_of
from .store import CaseStore
from .util import clip, norm

FIELDS = ("text", "statement", "headline", "title", "research_question", "short_answer", "structured", "hugo_wording",
          "question", "message", "table_key", "alias", "answer")


def search(store: CaseStore, q: str, limit: int = 24) -> list[dict]:
    qn = norm(q)
    if not qn:
        return []
    toks = [t for t in re.findall(r"[\wáéíóúñ\-·]+", qn) if len(t) > 1]
    out = []
    for e in store.all().values():
        eid = e["id"]
        score = 0
        if norm(eid) == qn or norm(str(e.get("alias", ""))) == qn or norm(str(e.get("table_key", ""))) == qn:
            score = 1000
        else:
            hay = norm(" ".join(str(e.get(f, "")) for f in FIELDS) + " " + eid)
            if qn in hay:
                score += 200 + (50 if norm(title_of(e)).startswith(qn) else 0)
            hits = sum(1 for t in toks if t in hay)
            if toks and hits:
                score += 40 * hits / len(toks) * 2
            if hits < max(1, len(toks) // 2) and qn not in hay:
                score = 0
        if score:
            if (e.get("review") or {}).get("state") == "rejected":
                score *= 0.3
            out.append({"id": eid, "type": e.get("type"), "label": TYPES.get(e.get("type"), {}).get("label", ""),
                        "alias": e.get("alias") or e.get("table_key"), "title": clip(title_of(e), 140),
                        "status": e.get("status"), "review": (e.get("review") or {}).get("state"), "score": round(score, 1)})
    return sorted(out, key=lambda x: -x["score"])[:limit]
