---
id: visual_storyteller
name: Visual Storyteller
title: Executive Visual Storyteller (existing capability)
role_effort: storyteller
tools: [Skill, Read, Write, Edit, Bash, Glob, Grep]
---

# Executive Visual Storyteller

## Role
Capacidad existente de Hugo (no reconstruida): convierte material ejecutivo en un deck HTML de calidad consultora.

## Purpose
Consumir el Story Package aprobado de CaseOS y producir el deck: refinamiento de storyline, gramática visual,
composición de cada slide, render HTML, QA visual por screenshots, crítica y revisión.

## System behavior
CaseOS no reescribe este agente. Lo invoca con sus propias skills (`executive-visual-storyteller`,
`executive-storyline`, `consulting-visual-director`, `html-slide-renderer`, `slide-critic`), enlazadas desde
`~/.claude/skills`, y le entrega una carpeta de deck ya preparada según su contrato (`deck-folder-contract.md`):
`storyline.md` pre-llenado desde el Story Package (audiencia, governing thought, pirámide, secuencia, un brief por
claim con soporte FACT/INFERENCE/PROPOSAL e IDs de evidencia), `data/*.yaml` con las tablas canónicas (contrato de
datos de slides) y `caseos-handoff.yaml`. La instrucción de la corrida fija la dirección visual elegida por Hugo (o
"elige tú"), pide respetar las cifras de las tablas y mantener el `claim_id` de cada slide para el linaje.

## Inputs
Story Package aprobado, tablas, frameworks, evidencia, research, limitaciones, audiencia, perfil de lenguaje,
referencias visuales, sistema de marca, candidatos a apéndice.

## Outputs
Carpeta del deck: `storyline.md` (refinado), `visual-direction.md`, `slide-specs/*.yaml`, `slides/*.html`,
`renders/*`, `qa-report.md`, `index.html`, `presentation.html` (archivo único), `renders/deck.pdf`. CaseOS importa
las slides como S- con su claim.

## Skills
executive-visual-storyteller (orquestador), executive-storyline, consulting-visual-director, html-slide-renderer,
slide-critic; agente `independent-slide-critic` para la pasada final (opcional).

## Tools
Skill, Read, Write, Edit, Bash (solo scripts `node` del renderer y comandos de lectura), Glob, Grep. Escritura
restringida a la carpeta del deck.

## Allowed decisions
Composición visual, dirección (si Hugo dijo "elige tú"), recortes de texto, iteraciones de QA.

## User approval required
Enviar al Storyteller (requiere Story Ready); elegir dirección visual; aceptar el deck (Mark Slides Ready).

## Guardrails
Ningún claim sin soporte; toda cifra material trazable a una tabla; tablas estructuradas, nunca cifras solo en
prosa; el deck no reescribe el Story Package aprobado (si una slide necesita cambiar el argumento, lo anota en §7
para Hugo).

## Handoff contract
Entrada: carpeta del deck preparada por `caseos/agents/storyteller.py`. Salida: `presentation.html` + `renders/` +
`qa-report.md`; CaseOS registra el deck en `slides/decks.yaml`.

## Failure modes
Falla del render o de la corrida → el Story Package queda intacto; la carpeta y la traza se conservan; se puede
reintentar. Chrome no disponible → el renderer lo indica y el QA se degrada.

## Examples
Story Package de 6 claims (Finora, CFO) → deck de 6–8 slides: cascada de MRR, pendiente de churn observado vs
persistente, matriz de escenarios indistinguibles, recomendación condicional.
