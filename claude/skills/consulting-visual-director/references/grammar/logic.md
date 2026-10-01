# Logic / argument

### `pyramid`
- **Use when** a governing thought is supported by 2–4 arguments, each supported by evidence
  (Minto) — or when something genuinely narrows with rank/volume (only then a triangle).
- **Anatomy** governing thought on top as a sentence; key-line arguments below, aligned; evidence
  under each. A literal triangle only for narrowing magnitudes.
- **Encode** vertical position = level of abstraction; thin connectors from each argument up to
  the thought; accent on the argument that carries the decision.
- **Focal** the governing thought.
- **Budget** 1 thought (≤ 20 words), 2–4 arguments (≤ 12 words), ≤ 3 evidence lines each.
- **Pitfalls** a triangle cut into colored slices with labels (the "Maslow" cliché); arguments that overlap (not MECE).
- **Build** HTML text blocks on the grid; `s.bracket` or elbow connectors from arguments to the thought; evidence in `.label-sm`.

### `issue_tree`
- **Use when** a question is broken into MECE sub-questions or hypotheses (diagnostic, "why" or
  "how" tree).
- **Anatomy** root question left; branches to the right in 2–3 levels; leaves carry status
  (supported / rejected / open) or data.
- **Encode** x = depth; status by marker (filled / hollow / crossed); accent = the branch that
  explains most of the answer.
- **Focal** the winning branch.
- **Budget** ≤ 3 levels; ≤ 12 leaves; ≤ 8 words per node.
- **Pitfalls** boxes around every node; unbalanced depth hiding MECE errors.
- **Build** nodes as HTML text with left alignment per level column (`P.grid.col`); `s.connect(parent, child, {route:'elbow', fromSide:'right', toSide:'left', mid})` with a shared `mid` per level so elbows align.

### `decision_tree`
- **Use when** choices with uncertain outcomes are compared on expected value or risk.
- **Anatomy** decision node → options → chance nodes → outcomes with probabilities and payoffs.
- **Encode** branch weight = probability; payoff right-aligned; accent = recommended path.
- **Build** squares for decisions, circles for chance (`s.rect`, `s.circle`), elbow connectors, labels on connectors.

### `causal_chain`
- **Use when** A causes B causes C causes the observed outcome; root-cause arguments.
- **Anatomy** links left→right (or top→bottom) with the mechanism written on each arrow.
- **Encode** the root cause in accent; evidence under each link; dashed = hypothesized link.
- **Focal** the root cause (the leftmost node), not the symptom.
- **Pitfalls** chains of boxes with "leads to" arrows and no mechanism.
- **Build** nodes as short sentences; `x-connect` with `label` carrying the mechanism.

### `hierarchy`
- **Use when** levels of authority, abstraction or priority (org levels, principle → policy → practice).
- **Anatomy** levels as rows; items per level; connectors up.
- **Encode** row = level; accent = where the change happens.
- **Pitfalls** default org-chart boxes; hierarchy used for things that are actually sequences.

### `driver_tree`
- **Use when** a metric is the result of drivers combined by arithmetic (× + − ÷) and the point
  is *which driver moves the result*.
- **Anatomy** output metric left (or top); operators on the connectors; drivers with current value,
  target and sensitivity.
- **Encode** operator glyphs (×, +, ÷) on junctions; driver tile emphasis = sensitivity; accent =
  the driver with the largest impact; small bars for deltas.
- **Focal** the high-leverage driver.
- **Budget** ≤ 3 levels; ≤ 10 drivers.
- **Pitfalls** listing metrics (CAC, LTV, churn…) without the arithmetic that links them.
- **Build** elbow connectors with operator labels placed at the junction (`s.label(... '×')`); values `.num`.

### `nested_structure`
- **Use when** scope contains scope (portfolio ⊃ programs ⊃ projects; market ⊃ segment ⊃ niche).
- **Anatomy** nested rectangles or brackets; labels in the top-left of each container.
- **Encode** containment = inclusion; size = share if data exists (then it becomes a treemap).
- **Pitfalls** nesting used for sequence.
- **Build** hairline `s.rect` containers with increasing insets; labels as `.caps` at top-left.
