# Deck folder contract

```text
<deck>/
  deck.json                 title, lang, direction, created
  storyline.md              stage 1 — audience, governing thought, pyramid, sequence, slide briefs, cuts
  visual-direction.md       stage 2–3 — reference learning, directions, decision, composition plan
  slide-specs/Sxx.yaml      stage 3 — one spec per slide (IR consumed by the renderer)
  slides/NN.html            stage 4 — one standalone slide per file (1920×1080)
  assets/                   engine (core.css, primitives.js, deck.js), fonts/, themes/, theme.css (active direction), images
  directions/preview/       the two preview slides used for the direction board
  directions/renders/       <theme>-<NN>.png
  directions/direction-board.png
  renders/NN.png            full-size renders · NN.vK.png kept before each revision
  renders/thumbs/NN.png     480px thumbnails (blind read / squint test)
  renders/alt/              alternative compositions
  renders/contact-sheet.png all slides together (rhythm, repetition, density)
  renders/qa.json           machine QA · renders/qa-summary.md human QA
  renders/bundle-fidelity.txt
  renders/deck.pdf          vector PDF, one slide per page
  qa-report.md              stage 5 — critic verdicts, scores, iteration log, deck review
  index.html                deck viewer (links assets/)
  presentation.html         single self-contained file (fonts, CSS, JS, slides inline)
```

Conventions:
- Slide ids `S01…` match file numbers `01.html…`; element ids are prefixed (`s03-…`).
- Slide CSS nested in `[data-slide="Sxx"] { … }`; never targets html/body/:root.
- Only tokens in slides (no hex). Only local assets (`../assets/…`).
- Illustrative data is labelled as such in the source line.
