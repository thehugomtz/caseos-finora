# Dirección visual — Finora · La brecha clientes–monto se asocia a quién entra

> Producido por `consulting-visual-director`. Corrida autónoma (sin usuario disponible): decisiones tomadas y documentadas aquí.

## Referencias → reglas abstractas

Sin capturas de referencia. La única referencia es la nota de Hugo: «Hazlo formato techy minimalista pero sin perder el toque de consultoría». Traducida a reglas:

- **Techy minimalista**: fondo blanco, hairlines de 1,5 px, cero cajas con relleno salvo el marcador lima, cero sombras, cero radios, nombres de tablas y campos en mono (IBM Plex Mono, ya en los tokens `--font-mono`), números tabulares.
- **Toque de consultoría**: título-conclusión en cada lámina, un solo exhibit dominante, etiquetas directas (sin leyendas), anotación anclada al dato con líder + punto, línea de fuente con linaje (F-xxx) en el footer, tracker de sección en el kicker.

## Direcciones propuestas

No se corrió el board de direcciones (instrucción del handoff). La dirección es **la guía de formato de Hugo**, ya aplicada como tokens en `assets/theme.css` sobre la base «editorial»: títulos Open Sans (solo peso 400 vendorizado), texto DM Sans, fondo #ffffff, texto #414244, acento #b0ee45, acento 2 #43d6bb; `accent-text` #687e44 para texto chico del acento. No se tocaron tipografías ni colores.

## Decisión y sistema

**Contrato de codificación (se audita en cada lámina):**

| Visual | Significa | Nunca para |
|---|---|---|
| tinta sólida (`ink`) | lo observado / lo que existe hoy en los datos | lo propuesto |
| punteado (`dash`) | propuesto, no existe todavía (to-be, etapas, métricas que hoy no se calculan) | conectores, rejillas, totales |
| **lima** (`accent`) | **el insight**: una marca por lámina, usada como marcador (relleno, subrayado grueso, franja) | kickers, marcos, categorías |
| texto del insight | `accent-text` (#687e44) sobre blanco o tinta sobre lima (7,4:1) | texto de contexto |
| gris (`ink-4`, `ink-5`) | contexto | el insight |
| grosor de línea | en rutas: tramo con persona (grueso) vs sin persona (delgado) | decoración |
| mono | identificadores técnicos (tablas, campos) | prosa |

- **Acento 2 (#43d6bb)**: reservado. Ninguna lámina necesitó una segunda categoría que no se resolviera con tinta/gris; usarlo como decoración violaría «acento solo para el insight».
- **Semáforo (S10)**: se codifica con el llenado del marcador (● verde = se calcula hoy · ◐ amarillo = proxy por aprobar · ○ rojo = falta el dato) para no introducir rojo/verde/amarillo fuera de la paleta.
- **Sistema fijo**: márgenes 112 px, grilla 12 × 144; kicker en mayúsculas `ink-3` con formato «Sección · subtema» (+ «· propuesta» en las láminas de diseño); título Open Sans 56 px; footer «Fuente: …» a la izquierda y página a la derecha; anotaciones de datos con líder + punto; agrupaciones con llaves/brackets; conectores 2 px `ink-3`, énfasis 3 px.
- **Números**: formato del storyline (coma decimal, punto de miles: 1.678; COP 92,8 mil). Solo valores literales de `data/*.yaml` o del brief; los esquemas sin datos llevan «esquema ilustrativo, sin cifras».

## Composition plan

| # | Slide | Rol | Composición | Familia | Densidad | Focal |
|---|---|---|---|---|---|---|
| 00 | S00 | governing thought | single_big_statement + section_tracker | editorial | ligera | statement con «quién entra» |
| 01 | S01 | context | annotated_chart (divergencia) + per_client_strip | evidence | media | cuña de la brecha |
| 02 | S02 | diagnosis | marimekko | economics | media | cosechas 2023–24 |
| 03 | S03 | evidence | diverging_small_multiples | evidence | media | ticket estabilizado |
| 04 | S04 | evidence | small_multiples_time + window | evidence | densa | franja 2023 jun–dic |
| 05 | S05 | recommendation | split_and_converge | process | densa | entrada: puerta y canal fijos |
| 06 | S06 | recommendation | stage_matrix (metro map) | comparison | densa | fila Executive outbound |
| 07 | S07 | diagnosis | bridge + ranked_bars | economics | media | paso de composición |
| 08 | S08 | implication | bubble_matrix | comparison | ligera | Salud |
| 09 | S09 | recommendation | measurement_map | process | densa | franja del nudo |
| 10 | S10 | recommendation | driver_tree + semáforo | logic | densa | rama Eficiencia |
| 11 | S11 | recommendation | hub_and_spoke (registro) | relationships | media | registro del catálogo |
| 12 | S12 | limitation | formula_anatomy + slope | economics | ligera (respiro) | «no es CAC» |
| 13 | S13 | evidence | filter_pipeline | process | media | Paso 0 |
| 14 | S14 | recommendation | issue_tree + palancas | logic | densa | regla de orden |
| 15 | S15 | recommendation | signature_small_multiples | comparison | media | firmas |
| 16 | S16 | recommendation | from_to_architecture | operating_model | densa | espina account |
| 17 | S17 | recommendation | operating_cadence + carril continuo | operating_model | densa | decisiones |
| 18 | S18 | evidence | dumbbell | comparison | ligera (respiro) | brecha 2022 |
| 19 | S19 | diagnosis | stacked_decomposition | economics | media | segmentos de cobro |
| 20 | S20 | recommendation | lineage_flow | process | densa | discount_grant |
| 21 | S21 | recommendation | layered_divergence + mecanismo | evidence | densa | revenue no capturado |
| 22 | S22 | recommendation | staircase | economics | ligera | MRR neto |
| 23 | S23 | recommendation | decision_tree | logic | densa | rama «Descuento» |
| 24 | S24 | implication | small_multiples (mini puentes) | comparison | media | caso 2 |

Chequeo de ritmo: 25 composiciones distintas (100%); ninguna familia tres veces seguida; 0 card grids; respiros en S00, S08, S12, S18 y S22 después de tramos densos; el pivote a propuesta (S05) y a Revenue (S18) cambian de familia.
