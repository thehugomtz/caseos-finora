# Anti-slop rules

"AI slop" in slides is not ugliness; it is **the absence of a decision**. Title, paragraph, card,
card, card, four equal boxes, bullets and decorative icons are what a layout looks like when
nobody decided what the idea is, what matters most, and how the parts relate. Every rule below
forces one of those decisions.

## The rules

1. **Cards are a fallback, not a composition.** Before drawing any card, answer in writing:
   *Is there an order? A hierarchy? A flow? A dependency? A magnitude? A containment? A tension?*
   If any answer is yes, draw that relationship. Cards survive only when items are genuinely
   independent, parallel and unordered — and then question whether they belong on one slide.
   Max **one** card grid per deck, marked `data-qa-allow="card-grid"` with a justification in the spec.
2. **N items do not mean N equal boxes.** Symmetry must be earned by the content. If one item
   matters more, it must *look* like it matters more (scale, position, accent).
3. **One focal point, found in < 3 seconds at thumbnail size.** If the thumbnail shows four equal
   things, the slide has no point.
4. **Relationships are drawn, not implied.** Proximity alone is not a relationship. Use
   connection (lines/arrows), containment (rings, brackets), alignment on a shared axis,
   position on a scale, or sequence along a path.
5. **Every visual variable must mean something.** Color, size, weight, dash, position: if it
   varies, it encodes. Decoration that encodes nothing is deleted.
6. **Accent is a signal.** One accent color, used for the insight — never for frames, headers,
   kickers, section labels or trackers, and never "to make it pop". When everything is accented
   nothing is (QA: `accent-diluted`).
7. **Labels live on the thing.** Direct labeling beats legends; annotations sit at the data point
   they talk about.
8. **Whitespace is structure.** Do not fill the canvas because there is room. A slide that
   breathes reads as confident.
9. **Words are a budget.** 40–90 words on canvas for most slides. The rest is speaker notes or
   appendix. Never shrink type to fit text: cut text to fit the idea.
10. **The headline is a conclusion**, not a topic ("Mercado" ✗ → "El mercado crece 12%, pero solo
    en el segmento premium" ✓).

## Forbidden defaults (unless they encode something and the spec says why)

- 3 or 4 identical boxes because there are 3 or 4 concepts
- bullet lists centered inside rectangles
- icons that decorate (a rocket for "growth", a lightbulb for "idea", a gear for "operations")
- emoji
- artificial symmetry
- gratuitous gradients, drop shadows, glassmorphism
- badges/pills everywhere; rounded "SaaS dashboard" tiles
- borders around everything (whitespace and hairlines separate better)
- KPI card rows (four big numbers in boxes) instead of the relationship between the numbers
- stock photography as background
- charts with legends when direct labels fit; 3D; dual axes; rainbow palettes
- "Key takeaways" slides with 6 bullets

## Tests to run on every spec (and again on every render)

| Test | Question | If it fails |
|---|---|---|
| **Card test** | Are there ≥ 3 similar boxes holding text? Is there a relationship among them? | Replace with the composition that draws the relationship (semantic-map.md) |
| **Squint test** | At 480px wide, blurred, what is the one thing you see? | Rescale: focal ×1.5–2, demote the rest |
| **Symmetry test** | Is the symmetry in the content or only in the layout? | Break it: size/position by importance |
| **Proximity test** | Is any relationship shown only by things being near each other? | Draw it (connect, contain, align, sequence) |
| **Icon test** | Would removing each icon lose information? | Remove it |
| **Border test** | Can whitespace or a hairline replace each box border? | Replace it |
| **Accent test** | Does the accent mark exactly the insight? | Remove it everywhere else |
| **Fill test** | Is anything there only because there was space? | Delete it |
| **Legend test** | Could every legend entry be a direct label? | Label directly |
| **Word test** | Can 30% of the words go without losing the argument? | Cut; move to notes |
| **Headline test** | Does the headline state a conclusion the visual proves? | Rewrite (storyline) or recompose |

## Smell → move

| Smell | What it usually means | Move |
|---|---|---|
| Three cards with a title + 3 bullets each | parallel "pillars" with hidden structure | Are they stages → `timeline`/`journey`; layers → `layered_architecture`; drivers → `driver_tree`; options → `decision_tree`/`two_by_two`; converging → `converging_paths` |
| Four KPI tiles | metrics without their relationship | `driver_tree` / `unit_economics_tree`, or `hero_metric` for the one that matters + context |
| A table of text | comparison without a pattern | `harvey_matrix`, `dumbbell`, `side_by_side_contrast`, or cut to the 2 rows that matter |
| Icon row with captions | a list pretending to be a framework | Find the verb; if none, it is a list — cut to 3 items and write them as a sentence |
| Centered title + centered paragraph | no composition at all | `single_big_statement` (if it's a thought) or `split_narrative` (if it needs evidence) |
| Chart + 5 bullets beside it | the chart does not make the point | Annotate the chart with the 1–2 bullets that matter; drop the rest to notes |
| Everything the same size | no hierarchy decision | Rank objects 1→4 in the spec; scale accordingly |
| Colored boxes per category | color used as decoration | Neutral structure + one accent for the insight |
| Chevron row "Phase 1 → Phase 2 → Phase 3" | time without scale or content | `timeline` with true durations and what changes when |
| Venn with text in every region | overlap without meaning | Keep the intersection only, or switch to `two_by_two` |
| Org chart of boxes | structure without decisions | `governance_architecture` / `decision_rights_matrix` |

## When cards are legitimate

- A catalogue of truly independent items the audience will browse (appendix).
- Small multiples with shared scales (then they are charts, not cards).
- A single "option" view where each option has identical attributes and the comparison is the
  point — prefer `harvey_matrix` first.

Even then: no shadows, no rounded tiles, no icons; hairline or whitespace separation; the
recommended item visibly different.
