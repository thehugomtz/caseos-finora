---
name: case-research-synthesis
description: CaseOS skill that every research run ends with. Turns whatever a research agent found into what matters for THIS case — the case question it serves, a short answer, findings with evidence, alternative explanations, what is established / contested / unknown, the implication for the case, whether it changes the current story, which hypotheses and claims it affects, the suggested action and new questions — as a structured handoff to the Chief of Staff. Never "here are 18 interesting things I found".
license: MIT (CaseOS)
---

# Case Research Synthesis

Research exists to reduce uncertainty that matters to the case. The synthesis answers: *what does this change
for us?* Start from the case question the research was launched for — not from what was interesting.

## Required output (ResearchResult)
- **research_question** — what was asked, as asked.
- **case_question** — the case question / hypothesis / decision / claim it serves (by ID when known).
- **why_it_matters** — one or two sentences: which decision or story element could change.
- **short_answer** — the answer in ≤3 sentences, with its confidence. If the evidence does not answer the question,
  say so first ("No se puede responder con lo disponible porque…").
- **findings** — 1–5 findings that matter for the case, each a full-sentence claim with its evidence, confidence and
  limitation. Cut everything that does not change the case.
- **evidence / claims** — every material claim with its source ID, source type, confidence, freshness and whether it
  supports or contests the case hypothesis.
- **alternative_explanations** — other mechanisms compatible with the same evidence.
- **what_is_established / what_is_contested / what_remains_unknown** — three honest buckets.
- **case_implication** — what this means for the case in one paragraph.
- **changes_current_story** — yes / no / maybe, with why.
- **affected_hypotheses / affected_claims** — IDs and the effect (supports, weakens, contradicts…).
- **suggested_action** — the next step you would take (not a decision).
- **new_questions** — at most three, each phrased as an answerable question.
- **handoff_to_cos** — two or three lines the Chief of Staff can act on.

## Discipline
- Separate external research from internal evidence, and current data from benchmarks. A benchmark is context,
  never a recommendation and never evidence about this company.
- No invented citations. If a claim has no source, it is labelled as inference and cannot carry numbers.
- Do not fill gaps with "common knowledge" silently: name the gap.
- Prefer the smallest answer that resolves the uncertainty. Precision beyond what the decision needs is noise.
- Write in the case language. Keep Hugo's vocabulary; add precision next to it.
