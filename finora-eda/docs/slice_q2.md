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

- Terminal: `.venv/bin/python -m agent Q2` (con `--golden` la guarda como investigación dorada), o `.venv/bin/python -m agent W2` para una pregunta del caso (W6 y W7 imprimen qué falta).
- `python -m agent recompose <archivo>` vuelve a componer la narrativa y usa el modelo. `python -m agent revisual <archivo>` solo reasigna las gráficas automáticas, sin modelo.
- Cada corrida queda en `#investigacion/INV-…`; con el servidor, ese enlace la vuelve a abrir.
- Sin servidor: `finora_eda.html` trae embebidas las respuestas verificadas y la investigación dorada. Ahí Enter lleva a la respuesta verificada más cercana, o dice con honestidad que la pregunta necesita el servidor.
- Evaluaciones: `.venv/bin/python -m evals.run_evals` (no llaman al modelo; 82 en total).

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

## Preparar narrativa (iteración del 28-sep-2026)

Sirve para armar la historia mientras exploras. Guardas lo que te sirve de cada respuesta, sección, tarjeta, hallazgo o investigación. Le dices para qué parte de la historia sirve y por qué. Al final, el agente consolida una presentación en láminas web. Todo texto que escribe el agente pasa por un validador en código antes de mostrarse.

| Paso | Qué haces | Qué hace el sistema |
|---|---|---|
| Crear | **✎ Preparar narrativa** en la barra lateral (o `#narrativas`). Pones título, audiencia (CEO, CRO, CFO o Mixta), objetivo y un contexto pegado: un caso, un correo o notas | Guarda la narrativa en `narratives/`, fuera de git |
| Guardar | **＋ Guardar en narrativa** en una respuesta, o **＋ Narrativa** en secciones, tarjetas, drivers y hallazgos (también desde la paleta). Eliges el papel (Situación, Hallazgo, Implicación, Decisión o Acción) y escribes para qué la guardas | Copia el texto validado, las afirmaciones con su estado y sus cifras, la gráfica y la fuente. Cada cifra va con la etiqueta de qué mide |
| Profundizar | **Profundizar** en una pieza, o **Investigar** en un hueco o un pendiente | Lanza una investigación en vivo con la pieza como contexto del hilo: sirve de contexto, no de evidencia. Un aviso arriba te regresa a la narrativa |
| Esqueleto | **Proponer esqueleto** | Propone secciones con su mensaje, preguntas, las piezas que ya sirven, hechos del registro canónico que convendría guardar (**＋ Guardar**) y huecos por investigar. No lleva cifras |
| Unir | **Unir narrativas** | Junta las piezas de varias narrativas sin duplicar una misma fuente y las ordena por papel. Cada nota conserva el título de su narrativa de origen |
| Consolidar | **Consolidar presentación** | Arma láminas con papel, título, mensaje, puntos, la gráfica de una pieza, la evidencia citada y notas del presentador. Lo que no tiene piezas queda como pendiente, con la pregunta que habría que investigar. **Imprimir** la guarda en PDF desde el navegador |

Reglas que se verifican en código (`agent/narrative.py`, funciones `validate_story` y `validate_plan`):

- Toda cifra de una lámina debe estar en la evidencia de las piezas que esa lámina cita: su texto, sus afirmaciones, sus cifras y la etiqueta de qué mide. Las notas del usuario orientan el orden y el énfasis, pero no son evidencia.
- No se admiten cantidades con letras, calificativos sin respaldo, lenguaje causal ni IDs en el texto. "Explica" solo vale si la pieza citada ya lo dice.
- La gráfica de una lámina tiene que venir de una pieza que esa lámina cita.
- Implicación, Decisión y Acción van en condicional, salvo que la lámina cite una decisión o una acción que guardó el usuario.
- Lo que falta no se rellena: queda como pendiente, sin cifras.
- Si el texto no pasa, el reintento corrige la presentación anterior en lugar de reescribirla, hasta 3 intentos. Si ninguno pasa, se muestran las piezas tal cual y la presentación queda marcada como degradada.
- Cada una de las 117 cifras del registro canónico lleva su etiqueta de qué mide (`FACT_LABELS` en el pipeline). Si falta alguna, el pipeline se detiene. El compositor recibe cada cifra con su etiqueta, para que no llame "revertido" a un total.

Pruebas del 28-sep-2026 con la narrativa "Caso CFO · qué mide hoy el MRR": 8 piezas y el caso del CFO pegado como contexto.

| Corrida | Intentos | Costo equivalente | Resultado |
|---|---|---|---|
| Esqueleto | 1 (63 s) | US$0,21 | 7 secciones, aprobado al primer intento |
| Presentación 1 | 2 | ≈US$0,22 por intento | Degradada por "cientos", "dos" y "explica". Se endureció el prompt y el reintento pasó a corregir la versión anterior |
| Presentación 2 | 2 | ≈US$0,22 por intento | Validada, pero una lámina llamó "monto revertido" al movimiento bruto total. Por eso se etiquetaron las cifras del registro |
| Presentación 3 | 2 (104 s) | US$0,48 | Validada: 8 láminas y 4 pendientes. El primer intento se rechazó por un "3 meses" que solo aparecía en la etiqueta; ahora la etiqueta cuenta como evidencia |

## Preguntas del caso (iteración del 28-sep-2026)

La cola de investigación del caso sale del workplan W0–W7 del brief de trabajo v0.3 (Alegra · Investigación y workplan, sección 08), que es la fuente de verdad. Vive en `brain/business/case_questions.yaml` y se abre con **Preguntas del caso** en la barra lateral, con `#caso` o desde la paleta. El buscador libre (⌘K y Enter) sigue igual como modo de exploración adicional. No cambió la lógica analítica: el mismo agente, las mismas tools y el mismo validador de afirmaciones.

| Pregunta | Prioridad | Hipótesis | Capacidad con los datos actuales |
|---|---|---|---|
| W0 · ¿Qué podemos nombrar y comparar válidamente? | P0 · puerta | HG | Respondible (condicionada) |
| W1 · ¿El monto identifica los escenarios del CFO? | P1 · conceptual | HIF | Respondible (prueba lógica) |
| W2 · ¿Qué cambió en los primeros pagadores observados? | P1 · evidencia acotada | HO1 | Parcial |
| W3 · ¿Dónde se concentra el cambio del monto observado? | P1 · evidencia acotada | HO3 | Parcial |
| W4 · ¿La industria concentra el cambio observado? | P2 · condicionada | HO2 | Parcial, si W2 o W3 muestran un cambio material |
| W5 · ¿Cambió la economía posterior de los nuevos pagadores? | P2 · condicionada | HO4 | Parcial, si el aporte posterior cambia la lectura |
| W6 · ¿Qué evidencia mínima distinguiría las explicaciones del CRO? | Brecha crítica | HC1–HC3 | Bloqueada |
| W7 · ¿Qué distinguiría los componentes del valor y la pertenencia recurrente? | Brecha crítica | HF1–HF3 | Bloqueada |

Cada tarjeta muestra el ID, la prioridad, la pregunta, la hipótesis asociada, por qué importa, la capacidad de respuesta (impacto × capacidad, como en el brief), el estado, la evidencia faltante cuando aplica, de qué depende y el CTA. En el detalle están el método, el entregable, el criterio de cierre, los límites del brief, los sustitutos inválidos y los hechos ya verificados que el agente reutilizará.

Estados:

- **Bloqueada**: la capacidad es cero (W6 y W7). No se investiga: el servidor rechaza la corrida con 409 y la interfaz no la ofrece. **Investigar: ver qué falta** abre una respuesta determinista, sin corrida del agente y sin datos de pagos. Explica, por cada explicación del CRO o del CFO, qué comparación la distinguiría, la evidencia mínima, los datos que faltan (con sus campos del catálogo), la fuente potencial, qué conclusión queda bloqueada y cuál sería el sustituto inválido.
- **Pendiente**: se puede investigar y todavía no tiene respuesta. Si depende de otra pregunta sin respuesta, la tarjeta lo dice, pero no lo impide.
- **Investigando**: hay una corrida en curso. **Ver la investigación en vivo** se vuelve a enganchar al stream.
- **Respondida**: hay una respuesta publicada en `investigations/caso/<W>.json`, que el pipeline embebe en el HTML.

Al investigar W0–W5, el agente recibe la pregunta del caso como contexto (no como evidencia): la hipótesis y lo que la distingue, el alcance permitido, el método y el criterio de cierre del brief, lo que no se puede concluir, los sustitutos inválidos y los hechos canónicos relacionados. Registra la hipótesis del caso y su rival antes de mirar datos. Al cerrar, el compositor del caso (`agent/prompts/caso.md`) entrega siete partes obligatorias:

1. Respuesta: titular y texto, con sus afirmaciones.
2. Hechos observados: solo afirmaciones con estado Hecho observado o Evidencia fuerte, con el texto que validó el código.
3. Interpretación permitida, dentro del alcance de la pregunta.
4. Qué no podemos concluir: límites de la corrida más los del brief.
5. Hipótesis fortalecidas o debilitadas: el efecto lo deriva el código del estado de cada hipótesis (Soportada → fortalecida, No soportada → debilitada, Direccional → señal direccional).
6. Preguntas que siguen abiertas.
7. Siguiente pregunta recomendada: un ID de la cola o una pregunta propia.

Reglas que se verifican en código (`agent/caso.py`, `validate_case_answer`):

- Cada cifra debe estar en las afirmaciones que cita ese bloque. Tampoco se admiten cantidades con letras, calificativos sin respaldo, lenguaje causal ni IDs de afirmaciones o evidencia en el texto.
- Sustitutos inválidos por pregunta: por ejemplo, conversión o leads en W2, descuento o etiquetas contractuales en W3. No pueden aparecer en la respuesta, en la interpretación, en la lectura de las hipótesis ni en los hechos citados; solo en lo que no podemos concluir.
- Cada lectura de hipótesis cita afirmaciones ligadas a esa hipótesis. La siguiente pregunta tiene que ser otra de la cola.
- Si la respuesta no pasa, el reintento corrige la anterior, hasta 3 intentos. Si ninguno pasa, queda una respuesta sin texto libre: afirmaciones validadas, el alcance del brief y el orden del brief. Se marca como compuesta sin texto libre.

Cada respuesta se guarda como pieza en Preparar narrativa con **＋ Guardar en narrativa** (tipo `respuesta_caso`); las bloqueadas también. Esta iteración no genera deck ni narrativa final.

Pruebas (sin modelo): 21 evaluaciones nuevas. Incluyen una respuesta de muestra sobre las afirmaciones reales de la dorada, cada rechazo del validador, el efecto derivado de las hipótesis, el respaldo, las bloqueadas y un flujo completo con el agente y el compositor simulados. No se corrió ninguna pregunta W con el modelo; una corrida en vivo toma entre 5 y 18 minutos y cuesta alrededor de US$1,3 a 1,8 de equivalente en API.

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
| Narrativas | `agent/narrative.py`, `agent/prompts/narrador_plan.md`, `agent/prompts/narrador.md` | Guarda narrativas y piezas, las une, propone el esqueleto y consolida la presentación. Valida cada lámina contra la evidencia que cita y, si no pasa, cae en una presentación hecha solo con las piezas. |
| Preguntas del caso | `brain/business/case_questions.yaml`, `agent/caso.py`, `agent/prompts/caso.md` | Cola W0–W7 del brief v0.3: contexto para el investigador, compositor de siete partes con su validador, respaldo sin texto libre y respuestas deterministas de las bloqueadas. |
| Servidor | `app/server.py` | Sirve el workspace y la API: `POST /api/investigations` (acepta W0–W5 y rechaza las bloqueadas), streaming por SSE, `GET` del documento y de la dorada, `/api/caso` (estado de la cola y respuesta de cada pregunta) y `/api/narratives` (crear, editar, piezas, unir, esqueleto, consolidar). Solo 127.0.0.1. |
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
- Las preguntas del caso W0–W5 solo se investigan con el servidor local. Sin él, la cola muestra las bloqueadas y las respuestas ya publicadas. El servidor corre una investigación a la vez: si hay una en curso, Investigar espera.
- Los sustitutos inválidos se detectan por términos. Un sustituto dicho con otras palabras pasaría: eso le toca a la pasada crítica.
- Preparar narrativa solo aparece con el servidor local: el HTML estático no guarda ni consolida. Profundizar desde una pieza es una investigación en vivo completa y tarda lo mismo (de 5 a 18 minutos). Proponer el esqueleto toma alrededor de un minuto y consolidar, de uno a tres.
- El validador de láminas comprueba que cada cifra salga de una pieza citada, no que se use con el sentido correcto. La etiqueta de qué mide reduce ese riesgo, pero no lo elimina: eso le toca a la pasada crítica.
