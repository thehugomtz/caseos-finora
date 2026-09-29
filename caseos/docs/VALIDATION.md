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

## 8. Tercera ronda (29-sep-2026): Framing & Shaping

Pedido de Hugo: que Framing sea también *shaping* y que su salida sea un documento estructurado —problema, storytelling,
hipótesis y tareas de investigación tipadas (datos, research u otro agente)— que aterrice en Research.

- **Pruebas:** `pytest` → 53 pasan, 1 omitida (en vivo, opt-in). Nuevas: `test_shaping.py` (propuestas que esperan a
  Hugo, revisiones que no sobrescriben, tarea aprobada que se lanza con su agente, migración desde Entregables, el Guion
  llega al Story Package y al Storyteller, ids que no se reutilizan) y `test_shaping_endpoints`.
- **Migración en el caso real** (pedida por Hugo; corrida como `caseos`, todo como propuesta): 3 secciones del Guion
  (Overview 1 lámina, Growth 7, Revenue 4) desde los Entregables aprobados, 5 tareas desde el research necesario del
  Framer (tipo sugerido por el Router) y una versión limpia de Entregables propuesta en el brief. Nada aprobado cambió.
  La bitácora la registra dos veces: la primera corrida le ponía a las tres secciones el mismo «para qué» (la línea de
  Overview menciona Growth y Revenue); se restauró el respaldo, se corrigió y se volvió a correr.
- **UI (sandbox `finora-shaping`, 8781, a 1512×945, claro y oscuro):** escribir y aprobar el problema; aprobar una
  sección; editar Growth (reordenar, añadir y quitar láminas; ids renumerados); cambiar el tipo de una tarea a Datos;
  aprobar todo; añadir y quitar una tarea (con confirmación); «Ver documento»; el plan en Research con *Lanzar*; la
  cobertura del Guion en Story (con evidencia · parcial · sin evidencia); la propuesta de Entregables en Briefing. El
  borrador y el cursor sobreviven a un repintado en vivo. No se lanzó ninguna tarea real (cuota); la ruta de lanzamiento
  está cubierta por pruebas con el lanzador sustituido.
- **Encontrado y corregido:** al añadir una lámina el cursor regresaba al título de la sección (Safari no enfoca
  botones); una tarea nueva reutilizaba el id de una propuesta descartada; el orden del Guion dependía de qué se aprobaba
  primero; la etiqueta «El Briefer propone» aparecía en propuestas que no eran del Briefer.
- **Límite de la herramienta, no de la app:** la tecla Enter del navegador automatizado no inserta salto de línea en un
  textarea; con un teclado real sí.

## 9. Cuarta ronda (29-sep-2026, mañana): el plan sale de las preguntas del guion

Lo que Hugo notó: el plan «se fue a ver cosas de research» cuando casi todo era trabajar propuestas. Una pregunta como
«¿cómo definirías el funnel si no todos lo recorren igual?» ya es investigación y propuesta: con el contexto del caso se
puede poner una respuesta sobre la mesa («todo depende del punto de entrada…») y el preview debería decir «investigar
datos» en el modelo.

- **Plan desde el guion en vivo** (sandbox `finora-plan`, copia idéntica del caso real a las 10:13): 12 tareas para 11
  láminas (7 de propuesta, 5 de datos), cada una con respuesta de arranque en el registro de Hugo, sus palabras
  textuales con ID y pasos con tablas reales; S2.1 queda fuera con su razón («por precisar»). RT-001…RT-005 llegaron
  como versión mejorada. Sin correcciones de las guardas. US$2.28 equivalentes, 14 min, 102 mil tokens de salida.
- **Herramienta del modelo en vivo:** un agente llamó `mcp__caseos_datos__consultar_modelo`, recibió 34 meses de
  `mart.monthly_metrics` y la consulta quedó registrada (US$0.015 con esfuerzo bajo). En la corrida real, Data
  Engineering consultó `mart.new_customers` / `mart.customer_month` por su cuenta.
- **Encontrado y corregido:** las paráfrasis del Framer importadas del brief v0.3 («Separaste…», «Tu lectura fue…») no
  se pueden citar como palabras de Hugo; el plan completo necesitaba su propio tope de gasto (rol `planner`, US$8); una
  reconstrucción del plan también reemplaza los cambios propuestos a tareas aprobadas; los chips de un turno apuntaban a
  propuestas ya reemplazadas; el Story Package solo sabía usar evidencia aceptada (0 en el caso) — ahora hay borrador.

### Corrida en el caso real (29-sep, 10:31 → ~12:00) — delegada por Hugo en el chat (D-016)

Plan aplicado y aprobado «vía Claude», 12 investigaciones lanzadas (R-010…R-021), evaluación del COS de cada una y
borrador del Story Package. Encontrado y corregido sobre la marcha:

- **Números de numpy en YAML:** tres investigaciones de Analytics (R-012, R-017, R-020) terminaron en el workspace pero
  su resultado no se pudo guardar (`np.float64` en las visualizaciones) y la research quedó «running» para siempre.
  Ahora `util.plain` convierte numpy/Decimal antes de escribir, un resultado que no se puede guardar marca la research
  como fallida, y `analytics.recover_research` (acción *recover*) la reconstruye desde la investigación publicada — sin
  volver a correrla y sin duplicar findings (36 findings reutilizados, 36 tablas).
- **Findings de Analytics sin tabla:** sus cifras no podían llegar a la historia hasta un clic por finding. Ahora la
  tabla de evidencia se crea al terminar la investigación (queda propuesta, como el finding).
- **Citas del modelo:** citar el catálogo («no hay tablas de leads») y poner un comentario después del SQL no se podía
  verificar; 7 citas legítimas quedaron «sin verificar». Regla corregida, el catálogo se registra, y la acción
  *reverify* las revisa leyendo `sql_runs` y la traza de herramientas de la corrida (la confianza no se toca).
- **Story Package:** 15 min no alcanzan para una historia completa con esfuerzo max; ahora 40 min.
- **Cola del COS:** con 3 corridas simultáneas y esfuerzo max, cada evaluación tarda ~10 min y cuesta ~US$1.25; doce
  evaluaciones son la parte más lenta del ciclo.
- **Traza del workspace:** los errores de herramienta del investigador ahora dicen qué falló (el investigador los corrige).

- **Esquema del Framer inválido (29-sep, 11:57 → 13:30):** al darle `id` a las tareas del plan, el esquema del Framer lo
  repetía (`required: ["id", "id", …]`) y el CLI rechazaba cada turno antes de empezar; el Challenge de Hugo sobre C-005
  (13:13) falló por eso y quedó guardado para reintentar. Corregido, y `tests/test_schemas.py` revisa todos los esquemas de
  los agentes (metaesquema JSON, obligatorios repetidos o sin definir, `additionalProperties: false`).
- **Cómo se llegó a un claim:** el detalle de un claim muestra lo registrado de la investigación que lo sostiene (sin
  llamar a un modelo). Una versión que le pedía al COS reconstruir el camino fue bloqueada por las salvaguardas del
  modelo y se retiró a pedido de Hugo.

### Corrida en el caso real (29-sep, 14:05 → tarde) — delegada por Hugo en el chat (D-017)

Hugo pidió que el COS y los especialistas respondan las 8 preguntas del caso con propuestas sólidas y que Story lo
muestre. Hecho «vía Claude»: los dos Challenge de Hugo (13:43 sobre C-005, 13:56 sobre C-011) se reintentaron; el COS
revisó la cobertura pregunta por pregunta; sus huecos y las tareas del Framer se aprobaron y lanzaron (R-022…R-028); su
propuesta sobre D-007 quedó registrada como decisión **propuesta** (D-018, decide Hugo); después, borrador 2 del Story
Package. Encontrado y corregido:

- **Un turno largo del Framer se cortaba a los 15 min** (13:43): Framer 40 min, Briefer 30 min, COS (preguntas e
  impacto) 40 min — la revisión de cobertura terminó a los 14 min 59 s; presupuesto del Framer US$8; el aviso de fallo
  dura 20 s y dice por qué.
- **El Framer reescribía una tarea que ya estaba en Research:** una revisión de RT-001 (ya investigada como R-010) no
  lanzaba nada. Ahora la versión nueva entra como tarea nueva que dice qué reformula.
- **El Framer perdía las palabras de Hugo del mismo turno:** citaba su mensaje, pero la nota que las guarda aún no tenía
  ID, y la cita se quitaba («sin referencia válida»). Ahora la cita apunta a la nota de ese turno si sus palabras
  coinciden, y una tarea puede enlazar un item del mismo turno con «#n» (su posición); antes quedaban sueltas (RT-025
  no estaba ligada a las seis causas nuevas H-052…H-057).
- **Story veía 400 caracteres de cada diseño:** el marco de medición o el modelo de datos de un especialista llegaba
  recortado al borrador; ahora llegan el marco, las decisiones que habilita, las métricas, las entidades, la lógica de
  clasificación y ejemplos.
- **Instrucciones delegadas etiquetadas como de Hugo:** el prompt de Story decía «Instrucciones de Hugo» aunque las
  escribiera Claude por delegación; ahora dice de quién son (`via`), y lo textual de Hugo va entre comillas con su ID.
- **Límite de sesión de la suscripción (14:58 → 16:20):** a media corrida, el CLI respondió «You've hit your session
  limit · resets 4:20pm». Cayeron R-029, tres evaluaciones del COS y el primer intento del borrador 2; se reintentaron
  a las 16:21 (research: acción *retry*; COS: *send_to_cos* con nota de reintento). El servidor de vista previa se
  apaga cuando termina el turno de Claude: mientras haya trabajos, el turno sigue abierto.
- **Tope de presupuesto del Story Package:** con el diseño completo de los especialistas en el prompt, el borrador 2
  topó los US$6 equivalentes a los 32 min (sin resultado). Story: US$15 y 60 min.
