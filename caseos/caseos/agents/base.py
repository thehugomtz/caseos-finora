"""Agent registry, contracts and prompt composition.

The agent's system prompt = CaseOS kernel (principle, epistemic rules, language profile, ID discipline)
+ the "System behavior" section of agents/<id>.md (the same document shown in the repo and in Under the hood)
+ the skills selected for this request (skills.select / skills.compose).
"""
from __future__ import annotations

import functools
import re

from .. import config, skills
from ..util import read_yaml

AGENTS: dict[str, dict] = {
    "framer": {"doc": "framer.md", "name": "Framer", "group": "framing", "icon": "compass",
               "short": "Problem Framing & Initial Storytelling"},
    "cos": {"doc": "cos.md", "name": "Chief of Staff", "group": "synthesis", "icon": "orbit",
            "short": "Case state, impact, decisions, Story Package"},
    "router": {"doc": "research-router.md", "name": "Research Router", "group": "research", "icon": "route",
               "short": "Intensidad, especialista y skills mínimas"},
    "analytics": {"doc": "analytics.md", "name": "Analytics", "group": "research", "icon": "chart",
                  "short": "Business Exploration Workspace"},
    "business_research": {"doc": "business-research.md", "name": "Business Research", "group": "research",
                           "icon": "globe", "short": "Conocimiento externo con fuentes"},
    "measurement": {"doc": "measurement.md", "name": "Measurement", "group": "research", "icon": "ruler",
                    "short": "KPI trees, journeys, cohortes, instrumentación"},
    "data_engineering": {"doc": "data-engineering.md", "name": "Data Engineering", "group": "research",
                         "icon": "db", "short": "Fuente de verdad, grano, modelos"},
    "visual_storyteller": {"doc": "visual-storyteller.md", "name": "Visual Storyteller", "group": "slides",
                           "icon": "slides", "short": "Executive Visual Storyteller existente"},
}

SECTIONS = ["Role", "Purpose", "System behavior", "Inputs", "Outputs", "Skills", "Tools", "Allowed decisions",
            "User approval required", "Guardrails", "Handoff contract", "Failure modes", "Examples"]


@functools.lru_cache(maxsize=None)
def contract(agent_id: str) -> dict:
    spec = AGENTS[agent_id]
    text = (config.AGENTS_DIR / spec["doc"]).read_text(encoding="utf-8")
    front = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        front = read_yaml_str(text[3:end])
        text = text[end + 4:]
    parts = re.split(r"^## +", text, flags=re.M)
    sections = {}
    for p in parts[1:]:
        head, _, body = p.partition("\n")
        sections[head.strip()] = body.strip()
    return {"id": agent_id, **spec, "front": front, "sections": sections, "doc_path": f"agents/{spec['doc']}"}


def read_yaml_str(s: str) -> dict:
    from ..util import yaml_load
    return yaml_load(s) or {}


def kernel(language: dict | None = None) -> str:
    lang = language or {}
    obs = lang.get("observed") or {}
    terms = ", ".join((obs.get("preserved_terms") or [])[:20])
    return f"""# CaseOS kernel
You work inside CaseOS, a human-gated multi-agent case room. Principle: **Agents do the work. Hugo owns the judgment.**
Agents organize, research, analyze, propose, question, find evidence, detect contradictions, suggest next steps,
synthesize and produce artifacts. Hugo approves the framing, decides between alternatives, decides when research is
enough and when a phase is ready, accepts or rejects findings, approves storyline changes and the Story Package, and
controls the advance between phases. You never do those things yourself: you propose them.

Epistemic rules: facts ≠ hypotheses · observed ≠ causal · benchmark ≠ recommendation · user intuition ≠ evidence ·
absence of evidence ≠ evidence of absence. Never invent numbers, sources, citations or case facts; name gaps instead
of filling them with "common knowledge".

Language profile of this case: primary language `{lang.get('primary', 'es')}`; tone: {lang.get('tone', 'direct, conversational')};
technical level: {lang.get('technical_level', 'adaptive')}; preserve Hugo's vocabulary: {lang.get('preserve_user_vocabulary', True)};
avoid unnecessary jargon: {lang.get('avoid_unnecessary_jargon', True)}. Write everything addressed to Hugo in that language.
{('Observed register: ' + str(obs.get('register')) + '. ') if obs.get('register') else ''}{('Terms Hugo uses (keep them): ' + terms + '.') if terms else ''}
Technical vocabulary must clarify, not perform intelligence.

IDs: refer to case elements by their IDs (Q-001 question, H-003 hypothesis, N-004 idea, R-014 research, F-008 finding,
T-004 table, D-017 decision, X-002 alert, C-006 story claim, S-008 slide). Only use IDs that exist in the state you are
given. Return exactly the structured output requested.
"""


def system_prompt(agent_id: str, selected: list[dict], language: dict | None = None, extra: str = "") -> str:
    c = contract(agent_id)
    behavior = c["sections"].get("System behavior", "")
    parts = [kernel(language), f"# Agent: {c['name']} — {c['front'].get('title', c['short'])}", behavior]
    if extra:
        parts.append(extra)
    if selected:
        parts.append("# Skills loaded for this request\nApply them as working methods. Where a skill conflicts with the "
                     "CaseOS kernel or the agent behavior above, CaseOS wins.\n\n" + skills.compose(selected))
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def card(agent_id: str) -> dict:
    """Everything the UI needs to explain an agent (topology drawer, Under the hood)."""
    c = contract(agent_id)
    return {"id": agent_id, "name": c["name"], "short": c["short"], "title": c["front"].get("title"),
            "group": c["group"], "icon": c["icon"], "doc_path": c["doc_path"], "tools": c["front"].get("tools") or [],
            "sections": {k: c["sections"].get(k, "") for k in SECTIONS}, "skills": skills.for_agent(
                {"analytics": "analytics"}.get(agent_id, agent_id)),
            "model": config.model_for(c["front"].get("role_effort") or agent_id),
            "effort": config.EFFORT.get(c["front"].get("role_effort") or agent_id)}
