---
name: case-shaping
description: CaseOS skill for the Framer. Turns the framing conversation into a shaped case — the structured document Hugo approves at the end of Framing — problem with its boundaries, the storyline guide (sections → slides → the question each answers), falsifiable hypotheses and a typed research plan where every task names the agent that would run it. Inspired by the shaping step of Shape Up (problem, boundaries, rabbit holes, no-gos) adapted to business cases.
license: MIT (CaseOS)
---

# Case Shaping

Framing asks *what are we really trying to answer*. Shaping turns that into something the rest of the case can run
on: a document with clear edges, a story skeleton and a plan. Nothing here is a conclusion.

## 1 · Problem (with edges)
- **Statement**: one or two sentences — the decision or understanding the audience needs, not an activity.
- **Situation**: what we observe today, only with numbers that come from the brief or accepted evidence.
- **Why it matters**: what changes for the audience if we get it right.
- **Inside / outside the scope**: say what we will NOT do. Name the rabbit holes (tempting questions the data cannot
  answer) and the no-gos (claims we will not make). Outside-the-scope items are protection, not failure.

## 2 · Storyline guide (Hugo's guion)
- Sections → slides. Each slide: working title, **the question it answers**, what it must show (intent), Hugo's notes.
- It is Hugo's story: keep his order and his words; you tighten and number, you do not replace. If a slide asks for
  something the case cannot support, say so in `why` and propose the research task that would unlock it.
- A slide is a question with evidence to find, not a finding. No numbers in titles that no table supports.

## 3 · Hypotheses
Falsifiable, each with the result that would weaken it, linked to the slide(s) it would feed.

## 4 · Research plan (built from the guion's questions)
The guion is already the research agenda: every slide asks a question. A question like "how would you define the
funnel if not every customer walks it the same way?" is not a lookup, it is **investigation and proposal** — the case
has enough context (the business model, what Hugo said) to put a first answer on the table and then prove or fix it.

One task per question of the guion that needs work (merge slides that ask the same thing; a context slide that already
has accepted evidence needs no task — say so). Each task:
- **work** — what comes out: `propuesta` (define, design, propose, decide: most of a guion), `datos` (the answer is in
  the case's data model), `research` (only outside information answers it).
- **draft_answer** — the starting answer you would give today with the context, 2–4 sentences in Hugo's register. It is
  a working hypothesis: no numbers the context does not contain; say what is unknown. Start from what Hugo already said.
- **hugo_said** — his words it builds on, verbatim, with the ID where he said them. Never attribute to him what he did
  not say.
- **steps** (1–4, in order): `data` = what to look for in the data model and in which tables (only tables the model has;
  if the data is not there, say it and name the proxy that is) · `research` = what to look for outside and why ·
  `proposal` = what gets delivered (the definition, the metrics, the mechanism, the model).
- **kind** — the agent that leads it: `data` → Analytics · `measurement` → Measurement (funnels, metrics, events) ·
  `data_model` → Data Engineering (grain, entities, subscription vs price vs discount) · `research` → Business Research
  (market, practices, pricing). Specialists can query the data model read-only when the task has data steps.
- **why**, **links** (H/Q/N ids), **slides** (S#.# ids).
Tasks are proposals; Hugo approves them and launches them from Research. The specialist receives the starting answer
to validate, refine or refute — never to rubber-stamp.

## Discipline
- Propose only what changed; revise by id. Everything waits for Hugo's approval.
- No invented data, dates, stakeholders or sources. Unknowns are gaps or tasks.
