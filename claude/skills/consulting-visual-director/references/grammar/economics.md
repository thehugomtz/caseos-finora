# Economics

### `waterfall`
- **Use when** a total is built (or eroded) by ordered components, and the size of each step is the point.
- **Anatomy** first total bar, floating delta bars, final total bar; dotted connectors between tops;
  values on each bar; category labels below.
- **Encode** color by sign (muted for normal steps, accent for the step that matters; `neg` only
  if sign is the message); total bars in ink.
- **Focal** the largest (or most surprising) step.
- **Budget** 4–8 steps; one callout explaining the focal step.
- **Pitfalls** red/green for every step; a legend; unlabeled bars; unsorted steps when order is arbitrary.
- **Build** `c.band` + `c.linear`, `c.waterfall(steps, {x, y})` returns geometry for callouts.

### `bridge`
- **Use when** explaining the change of a metric between two periods/scenarios (price, volume, mix, cost…).
- **Anatomy** as waterfall with start = period A and end = period B; drivers in between.
- **Encode** positive/negative drivers distinguished by tone; accent the driver the message is about.
- **Focal** the dominant driver of the change.

### `contribution_tree`
- **Use when** a total splits hierarchically into contributors (business → units → products) and
  *where the value concentrates* matters.
- **Anatomy** tree left→right with values; bar lengths per node on a shared scale.
- **Encode** bar length = contribution; accent = concentration (e.g. 2 nodes = 70%).
- **Build** elbow connectors + `c.bars(orient:'h')` inline with each node.

### `stacked_decomposition`
- **Use when** the mix/composition of a total (or its change) is the message.
- **Anatomy** 100% stacked bars or a single segmented bar with direct labels; ≤ 5 segments.
- **Encode** ordered segments; the focal segment in accent, the rest neutral shades.
- **Pitfalls** rainbow segments with a legend; > 5 segments (group the tail as "Otros").
- **Build** `s.rect` per segment from cumulative scale; labels inside if width > 90px, else callout.

### `unit_economics_tree`
- **Use when** LTV/CAC-style economics: the relationship between acquisition cost, revenue per
  unit, margin and retention is the point (not the metrics as a list).
- **Anatomy** `LTV/CAC` (or payback) as the root; `LTV = ARPU × margin × lifetime (1/churn)`; `CAC = spend / new customers`; values at each node; the lever highlighted.
- **Encode** operators on junctions; accent = the lever the recommendation pulls; small deltas vs target.
- **Focal** the ratio and the lever that moves it.
- **Pitfalls** five KPI cards (CAC, LTV, churn, ARPU, ARR) with no arithmetic between them.

### `value_leakage`
- **Use when** potential value is lost at successive stages ("we capture only 24% of what we
  identify") and the point is *where it leaks*.
- **Anatomy** a descending bridge from potential to captured, each leak a labelled drop; or a
  horizontal pipe with leaks whose size = value lost.
- **Encode** leak size = value lost; accent = largest leak; captured value in ink as the endpoint.
- **Focal** the largest leak (or the small captured bar vs the big potential).
- **Build** `c.waterfall` with negative steps; leak categories written as causes, not as stage names only.

### `marimekko`
- **Use when** two dimensions of a market/portfolio matter at once (segment size × share within).
- **Anatomy** variable-width columns (width = segment size), stacked shares inside.
- **Encode** width and height both quantitative; accent our share or the white space.
- **Pitfalls** too many segments; labels that don't fit — use callouts.
- **Build** cumulative x from sizes; `s.rect` per cell; labels only on cells > 80×40px.
