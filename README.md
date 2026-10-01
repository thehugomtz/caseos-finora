# Finora · el caso resuelto con IA, de punta a punta

Este repo es la entrega de Víctor Hugo Martínez Medina para el reto técnico de Alegra, «Business Analytics: del dato a la
decisión». Trae las dos herramientas con las que resolví el caso y el caso tal como quedó, con todo su rastro: qué
hicieron los agentes, qué decidí yo y cuánto costó cada corrida.

| | Qué es | Dónde |
|---|---|---|
| **CaseOS** | Un case room con agentes y compuertas humanas: Brief → Framing & Shaping → Research → Chief of Staff → Story → Slides. Los agentes hacen el trabajo y yo apruebo cada paso. | [`caseos/`](caseos/) |
| **Business Exploration Workspace** | La herramienta de EDA. Un pipeline reproducible sobre los CSV de Finora y un agente que investiga preguntas con SQL, revisado por un validador. | [`finora-eda/`](finora-eda/) |
| **Executive Visual Storyteller** | Mis skills para hacer decks ejecutivos en HTML. CaseOS las usa para armar el deck. | [`claude/`](claude/) |

## Pruébalo

Necesitas macOS o Linux (en Windows, WSL; o sigue [CLAUDE.md](CLAUDE.md)) y Python 3.11 o más nuevo. Para correr
agentes necesitas además una sesión de Claude Code o una `ANTHROPIC_API_KEY`. Recorrer el caso no gasta nada.

```bash
git clone https://github.com/thehugomtz/caseos-finora.git && cd caseos-finora
./start.sh
```

`start.sh` instala lo necesario y te pregunta con qué modelo quieres que trabajen los agentes. Luego abre CaseOS en
http://127.0.0.1:8780 con el caso Finora. Para este ejercicio usé **Claude Opus 5.5** (`claude-opus-5-5`) con esfuerzo
máximo.

**Con un asistente de IA.** Abre Claude Code (u otro agente de código) en esta carpeta y dile: «el candidato pasó este
repo, ¿cómo pruebo su herramienta?». [CLAUDE.md](CLAUDE.md) le dice qué hacer, y antes de instalar te pregunta el modelo.

**Sin instalar nada.** Abre en el navegador
[`presentation.html`](caseos/cases/finora/slides/decks/finora-v5-20260930-112103/presentation.html), el deck final, en
un solo archivo. Abre también [`finora_eda.html`](finora-eda/finora_eda.html), el workspace de EDA con sus respuestas
verificadas. El PDF del deck está en
[`renders/deck.pdf`](caseos/cases/finora/slides/decks/finora-v5-20260930-112103/renders/deck.pdf).

## Qué ver en 5 minutos

1. **Home.** En qué fase va el caso, qué espera una decisión mía y qué hicieron los agentes.
2. **Framing & Shaping.** Mis ideas tal como las dije, separadas en hechos, intuiciones, hipótesis y preguntas, más el
   guion de la historia.
3. **Research.** Cada investigación con «cómo llegó»: de dónde arrancó, qué consultó en el modelo de datos, qué buscó y
   qué descartó.
4. **Chief of Staff.** Alertas de impacto con opciones y el registro de decisiones.
5. **Story.** Cada afirmación con su evidencia aceptada. El código valida que cada cifra exista en una tabla.
6. **Slides.** El deck final y sus anexos. «Abrir presentación» lo muestra; al presentar, el cursor es un puntero
   láser.
7. **Analytics.** El workspace de EDA, montado dentro de CaseOS.

**Demo mode**, en la barra lateral, recorre el flujo en 14 pasos. **Under the hood** muestra agentes, skills y
handoffs.

## Esto corrió de verdad

Nada del caso se escribió a mano para la demo. Todo quedó registrado en archivos que puedes revisar:

- **70 corridas de agentes de CaseOS**, todas con Opus 5.5 en esfuerzo máximo, del 29 al 30 de septiembre de 2026.
  Costaron US$154 equivalentes.
- **Dos corridas del Visual Storyteller**, que hicieron los decks: US$28.7 la del v3 y US$22.9 la del v5, que tardó 49
  minutos.
- **27 corridas del agente de EDA**, con Claude Opus 5, del 27 al 29 de septiembre.
- **Más de 2,200 eventos en la bitácora del caso**, cada uno con su hora y su autor: yo, un agente, o Claude Code cuando le
  delegué algo. Lo delegado lleva la marca «vía Claude».
- **El historial de git de ambas herramientas**, del 27 al 30 de septiembre.

Los costos los reporta el SDK. Con suscripción no se cobra por corrida.

`python3 scripts/evidencia.py` lo resume. El detalle está en [docs/EVIDENCIA.md](docs/EVIDENCIA.md) y cómo trabajé, en
[docs/COMO-TRABAJE-CON-IA.md](docs/COMO-TRABAJE-CON-IA.md).

## Prueba algo nuevo

- **Un caso tuyo.** En el selector de caso, «Nuevo caso». Le pones nombre y empiezas a platicar con el Briefer.
- **Experimentar con Finora.** `./start.sh --copia` crea «Finora (prueba)», una copia para lanzar agentes sin tocar el
  original. Si tocaste el original, `git restore caseos/cases/finora` lo regresa.
- **El workspace de EDA solo.** Ver [finora-eda/README.md](finora-eda/README.md).

## Modelos

| | Modelo con el que se hizo | Cómo cambiarlo |
|---|---|---|
| Agentes de CaseOS (Briefer, Framer, Research, Chief of Staff, Story, Visual Storyteller) | `claude-opus-5-5`, esfuerzo `max` | `start.sh` lo pregunta, o `CASEOS_MODEL` y `CASEOS_EFFORT` |
| Agente del workspace de EDA | `claude-opus-5` | `FINORA_MODEL`; `start.sh` le pone el mismo que a CaseOS |
| Construcción de las herramientas y coordinación | Claude Code con Opus 5.5 | — |

Referencias con Opus 5.5 en esfuerzo máximo:

| Corrida | Tiempo | Costo equivalente |
|---|---|---|
| Un turno del Framer | 1–7 min | ~US$0.4–0.5 |
| Una investigación profunda | ~8 min | ~US$1.6 |
| Un deck completo del Storyteller | ~50 min | US$23–29 |

En esfuerzo `high`, los turnos bajan a 1–2 minutos.

## Estructura

```text
caseos/        la app (FastAPI + web sin build), sus agentes, skills, pruebas y el caso real en cases/finora
finora-eda/    el workspace de EDA: pipeline de la Fase 1, capa agéntica, cerebro del caso e investigaciones
claude/        skills y agentes del Executive Visual Storyteller (CaseOS los enlaza al arrancar)
docs/          cómo trabajé con IA, dónde verificar la evidencia y el historial
scripts/       evidencia.py: resumen de lo que corrió
start.sh       instala, pregunta el modelo y arranca
```

Documentos de cada herramienta:

- **CaseOS:** [README](caseos/README.md), [arquitectura](caseos/ARCHITECTURE.md), [agentes](caseos/AGENTS.md),
  [guardrails](caseos/GUARDRAILS.md) y [validación](caseos/docs/VALIDATION.md).
- **Workspace de EDA:** [README](finora-eda/README.md), [arquitectura](finora-eda/docs/propuesta_arquitectura_v1.md) y
  [slice](finora-eda/docs/slice_q2.md).

## Notas

- **No hay llaves en el repo.** Los agentes usan tu sesión de Claude o tu `ANTHROPIC_API_KEY`.
- **Datos.** Los datos y el enunciado son material del reto de Alegra y se comparten solo para evaluar esta entrega.
- **Pruebas.** `cd caseos && ../.venv/bin/python -m pytest -q` corre 87 pruebas. En el workspace,
  `cd finora-eda && ../.venv/bin/python -m evals.run_evals` corre 94 evaluaciones. Ninguna de las dos llama al modelo.
