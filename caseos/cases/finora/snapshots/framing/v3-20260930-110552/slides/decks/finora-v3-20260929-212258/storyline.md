# Storyline — Finora · La brecha clientes–monto se asocia a quién entra; el porqué no está e…

> Pre-llenado por CaseOS desde el **Story Package v3** aprobado por Hugo (2026-09-29). Es el Stage 1 del Executive Visual Storyteller: puedes pulir títulos y recortar texto, **no cambies el argumento ni las cifras**; lo que no se sostenga va a §7 para Hugo. Las cifras de cada slide están en `data/*.yaml`. Conserva `claim_id` en cada spec.

## 1. Audiencia y decisión

| | |
|---|---|
| **Audiencia** | CEO: contexto de salud general del modelo (Overview) antes de Growth y Revenue. Qué decide todavía no está definido., CRO: cómo definir, medir y operar el funnel en un modelo híbrido, y qué podría explicar más leads sin más clientes nuevos., CFO: cómo introducir descuentos temporales sin perder la respuesta a «¿por qué cambió nuestro MRR?»: mecanismo, modelo de datos y clasificación. |
| **Objetivo / decisión** | BORRADOR 3 (N-050 a N-054). Incorpora tus cambios: C-021 con las etapas literales por ruta y canal, y su dueño (R-031); C-006 rehecho como «cómo se mide cada funnel», por familia y con fórmula; C-009 con las métricas que faltaban y una regla MECE; C-023 como árbol MECE por niveles, sin «artefacto» (medición contra negocio, R-032); C-013 con el modelo de datos as-is vs to-be (R-033); C-017 con el modelo de precios y descuentos y sus casuísticas (R-034). Ajustes que se derivan de esos cambios: C-005 (el canal pasa a ser atributo de la entrada), C-011 y C-012 (coherentes con el árbol), C-014 (usa los nombres nuevos de las métricas), C-022 (gobierna el catálogo sin duplicar métricas), C-019 y C-020 (coherentes con C-017), y C-020 y C-024 sin F-131 (choca con F-184, X-100). C-001 y C-004 conservan las gráficas que elegiste. Todo cita findings propuestos: queda pendiente de tu aceptación y el paquete no puede marcarse Ready. El choque entre D-007 y D-018 lo decides tú. |
| **Qué creen hoy (From)** | Finora suma clientes mucho más rápido que monto pagado. Esa brecha se lee con explicaciones que los pagos no confirman: «más leads que no convierten» y «cambios de suscripción o descuentos». |
| **Qué deben creer al salir (To)** | La brecha coincide con quién entra: más primeros pagadores, con menor ticket estabilizado, dentro de cada industria. No coincide con la base previa ni con salidas persistentes. El porqué del CRO y del CFO no está en los datos del caso, pero hay un diseño concreto para decidirlo: rutas con sus etapas literales por canal y dueño, métricas por funnel y comunes sin duplicados, un árbol MECE de la brecha con su dato y su palanca, y modelos de datos as-is vs to-be para el funnel y para precios y descuentos. |
| **Formato** | Presentación ejecutiva ≤ 5 min para CEO, CRO y CFO: Situación → Hallazgo → Implicación → Decisión → Acción; Material de soporte (propuesto, no final) · 1 Overview — observaciones generales y salud del negocio que introducen las secciones siguientes (p. ej. clientes 4,5× vs ingreso 2,8×; MRR por clie |
| **Idioma** | es — tono directo y conversacional; conservar términos de Hugo |

## 1b. Guion de Hugo (orden de secciones y láminas: respétalo)

| Lámina | Pregunta que responde | Qué debe mostrar | Claims | Cobertura |
|---|---|---|---|---|
| **S1 · Overview** | Situación (Overview): Finora suma clientes mucho más rápido que monto pagado (4,5× vs 2,8×; ~−38% por cliente activo, periodo por fijar). Esa brecha abre Growth y Revenue. | | | |
| S1.1 Overview |  | observaciones generales y salud del negocio que introducen las secciones siguientes (p. ej. clientes 4,5× vs ingreso 2,8×; MRR por cliente activo −38%) | C-001, C-002 | covered |
| **S2 · Growth** | Growth, lo que sí vemos: los primeros pagadores observados y su actividad económica por industria, y el gasto de Marketing por categoría en el tiempo, descritos sin atribuir ventas al gasto.
Growth, lo que no vemos: no todos recorren el funnel igual (propuesta: Assisted, Self Service, Executive). Demanda, calidad, capacidad/atención y post-SQL quedan como explicaciones a contrastar, cada una con el dato que permitiría elegir.
Growth, cómo operarlo: primero definiciones y fuentes comunes; después, seguimiento recurrente por foros (dashboards, análisis ad hoc, agentes), atado a decisiones del CRO que aún no están definidas. | | | |
| S2.1 Las relaciones que comentó Hugo |  | las relaciones que comentó Hugo (por precisar) | — | missing |
| S2.2 Entradas y actividad económica de clientes y segmentos |  | Revisar entradas y actividad económica de clientes y segmentos; inversión de S&M por categoría (generación de demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses y Travel · habilitación, ¿producto?: So… | C-003, C-004 | covered |
| S2.3 Cómo definir y medir el funnel si no todos lo recorren igual | ¿Cómo definir y medir el funnel si no todos lo recorren igual? | cómo definir y medir el funnel si no todos lo recorren igual (self-serve, entrada directa a SQL, estancamientos de semanas): Assisted / Self Service / Executive, con canales (incl. digital, WoM, clientes que no requirie… | C-005, C-021 | covered |
| S2.4 Dónde y en qué segmentos se concentra la pérdida de crecimiento | ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento? | dónde y en qué segmentos se concentra la pérdida de crecimiento (industria, churn, low tickets, mix; quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco volumen) | C-007, C-008 | covered |
| S2.5 Qué métricas propondrías que hoy no existen | ¿Qué métricas propondrías que hoy no existen? | qué métricas propondrías que hoy no existen (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) y cómo medirlas, robustecerlo y bajar lo que tenga sentido | C-006, C-009, C-022, C-010 | covered |
| S2.6 Hipótesis ToFu y BoFu |  | Definir que hipótesis ToFu y BoFu (demanda, calidad, velocidad de atención, conversión post-SQL; p. ej. la capacidad comercial instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó) podrían es… | C-011, C-023, C-012 | covered |
| S2.7 Solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar |  | solución analítica para que el CRO opere el funnel de forma recurrente y qué decisiones le permite tomar (técnica: pulir CRM, analítica digital · decision making: dashboards automatizados por foro, análisis ad hoc, agen… | C-013, C-014 | covered |
| **S3 · Revenue** | Revenue: con solo el monto pagado, cada ejemplo del CFO admite dos lecturas (cambio de suscripción o descuento). Proponemos cómo introducir descuentos temporales y un modelo de datos que separe el valor de la suscripción del precio pagado. | | | |
| S3.1 Qué data observable de pricing introductorio podemos sacar | ¿Qué data observable de pricing introductorio podemos sacar? | qué data observable de pricing introductorio podemos sacar | C-015, C-024 | covered |
| S3.2 Cómo debería Finora introducir descuentos temporales | ¿Cómo debería Finora introducir descuentos temporales? | cómo debería Finora introducir descuentos temporales (mecanismo propuesto, implicaciones multidisciplinarias, preguntas del CFO contestadas con el modelo propuesto) | C-017, C-018 | covered |
| S3.3 Cómo separar el valor de la suscripción del precio efectivamente pagado | ¿Cómo separar el valor de la suscripción del precio efectivamente pagado? | cómo separar el valor de la suscripción del precio efectivamente pagado: propuesta de modelo de datos (campos, tablas, definiciones) | C-019 | covered |
| S3.4 Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales | ¿Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales? | cómo clasificar inicio y fin de un descuento para que no se confundan con contracción o expansión reales (Hugo: probablemente lo integra la misma propuesta de modelo de datos) | C-020, C-025 | covered |

Las láminas `missing` no se diseñan con cifras: si Hugo las quiere en el deck, van como pregunta abierta o se quedan fuera; anótalo en §7.

## 2. Governing thought

> **La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.**

## 3. Pirámide

Lógica: SCR con pilares, siguiendo tu guion aprobado (Overview → Growth → Revenue) — La respuesta va primero y cada lámina sigue el orden lo que vemos → lo que no vemos → propuesta concreta. En Overview, la brecha coincide con quién entra y no con la base previa. En Growth vemos más primeros pagadores, con menor ticket estabilizado dentro de cada industria, y un gasto que no se mueve con ellos. El porqué no está en los pagos, así que proponemos: rutas con etapas literales por canal (S2.3), métricas por funnel y comunes sin duplicados (S2.5), un árbol MECE de la brecha (S2.6) y un modelo de datos as-is vs to-be con foros atados a decisiones (S2.7). En Revenue mostramos qué se lee del monto y qué no, el mecanismo y el modelo de descuentos por origen, la escalera de valor y la regla de clasificación. El cierre responde los casos del CFO con el modelo.

```
Governing thought: La brecha clientes–monto se asocia a quién entra; el porqué no está en los pagos: proponemos medir por funnel y separar descuento de suscripción.
├─ S1 · Overview
│   └─ C-001: Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×
│   └─ C-002: La caída por cliente se asocia a quién entra; la base previa sostiene su monto
├─ S2 · Growth
│   └─ C-003: Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias
│   └─ C-004: Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas
│   └─ C-005: Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar
│   └─ C-021: Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño
│   └─ C-007: La pérdida está en el monto por cliente de cosechas de menor ticket
│   └─ C-008: Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar
│   └─ C-006: Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento
│   └─ C-009: Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta
│   └─ C-022: Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro
│   └─ C-010: Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC
│   └─ C-011: Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha
│   └─ C-023: Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja
│   └─ C-012: Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta
│   └─ C-013: Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción
│   └─ C-014: Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro para preguntas del día a día a través de agentes de IA que permitan generar visualizaciones y hacer análisis adhoc
├─ S3 · Revenue
│   └─ C-015: Lo observable es el primer y segundo pago; el descuento no es verificable
│   └─ C-024: Con cliente, mes y monto se ve qué cambió, no por qué
│   └─ C-017: El descuento se registra como objeto propio, con origen, source y fecha de fin
│   └─ C-018: El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan
│   └─ C-019: La Propuesta de Modelo de datos separa el valor en una escalera con vigencias
│   └─ C-020: Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»
│   └─ C-025: Con el modelo propuesto, cada caso del CFO se lee en su capa
```

## 4. Secuencia

| # | Pregunta de la audiencia | Título (conclusión) | Rol | Claim |
|---|---|---|---|---|
| S01 | ¿Qué tan sano está el modelo si suma clientes mucho más rápido que monto pagado? | Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8× | context | C-001 |
| S02 | ¿El −38% por cliente viene de la base que ya teníamos o de quién entra? | La caída por cliente se asocia a quién entra; la base previa sostiene su monto | diagnosis | C-002 |
| S03 | ¿Qué cambió en quién entra y en qué industrias? | Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias | evidence | C-003 |
| S04 | ¿Hasta dónde se puede relacionar la Inversión en Marketing por categoría con las ventas cruzando fechas? | Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas | evidence | C-004 |
| S05 | ¿Cómo definir el funnel si no todos lo recorren igual? | Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar | recommendation | C-005 |
| S06 | ¿Qué etapas aplican a cada funnel, por canal, literalmente como las del Executive? | Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño | recommendation | C-021 |
| S07 | ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento? | La pérdida está en el monto por cliente de cosechas de menor ticket | diagnosis | C-007 |
| S08 | ¿Hay industrias de bajo churn, ticket alto y poco volumen que valga la pena mirar? | Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar | implication | C-008 |
| S09 | ¿Cómo se mide cada funnel, más allá de la conversión? | Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento | recommendation | C-006 |
| S10 | ¿Qué otras métricas hay que proponer y cómo se mide cada una? | Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta | recommendation | C-009 |
| S11 | ¿Cómo se evita que una métrica aparezca en dos lugares o con dos fórmulas? | Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro | recommendation | C-022 |
| S12 | ¿Podemos calcular el CAC hoy? | Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC | limitation | C-010 |
| S13 | ¿Cuánto de «no más ventas» depende de cómo se cuenta y cuánto es negocio? | Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha | evidence | C-011 |
| S14 | ¿Qué podría explicar «más leads, pero no más ventas», ordenado sin que una causa aparezca en dos lugares? | Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja | recommendation | C-023 |
| S15 | ¿Cómo se sabe si falta capacidad comercial o si bajó la calidad de la máquina de leads? | Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta | recommendation | C-012 |
| S16 | ¿Qué modelo de datos se propone para operar el funnel, as-is vs to-be? | Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción | recommendation | C-013 |
| S17 | ¿Cómo opera el CRO el funnel de forma recurrente y qué decide en cada foro? | Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro para preguntas del día a día a través de agentes de IA que permitan generar visualizaciones y hacer análisis adhoc | recommendation | C-014 |
| S18 | ¿Qué data observable de pricing introductorio podemos sacar? | Lo observable es el primer y segundo pago; el descuento no es verificable | evidence | C-015 |
| S19 | ¿Qué se puede leer del monto pagado y qué no? | Con cliente, mes y monto se ve qué cambió, no por qué | diagnosis | C-024 |
| S20 | ¿Cómo se registra un descuento según su origen (promoción digital con su source, promoción física, negociado, retención, partner o apilado) y cómo pega en el puente? | El descuento se registra como objeto propio, con origen, source y fecha de fin | recommendation | C-017 |
| S21 | ¿Cómo debería Finora introducir descuentos temporales sin perder el porqué del MRR? | El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan | recommendation | C-018 |
| S22 | ¿Cómo separar el valor de la suscripción del precio efectivamente pagado? | La Propuesta de Modelo de datos separa el valor en una escalera con vigencias | recommendation | C-019 |
| S23 | ¿Cómo clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión reales? | Si la suscripción no cambia, inicio o fin de descuento va a «Descuento» | recommendation | C-020 |
| S24 | Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece el descuento: ¿cómo se lee cada caso con el modelo propuesto? | Con el modelo propuesto, cada caso del CFO se lee en su capa | implication | C-025 |

**Read-through (solo títulos):** Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8× → La caída por cliente se asocia a quién entra; la base previa sostiene su monto → Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias → Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas → Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar → Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño → La pérdida está en el monto por cliente de cosechas de menor ticket → Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar → Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento → Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta → Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro → Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC → Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha → Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja → Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta → Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción → Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro para preguntas del día a día a través de agentes de IA que permitan generar visualizaciones y hacer análisis adhoc → Lo observable es el primer y segundo pago; el descuento no es verificable → Con cliente, mes y monto se ve qué cambió, no por qué → El descuento se registra como objeto propio, con origen, source y fecha de fin → El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan → La Propuesta de Modelo de datos separa el valor en una escalera con vigencias → Si la suscripción no cambia, inicio o fin de descuento va a «Descuento» → Con el modelo propuesto, cada caso del CFO se lee en su capa

## 5. Slide briefs

```yaml
slide_id: S01
claim_id: C-001
question: ¿Qué tan sano está el modelo si suma clientes mucho más rápido que monto pagado?
message: Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×
role_in_story: context
support:
- claim: Medidos de punta a punta entre ene-22 y oct-24 sobre la ventana completa, los clientes activos pasan de
    377 a 1.678 (índice 445 en base ene-22) y el MRR pagado de COP 35,0 millones a COP 97,0 millones (índice 277),
    lo que coincide con los múltiplos 4,5× y 2,8× publicados en el Overview.
  type: FACT
  source: F-071
  strength: strong
- claim: El MRR por cliente activo, definido como MRR pagado dividido entre los clientes con pago mayor que cero
    en el mes y expresado en COP tras aplicar la escala fija del campo amount, pasa de COP 92,8 mil en ene-22 a
    COP 57,8 mil en oct-24, una variación de −38%.
  type: FACT
  source: F-072
  strength: strong
- claim: Los clientes activos crecieron más rápido que el MRR pagado entre ene-22 y oct-24.
  type: FACT
  source: F-001 · C-RES-01
  strength: strong
- claim: El MRR por cliente activo de oct-24 es más de 30% menor que el de ene-22.
  type: FACT
  source: F-002 · C-RES-02
  strength: strong
- claim: 'Las cifras de titular del Overview se apoyan en métricas de stock de ventana completa: ene-22 existe como
    mes base con 377 clientes activos, COP 35,0 millones de MRR pagado y COP 92,8 mil por cliente activo; en cambio
    las métricas de flujo se miden desde mar-22, con 272 altas registradas en 2022 (m…'
  type: FACT
  source: F-074
  strength: strong
- claim: Entre ene-22 y oct-24 (ventana completa), los clientes con pago en el mes pasan de 377 a 1.678 (4,5×) y
    el MRR pagado observado, de COP 35,0 millones a COP 97,0 millones (2,8×). El MRR pagado observado por cliente
    activo baja de COP 92,8 mil a COP 57,8 mil (−38%). Esa brecha abre Growth (quién entra) y Revenue (qué se paga
    y por qué cambia).
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-071.yaml
- data/FIN-F-072.yaml
- data/FIN-GROWTH-01.yaml
visual_intent: 'Una línea: MRR pagado por cliente activo, en COP, de ene-22 a oct-24 (T-027): de COP 92,8 mil a
  57,8 mil (−38%). Si hace falta la comparación, en apoyo: clientes activos y MRR pagado en la misma gráfica, cada
  uno con ene-22 = 100 (T-001), las dos líneas juntas.'
must_show:
- 4,5×
- 2,8×
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Los clientes activos crecen 4,5× y el MRR pagado observado, 2,8×
notes: 'Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos.; Es monto pagado observado
  (campo amount con escala fija), no MRR contratado (F-082).; Cliente activo = pago mayor que cero en el mes. Un
  cliente sin pago puede estar cancelado, en pausa o atrasado (F-082).; Es stock con ventana completa desde ene-22;
  los flujos arrancan en mar-22 (F-074).; El −38% no se presenta como deterioro de la salud: todavía no separa la
  mezcla de entrada, el precio y las salidas. · En palabras de Hugo: “Finora suma clientes mucho más rápido que
  monto pagado (4,5× vs 2,8×; ~−38% por cliente activo). Esa brecha abre Growth y Revenue.”'
evidence_gaps: []
```

```yaml
slide_id: S02
claim_id: C-002
question: ¿El −38% por cliente viene de la base que ya teníamos o de quién entra?
message: La caída por cliente se asocia a quién entra; la base previa sostiene su monto
role_in_story: diagnosis
support:
- claim: Entre ene-22 y oct-24 el cambio del MRR por cliente activo de −COP 35,0 mil se reparte entre composición
    de la base, que explica 108% del cambio, y el efecto dentro de las cosechas, que explica −8%; el MRR por cliente
    de los clientes activos en ene-22 pasa de COP 92,8 mil a COP 97,4 mil.
  type: FACT
  source: F-075
  strength: strong
- claim: En oct-24 las cosechas 2023 y 2024 reúnen 65% de los clientes activos y 50% del MRR, con MRR por cliente
    de COP 46,3 mil y COP 43,0 mil, frente a COP 97,4 mil de los clientes activos en ene-22, que conservan 17,8%
    de los clientes activos.
  type: FACT
  source: F-076
  strength: strong
- claim: Entre ene-22 y oct-24 el MRR por cliente activo pasó de COP 92,8 mil a COP 57,8 mil, y la descomposición
    por cosecha asigna a la composición de entrada 108% del cambio y al efecto dentro de las cosechas −8%.
  type: FACT
  source: F-056 · Q2·C-001
  strength: strong
- claim: El MRR por cliente de la base previa en oct-24 (COP 97,4 mil) se ubica por encima del de ene-22 (COP 92,8
    mil), una variación de +5%, y el efecto dentro de las cosechas aporta COP 2,7 mil del cambio del MRR por cliente
    activo.
  type: FACT
  source: F-058 · Q2·C-006
  strength: strong
- claim: Entre dic-22 y oct-24 el MRR por cliente activo cambia −COP 31,7 mil (−35%), de lo cual la composición
    de cosechas explica −COP 26,6 mil (84%) y el efecto dentro de las cosechas −COP 5,2 mil; las cosechas 2023 y
    2024 son 65% de los clientes activos y 50% del MRR en oct-24.
  type: FACT
  source: F-097
  strength: strong
- claim: Entre dic-22 y oct-24 el MRR por cliente activo pasa de COP 89,5 mil a COP 57,8 mil, y la composición de
    cosechas explica −COP 26,6 mil del cambio frente a −COP 5,2 mil del efecto dentro de las cosechas; el MRR por
    cliente de la base previa pasa de COP 97,0 mil a COP 97,4 mil.
  type: FACT
  source: F-092
  strength: strong
- claim: Los clientes existentes no pagan menos y las cosechas 2023–24, de menor ticket, ya son la mayoría de los
    clientes activos.
  type: FACT
  source: F-019 · C-MON-04
  strength: strong
- claim: 'Con base ene-22, la descomposición por cosecha asigna 108% del cambio del MRR pagado observado por cliente
    activo a la composición de la base; con base dic-22, 84%. La cifra depende de la ventana; la dirección no. Los
    clientes activos en ene-22 pasan de COP 92,8 mil a COP 97,4 mil por cliente (+5%), mientras que las cosechas
    2023 y 2024 ya son 65% de los activos y 50% del MRR en oct-24, con COP 46,3 mil y COP 43,0 mil por cliente.
    Propuesta: reportar el monto por cliente siempre partido en base previa y cosechas, con una base de comparación
    fija que decidas tú.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-075.yaml
- data/FIN-F-076.yaml
- data/FIN-F-097.yaml
- data/FIN-F-072.yaml
visual_intent: 'Mezcla que arrastra: la base previa sostiene su monto mientras las cosechas nuevas, con menos monto
  por cliente, ganan peso y bajan el promedio.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: La caída por cliente se asocia a quién entra; la base previa sostiene su monto
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Composición no es causa: no separa
  tipo de cliente, plan, tarifa ni descuento; el panel no trae esas tablas (F-062).; La base de comparación (ene-22
  o dic-22) es una decisión pendiente (X-060).; La salida de pocas cuentas grandes también baja el promedio (F-101,
  F-102) y aquí no se separa.; «Quién entra» describe primeros pagadores observados, no la calidad de los leads.
  · En palabras de Hugo: “Observaciones generales y salud del negocio que introducen las secciones siguientes.”'
evidence_gaps: []
```

```yaml
slide_id: S03
claim_id: C-003
question: ¿Qué cambió en quién entra y en qué industrias?
message: Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias
role_in_story: evidence
support:
- claim: Las altas mensuales pasan de 26 en dic-22 a 60 en ene-23 y el punto más alto del periodo se observa en
    jun-24 con 84.
  type: FACT
  source: F-110
  strength: strong
- claim: Las altas por mes se duplicaron con un escalón a inicios de 2023 y desde ene-23 no muestran una tendencia
    distinguible de cero.
  type: FACT
  source: F-039 · C-ADQ-09
  strength: partial
- claim: Entre 2022 y 2024 las altas por mes cambian +104% mientras el valor inicial incorporado por mes cambia
    +6% medido por run-rate temprano y +17% medido por monto habitual.
  type: FACT
  source: F-113
  strength: strong
- claim: 'El volumen de primeras apariciones y el valor inicial que incorporan no se mueven a la misma velocidad:
    entre 2022 y 2024 las altas por mes cambiaron +104% frente a +6%, +17% y +60% del valor inicial incorporado
    por mes según la normalización usada, y el MRR nuevo por mes pasó de COP 3,5 millones a…'
  type: FACT
  source: F-045 · W2·C-007
  strength: strong
- claim: El valor inicial incorporado por mes creció menos que las altas entre 2022 y 2024 en las tres normalizaciones
    probadas, y entre 2023 y 2024 cambió menos de 10% en todas.
  type: FACT
  source: F-037 · C-ADQ-08
  strength: strong
- claim: En cohortes de ventana limpia, la mediana del segundo pago (M1) de las altas es COP 52,5 mil en 2022, COP
    36,8 mil en 2023 y COP 38,9 mil en 2024, y la mediana del monto usual temprano (M0–M2) pasa de COP 60,9 mil
    en 2022 a COP 36,8 mil en 2023 y COP 37,8 mil en 2024.
  type: FACT
  source: F-160
  strength: partial
- claim: 'El ticket estabilizado no continúa bajando después de 2023: la mediana del segundo pago de las altas de
    2024 (COP 38,9 mil) es mayor que la de 2023 (COP 36,8 mil) y la mediana del monto usual temprano pasa de COP
    36,8 mil a COP 37,8 mil.'
  type: FACT
  source: F-161
  strength: partial
- claim: 'La caída del ticket de entrada entre las cohortes 2022 y 2023 se observa también con el ticket estabilizado:
    la mediana del segundo pago pasa de COP 52,5 mil a COP 36,8 mil y la del monto usual temprano de COP 60,9 mil
    a COP 36,8 mil, mientras la mediana del primer pago pasa de COP 63,0 mil a COP 3…'
  type: FACT
  source: F-162
  strength: partial
- claim: La mediana del monto usual temprano de las altas es menor en 2024 que en 2022 en Producción (COP 55,1 mil
    a COP 37,8 mil), Restaurantes (COP 62,0 mil a COP 48,3 mil), Retail (COP 35,7 mil a COP 25,2 mil), Salud (COP
    63,0 mil a COP 48,8 mil), Servicios profesionales (COP 63,0 mil a COP 31,5 mil) y T…
  type: FACT
  source: F-163
  strength: partial
- claim: Medido con el monto usual temprano, el efecto dentro de las industrias explica 91% del cambio del ticket
    de entrada 2022→2023 y 96% del cambio 2022→2024, frente a 9% y 4% del mix de industrias; el límite inferior
    del intervalo bootstrap del efecto dentro es 84% y 90%.
  type: FACT
  source: F-164
  strength: strong
- claim: Entre 2022 y 2024 la mediana del ticket de entrada baja en 6 industrias y el promedio baja en 6 industrias.
  type: FACT
  source: F-114
  strength: strong
- claim: El aumento de altas por mes entre 2022 y 2024 corresponde a clientes con run-rate inicial menor que la
    mediana de 2022; por encima de esa mediana, las altas por mes no aumentaron.
  type: FACT
  source: F-030 · C-ADQ-07
  strength: strong
- claim: Las altas por mes pasan de 27 en 2022 (mar–dic) a 54 en 2023 y 55 en 2024 (ene–oct).
  type: FACT
  source: F-192
  strength: strong
- claim: Desde ene-23 la pendiente de las altas por mes es +0,47 por mes, con un intervalo de confianza entre −0,40
    y +1,33 que contiene cero.
  type: FACT
  source: F-193
  strength: partial
- claim: 'Los primeros pagadores observados pasan de 27,2 por mes en 2022 (mar–dic) a 54,7 desde ene-23. Es un escalón
    sin tendencia distinguible después: pendiente de +0,47 por mes, con intervalo de −0,40 a +1,33. Entre 2022 y
    2024 suben +104% por mes, mientras el valor inicial que incorporan sube +6% (run-rate temprano) o +17% (monto
    habitual). Con ticket estabilizado, la mediana del segundo pago baja de COP 52,5 mil en 2022 a COP 36,8 mil
    en 2023 y COP 38,9 mil en 2024. El efecto dentro de cada industria explica 91% del cambio 2022→2023 y 96% del
    cambio 2022→2024.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-110.yaml
- data/FIN-F-113.yaml
- data/FIN-F-160.yaml
- data/FIN-F-164.yaml
- data/FIN-F-114.yaml
visual_intent: 'Outgrow: el conteo de primeros pagadores sube en escalón y se aplana, mientras el valor que traen
  crece mucho menos.'
must_show:
- '6 '
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Entran más primeros pagadores, con menor ticket estabilizado, en las 6 industrias
notes: 'Pendiente de tu aceptación; F-160 a F-163 tienen confianza media.; Primer pago observado no es adquisición
  (ni Won ni suscripción activa); el hito lo acuerda el CRO (X-052).; El escalón de inicios de 2023 puede ser en
  parte registro (H-024) o un cambio operativo (H-025, H-068). Sin confirmar.; El ticket estabilizado sigue siendo
  monto pagado: no separa tarifa, plan, empaquetamiento ni descuento (F-167).; La industria es la única segmentación
  disponible: no sustituye al canal ni a la ruta. · En palabras de Hugo: “Revisar entradas y actividad económica
  de clientes y segmentos.”'
evidence_gaps: []
```

```yaml
slide_id: S04
claim_id: C-004
question: ¿Hasta dónde se puede relacionar la Inversión en Marketing por categoría con las ventas cruzando fechas?
message: Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas
role_in_story: evidence
support:
- claim: Entre 2023 ene-may y 2023 jun-dic el S&M por mes pasó de 3,01 a 1,44 en unidad reportada, mientras las
    altas por mes pasaron de 45,2 a 60,6.
  type: FACT
  source: F-214
  strength: partial
- claim: Con un mes de rezago, el mes de mayor S&M (oct-22, 3,75) precede a 19 altas, mientras el mes de menor S&M
    (ago-23, 1,10) precede a 56 altas.
  type: FACT
  source: F-220
  strength: partial
- claim: 'En niveles mensuales, el S&M total se asocia negativamente con las altas: −0,57 en el mismo mes sobre
    32 meses y −0,55 con un mes de rezago sobre 31 meses.'
  type: FACT
  source: F-219
  strength: partial
- claim: Por ventana, las altas por mes van de 27,2 en 2022 mar-dic a 55,4 en 2024 ene-oct, y el S&M por alta va
    de 0,11 a 0,04 en unidad reportada, con su valor menor en 2023 jun-dic (0,02).
  type: FACT
  source: F-221
  strength: partial
- claim: En la composición del S&M, la generación de demanda va de 64% en 2022 S1 a 58% en 2024 jul-oct, la capacidad
    comercial de 26% a 38% y la habilitación de 10% a 4%.
  type: FACT
  source: F-217
  strength: partial
- claim: En 2023 jun-dic las altas por mes son 60,6 frente a 45,2 en 2023 ene-may, mientras el gasto de generación
    de demanda por mes baja de 1,73 u a 0,82 u y el S&M total por mes de 3,01 u a 1,44 u.
  type: FACT
  source: F-107
  strength: partial
- claim: La correlación en niveles entre el S&M total y las altas del mismo mes es −0,57; en cambios mes a mes el
    mayor valor absoluto observado es 0,27 con un valor p mínimo de 0,14, y de 48 pruebas de correlación 9 resultan
    significativas, todas ellas negativas en niveles con las altas.
  type: FACT
  source: F-118
  strength: partial
- claim: Las correlaciones en niveles entre gasto y altas (rezagos 0–1) son todas negativas, y ninguna correlación
    de cambios mes a mes alcanza |r| ≥ 0,3 ni p < 0,05.
  type: FACT
  source: F-023 · C-INV-03
  strength: partial
- claim: Toda correlación con p < 0,05 es una correlación negativa en niveles con las altas.
  type: FACT
  source: F-024 · C-INV-04
  strength: partial
- claim: 'El archivo de gasto de S&M reporta cada rubro en unidades reportadas (u) sin factor de escala: el S&M
    total va de 1,10 u en su valle de ago-23 a 3,45 u en su pico de may-23, magnitudes que no se pueden leer como
    COP.'
  type: FACT
  source: F-063
  strength: strong
- claim: 'El archivo se comporta como una asignación de arriba hacia abajo en su primer tramo: Team equivale a 12%
    del S&M total en 17 meses hasta may-23, y desde jun-23 su participación se mueve entre 19% y 38% con 17 valores
    distintos en 17 meses.'
  type: FACT
  source: F-066
  strength: partial
- claim: Team equivale a una participación exactamente constante del S&M total en 17 meses consecutivos hasta may-23.
  type: FACT
  source: F-115
  strength: strong
- claim: Todos los rubros del archivo de S&M cubren los mismos 34 meses de ene-22 a oct-24 sin valores ausentes,
    pero Freelance queda en cero en 17 de esos meses y PayrollExpenses toma valor negativo en 5.
  type: FACT
  source: F-065
  strength: partial
- claim: 'No es posible decidir con los datos si SoftwareTools y Freelance corresponden a habilitación comercial
    o a gasto de producto: el archivo solo trae el nombre del rubro y su monto mensual, sin centro de costo, proveedor
    ni atribución funcional; agruparlos en Habilitación es una convención del catálog…'
  type: FACT
  source: F-068
  strength: partial
- claim: 'El paso de asociación a efecto entre el gasto de S&M por categoría y los primeros pagos observados no
    es evaluable con estos datos: no hay etapas del funnel con fechas ni fuente del lead que liguen el gasto de
    un mes con clientes concretos, y la unidad del gasto no está documentada.'
  type: FACT
  source: F-119
  strength: partial
- claim: 'El gasto y los primeros pagadores se mueven en sentido contrario en los dos semestres: el gasto no sirve
    como proxy de capacidad ni de leads'
  type: FACT
  source: F-207
  strength: partial
- claim: 'En 2023 jun–dic hay 60,6 primeros pagadores por mes, frente a 45,2 en ene–may. En esos mismos tramos,
    la Generación de Demanda (ToFu) baja de 1,73 u a 0,82 u por mes y el S&M total, de 3,01 u a 1,44 u. La correlación
    en niveles entre S&M total y primeros pagadores del mismo mes es −0,57; en cambios mes a mes, el mayor valor
    absoluto es 0,27 (p mínimo 0,14): no hay una relación positiva que leer. El archivo viene en unidades reportadas
    (u), sin escala a COP, y hasta may-23 Team es un 12% fijo del total durante 17 meses. Propuesta: que Finora
    documente la unidad del gasto y lo registre por canal y campaña (campaign_spend, C-013), para leer el gasto
    contra entradas y Won por cohorte y canal, no cruzando fechas.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-214.yaml
- data/FIN-F-220.yaml
- data/FIN-F-219.yaml
- data/FIN-F-221.yaml
- data/FIN-F-217.yaml
- data/FIN-F-107.yaml
- data/FIN-F-118.yaml
- data/FIN-F-066.yaml
- data/FIN-F-063.yaml
- data/FIN-F-067.yaml
visual_intent: 'Dos paneles con los mismos meses (ene-22 a oct-24): arriba el S&M total por mes (unidad reportada),
  abajo las altas por mes; en 2023 jun-dic el gasto baja mientras las altas suben (T-101). Apoyo: dispersión de
  S&M contra altas con un mes de rezago (F-220, T-107) y barras por ventana de altas por mes y S&M por alta (T-108).
  Sin atribuir ventas al gasto.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Gasto de S&M y primeros pagadores van en sentidos distintos; cruzar fechas no atribuye ventas
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; La unidad del gasto no está documentada
  (F-063): no se puede leer como COP.; Hasta may-23 el archivo se comporta como una asignación de arriba hacia abajo
  (F-066); PayrollExpenses es negativo en 5 meses y Freelance queda en cero desde jun-23 (T-009).; No se puede decidir
  si SoftwareTools y Freelance son Habilitación o producto (F-068).; Es coincidencia temporal, no efecto (F-119,
  F-222). El valle de ago-23 y el corte de jun-23 pueden ser contables (H-023, H-070, H-071). · En palabras de Hugo:
  “Inversión de S&M por categoría (generación de demanda ToFu: Paid Media y publicidad no web · Team: Payroll Expenses
  y Travel · habilitación, ¿producto?: Software Tools y Freelance) y hasta dónde se puede relacionar con ventas
  cruzando fechas.”'
evidence_gaps: []
```

```yaml
slide_id: S05
claim_id: C-005
question: ¿Cómo definir el funnel si no todos lo recorren igual?
message: Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar
role_in_story: recommendation
support:
- claim: 'Regla MECE que respeta las definiciones de Hugo: la ruta sale de quién movió cada tramo, y la puerta de
    entrada queda aparte, fija al entrar.'
  type: FACT
  source: F-209
  strength: partial
- claim: 'Q-063: propongo que solo cuente como intervención la interacción de ida y vuelta con SDR/AE. El formulario
    de «hablar con ventas» es la entrada, no un tramo sin persona.'
  type: FACT
  source: F-210
  strength: partial
- claim: 'Reactivate funciona como loop sobre episodios estancados, no como cuarta ruta: conserva fecha y puerta,
    y el primer pago cuenta una sola vez en su ruta, con bandera.'
  type: FACT
  source: F-211
  strength: partial
- claim: 'Las tasas se comparan entre puertas, que son fijas al entrar, no entre rutas: la ruta se define por lo
    que pasó, y eso sesga por construcción la conversión de Hybrid (H-050).'
  type: FACT
  source: F-212
  strength: strong
- claim: Con los datos de hoy solo se miden el nudo y la vuelta de pagadores. Esa vuelta es un loop de Revenue,
    en parte es timing de pago, y no debe llamarse Reactivate.
  type: FACT
  source: F-213
  strength: strong
- claim: La puerta se asigna al abrir el episodio, con información previa al contacto, y no se cambia. Lo que pasa
    después (contacto humano, escalamiento) se registra aparte.
  type: FACT
  source: F-188
  strength: partial
- claim: El único nudo común que se puede medir hoy es el primer pago. Won solo existe en las puertas con vendedor,
    y cambiar el nudo a «sigue pagando en M1» mueve poco el conteo.
  type: FACT
  source: F-190
  strength: partial
- claim: 'No es un funnel: son tres puertas con hitos propios que llegan a un nudo común (primer pago) y a un lado
    derecho común. AAARRR sirve como vocabulario, no como secuencia.'
  type: FACT
  source: F-140
  strength: partial
- claim: Entre Executive, Self Service y Hybrid solo se compara del nudo hacia la derecha. Antes del nudo, cada
    funnel tiene su propia unidad, sus etapas y sus tiempos, y sus tasas no se comparan ni se promedian.
  type: FACT
  source: F-155
  strength: strong
- claim: 'Hoy no se puede medir ningún funnel antes del primer pago: el modelo no tiene leads, etapas, dueños, canal
    ni ruta.'
  type: FACT
  source: F-223
  strength: strong
- claim: La única comparación válida entre rutas es por puerta, con cohorte y ventana fija. La ruta se clasifica
    al final con una regla por eventos, y las métricas de etapa se leen dentro de cada ruta.
  type: FACT
  source: F-224
  strength: partial
- claim: Reactivate (leads estancados) y la reactivación del puente de MRR (clientes que vuelven a pagar) son poblaciones
    distintas y hay que medirlas por separado.
  type: FACT
  source: F-226
  strength: partial
- claim: 'La unidad es el journey: cuenta × intento (varias personas de una misma empresa son un solo journey).
    Al entrar se fijan dos atributos que ya no cambian: la puerta (producto o CRM/Ventas) y el canal (outbound SDR,
    inbound «hablar con ventas», referido o partner, o signup por paid media, publicidad no web u orgánico). La
    ruta se clasifica al final, por eventos: Executive si arranca con persona y nunca pasa por Checkout Self; Self
    Service si nunca interviene una persona; Hybrid A si arranca en el producto y después entra una persona; Hybrid
    B si arranca con persona y cierra por Checkout Self. Mientras el journey está abierto, la ruta es provisional.
    Reactivate no es otra ruta: es un loop para journeys estancados, con bandera, que no crea un New nuevo. Los
    clientes que vuelven a pagar son un loop de Revenue y se miden aparte.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Split y converge: una entrada con puerta y canal fijos se abre en rutas según quién mueve cada tramo,
  y todas llegan al mismo nudo. Reactivate aparece como un loop que devuelve el journey a la etapa donde se estancó.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Proponemos rutas Executive, Self Service e Hybrid, con puerta y canal fijos al entrar
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Es propuesta: hoy el modelo no
  tiene leads, etapas, dueños, canal ni ruta (F-223).; Qué cuenta como intervención de persona sigue abierto (Q-063).
  Con la regla actual, una entrada que pide persona y que nadie atiende termina como Self Service (H-072).; No sabemos
  si existe compra self-serve sin persona, ni si hay prueba gratis, freemium o pago al registrarse (Q-046).; La
  ruta no se infiere del monto. La tasa de Hybrid refleja a quién eligen tocar SDR/AE (H-050): por eso las tasas
  se comparan entre puertas, no entre rutas. · En palabras de Hugo: “Assisted / Self Service / Executive, con canales
  (incl. digital, WoM, clientes que no requirieron KAM), funnel propuesto.”'
evidence_gaps: []
```

```yaml
slide_id: S06
claim_id: C-021
question: ¿Qué etapas aplican a cada funnel, por canal, literalmente como las del Executive?
message: Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño
role_in_story: recommendation
support:
- claim: 'Regla MECE que respeta las definiciones de Hugo: la ruta sale de quién movió cada tramo, y la puerta de
    entrada queda aparte, fija al entrar.'
  type: FACT
  source: F-209
  strength: partial
- claim: 'Q-063: propongo que solo cuente como intervención la interacción de ida y vuelta con SDR/AE. El formulario
    de «hablar con ventas» es la entrada, no un tramo sin persona.'
  type: FACT
  source: F-210
  strength: partial
- claim: 'Reactivate funciona como loop sobre episodios estancados, no como cuarta ruta: conserva fecha y puerta,
    y el primer pago cuenta una sola vez en su ruta, con bandera.'
  type: FACT
  source: F-211
  strength: partial
- claim: 'Hoy no se puede medir ningún funnel antes del primer pago: el modelo no tiene leads, etapas, dueños, canal
    ni ruta.'
  type: FACT
  source: F-223
  strength: strong
- claim: La única comparación válida entre rutas es por puerta, con cohorte y ventana fija. La ruta se clasifica
    al final con una regla por eventos, y las métricas de etapa se leen dentro de cada ruta.
  type: FACT
  source: F-224
  strength: partial
- claim: Para medir velocidad y estancamiento hacen falta fechas de entrada y salida por etapa y la fecha de última
    actividad. El umbral de estancamiento se calibra por etapa y se acuerda con Finora (Q-064).
  type: FACT
  source: F-225
  strength: partial
- claim: Hoy no se puede medir ninguna etapa antes del primer pago, ni la puerta. La prueba más rápida es que Finora
    etiquete hacia atrás, desde el CRM, a los pagadores 2022–2024.
  type: FACT
  source: F-191
  strength: strong
- claim: Entre Executive, Self Service y Hybrid solo se compara del nudo hacia la derecha. Antes del nudo, cada
    funnel tiene su propia unidad, sus etapas y sus tiempos, y sus tasas no se comparan ni se promedian.
  type: FACT
  source: F-155
  strength: strong
- claim: 'Por ruta y canal, en orden y con dueño. Es propuesta; solo Executive outbound es literal tuyo. EXECUTIVE
    · outbound SDR: New → Working SDR → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won; el SDR es dueño hasta
    SQL SDR y el AE desde Demo AE · inbound «hablar con ventas» (paid media, publicidad no web u orgánico): New
    → Engaged SDR → SQL SDR → Demo AE → Proposal AE → Won; se salta Working SDR porque la cuenta levantó la mano
    · referido o partner (tu WoM, por confirmar): New → Demo AE → Proposal AE → Won, solo con AE. SELF SERVICE ·
    signup en producto (paid media, publicidad no web u orgánico): New → Signup Self → Activated Self → Checkout
    Self → Won; dueño Growth/Producto, por confirmar; si no hay prueba ni registro antes del pago, queda New → Checkout
    Self → Won. HYBRID A · signup en producto: New → Signup Self → Activated Self → Engaged SDR → SQL SDR → Demo
    AE → Proposal AE → Won; pasa de Growth/Producto al SDR y al AE; la persona entra por una señal de uso, fit o
    intención, o porque la cuenta pide ayuda; Engaged SDR y SQL SDR se pueden saltar; variante: la persona ayuda
    y la cuenta paga sola por Checkout Self. HYBRID B · outbound SDR: New → Working SDR → Engaged SDR → SQL SDR
    → Demo AE → Checkout Self → Won; pasa del SDR al AE y la cuenta cierra sola; Demo AE se puede saltar · inbound
    «hablar con ventas»: lo mismo, sin Working SDR. REACTIVATE (loop): un journey estancado en cualquier etapa abierta
    entra al loop y, si se re-engancha, vuelve a su etapa con su puerta y su ruta. QUÉ DEL EXECUTIVE APLICA A LOS
    OTROS: New y Won aplican a todas las rutas. Working SDR solo donde hay prospección outbound (Executive e Hybrid
    B outbound). Engaged SDR, SQL SDR y Demo AE aplican a Executive, a Hybrid A (se pueden saltar) y a Hybrid B.
    Proposal AE aplica a Executive y a Hybrid A; en Hybrid B la reemplaza Checkout Self. Self Service no usa ninguna
    etapa de SDR ni de AE: las cambia por Signup Self, Activated Self y Checkout Self.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Reusar o reemplazar: qué etapas del Executive reusa cada ruta, cuáles salta y cuáles cambia por
  etapas de producto, con el traspaso de dueño (SDR → AE → cliente) visible en cada ruta.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Cada ruta usa las etapas del Executive que le aplican, por canal y con dueño
notes: 'Pendiente de tu aceptación: F-209 a F-211 y F-223 a F-225 están propuestos.; No afirmamos que Finora tenga
  criterios de etapa definidos: el brief da la secuencia y un traspaso SDR → AE que ocurre «sobre todo» y «normalmente».
  Demo y Proposal hay que confirmarlas contra el CRM.; Las etapas de Self Service e Hybrid son propuesta. Activated
  Self se define con Producto, y no sabemos si hay prueba, freemium o pago al registrarse (Q-046).; La frontera
  entre Executive inbound e Hybrid A depende de Q-063. Una variante de Hybrid B (el SDR contacta y la cuenta se
  registra sola) es Hybrid B con la regla laxa y Self Service con la estricta.; Faltan por confirmar el canal referido/partner
  y el dueño de Self Service. Parte de los saltos de etapa puede ser registro del CRM (H-051). · En palabras de
  Hugo: “«queria ver una prouesta aterrizada por casuistica de canal literalmente de los funeles asi como te pase
  la de new, working, SDR, engaged, bla bla quiero ver cuales aplican para los otros»”'
evidence_gaps: []
```

```yaml
slide_id: S07
claim_id: C-007
question: ¿Dónde y en qué segmentos se concentra la pérdida de crecimiento?
message: La pérdida está en el monto por cliente de cosechas de menor ticket
role_in_story: diagnosis
support:
- claim: Entre dic-22 y oct-24 el MRR por cliente activo cambia −COP 31,7 mil (−35%), de lo cual la composición
    de cosechas explica −COP 26,6 mil (84%) y el efecto dentro de las cosechas −COP 5,2 mil; las cosechas 2023 y
    2024 son 65% de los clientes activos y 50% del MRR en oct-24.
  type: FACT
  source: F-097
  strength: strong
- claim: Entre dic-22 y oct-24 el MRR por cliente activo pasa de COP 89,5 mil a COP 57,8 mil, y la composición de
    cosechas explica −COP 26,6 mil del cambio frente a −COP 5,2 mil del efecto dentro de las cosechas; el MRR por
    cliente de la base previa pasa de COP 97,0 mil a COP 97,4 mil.
  type: FACT
  source: F-092
  strength: strong
- claim: 'La caída del MRR por cliente activo no se concentra en una industria: bajó en las 6 industrias entre dic-22
    y oct-24, y el ticket de entrada promedio y mediano bajó también en las 6 industrias entre 2022 y 2024.'
  type: FACT
  source: F-096
  strength: strong
- claim: Entre dic-22 y oct-24 el MRR por cliente activo cae −46,6% en Servicios profesionales, −45,6% en Restaurantes
    y −43,1% en Retail, frente a −18,8% en Producción, −15,5% en Tecnología y −14,4% en Salud.
  type: FACT
  source: F-094
  strength: partial
- claim: El MRR por cliente activo bajó en las seis industrias entre dic-22 y oct-24.
  type: FACT
  source: F-020 · C-MON-05
  strength: strong
- claim: Medido con el monto usual temprano, el efecto dentro de las industrias explica 91% del cambio del ticket
    de entrada 2022→2023 y 96% del cambio 2022→2024, frente a 9% y 4% del mix de industrias; el límite inferior
    del intervalo bootstrap del efecto dentro es 84% y 90%.
  type: FACT
  source: F-164
  strength: strong
- claim: La mediana del monto usual temprano de las altas es menor en 2024 que en 2022 en Producción (COP 55,1 mil
    a COP 37,8 mil), Restaurantes (COP 62,0 mil a COP 48,3 mil), Retail (COP 35,7 mil a COP 25,2 mil), Salud (COP
    63,0 mil a COP 48,8 mil), Servicios profesionales (COP 63,0 mil a COP 31,5 mil) y T…
  type: FACT
  source: F-163
  strength: partial
- claim: Entre ene-22 y oct-24 el cambio del MRR por cliente activo de −COP 35,0 mil se reparte entre composición
    de la base, que explica 108% del cambio, y el efecto dentro de las cosechas, que explica −8%; el MRR por cliente
    de los clientes activos en ene-22 pasa de COP 92,8 mil a COP 97,4 mil.
  type: FACT
  source: F-075
  strength: strong
- claim: El churn observado bajó más de un punto entre 2022 y 2024, mientras el churn que no vuelve a pagar en tres
    meses cambió menos de 0,3 puntos.
  type: FACT
  source: F-033 · C-RET-03
  strength: strong
- claim: 'El churn observado bajó entre 2022 y 2024 mientras el churn que no vuelve a pagar en el trimestre siguiente
    se mantuvo: pasó de 3,52% a 2,04% el observado y de 0,98% a 0,96% el que no vuelve.'
  type: FACT
  source: F-183
  strength: strong
- claim: Con base dic-22, el efecto dentro de las cosechas aporta −COP 5,2 mil del cambio del MRR por cliente activo
    (16% del total), concentrado en la cosecha 2022 (−COP 3,7 mil) y en las altas de feb-22 (−COP 1,6 mil).
  type: FACT
  source: F-059 · Q2·C-007
  strength: strong
- claim: 'Quienes hacen churn pagaban en promedio más que el cliente activo del mes previo: la razón de medias es
    1,70 en 2022, 1,58 en 2023 y 1,37 en 2024, con límites inferiores del intervalo bootstrap de 1,26, 1,18 e 1,10.'
  type: FACT
  source: F-101
  strength: strong
- claim: 'Medido por la mediana, quienes hacen churn no pagaban más: la razón de medianas es 1,00 en 2022, 0,97
    en 2023 y 1,11 en 2024, con intervalos que van de 0,97 a 1,15 en el total, de modo que la diferencia de promedios
    se concentra en pocas cuentas grandes.'
  type: FACT
  source: F-102
  strength: strong
- claim: 'No se concentra en una industria: el MRR pagado observado por cliente activo bajó en las 6 entre dic-22
    y oct-24. Cayó más en Servicios profesionales (−46,6%), Restaurantes (−45,6%) y Retail (−43,1%) que en Producción
    (−18,8%), Tecnología (−15,5%) y Salud (−14,4%). Se asocia a cosechas: con base dic-22, la composición explica
    84% del cambio, y el menor ticket de entrada ocurre dentro de cada industria (96% del cambio 2022→2024). No
    se asocia a salidas persistentes: el churn observado baja de 3,52% a 2,04%, mientras que el de quienes no vuelven
    a pagar en un trimestre queda en 0,98% y 0,96%.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-094.yaml
- data/FIN-F-096.yaml
- data/FIN-F-164.yaml
- data/FIN-F-097.yaml
- data/FIN-F-075.yaml
- data/CFO-03.yaml
visual_intent: 'Difusión contra concentración: la caída aparece en todas las industrias con distinta intensidad,
  mientras que el peso de las cosechas de menor ticket es lo que la concentra.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: La pérdida está en el monto por cliente de cosechas de menor ticket
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; La industria es una segmentación
  disponible, no un sustituto de canal ni de ruta; no se afirma una causa industrial.; No hay tamaño de cliente,
  motivos de churn ni estado de suscripción (F-106).; Quienes se van pagaban más en promedio, pero no en mediana:
  la salida de pocas cuentas grandes también baja el promedio (F-101, F-102).; La cifra de composición depende de
  la base elegida (X-060). · En palabras de Hugo: “Dónde y en qué segmentos se concentra la pérdida de crecimiento
  (industria, churn, low tickets, mix).”'
evidence_gaps: []
```

```yaml
slide_id: S08
claim_id: C-008
question: ¿Hay industrias de bajo churn, ticket alto y poco volumen que valga la pena mirar?
message: 'Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar'
role_in_story: implication
support:
- claim: 'Salud combina el menor churn persistente (0,56 puntos porcentuales mensuales), el mayor ticket de entrada
    mediano de 2024 (COP 52,5 mil, igualado con Restaurantes) y el menor volumen: 124 clientes activos en oct-24
    frente a 459 en Restaurantes.'
  type: FACT
  source: F-104
  strength: partial
- claim: 'El ticket de entrada mediano de 2024 en Retail (COP 26,2 mil) y en Servicios profesionales (COP 31,5 mil)
    queda por debajo del de Salud (COP 52,5 mil) y Restaurantes (COP 52,5 mil), mientras Retail suma 360 clientes
    activos en oct-24 frente a 124 en Salud: el volumen incorporado se asocia con el me…'
  type: FACT
  source: F-099
  strength: partial
- claim: En 2024 el churn observado por industria va de 1,46 en Restaurantes a 2,57 en Tecnología, y medido solo
    por churns que no vuelven a pagar en un trimestre va de 0,56 en Salud a 1,33 en Retail (puntos porcentuales
    mensuales).
  type: FACT
  source: F-103
  strength: partial
- claim: Salud y Tecnología son también las industrias con menor caída del MRR por cliente entre dic-22 y oct-24
    (−14,4% y −15,5%) y aportan 11,7% y 17,0% del crecimiento del MRR, con 124 y 206 clientes activos en oct-24.
  type: FACT
  source: F-105
  strength: partial
- claim: 'Salud es la excepción en el tramo 2022→2023: su mediana del monto usual temprano es COP 63,0 mil en 2022
    y COP 63,0 mil en 2023, mientras su promedio pasa de COP 62,5 mil a COP 67,0 mil; el descenso de esa industria
    aparece solo en 2024 (COP 48,8 mil).'
  type: FACT
  source: F-165
  strength: partial
- claim: 'Salud combina el menor churn persistente (0,56 puntos porcentuales mensuales), el ticket de entrada mediano
    más alto de 2024 (COP 52,5 mil, empatado con Restaurantes) y poco volumen: 124 clientes activos en oct-24 frente
    a 459 en Restaurantes. Es además de las industrias con menor caída del MRR por cliente entre dic-22 y oct-24
    (−14,4%) y aporta 11,7% del crecimiento del MRR. En 2024 el churn observado por industria va de 1,46 a 2,57
    puntos mensuales: un rango estrecho. Es una señal para validar con tamaño, canal y motivos de salida, no un
    segmento.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-104.yaml
- data/FIN-F-105.yaml
- data/FIN-F-165.yaml
- data/FIN-F-103.yaml
visual_intent: 'Trade-off: churn persistente contra ticket de entrada, con el tamaño de la base como volumen; Salud
  queda aislada en bajo churn, ticket alto y poco volumen.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: 'Salud combina menor churn persistente, ticket alto y poco volumen: señal a validar'
notes: 'Pendiente de tu aceptación: F-104, F-099, F-103, F-105 y F-165 están propuestos (confianza media).; Con
  pocos clientes por industria, las medianas se mueven con pocas altas.; Salud es la excepción del tramo 2022→2023:
  su ticket baja recién en 2024 (T-067).; No se fabrica un segmento por clustering: no hay concentración clara (H-044
  sigue abierta). · En palabras de Hugo: “Quizá una matriz de burbuja: industrias de bajo churn, ticket alto y poco
  volumen.”'
evidence_gaps: []
```

```yaml
slide_id: S09
claim_id: C-006
question: ¿Cómo se mide cada funnel, más allá de la conversión?
message: Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento
role_in_story: recommendation
support:
- claim: 'Hoy no se puede medir ningún funnel antes del primer pago: el modelo no tiene leads, etapas, dueños, canal
    ni ruta.'
  type: FACT
  source: F-223
  strength: strong
- claim: La única comparación válida entre rutas es por puerta, con cohorte y ventana fija. La ruta se clasifica
    al final con una regla por eventos, y las métricas de etapa se leen dentro de cada ruta.
  type: FACT
  source: F-224
  strength: partial
- claim: Para medir velocidad y estancamiento hacen falta fechas de entrada y salida por etapa y la fecha de última
    actividad. El umbral de estancamiento se calibra por etapa y se acuerda con Finora (Q-064).
  type: FACT
  source: F-225
  strength: partial
- claim: Reactivate (leads estancados) y la reactivación del puente de MRR (clientes que vuelven a pagar) son poblaciones
    distintas y hay que medirlas por separado.
  type: FACT
  source: F-226
  strength: partial
- claim: Valor y calidad por ruta son lo que le importa al CFO, y hoy solo existen agregados.
  type: FACT
  source: F-227
  strength: partial
- claim: La conversión que sirve es por cohorte de entrada, con ventana fija y solo en cohortes que ya la cumplieron.
    La tasa de período y el promedio de solo los que convirtieron castigan a las entradas recientes, y ese es justo
    el test de H-003.
  type: FACT
  source: F-141
  strength: strong
- claim: Las tasas se miden por cohorte con una ventana fija por motion, y los resultados comunes por cohorte de
    primer pago a M3/M6/M12. Así se separa un retraso (HC3a) de una brecha persistente (HC3b), y un cambio de mezcla
    no parece un cambio de desempeño.
  type: FACT
  source: F-158
  strength: strong
- claim: Entre Executive, Self Service y Hybrid solo se compara del nudo hacia la derecha. Antes del nudo, cada
    funnel tiene su propia unidad, sus etapas y sus tiempos, y sus tasas no se comparan ni se promedian.
  type: FACT
  source: F-155
  strength: strong
- claim: 'Las tasas se comparan entre puertas, que son fijas al entrar, no entre rutas: la ruta se define por lo
    que pasó, y eso sesga por construcción la conversión de Hybrid (H-050).'
  type: FACT
  source: F-212
  strength: strong
- claim: 'Para medir el lado izquierdo hay que instrumentar en origen: fechas por etapa en el CRM, puerta y canal
    por cuenta, y gasto por canal. Aun así, la atribución reparte crédito, no prueba causa.'
  type: FACT
  source: F-144
  strength: strong
- claim: Con los datos de hoy solo se miden el nudo y la vuelta de pagadores. Esa vuelta es un loop de Revenue,
    en parte es timing de pago, y no debe llamarse Reactivate.
  type: FACT
  source: F-213
  strength: strong
- claim: 'Sale directo de las etapas de C-021. Notación: journey = cuenta × intento; cohorte = los journeys con
    New en el mes; W = ventana fija desde New, que Finora calibra con su ciclo real. Toda tasa se lee por cohorte
    y solo cuando la cohorte ya cumplió W. CAPA COMÚN, por puerta y canal (es la única que se compara entre funnels).
    Volumen: entradas = journeys con New en el mes, por puerta y canal (p. ej., leads digitales = entradas con canal
    paid media u orgánico); Won por puerta y ruta, con su mezcla = Won de la ruta ÷ Won de la puerta. Calidad al
    entrar: entradas válidas = entradas menos duplicados, clientes actuales y ex-clientes (se marcan aparte) y spam;
    tasa de no-prospectos = lo quitado ÷ entradas; mezcla de ajuste = entradas de ajuste alto ÷ entradas válidas,
    con criterios congelados al crear el lead. Conversión: win rate de cohorte = journeys de la cohorte con Won
    dentro de W ÷ journeys de la cohorte (p. ej., CR digital = ese cociente para las entradas digitales). Velocidad:
    tiempo de cierre = mediana y P75 de los días de New a Won de los ganados, siempre por ruta y junto al win rate;
    Won → primer pago = mediana del tiempo entre ambos y parte de los Won sin pago en el plazo acordado. Valor:
    MRR de entrada por Won = mediana del MRR contratado y del primer pago; MRR nuevo = Won × MRR de entrada por
    Won. POR RUTA, sobre sus etapas literales (se lee solo dentro de la ruta). Volumen por etapa = journeys que
    alcanzan o se saltan la etapa. Conversión por etapa = de quienes alcanzaron una etapa, los que alcanzan la siguiente
    en N días ÷ quienes la alcanzaron. Tiempo en etapa = mediana y P75 de los días entre entrar y salir. Estancamiento
    = abiertos en la etapa sin cambio ni actividad por más de su umbral ÷ abiertos en la etapa. Calidad del handoff
    = lo que acepta el siguiente dueño ÷ lo que recibe (p. ej., SQL aceptados por el AE ÷ SQL SDR). En Executive
    pesan el tiempo de cierre y el estancamiento de SQL SDR a Proposal AE; en Self Service, Signup → Activated →
    Checkout Self, sin handoff; en Hybrid A, además, el paso de producto a SDR; en Hybrid B, Demo AE → Checkout
    Self. LOOP REACTIVATE: entradas al loop; re-enganche = los que vuelven a moverse de etapa ÷ los que entraron;
    tiempo a re-enganche; Won y MRR atribuidos al loop; stock de estancados sin tocar. HOY no se calcula nada de
    esto antes del pago: solo existen, sin puerta ni ruta, el total de primeros pagos observados y su monto (C-003).
    La retención y el costo por Won viven en las métricas comunes (C-009).'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Converge: cada funnel lleva sus métricas por familia en su propio tramo, y todos desembocan en el
  mismo nudo (Won y primer pago), el único lugar donde se comparan por puerta.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Proponemos medir cada funnel por volumen, conversión, velocidad, valor, calidad y estancamiento
notes: 'Pendiente de tu aceptación: F-223 a F-227 y los demás findings citados están propuestos.; Hoy no se calcula
  ninguna métrica antes del pago (F-223): es diseño.; W, el umbral de estancamiento por etapa y el plazo Won → pago
  son parámetros a acordar con Finora, no estándares de mercado (Q-064).; Won o primer pago como hito de adquisición
  sigue por acordar con el CRO.; La conversión de Hybrid refleja a quién eligen tocar SDR/AE, no lo que aporta la
  persona (H-050). Las tasas de etapas intermedias no se comparan entre rutas (SQL contra activación). · En palabras
  de Hugo: “«¿cada funnel? ¿cómo lo mides? no me refiero a solo medir la connversión, ¿que metricas hay en todo
  eso? Ej. Digital podría tener digital leads y CR digital, algo asi, Executive ya sabes que tiens New, pero tambien
  puedes tener métricas de tiempo de cierre»”'
evidence_gaps: []
```

```yaml
slide_id: S10
claim_id: C-009
question: ¿Qué otras métricas hay que proponer y cómo se mide cada una?
message: 'Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta'
role_in_story: recommendation
support:
- claim: 'En verde (se puede calcular hoy, con nombre honesto): MRR pagado observado y su puente, clientes activos,
    ARPA por cliente, churn observado, NRR/GRR de la base y métricas de cohorte.'
  type: FACT
  source: F-135
  strength: strong
- claim: 'El monto pagado mezcla fecha de cobro con mes de servicio: los atrasos y los pagos multimes inflan el
    churn, la reactivación y la expansión observados. Antes de llamarlos churn o MRR hace falta una regla de normalización
    y una ventana de gracia.'
  type: FACT
  source: F-136
  strength: strong
- claim: 'El «ARPU» de hoy es en realidad ARPA (por cliente, no por usuario), y su caída total mezcla cohortes:
    hay que reportarlo por cohorte y medir el ARPA de entrada con un monto estabilizado (M1 o monto usual), no con
    el primer pago.'
  type: FACT
  source: F-139
  strength: partial
- claim: El churn observado bajó más de un punto entre 2022 y 2024, mientras el churn que no vuelve a pagar en tres
    meses cambió menos de 0,3 puntos.
  type: FACT
  source: F-033 · C-RET-03
  strength: strong
- claim: 'El CAC solo existe como «S&M por alta en unidades reportadas»: sin la unidad del gasto no hay CAC en COP,
    ni payback, ni LTV:CAC, y sin motion o canal no hay CAC por Self Service/Assisted/Executive ni por Digital/KAM.'
  type: FACT
  source: F-137
  strength: partial
- claim: El LTV con margen y el UCM están en rojo (necesitan margen bruto o costo de servir). Lo que se puede defender
    hoy es un «LTV empírico de ingreso» a horizonte fijo por cohorte.
  type: FACT
  source: F-138
  strength: partial
- claim: 'El churn observado bajó entre 2022 y 2024 mientras el churn que no vuelve a pagar en el trimestre siguiente
    se mantuvo: pasó de 3,52% a 2,04% el observado y de 0,98% a 0,96% el que no vuelve.'
  type: FACT
  source: F-183
  strength: strong
- claim: El churn observado pasó de 3,52% en 2022 a 2,04% en 2024, mientras el churn que no vuelve a pagar en el
    plazo de seguimiento pasó de 0,98% a 0,96%.
  type: FACT
  source: F-175
  strength: strong
- claim: El churn mensual observado de logos baja de 3,5% en 2022 a 1,9% en 2024, mientras el churn que no vuelve
    a pagar en un plazo de un trimestre pasa de 0,98% a 0,96%, y 44% de los churns observados vuelve a pagar al
    mes siguiente.
  type: FACT
  source: F-079
  strength: strong
- claim: 'Incluso después del pago, el as-is no separa estados que C-009 necesita: cancelación vs mora, prepago
    vs expansión, y plan vs precio vs descuento.'
  type: FACT
  source: F-239
  strength: strong
- claim: 'El to-be de la hipótesis de trabajo se sostiene con patrones estándar, con tres ajustes: espina de identidad,
    puerta separada de ruta, y suscripción dividida en contratado, descontado, facturado y cobrado.'
  type: FACT
  source: F-240
  strength: partial
- claim: 'A tu lista (MRR, ARR, ARPU, CAC, LTV, Churn, UCM) se suman el churn persistente, las capas de lista, descuento
    y neto, el quick ratio, NRR/GRR, el payback y LTV:CAC. Regla MECE: cada métrica vive en un solo lugar. Lo que
    pasa hasta Won y el primer pago está en el funnel (C-006); lo que pasa con la cuenta que ya paga está aquí,
    como común. Puerta, ruta, canal, industria y cohorte son cortes, no métricas nuevas. Semáforo: verde = se calcula
    hoy con nombre honesto; amarillo = proxy con una regla por aprobar; rojo = falta el dato. RESULTADO · MRR pagado
    observado = suma de lo pagado en el mes (verde) · MRR normalizado = cada pago repartido entre los meses que
    cubre (amarillo) · ARR run-rate = MRR normalizado anualizado (amarillo) · MRR de lista, descuento recurrente
    y MRR neto = lista − descuento; el descuento es el revenue que dejamos de capturar (rojo, se detalla en S3).
    MOVIMIENTO · puente: MRR nuevo + expansión + reactivación − contracción − churn = cambio del MRR (verde sobre
    monto pagado, se lee con cuidado); en el to-be suma la línea Descuento y deja el efecto de cobro fuera del MRR
    · quick ratio = entradas ÷ salidas del puente, trimestral (verde). CLIENTES · clientes activos = clientes con
    pago en el mes (verde) · churn de logos observado = los que dejan de pagar ÷ activos del mes previo (verde)
    · churn persistente = los que no vuelven a pagar en un trimestre ÷ activos del mes previo (amarillo): 3,52%
    contra 0,98% en 2022 y 2,04% contra 0,96% en 2024 · reactivaciones, como loop de Revenue (verde) · ARPA = MRR
    ÷ clientes activos, por cohorte; es lo que se pide como ARPU (verde; por usuario, rojo). RETENCIÓN POR COHORTE
    DE PRIMER PAGO · logos que siguen pagando en M3, M6 y M12 (verde) · NRR = MRR actual de la cohorte ÷ su MRR
    inicial · GRR = lo mismo sin expansión (verdes sobre monto pagado, no contractuales). EFICIENCIA · CAC = gasto
    de S&M ÷ nuevas cuentas; por canal y ruta = gasto del canal ÷ Won del canal (hoy solo el proxy de C-010) · payback
    = CAC ÷ (valor de entrada × margen bruto), en meses (rojo) · LTV empírico de ingreso = ingreso acumulado por
    alta a horizonte fijo, por cohorte (verde) · LTV con margen y LTV:CAC (rojos) · UCM = ARPA − costo variable
    de servir (rojo).'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data:
- data/CFO-03.yaml
- data/FIN-F-183.yaml
- data/FIN-F-079.yaml
visual_intent: 'Árbol de ingreso recurrente: el resultado se abre en movimiento, clientes, retención y eficiencia;
  cada hoja está en un solo lugar, con su color de semáforo.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: 'Proponemos métricas comunes MECE con semáforo: qué se mide hoy y qué falta'
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; El monto pagado mezcla fecha de
  cobro y mes de servicio: el churn, la reactivación y la expansión observados salen inflados (F-136). La retención
  aquí es «sigue pagando», no retención contractual.; El churn observado de 2024 no coincide entre tablas: 2,04%
  en T-002 y T-085 (ventana ene–jul) y 1,9% en T-034. Hay que fijar una sola cifra (X-101).; CAC en COP, payback,
  LTV con margen, LTV:CAC y UCM no tienen valor: faltan unidad del gasto, canal, margen y costo de servir (F-137,
  F-138).; El as-is no separa cancelación de mora, prepago de expansión ni plan de precio y descuento (F-239). ·
  En palabras de Hugo: “«C-009 ¿hay otras métricas que debean de proponerse? De todo eso hay que ser explicitos
  en como se miden y siempre siempre ser MECE» · MRR, ARR, ARPU, CAC, LTV, Churn, UCM y cómo medirlas.”'
evidence_gaps: []
```

```yaml
slide_id: S11
claim_id: C-022
question: ¿Cómo se evita que una métrica aparezca en dos lugares o con dos fórmulas?
message: Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro
role_in_story: recommendation
support:
- claim: Entre Executive, Self Service y Hybrid solo se compara del nudo hacia la derecha. Antes del nudo, cada
    funnel tiene su propia unidad, sus etapas y sus tiempos, y sus tasas no se comparan ni se promedian.
  type: FACT
  source: F-155
  strength: strong
- claim: Las tasas se miden por cohorte con una ventana fija por motion, y los resultados comunes por cohorte de
    primer pago a M3/M6/M12. Así se separa un retraso (HC3a) de una brecha persistente (HC3b), y un cambio de mezcla
    no parece un cambio de desempeño.
  type: FACT
  source: F-158
  strength: strong
- claim: Hoy no se puede calcular ninguna métrica por motion ni nada anterior al pago. Además, probar las palancas
    de H-006 y H-028 requiere un experimento.
  type: FACT
  source: F-159
  strength: strong
- claim: Con los datos de hoy solo se miden el nudo y la vuelta de pagadores. Esa vuelta es un loop de Revenue,
    en parte es timing de pago, y no debe llamarse Reactivate.
  type: FACT
  source: F-213
  strength: strong
- claim: 'En verde (se puede calcular hoy, con nombre honesto): MRR pagado observado y su puente, clientes activos,
    ARPA por cliente, churn observado, NRR/GRR de la base y métricas de cohorte.'
  type: FACT
  source: F-135
  strength: strong
- claim: 'El «ARPU» de hoy es en realidad ARPA (por cliente, no por usuario), y su caída total mezcla cohortes:
    hay que reportarlo por cohorte y medir el ARPA de entrada con un monto estabilizado (M1 o monto usual), no con
    el primer pago.'
  type: FACT
  source: F-139
  strength: partial
- claim: 'La operación recurrente se sostiene con el historial de etapas del CRM (viene de forma nativa) y un tablero
    por foro: el semanal decide oportunidades, el mensual la mezcla de motion y canal, el trimestral la inversión
    y la capacidad.'
  type: FACT
  source: F-148
  strength: partial
- claim: La única comparación válida entre rutas es por puerta, con cohorte y ventana fija. La ruta se clasifica
    al final con una regla por eventos, y las métricas de etapa se leen dentro de cada ruta.
  type: FACT
  source: F-224
  strength: partial
- claim: 'El catálogo no suma métricas: gobierna las del funnel (C-006) y las comunes (C-009). Cada métrica entra
    una sola vez con nombre, fórmula versionada, grano, dueño, semáforo de hoy, el evento o la tabla que le falta
    en el to-be (C-013) y el foro que la usa (C-014). Reglas MECE: un nombre, una fórmula y un lugar; puerta, ruta,
    canal, industria y cohorte son cortes; las tasas de etapa se leen dentro de su ruta y solo la capa común se
    compara entre puertas. Controles de cada mes: las entradas por puerta suman el total; los primeros pagos por
    ruta, más los que no se cruzan con el CRM, igualan los primeros pagos del mes; y los puentes de clientes y de
    MRR cierran.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Una casilla por métrica: cada métrica del funnel y de las comunes cae en un solo lugar, conectada
  a su fuente y a su foro.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Cada métrica vive en un solo lugar del catálogo, con dueño, fuente y foro
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Es diseño: los dueños de cada
  métrica se definen con Finora.; Construirlo choca con D-007 tal como está redactada; D-018 lo decides tú. · En
  palabras de Hugo: “«siempre siempre ser MECE»”'
evidence_gaps: []
```

```yaml
slide_id: S12
claim_id: C-010
question: ¿Podemos calcular el CAC hoy?
message: 'Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC'
role_in_story: limitation
support:
- claim: El gasto comercial por alta es menor en 2024 que en 2022 (0,105 u frente a 0,036 u en la unidad reportada,
    un cambio de −66%), y la correlación en niveles entre el gasto total y las altas del mismo mes es −0,57.
  type: FACT
  source: F-081
  strength: partial
- claim: El S&M total por alta es 0,105 u en 2022 y 0,036 u en 2024, un cambio de −66%, y el S&M total pasa de 3,45
    u en may-23 a 1,10 u en ago-23.
  type: FACT
  source: F-108
  strength: strong
- claim: 'El peso de Habilitación en el S&M total no es estable: pasa de 12% en 2022 a 7% en 2023 y 4% en 2024,
    por lo que el nivel del gasto por alta depende de si el rubro se cuenta como comercial.'
  type: FACT
  source: F-069
  strength: partial
- claim: Habilitación pesa 12% del S&M total en 2022 y 4% en 2024, y el gasto por alta baja de 0,11 a 0,04 incluyéndola
    y de 0,09 a 0,03 excluyéndola.
  type: FACT
  source: F-070
  strength: partial
- claim: El S&M total por cliente nuevo es más de 50% menor en 2024 que en 2022.
  type: FACT
  source: F-022 · C-INV-02
  strength: strong
- claim: 'El CAC solo existe como «S&M por alta en unidades reportadas»: sin la unidad del gasto no hay CAC en COP,
    ni payback, ni LTV:CAC, y sin motion o canal no hay CAC por Self Service/Assisted/Executive ni por Digital/KAM.'
  type: FACT
  source: F-137
  strength: partial
- claim: 'Lo único que se puede calcular es el S&M total por primer pagador observado, en la unidad del archivo:
    0,105 u en 2022 y 0,036 u en 2024 (−66%). No es CAC: la unidad del gasto no está documentada, no hay canal ni
    ruta, y el primer pago no es el hito de adquisición acordado. Además, depende de qué rubros se cuenten: Habilitación
    pesa 12% del S&M en 2022, 7% en 2023 y 4% en 2024, y el gasto por alta baja de 0,11 a 0,04 si se incluye y de
    0,09 a 0,03 si se excluye. En las métricas comunes (C-009) queda como proxy del CAC, en rojo hasta tener la
    unidad y el canal.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-081.yaml
- data/FIN-F-069.yaml
- data/FIN-F-070.yaml
visual_intent: 'Sensibilidad: el mismo cociente cambia según qué rubros entren; muestra lo frágil del proxy más
  que su nivel.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: 'Hoy solo existe S&M por primer pagador en unidades reportadas: no es CAC'
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; El −66% no se lee como más eficiencia
  comercial: puede venir de cómo se arma el archivo (X-005, H-070).; No hay CAC por canal ni por ruta; no se da
  ningún valor de CAC en COP. · En palabras de Hugo: “CAC (qué métricas propondrías que hoy no existen).”'
evidence_gaps: []
```

```yaml
slide_id: S13
claim_id: C-011
question: ¿Cuánto de «no más ventas» depende de cómo se cuenta y cuánto es negocio?
message: Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha
role_in_story: evidence
support:
- claim: Excluyendo oct-24, las altas por mes de 2024 son 56 frente a 54 en 2023; incluyendo oct-24 son 55.
  type: FACT
  source: F-196
  strength: strong
- claim: Entre mar-22 y oct-24 las altas corresponden a 1.476 clientes distintos, con 0 meses-cliente marcados a
    la vez como alta y reactivación y 0 altas con un pago anterior registrado; las reactivaciones suman 468 eventos
    en un flujo aparte.
  type: FACT
  source: F-197
  strength: partial
- claim: En 2023 y en 2024 (ene–oct) las reactivaciones por mes son 12 y 16 frente a 54 y 55 altas por mes, de modo
    que sumarlas o separarlas deja ambos periodos en el mismo orden.
  type: FACT
  source: F-201
  strength: strong
- claim: 'No es posible verificar si un cliente nuevo corresponde a un negocio que ya pagaba bajo otro identificador:
    el panel solo trae identificador de cliente, industria, mes y monto, sin estado de suscripción, fuente del lead
    ni motivo de salida.'
  type: FACT
  source: F-202
  strength: partial
- claim: En 2023, 175 de 650 altas coinciden en monto exacto e industria con el último pago de un churn reciente,
    frente a 196 altas bajo un emparejamiento placebo con churns muy posteriores; en 2022 (mar–dic) las cifras son
    76 de 272 contra 68.
  type: FACT
  source: F-203
  strength: partial
- claim: 'La premisa «no más ventas» depende de la ventana: con los pagos se sostiene en jul–oct 2024, pero no en
    mar–oct.'
  type: FACT
  source: F-125
  strength: strong
- claim: Con el modelo actual no se puede validar ni descartar ninguna de H-001 a H-008. El gasto sube mientras
    las altas bajan, pero eso no dice nada de los leads.
  type: FACT
  source: F-126
  strength: partial
- claim: 'En pagos, el problema aparece en jul–oct 2024, no en todo el año: hay que fijar el periodo antes de buscar
    causas'
  type: FACT
  source: F-204
  strength: strong
- claim: Tres artefactos del lado de pagos no alcanzan para explicar la caída de jul–oct 2024
  type: FACT
  source: F-205
  strength: strong
- claim: 'Antes del árbol hay que fijar qué es «venta» y qué ventana se compara: en los pagos, la respuesta cambia
    según la unidad y el trimestre.'
  type: FACT
  source: F-229
  strength: strong
- claim: Con el modelo actual no se puede validar ni descartar ninguna hoja de las ramas 1 a 4, y de H-057 solo
    se ve el arranque.
  type: FACT
  source: F-230
  strength: strong
- claim: Las altas por mes pasan de 27 en 2022 (mar–dic) a 54 en 2023 y 55 en 2024 (ene–oct).
  type: FACT
  source: F-192
  strength: strong
- claim: 'Paso 0 del árbol (C-023): fijar qué es «venta» (Won o primer pago) y qué ventana se compara, porque en
    los pagos la respuesta cambia: la premisa «no más ventas» se sostiene en jul–oct 2024 y no en mar–oct. Del lado
    de los pagadores, tres revisiones de medición no cambian la lectura. Sin oct-24, las altas por mes de 2024 son
    56 frente a 54 en 2023 (55 con octubre). Altas y reactivaciones son flujos separados: 1.476 clientes con alta,
    468 reactivaciones y 0 meses marcados como ambos. Y las altas que coinciden en monto e industria con un churn
    reciente no superan al emparejamiento placebo (175 de 650 frente a 196 en 2023). Lo que falta revisar del lado
    de los leads (no-prospectos, duplicados, cambios de definición) necesita el CRM.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-196.yaml
- data/FIN-F-197.yaml
- data/FIN-F-203.yaml
- data/FIN-F-192.yaml
visual_intent: 'Filtro: la premisa pasa por las revisiones de medición del lado de pagos y la brecha sigue en pie;
  lo del lado de leads queda en espera del CRM.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Primero se fija qué es venta; revisar la medición en pagos no cierra la brecha
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; No se afirma que la medición quedó
  descartada: con los pagos solo se acotan las revisiones del lado de pagadores.; No se puede verificar si un primer
  pagador es un negocio que ya pagaba con otro ID (F-202). En 2024 el placebo no sirve porque hay pocos churns posteriores.;
  Primer pago no es Won. La ventana jul–oct 2024 es corta y puede incluir compra adelantada (H-066, H-075). · En
  palabras de Hugo: “Definir qué hipótesis ToFu y BoFu podrían estar afectando su motor y qué datos validarían o
  descartarían cada una.”'
evidence_gaps: []
```

```yaml
slide_id: S14
claim_id: C-023
question: ¿Qué podría explicar «más leads, pero no más ventas», ordenado sin que una causa aparezca en dos lugares?
message: 'Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja'
role_in_story: recommendation
support:
- claim: El árbol queda MECE si la brecha se reparte en orden por identidad —validez del lead → puerta (motion)
    → mezcla vs tasa → etapa → cobro—, así cada pedazo de caída cae en una sola hoja.
  type: FACT
  source: F-228
  strength: strong
- claim: 'Antes del árbol hay que fijar qué es «venta» y qué ventana se compara: en los pagos, la respuesta cambia
    según la unidad y el trimestre.'
  type: FACT
  source: F-229
  strength: strong
- claim: Con el modelo actual no se puede validar ni descartar ninguna hoja de las ramas 1 a 4, y de H-057 solo
    se ve el arranque.
  type: FACT
  source: F-230
  strength: strong
- claim: 'Capacidad (H-006), estancamiento (H-055) e incentivos del SDR (H-054) no compiten por la misma brecha
    si se miden por su firma: tiempo a primer toque y carga; bolsa de estancados y compra de los retomados; aceptación
    del AE según el origen del SQL.'
  type: FACT
  source: F-231
  strength: partial
- claim: 'Calidad al entrar (H-005), decisión en Proposal (H-056) y misma demanda por otra puerta (H-053) solo se
    prueban con datos que no dependan de lo que Sales opine después: señales congeladas al crear el lead, motivos
    validados con compradores y cruce de identidad con el producto.'
  type: FACT
  source: F-232
  strength: partial
- claim: 'Dos tipos de dato bastan para distinguir 4 de las 8 hipótesis (H-001, H-002, H-003, H-004): las entradas
    únicas con fecha (con canal, motion y segmento) y el vínculo con pago. Son justamente las que convertirían «más
    leads» en un artefacto.'
  type: FACT
  source: F-127
  strength: partial
- claim: H-005, H-006 y H-007 necesitan datos que suelen estar en un CRM, pero no siempre con su historia. La evidencia
    externa hace plausible H-006, pero no la prueba para Finora.
  type: FACT
  source: F-128
  strength: partial
- claim: Para H-008 no alcanzan las razones de pérdida del CRM. Además hay una señal lateral que amerita una pregunta
    concreta sobre precio o condiciones en 2024.
  type: FACT
  source: F-129
  strength: partial
- claim: 'La comparación que separa es mezcla vs. tasa por grupo de entrada: la mezcla de ajuste habla de H-005;
    la tasa dentro de cada banda, si cae sobre todo en entradas lentas y en semanas de alta carga, habla de H-006.'
  type: FACT
  source: F-122
  strength: partial
- claim: 'Las tasas se comparan entre puertas, que son fijas al entrar, no entre rutas: la ruta se define por lo
    que pasó, y eso sesga por construcción la conversión de Hybrid (H-050).'
  type: FACT
  source: F-212
  strength: strong
- claim: 'Paso 0, antes del árbol: fijar qué es venta (Won o primer pago), una ventana W igual para el periodo base
    y el del aumento, cohortes por fecha de creación y New separado de Reactivate. Identidad: ventas = Σ por puerta
    de las entradas válidas × la conversión de cada etapa dentro de W. La brecha se reparte en este orden, cada
    nivel con su regla de corte, y cada pedazo cae en una sola hoja. MEDICIÓN · Validez, ¿el aumento de New es demanda
    nueva que puede comprar? Hojas: no-prospectos, si sube la parte de duplicados, clientes actuales, ex-clientes
    o spam (H-052); desfase o cambio de definición, si la ventana es más corta que el ciclo o cambió qué se registra
    como New (H-003, H-004, H-027, H-069); misma demanda por otra puerta, si compradores que antes entraban solos
    por producto ahora pasan por Ventas (H-053). NEGOCIO · Mezcla, con entradas válidas, ¿cambió quién entra o cuánto
    convierte cada grupo? Efecto mezcla = Σ cambio de mezcla × tasa base; efecto tasa = Σ mezcla nueva × cambio
    de tasa; el término cruzado se asigna con una regla fija. Hoja: entra peor mezcla (H-002, H-005), medida con
    señales congeladas al crear el lead. Antes del SQL, si es tasa: capacidad, si el tiempo a primer toque sube
    con la carga por SDR/AE (H-006); estancados sin seguimiento, si crece la bolsa de estancados y los retomados
    sí compran (H-054 no, H-055). Después del SQL: SQL menos maduros por la meta del SDR, si la aceptación del AE
    y la caída posterior empeoran solo en los SQL del SDR frente a otros orígenes (H-054); decisión en Demo o Proposal
    por precio, plan, competidor o funcionalidad, con motivos validados con compradores (H-056, H-008). Cobro: el
    Won no llega a pagar o se cae en el arranque (H-057). H-007 no es hoja: es la regla que ubica la etapa antes
    o después del SQL. PALANCA DEL CRO: validez → definición de lead válido, deduplicación y ruteo · mezcla → scoring
    y mezcla de fuentes con el CMO · antes del SQL → capacidad, SLA y cadencias de seguimiento · después del SQL
    → criterio de SQL y comisiones, o pricing y respuesta a la competencia con CFO y CPO · cobro → handoff a cobro
    y onboarding. Hoy no se valida ni se descarta ninguna hoja de validez, mezcla o etapa; de cobro solo se ve el
    arranque.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Descomposición: la brecha se parte en orden (validez → puerta → mezcla contra tasa → etapa → cobro);
  cada pedazo cae en una sola hoja con su dato y su palanca, con la medición separada del negocio.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: 'Proponemos un árbol MECE: cada pedazo de la brecha cae en una sola hoja'
notes: 'Pendiente de tu aceptación: F-228 a F-232 y los demás findings citados están propuestos.; Reordena las tres
  ramas de D-001 (cantidad, mezcla, compra según tiempo). Si lo adoptas, hace falta una decisión nueva que referencie
  D-001 (X-150); no se sobrescribe en silencio.; Las hojas son causas candidatas: no afirmamos que en Finora cambiaron
  metas, comisiones, precio o competencia. La caída post-SQL no se atribuye al AE.; Comparar SQL directos contra
  SQL del SDR no es un experimento: vienen de orígenes distintos; solo sirve ver cómo cambia cada grupo en el tiempo,
  y aun así es asociación.; Si aparecen a la vez las firmas de mezcla y de capacidad, se reportan como interacción
  (H-028), no como hoja nueva. · En palabras de Hugo: “«lo mismo en C-023mucho artefacto pero no hay nada MECE,
  me confunde»”'
evidence_gaps: []
```

```yaml
slide_id: S15
claim_id: C-012
question: ¿Cómo se sabe si falta capacidad comercial o si bajó la calidad de la máquina de leads?
message: Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta
role_in_story: recommendation
support:
- claim: 'El dato mínimo son dos tablas: entradas con el ajuste congelado al entrar y el primer contacto humano,
    y un roster semanal de SDR/AE con su ramp.'
  type: FACT
  source: F-121
  strength: partial
- claim: 'La comparación que separa es mezcla vs. tasa por grupo de entrada: la mezcla de ajuste habla de H-005;
    la tasa dentro de cada banda, si cae sobre todo en entradas lentas y en semanas de alta carga, habla de H-006.'
  type: FACT
  source: F-122
  strength: partial
- claim: Lo que el modelo sí dice sobre los compradores no permite elegir entre H-005 y H-006.
  type: FACT
  source: F-124
  strength: strong
- claim: 'Con el modelo actual no se puede separar H-005 de H-006: faltan las entradas, los reps y los tiempos de
    contacto.'
  type: FACT
  source: F-120
  strength: partial
- claim: Hoy no se puede calcular ninguna métrica por motion ni nada anterior al pago. Además, probar las palancas
    de H-006 y H-028 requiere un experimento.
  type: FACT
  source: F-159
  strength: strong
- claim: 'Capacidad (H-006), estancamiento (H-055) e incentivos del SDR (H-054) no compiten por la misma brecha
    si se miden por su firma: tiempo a primer toque y carga; bolsa de estancados y compra de los retomados; aceptación
    del AE según el origen del SQL.'
  type: FACT
  source: F-231
  strength: partial
- claim: 'Calidad al entrar (H-005), decisión en Proposal (H-056) y misma demanda por otra puerta (H-053) solo se
    prueban con datos que no dependan de lo que Sales opine después: señales congeladas al crear el lead, motivos
    validados con compradores y cruce de identidad con el producto.'
  type: FACT
  source: F-232
  strength: partial
- claim: 'En el árbol (C-023), la calidad es la hoja de mezcla y la capacidad es una hoja de antes del SQL. Se separan
    por puerta, entre el periodo base y el de la caída. Si empeora la mezcla de ajuste al entrar y la velocidad
    de atención está estable, apunta a calidad (H-005). Si la mezcla está estable, suben la carga y la espera y
    la caída se concentra en entradas atendidas tarde, apunta a capacidad (H-006). Si pasan ambas cosas, apunta
    a las dos a la vez (H-028). Dato mínimo: entradas con su banda de ajuste congelada al crearse y su primer contacto
    humano, más un roster semanal de SDR/AE con su ramp; el gasto de Team no mide capacidad. Con datos observados
    es asociación, porque SDR/AE eligen a quién tocar: para probar la palanca hacen falta experimentos naturales
    (llegadas fuera de horario, reparto por turnos) o un piloto.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Dos firmas distintas: calidad mueve la mezcla con la velocidad quieta; capacidad mueve la carga
  y la espera con la mezcla quieta.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Calidad y capacidad se separan con mezcla contra tasa, dentro de cada puerta
notes: 'Pendiente de tu aceptación; F-120 tiene confianza baja.; Hoy no se puede separar H-005 de H-006: faltan
  entradas, reps y tiempos de contacto (F-120).; No usamos Self Service como grupo de control: depende de que haya
  existido sin SDR/AE en ambos periodos (X-012).; Las bandas de ajuste deben validarse antes en el periodo base.
  La capacidad también puede estar en el AE, no solo en el SDR (X-153). · En palabras de Hugo: “La capacidad comercial
  instalada no alcanza la demanda generada, la calidad de la máquina de leads bajó.”'
evidence_gaps: []
```

```yaml
slide_id: S16
claim_id: C-013
question: ¿Qué modelo de datos se propone para operar el funnel, as-is vs to-be?
message: Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción
role_in_story: recommendation
support:
- claim: 'El as-is es un modelo de «después del pago»: tres fuentes con tres granos (cliente × mes, cliente, mes)
    y ninguna mira antes del primer pago.'
  type: FACT
  source: F-238
  strength: strong
- claim: 'Incluso después del pago, el as-is no separa estados que C-009 necesita: cancelación vs mora, prepago
    vs expansión, y plan vs precio vs descuento.'
  type: FACT
  source: F-239
  strength: strong
- claim: 'El to-be de la hipótesis de trabajo se sostiene con patrones estándar, con tres ajustes: espina de identidad,
    puerta separada de ruta, y suscripción dividida en contratado, descontado, facturado y cobrado.'
  type: FACT
  source: F-240
  strength: partial
- claim: Seis reglas del modelo son decisiones de negocio, no hechos, y tienen que quedar escritas antes de construir.
  type: FACT
  source: F-241
  strength: strong
- claim: 'Lo que no se capture desde ya no se reconstruye después: el to-be mide hacia adelante, salvo que Finora
    tenga historial en sus sistemas.'
  type: FACT
  source: F-242
  strength: partial
- claim: El lado Revenue ya se puede operar mes a mes, pero con pagos observados el CRO confundiría el momento del
    cobro con churn y expansión. La facturación es la primera pieza técnica.
  type: FACT
  source: F-145
  strength: strong
- claim: El lado Growth no existe en los datos. Sin motion, canal ni fechas de hitos no se puede calcular ninguna
    conversión ni CAC por motion; hoy solo se ve la mezcla de gasto.
  type: FACT
  source: F-146
  strength: partial
- claim: 'Para medir el lado izquierdo hay que instrumentar en origen: fechas por etapa en el CRM, puerta y canal
    por cuenta, y gasto por canal. Aun así, la atribución reparte crédito, no prueba causa.'
  type: FACT
  source: F-144
  strength: strong
- claim: Hoy no se puede medir ninguna etapa antes del primer pago, ni la puerta. La prueba más rápida es que Finora
    etiquete hacia atrás, desde el CRM, a los pagadores 2022–2024.
  type: FACT
  source: F-191
  strength: strong
- claim: Con los datos de hoy solo se miden el nudo y la vuelta de pagadores. Esa vuelta es un loop de Revenue,
    en parte es timing de pago, y no debe llamarse Reactivate.
  type: FACT
  source: F-213
  strength: strong
- claim: 'El monto pagado mezcla fecha de cobro con mes de servicio: los atrasos y los pagos multimes inflan el
    churn, la reactivación y la expansión observados. Antes de llamarlos churn o MRR hace falta una regla de normalización
    y una ventana de gracia.'
  type: FACT
  source: F-136
  strength: strong
- claim: De los 751 eventos de churn observado entre mar-22 y oct-24, 44% vuelve a pagar al mes siguiente bajo el
    mismo identificador de cliente, y esos retornos se registran en el flujo de reactivaciones.
  type: FACT
  source: F-199
  strength: strong
- claim: 'AS-IS: tres fuentes, todas de después del pago. Pagos, con grano cliente × mes (ID, mes y monto sin escala
    → customer_id, month y amount_cop): responde cuánto pagó cada cliente cada mes, el puente de monto pagado y
    las cohortes por primer pago. No responde nada de quien no pagó, ni plan, precio o descuento, ni si un cero
    es cancelación, mora o desfase (44% de los churn observados vuelve a pagar al mes siguiente), ni si un pico
    es prepago o expansión. Industria, con grano cliente (ID en otro formato): responde el corte por industria;
    no responde tamaño, segmento ni cambios en el tiempo. Gasto S&M, con grano mes × rubro y sin unidad: responde
    el gasto por rubro y una eficiencia agregada; no responde canal ni campaña. Ninguna de las tres responde canal,
    puerta, etapa, intervención, tiempo de cierre ni estancamiento. TO-BE: una espina y tres capas. Espina: account
    (una fila por cuenta; llave account_id) y account_xref (llave: sistema + ID de origen + inicio de vigencia),
    que une CRM, producto, facturación y los IDs de hoy. Demanda: channel (canal × versión de la regla source/medium),
    campaign, touch (un toque con UTMs; llave touch_id), campaign_member (persona × campaña) y campaign_spend (gasto
    por campaña, con moneda). Comercial: person, lead, opportunity, stage_history (un cambio de etapa: de, a, cuándo
    y quién), activity y assignment. Producto y facturación: product_event, subscription, subscription_item_version
    (lo contratado), discount (lo descontado), invoice (lo facturado) y payment (lo cobrado). Marts: funnel_entry,
    una fila por entrada con puerta, ruta y fecha de cada hito, que alimenta C-006; y account_month, cuenta × mes
    con MRR de lista y neto y estado de suscripción, que alimenta C-009 y se concilia cada mes con el monto pagado
    de hoy. BRECHA → MÉTRICA QUE HABILITA: llave común → cruzar entrada, toque y pago de una misma cuenta · touch,
    channel y campaign_spend → entradas, win rate y costo por Won por canal · puerta y ruta en funnel_entry → cohortes
    y win rate por puerta · stage_history → volumen y conversión por etapa · fechas de hitos → tiempo de cierre
    y Won → primer pago · activity y assignment → calidad del handoff, carga por SDR/AE y estancamiento · estado
    de suscripción → churn por cancelación separado de mora · contratado, descontado, facturado y cobrado → MRR
    de lista y neto, línea Descuento y efecto de cobro (S3).'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data:
- data/FIN-F-199.yaml
visual_intent: 'From → to: tres fuentes aisladas de después del pago pasan a una espina de cuenta que une demanda,
  funnel y suscripción; cada brecha que se cierra enciende una métrica.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Proponemos pasar de pagos por cliente-mes a una cuenta común con demanda, funnel y suscripción
notes: 'Pendiente de tu aceptación: F-238 a F-242 y los demás findings citados están propuestos.; Es diseño, no
  algo construido; si entra a la historia bajo D-007 depende de D-018.; R-033 trata Reactivate como puerta y usa
  las rutas self_serve_puro, hybrid y sales_assisted; C-005 (R-031) lo trata como loop, con las rutas Executive,
  Self Service, Hybrid A y B. Hay que alinearlos antes de construir.; Varias reglas son decisiones de negocio y
  deben quedar escritas antes (F-241): orden de puerta, cuándo una entrada es nueva, estados New/Working/Engaged,
  ventana W, umbral de estancamiento y base del puente (lista o neto).; Mide hacia adelante, salvo que Finora tenga
  historial en sus sistemas (F-242). Que el caso no traiga canal ni etapas no prueba que Finora no los registre.
  · En palabras de Hugo: “«C-013, quiero ver explicitamente el modelo de datos que se propone, as is vs to be» ·
  técnica: pulir CRM, analítica digital.”'
evidence_gaps: []
```

```yaml
slide_id: S17
claim_id: C-014
question: ¿Cómo opera el CRO el funnel de forma recurrente y qué decide en cada foro?
message: 'Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro
  para preguntas del día a día a través de agentes de IA que permitan generar visualizaciones y hacer análisis adhoc'
role_in_story: recommendation
support:
- claim: 'Los marcos coinciden: medir volumen, alcance y tiempo por hito en cada motion y unirlos en resultados
    económicos comunes. Un bowtie por motion (Self Service, Assisted, Executive/KAM) evita la tasa mezclada.'
  type: FACT
  source: F-147
  strength: partial
- claim: 'La operación recurrente se sostiene con el historial de etapas del CRM (viene de forma nativa) y un tablero
    por foro: el semanal decide oportunidades, el mensual la mezcla de motion y canal, el trimestral la inversión
    y la capacidad.'
  type: FACT
  source: F-148
  strength: partial
- claim: Los agentes de IA y la atribución van encima, no en la base. Los agentes deben trabajar solo sobre métricas
    gobernadas y entrar con un piloto controlado. La atribución reparte crédito; para decidir presupuesto hacen
    falta experimentos.
  type: FACT
  source: F-149
  strength: partial
- claim: 'Para medir el lado izquierdo hay que instrumentar en origen: fechas por etapa en el CRM, puerta y canal
    por cuenta, y gasto por canal. Aun así, la atribución reparte crédito, no prueba causa.'
  type: FACT
  source: F-144
  strength: strong
- claim: 'Cada foro trae sus métricas (C-006, C-009) y la decisión que habilita. Semanal (CRO, líderes de SDR/AE
    y RevOps): estancamiento por etapa, calidad del handoff, tiempo en etapa, carga por SDR/AE y stock sin tocar
    del loop Reactivate → qué journeys avanzar, retomar o descalificar, y dónde reasignar capacidad. Mensual de
    Growth & Revenue (CRO, Marketing, CS/KAM y Finanzas): entradas y win rate de cohorte por puerta y canal, mezcla
    de Won por ruta, tiempo de cierre, MRR de entrada, puente de MRR y churn persistente → mover la Inversión en
    Marketing entre canales y ajustar el ruteo entre rutas. Trimestral (CEO, CFO y CRO): CAC y costo por Won por
    canal y ruta, payback, NRR/GRR por cohorte y MRR de lista contra neto → repartir entre Generación de Demanda,
    Team y Habilitación. Por encima van el Análisis Ad hoc por hoja del árbol (C-023) y agentes de IA que trabajan
    solo sobre métricas gobernadas (vigilancia de estancamientos, pre-lectura del foro, higiene del CRM), con un
    piloto controlado.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Cadencia a decisión: cada foro conecta pocas métricas con una decisión concreta, de lo operativo
  (semanal) a la inversión (trimestral).'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: 'Proponemos dos vías: una formal y ejecutiva a través de dashboards adhoc a los foros recurrentes y otro
  para preguntas del día a día a través de agentes de IA que permitan generar visualizaciones y hacer análisis adhoc'
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Las decisiones del CRO aún no
  están definidas; los foros son propuesta.; La atribución reparte crédito, no prueba causa: para decidir presupuesto
  hacen falta experimentos (F-149).; Depende del modelo de C-013; mientras tanto solo existen las métricas verdes
  de C-009. · En palabras de Hugo: “Decision making: dashboards automatizados por foro, análisis ad hoc, agentes
  de IA.”'
evidence_gaps: []
```

```yaml
slide_id: S18
claim_id: C-015
question: ¿Qué data observable de pricing introductorio podemos sacar?
message: Lo observable es el primer y segundo pago; el descuento no es verificable
role_in_story: evidence
support:
- claim: El primer pago observado de las altas tiene una mediana de COP 63,0 mil en 2022, COP 36,8 mil en 2023 y
    COP 42,0 mil en 2024, con un rango intercuartílico en 2024 entre COP 25,2 mil y COP 60,9 mil.
  type: FACT
  source: F-083
  strength: strong
- claim: En cohortes de ventana limpia, la mediana del segundo pago (M1) de las altas es COP 52,5 mil en 2022, COP
    36,8 mil en 2023 y COP 38,9 mil en 2024, y la mediana del monto usual temprano (M0–M2) pasa de COP 60,9 mil
    en 2022 a COP 36,8 mil en 2023 y COP 37,8 mil en 2024.
  type: FACT
  source: F-160
  strength: partial
- claim: En la cohorte 2022 el primer pago promedio (COP 128,7 mil) supera al pago promedio del segundo mes (COP
    59,0 mil) y la razón entre la mediana de M1 y la mediana de M0 es 0,83; esa brecha desaparece en las cohortes
    siguientes, con razón 1,00 en 2023 y 0,93 en 2024, patrón consistente con pagos inici…
  type: FACT
  source: F-166
  strength: partial
- claim: Entre las altas de ventana limpia, la parte cuyo primer pago supera con holgura su segundo pago es 23,2%
    en 2022, 7,1% en 2023 y 11,6% en 2024, mientras la parte cuyo segundo pago supera con holgura al primero es
    1,1%, 1,5% y 0,9% en los mismos años.
  type: FACT
  source: F-086
  strength: partial
- claim: Entre las altas de ventana limpia, el segundo pago coincide exactamente con el primero en 73,5% de las
    altas de 2022, 90,3% de 2023 y 77,3% de 2024.
  type: FACT
  source: F-087
  strength: partial
- claim: La huella de un descuento temporal limpio casi no aparece en el histórico (34 de 1.247 contracciones).
    Eso es consistente con que los descuentos sean algo por introducir, pero no prueba que no existieran.
  type: FACT
  source: F-134
  strength: partial
- claim: 'No es posible separar en los pagos un precio de lista, un descuento introductorio, un crédito o una pausa
    de suscripción: el dato disponible es el monto observado por cliente y mes, sin catálogo de precios ni definición
    documentada de lo que ese monto representa.'
  type: FACT
  source: F-093
  strength: partial
- claim: 'Lo observable del pricing introductorio es el primer y el segundo pago de cada alta. La mediana del primer
    pago baja de COP 63,0 mil en 2022 a COP 36,8 mil en 2023 y COP 42,0 mil en 2024; la del segundo, de COP 52,5
    mil a COP 36,8 mil y COP 38,9 mil. El segundo pago repite el primero en 73,5%, 90,3% y 77,3% de las altas, y
    el primero supera con holgura al segundo en 23,2%, 7,1% y 11,6%. Eso se asocia a pagos iniciales grandes en
    2022, pero no dice si hubo descuento: sin lista ni descuento registrados, no es verificable.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-083.yaml
- data/FIN-F-160.yaml
- data/FIN-F-086.yaml
- data/FIN-F-087.yaml
visual_intent: 'Estabilización: el primer pago se acerca al segundo después de 2022; la brecha inicial se cierra.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Lo observable es el primer y segundo pago; el descuento no es verificable
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; No se afirma que hubo descuentos
  en el histórico; el caso habla de introducirlos (F-134 no prueba ausencia).; No se infieren descuentos del tamaño
  de un salto del monto. · En palabras de Hugo: “Qué data observable de pricing introductorio podemos sacar.”'
evidence_gaps: []
```

```yaml
slide_id: S19
claim_id: C-024
question: ¿Qué se puede leer del monto pagado y qué no?
message: Con cliente, mes y monto se ve qué cambió, no por qué
role_in_story: diagnosis
support:
- claim: 'Parte del movimiento del puente no corresponde a un cambio sostenido de nivel: 29% del MRR de expansión
    se revierte al mes siguiente y 25,3% del movimiento bruto del monto pagado sin altas vuelve exacto al nivel
    previo.'
  type: FACT
  source: F-172
  strength: strong
- claim: 'El puente actual no separa una baja definitiva de una interrupción temporal: 44% de los churns observados
    vuelve a pagar al mes siguiente y 32% de los retornos después de meses sin pago liquidan exactamente los meses
    pendientes.'
  type: FACT
  source: F-174
  strength: strong
- claim: Del MRR de reactivación de la ventana limpia, la parte que regresa al monto usual explica 11,5% y la parte
    que llega con un monto que cubre los meses del hueco más el corriente explica 42,6%; el resto, 45,9%, no encaja
    en esas firmas de momento de cobro.
  type: FACT
  source: F-180
  strength: partial
- claim: 'Los retornos de pago coinciden con interrupciones cortas y con liquidación de atrasos: 44% de los churns
    observados vuelve a pagar al mes siguiente y 32% de los retornos tras meses sin pago liquida exactamente los
    meses pendientes.'
  type: FACT
  source: F-182
  strength: strong
- claim: 'La contracción observada no muestra la firma de momento de cobro: la parte que regresa al nivel previo
    a la baja al mes siguiente explica 4,0% del MRR de contracción, mientras la parte que al mes siguiente sigue
    igual o más abajo explica 88,9%.'
  type: FACT
  source: F-184
  strength: partial
- claim: 'Hay reversión de calendario en el puente, pero fuera de la contracción: 25,3% del movimiento bruto del
    monto pagado sin altas vuelve exacto al nivel previo al mes siguiente y 29% del MRR de expansión se revierte
    al mes siguiente.'
  type: FACT
  source: F-185
  strength: strong
- claim: 'En verde (se puede calcular hoy, con nombre honesto): MRR pagado observado y su puente, clientes activos,
    ARPA por cliente, churn observado, NRR/GRR de la base y métricas de cohorte.'
  type: FACT
  source: F-135
  strength: strong
- claim: 'El monto pagado mezcla fecha de cobro con mes de servicio: los atrasos y los pagos multimes inflan el
    churn, la reactivación y la expansión observados. Antes de llamarlos churn o MRR hace falta una regla de normalización
    y una ventana de gracia.'
  type: FACT
  source: F-136
  strength: strong
- claim: 'El puente normalizado exacto que pide repartir un pago entre los meses que cubre no es medible con los
    datos disponibles: no hay definición del campo de monto ni estado de la suscripción ni periodo devengado por
    pago, de modo que el reparto solo puede acotarse con firmas de reversión y de liquidaci…'
  type: FACT
  source: F-186
  strength: partial
- claim: Con los datos de hoy solo se miden el nudo y la vuelta de pagadores. Esa vuelta es un loop de Revenue,
    en parte es timing de pago, y no debe llamarse Reactivate.
  type: FACT
  source: F-213
  strength: strong
- claim: 'Se ve cuánto cambió el monto pagado y en qué movimiento del puente, pero parte de ese movimiento es calendario
    de cobro. 25,3% del movimiento bruto sin altas vuelve exacto al nivel previo al mes siguiente, 29% del MRR de
    expansión se revierte al mes siguiente y 44% de los churn observados vuelve a pagar al mes siguiente. En la
    reactivación, 42,6% llega con un monto que cubre los meses del hueco más el corriente y 11,5% regresa al monto
    usual. En la contracción, solo 4,0% vuelve al nivel previo y 88,9% sigue igual o más abajo. Lo que no se ve
    es el porqué: suscripción, tarifa, descuento o cobro.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-172.yaml
- data/FIN-F-174.yaml
- data/FIN-F-180.yaml
- data/FIN-F-184.yaml
- data/FIN-F-185.yaml
visual_intent: 'Ruido contra señal: una parte del movimiento del puente se deshace al mes siguiente; la reactivación
  la concentra y la contracción no.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Con cliente, mes y monto se ve qué cambió, no por qué
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; F-131 salió de este claim: su
  lectura de la contracción choca con F-184 (X-100). Aquí se usa F-184 y la tensión queda abierta.; El reparto exacto
  de un pago entre los meses que cubre no se puede medir; solo se acota (F-186).; Las etiquetas del puente describen
  el monto pagado, no altas, bajas ni expansiones contractuales. · En palabras de Hugo: “Qué data observable de
  pricing introductorio podemos sacar.”'
evidence_gaps: []
```

```yaml
slide_id: S20
claim_id: C-017
question: ¿Cómo se registra un descuento según su origen (promoción digital con su source, promoción física, negociado,
  retención, partner o apilado) y cómo pega en el puente?
message: El descuento se registra como objeto propio, con origen, source y fecha de fin
role_in_story: recommendation
support:
- claim: 'Hoy el modelo no puede separar un descuento de una contracción, un pago multi-mes o un mes sin cobro:
    solo hay cliente × mes × monto.'
  type: FACT
  source: F-233
  strength: strong
- claim: 'Los sistemas de billing separan tres cosas que el to-be también debe separar: la oferta, el código que
    la distribuye y el descuento aplicado con vigencia.'
  type: FACT
  source: F-234
  strength: strong
- claim: 'El source no puede vivir solo en el descuento: hay que capturarlo en la adquisición de todos los clientes
    y guardar aparte el canal asignado al código.'
  type: FACT
  source: F-235
  strength: partial
- claim: 'Cómo pega un descuento en el MRR es una convención, no un hecho: C-020 se sostiene, pero se aparta del
    default del mercado y hay que declararla.'
  type: FACT
  source: F-236
  strength: strong
- claim: 'Negociación, retención y partner necesitan registro propio, y hay dos trampas: el precio especial que
    esconde un descuento y el downgrade de retención.'
  type: FACT
  source: F-237
  strength: partial
- claim: Ninguna de las herramientas revisadas separa el efecto de un descuento del de un cambio de suscripción.
    Usadas tal cual, el fin de un descuento aparecería como expansión y el caso 100→130 con −30 aparecería como
    «sin cambio».
  type: FACT
  source: F-150
  strength: strong
- claim: Para no perder el porqué del MRR, cada descuento tiene que registrarse como objeto propio con fecha de
    fin, separado de la cantidad y del precio de lista, y leerse desde la factura. Hay cinco trampas concretas que
    evitar.
  type: FACT
  source: F-152
  strength: strong
- claim: Con descuentos temporales, el MRR neto, el revenue reconocido y la caja pueden separarse. Cuál vista aplica
    depende de si los contratos de Finora son mensuales cancelables o a plazo fijo.
  type: FACT
  source: F-153
  strength: partial
- claim: El descuento cambia la composición de las cohortes. La evidencia externa asocia la adquisición con descuento
    a clientes de menor valor, y el churn al vencer el descuento tiene otras causas posibles; Finora tendría que
    marcar esas cohortes y medir contra un grupo de control.
  type: FACT
  source: F-154
  strength: partial
- claim: 'El puente actual no separa una baja definitiva de una interrupción temporal: 44% de los churns observados
    vuelve a pagar al mes siguiente y 32% de los retornos después de meses sin pago liquidan exactamente los meses
    pendientes.'
  type: FACT
  source: F-174
  strength: strong
- claim: 'AS-IS: un solo monto por cliente y mes, con transacciones → cliente-mes en COP → movimientos del monto
    con banderas de expansión, contracción, churn y reactivación, monto usual y firmas de pago multimes. Responde
    cuánto pagó el cliente y cómo se movió el monto. No guarda lista, plan, contratado, descuento, origen, source
    ni la diferencia entre factura y pago, así que un descuento se vería igual que una contracción, un pago multimes
    o un mes sin cobro (44% de los churn observados vuelve a pagar al mes siguiente). TO-BE por bloques. Lista y
    contrato: price_list_version (precio por plan y frecuencia, con vigencia) y subscription_item_version (plan
    × cantidad × precio acordado, sin descuentos), que solo cambia con un subscription_change_event. Descuento:
    discount_grant, con tipo, valor, duración, vigencia pactada y real, alcance, apilamiento, motivo, aprobación
    y un solo origen (promoción, negociación, retención o partner). Atribución: campaign (con su rubro de S&M) →
    promotion (la oferta) → promo_code (código, link o QR, con medio, canal asignado, UTM y landing) → promo_redemption
    (el canje, ligado a la sesión), más acquisition_touch con el source observado de todo cliente, tenga o no descuento.
    Aplicación: discount_application (cuánto descontó cada grant en cada línea de factura y en qué orden). Medición:
    una foto de cierre por suscripción y mes con lista, contratado, descuento recurrente, neto, descuento único,
    facturado y cobrado. CASUÍSTICA → PUENTE (C-020). Promoción digital: código con UTM y landing, canje en la sesión
    y source del alta en acquisition_touch → «Descuento (inicio)» con origen promoción y, al vencer, «Descuento
    (fin)», nunca expansión. Promoción física: un código por pieza, evento o punto, o un QR con UTM → la misma línea,
    con origen promoción física, comparable con la digital en retención y MRR neto. Descuento negociado: grant ligado
    al deal y a su aprobación, con precio especial = lista + descuento → «Descuento» con origen negociación, no
    menor MRR de entrada. Retención: si el cliente acepta un descuento → «Descuento» con origen retención; si baja
    de plan → Contracción real. Partner: grant ligado al partner → «Descuento» con origen partner. Apilados: cada
    grant con su orden y su propia línea. Mes gratis: descuento total con bandera sin cobro, no churn. Pausa: estado
    de la suscripción, no descuento.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data:
- data/FIN-F-174.yaml
visual_intent: 'Trazabilidad: cada peso de descuento se sigue desde la oferta y su canal hasta su línea del puente,
  separado de lo contratado; lo digital y lo físico llegan al mismo objeto con distinto source.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: El descuento se registra como objeto propio, con origen, source y fecha de fin
notes: 'Pendiente de tu aceptación: F-233 a F-237 y los demás findings citados están propuestos.; No afirmamos que
  hubo descuentos en el histórico: el diseño es hacia adelante. Los ejemplos de promociones de R-034 son ilustrativos,
  no datos de Finora.; No sabemos si Finora captura hoy el source en el alta de todos los clientes. Si no, el código
  de descuento se volvería la única atribución (H-073).; Sin la regla «precio especial = lista + descuento», los
  descuentos negociados, de partner o de retención quedarían como precio menor (H-074).; Los efectos comerciales
  del descuento (cohortes de menor valor, churn al vencer) son evidencia externa, no de Finora (F-154, H-049). ·
  En palabras de Hugo: “«C-017 lo mismo quiero ver un modelo de datos y considera mas casuisticas, un descuento
  podría provenir de una promocion tanto digital como fisica y si es digital hay que considerar el source tambiem»”'
evidence_gaps: []
```

```yaml
slide_id: S21
claim_id: C-018
question: ¿Cómo debería Finora introducir descuentos temporales sin perder el porqué del MRR?
message: El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan
role_in_story: recommendation
support:
- claim: 'No hay un estándar para tratar los descuentos temporales en el MRR: es una decisión de definición que
    el CFO tiene que tomar y declarar. Para Finora, lo más útil es mostrar las dos capas (lista y neto).'
  type: FACT
  source: F-151
  strength: strong
- claim: Con descuentos temporales, el MRR neto, el revenue reconocido y la caja pueden separarse. Cuál vista aplica
    depende de si los contratos de Finora son mensuales cancelables o a plazo fijo.
  type: FACT
  source: F-153
  strength: partial
- claim: El descuento cambia la composición de las cohortes. La evidencia externa asocia la adquisición con descuento
    a clientes de menor valor, y el churn al vencer el descuento tiene otras causas posibles; Finora tendría que
    marcar esas cohortes y medir contra un grupo de control.
  type: FACT
  source: F-154
  strength: partial
- claim: No hay una convención única de mercado para el descuento en el MRR, y la convención «solo neto» borra justo
    las distinciones que pide el CFO. El modelo debe guardar bruto, descuento y neto por separado; la convención
    oficial queda como decisión.
  type: FACT
  source: F-132
  strength: partial
- claim: 'Cómo pega un descuento en el MRR es una convención, no un hecho: C-020 se sostiene, pero se aparta del
    default del mercado y hay que declararla.'
  type: FACT
  source: F-236
  strength: strong
- claim: 'Mecanismo Propuesto: el CFO declara la convención, porque no hay un estándar de mercado y la de C-020
    se aparta del default de herramientas como ChartMogul · el MRR se reporta en dos capas, lista y neto, y el descuento
    es la diferencia: el revenue que dejamos de capturar, abierto por origen · las cohortes que entren con descuento
    se marcan y se comparan con cohortes sin descuento. Con descuentos, el MRR neto, el revenue reconocido y la
    caja se separan; cuál vista manda depende de si los contratos son mensuales cancelables o a plazo fijo. Implicaciones
    Multidisciplinarias: Finanzas fija la convención y el reconocimiento; Marketing y Ventas crean promociones,
    códigos y aprobaciones; Producto y Billing registran el descuento con su vigencia; Data arma la foto de cierre
    y el puente.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Dos capas que se separan: el MRR de lista y el neto divergen por el descuento, y la caja se aparta
  de ambos.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: El CFO decide la convención; con descuentos, MRR neto, revenue y caja se separan
notes: 'Pendiente de tu aceptación; F-132 tiene la fuente sin verificar.; No sabemos si los contratos de Finora
  son mensuales cancelables o a plazo fijo.; La comparación de cohortes con y sin descuento necesita un grupo comparable;
  con datos observados es asociación (H-049). · En palabras de Hugo: “Cómo debería Finora introducir descuentos
  temporales (Mecanismo Propuesto, Implicaciones Multidisciplinarias, preguntas del CFO contestadas con el modelo
  propuesto).”'
evidence_gaps: []
```

```yaml
slide_id: S22
claim_id: C-019
question: ¿Cómo separar el valor de la suscripción del precio efectivamente pagado?
message: La Propuesta de Modelo de datos separa el valor en una escalera con vigencias
role_in_story: recommendation
support:
- claim: 'El monto pagado no identifica los componentes: con los campos actuales no se puede separar suscripción,
    tarifa, descuento ni momento de cobro.'
  type: FACT
  source: F-130
  strength: partial
- claim: No hay una convención única de mercado para el descuento en el MRR, y la convención «solo neto» borra justo
    las distinciones que pide el CFO. El modelo debe guardar bruto, descuento y neto por separado; la convención
    oficial queda como decisión.
  type: FACT
  source: F-132
  strength: partial
- claim: Se sabe qué forma tiene la evidencia que confirmaría cada componente; lo que no se sabe es si Finora la
    tiene.
  type: FACT
  source: F-133
  strength: partial
- claim: 'No hay un estándar para tratar los descuentos temporales en el MRR: es una decisión de definición que
    el CFO tiene que tomar y declarar. Para Finora, lo más útil es mostrar las dos capas (lista y neto).'
  type: FACT
  source: F-151
  strength: strong
- claim: Para no perder el porqué del MRR, cada descuento tiene que registrarse como objeto propio con fecha de
    fin, separado de la cantidad y del precio de lista, y leerse desde la factura. Hay cinco trampas concretas que
    evitar.
  type: FACT
  source: F-152
  strength: strong
- claim: 'El puente por capas del enunciado —MRR de lista, descuento y MRR neto— no es construible con los datos
    disponibles: el panel cliente-mes registra un solo monto por cliente y mes, sin precio de lista, plan, descuento
    ni crédito, y sin definición documentada de qué representa ese monto.'
  type: FACT
  source: F-168
  strength: partial
- claim: 'Los sistemas de billing separan tres cosas que el to-be también debe separar: la oferta, el código que
    la distribuye y el descuento aplicado con vigencia.'
  type: FACT
  source: F-234
  strength: strong
- claim: 'El to-be de la hipótesis de trabajo se sostiene con patrones estándar, con tres ajustes: espina de identidad,
    puerta separada de ruta, y suscripción dividida en contratado, descontado, facturado y cobrado.'
  type: FACT
  source: F-240
  strength: partial
- claim: 'Por suscripción y mes, cada peldaño lleva su fuente y su vigencia: lista (price_list_version, precio por
    plan y frecuencia) → contratado (subscription_item_version: plan, cantidad y precio acordado, sin descuentos)
    → descuento recurrente (discount_grant) → MRR neto = contratado − descuento recurrente → facturado (línea de
    factura, con el descuento aplicado vía discount_application) → cobrado (pago asignado a la factura). Lo contratado
    solo cambia con un subscription_change_event. El MRR, de lista y neto, se clasifica sobre los primeros peldaños
    comparando fotos de cierre (subscription_month_snapshot); facturado y cobrado son caja y solo generan un «efecto
    de cobro», nunca movimientos de MRR. El monto pagado de hoy sigue como capa de «monto pagado observado» y se
    concilia contra lo cobrado.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Escalera: el valor baja peldaño a peldaño de la lista a lo cobrado, y cada diferencia tiene nombre
  y dueño.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: La Propuesta de Modelo de datos separa el valor en una escalera con vigencias
notes: 'Pendiente de tu aceptación; F-130, F-132 y F-133 tienen la fuente sin verificar.; El puente por capas no
  se puede construir con el histórico (F-168): mide hacia adelante.; Las reglas del modelo son decisiones por escribir
  antes de construir (F-241). · En palabras de Hugo: “Propuesta de modelo de datos (campos, tablas, definiciones).”'
evidence_gaps: []
```

```yaml
slide_id: S23
claim_id: C-020
question: ¿Cómo clasificar el inicio y el fin de un descuento para que no se confundan con contracción o expansión
  reales?
message: Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»
role_in_story: recommendation
support:
- claim: Ninguna de las herramientas revisadas separa el efecto de un descuento del de un cambio de suscripción.
    Usadas tal cual, el fin de un descuento aparecería como expansión y el caso 100→130 con −30 aparecería como
    «sin cambio».
  type: FACT
  source: F-150
  strength: strong
- claim: Para no perder el porqué del MRR, cada descuento tiene que registrarse como objeto propio con fecha de
    fin, separado de la cantidad y del precio de lista, y leerse desde la factura. Hay cinco trampas concretas que
    evitar.
  type: FACT
  source: F-152
  strength: strong
- claim: 'No hay un estándar para tratar los descuentos temporales en el MRR: es una decisión de definición que
    el CFO tiene que tomar y declarar. Para Finora, lo más útil es mostrar las dos capas (lista y neto).'
  type: FACT
  source: F-151
  strength: strong
- claim: 'Cómo pega un descuento en el MRR es una convención, no un hecho: C-020 se sostiene, pero se aparta del
    default del mercado y hay que declararla.'
  type: FACT
  source: F-236
  strength: strong
- claim: 'Negociación, retención y partner necesitan registro propio, y hay dos trampas: el precio especial que
    esconde un descuento y el downgrade de retención.'
  type: FACT
  source: F-237
  strength: partial
- claim: 'Regla base: New, Expansión, Contracción, Churn y Reactivación se definen sobre el MRR contratado y el
    estado de la suscripción entre cierres de mes, nunca sobre el monto pagado. La línea «Descuento» se define sobre
    cambios en los términos de los descuentos y lleva su origen (promoción digital o física, negociación, retención
    o partner). Si la suscripción no cambia, el inicio de un descuento es «Descuento (inicio)», con signo negativo,
    y su fin es «Descuento (fin)», positivo: nunca Contracción ni Expansión. Si cambian las dos cosas el mismo mes,
    se aplica una regla secuencial: primero el efecto suscripción, con los términos de descuento del mes anterior;
    lo que resta es efecto descuento. Además: cambio de términos → «Descuento (cambio)»; descuento único → fuera
    del MRR, resta solo en lo facturado; mes gratis → «Descuento (inicio)» con bandera sin cobro, no churn; pausa
    → estado de suscripción, no descuento; downgrade de retención → Contracción; quien sale con descuento → Churn
    por su neto, sin «Descuento (fin)». Control: por suscripción y mes, la suma de líneas iguala el cambio del MRR
    neto.'
  type: PROPOSAL
  logic: recomendación condicional del Story Package
data: []
visual_intent: 'Separación: el cambio del MRR neto se reparte entre la línea de suscripción y la línea de descuento,
  sin que una contamine a la otra.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Si la suscripción no cambia, inicio o fin de descuento va a «Descuento»
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Es una convención por declarar:
  ChartMogul, por defecto, manda el inicio y el fin a contracción y expansión (F-236).; Recurrente contra único,
  mes gratis y pausa son decisiones, no hechos.; F-131 salió del claim: su lectura de la contracción choca con F-184
  (X-100). · En palabras de Hugo: “Cómo clasificar inicio y fin de un descuento para que no se confundan con contracción
  o expansión reales (probablemente lo integra la misma propuesta de modelo de datos).”'
evidence_gaps: []
```

```yaml
slide_id: S24
claim_id: C-025
question: 'Paga 100 y luego 80; la suscripción pasa de 100 a 130 con un descuento de 30 y sigue pagando 100; desaparece
  el descuento: ¿cómo se lee cada caso con el modelo propuesto?'
message: Con el modelo propuesto, cada caso del CFO se lee en su capa
role_in_story: implication
support:
- claim: 'El puente por capas del enunciado —MRR de lista, descuento y MRR neto— no es construible con los datos
    disponibles: el panel cliente-mes registra un solo monto por cliente y mes, sin precio de lista, plan, descuento
    ni crédito, y sin definición documentada de qué representa ese monto.'
  type: FACT
  source: F-168
  strength: partial
- claim: 'Parte del movimiento del puente no corresponde a un cambio sostenido de nivel: 29% del MRR de expansión
    se revierte al mes siguiente y 25,3% del movimiento bruto del monto pagado sin altas vuelve exacto al nivel
    previo.'
  type: FACT
  source: F-172
  strength: strong
- claim: 'El puente actual no separa una baja definitiva de una interrupción temporal: 44% de los churns observados
    vuelve a pagar al mes siguiente y 32% de los retornos después de meses sin pago liquidan exactamente los meses
    pendientes.'
  type: FACT
  source: F-174
  strength: strong
- claim: 'No se puede asignar la caída del MRR por cliente activo entre un precio de lista distinto y un descuento
    aplicado: sin precios ni descuentos registrados, el caso de lista mayor con descuento vigente y el caso de precio
    neto menor coinciden en el mismo monto observado.'
  type: FACT
  source: F-177
  strength: partial
- claim: 'Lo que sí se observa es composición, no beneficio comercial: el MRR por cliente activo pasó de COP 92,8
    mil en ene-22 a COP 57,8 mil en oct-24 (−38%), mientras el de la base previa cambió +5% y las cosechas 2023–24
    ya concentran 65% de los clientes activos en oct-24.'
  type: FACT
  source: F-178
  strength: strong
- claim: Ninguna de las herramientas revisadas separa el efecto de un descuento del de un cambio de suscripción.
    Usadas tal cual, el fin de un descuento aparecería como expansión y el caso 100→130 con −30 aparecería como
    «sin cambio».
  type: FACT
  source: F-150
  strength: strong
- claim: 'No hay un estándar para tratar los descuentos temporales en el MRR: es una decisión de definición que
    el CFO tiene que tomar y declarar. Para Finora, lo más útil es mostrar las dos capas (lista y neto).'
  type: FACT
  source: F-151
  strength: strong
- claim: 'Con el modelo (C-019, C-020), los ejemplos del enunciado se separan. De 100 a 80: si bajó lo contratado,
    es Contracción; si lo contratado sigue en 100 y empezó un descuento, es «Descuento (inicio)»; si solo cambió
    el mes del cobro, es efecto de cobro, fuera del MRR. De 100 a 130 con descuento de 30: Expansión por el paso
    de 100 a 130 y «Descuento (inicio)» por 30, con el neto en 100. Cuando desaparece el descuento: «Descuento (fin)»
    por 30, no Expansión. Hoy, con el monto pagado, el segundo caso se vería «sin cambio» y el tercero como expansión,
    y el puente ya mezcla cobro: 29% del MRR de expansión se revierte al mes siguiente y 44% de los churn observados
    vuelve a pagar al mes siguiente. Para Q-026, hacia adelante: MRR de lista (negocio subyacente) − MRR neto =
    revenue que dejamos de capturar, por origen. Hoy el −38% por cliente activo no se puede repartir entre lista
    y descuento.'
  type: INFERENCE
  logic: síntesis del COS sobre la evidencia citada
data:
- data/FIN-F-172.yaml
- data/FIN-F-174.yaml
- data/FIN-F-178.yaml
visual_intent: 'Cada caso en su capa: el mismo monto pagado se descompone en suscripción, descuento y cobro, y se
  ve qué línea se mueve en cada ejemplo.'
must_show:
- la relación de la intención visual
must_not_do:
- No tres cards con bullets.
- No convertirlo en una tabla.
- No cifras que no estén en data/.
takeaway: Con el modelo propuesto, cada caso del CFO se lee en su capa
notes: 'Pendiente de tu aceptación: todos los findings citados están propuestos.; Los casos son ejemplos del enunciado,
  no observaciones de Finora.; No damos una cifra histórica de revenue no capturado: el histórico no trae tarifas
  ni descuentos.; La lectura depende de la convención que declare el CFO (C-018). · En palabras de Hugo: “Preguntas
  del CFO contestadas con el modelo propuesto.”'
evidence_gaps: []
```

## 6. Lo que NO aparece (cortes) y apéndice

- Mapa completo de etapas por ruta y canal, con variantes y dueños — C-021 muestra la versión ejecutiva; las variantes (saltos, regla laxa o estricta de Q-063) van al anexo.
- Catálogo de métricas con fórmula, grano, hito y estado de hoy — C-006 y C-009 dan la definición; el detalle de las métricas y sus eventos no cabe en la lámina.
- Modelo de datos del funnel: entidades, llaves, reglas y ejemplos — Sostiene C-013; los ejemplos de R-033 son ilustrativos salvo los IDs legados.
- Modelo de precios y descuentos: entidades, reglas de clasificación y ejemplos ilustrativos — Sostiene C-017, C-019 y C-020; los ejemplos de promociones no son datos de Finora.
- Árbol MECE completo: qué valida, qué descarta y dato mínimo por hoja — C-023 da la estructura; la tabla hoja por hoja es de consulta.
- Calidad del archivo de S&M — La unidad sin documentar, Team fijo hasta may-23, PayrollExpenses negativo y el corte de Freelance condicionan C-004 y C-010.
- Momento de cobro en el puente — Detalle de reactivación y contracción por firma de cobro que respalda C-024.

## 7. Claims sin evidencia / supuestos / preguntas abiertas

- S2.1: ¿qué relaciones comentaste que debe mostrar la lámina? Sigue sin contenido.
- Q-063: ¿qué cuenta como intervención de persona? Define la frontera entre Executive inbound e Hybrid A, y la variante de Hybrid B.
- Q-064: ¿cuál es el umbral de estancamiento por etapa y cuándo caduca un episodio?
- Q-046: ¿existe compra self-serve sin persona? ¿Hay prueba gratis, freemium o pago al registrarse?
- ¿El hito de adquisición del CRO es Won, primer pago o suscripción activa?
- ¿Existen referidos o partners como canal? ¿Quién es dueño de Self Service?
- ¿Reactivate es puerta (R-033) o loop (R-031)? Hay que alinearlo antes de construir.
- ¿El árbol de C-023 reemplaza las tres ramas de D-001? (X-150)
- ¿Finora captura hoy el source (UTM, landing) en el alta de todos los clientes? (H-073)
- ¿Cuál es la unidad del gasto de S&M? ¿Software Tools y Freelance son Habilitación o producto? (Q-022)
- ¿Los contratos de Finora son mensuales cancelables o a plazo fijo? Define qué vista manda: MRR neto, revenue o caja.
- ¿Qué base de comparación usamos para el monto por cliente: ene-22 o dic-22? (X-060)
- ¿Qué cifra de churn observado 2024 usamos: 2,04% o 1,9%? (X-101)
- D-018 contra D-007: ¿entran los diseños a la historia como propuesta?
- Limitación: CAC en COP, payback, LTV con margen, LTV:CAC y UCM no tienen valor: faltan unidad del gasto, canal, margen y costo de servir (F-137, F-138).
- Limitación: Cliente activo = pago mayor que cero en el mes. Un cliente sin pago puede estar cancelado, en pausa o atrasado (F-082).
- Limitación: Comparar SQL directos contra SQL del SDR no es un experimento: vienen de orígenes distintos; solo sirve ver cómo cambia cada grupo en el tiempo, y aun así es asociación.
- Limitación: Composición no es causa: no separa tipo de cliente, plan, tarifa ni descuento; el panel no trae esas tablas (F-062).
- Limitación: Con pocos clientes por industria, las medianas se mueven con pocas altas.
- Limitación: Construirlo choca con D-007 tal como está redactada; D-018 lo decides tú.
- Limitación: Depende del modelo de C-013; mientras tanto solo existen las métricas verdes de C-009.
- Limitación: El as-is no separa cancelación de mora, prepago de expansión ni plan de precio y descuento (F-239).
- Limitación: El churn observado de 2024 no coincide entre tablas: 2,04% en T-002 y T-085 (ventana ene–jul) y 1,9% en T-034. Hay que fijar una sola cifra (X-101).
- Limitación: El escalón de inicios de 2023 puede ser en parte registro (H-024) o un cambio operativo (H-025, H-068). Sin confirmar.
- Limitación: El monto pagado mezcla fecha de cobro y mes de servicio: el churn, la reactivación y la expansión observados salen inflados (F-136). La retención aquí es «sigue pagando», no retención contractual.
- Limitación: El puente por capas no se puede construir con el histórico (F-168): mide hacia adelante.
- Limitación: El reparto exacto de un pago entre los meses que cubre no se puede medir; solo se acota (F-186).
- Limitación: El ticket estabilizado sigue siendo monto pagado: no separa tarifa, plan, empaquetamiento ni descuento (F-167).
- Limitación: El −38% no se presenta como deterioro de la salud: todavía no separa la mezcla de entrada, el precio y las salidas.
- Limitación: El −66% no se lee como más eficiencia comercial: puede venir de cómo se arma el archivo (X-005, H-070).
- Limitación: Es coincidencia temporal, no efecto (F-119, F-222). El valle de ago-23 y el corte de jun-23 pueden ser contables (H-023, H-070, H-071).
- Limitación: Es diseño, no algo construido; si entra a la historia bajo D-007 depende de D-018.
- Limitación: Es diseño: los dueños de cada métrica se definen con Finora.
- Limitación: Es monto pagado observado (campo amount con escala fija), no MRR contratado (F-082).
- Limitación: Es propuesta: hoy el modelo no tiene leads, etapas, dueños, canal ni ruta (F-223).
- Limitación: Es stock con ventana completa desde ene-22; los flujos arrancan en mar-22 (F-074).
- Limitación: Es una convención por declarar: ChartMogul, por defecto, manda el inicio y el fin a contracción y expansión (F-236).
- Limitación: F-131 salió de este claim: su lectura de la contracción choca con F-184 (X-100). Aquí se usa F-184 y la tensión queda abierta.
- Limitación: F-131 salió del claim: su lectura de la contracción choca con F-184 (X-100).
- Limitación: Faltan por confirmar el canal referido/partner y el dueño de Self Service. Parte de los saltos de etapa puede ser registro del CRM (H-051).
- Limitación: Hasta may-23 el archivo se comporta como una asignación de arriba hacia abajo (F-066); PayrollExpenses es negativo en 5 meses y Freelance queda en cero desde jun-23 (T-009).
- Limitación: Hoy no se calcula ninguna métrica antes del pago (F-223): es diseño.
- Limitación: Hoy no se puede separar H-005 de H-006: faltan entradas, reps y tiempos de contacto (F-120).
- Limitación: La atribución reparte crédito, no prueba causa: para decidir presupuesto hacen falta experimentos (F-149).
- Limitación: La base de comparación (ene-22 o dic-22) es una decisión pendiente (X-060).
- Limitación: La cifra de composición depende de la base elegida (X-060).
- Limitación: La comparación de cohortes con y sin descuento necesita un grupo comparable; con datos observados es asociación (H-049).
- Limitación: La conversión de Hybrid refleja a quién eligen tocar SDR/AE, no lo que aporta la persona (H-050). Las tasas de etapas intermedias no se comparan entre rutas (SQL contra activación).
- Limitación: La frontera entre Executive inbound e Hybrid A depende de Q-063. Una variante de Hybrid B (el SDR contacta y la cuenta se registra sola) es Hybrid B con la regla laxa y Self Service con la estricta.
- Limitación: La industria es la única segmentación disponible: no sustituye al canal ni a la ruta.
- Limitación: La industria es una segmentación disponible, no un sustituto de canal ni de ruta; no se afirma una causa industrial.
- Limitación: La lectura depende de la convención que declare el CFO (C-018).
- Limitación: La ruta no se infiere del monto. La tasa de Hybrid refleja a quién eligen tocar SDR/AE (H-050): por eso las tasas se comparan entre puertas, no entre rutas.
- Limitación: La salida de pocas cuentas grandes también baja el promedio (F-101, F-102) y aquí no se separa.
- Limitación: La unidad del gasto no está documentada (F-063): no se puede leer como COP.
- Limitación: Las bandas de ajuste deben validarse antes en el periodo base. La capacidad también puede estar en el AE, no solo en el SDR (X-153).
- Limitación: Las decisiones del CRO aún no están definidas; los foros son propuesta.
- Limitación: Las etapas de Self Service e Hybrid son propuesta. Activated Self se define con Producto, y no sabemos si hay prueba, freemium o pago al registrarse (Q-046).
- Limitación: Las etiquetas del puente describen el monto pagado, no altas, bajas ni expansiones contractuales.
- Limitación: Las hojas son causas candidatas: no afirmamos que en Finora cambiaron metas, comisiones, precio o competencia. La caída post-SQL no se atribuye al AE.
- Limitación: Las reglas del modelo son decisiones por escribir antes de construir (F-241).
- Limitación: Los casos son ejemplos del enunciado, no observaciones de Finora.
- Limitación: Los efectos comerciales del descuento (cohortes de menor valor, churn al vencer) son evidencia externa, no de Finora (F-154, H-049).
- Limitación: Mide hacia adelante, salvo que Finora tenga historial en sus sistemas (F-242). Que el caso no traiga canal ni etapas no prueba que Finora no los registre.
- Limitación: No afirmamos que Finora tenga criterios de etapa definidos: el brief da la secuencia y un traspaso SDR → AE que ocurre «sobre todo» y «normalmente». Demo y Proposal hay que confirmarlas contra el CRM.
- Limitación: No afirmamos que hubo descuentos en el histórico: el diseño es hacia adelante. Los ejemplos de promociones de R-034 son ilustrativos, no datos de Finora.
- Limitación: No damos una cifra histórica de revenue no capturado: el histórico no trae tarifas ni descuentos.
- Limitación: No hay CAC por canal ni por ruta; no se da ningún valor de CAC en COP.
- Limitación: No hay tamaño de cliente, motivos de churn ni estado de suscripción (F-106).
- Limitación: No sabemos si Finora captura hoy el source en el alta de todos los clientes. Si no, el código de descuento se volvería la única atribución (H-073).
- Limitación: No sabemos si existe compra self-serve sin persona, ni si hay prueba gratis, freemium o pago al registrarse (Q-046).
- Limitación: No sabemos si los contratos de Finora son mensuales cancelables o a plazo fijo.
- Limitación: No se afirma que hubo descuentos en el histórico; el caso habla de introducirlos (F-134 no prueba ausencia).
- Limitación: No se afirma que la medición quedó descartada: con los pagos solo se acotan las revisiones del lado de pagadores.
- Limitación: No se fabrica un segmento por clustering: no hay concentración clara (H-044 sigue abierta).
- Limitación: No se infieren descuentos del tamaño de un salto del monto.
- Limitación: No se puede decidir si SoftwareTools y Freelance son Habilitación o producto (F-068).
- Limitación: No se puede verificar si un primer pagador es un negocio que ya pagaba con otro ID (F-202). En 2024 el placebo no sirve porque hay pocos churns posteriores.
- Limitación: No usamos Self Service como grupo de control: depende de que haya existido sin SDR/AE en ambos periodos (X-012).
- Limitación: Pendiente de tu aceptación: F-071, F-072, F-001, F-002 y F-074 están propuestos.
- Limitación: Pendiente de tu aceptación: F-104, F-099, F-103, F-105 y F-165 están propuestos (confianza media).
- Limitación: Pendiente de tu aceptación: F-209 a F-211 y F-223 a F-225 están propuestos.
- Limitación: Pendiente de tu aceptación: F-223 a F-227 y los demás findings citados están propuestos.
- Limitación: Pendiente de tu aceptación: F-228 a F-232 y los demás findings citados están propuestos.
- Limitación: Pendiente de tu aceptación: F-233 a F-237 y los demás findings citados están propuestos.
- Limitación: Pendiente de tu aceptación: F-238 a F-242 y los demás findings citados están propuestos.
- Limitación: Pendiente de tu aceptación: todos los findings citados están propuestos.
- Limitación: Pendiente de tu aceptación; F-120 tiene confianza baja.
- Limitación: Pendiente de tu aceptación; F-130, F-132 y F-133 tienen la fuente sin verificar.
- Limitación: Pendiente de tu aceptación; F-132 tiene la fuente sin verificar.
- Limitación: Pendiente de tu aceptación; F-160 a F-163 tienen confianza media.
- Limitación: Primer pago no es Won. La ventana jul–oct 2024 es corta y puede incluir compra adelantada (H-066, H-075).
- Limitación: Primer pago observado no es adquisición (ni Won ni suscripción activa); el hito lo acuerda el CRO (X-052).
- Limitación: Quienes se van pagaban más en promedio, pero no en mediana: la salida de pocas cuentas grandes también baja el promedio (F-101, F-102).
- Limitación: Qué cuenta como intervención de persona sigue abierto (Q-063). Con la regla actual, una entrada que pide persona y que nadie atiende termina como Self Service (H-072).
- Limitación: R-033 trata Reactivate como puerta y usa las rutas self_serve_puro, hybrid y sales_assisted; C-005 (R-031) lo trata como loop, con las rutas Executive, Self Service, Hybrid A y B. Hay que alinearlos antes de construir.
- Limitación: Recurrente contra único, mes gratis y pausa son decisiones, no hechos.
- Limitación: Reordena las tres ramas de D-001 (cantidad, mezcla, compra según tiempo). Si lo adoptas, hace falta una decisión nueva que referencie D-001 (X-150); no se sobrescribe en silencio.
- Limitación: Salud es la excepción del tramo 2022→2023: su ticket baja recién en 2024 (T-067).
- Limitación: Si aparecen a la vez las firmas de mezcla y de capacidad, se reportan como interacción (H-028), no como hoja nueva.
- Limitación: Sin la regla «precio especial = lista + descuento», los descuentos negociados, de partner o de retención quedarían como precio menor (H-074).
- Limitación: Varias reglas son decisiones de negocio y deben quedar escritas antes (F-241): orden de puerta, cuándo una entrada es nueva, estados New/Working/Engaged, ventana W, umbral de estancamiento y base del puente (lista o neto).
- Limitación: W, el umbral de estancamiento por etapa y el plazo Won → pago son parámetros a acordar con Finora, no estándares de mercado (Q-064).
- Limitación: Won o primer pago como hito de adquisición sigue por acordar con el CRO.
- Limitación: «Quién entra» describe primeros pagadores observados, no la calidad de los leads.
- (El Storyteller anota aquí lo que no se sostenga al diseñar.)

### Notas del Storyteller al diseñar (corrida retomada, 2026-09-29)

- **Dato que no cuadra entre tablas (S18 · C-015):** la mediana del segundo pago (M1) de 2022 es COP 52,5 mil en FIN-F-160 (altas con M1) y COP 46,2 mil en FIN-F-086/FIN-F-087 (otra base de cohorte); 2023 y 2024 también difieren (36,8 vs 35,0; 38,9 vs 37,8). La lámina usa FIN-F-160, como el brief. Hay que fijar una sola base antes de circular el deck.
- **S21 · C-018 «MRR neto, revenue y caja se separan»:** el esquema dibuja lista contra neto (el descuento) y la caja en un carril aparte; el revenue reconocido no se dibuja porque la evidencia (F-153) solo dice que *puede* separarse según el tipo de contrato, no cómo. Se deja como frase literal bajo el esquema.
- **S15 · C-012:** las tres firmas se muestran como mezcla de ajuste · tasa dentro de cada banda · carga y espera al primer contacto. La fila «tasa dentro de cada banda» sale literal de F-122 (es la comparación «mezcla contra tasa» del título); la velocidad de atención queda dentro de «espera al primer contacto».
- **S17 · C-014:** título recortado sin cambiar el argumento; el título completo de Hugo va en las notas del orador (y en `slide-specs/S17.yaml › headline_original`).
- **S06 · C-021:** «tu secuencia literal» (dirigido a Hugo) se cambió por «secuencia literal del brief», porque el deck es para CEO, CRO y CFO.
- **S19 · C-024:** las partes sin firma asignada van en gris y sin cifra: no se calculan restos. El 7,1% de contracción que sube sin llegar (FIN-F-184) queda sin rotular en la barra y va en las notas.
- **S2.1 «Las relaciones que comentó Hugo»:** sigue `missing`; no se diseñó lámina (sin contenido ni cifras).
- **Cifras de 2024 con ventana ene–jul:** el churn observado 2024 (2,04%) de S07 es la ventana ene–jul; otra tabla da 1,9% (X-101). En S10 el dato pasó a las notas del orador.
- **S03 · C-003, para decidir:** el título dice «menor ticket estabilizado, en las 6 industrias», pero el «6 de 6» (FIN-F-114) se mide con el ticket de entrada (primer pago, M0), que en 2022 viene inflado por pagos iniciales grandes (la misma advertencia de S18). El panel central sí es ticket estabilizado (M1, FIN-F-160) y la barra 96/4 es monto usual temprano (FIN-F-164). La lámina ahora rotula cada medida; si quieres que el «6 de 6» también sea estabilizado, falta ese dato por industria.
- **S16 · C-013:** en la capa de suscripción se usa `discount_grant` (nombre de R-034, el mismo objeto de S20 y S22) en vez de `discount` (R-033), y las columnas se nombran como el título: Demanda · Funnel comercial · Suscripción y facturación.
- **Pies de página:** se quitaron los códigos de decisión y de tensión (Q-, D-, X-) de las frases del pie (S09, S14); se conservan los de linaje (C-, R-, F-, FIN-F-).
