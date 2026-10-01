# Scoring rubric (1–5) and verdicts

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **Story** | Topic title; body doesn't prove anything; two ideas | Conclusion title, but the body proves it only partially or needs the presenter | Title is a sharp conclusion; the body proves it alone; one idea |
| **Focal & hierarchy** | Nothing dominates, or the wrong thing does | Focal exists but competes with 1–2 elements; hierarchy partly matches the spec | The eye lands on the takeaway in < 3 s at thumbnail size; 1→4 order matches the spec |
| **Visualization fidelity** | Decorated text (cards, icons, bullets in boxes) | A reasonable diagram, but the relationship is implied by proximity or labels | Geometry enacts the relationship verb; remove the words and the structure still says it |
| **Economy** | > 1.5× word budget, redundant objects, legends | Within budget but 20–30% could still go | Every word and object earns its place; notes carry the rest |
| **Craft** | ✖ errors (overflow, overlap, contrast), misalignments | No errors; some near-misses, crowded labels, uneven spacing | Clean alignment to grid, consistent spacing, crisp labels, no collisions |
| **System** | Breaks the deck's type/color/line conventions | Minor deviations (a stray size, a second accent use) | Indistinguishable system; composition varies, language doesn't |

## Verdict rules

- **RECOMPOSE** — any of: Story ≤ 2 · Fidelity ≤ 2 · Focal ≤ 2 · unjustified card grid ·
  blind read ≠ takeaway. Output: the new composition id, its family, and the reason
  ("the idea is a leak, not a list → value_leakage"). The visual director writes a new spec.
- **PATCH** — all ≥ 3 but: any ✖ error, or Craft ≤ 3, or Economy ≤ 3. Output: an ordered list
  of concrete edits. Re-render and re-score only the affected dimensions + a fresh blind read.
- **PASS** — all ≥ 4, zero ✖, all ⚠ fixed or justified in writing.

## Examples of verdict statements

- "RECOMPOSE — blind read says 'there are four areas of AI'; takeaway is 'value leaks after the
  pilot'. The row of four boxes hides the sequence and the magnitudes. → value_leakage
  (economics): bridge from identified to captured value, largest leak in accent."
- "PATCH — (1) annotation on the Q4 bar collides with the value label: move annotation to
  x=1380, leader elbow; (2) cut subtitle from 31 to 14 words; (3) the three lane labels sit at
  x=112/116/112 → snap to 112."
- "PASS — focal lands on the 24% captured bar in the blind read; all flags resolved; `sparse`
  justified (breather after two dense slides)."
- "RECOMPOSE — blind read: 'the loss sits in operation and institution'. Takeaway: 'we invest in the
  layer that loses least'. The takeaway's proof (a budget dumbbell) is the smallest object, and a
  ring tint that means nothing pulls the eye to technology. → same family, new encoding: tint the
  rings by budget share (money in the core), keep the leak markers on the rim, headline carries both."
