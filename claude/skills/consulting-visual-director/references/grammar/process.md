# Process / motion

### `funnel`
- **Use when** volume shrinks through ordered stages and the point is *where* it shrinks most.
- **Anatomy** stages stacked top→bottom (or left→right) with width proportional to volume;
  stage names on one side, volumes and conversion rates on the other.
- **Encode** width = volume (true scale, never decorative tapering); accent = the stage with the
  biggest drop; conversion % between stages as annotations on the gap.
- **Focal** the worst conversion step.
- **Budget** 3–7 stages; one annotation explaining the focal drop.
- **Pitfalls** decorative funnels with equal steps; 3D cones; percentages that don't add up.
- **Variants** horizontal_funnel, funnel_by_segment (small multiples), leaky_funnel.
- **Build** `P.geo.trapezoid(cx, y, wTop, wBot, h)` per stage with widths from a linear scale; gaps of 8–12px; labels left, numbers right, drop annotation with `s.callout`.

### `journey`
- **Use when** a customer/user/employee moves through steps and the point is *where the
  experience breaks or wins*.
- **Anatomy** a horizontal path with stages; moments of truth marked; an emotion/effort curve or
  a pain marker row beneath.
- **Encode** position = order; curve height = sentiment/effort; accent markers = pain points.
- **Focal** the moment of truth that fails.
- **Budget** 5–8 stages; ≤ 3 pain annotations.
- **Pitfalls** icon + caption per stage in identical boxes; no sense of time or friction.
- **Build** a baseline `s.line`; stage ticks + labels; sentiment as `c.line` with `radius`; pains with `s.dot` + `s.callout`.

### `pipeline`
- **Use when** work items/opportunities sit in stages with counts and flow rates.
- **Anatomy** stage columns along a line, count at each stage, arrows with conversion or dwell time.
- **Encode** bar/number size = WIP; arrow label = conversion; accent = bottleneck (highest dwell).
- **Focal** the bottleneck.
- **Build** stage numbers as `.metric`-scaled labels; `s.connect(..., {route:'straight', label:'38% · 21 días'})`.

### `swimlane`
- **Use when** several actors hand work to each other and the point is *handoffs, waits or
  ownership gaps*.
- **Anatomy** one horizontal lane per actor (thin rules, not boxes); activities as segments on
  lanes; handoff connectors between lanes; optional time axis at the bottom.
- **Encode** x = time (true scale if durations matter); segment length = duration; hatched or
  accent gaps = waiting; vertical connectors = handoffs.
- **Focal** the waits/handoffs that dominate lead time.
- **Budget** 3–6 lanes; ≤ 12 activities; labels ≤ 4 words.
- **Pitfalls** a flowchart of boxes; lanes as filled bands that shout louder than content.
- **Variants** swimlane + time_axis, service_blueprint.
- **Build** lane rules with `s.line` at fixed y; activities as `s.rect` (height 10–16px) or thick `s.line` (w 10); waits as dashed accent lines with duration labels; handoffs with `s.connect(route:'elbow')`.

### `stage_gate`
- **Use when** a process has decision points with criteria and the point is *what must be true
  to pass*.
- **Anatomy** stages along a line; gates as vertical markers (diamonds/bars) with criteria below.
- **Encode** gate markers in ink; the failing/most-restrictive gate in accent.
- **Focal** the gate that blocks.
- **Build** stage labels above the line, gate criteria below in `.label-sm`; gate glyph via small rotated square (`s.poly`).

### `flywheel`
- **Use when** a reinforcing cycle creates momentum; the point is *what feeds what* and where to push.
- **Anatomy** 3–6 nodes on a circle; curved arrows in one direction; the push point marked.
- **Encode** arrow direction = causality; accent = where the investment enters.
- **Focal** the entry point or the weakest link.
- **Pitfalls** a circle of icons with no causal meaning; more than 6 nodes.
- **Build** `P.geo.around`; `s.connect(a, b, {route:'arc', bend:0.18})`; centre label for the outcome that compounds.

### `loop`
- **Use when** a control/learning loop (sense → decide → act → learn) or a feedback mechanism
  is the idea.
- **Anatomy** 3–5 steps on a ring or rounded rectangle path; one input and one output edge.
- **Encode** the step that is missing today in accent or dashed.
- **Focal** the missing/broken step.
- **Build** ring path with arrowheads (`s.path(P.geo.arc(...), {arrow:'end'})`); steps as labels outside the ring.

### `timeline`
- **Use when** dated events or a roadmap; the point is *when* and *what changes when*.
- **Anatomy** a time axis; events as ticks with labels; phases as bands; today marker.
- **Encode** x = true time; phase bands light; milestones as dots; accent = decision date or inflection.
- **Focal** the milestone or phase the message is about.
- **Budget** ≤ 10 events; labels ≤ 6 words.
- **Pitfalls** equal spacing for unequal time; chevrons for phases.
- **Build** `c.linear([t0,t1],{axis:'x'})`; alternate labels above/below to avoid collisions; phases as `s.rect` with `surface` fill.

### `branching_journey`
- **Use when** a path splits at decision points into different outcomes.
- **Anatomy** trunk → branches with conditions on the fork; outcomes at the ends.
- **Encode** branch weight = share of cases; accent = the branch the message recommends or warns about.
- **Build** `s.connect(fork, outcome, {route:'curve'})`; condition labels as knockout connector labels.

### `converging_paths`
- **Use when** distinct routes/motions/segments reach the same outcome; the point is how
  different the routes are, or that the destination is shared.
- **Anatomy** 2–4 lanes left→right, each with its own stages (ticks/nodes) and a KPI; lanes
  bend into one outcome on the right.
- **Encode** lane length/number of stages = effort/time; node markers = measurement points;
  outcome size = value; accent = the lane that differs or the outcome.
- **Focal** the shared outcome (or the one different lane).
- **Budget** ≤ 4 lanes, ≤ 6 stages each, one KPI annotation per lane.
- **Pitfalls** three cards with arrows to a box; lanes forced equal.
- **Variants** sankey_lite (width = volume), braided_paths.
- **Build** lane labels as HTML at fixed y; stage ticks via `s.line`/`s.dot`; `s.connect(laneEnd, outcome, {route:'curve', toAt})` spreading `toAt` so arrows land separately.

### `diverging_paths`
- **Use when** one source produces several distinct results (one platform → products; one
  decision → consequences).
- **Anatomy** mirror of converging_paths: source left, fan-out to outcomes.
- **Build** same technique with `fromAt` spread on the source side.

### `value_stream`
- **Use when** the point is *lead time vs work time*: most of the elapsed time is waiting.
- **Anatomy** a time ruler; work segments solid, wait segments hatched/dashed; totals at the end.
- **Encode** length = duration (true scale); accent = the longest waits; summary "x% of time is waiting".
- **Focal** the wait share or the single longest wait.
- **Build** segments with `s.line(w:14)` solid vs `dash:'dash'`; bracket over the waits with the total (`s.bracket(..., {side:'top'})`).
