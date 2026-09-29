# Guardrails

Dos clases de reglas, y conviene no confundirlas:

- **En código** — se cumplen siempre, sin importar lo que conteste el modelo. Tienen prueba.
- **En instrucciones** — están en `agents/*.md` y en las skills; el modelo las sigue casi siempre, pero no hay garantía
  mecánica. Donde se pudo, se añadió una verificación que las **marca** (no las bloquea).

## En código

| Regla | Dónde | Prueba |
|---|---|---|
| Solo Hugo marca Ready, reabre, resuelve alertas y confirma decisiones | `phases.mark_ready`, `phases.reopen`, `cos.resolve_alert`, `decisions.confirm` (`actor == "hugo"`) | `test_only_hugo_marks_ready`, `test_cos_contradiction_flags_claim_and_waits_for_hugo` |
| Una fase no avanza con bloqueos (brief sin entregables, framing sin pregunta ejecutiva, sin hipótesis o sin el problema aprobado en el Shaping, story inválida…) | `phases.readiness` | `test_framing_gate_requires_question_and_hypothesis`, `test_api_flow` |
| Mark Ready = snapshot + artefacto aprobado versionado + decisión + brain.md + hora + desbloqueo; la versión anterior se conserva | `phases.mark_ready` | `test_mark_ready_snapshot_decision_brain_unlock` |
| Reabrir exige razón, muestra el impacto antes y marca needs_review lo afectado; no borra nada | `phases.impact`, `phases.reopen`, `lineage.impact_radius` | `test_reopen_flags_downstream_without_deleting` |
| Todo lo que produce un agente entra como propuesto; las decisiones de agentes quedan `proposed` | `store.create`, `decisions.record_decision` | `test_messy_text_is_classified_guarded_and_keeps_hugo_words` |
| Un FACT sin base (brief, material del caso o evidencia **aceptada**) se reclasifica | `framer.guard` | `test_fact_needs_accepted_evidence` |
| El Briefer solo propone: nada entra al brief sin que Hugo lo apruebe o lo edite; una propuesta sobre una sección aprobada es una revisión; el enunciado pegado lo guarda el código literal | `briefing.propose` / `approve`, `briefer.guard` | `test_briefer_proposes_and_hugo_approves_section_by_section`, `test_reframe_is_a_revision_not_an_overwrite`, `test_pasted_statement_is_stored_verbatim_by_code` |
| El Framer solo propone el Shaping (problema, guion, tareas): nada entra al documento sin que Hugo lo apruebe o lo edite; una propuesta sobre algo aprobado es una revisión | `shaping.propose` / `approve` (`actor == "hugo"`) | `test_proposals_wait_for_hugo_and_approved_content_is_his`, `test_revision_of_an_approved_section_does_not_overwrite_it` |
| Una tarea del plan se lanza solo si está aprobada y por clic de Hugo; ya lanzada no se puede quitar (se rechaza en Research); los ids no se reutilizan | `shaping.send_task`, `shaping.remove`, `next_*_id` | `test_an_approved_task_launches_with_its_agent`, `test_ids_are_never_reused`, `test_shaping_endpoints` |
| Lo que un agente escribe en una tarea se revisa antes de ser propuesta: láminas e IDs que existen, citas de Hugo textuales (nunca una paráfrasis) que coinciden con lo que dijo, «investigar datos» solo con tablas del modelo, y cifras de la respuesta de arranque con fuente en el contexto (si no, se marcan) | `shaping.guard_tasks` | `test_the_guion_becomes_tasks_with_a_starting_answer_and_real_steps` |
| Rehacer el plan no toca lo aprobado: reemplaza propuestas sin aprobar y, para una tarea aprobada, propone un cambio; una tarea lanzada no se cambia | `shaping.supersede_pending_tasks`, `planner.apply_plan` | `test_a_new_plan_can_improve_an_approved_task_but_not_a_launched_one` |
| Un especialista consulta el modelo de datos solo en lectura, y una cifra del modelo cuenta solo si su consulta corrió en la corrida | `llm.data_tool_handlers` + `datamodels.guard_sql`, `research.verify_citations` | `test_data_tools_are_read_only_and_log_what_ran`, `test_a_model_citation_counts_only_if_its_query_ran`, `test_a_launched_task_takes_its_starting_answer_and_the_model_to_the_specialist` |
| La estructura de la historia no vive en Entregables: el Briefer la deja fuera y la migración la mueve al Guion solo como propuesta | `briefer.guard`, `shaping.migrate` | `test_storyline_moves_out_of_the_brief_as_proposals` |
| El Story Package sigue el Guion: una lámina sin evidencia queda `missing` y se avisa; nunca se rellena | `story.validate_package` (`guion_map`) | `test_guide_reaches_story_package_and_storyteller` |
| El modelo de datos es de solo lectura: una SELECT sobre raw/staging/mart; sin archivos, sin escrituras, sin reconfigurar | `datamodels.guard_sql`, DuckDB con `enable_external_access=false` y `lock_configuration` | `test_queries_are_read_only_and_limited` |
| Las capas cuadran y se puede comprobar una tabla re-ejecutando su consulta | `datamodels.checks`, `verify_table` | `test_three_layers_and_every_check_passes`, `test_an_evidence_table_is_verified_against_the_model` |
| Hipótesis sin falsificador quedan marcadas | `framer.guard`, `framer.apply_turn` | idem |
| Advisors ≤ 2, alternativas ≤ 3, Organize sin alternativas, Challenge solo en su modo | `framer.guard` | `test_mode_limits_on_alternatives` |
| Las palabras de Hugo nunca se reemplazan en silencio (historial visible) | `framer.apply_turn` | `test_messy_text_…` |
| Referencias a IDs inexistentes se descartan y se reporta | `framer.guard`, `research._persist`, `story.apply_package` | varias |
| Research sin propósito de caso no se lanza sin decisión de Hugo | `research.map_purpose`, `create_request` | `test_research_without_case_purpose_waits_for_hugo` |
| Una cita solo cuenta si su URL se recuperó en esa corrida; si no, el claim baja a confianza baja y se marca | `research.verify_citations` | `test_citations_must_come_from_retrieved_urls`, `test_specialist_run_…` |
| Las cifras viajan en tablas: una cifra de un claim que no está en sus tablas invalida el Story Package | `evidence.unsupported_numbers`, `story.validate_package` | `test_story_package_validation` |
| Las cantidades con letras («a la mitad», «el doble», «por cuatro») deben coincidir con las cifras del claim o sus tablas | `evidence.verbal_ratio_issues`, `story.validate_package` | `test_quantities_in_words_must_match_the_data`, `test_story_package_rejects_a_headline_the_data_does_not_support` |
| Claims sin evidencia aceptada, o que dependen de algo needs_review, invalidan el paquete | `story.validate_package` | idem |
| Evidencia que contradice o debilita un claim/hipótesis lo marca needs_review (sin reescribirlo) y abre una alerta con opciones | `cos._impact_job` | `test_cos_contradiction_…` |
| El Storyteller solo recibe un Story Package aprobado y válido; escribe solo en su carpeta; Bash solo scripts del renderer | `storyteller.prepare`, `storyteller._guard` | `test_visual_storyteller_accepts_the_story_package`, `test_storyteller_run_is_confined_to_its_deck` |
| Salidas de agentes validadas contra JSON Schema antes de tocar el estado | `llm.AgentSDKLLM.run` (`output_format`) | — |
| Ninguna solicitud se pierde: se guarda antes de correr, se reintenta, se recupera al reiniciar | `jobs.py`, `framer.recover_turns` | `test_api_flow` |

## En instrucciones (con verificación que marca)

| Regla | Dónde se pide | Qué se verifica |
|---|---|---|
| «El vocabulario técnico aclara, no actúa»: sin jerga performativa, términos nuevos explicados, respuesta en el idioma del caso | `adaptive-case-framer`, kernel de CaseOS | `language.assess` en cada turno del Framer: los problemas se anotan en las correcciones del turno |
| Lenguaje asociativo, no causal, con evidencia observacional | `story-package`, kernel | `story.validate_package` lo marca como aviso |
| Recomendaciones condicionales | `story-package` | — |
| No inventar fuentes | research skills | `verify_citations` (arriba) |
| Una sola pregunta aclaratoria en Organize | `clarification-protocol` | — |
| Traza operativa, nunca cadena de pensamiento | kernel | la UI muestra herramientas, skills, handoffs y validaciones; no hay campo de razonamiento |

## Datos y seguridad

Sin secretos en el repo (`.env` ignorado; los agentes usan la sesión local). Servidor solo en `127.0.0.1`. Rutas de
archivo con guarda del caso. El workspace de Finora se monta sin modificarse (su árbol de git sigue limpio y sus 94
evaluaciones pasan).
