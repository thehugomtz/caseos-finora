# Vertical slice agentic · pregunta 2

> ¿Por qué disminuyó el MRR por cliente?

La primera rebanada de punta a punta de la arquitectura v1.2 (§12): **cerebro → capa SQL → agente → validador → compositor → vista → linaje**, para una sola pregunta dorada. No agrega features a la arquitectura congelada; implementa una parte de ella.

## Cómo probarlo en local

Requisitos: el entorno virtual del proyecto y una sesión de Claude Code iniciada con tu cuenta (tu suscripción). No hace falta API key.

```bash
uv venv --system-site-packages --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements-agent.txt
.venv/bin/python -m uvicorn app.server:app --host 127.0.0.1 --port 8765
```

Abre `http://127.0.0.1:8765`, pulsa ⌘K, elige la pregunta 2 y usa **Ver investigación** (la dorada, pre-generada) o **Investigar en vivo** (corre el agente ahora; tarda unos cinco minutos).

Otras formas:

- Terminal: `.venv/bin/python -m agent Q2` (con `--golden` la guarda como investigación dorada).
- Sin servidor: `finora_eda.html` trae embebida la investigación dorada y la abre sin red.
- Evaluaciones: `.venv/bin/python -m evals.run_evals` (no llaman al modelo).

## Qué hace cada pieza

| Pieza | Archivo | Qué hace |
|---|---|---|
| Capa SQL | `agent/warehouse.py` | Construye el mart en DuckDB desde las salidas de la Fase 1 y verifica paridad exacta (19 pruebas). Conexión del agente de solo lectura y sin acceso a archivos. |
| Capa semántica | `agent/semantic.py` | `query_metric`: compila métricas del catálogo a SQL; aplica la ventana limpia, marca comparaciones no comparables y adjunta precauciones. |
| Análisis | `agent/analytics.py` | Catálogo cerrado: `mix_within_decomposition` (funciones exactas de la Fase 1), `vintage_arpa`, `ticket_distribution` y el nuevo `churn_selection`. |
| Evidencia | `agent/evidence.py` | Registro inmutable: parámetros, consulta, resultado, hash y versiones de datos y cerebro. Lo escriben las tools, nunca el agente. |
| Validador | `agent/validator.py` | Cifras solo ligadas a evidencia; rechaza cifras a mano o con letras, calificativos sin cifra y lenguaje causal; confirma o degrada estados; deriva el estado de cada hipótesis. |
| Tools | `agent/tools.py` | 8 tools como servidor MCP en proceso: `brain_lookup`, `search_evidence`, `query_metric`, `run_sql`, `run_analysis`, `upsert_hypotheses`, `propose_claim`, `propose_visual`. |
| Visuales | `agent/visuals.py` | Gramática visual determinista: intención → forma; el título es el texto validado. |
| Agente y compositor | `agent/orchestrator.py`, `agent/prompts/` | Un agente investigador con salida estructurada; un compositor sin tools cuya narrativa pasa por el validador (un reintento; si no, composición sin texto libre). |
| Servidor | `app/server.py` | Sirve el workspace y la API: `POST /api/investigations`, streaming por SSE, `GET` del documento y de la dorada. Solo 127.0.0.1. |
| Vista | `templates/finora_eda_app.js` | Documento de investigación con los componentes de la Fase 1, modo en vivo y panel de linaje (Evidencia · Método · Consulta · Fuente). |
| Cerebro | `brain/frameworks/playbooks/arpa_decline.yaml`, `brain/guardrails/*` | Playbook MECE anclado en la identidad del MRR por cliente, reglas epistémicas, datos faltantes y léxico causal. |

## Garantías que se verifican en código

- Las hipótesis y sus firmas se registran antes de la primera evidencia; después no se pueden cambiar.
- Ninguna tool de análisis corre sin árbol pre-registrado; hay un presupuesto de 15 análisis.
- Toda cifra visible es una variable ligada a una evidencia; las evaluaciones recalculan el 100% desde la evidencia guardada.
- Los estados los confirma el código (asociaciones y SQL ad hoc con techo Direccional; Evidencia fuerte exige dos variantes y nada en contra).
- La narrativa solo puede usar cifras y calificativos que ya están en las afirmaciones que cita.
- El registro de análisis muestra todo lo ejecutado, lo descartado y lo que el validador rechazó.

## Desviaciones respecto de la arquitectura v1.2

| v1.2 dice | La slice hace | Por qué |
|---|---|---|
| Claude API con el Tool Runner del SDK y API key (§3.5) | Claude Agent SDK sobre la sesión local de Claude Code | Decisión del 27-sep-2026: probar en local con la suscripción de Claude. Si `ANTHROPIC_API_KEY` está definida, el mismo código la usa. |
| PostgreSQL con esquema `app` (§9) | DuckDB para el mart; investigaciones en JSON | Plan B previsto en §9, elegido al congelar la arquitectura. |
| 10 tools (§4) | 8 tools | `propose_metric` y `run_scenario` no los necesita la pregunta 2. |
| Pasada crítica (SHOULD) | No incluida | Es SHOULD en §12. Hoy una lista de calificativos cubre los casos frecuentes; la verificación semántica fina le toca a esa pasada. |
| Lente de audiencia (SHOULD) | Fija: Finanzas | SHOULD en §12. |

## Aislamiento del agente

El agente corre sin las herramientas integradas de Claude Code (`tools=[]`), sin tus ajustes ni tu CLAUDE.md (`setting_sources=[]`) y sin tus conectores de claude.ai (`strict_mcp_config=True`). Solo ve las 8 tools de Finora y la salida estructurada. La base es de solo lectura y no puede leer archivos.

## Uso y costo

Con la suscripción no se cobra por token: el consumo sale de los límites de tu plan, igual que Claude Code. Cada investigación reporta el costo equivalente que tendría en la API. Distribuir un producto con login de claude.ai a terceros no está permitido; para otras personas se usa API key.

Corridas del 27-sep-2026 (las tres con la suscripción, `apiKeySource: none`):

| Corrida | Cómo | Duración | Turnos del agente | Costo equivalente | Resultado |
|---|---|---|---|---|---|
| 1 | Terminal | 285 s | 34 | US$1,34 | Publicada; destapó dos huecos del validador (calificativos y cifras con letras) |
| 2 | Botón "Investigar en vivo" | 297 s | 31 | US$1,41 | Publicada; el compositor corrigió su narrativa al segundo intento |
| 3 | Terminal con `--golden` | 663 s | 27 | US$1,13 | Dorada actual; pasa las 42 evaluaciones |

La duración varía: en la corrida 3 el segundo intento del compositor esperó 460 s por latencia del servicio para generar la misma cantidad de texto que el primero, que tardó 57 s.

## Límites conocidos

- La verificación semántica fina queda pendiente. El validador rechaza una lista de calificativos sin cifra ("casi todos", "la mayoría", "en cada trimestre"), pero no entiende el sentido; la dorada todavía dice que el MRR por cliente "desciende de forma sostenida". Eso le toca a la pasada crítica (SHOULD en §12).
- Solo la pregunta 2 corre en vivo (un playbook). Las demás preguntas doradas abren la paleta con sus secciones, como en la Fase 1.
- El servidor corre una investigación a la vez y guarda cada corrida en `investigations/runs/` (fuera de git).
