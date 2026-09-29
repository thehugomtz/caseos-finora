"""Language discipline: technical vocabulary must clarify, not perform intelligence.

A deterministic check used as a runtime guard on Framer replies (it annotates, never blocks) and in tests/evals:
- performative jargon that the user never used and the reply does not explain,
- English-heavy replies when the case language is Spanish (Hugo's own English business terms are allowed).
"""
from __future__ import annotations

import re

from .util import norm

# Terms that are fine when they clarify (and are explained or are Hugo's own) but become performance otherwise.
TECH = ["arr", "mrr", "nrr", "grr", "cac", "ltv", "payback", "cohort", "cohorte", "funnel velocity", "throughput", "elasticity",
        "elasticidad", "decompose", "descomponer", "degradation", "degradación", "top-of-funnel", "top of funnel", "downstream",
        "upstream", "attribution", "atribución", "incrementality", "incrementalidad", "north star", "quick ratio", "unit economics",
        "revenue bridge", "mix effect", "efecto mezcla", "shapley", "counterfactual", "contrafactual", "endogeneity", "endogeneidad",
        "heterogeneity", "heterogeneidad", "stationarity", "confounder", "leverage", "synergy", "sinergia", "holistic", "holístico"]
PERFORMATIVE = ["throughput elasticity", "conversion degradation", "downstream conversion", "decompose top-of-funnel", "leverage synergies",
                "holistic", "paradigm", "best-in-class", "world-class", "synergy", "sinergia"]
EN_STOP = {"the", "and", "of", "to", "we", "need", "is", "are", "with", "that", "this", "for", "on", "in", "it", "be", "as", "by"}
EXPLAIN = re.compile(r"\((?:[^)]{3,})\)|\b(o sea|es decir|que significa|que quiere decir|dicho simple|en simple)\b", re.I)


def assess(reply: str, profile: dict | None = None, user_text: str = "") -> dict:
    prof = profile or {}
    obs = prof.get("observed") or {}
    own = {norm(t) for t in (obs.get("preserved_terms") or [])} | set(re.findall(r"[a-záéíóúñ\-]+", norm(user_text)))
    text = norm(reply)
    words = re.findall(r"[a-záéíóúñ\-]+", text)
    found = [t for t in TECH if re.search(rf"\b{re.escape(norm(t))}\b", text)]
    unexplained = []
    for t in found:
        if norm(t) in own:
            continue
        i = text.find(norm(t))
        window = reply[max(0, i - 10): i + len(t) + 90] if i >= 0 else ""
        if not EXPLAIN.search(window):
            unexplained.append(t)
    performative = [p for p in PERFORMATIVE if norm(p) in text]
    en = sum(1 for w in words if w in EN_STOP)
    en_ratio = en / max(1, len(words))
    spanish = (prof.get("primary") or "es").startswith("es")
    issues = []
    if performative:
        issues.append("jerga performativa: " + ", ".join(performative))
    if len(unexplained) > 2:
        issues.append("términos técnicos sin explicar: " + ", ".join(unexplained[:5]))
    if spanish and en_ratio > 0.08:
        issues.append(f"respuesta demasiado en inglés ({en_ratio:.0%} de palabras funcionales en inglés)")
    return {"ok": not issues, "issues": issues, "technical_terms": found, "unexplained": unexplained,
            "performative": performative, "english_ratio": round(en_ratio, 3), "words": len(words)}
