---
name: deep-business-research
description: CaseOS Level-3 research method for questions that are material to a decision. Adapted from shawnpetros/claude-skills deep-research (MIT) — depth + breadth + counter-argument researchers, then peer review, then synthesis — extended for business cases with evidence definition, contradictory-evidence search, a source-quality ladder, triangulation and a case synthesis with HIGH CONFIDENCE / PLAUSIBLE / CONTESTED / UNKNOWN buckets. In CaseOS the roles are separate agent runs orchestrated by code, not subagents.
license: MIT (CaseOS adaptation of shawnpetros/claude-skills deep-research)
---

# Deep Business Research

Use only when the answer could change a decision or the storyline. Quick lookups and framework comparisons use
Level 1 / Level 2 research instead.

## Flow (code runs the roles; each role follows its section)
1. **Clarify the question** — restate it; name the case question/hypothesis/decision it serves; pin the scope.
2. **Define the evidence needed** — what result A would imply, what result B would imply, the minimum evidence that
   separates them, the preferred source types and a stop condition.
3. **Depth researcher** — goes deep on the primary question; multiple searches and fetches; a citation for every
   load-bearing claim.
4. **Breadth researcher** — adjacent topics, alternative framings, historical context, how practitioners actually do
   it; what someone must know to understand the question properly.
5. **Counter researcher** — builds the strongest counter-hypothesis and actively searches for contradicting
   evidence, failure cases and known criticisms. Adversarial, not balanced.
6. **Search contradictory evidence** — part of the counter role: look specifically for evidence against the leading
   answer, not only for alternative opinions.
7. **Source-quality review** — grade each source on the ladder below; flag marketing/SEO content; check freshness.
8. **Triangulation** — which claims are corroborated by independent sources of adequate quality.
9. **Peer review** — claim → citation mapping, bare assertions, internal contradictions, hallucination-risk flags
   (specific-sounding claims without a citation), false balance, scope drift.
10. **Case synthesis** — the case-research-synthesis output with explicit buckets.

## Confidence buckets
- **HIGH CONFIDENCE** — corroborated by ≥2 independent sources of grade A/B, no credible contradiction.
- **PLAUSIBLE** — one good source or several weaker ones; no contradiction found.
- **CONTESTED** — credible sources disagree; show both sides with citations and say which weighs more and why.
- **UNKNOWN** — researched without finding support; say what would settle it.

## Source-quality ladder (contextual order)
A · primary sources, official documentation, regulatory / institutional data, peer-reviewed academic work ·
B · credible industry research, company disclosures (filings, pricing pages as primary evidence of the company's own
offer), high-quality expert analysis with method · C · reputable journalism, practitioner write-ups with data ·
D · community / anecdotal, vendor marketing, SEO content. Marketing content is never evidence equivalent to A/B.

## Claim discipline (every material claim)
```yaml
claim: <one sentence>
source: <SRC id>
source_type: primary | official | regulatory | academic | industry | company | expert | journalism | community | marketing
confidence: high | medium | low
freshness: <publication or data date; flag if > 18 months on fast-moving topics>
supports_or_contests: supports | contests | context
notes: <caveats, sample, geography>
```
No invented sources. Every URL cited must be one actually retrieved in this run. Gaps are named, not filled.

## Known failure modes (from the reference skill)
SEO swamp on business topics · hallucinated report titles · stale data presented as current · false balance between
mainstream and fringe · scope creep away from the case question. The peer reviewer checks each explicitly.
