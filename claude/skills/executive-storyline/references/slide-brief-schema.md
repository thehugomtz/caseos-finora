# Slide brief schema (storyline output)

One YAML block per slide inside `storyline.md` §5. It describes the argument, not the design.

```yaml
slide_id: S06
question: "¿Cómo debería medirse el funnel?"
message: "Un funnel único oculta tres acquisition motions con comportamientos diferentes."   # action title
role_in_story: "evidence"          # see storyline-patterns.md role vocabulary
role_detail: "Responde la primera pregunta del CRO y establece el framework de medición."
support:
  - claim: "Self-service convierte 3.1% en 9 días"
    type: FACT                      # FACT | INFERENCE | PROPOSAL
    source: "CRM Q2"
    strength: strong                # strong | partial | none
  - claim: "Sales-assisted aporta 58% del ARR nuevo con 24% de conversión"
    type: FACT
    source: "CRM Q2"
    strength: strong
  - claim: "Medir los tres con la misma tasa de conversión esconde qué palanca mover"
    type: INFERENCE
    logic: "tasas y ciclos 3–7× distintos → un promedio no describe a ninguno"
visual_intent: "Mostrar tres journeys distintos que convergen en un resultado económico común."
must_show:
  - diferencias de recorrido
  - puntos de medición
  - resultado común
must_not_do:
  - "No usar tres cards con bullets."
  - "No convertirlo en una tabla."
takeaway: "Finora debe medir cada acquisition motion con una lógica diferente."
notes: "Qué se dice en voz alta y no va en la slide."
evidence_gaps: []                   # claims that need data before this slide can ship
```

## Field rules

- `message` — a conclusion with a verb; ≤ ~15 words; would still be true and useful if it were
  the only thing the audience read.
- `question` — the audience's question this slide answers; it must follow from the previous
  slide's message.
- `support` — only what proves the message; each item tagged. INFERENCE items carry `logic`.
  PROPOSAL items never appear before the evidence that justifies them.
- `visual_intent` — the relationship to make visible (a verb: converge, leak, nest, cause…),
  never a layout ("dos columnas", "cuatro cajas").
- `must_show` — the minimum content without which the message is unproven.
- `must_not_do` — lazy renderings to avoid, named specifically.
- `notes` — what the presenter says; detail moved off the canvas lands here.
- `evidence_gaps` — if non-empty, the slide is flagged in §7 and the headline is softened or the
  gap is closed before rendering.
