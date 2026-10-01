---
name: executive-storyline
description: "Turn raw material (briefing, document, business case, findings, research, data, outline, or a mix) into an executive storyline BEFORE any design: audience and decision, governing thought, pyramid (key line), argument sequence, one brief per slide (question, action-title message, role in story, support, visual intent, must_show, must_not_do), fact/inference/proposal separation, and a cut list. Pyramid Principle, SCR/SCQA, answer-first, MECE. Challenges weak content instead of formatting it. Never produces HTML. Use as stage 1 of executive-visual-storyteller, or alone when the user says 'arma la narrativa', 'storyline', 'qué historia cuento', 'governing thought', '¿estoy comunicando una conclusión o solo mostrando datos?', 'títulos de conclusión', 'reduce el deck', 'ordena este contenido para comité', 'build the storyline', 'is this a conclusion or just data?'."
---

# Executive Storyline

Design does not fix a bad idea. This skill decides **what the audience must understand, in what
order, and why they should believe it** — before anyone thinks about layout.

Output: `storyline.md` in the deck folder (structure below). No HTML, no layouts, no colors.
The only visual thing you write is `visual_intent`: the *relationship* the slide must make
visible, never its layout.

## Procedure

**0 · Frame the audience and the decision.** Who is in the room (or reading)? What decision or
belief change is this for? What do they believe today, and what must they believe after (From → To)?
What will they be skeptical about? Presented or read-ahead? How many minutes? If the decision is
unknown, infer the most plausible one, state it as an assumption, and flag it.

**1 · Inventory claims.** Extract atomic claims from all sources. Tag each:
- `FACT` — sourced, verifiable (keep the source).
- `INFERENCE` — reasoned from facts (write the logic in one line).
- `PROPOSAL` — what we recommend.
Rate evidence strength (strong / partial / none). Claims without support are listed in section 7
and never become headlines without a caveat.

**2 · Synthesize the governing thought.** One sentence (≤ 25 words) that answers the audience's
main question. Tests: it is specific (numbers, names), arguable, implies action, and survives
"so what?". Could the CEO repeat it after the meeting? If the sources support several, pick the
one that serves the decision and demote the rest.

**3 · Build the key line.** 2–5 supporting points, each a full-sentence conclusion, MECE.
Choose the logic explicitly:
- *Inductive* (pillars/reasons that together prove the thought) — for recommendations.
- *Deductive* (situation → complication → therefore) — for problems the audience does not yet feel.
Check MECE: no overlap between points; together they are sufficient.

**4 · Sequence.** Pick an archetype from `references/storyline-patterns.md` (SCR, answer-first +
pillars, diagnosis → root cause → prescription, options → criteria → recommendation, from–to,
value at stake, status + decision). Each slide answers **one** question that the previous slide
raised. Connect titles with *and so / but / therefore* — if a transition needs "also", the order
is wrong or the slide is redundant.

**5 · Write one brief per slide** (YAML, schema in `references/slide-brief-schema.md`):
question, message (action title), role_in_story, support (with FACT/INFERENCE/PROPOSAL tags),
visual_intent (the relationship to make visible), must_show, must_not_do, notes (what is said
but not shown).

**6 · Cut and park.** List what does NOT appear and why (not decision-relevant, weak evidence,
process detail, redundant). Park supporting detail in appendix or speaker notes. A deck is judged
by what it leaves out.

**7 · Test before handing off:**
- **Ghost-deck read-through**: read only the titles in order — do they tell the whole argument?
- **So-what test** on every title.
- **One question per slide**; no slide carries two messages.
- **Evidence test**: every title is supported by the slide's content (vertical logic).
- **Skeptic test**: what would a skeptical CFO attack? Is it pre-empted or acknowledged?
- **Budget**: slide count fits the time (≈ 2–3 min per content slide when presented).

## Principles

- **Answer first.** The governing thought appears on slide 1–2, not at the end.
- **Titles are conclusions** (subject + verb + so-what), ≤ ~15 words, ≤ 2 lines. Never topics.
  "Resultados Q2" ✗ → "Q2 creció 8% pero todo el crecimiento vino de precio, no de volumen" ✓.
- **One idea per slide.** If a slide needs "y además", split it or demote the second idea.
- **Separate fact, inference and proposal** — in the brief tags and in the language
  ("los datos muestran…" / "esto sugiere…" / "proponemos…").
- **Specific beats general.** Numbers, names, dates. Hedging words ("potencialmente",
  "podría ayudar") are removed or justified.
- **MECE when it applies** (key line, issue trees, segmentations) — not for narrative flow.
- **Synthesize, prioritize, eliminate, structure — then visualize.** Never turn 400 words into
  small type.
- **The headline's verb must be literally true** against its own exhibit: do not write "cierran
  las fugas" over bars that recover 40% of them — write what the data shows ("recuperan $370 M").
- **The takeaway lives on the page**, never only in the speaker notes. If the audience must
  conclude it, the slide must say or show it.
- **One name per concept across the deck.** A leak called "Nunca llega a producción" on page 2 has
  that exact name everywhere. Build a vocabulary list in §4 and reuse it.
- **No internal references in board-facing text** ("S02", "v2", file names): say "página 2".

## Challenge weak content (do not format it)

When the input is a list, ask what relationship the list hides. See
`references/synthesis-examples.md`. Canonical case — input: *"Métricas: CAC, LTV, churn, ARPU,
ARR"*. Do not brief five KPI boxes. Ask: what do we want to say about them? Usually the
relationship is unit economics: `LTV = ARPU × margen / churn`, `LTV/CAC` as the health ratio, ARR
as the scale outcome — so the slide is a driver tree whose message is *which lever moves the
ratio*. Write that as the brief and flag the question to the user if the intent is unclear.

## Output: storyline.md

```markdown
# Storyline — <deck title>
## 1. Audiencia y decisión        (who, decision, From → To, skepticism, format, time)
## 2. Governing thought           (one sentence) + why this one
## 3. Pirámide                    (governing thought → key line → evidence; logic type; MECE check)
## 4. Secuencia                   (archetype; table: # · question · action title · role)
                                  + ghost-deck read-through (titles only, in order)
## 5. Slide briefs                (one YAML block per slide)
## 6. Lo que NO aparece           (cut list with reason) + apéndice + notas
## 7. Claims sin evidencia / supuestos / preguntas abiertas
```

Language: write in the user's language (Spanish by default for Spanish requests); keep business
terms the user uses in English (funnel, churn, pipeline) as they write them.

## Handoff

`consulting-visual-director` reads section 5. Make `visual_intent` a relationship
("mostrar tres journeys distintos que convergen en un resultado económico común"), and seed
`must_not_do` with the lazy versions you can already foresee ("no tres cards con bullets",
"no una tabla").
