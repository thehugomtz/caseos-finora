# Tokens, typography and themes

## Type scale (canvas px ≈ 2 × pt on a 13.33in slide)

| Role | Class | Size | Use |
|---|---|---|---|
| Hero number | `.metric` | 160–260 | one number per slide |
| Statement | `.statement` | 80–110 | governing thought, section openers |
| Headline | `.headline` | 56 | action title, ≤ 2 lines |
| Sub/lead | `.lead` / `.subhead` | 30 | one supporting sentence |
| Body | `.body` | 24 | short explanations (rare on canvas) |
| Label | `.label` | 22 / 600 | object names in diagrams |
| Annotation | `.annotation` | 22–23 | the "so what" at a data point |
| Small label | `.label-sm` | 20 | axes, secondary descriptors |
| Source | `.source` (footer) | 17 | sources, notes |
| Kicker | `.kicker` | 20 caps | section/tracker |

Rules: never below 18px on canvas (15 footer). ≤ 6 distinct sizes per slide. Numbers with
tabular lining figures (`.num`). Sentence case for headlines; caps only for kickers/tags.

## Headlines

Conclusion-led, ≤ ~15 words, ≤ 2 lines at 56px across ≤ 1560px. `text-wrap: balance` is on.
Emphasis inside a headline: prefer none; at most one phrase in `accent-text` or `.hl` marker.

## Number formatting (es-MX default)

`P.fmt(1200) → "1,200"`, `P.fmt(-310, {sign:true}) → "−310"`, `P.fmt(0.24*100, {suffix:'%'})`.
Currency: `$1,200 M` / `$1.2 mil M` — pick one convention per deck and state units in the label
or axis title, not on every number.

## Color roles

| Token | Role |
|---|---|
| `ink` | primary text, totals, key structure |
| `ink-2` | secondary text |
| `ink-3` | tertiary text, connectors, axis labels (≥ 4.5:1 on bg) |
| `ink-4` | context marks (gray bars, secondary lines) |
| `ink-5` | faint fills (ring bands, phase bands) |
| `rule` | hairlines, gridlines |
| `surface` | rare panel fill |
| `accent` | the insight (marks) |
| `accent-text` | accent for small text when `accent` fails contrast |
| `accent-soft` | faint accent fill (target quadrant, highlight band) |
| `accent-2` | a second *category* color, never a second emphasis |
| `neg` / `pos` | only when sign is the message |

## Custom theme (new direction)

1. Copy the closest theme to `assets/themes/<name>.css`; keep it inside `@layer theme`.
2. Change tokens only: fonts (vendored: Newsreader, Inter, Archivo, IBM Plex Sans/Mono — or add
   OFL fonts to `assets/fonts/fonts.css`), colors, weights, `--structure-w`, `--radius`.
3. Add at most a few language rules (kicker treatment, annotation face, metric weight).
4. Contrast check: `ink-3` on `bg` ≥ 4.5:1; if `accent` < 4.5:1 for small text, set `accent-text`.
5. Render the direction previews with `directions.mjs` before adopting it.
