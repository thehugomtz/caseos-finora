# Validación (28-sep-2026)

Qué se probó, con qué resultado y qué se corrigió en el camino. Costos = equivalente en dólares que reporta el SDK;
con suscripción no se factura por corrida.

## 1. Pruebas automáticas

`.venv/bin/python -m pytest -q tests` → **32 pasan**, 1 omitida (la eval en vivo, opcional).
`CASEOS_LIVE=1 .venv/bin/python -m pytest -q tests/test_live.py` → **pasa** con el modelo real (119 s): respuesta en el
registro de Hugo, sin jerga performativa ni inglés, su intuición como USER_INTUITION (no FACT), hipótesis con
falsificador, sus palabras junto a la estructura y su vocabulario preservado.

| Área (§89) | Pruebas |
|---|---|
| Persistencia, IDs, linaje | `test_persistence_survives_reload`, `test_ids_are_sequential_and_never_reused` |
| Compuertas | `test_only_hugo_marks_ready`, `test_mark_ready_snapshot_decision_brain_unlock`, `test_framing_gate_requires_question_and_hypothesis`, `test_reopen_flags_downstream_without_deleting`, `test_brain_sections_present` |
| Framing: texto desordenado → clasificación | `test_messy_text_is_classified_guarded_and_keeps_hugo_words`, `test_fact_needs_accepted_evidence`, `test_mode_limits_on_alternatives`, `test_challenge_mode_keeps_the_challenge_block` |
| Adaptación de lenguaje | `test_performative_jargon_is_flagged`, `test_hugo_terms_and_explained_terms_are_fine`, `test_english_reply_in_a_spanish_case_is_flagged`, `tests/test_live.py` (en vivo) |
| Ruteo de research | `test_routing_by_intensity_and_specialty`, `test_analytics_route_requires_a_workspace`, `test_research_without_case_purpose_waits_for_hugo` |
| Disciplina de citas | `test_citations_must_come_from_retrieved_urls`, `test_specialist_run_persists_proposed_findings_with_lineage` |
| Handoff Analytics → EvidenceTable | `test_analytics_finding_becomes_a_canonical_evidence_table` (contra el workspace real), `test_table_contract_and_unsupported_numbers`, `test_numbers_in_spanish_formats` |
| COS marca claims afectados | `test_cos_flags_claims_on_the_same_lineage`, `test_cos_contradiction_flags_claim_and_waits_for_hugo`, `test_alert_on_the_framing_itself_resolves_cleanly` |
| Story Package | `test_story_package_validation`, `test_story_package_is_versioned_and_proposed_for_review`, `test_quantities_in_words_must_match_the_data`, `test_story_package_rejects_a_headline_the_data_does_not_support` |
| Visual Storyteller acepta el paquete | `test_visual_storyteller_accepts_the_story_package` (usa el `new-deck.mjs` real), `test_storyteller_run_is_confined_to_its_deck` |
| API | `test_api_flow` (crear caso, compuertas, turno del Framer como job lanzado desde un hilo, comandos, búsqueda) |

## 2. No se rompió lo existente

- finora-eda: árbol de git limpio (CaseOS no modificó nada); `.venv/bin/python -m evals.run_evals` → **94/94**.
- Respaldo previo: tag `pre-caseos-2026-09-28` + bundle + tgz del estado de ejecución en `Claude Prueba/_backups/`.

## 3. Flujo en vivo (modelo real, `claude-opus-5` effort high, suscripción)

Las pruebas en vivo corrieron en un **sandbox** (`.runtime/e2e/cases`, puerto 8781: copia de Finora con los mensajes de
“Hugo” escritos por Claude). El caso real `cases/finora` se reimportó limpio al final: ahí no hay nada escrito a nombre
de Hugo.

| Paso | Resultado | Costo · tiempo |
|---|---|---|
| Framer · Organize («creo que están metiendo más leads pero esa madre no está convirtiendo…») | Respuesta en su registro; 9 elementos: intuiciones como USER_INTUITION con sus palabras, hipótesis con falsificador, supuesto «MRR por cliente = recurrente» explícito, una sola pregunta aclaratoria; términos nuevos explicados («mezcla»). Chequeo de lenguaje OK. | US$0.36 · 94 s |
| Framer · Challenge | Supuestos ocultos con confianza/impacto, contraargumento más fuerte, explicación alternativa (salida de clientes caros + primer pago prorrateado), evidencia que la invalidaría, claim de mayor riesgo. Tono tranquilo. | US$0.39 · 99 s |
| Framer · Advise («¿cómo separamos mezcla de nivel de entrada sin prometerle al CFO algo que no podemos medir?») | Empieza por lo incómodo (ya hay evidencia que empuja hacia su lectura); 3 alternativas con cuándo gana y qué cuesta; una lente (CFO) ruteada; carga las skills core de Advise (bulletproof, consulting); dice qué **no** prometer (tarifa vs descuento). | US$0.51 · 106 s |
| Research L1 (Business) «¿Qué significa ARPA…?» | El Router la reformuló para el caso; 3 fuentes, **todas verificadas** contra 17 URLs recuperadas; 5 findings propuestos enlazados a H-024 («respaldo conceptual, no evidencia sobre Finora»). | US$0.59 + ruteo 0.08 · 3.7 min |
| Research Measurement (Router → L3) sobre la pregunta del CRO | Registro de hitos por cuenta en vez de funnel lineal: 8 eventos, 13 métricas, 6 dimensiones, la decisión del CRO que habilita; 8 fuentes verificadas (65 URLs). | US$1.59 + 0.09 · 8 min |
| COS · impacto de R-011 (automático) | 5 alertas con opciones A/B/C y recomendación; H-017 y H-023 marcadas needs_review sin reescribirse; conserva el vocabulario de Hugo como opción. | US$0.25 · 79 s |
| COS · impacto de R-010 | 5 alertas (hipótesis del CRO no contrastables hoy, dividir Q-001). Interrumpida una vez por un reinicio del servidor: la solicitud se conservó y el reintento funcionó. | US$0.44 · 2 min |
| Ciclo de iteración | Alerta → decisión de Hugo → framing needs_review → Framer aplica el cambio (y detecta que evidencia ya aceptada usa el nombre viejo) → Framing Ready v2. | US$0.34 · 53 s |
| Compuertas | Briefing → Framing (v1, v2) → Research → Synthesis → Story Ready, cada una con snapshot, decisión y artefacto aprobado. | — |
| Story Package | 4 claims (contexto · diagnóstico · descarte · limitación), recomendaciones condicionales («no decidir precio con este paquete»); **validación OK sin errores ni avisos** al primer intento. | US$0.42 · 108 s |
| COS · pregunta libre («qué falta para cerrar la historia para el CFO?», vía command layer) | Detecta que el paquete responde la composición pero no la pregunta literal del CFO (contrato vs tarifa vs descuento); propone opciones A/B/C con recomendación y «tú decides»; señala que el puente (T-003) no está en la historia y que el caveat clave descansa en research sin revisar. | US$0.38 · 99 s |
| Visual Storyteller | 4 slides, 4/4 PASS, linaje slide → claim → tabla cerrado (sección 5). | US$8.87 · 27 min |

## 4. Errores encontrados y corregidos durante la validación

1. El Framer devolvía 500: `jobs.submit` buscaba el loop desde un hilo del threadpool → se agenda en el loop del servidor.
2. Un turno quedaba «en cola» para siempre tras un reinicio → `recover_turns` al arrancar; si el envío falla, el turno queda fallido y reintentable.
3. Refinar un elemento importado reemplazaba las palabras de Hugo → quedan en `hugo_wording_history`.
4. Modo Organize podía devolver alternativas si el modelo mandaba más de 3 → siempre vacías en Organize.
5. **Toda investigación no-analytics fallaba** (`dict.fromkeys` sobre dicts en `_case_context`) → corregido; la prueba lo cubre.
6. Una ruta fijada por Hugo pasaba dicts como IDs de skills → el loader acepta ambos.
7. Al completar una investigación, la pregunta reformulada por el agente sobrescribía la de Hugo → la de Hugo se conserva; la del agente va en `worked_question` y se muestra debajo.
8. Evidencia que contradice/debilita un claim o hipótesis no lo marcaba needs_review → ahora sí (sin reescribirlo); descartar la alerta lo limpia.
9. Resolver una alerta sobre el framing fallaba después de registrar la decisión (quedaba a medias) → validación previa; el cambio de framing pasa por el Framer y marca la fase needs_review.
10. El COS no veía el texto de los candidatos por linaje (pidió «el enunciado de Q-016») → el prompt incluye su texto; el digest mapea alertas resueltas → decisión.
11. UI: 4 de 8 pestañas del ledger del framing quedaban recortadas; ⌘K no cerraba con Escape si el foco salía del input; fuentes duplicadas por finding; un agente en reposo decía «borrador»; título «cambia el framing framing».
12. «qué falta para cerrar» sin complemento caía al clasificador → comando determinista.
13. Rutas relativas de `CASEOS_CASES_DIR` se mostraban mal en la traza → se resuelven a absolutas.
14. Se podía lanzar un segundo Storyteller mientras corría otro, y un deck quedaba «en curso» para siempre tras un reinicio → bloqueo en servidor y UI; `recover_decks` al arrancar marca interrumpido.
15. Caracteres de ancho cero al inicio de respuestas rompían los títulos Markdown → se limpian al renderizar.
16. Demo mode: tres pasos no encontraban qué resaltar en un caso nuevo → selector del decision log y respaldo al estado vacío de la vista.
17. Cantidades con letras que contradicen los datos pasaban la validación del Story Package (ver sección 5) → `evidence.verbal_ratio_issues`.

## 5. Visual Storyteller en vivo

Story Ready (D-029) → `prepare` (con el `new-deck.mjs` del renderer: storyline pre-llenado, 3 tablas en `data/*.yaml`,
`caseos-handoff.yaml`) → corrida con las skills **enlazadas** (la sesión las descubre: `executive-visual-storyteller`,
`executive-storyline`, `consulting-visual-director`, `html-slide-renderer`, `slide-critic`), dirección *editorial*, sin
crítico independiente (para una sola pasada; se declara en su reporte de QA).

- **Resultado:** 4 slides (una por claim), 4 composiciones distintas (`divergence_panels`, `step_down_with_volume`,
  `hypothesis_knockout`, `denominator_conflation`), 3 rondas de QA con renders por ronda, **4/4 PASS**, 0 errores y 0
  avisos automáticos, fidelidad 0% de píxeles distintos, `presentation.html` + PDF. 27 min · 99 turnos · US$8.87.
- **Linaje cerrado:** cada slide se importó como S-001…S-004 con su `claim_id` (C-001…C-004); cada pie de slide cita la
  tabla y el claim (p. ej. «Fuente: T-001 · FIN-GROWTH-01 … · CaseOS C-001»). Slides quedó *por revisar* (gate de Hugo).
- **Guardas:** todas las escrituras de la corrida quedaron dentro de la carpeta del deck. La guarda (probada en
  `test_storyteller_run_is_confined_to_its_deck`) permite los scripts del renderer y copias dentro del deck, y niega
  escrituras fuera, `rm`, `node -e` en línea y herramientas no habilitadas. Desde esta validación cada negación queda en
  la traza (`caseos-run.json › denials` y un evento en vivo); en esta corrida todavía no se registraban.
- **Lo que atrapó el Storyteller:** el titular aprobado de C-001 decía que el monto «cayó a la mitad»; la tabla dice
  COP 92,8 → 57,8 mil (×0.62). No lo dibujó: usó la redacción literal del finding («más de 30%»), lo documentó en
  `storyline.md §7` y dejó la reversión a una línea. La validación de CaseOS solo revisaba cifras escritas con dígitos;
  **ahora también revisa cantidades con letras** («a la mitad», «el doble», «por cuatro»…) contra las cifras del claim y
  sus tablas (error si las contradicen; aviso si no hay contra qué comprobar). Re-validado el paquete del sandbox, marca
  exactamente C-001 y nada más.

Deck: `.runtime/e2e/cases/finora/slides/decks/finora-sandbox-d-v1-20260928-222214/presentation.html`.

## 6. UI

Recorrido de todas las vistas a 1512×945 (Home, Briefing, Framing, Research + detalle, Chief of Staff, Story, Slides,
Agents, Artifacts, Analytics): sin desbordes horizontales ni texto recortado tras la corrección de las pestañas; ⌘K busca
por ID y texto; el detalle de research muestra respuesta, findings con evidencia, fuentes, límites y acciones.

## 7. Segunda ronda (28-sep-2026, noche): Opus 5.5 max, caso en blanco, Briefing conversacional, modelo de datos, tema claro, guía de formato

- **Modelo:** `claude-opus-5-5` con esfuerzo `max` verificado en vivo sobre la suscripción (`apiKeySource: none`).
- **Pruebas:** `pytest` → 46 pasan (nuevas: `test_briefing.py`, `test_datamodels.py`, `test_slidestyle.py`).
- **Modelo de datos (real):** raw 3 tablas · staging 3 vistas · mart 7 tablas/vistas; **7/7 checks** (66.674 filas
  raw = staging = mart; monto por mes al centavo en 34 meses; 1.961 clientes; S&M por mes; 19 pruebas de paridad del
  workspace). Consola: `SELECT … FROM mart.monthly_metrics` 34 filas en ~30 ms; `DELETE`, `read_csv`, `COPY`, `ATTACH` y
  cambios de configuración rechazados.
- **Briefer en vivo** (sandbox, caso «Prueba en blanco»): 7 propuestas con base (`hugo` o `inferido`), las palabras de
  Hugo al lado, una sola pregunta acotada, y detectó con el modelo de datos que no hay precios de lista ni descuentos.
  Costo: US$0.94 · **6.8 min** (43.644 tokens de salida en esfuerzo max).
- **UI:** aprobar, editar y aprobar, descartar y *Mark Ready* probados con clics; el borrador sobrevive a un repintado en
  vivo; vista Datos (linaje, detalle, muestra, consola, checks); guía de formato con vista previa; claro y oscuro.
- **Encontrado y corregido:** meses ISO (`2024-08`) se leían como el número 8 en la disciplina de cifras; `data_model`
  no viajaba en el resumen del caso; la guía de colores se encimaba en paneles angostos; Python sin certificados para
  bajar Google Fonts (se usa certifi).
