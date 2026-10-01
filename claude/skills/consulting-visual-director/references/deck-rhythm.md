# Deck rhythm and system consistency

**Visual consistency does not mean layout repetition.** The system repeats (type, spacing, color,
line, annotation, chart and footer conventions); the compositions vary with the ideas.

## Composition plan (write it in visual-direction.md before rendering)

| # | Slide | Role | Composition | Family | Density | Focal |
|---|---|---|---|---|---|---|
| 01 | S01 | governing thought | single_big_statement | editorial | light | statement |
| 02 | S02 | evidence | value_leakage | economics | dense | largest leak |
| … | | | | | | |

## Rules

- No composition twice in a row; no family three times in a row.
- ≥ 60% distinct compositions in decks of 5+ slides.
- Max one card grid per deck (and it must be justified in its spec).
- After two dense slides, a breather (statement, hero metric, dominant visual with little text).
- The story's pivot (complication → resolution) gets a visual change of pace.
- Sections: a kicker/tracker convention used consistently (same position, same style).
- A framework introduced once can return as a miniature tracker on later slides.

## Deck-wide encoding contract

Declare it once in `visual-direction.md` and audit it on EVERY slide — including kickers,
connectors, reference lines and outlines, where it most often breaks silently:

| Visual | Means (default) | Never use it for |
|---|---|---|
| ink, solid | real / captured / actual value | potential or paper value |
| outline (no fill) | potential, identified, not-yet-real value | real value |
| accent | the insight (in a diagnosis deck: value lost / friction) | frames, kickers, section labels |
| dashed | target / future / does not exist yet | running totals, connectors, gridlines |
| tint (opacity) | a quantity (e.g. budget share) or de-emphasis of context | decoration; a tint that means nothing still pulls the eye |

## System checklist (must be identical across slides)

- Margins and grid (112px sides, 12 × 144 module), header zone, footer zone.
- Headline size/weight/leading (except statement slides, which use `.statement`).
- Kicker style; footer (source left, page right); source-line wording ("Fuente: …").
- Type scale roles (label, annotation, label-sm) — no ad-hoc sizes.
- Accent meaning (always "the insight"), `neg`/`pos` meanings.
- Line weights per role (structure hairline, connectors 2px, emphasis 3px), arrowhead style.
- Annotation language: leader + dot, or bracket + label — pick one family per deck.
- Chart language: gridline treatment, axis labels, number formatting (es-MX: `1,200`, `24%`, `$1.2 mil M`).
