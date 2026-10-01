# Visual grammar — how to read an entry

This is a vocabulary, not a template library. Each entry describes a **composition**: a way of
arranging objects so that geometry enacts a relationship. The renderer builds it from
primitives, so every instance is drawn for its own content.

Entry format:

- **Use when** — the semantic trigger (relationship + evidence).
- **Anatomy** — the objects and how they are arranged.
- **Encode** — what position, size, color, line and containment mean in this composition.
- **Focal** — the default focal point (override when the message says otherwise).
- **Budget** — sensible limits for objects and words.
- **Pitfalls** — how this composition goes wrong.
- **Variants** — related compositions.
- **Build** — primitive-level technique hints for `html-slide-renderer`.

Families and files:

| Family | File | Compositions |
|---|---|---|
| Relationships / systems | `relationships.md` | ecosystem_map, system_map, hub_and_spoke, network, concentric_system, capability_map, dependency_map, interconnected_model |
| Process / motion | `process.md` | funnel, journey, pipeline, swimlane, stage_gate, flywheel, loop, timeline, branching_journey, converging_paths, diverging_paths, value_stream |
| Logic / argument | `logic.md` | pyramid, issue_tree, decision_tree, causal_chain, hierarchy, driver_tree, nested_structure |
| Comparison | `comparison.md` | before_after, from_to_shift, side_by_side_contrast, spectrum, two_by_two, harvey_matrix, archetypes, trade_off_frontier, dumbbell |
| Economics | `economics.md` | waterfall, bridge, contribution_tree, stacked_decomposition, unit_economics_tree, value_leakage, marimekko |
| Operating model | `operating-model.md` | layered_architecture, capability_stack, governance_architecture, operating_cadence, decision_rights_matrix, feedback_loop, control_tower |
| Evidence / analytics | `evidence.md` | annotated_chart, hero_metric, slope, scatter, bubble_matrix, cohort_chart, small_multiples, ranked_contribution, spotlight_chart, dot_plot |
| Editorial | `editorial.md` | single_big_statement, dominant_visual_plus_annotation, split_narrative, asymmetric_composition, visual_metaphor, full_slide_framework, progressive_build, voice_quote |

Hybrids are encouraged when the message needs them — name them explicitly
(e.g. `concentric_system + leak_markers`, `swimlane + time_axis`, `layered_architecture + cadence_loop`)
and state which part is focal.
