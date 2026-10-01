# Para el asistente de IA que abra este repo

Estás ayudando a alguien de Alegra a probar la entrega de un candidato, Víctor Hugo Martínez Medina, para el reto técnico
de Finora. Tu trabajo es dejarlo corriendo en esta computadora y guiar a la persona. No cambies el código ni el caso.

## 1. Antes de instalar, pregunta

- **Qué quiere hacer.** Si solo quiere ver el caso resuelto, no necesita modelo ni llaves: recorrer CaseOS no llama a
  ningún agente.
- **Con qué modelo quiere que trabajen los agentes**, si los va a correr. Dile que en este ejercicio el candidato usó
  **Claude Opus 5.5 (`claude-opus-5-5`) con esfuerzo `max`** en todos los agentes de CaseOS. El agente del workspace de
  EDA usó `claude-opus-5`. Ofrece:

  | Modelo | Para qué |
  |---|---|
  | `claude-opus-5-5` | Reproducir el ejercicio tal cual. Un turno puede tardar varios minutos. |
  | `claude-sonnet-5` | Más rápido y más barato. |
  | `claude-haiku-4-5-20251001` | Recorrer el flujo rápido. |
  | Otro ID | El que tenga disponible. |

- **Qué esfuerzo quiere.** `max` es el del ejercicio. `high` es más rápido: 1 a 2 minutos por turno.

## 2. Instala y arranca

En macOS o Linux, desde la raíz del repo:

```bash
./start.sh --model <id> --effort <max|high> --yes
```

El script:

1. Busca Python 3.11 o más nuevo. Usa `uv` si está.
2. Crea `.venv` en la raíz e instala `caseos/requirements.txt`, que cubre las dos herramientas.
3. Construye la base DuckDB del workspace de EDA.
4. Guarda el modelo en `.env`.
5. Arranca CaseOS en http://127.0.0.1:8780 y lo abre en el navegador.

Para detenerlo: Ctrl+C. Si el puerto está ocupado: `--port 8790`. `--no-open` evita abrir el navegador.

En Windows sin WSL, a mano desde la raíz:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r caseos\requirements.txt
cd finora-eda; ..\.venv\Scripts\python -c "from agent.warehouse import build; build()"; cd ..
$env:CASEOS_MODEL="claude-opus-5-5"; $env:CASEOS_EFFORT="max"; $env:FINORA_MODEL="claude-opus-5-5"
cd caseos; ..\.venv\Scripts\python -m caseos serve
```

## 3. Para correr agentes

- **Autenticación.** Los agentes corren con el Claude Agent SDK, que trae su propio CLI de Claude. Usan la sesión de
  Claude Code que ya exista en esta computadora o, si está definida, `ANTHROPIC_API_KEY`.
- **Sin sesión.** Si no hay ninguna, todo se puede recorrer, pero los botones que lanzan agentes van a fallar. Dile cómo
  iniciar sesión: correr `claude` y escribir `/login`. Si no tiene Claude Code, el CLI que trae el SDK está en
  `.venv/lib/python3.*/site-packages/claude_agent_sdk/_bundled/claude`. La otra opción es exportar `ANTHROPIC_API_KEY`
  antes de `./start.sh`.
- **Costo.** Antes de lanzar un agente, avísale que gasta de su cuenta. Referencias con Opus 5.5 en `max`:

  | Corrida | Costo equivalente | Tiempo |
  |---|---|---|
  | Un turno del Framer | ~US$0.4 | — |
  | Una investigación profunda | ~US$1.6 | — |
  | Un deck completo | US$23–29 | ~50 min |

## 4. Guíalo

- **Recorrido.** Sigue «Qué ver en 5 minutos» del [README](README.md). En la barra lateral de CaseOS, **Demo mode**
  recorre el flujo en 14 pasos.
- **Prueba de que corrió.** `.venv/bin/python scripts/evidencia.py` resume corridas, modelos, costos, bitácora y
  entidades. Para abrir algo concreto, ve [docs/EVIDENCIA.md](docs/EVIDENCIA.md).
- **Experimentar sin tocar el original.** `./start.sh --copia` crea «Finora (prueba)».
- **Un caso nuevo.** En el selector de caso, «Nuevo caso».
- **Sin servidor.** Si la plataforma no puede ejecutar comandos, la persona puede abrir directo en el navegador:
  - `caseos/cases/finora/slides/decks/finora-v5-20260930-112103/presentation.html`, el deck en un solo archivo.
  - `renders/deck.pdf`, en esa misma carpeta.
  - `finora-eda/finora_eda.html`.

## No hagas

- No corras `python -m caseos import-finora --force`: reconstruye Finora desde cero y borra lo trabajado.
- No edites a mano `caseos/cases/finora/`: es la evidencia. Para probar, usa la copia.
- No subas el `.env` ni llaves a git.

## Si algo falla

- **«Analytics no disponible».** Falta la base del workspace. `./start.sh` la construye; también el comando de la
  sección 2.
- **Regenerar láminas o el PDF.** Necesita Node 18+ y Google Chrome. Para ver el deck no hacen falta.
- **Corridas largas.** El Storyteller o una investigación profunda necesitan que el servidor siga vivo. Si se corta, la
  solicitud queda guardada y se reintenta con un clic.
- **Detalle técnico.** [caseos/README.md](caseos/README.md), [caseos/ARCHITECTURE.md](caseos/ARCHITECTURE.md) y
  [finora-eda/README.md](finora-eda/README.md).
