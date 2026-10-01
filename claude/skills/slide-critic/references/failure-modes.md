# Failure modes — symptom → diagnosis → move

| Symptom in the render | Diagnosis | Move | Verdict |
|---|---|---|---|
| Row/grid of equal boxes with text | Relationship not decided | Name the verb; pick from semantic-map | RECOMPOSE |
| Blind read ≠ takeaway | Focal on the wrong object, or wrong composition | Re-rank hierarchy; if the relationship itself is wrong, new composition | RECOMPOSE / PATCH |
| Everything the same size | No hierarchy decision | Scale focal ×1.5–2; demote context to `ink-4` | PATCH |
| Chart + paragraph beside it | The chart doesn't carry the claim | Annotate the proof point on the chart; move paragraph to notes | PATCH |
| Headline repeats the axis names | Topic title | Rewrite as conclusion (storyline) | PATCH (title) |
| Legend far from the data | Placement failure | Direct labels | PATCH |
| Accent everywhere | Emphasis inflation | Accent only on the insight; context gray | PATCH |
| Lines cross labels | Knockout missing or bad routing | `knockout:true`, change `fromAt/toAt`, route `elbow` | PATCH |
| Arrow spaghetti | Too many relations shown | Keep the relations the message needs; others dashed or removed | PATCH / RECOMPOSE |
| Tiny footnotes carry the argument | Evidence hidden | Promote the key number into an annotation | PATCH |
| Canvas filled edge to edge | Fill-the-space reflex | Remove 30%; restore margins; whitespace as structure | PATCH |
| Symmetric composition for asymmetric content | Symmetry not earned | Reposition by importance | PATCH / RECOMPOSE |
| Decorative icons | Icons don't encode | Delete | PATCH |
| Framework that needs a legend | Encoding too clever | Label the geometry directly or simplify encodings | PATCH |
| Stack of identical boxes (`box-stack`) | Layers without relations | Show what flows between layers, ownership, or the missing layer; else it's a list | RECOMPOSE |
| Slide looks like the previous one | Rhythm failure | Different family for one of them | RECOMPOSE |
| Three dense slides in a row | No breather | Insert/convert a statement or hero metric | Deck-level |
| Text overflow | Too many words for the idea | Cut words (don't shrink) | PATCH |
| Near-miss alignment (x=112 vs 118) | Hand-placed coordinates | Snap to `P.grid.col()` | PATCH |
| Low contrast on accent text | Accent used for small text | Use `accent-text` or ink | PATCH |
| Metaphor needs explaining | Decorative metaphor | Replace with a structural composition | RECOMPOSE |
| The takeaway's proof is the smallest object on the slide | Hierarchy inverted vs the story | Make the proof the dominant encoding (e.g. tint the rings by budget) | RECOMPOSE |
| A tint/gradient that means nothing pulls the eye | Meaningless visual variable | Make it encode something, or flatten it | PATCH / RECOMPOSE |
| Headline verb contradicted by the exhibit | Overclaim | Rewrite the verb to what the data shows | PATCH |
| Takeaway only in the speaker notes | Argument not on the page | Add one anchored annotation | PATCH |
| Same concept, two names across slides | Vocabulary drift | Unify names deck-wide | PATCH |
| Accent on kickers / section labels | Frame treated as insight | Kicker in ink-3 | PATCH (theme) |
| Dashed connectors in a waterfall while dashes mean target | Encoding collision | Solid thin connectors | PATCH |
