---
name: research-routing
description: CaseOS skill for the Research Router. Classifies every research request by intensity (Level 1 lookup, Level 2 business research, Level 3 deep research) and by specialist (analytics, business research, measurement strategy, data engineering/modeling), selects the minimum set of specialist skills, and checks that the request maps to at least one executive question, hypothesis, decision or story claim — otherwise it is flagged RESEARCH WITHOUT CASE PURPOSE for Hugo or the COS to decide.
license: MIT (CaseOS)
---

# Research Routing

Root rule: **do not research topics; research uncertainties that matter to the case.**

## 1. Purpose check (first)
Map the request to ≥1 of: executive question (Q), hypothesis (H), decision (D), story claim (C). If nothing maps,
return `purpose_ok: false` with the note "RESEARCH WITHOUT CASE PURPOSE" and what it would need to connect. Do not
refuse — Hugo or the COS decides whether it is worth it.

## 2. Intensity
- **L1 · Lookup** — small factual or definitional question ("¿Qué significa NRR?"). Minimal authoritative sources
  (official docs, standard definitions). Minutes.
- **L2 · Business research** — frameworks, benchmarks, practices, business design, alternatives ("¿Qué approaches
  existen para funnels híbridos?"). Several good sources, compared and synthesized.
- **L3 · Deep research** — material to a decision ("¿Qué measurement architecture hace más sentido bajo tres
  acquisition motions?"). deep-business-research: depth + breadth + counter + peer review.
Escalate one level when the answer would change a decision or a story claim; de-escalate when a definition or a
single comparison is enough.

## 3. Specialist
- **analytics** — answerable with the case's own data (trends, segments, cohorts, bridges, distributions). Goes to
  the Analytics Agent over the case's exploration workspace.
- **business** — external knowledge: market, competitors, pricing, benchmarks, practices, definitions.
- **measurement** — how to measure: KPI trees, funnels and non-linear journeys, lifecycle, cohorts, attribution,
  instrumentation, experimentation, analytics operating model.
- **data_engineering** — how the data should be modeled: source of truth, grain, facts/dimensions, events, temporal
  validity, identity, subscription/billing/pricing/discount modeling, MRR/ARR classification logic, data contracts.

## 4. Minimum skills
Load only what the question needs. Examples:
- "¿Cómo deberían afectar los descuentos temporales la clasificación de MRR?" → business L2 with
  commercial-skills + pricing-strategist + saas-metrics-coach; technical side to data_engineering.
- "¿Qué es NRR?" → business L1 with saas-metrics-coach only.
- "¿Qué competidores atacan el mismo segmento?" → business L2 with competitive-intel.
Never load every advisor. Never more than three specialist skills for one request.

## Output
intensity · specialty · skills · rationale (one line) · reformulated_question (answerable, scoped) ·
evidence_needed (what would answer it) · purpose (mapped IDs, ok, note).
