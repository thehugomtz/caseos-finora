# Evidence / analytics

Charts in an executive deck are arguments, not data dumps: one chart, one claim, and the claim
is written *on* the chart where the data proves it. Consult the `dataviz` skill (if available)
for color and mark specifics; this file decides *which* chart and *what it must say*.

### `annotated_chart`
- **Use when** a series or distribution supports the headline and one or two data features prove it.
- **Anatomy** the chart dominates (≥ 55% of canvas); gridlines minimal; direct labels; 1–2
  annotations with leader lines at the exact data point; a source line.
- **Encode** gray for context, accent for the proof; annotation text states the "so what".
- **Focal** the annotated feature (inflection, gap, outlier).
- **Budget** ≤ 2 annotations of ≤ 18 words; ≤ 12 axis labels.
- **Pitfalls** a legend; a title that repeats the axis names; every series colored.
- **Build** `s.chart(area)`, scales, `c.gridY(y, ticks, {tone:'rule'})`, marks, `c.annotate(x, y, text, {dx, dy})`.

### `hero_metric`
- **Use when** one number carries the message.
- **Anatomy** the number at display scale (160–260px), unit small; one line of meaning below;
  the comparison that makes it meaningful (vs target/last year/peers) as a small secondary element.
- **Encode** scale = importance; accent only on the delta or the number itself, not both.
- **Focal** the number.
- **Pitfalls** four hero numbers in a row (a KPI card grid); numbers without comparison.
- **Build** `.metric` text; secondary comparison as a mini bar or delta label.

### `slope`
- **Use when** several items change between two points in time/scenario and the ranking or
  direction of change matters.
- **Anatomy** two vertical axes; lines connecting item values; labels at both ends.
- **Encode** line tone = gray context, accent = the item(s) in the message.
- **Build** `c.linear` y; `s.line` per item; `s.label` anchored `mr` / `ml` at the ends; nudge labels to avoid collisions.

### `scatter`
- **Use when** the relationship between two variables or the outliers matter.
- **Anatomy** two axes, points, a trend line or quadrant thresholds, annotated outliers.
- **Encode** accent = the points that matter; size only if a third variable is essential.
- **Pitfalls** labelling every point.

### `bubble_matrix`
- **Use when** a portfolio view: two dimensions + size (e.g. attractiveness × ability × revenue).
- **Encode** bubble area (not radius) proportional to value (`r = k·√v`); accent = recommended moves;
  arrows for intended movement.

### `cohort_chart`
- **Use when** retention/behaviour by cohort over time.
- **Anatomy** retention curves (one per cohort, gray, latest in accent) or a triangle heatmap.
- **Focal** the change between old and new cohorts.

### `small_multiples`
- **Use when** the same chart across segments reveals a pattern that one combined chart hides.
- **Anatomy** a grid of identical mini-charts on the SAME scales; the odd one highlighted.
- **Note** this is a grid by construction but NOT a card grid: shared scales make the items
  comparable. Mark the container with `data-qa-allow="card-grid"` only if it uses framed panels.

### `ranked_contribution`
- **Use when** which items matter most (Pareto): sorted bars with a cumulative line or a cut-off.
- **Encode** sorted descending; accent the head; label the cut-off ("top 3 = 72%").

### `spotlight_chart`
- **Use when** many series exist but one tells the story.
- **Anatomy** all series in light gray, the focal series in accent with direct label.

### `dot_plot`
- **Use when** comparing values across many categories precisely (more precise than bars when
  ranges are narrow), or showing ranges/gaps.
- **Build** `c.band(keys, {axis:'y'})` + `s.dot`; hairline guides.
