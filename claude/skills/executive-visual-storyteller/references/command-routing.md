# Command routing

| User says (examples) | Stage / skill | Procedure | Output |
|---|---|---|---|
| "Convierte este documento en un deck ejecutivo" · "hazme la presentación" | Full pipeline | Stages 0→6 with gates G1–G4 | deck folder complete |
| "Arma solo la narrativa" · "¿qué historia cuento?" | executive-storyline | Stages 0–1 | storyline.md |
| "Revisa si estoy comunicando una conclusión o sólo mostrando datos" | executive-storyline (tests) + slide-critic (story) | For each slide: headline test, so-what test, does the body prove the title; rewrite titles | table: slide · current title · verdict · proposed title |
| "Esta slide está demasiado AI" · "se ve genérica" | slide-critic → consulting-visual-director | Name the smell (anti-slop.md); name the relationship; RECOMPOSE from a *different family*; render; before/after | new spec + render + 3-line rationale |
| "Busca una composición más editorial" | consulting-visual-director | Prefer editorial family (statement, dominant visual + annotation, asymmetric), fewer objects, more whitespace, serif display if the direction allows | new spec + render |
| "Convierte esta idea en un framework visual" | consulting-visual-director | Find MECE dimensions/stages; name the verb; pick family; name the framework | spec + render |
| "Haz esta slide más McKinsey-like en estructura, no en branding" | consulting-visual-director + renderer | Action title; one dominant exhibit; direct labels; annotated proof; source line; tracker/kicker; neutral palette + one highlight; no firm branding | revised slide |
| "Genera tres alternativas visuales para esta slide" | consulting-visual-director + renderer | 3 specs from 3 different families; render to `renders/alt/Sxx-a/b/c.png`; show side by side with one line each; recommend one | 3 renders + recommendation |
| "Reduce esta slide 40% sin perder el argumento" | executive-storyline + renderer | Keep message + proof; cut words/objects to ≤ 60%; move detail to notes; re-render; report words and ink before/after | revised slide + counts |
| "Haz que esta relación sea evidente visualmente" | consulting-visual-director | Replace proximity with connection/containment/alignment/scale; accent the relation | revised slide |
| "Propón direcciones visuales" · "usa estas referencias" | consulting-visual-director (direction + reference modes) | Reference learning → 2–3 directions → preview board → stop for choice | visual-direction.md + board |
| "Revisa el deck completo" · "QA" | slide-critic (+ independent-slide-critic) | Render all, blind reads, checklist, deck review | qa-report.md |
| "Métricas: CAC, LTV, churn, ARPU, ARR" (a list) | executive-storyline | Ask/propose the relationship (unit economics tree, growth bridge, efficiency frontier) before any slide | proposed architecture + question |
| "Exporta a PDF" · "dame un solo archivo" | html-slide-renderer | bundle.mjs --pdf | presentation.html + deck.pdf |
| "Publícalo / compártelo" | Artifact tool | Publish presentation.html (private by default) — only on request | link |
