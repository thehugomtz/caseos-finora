# Dirección visual — Finora · La brecha clientes–monto se asocia a quién entra; el porqué no está e…

> Producido por `consulting-visual-director` (modo dirección y composición). Corrida CaseOS del 30-sep-2026, deck v5.

## Decisión

**Dirección fijada por Hugo** (no se corrió el board de direcciones, como pide el handoff): su guía de formato aplicada
como tokens en `assets/theme.css` sobre la base «editorial». Títulos Open Sans, texto DM Sans, fondo `#ffffff`,
texto `#101010`, acento `#00d0b3` (en texto chico `#068372`), acento 2 `#a1eb4c`. No se cambió ningún token existente.

Se **agregaron** tokens de apoyo tomados de la misma guía, sin tocar los anteriores (bloque al final de `theme.css`):
`--mint #20eb9b` (solo el separador de Growth), `--coral #ff6364` y `--coral-text #c9393b` (solo alertas o lo que no
existe; la variante oscura pasa 4.5:1 en texto chico) y `--lime-text #4d7a17` (reservado; no se usó).

Referencias → reglas: no hubo capturas nuevas; se reutiliza el sistema del deck v3 re-tematizado.

## Contrato de codificación del deck

| Visual | Significa | Nunca se usa para |
|---|---|---|
| tinta sólida | valor real u observado | potencial |
| acento turquesa | el insight de la lámina (quién entra, el nudo, el descuento, la primera pieza) | marcos, kickers, títulos de sección |
| coral (texto) | lo que hoy no existe en el caso (métricas de funnel, CAC, dato de cada hoja) | énfasis general |
| punteado/discontinuo | propuesto o no construido | series de datos reales |
| grosor de línea | tramo con persona (SDR/AE) contra sin persona | decoración |
| color sólido a sangre | separador de sección (Overview turquesa · Growth menta · Revenue lima · Anexos tinta) | láminas de contenido |

Convenciones fijas: kicker `Sección · tema · propuesta` arriba a la izquierda; título de conclusión ≤ 2 líneas; fuente
abajo a la izquierda con IDs F-/T-; página abajo a la derecha (portadas y separadores sin pie); rótulos directos, sin
leyendas cuando cabe el rótulo.

## Estructura (guía de Hugo)

Portada → Overview → Growth → Revenue → portada final → separador «Anexos» → anexos (lo que el Story Package deja
fuera, en el orden de `appendix_candidates`). La idea central va en las notas de la portada: el guion de Hugo no trae
una lámina de resumen y no se agregó.

## Plan de composición

| # | Lámina | Brief | Claim | Rol | Composición | Familia | Densidad | Focal | Origen |
|---|---|---|---|---|---|---|---|---|---|
| 01 | S01 | — | — | portada | cover | editorial | ligera | título | nueva (guía) |
| 02 | S02 | — | — | separador | section_divider (turquesa) | editorial | ligera | «Overview» | nueva (guía) |
| 03 | S03 | S01 | C-001 | contexto | annotated_chart (divergence) + per_client_strip | evidence | media | la brecha | reutilizada v3 S01 |
| 04 | S04 | S02 | C-026 | diagnóstico | converging_evidence (tres mini-exhibits → pregunta) | process | densa | la pregunta abierta | nueva |
| 05 | S05 | — | — | separador | section_divider (menta) | editorial | ligera | «Growth» | nueva (guía) |
| 06 | S06 | S03 | C-021 | recomendación | stage_matrix (metro map) + reactivate_loop | comparison | densa | lista maestra | rehecha desde v3 S06 |
| 07 | S07 | S04 | C-027 | recomendación | split_and_converge (dos zonas) | process | densa | el nudo | nueva |
| 08 | S08 | S05 | C-007 | diagnóstico | cohort_slope + ranked_bars | comparison | media | cosechas 2023–24 | rehecha (sin puente, D-026) |
| 09 | S09 | S06 | C-028 | recomendación | enable_links (métrica → decisión) | logic | densa | eficiencia | nueva |
| 10 | S10 | S07 | C-023 | recomendación | issue_tree (ramas ordenadas + paso 0) | logic | densa | el orden 1→5 | rehecha desde v3 S14 |
| 11 | S11 | S08 | C-029 | recomendación | match_rows + fastest_test | comparison | densa | prueba más rápida | nueva |
| 12 | S12 | S09 | C-014 | recomendación | layered_stack (capa técnica → dos vías) | operating_model | densa | primera pieza | rehecha desde v3 S17 |
| 13 | S13 | — | — | separador | section_divider (lima) | editorial | ligera | «Revenue» | nueva (guía) |
| 14 | S14 | S10 | C-015 | evidencia | dumbbell + aligned_shares | comparison | media | brecha 2022 | adaptada de v3 S18 |
| 15 | S15 | S11 | C-024 | evidencia | stacked_decomposition (100% por línea) | economics | media | firmas de cobro | adaptada de v3 S19 |
| 16 | S16 | S12 | C-017 | recomendación | object_anatomy + implications_strip | operating_model | densa | objeto Descuento | rehecha desde v3 S20 |
| 17 | S17 | S13 | C-019 | recomendación | staircase (dónde nace cada movimiento) + rule_strip | economics | densa | peldaño Descuento | rehecha desde v3 S22 |
| 18 | S18 | S14 | C-025 | recomendación | small_multiples (mini puentes) + underlying_business | comparison | densa | «Descuento (inicio)» oculto | adaptada de v3 S24 |
| 19 | S19 | — | — | cierre | cover (repetida) | editorial | ligera | título | nueva (guía) |
| 20 | S20 | — | — | separador | section_divider (tinta) | editorial | ligera | «Anexos» | nueva (guía) |
| 21 | S21 | — | C-002 | anexo | marimekko | economics | media | cosechas nuevas | reutilizada v3 S02 |
| 22 | S22 | — | C-003 | anexo | diverging_small_multiples + within_industry_bar | evidence | media | ticket | reutilizada v3 S03 |
| 23 | S23 | — | C-004 | anexo | small_multiples_time + window_highlight | evidence | media | ventana 2023 | reutilizada v3 S04 |
| 24 | S24 | — | C-005 | anexo | split_and_converge + reactivate_loop | process | densa | fijos al entrar | reutilizada v3 S05 |
| 25 | S25 | — | C-006 | anexo | measurement_map | process | densa | el nudo | reutilizada v3 S09 |
| 26 | S26 | — | C-008 | anexo | bubble_matrix | comparison | ligera | Salud | reutilizada v3 S08 |
| 27 | S27 | — | C-009 | anexo | driver_tree + status_markers | logic | densa | eficiencia | reutilizada v3 S10 |
| 28 | S28 | — | C-010 | anexo | formula_anatomy | economics | media | no es CAC | reutilizada v3 S12 |
| 29 | S29 | — | C-022 | anexo | hub_and_spoke | relationships | densa | registro | reutilizada v3 S11 |
| 30 | S30 | — | C-011 | anexo | filter_pipeline | process | densa | Paso 0 | reutilizada v3 S13 |
| 31 | S31 | — | C-012 | anexo | signature_small_multiples | comparison | media | firmas | reutilizada v3 S15 |
| 32 | S32 | — | C-013 | anexo | from_to_architecture | operating_model | densa | llave de cuenta | reutilizada v3 S16 |
| 33 | S33 | — | C-018 | anexo | layered_divergence + mechanism + implications | evidence | densa | descuento | reutilizada v3 S21 |
| 34 | S34 | — | C-020 | anexo | decision_tree | logic | densa | rama «Descuento» | reutilizada v3 S23 |

**Chequeo de ritmo** (`deck-rhythm.md`): ninguna composición repetida seguida en el cuerpo; ninguna familia tres veces
seguidas (09–10 logic, 11 comparison); 0 card grids; 100% de composiciones distintas en el cuerpo (14 de 14).
**Excepción consciente:** Growth tiene siete láminas densas seguidas (06–12) porque el guion de Hugo pone ahí siete
preguntas; el respiro llega con el separador de Revenue (13). Se mitigó variando la gramática en cada una (metro map,
dos zonas, slope, enlaces, árbol, filas de coincidencia, pila) y enlazando S10 → S11 con los mismos números 1–5.
