# Qué se reutilizó, qué se adaptó, qué es nuevo

Regla del build: inspeccionar primero, reutilizar lo que ya funciona, no reconstruir el Executive Visual Storyteller, no
romper la versión existente.

## Respaldo antes de empezar

- `finora-eda`: tag de git `pre-caseos-2026-09-28`.
- `Claude Prueba/_backups/finora-eda-pre-caseos-2026-09-28.bundle` (repo completo) y
  `finora-eda-runtime-pre-caseos-2026-09-28.tgz` (estado de ejecución no versionado: brain, investigaciones, corridas).
- Verificación al cierre: el árbol de git de finora-eda sigue **limpio** (CaseOS no modificó un solo archivo) y sus
  **94/94 evaluaciones** pasan (`.venv/bin/python -m evals.run_evals`).

## Reutilizado tal cual

| Componente | Cómo lo usa CaseOS |
|---|---|
| **Business Exploration Workspace** (`../finora-eda`) | Montado en el mismo proceso en `/ws/finora` (su UI y su API sin cambios). CaseOS lee su brain (métricas, issues, hallazgos canónicos, preguntas y respuestas del caso), sus investigaciones (`runs/`, `caso/`, `golden/`) y sus narrativas; lanza su investigador (`agent.orchestrator.run`) para research de Analytics. Sus validadores, registro de evidencia y SQL de solo lectura siguen siendo los que garantizan cada cifra. |
| **Executive Visual Storyteller** (`~/.claude/skills`: executive-visual-storyteller, executive-storyline, consulting-visual-director, html-slide-renderer, slide-critic; `~/.claude/agents`: executive-visual-storyteller, independent-slide-critic) | **Enlazado por symlink, no copiado ni reescrito.** CaseOS solo le prepara la entrada (storyline pre-llenada desde el Story Package aprobado, `data/*.yaml`, `caseos-handoff.yaml`) usando el propio `new-deck.mjs` del renderer, lo corre con sus skills y lee lo que produce. |
| Skills de Hugo (`~/.codex/skills`: business-case-partner, bulletproof-problem-solving-chatgpt, consulting-problem-solving-chatgpt) | Copiadas a `skills/vendor/hugo/` para que el repo sea reproducible; se cargan como core del Framer y dynamic del COS. |
| Skills de alirezarezvani/claude-skills (MIT, commit `19392f7`) | 14 skills (advisors C-level como lentes; pricing, commercial, competitive, market, product, SaaS metrics como dynamic). Solo `SKILL.md` y `references/`; sin scripts. |
| Datos y material del caso Finora | Brief v0.3 y notas → `importers/finora_seed.yaml` (transcripción con procedencia por elemento); fuentes HTML copiadas a `cases/finora/brief/sources/`. |

## Adaptado (refactor, con procedencia)

| Origen | Destino | Qué cambió |
|---|---|---|
| Kit de gráficas SVG del workspace | `web/js/charts/kit.js` | Portado a tema oscuro con paleta validada (dataviz), tooltips, `renderEvidenceTable`. |
| Disciplina de cifras del validador del workspace (`agent/lint.py`) | `caseos/evidence.py` | Mismo principio (ninguna cifra fuera de la evidencia) aplicado al Story Package: cifras en español (COP 92,8 mil, −38%, 4,5×, 1.678) contra las tablas del claim. |
| Hallazgos canónicos e investigaciones del workspace | findings F-xxx + **EvidenceTables** T-xxx | Contrato de tabla §62 (columnas, unidades, definiciones, fuente, query, filtros, periodo, grano, limitaciones, visual preferido). |
| shawnpetros/claude-skills `deep-research` (MIT) | `skills/custom/deep-business-research` + `research._deep` | Profundidad + amplitud + contraargumento en paralelo → peer review → síntesis, orquestado por código (sin vault ni Agent tool). |
| alirezarezvani `chief-of-staff`, `decision-logger`, `context-engine` | `skills/custom/case-chief-of-staff` | Escribían en rutas globales de `~/.claude`; aquí el estado es el caso. Originales en `_reference-only/`, no se cargan. |
| alirezarezvani `executive-mentor` (/em:challenge, /em:stress-test) | `skills/custom/assumption-challenger` | Pre-mortem del framing en modo Challenge. |
| «clarification-protocol» (no existe con ese nombre upstream) | `skills/custom/clarification-protocol` | Escrita para CaseOS: una pregunta a la vez, solo lo que bloquea. |

## Nuevo

Todo `caseos/` (estado, fases y compuertas, linaje, decision log, brain.md, jobs, runtime de agentes, Framer, Research
Hub, puente de Analytics, COS, Story Package, handoff al Storyteller, command layer, búsqueda), la app `web/`, los
contratos `agents/*.md`, 8 skills propias (`adaptive-case-framer`, `case-research-synthesis`, `research-routing`,
`measurement-strategy`, `data-modeling`, `story-package`, `case-chief-of-staff` y las adaptaciones de arriba), el
importador de Finora y las pruebas.

## Deprecado / descartado

- Nada de finora-eda se deprecó: sigue funcionando solo (puerto 8765) y dentro de CaseOS.
- Un adaptador genérico `csv-duckdb` para casos nuevos se planeó y **no** se construyó (evitar sobre-ingeniería antes de
  tener un segundo caso con datos); la interfaz de adaptador está documentada en ARCHITECTURE › Workspaces.
- Scripts, assets y plantillas de las skills de terceros no se copiaron: los agentes de CaseOS no ejecutan scripts de skills.
