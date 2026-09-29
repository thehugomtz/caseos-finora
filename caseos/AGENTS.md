# Agentes

El contrato completo de cada agente vive en `agents/<id>.md` (Role · Purpose · System behavior · Inputs · Outputs ·
Skills · Tools · Allowed decisions · User approval required · Guardrails · Handoff contract · Failure modes · Examples).
La sección *System behavior* es lo que el runtime inyecta como instrucciones; el resto documenta el contrato.

**Regla común:** ningún agente decide por Hugo. Todo lo que producen entra como **propuesto** (`review.state: proposed`);
las decisiones sugeridas quedan `proposed`; solo Hugo acepta, rechaza, aprueba fases o resuelve alertas
(`actor == "hugo"` en código).

| Agente | Qué hace | Skills core (más dynamic/lens según la solicitud) | Herramientas | Sale como |
|---|---|---|---|---|
| **Briefer** (`briefer.md`) | Arma el brief con Hugo sección por sección a partir de lo que cuenta, reencuadra o pega. Propone con base (`hugo` / `enunciado` / `inferido`); nunca aprueba; el enunciado lo guarda el código literal. | brief-builder, clarification-protocol; dynamic: business-case-partner | ninguna | propuestas pendientes por sección (`brief/brief.yaml › pending`) |
| **Framer** (`framer.md`) | Convierte lo que Hugo piensa en framing y arma con él el **documento de Shaping**: separa 9 tipos epistémicos, conserva sus palabras junto a la versión estructurada, propone pregunta ejecutiva, frames, el **problema** (con no-gos), el **guion de la historia** (secciones → láminas) y el **plan de investigación** tipado por agente (datos · research · medición · modelo de datos). Modos Organize / Advise / Challenge. | adaptive-case-framer, business-case-partner, clarification-protocol, case-shaping (Organize); bulletproof + consulting (Advise); assumption-challenger + executive-mentor (Challenge); advisors C-level como lentes (0–1, máx. 2) | ninguna | `FramerTurn` → N/H/Q/D propuestos, propuestas de Shaping pendientes (`framing/current.yaml › pending`), perfil de lenguaje |
| **Research Router** (`research-router.md`) | Clasifica cada solicitud: especialista, intensidad L1/L2/L3, skills mínimas, y verifica que sirva a una Q/H/D/C del caso. | research-routing | ninguna | ruta + propósito (o *research without case purpose*) |
| **Business Research** | Mercado, prácticas, benchmarks, definiciones. L1 lookup, L2 business research, L3 deep research (profundidad + amplitud + contraargumento en paralelo → peer review → síntesis). | case-research-synthesis; deep-business-research (L3); dynamic: pricing, commercial, competitive-intel, market/product research, SaaS metrics | WebSearch, WebFetch | resultado §40 + findings propuestos |
| **Measurement** | Cómo medir: árboles de KPI, recorridos no lineales, cohortes, instrumentación, experimentos. | measurement-strategy, case-research-synthesis | WebSearch, WebFetch | §40 + bloque de medición (framework, métricas, eventos, dimensiones) |
| **Data Engineering** | Cómo modelar: grano, hechos/dimensiones, vigencia, identidad, suscripción/facturación/descuento. | data-modeling, case-research-synthesis | WebSearch, WebFetch | §40 + modelo de datos (entidades, campos, reglas, ejemplos) |
| **Analytics** | Reutiliza el Business Exploration Workspace: investiga con su propio agente y sus validadores; CaseOS toma la evidencia registrada. | (las del workspace) | adaptador del workspace | findings + **EvidenceTable** con linaje |
| **Chief of Staff** (`cos.md`) | Guarda el estado: evalúa el impacto de nueva evidencia, abre alertas con opciones A/B/C y recomendación, decision log, siguientes mejores acciones; arma el Story Package **siguiendo el Guion de Hugo** (una lámina sin evidencia se marca y vuelve pregunta, no se rellena). | case-chief-of-staff, story-package; dynamic: business-case-partner; challenge: assumption-challenger | ninguna | alertas, hipótesis/preguntas propuestas, Story Package (§61) |
| **Visual Storyteller** (`visual-storyteller.md`) | La capacidad existente de Hugo, **enlazada, no reconstruida**: storyline → dirección visual → composición → HTML → loop de QA (+ crítico independiente) → presentación. | executive-visual-storyteller, executive-storyline, consulting-visual-director, html-slide-renderer, slide-critic | Skill, Read, Write/Edit (solo en el deck), Bash (solo scripts del renderer) | deck HTML + slides S-xxx con `claim_id` |

## Esfuerzo y costo

Todos usan `claude-opus-5-5` con esfuerzo `max` (pedido de Hugo, 28-sep-2026); `CASEOS_EFFORT_<ROL>` lo baja por agente
sin cambiar de modelo. Cada corrida tiene un tope equivalente (`caseos/config.py › BUDGET_USD`) dimensionado para max.
Con suscripción no se factura por corrida; CaseOS muestra el costo equivalente de cada una para que se vea el consumo.

Medido en la validación (28-sep-2026, detalle en docs/VALIDATION.md): turno del Framer 1–1.8 min y US$0.34–0.51; research L1 ~4 min y US$0.6; Measurement L3 ~8 min y US$1.6; evaluación de impacto del COS 1–2 min y US$0.25–0.44; Story Package ~2 min y US$0.42; Visual Storyteller (4 slides, sin crítico independiente) 27 min y US$8.87.

## Topología

```
Hugo ──► Framer ──► documento de Shaping aprobado ──► plan de investigación ──► Research Router ──► Business · Measurement · Data Eng · Analytics
  ▲                                                                   │ findings / EvidenceTables
  │                                                                   ▼
  └──── alertas con opciones · decisiones ◄──────────────── Chief of Staff ──► Story Package ──► Visual Storyteller ──► deck
```

La vista **Agents** muestra esta topología en vivo (quién trabaja, en qué, qué produjo, qué skills cargó).
