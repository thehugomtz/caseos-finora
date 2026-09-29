# CaseOS

**Un case room con agentes para resolver casos de negocio de punta a punta.**
Brief → Framing → Research → Chief of Staff → Story Package → Executive Visual Storyteller → deck HTML.

> Los agentes hacen el trabajo. **Hugo es dueño del juicio.**
> Ninguna fase avanza sola: solo Hugo aprueba el framing, acepta evidencia, decide entre alternativas, aprueba la
> story y marca cada fase como Ready. Cada cambio queda con ID, linaje, versión y traza.

Finora es el primer caso (importado desde el brief v0.3 y el Business Exploration Workspace, no escrito a mano).
CaseOS es reutilizable: **New Case** crea un caso vacío con la misma estructura.

---

## Arrancar

```bash
cd "Claude Prueba/caseos"
uv venv --system-site-packages --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m caseos import-finora     # solo la primera vez (o --force para reimportar desde cero)
.venv/bin/python -m caseos serve             # http://127.0.0.1:8780
```

También: `./scripts/caseos.sh serve`, `./scripts/caseos.sh test`.

- **Sin llaves.** Los agentes corren con el **Claude Agent SDK sobre tu suscripción de Claude** (la sesión local de
  Claude Code). No hay API key en el repo; `ANTHROPIC_API_KEY` solo si quieres facturación por API a propósito.
  Ver `.env.example`.
- **Modelo:** `claude-opus-5` para todos los agentes. El costo se controla con *effort* por rol y un tope por corrida
  (`caseos/config.py`), nunca bajando de modelo. Cada corrida guarda su costo equivalente en `audit/runs/`.
- **Corridas largas** (research L3, Visual Storyteller): arranca el servidor en tu propia terminal para que un reinicio
  del panel no las interrumpa. Si algo se interrumpe, la solicitud queda guardada y se reintenta con un clic.
- Solo escucha en `127.0.0.1`.

## Cómo se usa (3–5 minutos)

1. **Home** — el estado del caso: fase actual, qué espera tu decisión, qué están haciendo los agentes.
2. **Briefing** — el brief importado con sus fuentes y los vacíos declarados. *Mark Ready* (solo tú).
3. **Framing** — escribe como piensas («creo que están metiendo más leads pero no convierten…»). El Framer separa
   hechos, intuiciones, supuestos, hipótesis (con falsificador) y preguntas; conserva **tus palabras junto a la versión
   estructurada**. Modos: *Organize* (ordena), *Advise* (2–3 alternativas), *Challenge* (intenta romperlo). Aprueba el
   framing con *Approve Framing · Mark Ready*.
4. **Research** — pide una investigación; el Router elige especialista (Business Research, Measurement, Data
   Engineering, Analytics) e intensidad (L1 lookup · L2 · L3 deep research con peer review). Las citas solo cuentan si la
   URL se recuperó en la corrida. Aceptas, rechazas, cuestionas o profundizas cada resultado.
5. **Analytics** — el Business Exploration Workspace de Finora, reutilizado tal cual (`/ws/finora`). Un claim validado se
   promueve a finding y viaja al COS como **EvidenceTable** con linaje completo.
6. **Chief of Staff** — sala de control: alertas de impacto (apoya / debilita / contradice…) con opciones A/B/C, decision
   log, claims más débiles, siguientes mejores acciones. Pregúntale lo que sea del caso.
7. **Story** — el COS arma el **Story Package**; el código valida que cada claim tenga evidencia aceptada y que cada cifra
   exista en una tabla. Lo apruebas tú.
8. **Slides** — el paquete aprobado pasa al **Executive Visual Storyteller existente** (no se reconstruyó: se enlaza) y
   regresa un deck HTML.
9. **Agents** / **Artifacts** — topología de agentes con lo que hace cada uno; archivos del caso, `brain.md`, decisiones,
   snapshots.

Atajos: **⌘K** busca cualquier ID o texto y ejecuta comandos («pregúntale a Measurement…», «mándale esto a research»,
«guarda como decisión…», «no estoy convencido», «qué falta para cerrar»). **Under the hood** muestra agentes, skills
cargadas, handoffs y validaciones (traza operativa, nunca cadena de pensamiento). **Demo mode** recorre el flujo en 14
pasos.

## Dónde vive cada cosa

| | |
|---|---|
| `caseos/` | backend (FastAPI, un solo proceso): estado, fases, agentes, jobs, validaciones |
| `web/` | la app (ES modules sin build step) |
| `agents/*.md` | contrato de cada agente (rol, comportamiento, inputs/outputs, guardrails, handoff, fallas) |
| `skills/` | `manifest.yaml` (fuente de verdad del loader), skills propias y de terceros con licencia y procedencia |
| `cases/<id>/` | un caso = carpetas de archivos legibles (YAML/Markdown): ver `cases/README.md` |
| `tests/` | 32 pruebas (núcleo, framer, research, handoffs, API) + 1 eval en vivo opcional |

Documentos: [ARCHITECTURE](ARCHITECTURE.md) · [AGENTS](AGENTS.md) · [SKILLS](SKILLS.md) · [GUARDRAILS](GUARDRAILS.md) ·
[REUSE](REUSE.md) (qué se reutilizó, refactorizó, creó o dejó de usarse) · [VALIDATION](docs/VALIDATION.md).

## Pruebas

```bash
.venv/bin/python -m pytest -q tests          # sin modelo: runtime simulado (FakeLLM)
CASEOS_LIVE=1 .venv/bin/python -m pytest -q tests/test_live.py   # opcional: un turno real del Framer (~US$0.4 equivalentes)
```

## Límites conocidos

- Analytics necesita un workspace analítico enlazado al caso. Hoy existe el adaptador del Business Exploration Workspace
  (Finora). Un caso nuevo sin workspace tiene Business Research, Measurement y Data Engineering; Analytics aparece como no
  disponible hasta que se escriba su adaptador (interfaz en ARCHITECTURE › Workspaces).
- El texto literal del enunciado de Alegra no está en el repo: el brief de Finora se reconstruyó desde el brief v0.3 y las
  notas del proyecto, y lo declara como vacío.
- Un turno del Framer tarda ~1.5 min (Opus 5, effort high); research L2 3–8 min; L3 y el Storyteller, más.
- `cases/finora` contiene material del reto: decide si es público o privado antes de subir el repo a GitHub.
