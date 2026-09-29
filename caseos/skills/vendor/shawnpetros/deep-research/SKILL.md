---
name: deep-research
description: Use when the user asks you to research a topic and wants thesis-grade synthesis, not a bullet-point summary. Activates on "research X", "deep dive on X", "find out about X", "what's actually known about X". Dispatches depth + breadth + counter-argument subagents concurrently, runs a peer-review pass over their findings for hallucination and citation quality, then synthesizes into a structured report with explicit high-confidence / contested / unknown buckets. Output file optionally persisted to a knowledge vault.
---

# Deep Research

A 4-role, peer-reviewed research pattern that produces thesis-grade output
instead of the web-search summary slop that LLMs default to.

## When to activate

- User asks "research X", "deep dive on X", "find out about X"
- User says "I want to know what's actually known about X"
- User asks a question where an answer built from one web search or
  confident-guessing from training data would be dangerous (load-bearing
  decisions, claims that will be cited, topics where hallucinations are
  likely)
- A previous conversation surfaced a speculative claim that needs
  validation before it lands in code or a plan

## When NOT to activate

- Quick factual lookups ("what's the latest version of React") — use
  Context7 or a single web fetch
- Well-known concepts the model already knows cold — answer directly
- Questions about the local codebase — use the Explore agent
- The user wants opinion, not evidence

## The four roles

All four are dispatched via the Agent tool with `subagent_type: general-purpose`.
Each role has a distinct prompt shape — do not collapse them.

### 1. Depth researcher (1 agent)

Goes deep on the PRIMARY question. Multiple web searches + web fetches
on the specific topic. Produces a detailed findings dossier with citations
for every load-bearing claim.

### 2. Breadth researcher (1 agent)

Surveys adjacent/related topics, alternative framings, and historical
context. Broader search scope, looking for relevance-adjacent material
the depth agent might miss. Explicitly asks "what related things should
I know to understand this properly?"

### 3. Counter-argument researcher (1 agent)

Actively searches for contradicting views, cases where the thesis fails,
opposing schools of thought, known criticisms. Not "balance" — actively
adversarial, looking for holes.

### 4. Peer reviewer (1 agent, runs AFTER the first three return)

Takes all findings from roles 1-3 and produces a peer-review report:
- Claim → citation mapping (which claims have support, which are bare assertions)
- Internal contradictions between findings
- Claims where multiple sources agree (high-confidence)
- Claims where sources disagree (contested)
- Gaps — things that were researched but no citation was found
- Hallucination risk flags — claims that sound specific but have no citation

## Process

1. **Brief.** Read the user's topic. Extract:
   - The primary question (depth target)
   - 2-4 adjacent topics (breadth targets)
   - 1-2 counter-hypotheses to actively seek (counter targets)
   - Any specific source types to privilege (academic papers, primary
     sources, industry reports) or exclude (pure marketing content)
2. **Dispatch concurrently.** In ONE message, send three Agent tool calls
   (depth + breadth + counter). They run in parallel. Each returns a
   structured findings dossier.
3. **Dispatch peer reviewer** with all three dossiers as input.
4. **Synthesize** (main session, not subagent). Produce the report per
   the output format below.
5. **Persist** to the vault if one exists (see "Vault persistence").

See `references/subagent-briefs.md` for the exact prompt template each
role should receive.

## Output format

Every deep-research output has the same six-section shape. See
`references/output-format.md` for the full template.

1. **Bottom-line-up-front** — 2-3 sentences answering the question with
   an explicit confidence grade.
2. **High-confidence findings** — claims with multi-source corroboration.
3. **Contested claims** — where sources disagree; both sides with
   citations.
4. **Unknowns** — questions the research did NOT resolve.
5. **Follow-up research questions** — what to investigate next.
6. **Citations** — consolidated list, graded by source quality.

Hallucination flags and peer-review notes appear inline next to the
specific claim, not in a separate dumping ground. A report that reads
clean without any flags is a report the peer-reviewer didn't try hard
enough on.

## Vault persistence

If the user has an Obsidian-style vault (default path:
`~/Documents/Personal Notes/`), write the report to
`50-References/deep-research-{slug}-{YYYY-MM-DD}.md` and update
`index.md` + `log.md` per the standard vault-write convention.

If no vault is configured, write to `./research/{slug}-{YYYY-MM-DD}.md`
in the current working directory.

In both cases, report the output path back to the user so they can
find it later.

## Concurrency rules

- Depth + breadth + counter dispatch IN PARALLEL (single message, 3 tool
  calls). Do not sequence them.
- Peer reviewer runs AFTER, sequentially. It needs the first three's
  outputs as input.
- Maximum 3 concurrent subagents at the research stage. Do not expand.
- Max 1 deep-research invocation at a time per session — if the user
  asks for two topics, do them sequentially.

## Known failure modes

See `references/failure-modes.md` for details. Headline list:

1. **LLM-marketing-content swamp**: web searches on AI/tech topics often
   return SEO-stuffed blog content. Peer-reviewer must flag claims
   supported only by such sources as low-grade.
2. **Hallucinated paper titles**: subagents sometimes cite plausible-
   sounding papers that don't exist. Peer reviewer verifies at least the
   top 3 citations by attempting to resolve them.
3. **Stale research**: on fast-moving topics, research older than 12
   months may be obsolete. Peer reviewer calls out date freshness.
4. **False balance**: equal weight for mainstream + fringe views is
   wrong when the evidence is asymmetric. Peer reviewer judges weight.
5. **Scope creep**: subagents drift from the primary question. The brief
   given to each role must pin scope hard.

## What to tell the user on completion

- One-paragraph executive summary (copy from the report's BLUF section)
- Path to the full report
- Any peer-review-flagged items that specifically bear on what they
  asked (don't swallow contested claims silently)
- A recommended next step based on what the research surfaced

Do not paste the full report inline unless the user asks. The vault
(or local file) is the artifact.
