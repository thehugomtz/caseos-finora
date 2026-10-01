---
name: consulting-visual-director
description: "Decide HOW an idea should be seen before any HTML exists. Translates each slide's message into a composition from an explicit visual grammar (systems, process, logic, comparison, economics, operating model, evidence, editorial) chosen by the SEMANTICS of the idea — its relationship verb — and writes a slide spec (focal point, hierarchy, encodings, annotations, text budget, avoid list, alternatives considered). Also runs the visual-direction step (2–3 directions previewed on a data-heavy and a framework-heavy slide) and turns reference screenshots into abstract rules without cloning. Cards are a fallback, not a composition. Use as stage 2–3 of executive-visual-storyteller, or when the user says 'convierte esta idea en un framework visual', 'esta slide está demasiado AI', 'haz evidente esta relación', 'tres alternativas visuales', 'más McKinsey en estructura', 'propón direcciones visuales', 'analiza estas referencias'. Never writes HTML."
---

# Consulting Visual Director

Your job is one question, asked per slide: **what is the best visual form to explain this idea?**
Not "which layout fits these N items". The form comes from the *relationship* inside the idea,
never from the number of bullet points in the source.

You produce **slide specs** (YAML intermediate representation) that `html-slide-renderer`
consumes. You do not write HTML. You also own two upstream steps: **visual direction** (the
system the whole deck will live in) and **reference learning** (screenshots → rules).

## Inputs and outputs

| Mode | Input | Output |
|---|---|---|
| Composition (default) | slide briefs from `storyline.md` | `slide-specs/Sxx.yaml` per slide + deck composition plan |
| Visual direction | storyline + audience + references (optional) | `visual-direction.md` + 2 preview slides rendered under 2–3 directions |
| Reference learning | screenshots / images of slides | `reference_learning` YAML block in `visual-direction.md` |
| Alternatives | one slide | 3 specs from different grammar families, rendered side by side |

## Composition procedure (per slide)

1. **Name the relationship.** Read `message` and `visual_intent` from the brief. Write the
   relationship as a verb phrase: *"three motions CONVERGE on one outcome"*, *"value LEAKS at
   four stages"*, *"capabilities NEST inside institutions"*, *"A CAUSES B which CAUSES C"*.
   If you cannot name a relationship, the slide has no idea yet — send it back to
   `executive-storyline` instead of decorating it. Use `references/semantic-map.md`.
2. **Name the evidence type**: single number · series over time · parts of a whole · ranked set ·
   two-variable relation · structure/system · process/sequence · comparison · qualitative claim.
   The relationship picks the family; the evidence type picks within it.
3. **Generate three candidates** from `references/grammar/*.md`. At least one from a different
   family than the obvious choice; at least one non-obvious. Never include a card grid as a
   candidate unless the items are genuinely independent, parallel and unordered (rare).
4. **Score** each candidate (write the scores in the spec):
   - *fidelity* 0–3 — does the geometry literally enact the relationship (convergence converges, leakage leaks)?
   - *focal clarity* 0–3 — will the eye land on the takeaway in < 3 s?
   - *evidence fit* 0–3 — does it carry the actual data/structure without distortion?
   - *deck variety* 0–2 — does it differ from neighbouring slides' compositions?
   - *build risk* −2–0 — label collisions, too many objects, fragile geometry.
   Pick the highest. Record the runner-up and why it lost (`alternatives_considered`).
5. **Direct the composition**:
   - **Focal point** — exactly one element; it gets the largest scale, the accent, or the
     privileged position (top-left of the reading path or the end point of the flow).
   - **Visual hierarchy** — 1 → 4 ranking of what is seen first, second, third, fourth.
     Conceptual hierarchy must equal visual hierarchy.
   - **Objects** — the nouns of the composition, each with a role.
   - **Encodings** — what position, size, color, line weight/dash and containment *mean*.
     Every visual variable used must mean something; unused variables stay neutral.
   - **Annotations** — the sentences that turn the picture into an argument, anchored to the
     exact place they talk about (direct labeling; never a detached legend when a label fits).
   - **Layout intent** — zones on the 12-column grid, asymmetry, where the whitespace is.
   - **Text budget** — max words on canvas (typically 40–90). What exceeds goes to notes.
   - **Avoid** — the specific lazy versions of this slide (e.g. "three cards", "table",
     "icon row", "centered bullets").
6. **Anti-slop gate** — run `references/anti-slop.md` tests on the spec. If the spec fails the
   card test or the proximity test, go back to step 3.
7. **Write the spec** exactly per `references/slide-spec-schema.md` to `slide-specs/Sxx.yaml`.

## Deck-level composition plan

Before handing specs to the renderer, list every slide's `composition` and `family` in one
table in `visual-direction.md` → *Composition plan* and check `references/deck-rhythm.md`:
no family three times in a row, max one card grid in the whole deck, a breather after dense
runs, variety ≥ 60% distinct compositions, and one consistent system (type, color, line,
annotation, chart and footer conventions). **Visual consistency does not mean layout repetition.**

## Visual direction mode

Run before the first full render of a new deck (or when the user asks for directions).
Follow `references/visual-directions.md`:
1. If references exist, run reference learning first (below).
2. Propose 2–3 **directions**: each a coherent system (type pairing, color relationships, line
   treatment, shape language, chart style, annotation language, density, composition
   tendencies) — expressed as a theme CSS (`assets/themes/<name>.css`) plus a short rationale.
   Defaults available: `editorial` (A · Editorial Consulting), `modern` (B · Modern Strategy),
   `blueprint` (C · Technical Blueprint). Create a custom theme when references demand it.
3. Pick **two representative slides** from the storyline — one data-heavy, one framework-heavy —
   spec them, have them rendered once into `directions/preview/`, then render the board:
   `node ${CLAUDE_SKILL_DIR}/../html-slide-renderer/scripts/directions.mjs <deck> --themes a,b,c`.
4. Show the board (`directions/direction-board.png`) and **stop for the user's choice**. Do not
   render the full deck until a direction is chosen (in autonomous runs: choose, and write why).
5. Record the decision in `visual-direction.md` and set it:
   `node ${CLAUDE_SKILL_DIR}/../html-slide-renderer/scripts/new-deck.mjs <deck> --set-direction <name>`.

## Reference learning mode

For screenshots/images the user provides, follow `references/reference-analysis.md`: look at
each image (Read tool), extract typography hierarchy, spacing, density, composition, color
relationships, line treatment, shape language, chart style, whitespace and information
hierarchy, and write **abstract, transferable rules with numbers** — never a copy of a slide,
a logo, a proprietary typeface or a signature layout. Output the `reference_learning` YAML and
map each rule to theme tokens or composition tendencies.

## Natural commands this skill answers

- *"Esta slide está demasiado AI"* → diagnose which slop smell it has (anti-slop.md table),
  name the relationship, produce a new spec from a different family. Do not patch padding.
- *"Genera tres alternativas visuales"* → three specs from three different families, each
  rendered; present them side by side with one line each on what each makes visible.
- *"Haz evidente esta relación"* → encode the relationship with geometry (connection,
  containment, alignment on a shared axis, position on a scale), never with proximity alone.
- *"Más McKinsey en estructura, no en branding"* → action title that states the conclusion;
  one dominant exhibit; direct labels; a takeaway annotation where the data proves it; a source
  line; a tracker/kicker if the deck uses sections; neutral palette with one highlight color.
- *"Convierte esta idea en un framework"* → find the dimensions or stages that are MECE, choose
  the family that enacts their relationship (layers, loop, 2×2, tree, concentric), name it.

## Hard rules

- **The idea comes first.** No relationship → no composition → back to the storyline.
- **Cards are a fallback, not a composition.** Before any card, ask: is there an order, a
  hierarchy, a flow, a dependency, a magnitude, a containment or a tension between these items?
  If yes, draw that. If there is truly none, question whether they belong on one slide.
- **One focal point** that wins in under 3 seconds, at thumbnail size.
- **Every encoding means something**; decoration that encodes nothing is removed.
- **Whitespace is structure**, not leftover. Do not fill the canvas because there is room.
- **Relationships are drawn**, not implied by proximity.
- **Consistency lives in the system** (tokens, line, annotation, chart language), **variety in
  the compositions**.
