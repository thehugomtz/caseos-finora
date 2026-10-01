# Relationships / systems

### `ecosystem_map`
- **Use when** several actors exchange value (money, data, services, trust) and the point is *who
  depends on whom* or *where the value pools*.
- **Anatomy** actors as labelled nodes placed by role (e.g. supply left, demand right, platform
  center); flows as directed connectors labelled with what moves.
- **Encode** node size = economic weight; connector weight = volume; accent = the flow or actor the
  message is about; dashed = missing/potential flow.
- **Focal** the value pool or the broken/missing flow.
- **Budget** 5–9 actors, ≤ 12 flows, flow labels ≤ 4 words.
- **Pitfalls** every actor the same size; arrow spaghetti; icons instead of names.
- **Variants** value_network, platform_map.
- **Build** place nodes on a loose grid; `s.connect(a,b,{route:'curve', label})`; knockout labels on flows; size nodes with circles (`s.circle`) + HTML labels beside, not inside.

### `system_map`
- **Use when** variables influence each other and loops explain the behaviour (reinforcing
  growth, balancing limits, vicious circles).
- **Anatomy** variables as short noun phrases; causal connectors with polarity (+/−); loop markers
  (R/B) in the loop's centre.
- **Encode** connector color: accent for the loop the message is about; dash for delays; polarity
  as small "+"/"−" labels at the arrowhead.
- **Focal** the dominant loop (thicker, accent) — other loops in gray.
- **Budget** 6–10 variables, 1 focal loop, ≤ 2 secondary loops.
- **Pitfalls** diagrams that need a legend to read; mixing actors with variables.
- **Variants** causal_loop, vicious_circle.
- **Build** variables placed around the loop's circle (`P.geo.around`); `route:'arc'` connectors with `bend` ~0.2; loop label as a small circle glyph + letter.

### `hub_and_spoke`
- **Use when** one entity coordinates, feeds or is fed by many (a platform, a central team, a
  data core); the point is centrality or dependency on the hub.
- **Anatomy** hub in the optical centre (or left-of-centre for asymmetry), spokes to 4–8 satellites
  placed on an arc or circle; labels outside the ring.
- **Encode** spoke weight = intensity; satellite size = importance; direction = who serves whom.
- **Focal** the hub (or the one spoke that is broken).
- **Budget** 4–8 spokes; satellite labels ≤ 5 words + optional metric.
- **Pitfalls** perfect radial symmetry with identical satellites = decorative wheel; icons in circles.
- **Variants** partial arc (satellites on a 180° arc, text on the open side), inbound vs outbound.
- **Build** `P.geo.around(n, cx, cy, r, start, sweep)`; `s.connect(hub, sat, {route:'straight', gap:12})`; labels anchored away from centre (`anchor` chosen by angle).

### `network`
- **Use when** many-to-many relationships form clusters, bridges or isolated nodes.
- **Anatomy** nodes grouped in clusters; edges; highlight the bridge or the gap.
- **Encode** clustering by position; node size = degree/importance; accent = bridge/outlier.
- **Focal** the structural insight (the bridge, the isolated cluster, the bottleneck).
- **Budget** ≤ 25 nodes shown; label only the nodes that matter.
- **Pitfalls** hairball; labelling every node.
- **Build** hand-placed cluster centres; nodes around them; thin `ink-4` edges, accent for the ones that matter.

### `concentric_system`
- **Use when** things nest: a core is surrounded by layers that contain, enable or constrain it
  (technology inside operations inside institution; product inside service inside ecosystem).
- **Anatomy** 2–4 rings around a core (full circles, or half/quarter rings anchored to an edge to
  free space for labels); ring names on the rings; data overlaid as markers.
- **Encode** distance from core = distance from the thing that creates value; ring tone from
  dark (core) to light (outer) or the reverse; markers sized by magnitude placed in the ring where
  they originate.
- **Focal** the ring or marker the message is about (e.g. where most value is lost).
- **Budget** ≤ 4 rings; 3–8 markers; ring labels ≤ 3 words + 1 descriptor line.
- **Pitfalls** equal-weight rings that say nothing; bullets inside rings; confusing nesting with
  sequence.
- **Variants** half_concentric (arcs anchored to the left edge), onion_with_data, target.
- **Build** `s.ring(cx, cy, r0, r1, a0, a1, {fill})` per layer; markers with `s.circle` sized by `Math.sqrt(value)`; labels via `s.callout` leaders to markers; ring names with `s.label` placed on the ring band.

### `capability_map`
- **Use when** the point is *which capabilities exist, which are missing or weak*.
- **Anatomy** capability domains as columns or bands; capabilities as short labels inside; a
  heat encoding for maturity/gap.
- **Encode** fill intensity or a dot scale = maturity; accent outline = priority gaps.
- **Focal** the gaps that block the strategy (not the full map).
- **Budget** 12–30 capabilities; 1–3 words each.
- **Pitfalls** a wall of equal boxes (it becomes a card grid — the gaps must dominate); rainbow heat.
- **Variants** capability_heatmap, maturity_dot_matrix.
- **Build** thin-ruled bands (`s.line`) rather than boxes; maturity as 1–4 filled dots (`s.dot`), gaps with accent ring.

### `dependency_map`
- **Use when** A cannot happen without B: prerequisites, critical path, sequencing constraints.
- **Anatomy** items left→right by earliest start; dependency arrows; the critical path thickened.
- **Encode** horizontal position = order/time; accent path = critical chain; dashed = soft dependency.
- **Focal** the critical path or the blocking dependency.
- **Budget** 6–14 items.
- **Pitfalls** crossings; showing every dependency.
- **Build** `route:'elbow'` connectors; rows by workstream; `x-connect` between items with `tone="accent" w="3"` on the critical path.

### `interconnected_model`
- **Use when** 2–3 domains overlap and the value lives in the intersection (e.g. desirability ×
  feasibility × viability).
- **Anatomy** overlapping circles/areas; the intersection named and highlighted.
- **Encode** overlap = shared capability; accent only on the intersection.
- **Focal** the intersection.
- **Budget** 2–3 sets; one label per set + one for the intersection.
- **Pitfalls** Venn with text crammed into every region; decorative overlaps that are not intersections.
- **Build** circles with `fillOpacity` 0.08–0.15 and hairline stroke; intersection label with callout.
