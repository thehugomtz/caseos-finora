# Construction notes — technique, not templates

How to build each grammar family from primitives. Coordinates below are illustrative; always
derive them from the content (counts, values, text lengths) and the 12-column grid.

## General technique

- **Plan first, in a comment**: zones by column span (`P.grid.span(1,7)`), the focal object's
  position, and the reading path. Asymmetry is the default: the focal object rarely sits dead centre.
- **Measure, then place**: after creating HTML labels, read their boxes (`s.box(el)`) to place
  the next thing (connectors, brackets, callouts) — never guess text heights.
- **Direct labels** sit 10–16px from their mark; leaders only when space forces it.
- **Label collisions**: alternate above/below on dense axes; nudge by measuring neighbours;
  shorten text before shrinking type.
- **Magnitude by area**: circle radius `r = k·√value` (never radius ∝ value).
- **One accent object per composition** (plus its label). Context in `ink-4`/`ink-3`.
- **Knockout** connector labels (`knockout:true`) so lines pass behind text.

## Relationships / systems

**Concentric system (full or partial rings).** Centre off-grid-centre for asymmetry (e.g.
`cx = P.grid.col(4)`, or anchored to the left edge with half rings `a0=0, a1=180`). Radii step by
a constant (e.g. 120/230/340) so ring *bands* read as layers. Fill rings from the outside in so
inner rings paint on top: `s.ring(cx,cy,r_in,r_out,0,360,{fill:'ink-5'})`. Ring names: labels
placed on the band at a fixed angle (`P.geo.polar(cx,cy,(r0+r1)/2, 300)`), `anchor:'mc'`.
Data markers: circles sized by `√value`, placed inside the band where they originate, with
callouts to an annotation column on the right.

**Hub and spoke.** `const pts = P.geo.around(n, cx, cy, r, -60, 240)` for a partial fan leaving
room for text; label anchor by angle: right half → `ml`, left half → `mr`, top → `bc`, bottom → `tc`.

**System map.** Place variables on a loose circle; `s.connect(a, b, {route:'arc', bend:0.18})`;
put `+`/`−` as small labels near arrowheads (`labelAt: 0.85`).

## Process / motion

**Converging paths.** Lane labels as HTML at fixed y (distribute with `P.geo.distribute(n, top, bottom)`);
stages as dots along each lane; connect lane ends to the outcome with `route:'curve'`,
spreading `toAt` (0.3/0.5/0.7) so arrowheads don't pile up; outcome as `.metric` + label, `data-focal`.

**Funnel.** `const wScale = v => minW + (maxW-minW) * v / max`; stage i:
`s.path(P.geo.trapezoid(cx, y_i, w(v_i), w(v_{i+1}), h), {fill: i===worst?'accent':'ink-5', stroke:null})`;
stage names left-aligned in a column, volumes right, conversion % as small labels in the gaps.

**Swimlane with time.** `const x = s.chart({x:X0, y:Y0, w:W, h:H}).linear([0, months], {axis:'x'})`;
lane rules `s.line(X0-?, laneY, X0+W, laneY, {stroke:'rule', w:1.5})`; lane names in a left column;
work segments `s.line(x(t0), y, x(t1), y, {stroke:'ink', w:12, cap:'butt'})`; waits
`{stroke:'accent', w:3, dash:'dash'}` with duration labels above; handoffs
`s.connect([x(t),y1],[x(t),y2],{route:'straight', w:1.5})`; time axis ticks at the bottom.
Bracket the waits (`s.bracket`) with the total wait time as the focal annotation.

**Timeline.** True time scale; alternate labels above/below; phases as thin `surface` bands
behind the axis; today marker as a vertical `dash` line.

**Flywheel / loop.** Nodes with `P.geo.around(n, cx, cy, r)`; arcs between consecutive nodes:
`s.path(P.geo.arc(cx, cy, r, a_i + pad, a_{i+1} - pad), {arrow:'end', tone:'ink-3'})` where
`pad` leaves room for the node label.

## Logic

**Issue tree / driver tree.** Levels as columns (`P.grid.col(1)`, `col(5)`, `col(9)`); children
distributed vertically around their parent's y; `s.connect(parent, child, {route:'elbow',
fromSide:'right', toSide:'left', mid: parentBox.r + 40})` — shared `mid` per level so the elbows
form one clean spine. Operators (× ÷ +) as small labels on the spine.

**Pyramid (Minto).** Governing thought as `.lead`/`.label` across 8–10 columns; arguments on one
row beneath; `s.bracket` or elbow connectors from arguments up to the thought. Use a triangle
only when magnitudes narrow.

## Comparison

**2×2.** Axes as two hairlines crossing at the midpoint with arrows at the positive ends; axis
titles at the ends (`caps`); quadrant names muted in the corners; items as dots + labels; the
target quadrant gets a very light `accent-soft` rect behind it (the only fill).

**Before/after.** Write the structure once as a function inside `P.draw` and call it with two
origins and two states. Same scale, same positions; accent only on changed elements.

**Dumbbell / slope.** Band scale for rows, linear for values; sort by gap; labels at the ends.

## Economics

**Waterfall / bridge / value leakage.** `c.waterfall(steps, {x, y})`. Totals in `ink`,
deltas in `ink-4`, the focal step `accent` (set `tone` on that step). A total that is *potential*
(identified, planned, on paper) is drawn as an outline: `{total: true, outline: true}`. De-emphasise
non-focal steps with `opacity` (e.g. 0.45) and put dark labels on them. Running-total connectors are
solid 1px (`connectorDash` only if dashes don't already mean "target" in the deck). Value labels above bars
(`s.label(bar.cx, bar.top - 10, …, {anchor:'bc'})`); category labels under the axis, written as
causes. Callout from the focal bar to an annotation column.

**Stacked decomposition.** Cumulative `x` over a 100% scale; segments as `s.rect`; label inside if
wide enough else a callout; focal segment in accent, others in `ink-4/ink-5` shades.

## Operating model

**Layered architecture.** Layers as rows separated by hairlines (not boxes); a consistent column
structure across layers: name (cols 1–3) · what it does (4–7) · owner / cadence (8–9) · metric or
value (10–12). Flow arrows in the left margin connecting layers. New/missing layer: accent rule +
accent name, or a dashed outline around that row only.

**Operating cadence.** Concentric hairline rings (weekly inner → quarterly outer), ritual markers
on each ring via `P.geo.polar`, labels outside via callouts.

## Evidence

**Annotated chart.** Chart ≥ 55% of canvas. Gridlines `rule`, 3–5 ticks, no chart border.
Gray series + one accent series/bar. `c.annotate` at the exact data point with a 1–2 sentence
"so what". Axis labels `label-sm`. Source in the footer.

**Hero metric.** `.metric` at 180–260px on columns 1–7; unit in `<span class="unit">` (0.42em) and
`white-space: nowrap` — a hero number must never wrap (QA: `metric-wraps`); the meaning line in
`.lead`; comparison as a small bar pair or "vs" label; keep the right side empty or with one
supporting mini-visual.

## Editorial

**Statement.** `.statement` on columns 1–10 starting around y = 300–360 (not vertically centered);
kicker above; one supporting element at most (a hairline that breaks, a small fact at the
bottom-left). Accent on at most one phrase.
