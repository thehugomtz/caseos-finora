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

Abre `http://127.0.0.1:8765` y pulsa ⌘K. Elige una pregunta frecuente para ver su respuesta, o escribe la tuya y pulsa **Enter**: el agente la investiga en vivo (entre 3 y 10 minutos). En la pregunta 2, **Ver investigación completa** abre la dorada, que ya viene pre-generada.

Otras formas:

- Terminal: `.venv/bin/python -m agent Q2` (con `--golden` la guarda como investigación dorada).
- `python -m agent recompose <archivo>` vuelve a componer la narrativa y usa el modelo. `python -m agent revisual <archivo>` solo reasigna las gráficas automáticas, sin modelo.
- Cada corrida queda en `#investigacion/INV-…`; con el servidor, ese enlace la vuelve a abrir.
- Sin servidor: `finora_eda.html` trae embebidas las respuestas verificadas y la investigación dorada. Ahí Enter lleva a la respuesta verificada más cercana, o dice con honestidad que la pregunta necesita el servidor.
- Evaluaciones: `.venv/bin/python -m evals.run_evals` (no llaman al modelo).

## Respuesta primero (iteración de UX del 27-sep-2026)

El workspace responde antes de mostrar evidencia. La investigación se abre solo cuando se pide. No cambió la lógica analítica: las respuestas se redactan desde las afirmaciones ya verificadas y pasan por el mismo lint que el agente.

| Qué ve el usuario | De dónde sale |
|---|---|
| **Lo esencial en 30 segundos** (portada): qué pasa, por qué creemos que pasa, qué no sabemos y dónde profundizar | `brain/business/answers.yaml` → `esencial` |
| **Respuesta** debajo del título de cada sección, con nivel de evidencia y una **lectura** bajo la gráfica que la prueba | `answers.yaml` → `secciones` |
| **Buscador**: 6 preguntas frecuentes por dominio; "Explorar por sección" queda en segundo plano. Con texto, sugiere respuestas verificadas cercanas y Enter pregunta | `stakeholder_questions.yaml` (`destacada`) y `palabras_clave` |
| **Vista de respuesta** (Q1–Q8): respuesta, nivel de evidencia, gráfica con titular declarativo y lectura, qué sabemos, qué no, qué necesitaríamos y los hallazgos que la soportan | `answers.yaml` → `preguntas` |
| **Pregunta libre + Enter**: con servidor, "Analizando tu pregunta…" con las etapas reales del agente y, mientras tanto, la respuesta verificada más cercana. Sin servidor, esa respuesta o un aviso honesto | `app/server.py` (texto libre), playbook `libre` |
| **Investigación**: pregunta, respuesta ejecutiva con titular, 2–4 drivers, visual principal y lo que no sabemos. "Ver cómo llegamos" despliega hipótesis, criterios, evidencia, límites y registro | `agent/orchestrator.py` (titulares), `finora_eda_app.js` |

Reglas que se verifican:

- El pipeline valida cada respuesta: que existan los facts, las afirmaciones, los datos faltantes, las gráficas y las tarjetas citadas, y le aplica el lint de `agent/lint.py` (sin cifras a mano ni con letras, sin calificativos, sin lenguaje causal; "explica" solo con descomposición).
- Toda conclusión trae su gráfica. La gramática visual asigna una a cada hallazgo que no la tenga. Lo No evaluable se muestra como una tabla de datos disponibles contra faltantes. La evidencia canónica de la Fase 1 reutiliza la gráfica de su tarjeta del workspace; así H1.1 (mix, No soportada) muestra la cascada de la tarjeta 7.1.
- Las evaluaciones exigen titular en la respuesta y en cada hallazgo, una gráfica por hallazgo y formas válidas (45 en total).
- Una pregunta que no se puede contestar con estos datos también tiene respuesta: lo que sí sabemos, lo que no y los campos que harían falta (playbook `libre`, nodo `datos_faltantes`).

## Qué hace cada pieza

| Pieza | Archivo | Qué hace |
|---|---|---|
| Capa SQL | `agent/warehouse.py` | Construye el mart en DuckDB desde las salidas de la Fase 1 y verifica paridad exacta (19 pruebas). Conexión del agente de solo lectura y sin acceso a archivos. |
| Capa semántica | `agent/semantic.py` | `query_metric`: compila métricas del catálogo a SQL; aplica la ventana limpia, marca comparaciones no comparables y adjunta precauciones. |
| Análisis | `agent/analytics.py` | Catálogo cerrado: `mix_within_decomposition` (funciones exactas de la Fase 1), `vintage_arpa`, `ticket_distribution` y el nuevo `churn_selection`. |
| Evidencia | `agent/evidence.py` | Registro inmutable: parámetros, consulta, resultado, hash y versiones de datos y cerebro. Lo escriben las tools, nunca el agente. |
| Validador | `agent/validator.py` | Cifras solo ligadas a evidencia; rechaza cifras a mano o con letras, calificativos sin cifra y lenguaje causal; confirma o degrada estados; deriva el estado de cada hipótesis. |
| Tools | `agent/tools.py` | 8 tools como servidor MCP en proceso: `brain_lookup`, `search_evidence`, `query_metric`, `run_sql`, `run_analysis`, `upsert_hypotheses`, `propose_claim`, `propose_visual`. |
| Visuales | `agent/visuals.py` | Gramática visual determinista: intención → forma; el título es el texto validado. Incluye la tabla de datos faltantes y la reutilización de gráficas de tarjetas de la Fase 1. |
| Agente y compositor | `agent/orchestrator.py`, `agent/prompts/` | Un agente investigador con salida estructurada; un compositor sin tools cuya narrativa pasa por el validador (un reintento; si no, composición sin texto libre). |
| Servidor | `app/server.py` | Sirve el workspace y la API: `POST /api/investigations`, streaming por SSE, `GET` del documento y de la dorada. Solo 127.0.0.1. |
| Vista | `templates/finora_eda_app.js` | Respuesta primero (portada, secciones, vista de respuesta), buscador con preguntas libres, documento de investigación con revelación progresiva, modo en vivo y panel de linaje (Evidencia · Método · Consulta · Fuente). |
| Cerebro | `brain/frameworks/playbooks/arpa_decline.yaml`, `brain/guardrails/*` | Playbook MECE anclado en la identidad del MRR por cliente, reglas epistémicas, datos faltantes y léxico causal. |

## Garantías que se verifican en código

- Las hipótesis y sus firmas se registran antes de la primera evidencia; después no se pueden cambiar.
- Ninguna tool de análisis corre sin árbol pre-registrado; hay un presupuesto de 15 análisis.
- Toda cifra visible es una variable ligada a una evidencia; las evaluaciones recalculan el 100% desde la evidencia guardada.
- Los estados los confirma el código (asociaciones y SQL ad hoc con techo Direccional; Evidencia fuerte exige dos variantes y nada en contra).
- La narrativa solo puede usar cifras y calificativos que ya están en las afirmaciones que cita.
- Una participación (`pct`) mayor a 100% solo se acepta en una descomposición (p. ej. "108% del cambio"). Fuera de ella casi siempre es una columna que ya venía en puntos porcentuales.
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

Corridas del 27-sep-2026 (todas con la suscripción, `apiKeySource: none`):

| Corrida | Cómo | Duración | Turnos del agente | Costo equivalente | Resultado |
|---|---|---|---|---|---|
| 1 | Terminal | 285 s | 34 | US$1,34 | Publicada; destapó dos huecos del validador (calificativos y cifras con letras) |
| 2 | Botón "Investigar en vivo" | 297 s | 31 | US$1,41 | Publicada; el compositor corrigió su narrativa al segundo intento |
| 3 | Terminal con `--golden` | 663 s | 27 | US$1,13 | Dorada actual (hipótesis, evidencia y afirmaciones) |
| 4 | `python -m agent recompose` sobre la dorada | 100 s | – | – | El validador rechazó las dos composiciones (calificativos y un "dos" escrito con letras); quedó la composición degradada. Se agregaron esas reglas al prompt del compositor |
| 5 | `python -m agent recompose` sobre la dorada | 71 s | 3 | US$0,27 | Narrativa vigente, con titulares; aprobada al primer intento |
| 6 | Enter en el buscador con la pregunta del CFO (texto libre, playbook `libre`) | 1.085 s | 39 + 2 | US$1,78 | Publicada. Respuesta principal No evaluable ("No se puede separar descuento de contracción; el deterioro coincide con la entrada"), con lo que sí sabemos y los campos que faltan. Hallazgo nuevo: las contracciones casi no se revierten al mes siguiente y las expansiones sí. Destapó un hueco: se aceptó una participación de 400% porque la columna SQL ya venía en puntos porcentuales; la narrativa no la citó y ahora hay una regla que la rechaza |

La duración varía: en la corrida 3 el segundo intento del compositor esperó 460 s por latencia del servicio para generar la misma cantidad de texto que el primero, que tardó 57 s.

## Límites conocidos

- La verificación semántica fina queda pendiente. El validador rechaza una lista de calificativos sin cifra ("casi todos", "la mayoría", "en cada trimestre"), pero no entiende el sentido; la dorada todavía dice que el MRR por cliente "desciende de forma sostenida". Eso le toca a la pasada crítica (SHOULD en §12).
- La pregunta 2 tiene playbook propio (`arpa_decline`). Las preguntas libres usan `libre`, más general: el árbol lo arma el agente sobre la identidad del MRR.
- Las respuestas de Q1 y Q3–Q8 se redactaron desde la evidencia de la Fase 1, sin correr el agente. Para investigarlas en vivo está **Investigar en vivo** (o **Investigar más →** cuando no son evaluables).
- El servidor corre una investigación a la vez y guarda cada corrida en `investigations/runs/` (fuera de git).
- El validador comprueba de dónde sale cada cifra y rechaza participaciones imposibles, pero no entiende unidades en general. Un 1% leído como fracción (100%) todavía pasaría; eso le toca a la pasada crítica.
- La gramática visual no sabe comparar años desde un SQL ad hoc con más de tres filas por corte, y el agente cae en una tabla (H2 de la corrida 6).
- Una pregunta libre amplia tarda más que la dorada: la corrida 6 tomó 18 minutos, 17 de ellos del investigador.
