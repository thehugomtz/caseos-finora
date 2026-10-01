# CaseOS

**Un case room con agentes para resolver casos de negocio de punta a punta.**
Brief → Framing & Shaping → Research → Chief of Staff → Story Package → Executive Visual Storyteller → deck HTML.

> Los agentes hacen el trabajo. **Hugo es dueño del juicio.**
> Ninguna fase avanza sola: solo Hugo aprueba el documento de Shaping, acepta evidencia, decide entre alternativas, aprueba la
> story y marca cada fase como Ready. Cada cambio queda con ID, linaje, versión y traza.

Finora es el primer caso (importado desde el brief v0.3 y el Business Exploration Workspace, no escrito a mano).
CaseOS es reutilizable: **New Case** crea un caso vacío con la misma estructura.

---

## Empezar un caso desde cero

Selector de caso › **Nuevo caso**: solo el nombre (y, si quieres, el modelo de datos). Te lleva a Briefing en blanco.

## Arrancar

En el repo compartido, desde la raíz: **`./start.sh`** instala todo, pregunta con qué modelo correr los agentes y abre
CaseOS con el caso Finora tal como quedó. A mano:

```bash
cd caseos
uv venv --python 3.13 .venv                   # o: python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m caseos serve             # http://127.0.0.1:8780
```

El caso Finora ya viene en `cases/finora` (no hace falta importarlo). `import-finora --force` lo reconstruye desde cero
y **borra** lo trabajado, no lo corras sobre el caso real. También: `./scripts/caseos.sh serve`, `./scripts/caseos.sh test`.

- **Sin llaves.** Los agentes corren con el **Claude Agent SDK sobre tu suscripción de Claude** (la sesión local de
  Claude Code). No hay API key en el repo; `ANTHROPIC_API_KEY` solo si quieres facturación por API a propósito.
  Ver `.env.example`.
- **Modelo:** el caso Finora se trabajó con `claude-opus-5-5` en esfuerzo **max** para todos los agentes (pedido de
  Hugo). Para otro modelo: `CASEOS_MODEL` (p. ej. `claude-sonnet-5`) y `CASEOS_EFFORT` (`max`, `high`…); por agente,
  `CASEOS_MODEL_<AGENTE>` y `CASEOS_EFFORT_<ROL>`. Cada corrida guarda modelo, esfuerzo y costo equivalente en
  `audit/runs/`.
- **Corridas largas** (research L3, Visual Storyteller): arranca el servidor en tu propia terminal para que un reinicio
  del panel no las interrumpa. Si algo se interrumpe, la solicitud queda guardada y se reintenta con un clic.
- Solo escucha en `127.0.0.1`.

## Cómo se usa (3–5 minutos)

1. **Home** — el estado del caso: fase actual, qué espera tu decisión, qué están haciendo los agentes.
2. **Briefing** — platicas con el **Briefer** como en Framing (ideas sueltas, un reencuadre o el enunciado pegado) y él
   propone el brief por secciones; tú apruebas, editas o descartas cada una. Nada aprobado se sobrescribe: un cambio
   llega como revisión. Aquí también eliges el **modelo de datos** del caso. *Mark Ready* pide objetivo, audiencia y
   entregables aprobados.
3. **Framing & Shaping** — escribe como piensas («creo que están metiendo más leads pero no convierten…»). El Framer
   separa hechos, intuiciones, supuestos, hipótesis (con falsificador) y preguntas; conserva **tus palabras junto a la
   versión estructurada**. Modos: *Organize* (ordena), *Advise* (2–3 alternativas), *Challenge* (intenta romperlo).
   Lo que sale de aquí es el **documento de Shaping** (`framing/current.md`), que se arma pieza por pieza y tú apruebas,
   editas o descartas cada una:
   1. **Problema** — planteamiento, situación, por qué importa, dentro y fuera del alcance (no-gos).
   2. **Pregunta ejecutiva**.
   3. **Guion de la historia** — secciones → láminas; cada lámina dice qué pregunta responde y qué debe mostrar.
   4. **Hipótesis** con falsificador.
   5. **Plan de investigación** — **Armar el plan desde el guion**: cada pregunta de tus láminas se vuelve una tarea con
      *qué sale* (investigación y propuesta · investigar datos · research externo), una **respuesta de arranque** escrita
      con el contexto del caso y lo que ya dijiste (con tus palabras textuales citadas), y los **pasos**: qué investigar
      en el modelo de datos (tablas reales), qué buscar afuera y qué se entrega. La lidera un agente: Analytics,
      Measurement, Data Engineering o Business Research. Cada lámina del guion muestra qué tarea la trabaja.
   6–8. Lo que no afirmamos todavía, decisiones necesarias y riesgos.

   *Mark Ready* pide el problema aprobado. Si tu estructura vivía en Entregables del brief, **Traer como propuestas** la
   convierte en Guion (y el research necesario en tareas tipadas) sin aprobar nada por ti.
4. **Research** — arriba, las tareas aprobadas del plan de investigación, con qué sale, su respuesta de arranque, sus
   pasos y un botón **Lanzar** (lanzarlas es tu clic). El especialista recibe la respuesta de arranque para validarla o
   refutarla y, si la tarea tiene pasos de datos, **consulta el modelo de datos en solo lectura**; una cifra del modelo
   solo cuenta si su consulta corrió en esa corrida (quedan listadas en el detalle). La pestaña **Propuestas · cómo
   llegaron** muestra, para cada propuesta, de dónde arrancó, cómo leyó el problema, qué revisó en orden (cada consulta
   al modelo, búsqueda y lectura, con su minuto), qué alternativas descartó y por qué, a qué llegó y qué hizo el COS. Es la
   traza operativa de la corrida, no el razonamiento interno del modelo (que no se guarda). Abajo puedes pedir cualquier otra investigación; el Router elige especialista (Business
   Research, Measurement, Data Engineering, Analytics) e intensidad (L1 lookup · L2 · L3 deep research con peer review).
   Las citas solo cuentan si la URL se recuperó en la corrida. Aceptas, rechazas, cuestionas o profundizas cada resultado.
5. **Datos** — el modelo de datos del caso en tres capas reales: **raw** (los CSV tal cual), **staging** (tipado con las
   reglas de la Fase 1) y **mart** (lo que consulta Analytics). Columnas, muestra real, consola SQL de solo lectura y 7
   checks de reconciliación que prueban que las capas cuadran al centavo. Cualquier tabla de evidencia se puede
   **comprobar** re-ejecutando su consulta sobre el modelo.
6. **Analytics** — el Business Exploration Workspace de Finora, reutilizado tal cual (`/ws/finora`). Un claim validado se
   promueve a finding y viaja al COS como **EvidenceTable** con linaje completo.
7. **Chief of Staff** — sala de control: alertas de impacto (apoya / debilita / contradice…) con opciones A/B/C, decision
   log, claims más débiles, siguientes mejores acciones. Pregúntale lo que sea del caso.
8. **Story** — el COS arma el **Story Package** siguiendo tu Guion; el código valida que cada claim tenga evidencia
   aceptada y que cada cifra exista en una tabla. La pestaña **Guion** muestra lámina por lámina qué claims la cubren y
   si la evidencia está (con evidencia · parcial · sin evidencia). En cada claim, **Cómo se llegó a esto** abre lo
   registrado de la investigación que lo sostiene: arranque, lectura del problema, pasos en orden, qué descartó y qué
   eligió, conclusión y evaluación del COS (sin llamar a ningún modelo). Una lámina sin evidencia no se rellena: queda marcada
   y su pregunta pasa a research. Lo apruebas tú.
9. **Slides** — el paquete aprobado pasa al **Executive Visual Storyteller existente** (no se reconstruyó: se enlaza) y
   regresa un deck HTML. Puedes darle una **guía de formato** en palabras simples: tipografía de títulos y de texto
   (cualquier Google Font), colores y notas; se aplica como tema del renderer con el contraste revisado. Sobre un deck
   terminado: reordenar arrastrando, editar texto sobre la lámina, agregar separadores, traer una lámina de un deck
   anterior, regenerar el PDF y **pedirle cambios puntuales al Storyteller** en láminas concretas (no rehace el deck). Al
   presentar, el cursor es un puntero láser (tecla L).
10. **Agents** / **Artifacts** — topología de agentes con lo que hace cada uno; archivos del caso, `brain.md`, decisiones,
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
| `tests/` | 87 pruebas (núcleo, framer, research, handoffs, API, editor de slides) + 1 eval en vivo opcional |

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
- El brief de Finora se armó desde el brief de trabajo de Hugo (v0.3, en `cases/finora/brief/sources`) y sus notas del
  proyecto.
- Con Opus 5.5 en esfuerzo max, un turno del Briefer o del Framer tarda varios minutos (medido: 6.8 min un turno del
  Briefer); research, COS y Storyteller, más. Con `high` los turnos eran de 1–2 min.
