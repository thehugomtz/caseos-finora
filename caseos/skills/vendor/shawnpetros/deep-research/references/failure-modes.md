# Known failure modes — deep-research

Patterns that have broken research quality in practice, with prevention
notes. Add to this file when a new failure mode surfaces.

## 1. LLM-marketing-content swamp

**Symptom:** Web searches on AI / tech / SaaS topics often return SEO-
optimized blog posts from companies selling products in the space. The
content is plausible but authorless, uncited, and frequently
hallucinates specifics to sound authoritative.

**Prevention:**
- Depth + breadth agents: when a result is a company blog, check
  whether the claim appears in a primary source. If not, down-weight.
- Peer reviewer: grade any source from a company blog as `industry`
  quality at best (never `primary` or `academic`).

## 2. Hallucinated paper titles and citations

**Symptom:** Subagents cite plausible-sounding papers that do not
exist — "Smith et al., 2024, 'Scaling Laws for Agentic Workflows'" when
no such paper exists. The LLM pattern-matches into a citation shape.

**Prevention:**
- Peer reviewer MUST attempt to verify the top 3 most-cited sources by
  fetching them. If a paper can't be located in arXiv / Google Scholar /
  the journal's site, flag.
- Researchers should prefer quoting URLs they actually web-fetched over
  citing paper titles from memory.

## 3. Stale research on fast-moving topics

**Symptom:** On topics like AI capabilities, model releases, or
platform algorithm changes, research from >12 months ago is frequently
obsolete — but subagents happily cite 2022 blog posts as though they
were current.

**Prevention:**
- Peer reviewer calls out date freshness. Any claim about a technology
  where the research is >12 months old gets flagged as "may be stale".
- Topics known to move fast (AI/ML, social platform algos, legal/
  regulatory) get a "freshness caveat" in the BLUF.

## 4. False balance

**Symptom:** Counter-agent finds opposition to a well-established
consensus (e.g. one fringe paper against dozens of replicated studies).
Synthesizer weighs them equally as "contested" because both sides have
citations.

**Prevention:**
- Peer reviewer judges weight, not just existence. A single counter-
  source does NOT make a claim "contested" — note it as a minority
  view or outlier, and put the consensus in "high confidence".
- The "contested claims" section is for GENUINE disagreement in the
  literature, not every criticism that exists.

## 5. Scope creep

**Symptom:** Subagent drifts from the primary question into adjacent
territory. Dossier is 1500 words but the core question is answered in
one paragraph.

**Prevention:**
- Every subagent brief has an explicit "Out of scope" section.
- Depth agent MUST stay on the primary question. Breadth is for breadth.
- Peer reviewer flags dossiers that drifted.

## 6. Confidence theatre

**Symptom:** Synthesizer produces a confidently-worded report even when
the underlying research didn't converge. Reader mistakes well-formatted
uncertainty for validated knowledge.

**Prevention:**
- The `confidence:` frontmatter field is mandatory and must be set
  honestly.
- BLUF must say "the research did not converge" if that's the reality.
  No softening.
- A `low` or `mixed` confidence report is not a failure — a
  confidently-wrong `high` report is.

## 7. Mono-source capture

**Symptom:** Several claims in the final report all trace to the same
underlying source (e.g. one company's white paper referenced by four
blog posts that all paraphrase it). Looks like multi-source agreement,
isn't.

**Prevention:**
- Peer reviewer checks provenance chains. If multiple citations collapse
  to the same primary source, annotate the claim as "single primary
  source" in the high-confidence section.

## 8. Researcher-induced framing bias

**Symptom:** The brief given to each subagent phrases the question in
a way that presupposes the answer. Counter-agent then searches for
counter-evidence to the framed version, not the real question.

**Prevention:**
- The synthesizer (main session) checks each subagent's brief before
  dispatch. Rewrite any brief that contains a conclusion in the
  question phrasing.
- Peer reviewer flags this if it sees evidence of it in the dossiers.

## 9. The "I'll just use training data" shortcut

**Symptom:** Subagent answers from memory instead of actually searching,
producing confident output with no citations. Looks plausible, no
provenance.

**Prevention:**
- Subagent briefs explicitly require N web searches and M web-fetches
  as a minimum. Numbers are non-negotiable.
- Peer reviewer flags any dossier with <3 citations as "insufficient
  research activity" regardless of content quality.

## 10. Vault write collision

**Symptom:** Skill writes to a vault path that conflicts with an
existing user file or doesn't exist. Silent failure.

**Prevention:**
- Check vault path exists before writing. If not, fall back to local
  `./research/` directory.
- Use date-stamped filenames so re-running on the same topic creates a
  new file rather than overwriting.
- Report the output path back to the user explicitly.
