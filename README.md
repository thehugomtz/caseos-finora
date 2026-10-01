# Finora · el caso resuelto con IA, de punta a punta

Este repo es la entrega de Víctor Hugo Martínez Medina para el reto técnico de Alegra, «Business Analytics: del dato a la
decisión». Trae las herramientas con las que resolví el caso y el caso tal como quedó, con todo su rastro: qué
hicieron los agentes, qué decidí yo y cuánto costó cada corrida.

## 1. Empieza por los videos

> Reprodúcelos a **1.2x**: en Loom, el botón de velocidad está abajo a la derecha del reproductor.

| Video | Qué cuenta | Duración (a 1.2x) |
|---|---|---|
| [**Short version** · Análisis del business case de Finora](https://www.loom.com/share/9b7a35b392b1432d904552439e77efd7) | El caso, la respuesta y la propuesta, en corto | 7:34 (≈6:20) |
| [**Long version** · Análisis del business case de Finora](https://www.loom.com/share/a4edcbfda2a74ca6b2679fba1930645e) | El caso completo, lámina por lámina | 11:29 (≈9:35) |
| [**Cómo usé IA con agentes**](https://www.loom.com/share/428f418cf8e2455897d56fb0a5bafa2c) | El proceso: las herramientas, los agentes, mis decisiones y cómo lo verifiqué | 6:15 (≈5:15) |

## 2. Qué hay aquí

| | Qué es | Dónde |
|---|---|---|
| **CaseOS** | Un case room con agentes y compuertas humanas: Brief → Framing & Shaping → Research → Chief of Staff → Story → Slides. Los agentes hacen el trabajo y yo apruebo cada paso. | [`caseos/`](caseos/) |
| **Business Exploration Workspace** | La herramienta de EDA. Un pipeline reproducible sobre los CSV de Finora y un agente que investiga preguntas con SQL, revisado por un validador. | [`finora-eda/`](finora-eda/) |
| **Executive Visual Storyteller** | Mis skills para hacer decks ejecutivos en HTML. CaseOS las usa para armar el deck. | [`claude/`](claude/) |
| **El caso Finora** | El caso completo, con bitácora, corridas, decisiones, evidencia y deck. | [`caseos/cases/finora/`](caseos/cases/finora/) |

## 3. Pruébalo: elige cómo

### A · Con tu asistente de IA (lo más fácil)

Abre tu asistente de código y pégale esto:

> Clona https://github.com/thehugomtz/caseos-finora y ayúdame a probar la herramienta del candidato.

Si ya tienes la carpeta, porque la clonaste o la bajaste de Drive y la descomprimiste, ábrela en tu asistente y dile:

> El candidato pasó este repo. ¿Cómo pruebo su herramienta?

| Asistente | Qué lee | Notas |
|---|---|---|
| **Claude Code** (terminal, app de escritorio o IDE) | [CLAUDE.md](CLAUDE.md) | Te pregunta qué quieres hacer y con qué modelo, instala y abre CaseOS. |
| **Codex**, **Cursor**, **Gemini CLI** u otro agente de código | [AGENTS.md](AGENTS.md) | Lo instala y lo abre igual. Los agentes de CaseOS corren con Claude, así que para lanzarlos necesitas una sesión de Claude Code o una `ANTHROPIC_API_KEY`. |
| **Un chat sin terminal** (por ejemplo, subir la carpeta a claude.ai) | README y docs | No puede correr el servidor, pero puede leerte el caso, el deck y la evidencia. Para verlo funcionando, usa la opción B o C. |

Antes de lanzar agentes, el asistente te pregunta el modelo. Para este ejercicio usé **Claude Opus 5.5**
(`claude-opus-5-5`) con esfuerzo máximo.

### B · Tú, en la terminal

Requisitos:

- macOS o Linux; en Windows, WSL o los comandos de [CLAUDE.md](CLAUDE.md).
- Python 3.11 o más nuevo.
- Para regenerar láminas, además Node 18+ y Google Chrome.

```bash
git clone https://github.com/thehugomtz/caseos-finora.git && cd caseos-finora
./start.sh
```

`start.sh` instala lo necesario, te pregunta con qué modelo y con qué esfuerzo quieres que trabajen los agentes, y abre
CaseOS en http://127.0.0.1:8780. La primera vez tarda unos minutos.

| Opción | Para qué |
|---|---|
| `./start.sh --copia` | Crea «Finora (prueba)», una copia para lanzar agentes sin tocar el original. |
| `./start.sh --model claude-sonnet-5 --effort high --yes` | Arranca sin preguntas, con otro modelo. |
| `./start.sh --port 8790` | Usa otro puerto si el 8780 está ocupado. |
| `./start.sh --solo-instalar` | Solo instala. |

Para detenerlo: Ctrl+C.

### C · Sin instalar nada

Abre directo en el navegador:

- [`presentation.html`](caseos/cases/finora/slides/decks/finora-v5-20260930-112103/presentation.html): el deck final, en
  un solo archivo.
- [`renders/deck.pdf`](caseos/cases/finora/slides/decks/finora-v5-20260930-112103/renders/deck.pdf): el mismo deck en
  PDF.
- [`finora_eda.html`](finora-eda/finora_eda.html): el workspace de EDA, con sus respuestas verificadas.

## 4. Cómo usar la herramienta

### CaseOS: recorrido de 5 minutos (http://127.0.0.1:8780)

1. **Home.** En qué fase va el caso, qué espera una decisión mía y qué hicieron los agentes.
2. **Framing & Shaping.** Mis ideas tal como las dije, separadas en hechos, intuiciones, hipótesis y preguntas. De ahí
   sale el guion de la historia y el plan de investigación.
3. **Research.** Cada investigación con «cómo llegó»: de dónde arrancó, qué consultó en el modelo de datos, qué buscó y
   qué descartó.
4. **Chief of Staff.** Alertas de impacto con opciones A/B/C y el registro de decisiones.
5. **Story.** Cada afirmación con su evidencia aceptada. El código valida que cada cifra exista en una tabla.
6. **Slides.** El deck final y sus anexos.
7. **Datos.** El modelo raw → staging → mart, con 7 checks que cuadran al centavo y una consola SQL de solo lectura.
8. **Analytics.** El workspace de EDA, montado dentro de CaseOS.

Más formas de recorrerlo:

- **Demo mode**, en la barra lateral, recorre el flujo en 14 pasos.
- **Under the hood** muestra agentes, skills y handoffs.
- **⌘K** busca cualquier ID o texto.

### Presentar el deck

En **Slides › Abrir presentación**:

| Tecla | Qué hace |
|---|---|
| → o Espacio | Siguiente lámina |
| ← | Lámina anterior |
| **F** | Pantalla completa |
| **G** | Vista general |
| **N** | Notas del presentador |
| **L** | Prende o apaga el puntero láser. Con el clic sostenido, la marca dura más. |
| Número + Enter | Salta a esa lámina |

### Lanzar agentes

Recorrer el caso no gasta nada. Lo que llama a un modelo:

- platicar con el Briefer o con el Framer;
- lanzar una tarea en Research;
- preguntarle al Chief of Staff;
- armar la historia;
- mandar al Visual Storyteller.

Hazlo en la copia («Finora (prueba)», con `./start.sh --copia`) o en un caso nuevo, desde el selector de caso, «Nuevo
caso». Así el original queda como evidencia. Si tocaste el original, `git restore caseos/cases/finora` lo regresa.

Referencias con Opus 5.5 en esfuerzo máximo:

| Corrida | Tiempo | Costo equivalente |
|---|---|---|
| Un turno del Framer | 1–7 min | ~US$0.4–0.5 |
| Una investigación profunda | ~8 min | ~US$1.6 |
| Un deck completo | ~50 min | US$23–29 |

En esfuerzo `high` todo baja a 1–2 minutos por turno.

### Business Exploration Workspace (http://127.0.0.1:8780/ws/finora/)

- **⌘K.** Una pregunta frecuente se responde al instante, con lo ya verificado.
- **Una pregunta libre y Enter.** El agente la investiga en vivo; tarda de 3 a 10 minutos.
- **«Ver cómo llegamos».** Abre la investigación: hipótesis, evidencia, límites y registro.
- **Preguntas del caso.** W0 a W5 vienen respondidas. W6 y W7 están bloqueadas porque los datos no alcanzan, y la
  herramienta dice qué faltaría.

Para correrlo solo, ver [finora-eda/README.md](finora-eda/README.md).

## 5. Esto corrió de verdad

Nada del caso se escribió a mano para la demo. Todo quedó registrado en archivos:

- **70 corridas de agentes de CaseOS**, todas con Opus 5.5 en esfuerzo máximo, del 29 al 30 de septiembre de 2026. Costaron
  US$154 equivalentes.
- **Dos corridas del Visual Storyteller**: US$28.7 la del deck v3 y US$22.9 la del v5, que tardó 49 minutos.
- **27 corridas del agente de EDA**, con Claude Opus 5, del 27 al 29 de septiembre.
- **Más de 2,200 eventos en la bitácora**, cada uno con su hora y su autor: yo, un agente, o Claude Code cuando le delegué
  algo. Lo delegado lleva la marca «vía Claude».
- **El historial de git de ambas herramientas**, del 27 al 30 de septiembre.

Los costos los reporta el SDK. Con suscripción no se cobra por corrida.

`python3 scripts/evidencia.py` lo resume. El detalle está en [docs/EVIDENCIA.md](docs/EVIDENCIA.md), cómo trabajé en
[docs/COMO-TRABAJE-CON-IA.md](docs/COMO-TRABAJE-CON-IA.md) y la línea de tiempo en [docs/HISTORIAL.md](docs/HISTORIAL.md).

## 6. Modelos

| | Modelo con el que se hizo | Cómo cambiarlo |
|---|---|---|
| Agentes de CaseOS (Briefer, Framer, Research, Chief of Staff, Story, Visual Storyteller) | `claude-opus-5-5`, esfuerzo `max` | `start.sh` lo pregunta, o `CASEOS_MODEL` y `CASEOS_EFFORT` |
| Agente del workspace de EDA | `claude-opus-5` | `FINORA_MODEL`; `start.sh` le pone el mismo que a CaseOS |
| Construcción de las herramientas y coordinación | Claude Code con Opus 5.5 | — |

## 7. Estructura

```text
caseos/        la app (FastAPI + web sin build), sus agentes, skills, pruebas y el caso real en cases/finora
finora-eda/    el workspace de EDA: pipeline de la Fase 1, capa agéntica, cerebro del caso e investigaciones
claude/        skills y agentes del Executive Visual Storyteller (CaseOS los enlaza al arrancar)
docs/          cómo trabajé con IA, dónde verificar la evidencia y el historial
scripts/       evidencia.py: resumen de lo que corrió
start.sh       instala, pregunta el modelo y arranca
CLAUDE.md      instrucciones para Claude Code
AGENTS.md      instrucciones para Codex, Cursor y otros agentes de código
```

Documentos de cada herramienta:

- **CaseOS:** [README](caseos/README.md), [arquitectura](caseos/ARCHITECTURE.md), [agentes](caseos/AGENTS.md),
  [guardrails](caseos/GUARDRAILS.md) y [validación](caseos/docs/VALIDATION.md).
- **Workspace de EDA:** [README](finora-eda/README.md), [arquitectura](finora-eda/docs/propuesta_arquitectura_v1.md) y
  [slice](finora-eda/docs/slice_q2.md).

## 8. Notas

- **No hay llaves en el repo.** Los agentes usan tu sesión de Claude o tu `ANTHROPIC_API_KEY`.
- **Datos.** Los datos y el enunciado son material del reto de Alegra y se comparten solo para evaluar esta entrega.
- **Pruebas.** `cd caseos && ../.venv/bin/python -m pytest -q` corre 87 pruebas. En el workspace,
  `cd finora-eda && ../.venv/bin/python -m evals.run_evals` corre 94 evaluaciones. Ninguna de las dos llama al modelo.
