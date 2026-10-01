# executive-visual-storyteller

Agente para **presentaciones ejecutivas de alto nivel en HTML**: storytelling de consultoría,
information design y composición visual, con un loop de crítica sobre los renders. **No** es un
"AI presentation maker": su trabajo es decidir *qué* decir, *cómo se ve cada idea* y *si funcionó*
antes de dar una slide por buena.

```
Story → Visual direction → Visual concept (spec) → HTML render → Visual QA (render → screenshot → critique → revise) → Package
```

## Estructura

```text
~/.claude/skills/
├── executive-visual-storyteller/     Orquestador (entrada): pipeline, gates, comandos naturales, este README
│   └── references/                   command-routing.md · deck-folder-contract.md
├── executive-storyline/              A · contenido → storyline.md (pirámide, SCR, títulos-conclusión). Sin HTML
│   └── references/                   storyline-patterns · slide-brief-schema · synthesis-examples
├── consulting-visual-director/       B · idea → composición (gramática visual por semántica), direcciones, referencias
│   └── references/                   semantic-map · grammar/ (8 familias, ~65 composiciones) · anti-slop ·
│                                     slide-spec-schema · visual-directions · reference-analysis · deck-rhythm
├── html-slide-renderer/              C · spec → HTML con primitivas + scripts de render/QA/bundle (cero dependencias)
│   ├── assets/                       core.css · primitives.js · deck.js · themes/{editorial,modern,blueprint}.css ·
│   │                                 fonts/ (OFL: Newsreader, Inter, Archivo, IBM Plex) · templates/slide.html
│   ├── scripts/                      new-deck · render (PNG+QA+contact sheet) · directions (tablero) · bundle (single-file+PDF)
│   └── references/                   primitives-api · construction-notes · tokens-and-typography
└── slide-critic/                     D · lectura a ciegas + checklist + rúbrica → PASS / PATCH / RECOMPOSE
    └── references/                   checklist · rubric · failure-modes
~/.claude/agents/
├── executive-visual-storyteller.md   subagente que precarga las 5 skills (delegar un deck completo)
└── independent-slide-critic.md       crítico con contexto limpio, sin permiso de editar (pasada final)
```

Requisitos: Node ≥ 22 y cualquier Chrome/Chromium/Edge instalado (se autodetecta; `CHROME_PATH` para
forzar uno). Sin `npm install`.

## Cómo usarlo

En cualquier proyecto de Claude Code, en lenguaje natural (la skill se activa sola) o explícito:

```text
/executive-visual-storyteller Convierte este documento en un deck ejecutivo para el comité: @brief.md
```

Para delegar el deck completo a un subagente (útil en decks largos o en paralelo):

```text
Usa el agente executive-visual-storyteller para convertir @caso.pdf en un deck de 8 slides; dirección editorial.
```

> Las skills funcionan de inmediato. Los agentes (`executive-visual-storyteller`, `independent-slide-critic`)
> se registran al cargar la sesión: si no aparecen, reinicia la sesión de Claude Code.

### Prompts de ejemplo

| Quieres… | Di… |
|---|---|
| Deck completo | "Convierte este documento en un deck ejecutivo de 6 slides para el Comité de Dirección." |
| Solo la historia | "Arma la narrativa y los títulos-conclusión antes de diseñar nada." |
| Diagnóstico de mensaje | "Revisa si estoy comunicando una conclusión o sólo mostrando datos." |
| Arreglar una slide genérica | "Esta slide está demasiado AI; busca una composición más editorial." |
| Framework | "Convierte esta idea en un framework visual: …" |
| Estructura de consultoría | "Haz esta slide más McKinsey-like en estructura, no en branding." |
| Opciones | "Genera tres alternativas visuales para la slide 4." |
| Síntesis | "Reduce esta slide 40% sin perder el argumento." |
| Relación | "Haz que esta relación sea evidente visualmente." |
| Dirección visual | "Propón direcciones visuales con estas referencias: [screenshots]." |
| Contenido débil | "Métricas: CAC, LTV, churn, ARPU, ARR" → el agente pregunta qué relación quieres mostrar y propone una arquitectura |
| Entregable | "Dame el single-file y el PDF." |

### Scripts (los usa el agente; también puedes correrlos a mano)

```bash
S=~/.claude/skills/html-slide-renderer/scripts
node $S/new-deck.mjs decks/mi-deck --title "Título" --direction editorial
node $S/directions.mjs decks/mi-deck --themes editorial,modern,blueprint
node $S/render.mjs decks/mi-deck            # renders/NN.png, thumbs, contact-sheet.png, qa-summary.md
node $S/bundle.mjs decks/mi-deck --pdf      # index.html, presentation.html, renders/deck.pdf + fidelidad
```

## Salida por proyecto

```text
decks/<slug>/
  storyline.md  visual-direction.md  slide-specs/Sxx.yaml  qa-report.md
  slides/NN.html  assets/  directions/  renders/ (NN.png, thumbs/, contact-sheet.png, qa.json, deck.pdf)
  index.html (visor: ←/→, G vista general, N notas, F pantalla completa, P imprimir)
  presentation.html (un solo archivo autocontenido: fuentes, CSS, JS y slides embebidos)
```

## Qué evita el "card-card-card AI slop" (mecanismos, no intenciones)

1. **Separación story / diseño.** `executive-storyline` no puede producir layout; entrega
   conclusiones y el *verbo* de cada idea. Sin relación nombrada no hay slide: vuelve a la historia.
2. **La composición se deriva de la semántica.** `semantic-map.md` va de verbo a composición: converge
   → converging paths; se fuga → value leakage; se anida → concentric system; depende → layers…
   El número de bullets nunca decide el layout.
3. **Elección forzada entre alternativas.** Cada spec lleva 3 candidatas de familias distintas, puntaje
   (fidelidad, foco, evidencia, variedad, riesgo) y el porqué del rechazo. Una composición elegida
   deja rastro; una por default no pasa el gate.
4. **Cards como último recurso, con permiso explícito.** Máximo un grid de cards por deck,
   marcado `data-qa-allow="card-grid"` y justificado en su spec.
5. **Detector automático de slop** (probe dentro de la página). Detecta grids de cajas casi
   idénticas con texto (fila o retícula), pilas de cajas, viñetas, emoji, sombras, gradientes,
   inflación de bordes y tiles redondeados, íconos decorativos, dilución del acento, falta de foco
   declarado, exceso de palabras, texto encimado o recortado, contraste, tamaño mínimo y
   desalineaciones de pocos píxeles. A nivel deck: composiciones repetidas, baja variedad, más de un
   grid de cards y rachas densas sin respiro.
6. **Crítica sobre la imagen, no sobre el código.** Lectura a ciegas del thumbnail (qué veo primero y
   qué dice) *antes* de leer el spec. Si no coincide con el takeaway, es falla de foco o de historia.
7. **RECOMPOSE ≠ PATCH.** Fidelidad, foco o historia ≤ 2 obliga a cambiar de gramática visual; está
   prohibido "arreglar" un problema conceptual con padding o tamaño de letra.
8. **Crítico independiente.** Contexto limpio, sin permiso de editar: quien diseña la slide no la aprueba.
9. **Primitivas, no plantillas.** No existe un "layout de 3 columnas" que rellenar; existen líneas,
   conectores anclados, anillos, escalas y labels. Componer es obligatorio.
10. **Consistencia de sistema con variedad de composición.** Los tokens, la línea, las anotaciones y
    la codificación de color se repiten en todo el deck; los layouts no.

## Demo

`~/GitHub/Claude Prueba/decks/demo-ia-banca/`: un banco ficticio que escala IA. Son 5 slides, cada
una con una composición distinta y ninguna card: statement con barra de proporción, value leakage,
sistema concéntrico teñido por presupuesto con las fugas en el borde, swimlane con eje de tiempo, y arquitectura de capas con
eje de gobierno. Incluye tablero de direcciones, specs, QA con 5 rondas: 2 RECOMPOSE (S05 por el autor,
S03 por el crítico independiente) y 2 pasadas independientes. También `presentation.html` y el PDF.
Cifras ilustrativas.
