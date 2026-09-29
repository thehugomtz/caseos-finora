# Casos

Un caso es una carpeta de archivos legibles. No hay base de datos: estos archivos **son** el estado.

```
cases/<id>/
  case.yaml              metadatos, fases (estado, versiones aprobadas), perfil de lenguaje, workspace analítico
  brain.md               memoria viva del caso (se regenera en cada cambio material; ver secciones abajo)
  README.md
  brief/                 brief.yaml · brief.md · sources/ · approved/brief.vN.yaml
  framing/               current.yaml (framing vivo) · current.md · conversation.jsonl (turnos con el Framer)
                         items/N-xxx.yaml (hechos, intuiciones, supuestos, observaciones…) · approved/ · versions/
  questions/Q-xxx.yaml   hypotheses/H-xxx.yaml   decisions/D-xxx.yaml
  research/R-xxx.yaml    solicitud + ruta + resultado (§40) + fuentes con verificación + revisión de Hugo
  evidence/findings/F-xxx.yaml   evidence/tables/T-xxx.yaml (EvidenceTables)   evidence/artifacts/
  cos/alerts/X-xxx.yaml  alertas de impacto con opciones   cos/state.yaml
  story/package.yaml     Story Package vigente · story.md · claims/C-xxx.yaml · versions/ · approved/
  slides/decks/<slug>/   carpeta del Visual Storyteller (storyline, data, specs, slides, renders, presentation.html)
  artifacts/A-xxx.yaml   snapshots/<fase>/v<N>-<hora>/ (copia del caso al marcar Ready)
  audit/activity.jsonl   traza operativa · audit/runs/ (cada corrida de agente) · audit/prompts/ · audit/jobs/
         versions/<ID>/vN.yaml (cada versión anterior de cada entidad)
```

**IDs:** Q pregunta · H hipótesis · N nota del framing · R research · F finding · T tabla · D decisión · X alerta ·
C claim · S slide · A artefacto. Son secuenciales por caso y nunca se reutilizan.

**brain.md** tiene las secciones: Case, Objective, Audience, Current Phase, Current Status, Approved Briefing, Approved Framing, Governing Question, Executive Questions, Current Story, Decisions, Active Hypotheses, Evidence We Trust, Things We Cannot Claim, Open Questions, Research Queue, Accepted Frameworks, Key Tables, Contradictions, Risks, Artifacts, Language Profile y Recent Material Changes.

## Crear un caso

- Desde la app: selector de caso › **New Case** (nombre, objetivo, audiencia, contexto, entregables, restricciones).
- Por API: `POST /api/cases`.
- Finora: `.venv/bin/python -m caseos import-finora` (importa el brief v0.3, el framing, las preguntas del plan de
  trabajo, los hallazgos canónicos y las tablas desde el workspace, con procedencia en cada elemento; `--force` lo
  rehace desde cero).

`finora/` contiene material del reto: decide si es público antes de subir el repo.
