# CASE BRAIN — Finora

> Memoria ejecutiva viva del caso. La genera CaseOS desde el estado del caso ante cada cambio material; no guarda todo, solo lo relevante. Cada ID enlaza a su archivo.
> Actualizado: 2026-09-28T22:22:27-06:00 · motivo: importación inicial del caso Finora

## Case
Business Analytics: del dato a la decisión — Alegra · reto técnico

## Objective
Entender qué explicaciones podríamos defender ante CRO y CFO, qué sigue siendo una posibilidad y qué información permitiría elegir entre ellas.

## Audience
CEO, CRO, CFO

## Current Phase
**Briefing**

| Fase | Estado | Ready |
|---|---|---|
| 01 Briefing | review | — |
| 02 Framing | review | — |
| 03 Research | in_progress | — |
| 04 Synthesis | not_started | — |
| 05 Story | not_started | — |
| 06 Slides | not_started | — |

## Current Status
7 investigaciones completadas (0 aceptadas), 0 en curso, 2 bloqueadas · 0 findings aceptados · 7 decisiones activas · 0 alertas abiertas.

## Approved Briefing
_Pendiente de aprobación (brief en `brief/brief.md`)._

## Approved Framing
_Pendiente de aprobación (framing vivo en `framing/current.md`)._

## Governing Question
¿Qué explicaciones podemos defender ante el CRO y el CFO con los datos disponibles, qué sigue siendo solo una posibilidad y qué información permitiría elegir entre ellas?

## Executive Questions
- **Q-001** (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- **Q-002** (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- **Q-003** (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?

## Current Story
- Qué sabemos: el caso relata más volumen comercial sin aumento proporcional de clientes nuevos, y plantea distinguir cambios de ingreso al introducir descuentos.
- Qué nos impide cerrar la explicación: las fuentes muestran pagos, industria y gasto, pero no toda la historia de quienes entraron ni los componentes del valor recurrente.
- Cómo proponemos avanzar: usar los pagos para describir lo que sí vemos, revisar con los ejemplos qué distingue el modelo y dejar claras las preguntas que requieren más evidencia.
- Qué tan seguros estamos: la separación de preguntas es defendible bajo las definiciones que explicamos; todavía tenemos poca evidencia para elegir una causa real del desempeño.
- Qué cambiaría el plan: descubrir eventos completos de entradas y compras, o información separada de suscripciones, tarifas y descuentos.

## Decisions
- **D-001** CRO pasa de cuatro a tres ramas · 2026-09-28 → Cantidad, mezcla y compra según tiempo. Se deja de tratar c…
- **D-002** CFO conserva tres grupos · 2026-09-28 → Entrantes, salientes y continuos, con suscripción y descuen…
- **D-003** Calidad, atención, post-SQL y oferta son explicaciones para contrastar · 2026-09-28 → Son explicaciones para contrastar, no causas ya confirmadas…
- **D-004** Preguntas de pagos separadas de causas · 2026-09-28 → HO responde cosas más pequeñas que HC/HF. No se usa un sust…
- **D-005** Prioridad por importancia × capacidad · 2026-09-28 → Orden revisable cuando conozcamos datos y resultados. Cero…
- **D-007** Solución fuera de esta etapa · 2026-09-28 → Sin dashboards, métricas definitivas, modelo de datos ni de…
- **D-008** Versiones del brief conservadas · 2026-09-28 → v0.3 técnica y v0.4 corta siguen accesibles; esta edición n…

_Por confirmar:_ D-009, D-010, D-011, D-012

## Active Hypotheses
- **H-001** (HC1) New creció, pero otras entradas bajaron. Entonces el total de personas que podrían comprar no creció tanto como parecía. · open
- **H-002** (HC2a) Aumentó la proporción de personas que históricamente compran menos o tardan más en hacerlo. · open
- **H-003** (HC2b) Hay más entradas recientes que todavía no tuvieron la misma oportunidad de comprar. · open
- **H-004** (HC3ab) HC3a: al principio compran menos, pero después alcanzan un resultado parecido. HC3b: la diferencia sigue existiendo incluso con más seguimiento comparable. · open
- **H-005** (HC3q) Al entrar, las personas muestran menor necesidad, intención o ajuste, medidos con el mismo criterio. · open
- **H-006** (HC3s) La menor compra coincide con más demora en atender a personas comparables. · open
- **H-007** (HC3p) Con entradas y avance previo comparables, el deterioro aparece después de un punto del recorrido. · open
- **H-008** (HC3o) Cambios de producto, precio, condiciones o alternativas afectan la elección aunque intención inicial y atención sean parecidas. · open
- **H-009** (HF1a) Entraron más o menos clientes, o entraron con suscripciones o tarifas distintas. · open
- **H-010** (HF1b) Hay descuentos documentados al entrar y cambió cuánto reducen el precio. · open
- … y 12 más

## Evidence We Trust
_Todavía no hay evidencia aceptada._

## Things We Cannot Claim
- Que el monto sea MRR contratado: mientras la recurrencia no se confirme, se habla de monto pagado observado.
- Que la primera transacción sea la adquisición del cliente: mientras la historia no se confirme, es la primera aparición observada.
- Que una comparación sin cobertura completa describa al negocio: se detiene esa comparación.
- Que hubo descuentos en el histórico: el caso habla de introducirlos.
- Que una simulación de escenarios describe lo que ocurrió: prueba qué se puede distinguir, no qué pasó.
- Nada sobre conversión de leads o del funnel: los pagos no incluyen a quien no compró.
- Que la primera aparición sea el hito de adquisición del CRO (Won, primer pago o suscripción activa siguen por acordar).
- Etiquetas contractuales (alta, baja o expansión de suscripción) sin vigencia verificada.
- Descuentos a partir del tamaño de un salto del monto.
- Una lectura del puente si las contribuciones no concilian con el total.
- … y 4 más

## Open Questions
- **Q-004** (C1) ¿Realmente aumentó igual la entrada total?
- **Q-005** (C2) ¿Cambió la gente que entra o el tiempo que ha tenido para comprar?
- **Q-006** (C3) ¿Personas similares están comprando menos o comprando más tarde?
- **Q-007** (F1) ¿Cuánto aportan los clientes que entran?
- **Q-008** (F2) ¿Cuánto dejan de aportar los clientes que salen?
- **Q-009** (F3) ¿Qué cambió en quienes permanecen?
- **Q-010** (W0) ¿Qué podemos nombrar y comparar válidamente?
- **Q-011** (W1) ¿El monto identifica los escenarios del CFO?
- **Q-012** (W2) ¿Qué cambió en los primeros pagadores observados?
- **Q-013** (W3) ¿Dónde se concentra el cambio del monto observado?
- … y 10 más

## Research Queue
- **R-001** (W0) Solo monto pagado observado y primera aparición observada son comparables · completed · por revisar
- **R-002** (W1) El monto no identifica los escenarios del CFO: observaciones idénticas admiten lecturas distintas · completed · por revisar
- **R-003** (W2) Más primeras apariciones de pago, con un primer pago menor · completed · por revisar
- **R-004** (W3) El cambio se concentra en la entrada de pagadores nuevos observados · completed · por revisar
- **R-005** (W4) La industria no concentra el cambio: el patrón aparece difundido · completed · por revisar
- **R-006** (W5) Respuesta parcial: a igual edad el aporte posterior es menor, concentrado en la entrada · completed · por revisar
- **R-007** (W6) Bloqueada: no hay sustituto válido con los datos actuales. La respuesta es la lista de evidencia que falta. · blocked
- **R-008** (W7) Bloqueada: no hay sustituto válido con los datos actuales. La respuesta es la lista de evidencia que falta. · blocked
- **R-009** (Q2) La caída se concentra en quién entra, no en la base previa · completed · por revisar

## Accepted Frameworks
- **D-001** CRO pasa de cuatro a tres ramas
- **D-002** CFO conserva tres grupos
- CRO por cuánto entra, quién entra y cómo compra con el tiempo: Incluye rutas distintas sin asumir que sabemos quién comprará en el futuro. C1, C2 y C3.
- CFO por clientes que entran / salen / permanecen: Evita contar la misma cuenta en dos grupos entre las mismas fechas; dentro de cada grupo distinguim…

## Key Tables
_Sin tablas aceptadas._

## Contradictions
_Sin contradicciones abiertas._

## Risks
_Sin riesgos altos abiertos._

## Artifacts
- **A-001** Brief de trabajo v0.3 (fuente de verdad) (`brief/sources/alegra_brief_de_trabajo.html`)
- **A-002** Business Exploration Workspace (Finora) (`/ws/finora/`)
- **A-003** Propuesta de arquitectura v1.2 del workspace agentic (`finora-eda/docs/propuesta_arquitectura_v1.md`)
- **A-004** Narrativa en borrador: Caso CFO · qué mide hoy el MRR (`finora-eda/narratives/NAR-20260928-150639-9b63.json`)
- **A-005** Narrativa en borrador: Exploración General (`finora-eda/narratives/NAR-20260928-163219-5cba.json`)

## Language Profile
```yaml
language:
  primary: es
  tone: direct, conversational
  technical_level: adaptive
  preserve_user_vocabulary: true
  avoid_unnecessary_jargon: true
```
Registro observado: conversacional, directo; mezcla español con términos de negocio en inglés · nivel técnico: analítico · vocabulario de Hugo: leads, funnel, MRR, churn, self-serve, SQL directo, post-SQL, New, primer pagador observado, monto observado, MECE, impacto × capacidad, CRO, CFO

## Recent Material Changes
- 2026-09-28 22:22 · Caso Finora importado desde el brief v0.3 y el Business Exploration Workspace
- 2026-09-28 22:22 · Research: not_started → in_progress (W0–W5 respondidas en el workspace antes de CaseOS; W6/W7 bloqueadas)
- 2026-09-28 22:22 · Framing: not_started → review (framing v0.3 importado; pendiente de Mark Ready)
- 2026-09-28 22:22 · Briefing: in_progress → review (brief importado; pendiente de Mark Ready)
- 2026-09-28 22:22 · import propone decisión: Sin deck ni narrativa final todavía
- 2026-09-28 22:22 · import propone decisión: La demo pública es el HTML estático; el agente se muestra en el video del proceso con IA
- 2026-09-28 22:22 · import propone decisión: Componer las respuestas desde evidencia verificada existente, no con una corrida del agente por pregunta
- 2026-09-28 22:22 · import propone decisión: El brief v0.3 es la fuente de verdad del caso
- 2026-09-28 22:22 · Hugo decidió: Versiones del brief conservadas
- 2026-09-28 22:22 · Hugo decidió: Solución fuera de esta etapa


<!-- ideas del framing por tipo: Intuición de Hugo 2, Propuesta 7, Observación 3, Desconocido 7 -->
