# Comparison

### `before_after`
- **Use when** the same system is shown in two states and the change is the message.
- **Anatomy** two aligned depictions of the same structure (left = today, right = target) with the
  changes marked; a divider or arrow between.
- **Encode** identical structure and scale on both sides so the eye sees only the change; accent
  only on what changed.
- **Focal** the change.
- **Pitfalls** two different diagrams that cannot be compared; two columns of bullets.
- **Build** draw one structure function and call it twice with different parameters (`P.draw` helper inside the slide script).

### `from_to_shift`
- **Use when** a set of shifts (from X to Y) defines a transformation.
- **Anatomy** rows of "from" (muted) → "to" (ink) aligned on two columns with arrows; the
  row that matters most emphasized.
- **Encode** muted vs ink contrast carries the direction; accent arrow for the key shift.
- **Budget** 3–6 shifts, ≤ 6 words each side.
- **Pitfalls** a table with a header "From / To" and 10 rows.
- **Build** two HTML text columns aligned to grid columns; `s.line(..., {arrow:'end'})` between.

### `side_by_side_contrast`
- **Use when** two options/models/players differ on a few attributes.
- **Anatomy** two columns, attributes as shared rows; the attribute that decides highlighted.
- **Encode** alignment across columns; bars or dots for comparable values; accent = decisive difference.
- **Pitfalls** two symmetric cards; attributes listed in different orders.

### `spectrum`
- **Use when** items sit between two poles of one dimension (centralized ↔ federated, cost ↔ premium).
- **Anatomy** a long axis with pole labels; items as markers with labels; optional movement arrows (today → target).
- **Encode** position = degree; arrows = intended movement; accent = our position/target.
- **Focal** where we are vs where we should be.
- **Build** `s.line` axis with end ticks; markers with `s.dot`; alternating label sides; `s.connect([x0,y],[x1,y],{route:'arc'})` for movement.

### `two_by_two`
- **Use when** two independent dimensions classify items and the quadrants have meaning.
- **Anatomy** two axes (hairlines), quadrant names in corners (muted), items as markers.
- **Encode** position = scores; marker size = a third variable only if essential; accent = the
  quadrant or items the message is about.
- **Focal** the target quadrant / the item that moves.
- **Pitfalls** four colored boxes with text (a card grid in disguise); axes without direction labels.
- **Build** axes via `s.line` with arrow ends; quadrant labels `.caps` in muted ink; items with `s.dot` + `s.label` offset.

### `harvey_matrix`
- **Use when** n options × m criteria and the pattern (who wins where) matters.
- **Anatomy** options as rows, criteria as columns, filled-circle ratings (0–4 quarters) instead of text.
- **Encode** quarter-filled circles; accent row for the recommended option; column for the deciding criterion.
- **Budget** ≤ 6 × 6.
- **Pitfalls** a table of words; traffic lights with rainbow colors.
- **Build** `s.circle` hairline + `s.ring(..., 0, r, 0, deg)` for partial fills.

### `archetypes`
- **Use when** 3–5 types/personas differ on a common set of traits.
- **Anatomy** each archetype as a small profile on the SAME axes (mini bar or dot profiles), names on top.
- **Encode** shared axes make differences visible; accent = the archetype that matters.
- **Pitfalls** persona cards with stock photos; identical boxes with bullet traits.
- **Build** small multiples of dot profiles (`s.dot` along short scales).

### `trade_off_frontier`
- **Use when** improving one objective costs another; options sit on or inside a frontier.
- **Anatomy** two axes; frontier curve; options as points; the recommended point marked.
- **Encode** distance to frontier = inefficiency; accent = recommended option.
- **Build** `c.linear` for both axes; frontier with `c.line(..., {radius:40})`; points + callouts.

### `dumbbell`
- **Use when** each item has two values (then/now, us/benchmark) and the gap is the story.
- **Anatomy** rows; two dots per row joined by a line; sorted by gap.
- **Encode** dot tone = which value; line length = gap; accent = largest gap.
- **Build** `c.linear({axis:'x'})`, `c.band(keys,{axis:'y'})`; `s.line` + two `s.dot` per row.
