---
name: story-package
description: CaseOS skill the Chief of Staff uses to turn a mature case into a Story Package the existing Executive Visual Storyteller can consume — audience, objective, governing thought, executive questions, story arc, sections, and claims that each carry their question, action headline, answer, role in the story, evidence/table/research IDs, confidence, limitations and visual intent — plus recommendations, appendix candidates, unresolved questions, language profile and visual references. Numbers travel as structured tables, never only in prose.
license: MIT (CaseOS)
---

# Story Package

The package is a contract, not a deck. It says what the audience must understand, in what order and why they
should believe it; the Visual Storyteller decides how it looks.

## Build
1. **Audience and objective** — who decides what; From → To (what they believe now, what they must believe after).
2. **Governing thought** — one sentence (≤25 words) that answers the audience's main question; specific, arguable,
   implies action, survives "so what?". It must be supported by accepted evidence or labelled as a proposal.
3. **Executive questions** — the questions the audience brings, in the order the story answers them.
4. **Story arc** — the archetype (SCR, answer-first + pillars, diagnosis → root cause → prescription, options →
   criteria → recommendation) and the sections. **When Hugo approved a storyline guide in Framing & Shaping, it is the
   arc:** keep his sections and their order, and build the claims slide by slide. Map every slide in `guion_map`
   (`covered` when accepted evidence answers its question, `partial` when only part of it, `missing` when nothing does).
   A `missing` slide is never filled in: its question goes to `unresolved_questions` so it can be researched.
5. **Claims** — one claim per idea. Each claim: `question` (the audience's), `headline` (a conclusion with a verb,
   ≤15 words), `answer` (2–3 sentences), `role_in_story` (context, evidence, diagnosis, implication, recommendation,
   limitation), `evidence_ids` (accepted findings F-…), `table_ids` (T-… for every number), `research_ids`,
   `framework_ids`, `confidence`, `limitations`, `visual_intent` (the *relationship* to make visible — converge,
   leak, split, outgrow… — never a layout).
6. **Recommendations** — conditional where evidence is associative ("si X se confirma, entonces…"); actions to
   validate, request data or experiment are legitimate recommendations.
7. **Appendix candidates, unresolved questions** — what is parked and why.

## Rules (validated in code before handoff)
- No unsupported claim: every claim cites accepted evidence, or is explicitly a PROPOSAL/limitation.
- Every material number in a headline or answer appears in one of the claim's tables.
- Causal language only where causality was shown; otherwise associative ("coincide con", "se asocia a").
- Nothing marked needs_review goes in without Hugo re-reviewing it.
- Hugo's storyline guide is followed, not rewritten; slides without evidence are flagged, not invented.
- Keep Hugo's vocabulary; the executive version may raise clarity, not replace his thinking.
