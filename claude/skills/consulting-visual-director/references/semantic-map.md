# Semantic map — relationship → composition

The composition is derived from the **verb** of the idea, not from how many items it has.
Find the verb, then the evidence type, then pick from the grammar. Ids refer to
`grammar/*.md` entries.

## 1. Find the verb

Rewrite the slide message as *subject + relationship verb + object*. Typical verbs:

| Verb | The idea sounds like… |
|---|---|
| **converge** | "different routes lead to the same result", "all roads end in…" |
| **diverge** | "one cause, many effects", "one platform, several products" |
| **sequence** | "first… then… finally", "the path is…", "it takes N steps" |
| **filter / attrite** | "we lose X% at each stage", "of 100 leads, 3 close" |
| **leak** | "value is lost between A and B", "we capture only X% of the potential" |
| **cycle / reinforce** | "more X brings more Y which brings more X", "it compounds" |
| **cause** | "X happens because of Y", "the root cause is…" |
| **decompose (+)** | "X is made of A + B + C", "where does the total come from" |
| **decompose (×)** | "X = A × B / C", "what drives X" |
| **nest / contain** | "A lives inside B", "the core is surrounded by…" |
| **depend / enable** | "A needs B first", "without B, A fails" |
| **layer / stack** | "each level builds on the one below", "from data to decision" |
| **compare** | "A vs B", "we are behind/ahead", "the gap is…" |
| **transform** | "from today to tomorrow", "we must shift from X to Y" |
| **position / classify** | "each item sits somewhere on two dimensions", "types of…" |
| **rank / prioritize** | "three of them matter most", "the long tail doesn't" |
| **trend** | "X has been rising/falling since…", "the inflection was…" |
| **bridge** | "from A last year to B this year, because of…" |
| **distribute / share** | "X% of the total is…", "the mix is…" |
| **correlate** | "the more X, the more/less Y" |
| **trade off** | "gaining X costs Y", "we cannot maximize both" |
| **govern / coordinate** | "who decides what, when", "the forum structure is…" |
| **center / hub** | "everything goes through X" |
| **branch / choose** | "the options are…, and each leads to…" |
| **emphasize** | "the one thing to remember is this number / this sentence" |

If two verbs compete, the slide carries two ideas: split it, or make one the focal point and the
other an annotation.

## 2. Verb → candidate compositions

| Verb | Primary | Strong alternatives | Lazy default to avoid |
|---|---|---|---|
| converge | `converging_paths` | `hub_and_spoke` (inbound), `funnel` (if volumes), `sankey_lite` | three cards with arrows to a box |
| diverge | `diverging_paths` | `issue_tree`, `hub_and_spoke` (outbound) | bullet list of effects |
| sequence | `timeline`, `journey` | `swimlane` (actors), `stage_gate` (decisions), `pipeline` (volumes), `value_stream` (work vs wait) | numbered cards / chevron row |
| filter / attrite | `funnel` | `value_leakage`, `pipeline`, `waterfall` (money) | pie chart; stacked cards |
| leak | `value_leakage` | `waterfall`, `funnel` | a table of losses |
| cycle / reinforce | `flywheel` | `loop`, `system_map` | circle of icons |
| cause | `causal_chain` | `system_map`, `issue_tree` (why-tree), `driver_tree` | "reasons" bullets |
| decompose (+) | `waterfall`, `contribution_tree` | `stacked_decomposition`, `marimekko`, `treemap` | pie with 8 slices |
| decompose (×) | `driver_tree` | `unit_economics_tree` | formula in a text box |
| nest / contain | `concentric_system` | `nested_structure`, `layered_architecture` | three boxes in a row |
| depend / enable | `dependency_map` | `layered_architecture`, `capability_stack`, `critical_path` | checklist |
| layer / stack | `layered_architecture` | `capability_stack`, `pyramid` (only if importance/volume narrows) | stack of identical boxes with no relation |
| compare (2 things) | `side_by_side_contrast` | `before_after`, `dumbbell`, `slope` | two cards |
| compare (n × criteria) | `harvey_matrix` | `bubble_matrix`, `small_multiples`, `dot_matrix` | a text table |
| transform | `before_after` | `from_to_shift`, `spectrum` (with movement arrows) | two columns of bullets |
| position / classify | `two_by_two` | `spectrum`, `scatter`, `archetypes` | a list with tags |
| rank / prioritize | `ranked_contribution` | `dot_plot`, `pareto` | alphabetical or unsorted bars |
| trend | `annotated_chart` (line) | `spotlight_chart`, `slope`, `small_multiples` | a chart with no annotation |
| bridge | `bridge` | `waterfall`, `slope` | two big numbers side by side |
| distribute / share | `stacked_decomposition` (100%) | `marimekko`, `waffle`, `treemap` | pie with > 4 slices |
| correlate | `scatter` (annotated) | `bubble_matrix`, `connected_scatter` | dual-axis chart |
| trade off | `trade_off_frontier` | `spectrum`, `two_by_two` | pros/cons list |
| govern / coordinate | `governance_architecture` | `operating_cadence`, `decision_rights_matrix`, `control_tower` | org chart of boxes |
| center / hub | `hub_and_spoke` | `concentric_system`, `control_tower` | box in the middle, cards around |
| branch / choose | `decision_tree` | `branching_journey`, `options_frontier` | three option cards |
| emphasize | `hero_metric`, `single_big_statement` | `dominant_visual_plus_annotation` | a chart for one number |

## 3. Evidence type narrows the choice

- **One number** → `hero_metric`; never a chart for a single value. Add the comparison that
  gives it meaning (vs target, vs last year, vs peers) as a secondary element.
- **Series over time** → line or bars with the inflection annotated (`annotated_chart`);
  many series → `spotlight_chart` or `small_multiples`, never a spaghetti chart.
- **Parts of a whole** → `waterfall` if the order of components matters, `stacked_decomposition`
  if the mix matters, `marimekko` if two dimensions matter.
- **Ranked set** → sorted horizontal bars with the cut-off annotated.
- **Two variables** → `scatter` with quadrant or trend annotation.
- **Structure / system** → systems family; the data (if any) is overlaid as size or color on
  the structure (e.g. leak markers sized by value on a concentric system).
- **Process** → process family; time or volume can be encoded in length or width.
- **Qualitative claim** → editorial family, or a framework that makes the claim's logic visible.

## 4. Quick heuristics

- If the source gives you **N parallel items**, ask which of them is *different*. The slide is
  usually about the one that breaks the pattern — make that the focal point and let the others
  be context (spotlight logic applies to frameworks too).
- If the items are **stages**, they have an order → process family. If they are **levels**,
  they have a dependency → layers. If they are **types**, they have dimensions → 2×2/spectrum.
  If they are **drivers**, they combine → tree. If they are **forces**, they interact → system map.
- If the message contains a **number that changes** from A to B, the change is the focal point:
  bridge, slope or before/after — not two separate charts.
- If you need a **legend**, first try direct labels. A legend is a failure of placement.
- **Data overlaid on structure** beats data and structure on separate slides: size markers on a
  map, durations on a journey, values on a tree.
