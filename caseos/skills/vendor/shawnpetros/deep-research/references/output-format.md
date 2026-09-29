# Output format — deep-research report

Every deep-research invocation produces a markdown report with this
exact structure. The structure is load-bearing: it forces the
synthesizer to separate what's KNOWN from what's CONTESTED from what's
UNKNOWN, which is the whole point.

## Template

```markdown
---
title: "Deep research: {topic}"
topic: {slug}
date: {YYYY-MM-DD}
confidence: {high | moderate | mixed | low}
---

# Deep research: {topic}

**Question:** {the primary question}

**BLUF (bottom line up front):**
{2-3 sentences answering the question with a confidence grade. If the
research didn't converge, say so here — the reader should know in 10
seconds whether this report resolved the question or just mapped it.}

## High-confidence findings

Claims where multiple independent sources agree AND the citations
verified.

- **{claim}** — {1-sentence expansion with key specifics.} [refs: 1, 3, 7]
- **{claim}** — ... [refs: 2, 4]

## Contested claims

Places where the research surfaced disagreement. Both sides stated with
citations. Do not resolve these by picking a side — the reader needs to
see the actual disagreement.

### {contested-claim-1}

- **Position A:** {summary} [refs: 2, 5]
- **Position B:** {summary} [refs: 8, 9]
- **Peer-review note:** {which side has stronger or more recent
  evidence, or "genuinely undecided in the literature"}

### {contested-claim-2}

...

## Unknowns

Questions the research actively tried to answer but could not. Explicit
about what was looked for and why it wasn't found.

- **{unknown-1}** — searched for {X}, found only {Y}; primary sources
  unavailable / rate-limited / pre-print-only / didn't exist.
- **{unknown-2}** — ...

## Follow-up research questions

What to investigate next, in priority order.

1. **{question-1}** — why it matters: {rationale}
2. **{question-2}** — ...

## Hallucination flags

Claims that sounded specific but failed verification during peer
review. Explicitly called out so they don't silently propagate.

- **"Paper X by Author Y, 2024"** — citation could not be located;
  no paper by that name appears in Google Scholar or arXiv. DO NOT
  cite this in downstream work.
- ...

## Citations

Consolidated list. Each citation graded for source quality.

| # | Citation | Type | Quality | Verified |
|---|----------|------|---------|----------|
| 1 | {url-or-reference} | primary / academic / industry / blog | high / medium / low | ✓ / ✗ / partial |

## Methodology note

```
Depth agent: {N} searches, {M} web-fetches, finished in {duration}
Breadth agent: {N} searches, {M} web-fetches, finished in {duration}
Counter agent: {N} searches, {M} web-fetches, finished in {duration}
Peer reviewer: verified {K} top-cited sources directly
```

This block is for forensics later — if a claim turns out wrong, it
tells us which agent pass surfaced it and whether the peer reviewer
actually checked it.
```

## Grading rubric for the `confidence:` frontmatter field

- **high** — primary sources converge on a clear answer, peer reviewer
  verified top citations, contested claims are peripheral
- **moderate** — consensus exists but with caveats; some contested
  claims bear on the core question
- **mixed** — the research surfaced genuine disagreement at the core of
  the question, not at the edges
- **low** — the research did not converge; use as an inventory of what's
  out there, not as an answer

## When the report says "low confidence"

This is not a failure. A well-structured "we couldn't find the answer"
report is more useful than a confidently-wrong "here's the answer"
report.

If confidence is low, the BLUF should say so in the first sentence:

> *BLUF: The research did not converge. {Specific reasons}.
> {What's known} is covered below, but the primary question remains open.
> See "Follow-up research questions" for next steps.*
