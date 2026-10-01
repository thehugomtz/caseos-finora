# CASE BRAIN — Finora

> Memoria ejecutiva viva del caso. La genera CaseOS desde el estado del caso ante cada cambio material; no guarda todo, solo lo relevante. Cada ID enlaza a su archivo.
> Actualizado: 2026-09-30T19:35:24-06:00 · motivo: Hugo reordenó el deck finora-v5-20260930-112103: 11→10, 12→11, 13→12, 14→13, 15→14, 16→15, 17→16, 18→17, 19→18, 20→19, 21→20, 22→21, 23→22,…

## Case
Business Analytics: del dato a la decisión — Alegra · reto técnico

## Objective
Responder a Finora en tres bloques, con datos solo donde realmente ayudan: (1) Overview — entender la salud general del modelo y qué señales tener en mente antes de entrar a Growth y Revenue; (2) Growth / CRO — cómo definir y medir el funnel si no todos los clientes lo recorren igual, qué hipótesis podrían explicar “más leads, pero no más ventas” (qué sostiene la data, qué sigue siendo posibilidad y qué dato permitiría elegir) y qué solución analítica le permitiría al CRO operar el funnel de forma recurrente y qué decisiones tomar con ella; (3) Revenue / CFO — cómo introducir descuentos temporales sin que el MRR confunda comportamiento del cliente con decisiones comerciales: mecanismo, modelo de datos y clasificación correcta de los movimientos.

## Audience
CEO — contexto de salud general del modelo (Overview) antes de Growth y Revenue; qué decide no está definido, CRO — cómo definir, medir y operar de forma recurrente el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos, CFO — cómo introducir descuentos temporales sin perder la respuesta a “¿por qué cambió nuestro MRR?”: mecanismo, modelo de datos y clasificación

## Current Phase
**Slides**

| Fase | Estado | Ready |
|---|---|---|
| 01 Briefing | ready | v1 · 2026-09-29T00:13 |
| 02 Framing | ready | v3 · 2026-09-30T11:05 |
| 03 Research | ready | v1 · 2026-09-29T20:33 |
| 04 Synthesis | ready | v1 · 2026-09-29T20:45 |
| 05 Story | ready | v2 · 2026-09-30T11:20 |
| 06 Slides | review | — |

## Current Status
34 investigaciones completadas (0 aceptadas), 0 en curso, 2 bloqueadas · 155 findings aceptados · 22 decisiones activas · 169 alertas abiertas.

COS: R-036 trae el tercer catálogo de métricas del caso (35: 30 por funnel + 5 comunes, semáforo 0/4/31); F-248–F-252 siguen propuestos. Con Story Ready y Slides en review, lo que bloquea es elegir un solo catálogo (C-022) y reconciliar el semáforo de C-009 (en total vs por funnel) antes de tocar láminas. Siguen abiertas dos definiciones de Hugo (Reactivate como funnel o loop, y dónde va Engaged) y la pregunta a Finora por los datos previos al pago con llave a customer_id.

## Approved Briefing
v1 aprobada el 2026-09-29 → `brief/approved/brief.v1.md`

## Approved Framing
v3 aprobada el 2026-09-30 → `framing/approved/current.v3.md`

## Governing Question
¿Qué explicaciones podemos defender ante el CRO y el CFO con los datos disponibles, qué huecos en su WoW y qué modelos se proponen para poder llegar a tomar mejores decisiones?

## Executive Questions
- **Q-001** (CRO) ¿Por qué está llegando más gente, pero los clientes nuevos no crecen en la misma proporción?
- **Q-002** (CFO) ¿Por qué cambió el ingreso recurrente y cuánto se explica por lo que el cliente contrata, por la tarifa o por descuentos?
- **Q-003** (CEO) ¿Cómo se conectan cómo conseguimos clientes y qué mueve el ingreso recurrente?

## Current Story
**Governing thought:** La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.
- **C-001** Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8× · supported
- **C-002** La caída por cliente se asocia a quién entra; la base previa sostiene su monto · superseded
- **C-003** Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias · superseded
- **C-004** Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas · superseded
- **C-005** Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar · superseded
- **C-006** Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento · superseded
- **C-007** La pérdida está en el monto por cliente de cosechas de menor ticket · supported
- **C-008** Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar · superseded
- **C-009** Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta · superseded
- **C-010** Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC · superseded

## Decisions
- **D-029** Story marcada Ready (v2) · 2026-09-30 → Ready
- **D-028** Framing marcada Ready (v3) · 2026-09-30 → Ready
- **D-027** Delegación a Claude (4): aprobar la historia v4 y lanzar el deck de corrido · 2026-09-30 → «Delego y sigue de corrido»: Claude acepta la evidencia nue…
- **D-026** Revisión del deck v3: los ajustes los hacen los agentes y quedan en CaseOS; Claude coordina · 2026-09-30 → «Ojo los ajustes los tienen que hacer los agentes y quedar…
- **D-025** Story marcada Ready (v1) · 2026-09-29 → Ready
- **D-024** Synthesis marcada Ready (v1) · 2026-09-29 → Ready
- **D-023** Delegación a Claude (3): aceptar la historia con su evidencia · 2026-09-29 → «Pero tu dale accept a todo lo de la story»
- **D-022** R-013 requiere más investigación H-022: Sin impacto material · 2026-09-29 → Sin impacto material
- **D-021** R-013 cambia el framing Q-018: Sin impacto material · 2026-09-29 → Sin impacto material
- **D-020** Research marcada Ready (v1) · 2026-09-29 → Ready
- … y 12 más

_Por confirmar:_ D-009, D-010, D-011, D-012, D-015, D-018

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
- … y 68 más

## Evidence We Trust
- **F-001** (C-RES-01) Los clientes activos crecieron más rápido que el MRR pagado entre ene-22 y oct-24. · high
- **F-002** (C-RES-02) El MRR por cliente activo de oct-24 es más de 30% menor que el de ene-22. · high
- **F-019** (C-MON-04) Los clientes existentes no pagan menos y las cosechas 2023–24, de menor ticket, ya son la mayoría de los clientes activos. · high
- **F-020** (C-MON-05) El MRR por cliente activo bajó en las seis industrias entre dic-22 y oct-24. · high
- **F-022** (C-INV-02) El S&M total por cliente nuevo es más de 50% menor en 2024 que en 2022. · high
- **F-023** (C-INV-03) Las correlaciones en niveles entre gasto y altas (rezagos 0–1) son todas negativas, y ninguna correlación de cambios mes a mes alcanza |r| ≥ 0,3 ni p < 0,05. · medium
- **F-024** (C-INV-04) Toda correlación con p < 0,05 es una correlación negativa en niveles con las altas. · medium
- **F-030** (C-ADQ-07) El aumento de altas por mes entre 2022 y 2024 corresponde a clientes con run-rate inicial menor que la mediana de 2022; por encima de esa mediana, las altas por mes no aumentaron. · high
- **F-033** (C-RET-03) El churn observado bajó más de un punto entre 2022 y 2024, mientras el churn que no vuelve a pagar en tres meses cambió menos de 0,3 puntos. · high
- **F-037** (C-ADQ-08) El valor inicial incorporado por mes creció menos que las altas entre 2022 y 2024 en las tres normalizaciones probadas, y entre 2023 y 2024 cambió menos de 10% en todas. · high
- … y 145 más

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
- … y 21 más

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
- … y 97 más

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
- **R-010** Hay ocho explicaciones en juego. Tres son artefactos de medición: conteo (H-001), mezcla (H-002) y tiempo (H-003/H-004). Las otras cuatro serían causas reales: calidad al entrar (… · completed · por revisar
- … y 26 más

## Accepted Frameworks
- **D-001** CRO pasa de cuatro a tres ramas
- **D-002** CFO conserva tres grupos
- CRO por cuánto entra, quién entra y cómo compra con el tiempo: Incluye rutas distintas sin asumir que sabemos quién comprará en el futuro. C1, C2 y C3.
- CFO por clientes que entran / salen / permanecen: Evita contar la misma cuenta en dos grupos entre las mismas fechas; dentro de cada grupo distinguim…

## Key Tables
- **T-001** `FIN-GROWTH-01` Clientes activos y monto observado por cliente activo
- **T-002** `CFO-03` Churn observado vs churn persistente
- **T-005** `FIN-F-063` El archivo de gasto de S&M reporta cada rubro en unidades reportadas (u) sin factor de escala
- **T-008** `FIN-F-066` El archivo se comporta como una asignación de arriba hacia abajo en su primer tramo
- **T-009** `FIN-F-067` La serie de Habilitación cambia de composición dentro del panel
- **T-011** `FIN-F-069` El peso de Habilitación en el S&M total no es estable
- **T-012** `FIN-F-070` Habilitación pesa 12% del S&M total en 2022 y 4% en 2024, y el gasto por alta baja de 0,11 a 0,04 incluyéndol…
- **T-013** `FIN-F-107` En 2023 jun-dic las altas por mes son 60,6 frente a 45,2 en 2023 ene-may, mientras el gasto de generación de…
- **T-016** `FIN-F-110` Las altas mensuales pasan de 26 en dic-22 a 60 en ene-23 y el punto más alto del periodo se observa en jun-24…
- **T-019** `FIN-F-113` Entre 2022 y 2024 las altas por mes cambian +104% mientras el valor inicial incorporado por mes cambia +6% me…
- … y 37 más

## Contradictions
- **X-040** R-011 contradice H-017
- **X-094** R-026 contradice H-032
- **X-101** R-028 contradice T-034

## Risks
- **X-004** R-013 cambia el framing
- **X-005** R-015 cambia el framing
- **X-006** R-015 abre una hipótesis nueva Q-020
- **X-007** R-015 cambia la historia Q-022
- **X-016** R-010 cambia el framing Q-001
- **X-031** R-018 debilita H-017
- **X-036** R-011 cambia la historia Q-002
- **X-037** R-011 cambia la historia T-003
- **X-038** R-011 cambia el framing Q-026
- **X-049** R-016 cambia el framing Q-001
- … y 31 más

## Artifacts
- Briefing v1: `brief/approved/brief.v1.md`
- Framing v3: `framing/approved/current.v3.md`
- Research v1: `research/approved/research.v1.yaml`
- Synthesis v1: `cos/approved/synthesis.v1.yaml`
- Story v2: `story/approved/current.v2.md`
- **A-001** Brief de trabajo v0.3 (fuente de verdad) (`brief/sources/alegra_brief_de_trabajo.html`)
- **A-002** Business Exploration Workspace (Finora) (`/ws/finora/`)
- **A-003** Propuesta de arquitectura v1.2 del workspace agentic (`finora-eda/docs/propuesta_arquitectura_v1.md`)
- **A-004** Narrativa en borrador: Caso CFO · qué mide hoy el MRR (`finora-eda/narratives/NAR-20260928-150639-9b63.json`)
- **A-005** Narrativa en borrador: Exploración General (`finora-eda/narratives/NAR-20260928-163219-5cba.json`)
- … y 1 más

## Language Profile
```yaml
language:
  primary: es
  tone: direct, conversational
  technical_level: adaptive
  preserve_user_vocabulary: true
  avoid_unnecessary_jargon: true
```
Registro observado: Conversacional y directo; piensa en funnels, láminas y bloques; mezcla español con términos de ventas en inglés. · nivel técnico: Analítico-negocio: maneja etapas del funnel, SDR/AE, ToFu/BoFu y métricas SaaS. · vocabulario de Hugo: Análisis Ad hoc, Mecanismo Propuesto, Implicaciones Multidisciplinarias, research, data, funnel, self-serve, estancamientos, churn, reactivación, negocio subyacente, revenue que dejamos de capturar, MRR, pricing

## Recent Material Changes
- 2026-09-30 19:35 · Hugo reordenó el deck finora-v5-20260930-112103: 11→10, 12→11, 13→12, 14→13, 15→14, 16→15, 17→16, 18→17, 19→18, 20→19, 21→20, 22→21, 23→22, 24→23, 10→24
- 2026-09-30 18:55 · Hugo editó el texto de la lámina 17 del deck finora-v5-20260930-112103: «Hoy no es construible : no hay lista, plan ni desc» → «»
- 2026-09-30 18:47 · Hugo editó el texto de la lámina 13 del deck finora-v5-20260930-112103: «Cada hoja del árbol tiene firma y dato propios; ho» → «Todos los datos apuntan a lo mismo: proceso, compo»
- 2026-09-30 18:46 · Hugo borró de la lámina 12 el porqué del Paso 0 (altas 2024 contra 2023, +7% / −19%) y la nota de cobro (2,8% y 3,1%); sin esa nota, la hoja «Won que no llega a pagar» lleva el mismo círculo que las demás y el pie ya no cita F-125 ni F-230 · vía Claude (el editor de texto no podía: el texto venía armado en partes)
- 2026-09-30 18:42 · Hugo editó el texto de la lámina 12 del deck finora-v5-20260930-112103: «Proponemos un árbol MECE: cada pedazo de la brecha» → «Existen 5 hipotésis que podrían explicar el increm»
- 2026-09-30 16:50 · Cambios de Hugo aplicados en las láminas 2, 6, 7, 11, 12, 13, 15, 16, 17, 19, 21 del deck finora-v5-20260930-112103
- 2026-09-30 16:18 · Hugo pidió al Visual Storyteller cambios en las láminas 2, 6, 7, 11, 12, 13, 15, 16, 17, 19, 21 del deck finora-v5-20260930-112103 · vía Claude: Hugo pidió ajustar las láminas donde tuvo dudas, reencuadrar la de cada hoja del árbol con su idea de volumen y tiempo (o un ribbon) y sumar lo que Claude identificó
- 2026-09-30 16:16 · Hugo reordenó el deck finora-v5-20260930-112103: 15→6, 6→7, 7→15, 34→19, 19→20, 20→21, 21→22, 22→23, 23→24, 24→25, 25→26, 26→27, 27→28, 28→29, 29→30, 30→31, 31→32, 32→33, 33→34 · vía Claude: Hugo respondió «Va» a mover las láminas 15, 7 y 34 para que sigan su guion
- 2026-09-30 14:54 · Hugo trajo «La brecha clientes–monto se asocia a quién entra» (lámina 1 de finora-v3-20260929-212258) como lámina 2 del deck finora-v5-20260930-112103 · vía Claude: Hugo pidió recuperar la lámina inicial del deck v3 («la lámina inicial… que describía el problema inicial»)


<!-- ideas del framing por tipo: Intuición de Hugo 3, Propuesta 38, Observación 5, Desconocido 9, Supuesto 3, Hecho 3 -->
