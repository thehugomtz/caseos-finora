# Dónde verificar que esto corrió

Todo lo del caso Finora vive en archivos legibles (YAML, JSON y Markdown) dentro de `caseos/cases/finora/` y
`finora-eda/investigations/`. Ningún número del caso se escribió a mano para la demo. Para un resumen:

```bash
python3 scripts/evidencia.py
```

## CaseOS · `caseos/cases/finora/`

| Qué | Dónde | Qué mirar |
|---|---|---|
| Cada corrida de un agente | `audit/runs/RUN-*.json` | Hay 70. Cada una tiene agente, propósito, modelo (`claude-opus-5-5`), esfuerzo (`max`), prompt de sistema y prompt, herramientas, traza de herramientas con su minuto, tokens, costo equivalente, duración y autenticación usada |
| Los prompts que se usaron | `audit/prompts/*.md` | El prompt completo de cada corrida, por hash |
| La bitácora | `audit/activity.jsonl` | Tiene más de 2,200 eventos, de una línea cada uno: hora, autor (`hugo`, un agente, `system` o `claude`), verbo, IDs y resumen. Lo que Hugo delegó en Claude Code dice «vía Claude» |
| Trabajos en segundo plano | `audit/jobs/JOB-*.json` | Hay 79, cada uno con su progreso y su resultado |
| Versiones anteriores de cada entidad | `audit/versions/` | Cada cambio guarda la versión previa |
| El caso congelado en cada «Ready» | `snapshots/<fase>/<versión>/` | Copias completas al marcar Briefing, Framing, Research, Synthesis y Story como listas |
| Decisiones | `decisions/D-*.yaml` | Hay 29, cada una con quién decidió, cuándo y por qué. D-016, D-017, D-023 y D-027 son delegaciones explícitas de Hugo a Claude |
| Evidencia | `evidence/findings/F-*.yaml`, `evidence/tables/T-*.yaml` | Hay 252 hallazgos, cada uno con su fuente, su confianza y su estado de revisión. Las 109 tablas traen su fuente y, si salieron del modelo de datos, la consulta |
| Investigaciones | `research/R-*.yaml` | Hay 36: la pregunta, el especialista, la respuesta, las afirmaciones con fuente y la evaluación del Chief of Staff |
| La historia | `story/package.yaml`, `story/claims/C-*.yaml` | Cada afirmación con su evidencia aceptada. El código valida que cada cifra exista en una tabla |
| Los decks | `slides/decks/*/` | El storyline, las specs por lámina, el HTML de cada lámina y sus renders. `caseos-run.json` es la traza de la corrida del Visual Storyteller; `edits.jsonl` registra las ediciones posteriores y `revisions/` los cambios puntuales que pidió Hugo |
| El estado del caso para los agentes | `brain.md` | Se regenera con cada cambio importante |

Las dos corridas del Visual Storyteller costaron US$28.7 (deck v3, 29 de septiembre) y US$22.9 (deck v5, 30 de
septiembre, 49 minutos).

## Business Exploration Workspace · `finora-eda/`

| Qué | Dónde |
|---|---|
| Corridas del agente de EDA, con modelo (`claude-opus-5`), pasos, consultas SQL, validación y tiempos | `investigations/runs/INV-*.json` |
| La investigación dorada, «¿Por qué disminuyó el MRR por cliente?» | `investigations/golden/Q2.json` |
| Las preguntas del caso | `investigations/caso/W0–W5.json` |
| El cerebro del caso: respuestas verificadas, hallazgos canónicos, métricas y reglas de lenguaje | `brain/` |
| La Fase 1 reproducible: el script que recalcula todo desde los CSV | `finora_eda.py` → `finora_eda.html`, `finora_analytical_dataset.csv`, `supporting/` |

## Git

El historial de las dos herramientas está completo en este repo, del 27 al 30 de septiembre de 2026, y resumido en
[HISTORIAL.md](HISTORIAL.md). `git log -- caseos` y `git log -- finora-eda` muestran cada uno por separado.

## Comprobar una cifra

En CaseOS, **Datos** → cualquier tabla de evidencia → **Comprobar**. Re-ejecuta su consulta sobre el modelo de datos
(raw → staging → mart) y compara. Los 7 checks de reconciliación muestran que las capas cuadran al centavo.
