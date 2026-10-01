# Visual directions

A **direction** is a complete visual *system*, not a color palette: type pairing and hierarchy,
color relationships, line treatment, shape language, chart language, annotation language,
density and composition tendencies. Directions are expressed as a theme CSS (tokens + a few
language rules) in `assets/themes/<name>.css`, so the same slide can be rendered under each
direction and compared on real content.

## Protocol

1. **Inputs**: audience (board, C-suite, investors, working team), setting (presented vs
   read-ahead), brand constraints, references (run `reference-analysis.md` first if any).
2. **Propose 2–3 directions** that are genuinely different on at least three axes (type, color
   temperature, line/shape language, density). Each gets: a name, a one-line intent, the token
   table, the language rules, when it fits, the risk.
3. **Preview on real content**: spec and render two representative slides — one **data-heavy**
   (chart/economics) and one **framework-heavy** (system/process/operating model) — into
   `directions/preview/` (they link `../../assets/theme.css`). Then:
   `node ${CLAUDE_SKILL_DIR}/../html-slide-renderer/scripts/directions.mjs <deck> --themes editorial,modern,blueprint`
4. **Show `directions/direction-board.png`** and recommend one (with the reason tied to audience
   and content). **Stop for the user's choice** before rendering the deck. In autonomous runs,
   choose and record why.
5. **Record** the decision in `visual-direction.md` and apply it with
   `new-deck.mjs <deck> --set-direction <name>`.

## Default directions

### A · Editorial Consulting (`editorial`)
- **Intent**: the calm authority of a top-tier strategy report. Diagrams dominate; type is quiet
  and precise.
- **Type**: serif display headlines (Newsreader, weight ~420, tight tracking) + grotesk text
  (Inter). Headline:body ratio ≈ 2.3:1. Kicker in small caps, `ink-3` (frame, never accent).
- **Color**: white canvas; deep navy ink (#0b1220); grays for structure; one electric blue
  accent (#1846f5) for the insight only.
- **Line**: 1.5–2px hairlines, round caps, small filled arrowheads; dashed = target / future;
  outline (no fill) = potential or paper value.
- **Shape**: no radius; open shapes, rules instead of boxes; circles for nodes and markers.
- **Charts**: no chart borders, horizontal gridlines only in `rule`, direct labels, one accent series.
- **Annotation**: 22–23px grotesk, leader lines with a small dot at the data point.
- **Density**: low–medium; whitespace ≥ 35%.
- **Fits**: boards, C-suite, strategy recommendations. **Risk**: can feel austere for sales contexts.

### B · Modern Strategy (`modern`)
- **Intent**: confident, contemporary, asymmetric — a strategy boutique rather than a bank.
- **Type**: bold slightly expanded grotesk headlines (Archivo 700, wdth ~108%), same family for text.
- **Color**: warm off-white (#f4f1ec), near-black ink, one vivid vermilion accent (#ff4b1f) —
  use `--accent-text` (#c2320e) for small accent text (contrast).
- **Line**: heavier structure (2.5–3px), square-ish geometry.
- **Shape**: geometric blocks allowed when they encode (bars, bands); ink square in the kicker.
- **Charts**: thick bars, few gridlines, big numeric labels.
- **Density**: medium; strong asymmetry.
- **Fits**: investors, transformation programs, internal strategy. **Risk**: too loud if the accent spreads.

### C · Technical Blueprint (`blueprint`)
- **Intent**: architecture-diagram precision for technical or operating-model content.
- **Type**: IBM Plex Sans + Plex Mono for labels/kickers/footers (uppercase tracking).
- **Color**: dark navy canvas (#0a1628) with a subtle 48px grid; light ink; bright blue accent
  (#3d8bff) and cyan secondary (#62e0d9) — secondary used for a second *category*, never for emphasis.
- **Line**: 1.5px technical lines, dimension-line conventions (ticks, measurement brackets).
- **Shape**: small radius (2px), node markers, dashed boundaries for systems.
- **Density**: controlled medium-high; mono labels keep it legible.
- **Fits**: CTO/CIO audiences, architecture and platform decisions, data/AI operating models.
  **Risk**: dark slides print badly; pair with a light variant for read-ahead PDFs.

## Building a custom direction

Copy the closest theme to `assets/themes/<name>.css` and change **tokens** (fonts from the
vendored set or OFL equivalents; colors; weights; structure width; radius) and **language rules**
(kicker treatment, annotation face, chart defaults). Check contrast: `--ink-3` on `--bg` ≥ 4.5:1;
use `--accent-text` when the accent fails small-text contrast. Keep the token names — slides
reference roles (`accent`, `ink-3`), never hex values.

## Decision record (in visual-direction.md)

```yaml
direction:
  chosen: editorial
  why: "board audience, read-ahead + presented; content is framework-heavy; editorial lets diagrams lead"
  rejected:
    modern: "strong but the vermilion competes with the leak markers"
    blueprint: "fits the AI topic but dark slides print badly for the board pack"
  adjustments: ["accent #1846f5 kept only for leaks/insights", "annotation size 23px"]
```
