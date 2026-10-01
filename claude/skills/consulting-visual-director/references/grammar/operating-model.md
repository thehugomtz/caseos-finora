# Operating model

### `layered_architecture`
- **Use when** capabilities or functions build on each other (data → models → decisions →
  action; observe → decide → enable → adopt), and the point is *which layer is missing, weak or new*.
- **Anatomy** 3–5 horizontal layers read bottom-up (foundation at the bottom) or top-down (from
  observation to action); each layer = name + what it does + owner/metric aligned in columns;
  connectors or arrows showing what flows up/down.
- **Encode** vertical order = dependency; a shared column structure (name | role | owner | metric)
  makes layers comparable; accent = the new/missing layer; dashed outline = does not exist today.
- **Focal** the missing or new layer.
- **Budget** ≤ 5 layers; ≤ 14 words per layer on canvas.
- **Pitfalls** a stack of identical boxes (QA flags `box-stack`): layers must show what flows
  between them, their widths or ownership must mean something, or it is just a list in boxes.
- **Variants** layered_architecture + cadence_loop; stair_stack (each layer offset = maturity).
- **Build** hairline separators (`s.line`) instead of filled boxes; layer names in `.label`; right-hand column for owner/metric; `s.connect` arrows on the left margin to show flow direction.

### `capability_stack`
- **Use when** each layer contains several capabilities with maturity/ownership.
- **Anatomy** layers as bands; capabilities inside as text chips; maturity dots.
- **Encode** dot count = maturity; accent outline = capability to build.
- **Pitfalls** turns into a wall of chips; keep ≤ 5 per layer and emphasize the gaps.

### `governance_architecture`
- **Use when** forums, committees and decision rights must be clear.
- **Anatomy** forums arranged by level (strategic → tactical → operational) with frequency,
  chair and decisions; escalation paths as connectors.
- **Encode** level = vertical; cadence as a small label; accent = new forum or the decision that moves.
- **Pitfalls** an org chart of boxes with no decision content.
- **Build** forum names `.label`, decisions `.label-sm`; `s.connect(route:'elbow', dash:'dash')` for escalations.

### `operating_cadence`
- **Use when** the rhythm (weekly/monthly/quarterly) of forums and rituals is the model.
- **Anatomy** concentric rings (inner = fast cadence, outer = slow) or a timeline strip over 13 weeks
  with ticks per ritual.
- **Encode** ring radius = cycle length; markers = rituals; accent = the new ritual.
- **Build** `s.ring` hairlines; markers with `P.geo.polar`; labels outside rings via callouts.

### `decision_rights_matrix`
- **Use when** who decides / recommends / executes must be explicit (RACI-like) without a text table.
- **Anatomy** decisions as rows, roles as columns, dot glyphs: filled = decides, ring = recommends, small = informed.
- **Encode** glyph type = role; accent row = contested decision.
- **Budget** ≤ 8 decisions × 6 roles.

### `feedback_loop`
- **Use when** an organizational loop (measure → review → decide → act) closes or is broken.
- **Anatomy** as `loop` with owners and cadence on each step.
- **Focal** where the loop is open today.

### `control_tower`
- **Use when** a central unit monitors signals from many units and dispatches decisions.
- **Anatomy** tower/center with incoming signal lines and outgoing decision lines; units around.
- **Encode** incoming (thin, muted) vs outgoing (ink/accent); accent = the signal that triggers action.
- **Pitfalls** a hub with icons; show the signals and decisions in words.
