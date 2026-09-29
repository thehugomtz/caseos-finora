# CASE BRAIN — Finora

> Memoria ejecutiva viva del caso. La genera CaseOS desde el estado del caso ante cada cambio material; no guarda todo, solo lo relevante. Cada ID enlaza a su archivo.
> Actualizado: 2026-09-29T09:21:46-06:00 · motivo: Migración pedida por Hugo: 3 sección(es) del guion y 5 tarea(s) de investigación propuestas · Entregables limpios propuestos en el brief

## Case
Business Analytics: del dato a la decisión — Alegra · reto técnico

## Objective
Responder a Finora en tres bloques, con datos solo donde realmente ayudan: (1) Overview — entender la salud general del modelo y qué señales tener en mente antes de entrar a Growth y Revenue; (2) Growth / CRO — cómo definir y medir el funnel si no todos los clientes lo recorren igual, qué hipótesis podrían explicar “más leads, pero no más ventas” (qué sostiene la data, qué sigue siendo posibilidad y qué dato permitiría elegir) y qué solución analítica le permitiría al CRO operar el funnel de forma recurrente y qué decisiones tomar con ella; (3) Revenue / CFO — cómo introducir descuentos temporales sin que el MRR confunda comportamiento del cliente con decisiones comerciales: mecanismo, modelo de datos y clasificación correcta de los movimientos.

## Audience
CEO — contexto de salud general del modelo (Overview) antes de Growth y Revenue; qué decide no está definido, CRO — cómo definir, medir y operar de forma recurrente el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos, CFO — cómo introducir descuentos temporales sin perder la respuesta a “¿por qué cambió nuestro MRR?”: mecanismo, modelo de datos y clasificación

## Current Phase
**Framing**

| Fase | Estado | Ready |
|---|---|---|
| 01 Briefing | ready | v1 · 2026-09-29T00:13 |
| 02 Framing | review | — |
| 03 Research | in_progress | — |
| 04 Synthesis | not_started | — |
| 05 Story | not_started | — |
| 06 Slides | not_started | — |

## Current Status
7 investigaciones completadas (0 aceptadas), 0 en curso, 2 bloqueadas · 0 findings aceptados · 8 decisiones activas · 0 alertas abiertas.

## Approved Briefing
v1 aprobada el 2026-09-29 → `brief/approved/brief.v1.md`

## Approved Framing
_Pendiente de aprobación (framing vivo en `framing/current.md`)._

## Governing Question
¿Qué explicaciones podemos defender ante el CRO y el CFO con los datos disponibles, qué sigue siendo solo una posibilidad y qué información permitiría elegir entre ellas?

## Executive Questions
- **Q-001** (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- **Q-002** (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- **Q-003** (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?

## Current Story
- Situación (Overview): Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo, periodo por fijar). Esa brecha abre Growth y Revenue.
- Growth, lo que sí vemos: los primeros pagadores observados y su actividad económica por industria, y el gasto de Marketing por categoría en el tiempo, descritos sin atribuir ventas al gasto.
- Growth, lo que no vemos: no todos recorren el funnel igual (propuesta: Assisted, Self Service, Executive). Demanda, calidad, capacidad/atención y post-SQL quedan como explicaciones a contrastar, cada una con el dato que permitiría elegir.
- Growth, cómo operarlo: primero definiciones y fuentes comunes; después, seguimiento recurrente por foros (dashboards, análisis ad hoc, agentes), atado a decisiones del CRO que aún no están definidas.
- Revenue: con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento). Proponemos cómo introducir descuentos temporales y un modelo de datos que separe el valor de la suscripción del precio pagado.
- Qué tan seguros estamos y qué cambiaría: la separación de preguntas es defendible bajo las definiciones que explicamos. Para elegir causas faltan eventos de entradas y compras, y datos separados de suscripción, tarifa y descuento.

## Decisions
- **D-013** Briefing marcada Ready (v1) · 2026-09-29 → Ready
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
- **H-005** (HC3q) Bajó la calidad de lo que genera la máquina de leads: al entrar, muestran menos necesidad, intención o ajuste. Es H-005 en palabras de Hugo. · open
- **H-006** (HC3s) El volumen de entradas superó la capacidad instalada de SDRs y AEs, así que la atención se demora y la compra cae. Es H-006 con un mecanismo concreto: la capacidad. · open
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
- … y 8 más

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
- … y 12 más

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
- El esqueleto (Overview + 4 láminas de Growth + Revenue) es material de soporte; si se usa como la presentación de ≤5 min, no cabe.
- La Lámina 4 carga tres preguntas del brief (concentración + métricas, hipótesis + datos, solución analítica) y puede quedar como una lista de frameworks sin respuesta.
- El agente propio dentro de «Seguimiento» puede leerse como demo de herramienta si no se ata a una decisión concreta del CRO.

## Artifacts
- Briefing v1: `brief/approved/brief.v1.md`
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
Registro observado: Conversacional y directo, informal («jaja»); piensa en láminas, columnas y bloques de deck; español con términos de negocio en inglés. · nivel técnico: Analítico / de negocio: maneja frameworks de Growth (AAARRR, CAC, LTV, UCM), ToFu/BoFu y roles comerciales (SDR, AE, KAM). · vocabulario de Hugo: entrada directa a SQL, Paid Media, Métricas Clave, low tickets, CRM, Analítica Digital, Decision Making, Análisis Adhoc, pricing introductorio, descuentos temporales, contracción, expansión, Propuesta de Modelo de datos, CEO

## Recent Material Changes
- 2026-09-29 09:21 · Migración pedida por Hugo: 3 sección(es) del guion y 5 tarea(s) de investigación propuestas · Entregables limpios propuestos en el brief
- 2026-09-29 09:21 · Migración pedida por Hugo: 3 sección(es) del guion y 5 tarea(s) de investigación propuestas · Entregables limpios propuestos en el brief
- 2026-09-29 00:26 · Framing actualizado (storyline inicial, decisions_needed, should_not_claim, language_notes, risks, research necesario)
- 2026-09-29 00:26 · Framer capturó propuesta: Una propuesta de modelo de datos que resuelva dos cosas: separar el valor de la suscripci…
- 2026-09-29 00:26 · Framer capturó pregunta: Tres casos donde el pago observado no alcanza: una expansión compensada por descuento (10…
- 2026-09-29 00:26 · Framer capturó propuesta: Sección Revenue: primero, lo observable de pricing y comportamiento actual en los pagos;…
- 2026-09-29 00:26 · Framer capturó desconocido: No sabemos qué decisiones quiere tomar el CRO con el funnel. La columna «Decision Making»…
- 2026-09-29 00:26 · Framer refinó N-009: Seguimiento recurrente: dashboards automatizados con métricas según los foros, análisis a…
- 2026-09-29 00:26 · Framer refinó N-010: Base técnica de la solución para el CRO: pulir el CRM e implementar analítica digital.
- 2026-09-29 00:26 · Framer capturó intuición de hugo: Hugo lee que Finora tiene un problema de instrumentación comercial y digital (CRM y analí…


<!-- ideas del framing por tipo: Intuición de Hugo 3, Propuesta 13, Observación 4, Desconocido 8, Supuesto 1 -->
