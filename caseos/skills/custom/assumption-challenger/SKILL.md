---
name: assumption-challenger
description: CaseOS adaptation (no upstream skill with this exact name exists in alirezarezvani/claude-skills at the inspected commit). Challenge-only skill for the Framer and the executive-mentor critic. Extracts the assumptions a framing or storyline depends on, rates confidence × impact, and produces the strongest counterargument, an alternative explanation, the evidence that would invalidate the idea and the highest-risk claim. Adapted from executive-mentor's /em:challenge (pre-mortem) and /em:stress-test (MIT, Alireza Rezvani), with CaseOS tone rules.
license: MIT (CaseOS adaptation of alirezarezvani/claude-skills)
---

# Assumption Challenger

Activate only when an idea is formed enough to break: Hugo asks for challenge, a framing is about to be approved,
a material assumption appears, two explanations compete, or a conclusion looks too comfortable.

## Procedure
1. **Extract assumptions.** For the idea on the table ask: what has to be true for this to hold? Cover data
   semantics (does the metric mean what we think?), measurement (are we comparing like with like?), causality
   (is this association or cause?), composition (is it mix or behavior?), timing (is the window representative?),
   and audience (does the executive actually care about this cut?).
2. **Rate each one.** Confidence: high / medium / low / unknown. Impact if wrong: critical / high / medium / low.
   Vulnerability = low-or-unknown confidence × critical-or-high impact.
3. **Pre-mortem.** Imagine the storyline failed in front of the CFO. Work backwards: which assumption broke first?
4. **Strongest counterargument.** The single best argument against the idea — the one a smart skeptic would use,
   not a strawman.
5. **Alternative explanation.** A different mechanism compatible with the same observations.
6. **Invalidating evidence.** Concrete observations that would make us drop the idea (what table, what pattern,
   what number direction).
7. **Highest-risk claim.** The one claim that, if wrong, takes the most of the story down with it.

## Output (the Framer's `challenge` block)
- hidden_assumptions: 3–6 items, each "assumption — confidence / impact — why it may be wrong"
- strongest_counterargument: one paragraph
- alternative_explanation: one paragraph
- invalidating_evidence: 2–4 concrete checks
- highest_risk_claim: one sentence + why

## Tone
Calm, specific, useful. No theatrical aggression, no "brutal honesty" persona, no rhetorical questions stacked for
effect. The goal is a stronger case, not a bruised partner. Hard things are said plainly.
