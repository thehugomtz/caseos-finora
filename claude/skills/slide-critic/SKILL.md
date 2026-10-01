---
name: slide-critic
description: "Visual QA loop for executive HTML slides: render → screenshot → blind read at thumbnail size → checklist (story, visual, content, technical) → scored verdict per slide: PASS, PATCH (executional fixes) or RECOMPOSE (wrong composition → regenerate with a different visual grammar) — plus a deck-level review from the contact sheet (rhythm, repetition, density, variety, system consistency). Combines automated probe metrics (overflow, clipping, text overlap, contrast, min size, word budget, card-grid detector, accent dilution, focal declaration, near-miss alignment, ink coverage) with image-based judgment, and refuses to fix conceptual failures with padding tweaks. Writes qa-report.md with an iteration log. Use as stage 5 of executive-visual-storyteller, or when the user says 'revisa estas slides', 'critica el deck', 'esta slide está muy AI', '¿se entiende en 3 segundos?', 'QA visual', 'review my slides', 'critique this deck'."
---

# Slide Critic

A slide is not done because the HTML compiles. It is done when a render has been **looked at**,
judged against its spec, and either passed or sent back with a precise instruction.

## The loop

```
render (render.mjs) → blind read (thumb) → inspect (full PNG + qa-summary) → score → verdict
   ↑                                                                               │
   └──── PATCH: executional fix in the same composition ◄──────────────────────────┤
   └──── RECOMPOSE: new spec from a different grammar (consulting-visual-director) ◄┘
```

Max **3 author iterations per slide**. If a slide still fails after 3, stop, keep the best
version, and escalate to the user with the specific unresolved problem. An independent review may
trigger **one more targeted patch** when its fixes are executional and concrete; apply it, and still
report the slide to the user as an explicit escalation (it went past the cap). A second RECOMPOSE
past the cap is never applied silently — ask.

## Step 1 · Render and read the machine report

```bash
node ${CLAUDE_SKILL_DIR}/../html-slide-renderer/scripts/render.mjs <deck>        # or --only 03
```
Read `renders/qa-summary.md`. **Every ✖ error must be fixed before any PASS.** ⚠ warnings must
each be either fixed or explicitly justified in the report (e.g. "`sparse` — intentional:
statement slide").

## Step 2 · Blind read (before reading the spec)

Open `renders/thumbs/NN.png` (480 px). In three seconds, write down:
1. **What I see first** (the element the eye lands on).
2. **What I think the slide says** (one sentence, in your own words).
3. **What I see second.**
Only then open the spec (`slide-specs/Sxx.yaml`) and compare with its `takeaway`, `focal_point`
and `visual_hierarchy`. A mismatch in 1 or 2 is a **focal/story failure**, not a craft detail.

## Step 3 · Inspect the full render

Open `renders/NN.png` and go through `references/checklist.md` — Story, Visual, Content,
Technical. Look for what metrics cannot see: boredom, clutter, weak hierarchy, a relationship
that is only implied, an annotation far from its data, lines that cross text, awkward rag,
widows in headlines, arrowheads colliding, visual weight drifting to a corner.

## Step 4 · Score and decide

Score each dimension 1–5 with the anchors in `references/rubric.md`:
**Story** (takeaway + headline) · **Focal & hierarchy** · **Visualization fidelity** (is the idea
*visualized* or just decorated?) · **Economy** (words, objects) · **Craft** (technical) ·
**System** (deck consistency).

Verdict rules:
- **RECOMPOSE** if Story ≤ 2, Fidelity ≤ 2, Focal ≤ 2, an unjustified card grid, or the blind
  read does not match the takeaway. Name the new composition family and why. Do not touch padding.
- **PATCH** if all dimensions ≥ 3 but any ✖ error remains or Craft/Economy ≤ 3. Write the
  patch list as concrete edits ("cut the second annotation to 12 words", "move the leak label
  left of the bar", "raise focal metric to 200px").
- **PASS** only if every dimension ≥ 4, no ✖ errors, every ⚠ fixed or justified.

Use `references/failure-modes.md` to diagnose symptoms and choose the move.

## Step 5 · Deck-level review

Open `renders/contact-sheet.png`. Check (details in checklist.md §Deck):
repetition of compositions, rhythm (dense/light alternation, breathers), density outliers,
boring slides, variety (≥ 60% distinct compositions), and **system consistency** (headline
position and size, margins, footer, accent meaning, line and annotation language). Read the
`Nivel deck` section of qa-summary.md. Visual consistency ≠ layout repetition.

## Step 6 · Write qa-report.md

```markdown
# QA — <deck>
## Resumen                 (verdict counts, iterations, residual risks)
## Deck                    (contact sheet findings, rhythm table, system consistency)
## Sxx — <headline>        (per slide)
- Lectura a ciegas: primero veo … / entiendo … / segundo …
- Spec: takeaway … / focal …  → coincide | no coincide
- Scores: story 4 · focal 5 · fidelity 4 · economy 3 · craft 4 · system 5
- Flags automáticos: ✖/⚠ … (resuelto | justificado: …)
- Veredicto: PASS | PATCH | RECOMPOSE (→ nueva composición: …, por qué)
- Cambios aplicados (iteración n): …
## Iteration log            (v1 → v2 → v3 per slide, with before/after renders kept as renders/NN.vK.png)
```
Keep the pre-revision render (`cp renders/NN.png renders/NN.v1.png`) before re-rendering, so
before/after can be compared.

## Independent mode

For the final pass, prefer a critic with fresh context: spawn the `independent-slide-critic`
agent (or a general-purpose subagent loading this skill) with the deck path. It reads renders,
specs and qa.json, **never edits files**, and returns verdicts. The author applies the changes.
The author of a slide is the worst judge of it.

## Non-negotiables

- Never PASS a slide you have not looked at as an image.
- Never fix a conceptual failure with spacing, font size or color.
- Never shrink type below the scale to resolve overflow — cut words or recompose.
- Never accept "it has a card grid but it looks clean": cards need a written justification.
