---
name: html-slide-renderer
description: "Render slide specs (YAML from consulting-visual-director) into self-contained 16:9 HTML slides built from low-level primitives — text roles, lines, arrows, DOM-anchored connectors, brackets, callouts, rings/arcs, funnels, a chart kit (scales, axes, bars, lines, waterfall), glyphs — on a 1920×1080 canvas with a 12-column grid and themeable tokens. Ships zero-dependency scripts (system Chrome via DevTools protocol) to scaffold decks, render PNGs with automated QA (overflow, overlap, contrast, min size, word budget, card-grid detector, accent dilution, focal check, ink coverage), build contact sheets and visual-direction boards, and bundle a single-file presentation.html + vector PDF with a pixel-fidelity check. Use as stage 4 of executive-visual-storyteller, or whenever HTML slides must be built or fixed from a spec. Primitives, not templates. Not for .pptx (use the pptx skill)."
---

# HTML Slide Renderer

Turns a **slide spec** into a real slide. You compose freely with primitives; there are no
finished layouts to fill. The spec decides the composition — you decide coordinates, measure,
render, look, and fix.

## 0 · Reuse check (do once per environment)

Before building anything, check whether a compatible HTML-slides skill is installed
(`html-slides`, `frontend-slides`, reveal.js-based, or similar) under `~/.claude/skills`,
project `.claude/skills` or plugins. At install time none existed, so this renderer is the
default. If one appears later, compare: 16:9 fixed canvas, primitives for diagrams, render/QA
scripts, single-file export. Reuse it only if it matches all four; do not duplicate infrastructure.

## 1 · Scripts (zero dependencies: Node ≥ 22 + any Chrome/Chromium/Edge)

```bash
S=${CLAUDE_SKILL_DIR}/scripts
node $S/new-deck.mjs <deck> --title "Título" --direction editorial --slides 5   # scaffold (never overwrites)
node $S/new-deck.mjs <deck> --set-direction modern                              # switch theme
node $S/new-deck.mjs <deck> --update-assets                                     # refresh engine files
node $S/directions.mjs <deck> --themes editorial,modern,blueprint               # direction board from directions/preview/
node $S/render.mjs <deck> [--only 03,04] [--grid]                               # PNG + thumbs + QA + contact sheet
node $S/render.mjs --file path/slide.html --out path/slide.png                  # one-off render + QA
node $S/bundle.mjs <deck> --pdf                                                 # index.html + presentation.html + deck.pdf + fidelity
```

Chrome is auto-detected; override with `CHROME_PATH=/path/to/chrome`. If no Chrome can run,
fall back to the built-in browser pane (open the slide file, screenshot) and say so in the QA report.

## 2 · Canvas contract

- **1920 × 1080 px**, fixed. Slides scale uniformly to any viewport; they never reflow.
- **Grid**: 112 px side margins, 12 columns × 112 px, 32 px gutters (module 144).
  Column *k* starts at `P.grid.col(k) = 112 + 144(k−1)`; `P.grid.span(a,b) → {x,w}`.
- **Zones**: header at top 88 px (kicker + headline, ≤ 2 lines); content ~260–990; footer at
  bottom (source left, page right). The content zone is yours to compose asymmetrically.
- **Type roles** (never ad-hoc sizes): `.statement` 96 · `.headline` 56 · `.lead` 30 ·
  `.body` 24 · `.label` 22/600 · `.annotation` 22–23 · `.label-sm` 20 · `.source` 17 · `.metric` 220 (override size per slide when needed, keep it on the scale).
  Minimum 18 px on canvas (15 px for footer/source).
- **Tokens only** (never hex in slides): `ink ink-2 ink-3 ink-4 ink-5 rule bg surface accent
  accent-text accent-soft accent-2 neg pos highlight`. Accent = the insight, nothing else.
- **Lines**: structure 1.5 px (`hair`), connectors 2 px, emphasis 3 px, data marks as needed.

## 3 · Slide file anatomy

Start from `assets/templates/slide.html` (the scaffold creates it). Keep:
- `<main class="slide" data-slide="S03" data-composition="…" data-family="…" data-word-budget="…">`
  — composition/family from the spec (QA uses them for deck rhythm).
- Slide CSS **inside** `[data-slide="S03"] { … }` (native nesting). Never style `html/body/:root`.
- Element ids prefixed with the slide id (`s03-hub`).
- Exactly one focal element with `data-focal`.
- `<aside class="notes">` for speaker notes; `<footer class="footer">` with `.source` and `.page`.
- Drawing code in `P.draw('S03', (s, P) => { … })` after `</main>`.

## 4 · Primitives (full API: `references/primitives-api.md`)

- **Text (HTML, wraps, measurable)**: `s.label(x, y, html, {anchor, w, cls, knockout, focal})`.
- **Shapes (SVG)**: `s.line`, `s.polyline(points,{radius})`, `s.path(d)`, `s.circle`, `s.dot`,
  `s.rect`, `s.poly`, `s.ring(cx,cy,r0,r1,a0,a1)`, `s.text` (short labels only), `s.glyph(name)`, `s.image`.
- **Relations**: `s.connect(from, to, {route:'curve'|'elbow'|'straight'|'arc', fromSide, toSide,
  fromAt, toAt, arrow, tone, w, dash, label})` anchored to real element boxes;
  `s.bracket(targets, {side, style:'curly'|'square'|'line', label})`;
  `s.callout({target, at, text, w, elbow})`.
- **Declarative** equivalents in HTML: `<x-connect>`, `<x-bracket>`, `<x-callout>`.
- **Charts**: `const c = s.chart({x,y,w,h})`; `c.linear`, `c.band`, `c.gridY`, `c.axisX`, `c.axisY`,
  `c.bars`, `c.line`, `c.area`, `c.waterfall`, `c.refLine`, `c.annotate`.
- **Geometry**: `P.geo.polar/around/distribute/arc/ring/rounded/trapezoid/chevron/brace/braceH`.

## 5 · Rendering rules

1. **Implement the spec literally**: composition, focal point, hierarchy order, encodings,
   annotations, avoid list. If the spec is infeasible, say so and send it back; do not
   silently substitute a card grid.
2. **Words in HTML, geometry in SVG.** HTML text wraps and is measured by QA; SVG text is only
   for 1–3 word labels inside geometry.
3. **Anchor relations to elements** (`s.connect('#s03-a', '#s03-b')`) so they survive text
   reflow. Use explicit points only for data coordinates.
4. **Plan coordinates on the grid first** (write the column spans in a comment), then draw.
5. **Charts from data with scales**, never hand-placed bars. Direct labels, no legends, gray
   context + accent proof, one annotation at the exact data point.
6. **Hierarchy by scale, weight and tone** in the spec's order: level 1 largest/accent,
   level 4 smallest/ink-3.
7. **No emoji; icons only if they encode information** (`s.glyph`); no shadows, no gradients,
   no rounded tiles unless the spec justifies it.
8. **Knockout labels** (`knockout:true`) where a label sits on a line.
9. Construction technique for each grammar family: `references/construction-notes.md`.
   Type, tokens and custom themes: `references/tokens-and-typography.md`.

## 6 · Loop

Write/modify `slides/NN.html` → `render.mjs <deck> --only NN` → **Read the PNG** (and the thumb)
→ fix → re-render. Never report a slide as done from HTML alone: it is done when its render has
been looked at and `slide-critic` passes it. After all slides pass: `bundle.mjs <deck> --pdf`
and check the fidelity lines (≤ 0.5% differing pixels per slide).

## 7 · Troubleshooting

- *Connector lands in the wrong place* → the target box changed after drawing; draw inside
  `P.draw` (runs after fonts load), not in inline scripts.
- *Text overflow/clipping errors* → cut words (spec budget), don't shrink below the type scale.
- *Fonts look like fallbacks* → check `assets/fonts/fonts.css` is linked first and the family
  name matches the theme.
- *Bundle differs from render* → slide CSS was not wrapped in `[data-slide]` or targets
  `.slide` directly; see the bundle warnings.
