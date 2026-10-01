# Slide spec schema (the intermediate representation)

One YAML file per slide in `slide-specs/Sxx.yaml`. The storyline brief says *what* the slide
must argue; the spec says *how it will be seen*. The renderer implements the spec literally;
the critic judges the render against it.

```yaml
slide:
  id: S07                       # stable id; used in data-slide and file names
  file: slides/07.html
  role_in_story: "evidence"     # from the storyline brief

  headline: "Un funnel único oculta tres mecanismos de adquisición distintos"   # action title (conclusion)
  kicker: "Medición del funnel"  # optional section/tracker label
  takeaway: "Finora debe medir cada acquisition motion con una lógica diferente."  # what the audience must retain
  question: "¿Cómo debería medirse el funnel?"

  relationship: "three motions CONVERGE on one economic outcome, via different paths"
  evidence_type: framework       # number | series | parts | ranked | two_variable | structure | process | comparison | qualitative

  composition: converging_paths  # grammar id (hybrids: "converging_paths + kpi_annotations")
  family: process                # relationships | process | logic | comparison | economics | operating_model | evidence | editorial
  alternatives_considered:
    - id: side_by_side_contrast
      score: {fidelity: 1, focal: 2, evidence: 2, variety: 2, risk: 0}
      rejected_because: "compares the motions but hides that they end in the same outcome"
    - id: funnel_by_segment
      score: {fidelity: 2, focal: 1, evidence: 1, variety: 1, risk: -1}
      rejected_because: "implies volume data we do not have"
  chosen_score: {fidelity: 3, focal: 3, evidence: 2, variety: 2, risk: 0}

  focal_point: shared_outcome    # exactly one object id from `objects`
  visual_hierarchy:              # what the eye must see, in order (conceptual order == visual order)
    1: shared_outcome
    2: the three motions (names)
    3: how the paths differ (length, stages)
    4: per-motion KPIs

  objects:                        # the nouns of the composition
    - id: self_service_path
      kind: path                  # path | node | ring | bar | axis | label | marker | band | bracket | metric | text
      content: "Self-service: signup → activation → paid (9 días)"
    - id: direct_sql_path
      kind: path
      content: "Direct SQL: …"
    - id: assisted_path
      kind: path
      content: "Sales-assisted: …"
    - id: shared_customer_outcome
      kind: metric
      content: "$4.2M ARR nuevo / trimestre"

  encodings:                      # what each visual variable MEANS (unused variables stay neutral)
    x_position: "stage order within each motion"
    path_length: "time to convert (true scale)"
    line_weight: "share of new ARR"
    accent: "the outcome (and nothing else)"
    dash: "stages we cannot measure today"

  annotations:                    # sentences anchored to exact places
    - at: assisted_path
      text: "24% conversión, 61 días: medir por velocidad, no por volumen"
    - at: self_service_path
      text: "3% conversión, 9 días: medir activación, no leads"

  layout_intent:
    grid: "paths on columns 1–8, outcome on columns 9–12"
    reading_path: "left → right, converge at outcome"
    asymmetry: "outcome larger and right-of-centre; whitespace above paths"
    whitespace: "top-right quadrant intentionally empty"

  text_budget: 70                 # max words on canvas (becomes data-word-budget)
  must_show: [diferencias de recorrido, puntos de medición, resultado común]
  avoid:
    - "three cards with bullets"
    - "a table"
    - "four-column grid"
    - "icons per motion"

  data:                            # inline data or a path; charts are drawn from this
    source: "CRM Q2 2026 (ilustrativo)"
    values: []

  notes: |                         # speaker notes: what is said, not shown
    …
  sources: ["CRM Q2 2026", "Entrevistas equipo comercial"]
```

## Rules

- `headline` is a full-sentence conclusion (≤ 2 lines at 56px, ~15 words).
- `relationship` must contain a verb from `semantic-map.md`. No verb → no slide.
- `focal_point` names exactly one object; the renderer marks it `data-focal`.
- `visual_hierarchy` has 3–4 levels; the renderer maps them to scale/weight/tone in that order.
- `encodings` lists only variables that carry meaning.
- `annotations` are anchored to objects or data points; each ≤ 18 words.
- `text_budget` is enforced by QA (`data-word-budget`).
- `avoid` must contain the lazy versions of this slide, named specifically.
- `alternatives_considered` records at least two rejected options with reasons — this is what
  proves the composition was chosen, not defaulted to.
- Charts: `data.values` holds the numbers; the renderer draws from data with scales — never
  hand-placed bars.
