# Arquitectura

Un **monolito modular**: un proceso Python (FastAPI) que sirve la app, la API, los eventos en vivo (SSE), corre el
trabajo de los agentes como jobs en segundo plano y monta en el mismo proceso el Business Exploration Workspace existente.
El estado del caso son **archivos** legibles y versionados; no hay base de datos.

```
                ┌──────────────────────────── navegador (web/, ES modules) ────────────────────────────┐
                │ Home · Briefing · Framing · Research · Chief of Staff · Story · Slides · Agents ·     │
                │ Artifacts · ⌘K · Under the hood · Demo              ▲ SSE (/events)                   │
                └───────────────┬──────────────────────────────────────┼──────────────────────────────┘
                                │ REST /api                            │
┌───────────────────────────────▼──────────────────────────────────────┴──────────────────────────────┐
│ caseos.server (FastAPI, 127.0.0.1)                                                                   │
│                                                                                                      │
│  human gates ─ phases.py (Mark Ready / Reopen + impact radius)    decisions.py (decision log)        │
│  case state ── store.py (1 YAML por entidad, versiones, activity.jsonl) · lineage.py · brain.py       │
│  agentes ───── agents/framer.py · research.py · analytics.py · cos.py · story.py · storyteller.py    │
│                 └─ jobs.py (cola persistente, retry, recuperación al reiniciar) → bus.py (SSE)        │
│  runtime ───── llm.py: Claude Agent SDK (suscripción) · RunSpec → salida JSON validada por schema    │
│  skills ────── skills.py + skills/manifest.yaml (core · dynamic · challenge · lens · linked)          │
│  guardas ───── framer.guard · language.py · evidence.py (tablas + cifras) · research.verify_citations │
│                story.validate_package · storyteller._guard                                           │
│                                                                                                      │
│  /ws/finora ── finora-eda montado en proceso (su UI y su API, sin modificar)                         │
└──────────────────────────────┬──────────────────────────────────────────┬───────────────────────────┘
                               │                                          │
                  cases/<id>/ (archivos)              ~/.claude/skills  (Executive Visual Storyteller,
                                                       enlazado por symlink, nunca copiado)
```

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `config.py` | rutas, modelo (`claude-opus-5`), effort y tope de costo por rol, host/puerto |
| `model.py` | fases, tipos de entidad y prefijos de ID (Q H N R F T D X C S A), tipos epistémicos |
| `store.py` | `CaseStore`: crear/actualizar entidades con versión, escritura atómica, caché por mtime, traza, snapshots |
| `lineage.py` | grafo de linaje (links no dirigidos), linaje por tipo, *downstream* e **impact radius** |
| `phases.py` | estado de fases, `readiness` (bloqueos y avisos por fase), `mark_ready` (solo Hugo), `reopen` |
| `decisions.py` | decision log (§55): activas si decide Hugo, propuestas si las sugiere un agente; `do_not_resurface` |
| `brain.py` | `brain.md`: memoria viva del caso, se regenera en cada cambio material |
| `briefing.py`, `framing_doc.py` | brief y framing vivo (`framing/current.yaml` → `current.md`) |
| `agents/` | `base.py` (contratos desde `agents/*.md`, kernel del sistema), `framer.py` |
| `research.py` | Router, especialistas, L3 (profundidad + amplitud + contraargumento + peer review), aceptar/cuestionar |
| `analytics.py` | puente con el workspace: corridas, promover claims a findings, **EvidenceTable** con linaje |
| `cos.py` | sala de control, impacto (linaje + evaluación del COS), alertas con opciones, siguientes acciones |
| `story.py` | Story Package (§61), validación, versiones, claims con IDs estables |
| `storyteller.py` | handoff al Visual Storyteller existente, corrida con skills enlazadas, importación del deck |
| `commands.py`, `actions.py`, `search.py` | command layer (§68), acciones por entidad (§69), búsqueda ⌘K |
| `jobs.py`, `bus.py` | trabajos en segundo plano y eventos en vivo |
| `language.py` | disciplina de vocabulario («el vocabulario aclara, no actúa») |
| `workspaces/` | adaptadores de workspace analítico |

## Estado del caso

Cada entidad es un YAML con `id`, `type`, `version`, `links`, `review.state` (proposed · accepted · rejected),
`origin` (actor, fuente) y, si aplica, `stale` (needs_review con razón). Actualizar guarda la versión anterior en
`audit/versions/<ID>/v<n>.yaml`. Toda acción deja una línea en `audit/activity.jsonl` y un evento SSE.

**Linaje.** `Pregunta → Hipótesis → Research → Evidencia (finding/tabla) → Decisión → Claim → Slide`. Los links se
guardan como referencias salientes y el grafo se lee no dirigido. `impact_radius(fase)` = lo que vive después de esa fase
y está conectado a lo que vive en ella: es lo que se marca needs_review al reabrir. Nada se borra.

**Fases y compuertas.** `not_started → in_progress → review → ready`, más `reopened` y `needs_review`.
`mark_ready` exige `actor == "hugo"` y sin bloqueos; hace snapshot del caso, escribe el artefacto aprobado versionado
(`*/approved/*.vN.*`), registra la decisión, actualiza `brain.md`, sella la hora y desbloquea la siguiente fase.
`reopen` exige razón, muestra antes el impacto y marca needs_review lo afectado.

## Agentes y runtime

Cada corrida es un `RunSpec` → `llm.AgentSDKLLM.run`:

- `claude-agent-sdk` con `setting_sources=[]`, `strict_mcp_config=True`, herramientas explícitas (`[]` para Framer y COS;
  `WebSearch`/`WebFetch` para research) y `output_format` = JSON Schema: la salida se valida antes de tocar el estado.
- El system prompt = kernel de CaseOS + sección *System behavior* de `agents/<id>.md` + skills seleccionadas. Se guarda
  por hash en `audit/prompts/`; la corrida (prompt, skills con hash, herramientas usadas, URLs vistas, uso, costo
  equivalente, duración) en `audit/runs/`.
- Autenticación: suscripción (sesión de Claude Code); se detecta y se muestra en cada corrida.
- `FakeLLM` sustituye al runtime en las pruebas.

**Jobs.** La solicitud se escribe a disco antes de correr. Estados: queued · running · succeeded · failed · interrupted.
Un reinicio marca como interrumpido lo que estaba en curso (y los turnos del Framer como reintentables); nada se pierde.
Los endpoints síncronos corren en hilos: `jobs._spawn` agenda en el loop del servidor con `call_soon_threadsafe`.

## Handoffs (contratos)

| De → a | Contrato | Validación en código |
|---|---|---|
| Framer → caso | `FramerTurn` (items epistémicos + patch del framing + perfil de lenguaje) | `framer.guard`, `language.assess` |
| Research → COS | resultado `case-research-synthesis` (§40) + fuentes | `research.verify_citations` (URLs recuperadas) |
| Analytics → COS | **EvidenceTable** (§62: table_id, columnas, filas, unidades, definiciones, fuente, query, filtros, periodo, grano, limitaciones, visual preferido) | `evidence.validate_table` |
| COS → Story | Story Package (§61) | `story.validate_package`: evidencia aceptada, cifras en tablas, dependencias needs_review, lenguaje causal |
| Story → Storyteller | carpeta del deck: `storyline.md`, `data/*.yaml`, `caseos-handoff.yaml` | Story Ready + paquete válido; `storyteller._guard` limita escrituras al deck |

## Workspaces

Un workspace analítico es un módulo con `adapter(cfg)` que expone: `available`, `info()`, `canonical()`,
`canonical_table(h, table_key)`, `run(id)`, `runs()`, `claim_table(run, claim, table_key)`, `new_investigation(q)`,
`run_investigation(inv, on_event)`, `mount(app)`. `finora_eda.py` lo implementa sobre el workspace existente leyendo sus
archivos y corriendo su investigador en proceso (sin tocar su código). El caso lo declara en `case.yaml › workspace`.

## Visual Storyteller

No se reconstruyó. `storyteller.ensure_links()` crea symlinks de las 5 skills y 2 agentes de `~/.claude` en
`caseos/.claude/`; la corrida usa el SDK con `setting_sources=["project"]` para que Claude Code las descubra, un
`AgentDefinition` para el crítico independiente, y `can_use_tool` que confina escrituras a la carpeta del deck y Bash a
los scripts del renderer. `prepare()` crea el deck con el propio `new-deck.mjs` del renderer y escribe el handoff;
`import_deck()` registra slides (S-xxx) con su `claim_id` para cerrar el linaje.

## Front end

HTML + ES modules sin build (`web/js`), `h()` hyperscript, un router por hash y SSE para el estado en vivo. Kit de
gráficas SVG portado del workspace (línea, barras, cascada, dispersión, puntos) con paleta validada para fondo oscuro.
Fuentes locales (Inter, Newsreader, IBM Plex Mono; OFL). Los estáticos se sirven bajo una ruta versionada por arranque.

## Seguridad

Solo `127.0.0.1`. Sin secretos en el repo. Las rutas de archivos pasan por una guarda de ruta del caso. Los agentes de
Framer y COS no tienen herramientas; los de research solo búsqueda web; el Storyteller escribe solo en su carpeta.
