# Guardrails

Dos clases de reglas, y conviene no confundirlas:

- **En código** — se cumplen siempre, sin importar lo que conteste el modelo. Tienen prueba.
- **En instrucciones** — están en `agents/*.md` y en las skills; el modelo las sigue casi siempre, pero no hay garantía
  mecánica. Donde se pudo, se añadió una verificación que las **marca** (no las bloquea).

## En código

| Regla | Dónde | Prueba |
|---|---|---|
| Solo Hugo marca Ready, reabre, resuelve alertas y confirma decisiones | `phases.mark_ready`, `phases.reopen`, `cos.resolve_alert`, `decisions.confirm` (`actor == "hugo"`) | `test_only_hugo_marks_ready`, `test_cos_contradiction_flags_claim_and_waits_for_hugo` |
| Una fase no avanza con bloqueos (brief sin entregables, framing sin pregunta ejecutiva o sin hipótesis, story inválida…) | `phases.readiness` | `test_framing_gate_requires_question_and_hypothesis`, `test_api_flow` |
| Mark Ready = snapshot + artefacto aprobado versionado + decisión + brain.md + hora + desbloqueo; la versión anterior se conserva | `phases.mark_ready` | `test_mark_ready_snapshot_decision_brain_unlock` |
| Reabrir exige razón, muestra el impacto antes y marca needs_review lo afectado; no borra nada | `phases.impact`, `phases.reopen`, `lineage.impact_radius` | `test_reopen_flags_downstream_without_deleting` |
| Todo lo que produce un agente entra como propuesto; las decisiones de agentes quedan `proposed` | `store.create`, `decisions.record_decision` | `test_messy_text_is_classified_guarded_and_keeps_hugo_words` |
| Un FACT sin base (brief, material del caso o evidencia **aceptada**) se reclasifica | `framer.guard` | `test_fact_needs_accepted_evidence` |
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
