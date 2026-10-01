# Critic checklist

Automated = covered by `render.mjs` (qa-summary.md). Visual = requires looking at the render.

## Story

| Check | How to test |
|---|---|
| Takeaway understood in 3 s | Visual: blind read at thumbnail size matches the spec `takeaway` |
| Headline is a conclusion | Visual/text: subject + verb + so-what; not a topic. Automated hint: `headline-topic` |
| One question answered | Visual: could the slide be split? Is there a second idea competing? |
| One dominant idea | Visual: one focal; automated: `no-focal`, `many-focals` |
| Headline proved by the body | Visual: does the visual show the claim, or something adjacent? |
| Headline verb literally true | Visual: does the exhibit contradict the verb ("cierran" vs bars showing 40% recovered)? |
| Takeaway on the page | Compare spec `takeaway` with the canvas: if it only lives in the notes, add it |
| Takeaway's proof is dominant | The object that proves the takeaway must not be the smallest thing on the slide |

## Visual

| Check | How to test |
|---|---|
| Clear focal point | Visual: squint test on the thumb; automated: focal area/size in the metrics line |
| Visual hierarchy = conceptual hierarchy | Visual: rank what you see 1→4 and compare with spec `visual_hierarchy` |
| Idea visualized, not decorated | Visual: does geometry enact the relationship verb (converge/leak/nest…)? |
| Cards used out of laziness? | Automated: `card-grid`, `box-stack`; Visual: is there an order/flow/hierarchy the boxes hide? |
| Enough whitespace | Automated: `dense` (ink > 34%); Visual: does it breathe? is empty space structural? |
| Redundant elements | Visual: delete-test each object — does meaning drop? |
| A smarter composition exists? | Visual: compare against `alternatives_considered`; would the runner-up be clearer now that you see it? |
| Relationships drawn, not implied by proximity | Visual |
| Accent marks only the insight | Automated: `accent-diluted`; Visual |

## Content

| Check | How to test |
|---|---|
| Can 30% of the text go? | Automated: words vs budget; Visual: read each block and strike what the visual already says |
| Text that belongs in notes | Automated: `long-paragraph`; Visual |
| Evidence that doesn't serve the argument | Visual: each number/label must support the headline |
| Claims without support | Compare with storyline §7; unsupported claims need a caveat or removal |
| Source line present for data | Visual: footer `.source` |

## Technical

| Check | How to test |
|---|---|
| Overflow / clipping / truncation | Automated: `text-clipped`, `text-spill`, `text-truncated`, `text-offcanvas` |
| Text overlaps text | Automated: `text-overlap` |
| Text crossed by lines | Visual (use `knockout` labels) |
| Contrast | Automated: `low-contrast`, `contrast-unknown` |
| Legibility / minimum sizes | Automated: `font-too-small` |
| Alignment | Automated: `near-miss-alignment`; Visual: `render.mjs --grid` overlays the 12-col grid |
| Density | Automated: words, ink %, text blocks |
| Consistency of type | Automated: `type-scale`, `font-families` |
| Hero numbers intact | Automated: `metric-wraps` ("$910" / "M" is an error) |
| Runtime | Automated: `draw-error`, `js-exception`, `asset-failed`, `broken-image` |
| Decoration | Automated: `emoji`, `gradient`, `shadow`, `border-inflation`, `rounded-boxes`, `icons`, `bullets` |

## Deck

| Check | How to test |
|---|---|
| Repetition | Automated: `repeat-composition`, `repeat-family`, `low-variety`; Visual: contact sheet |
| Rhythm | Visual: dense/light alternation; automated: `no-breather` |
| Density outliers / boring slides | Automated: `density-outlier`; Visual: which thumbnail would you skip? |
| Card grids across deck | Automated: `deck-card-grids` (max 1) |
| System consistency | Visual: headline position/size, margins, kicker, footer, accent meaning, line & annotation language identical across slides |
| Story flow | Read the headlines in order under the contact sheet: do they argue? |
| Encoding contract | Audit ink / outline / accent / dashed / tint on every slide, incl. kickers, connectors, reference lines (deck-rhythm.md) |
| Vocabulary | One name per concept across slides (leaks, areas, metrics) |
| No internal IDs | Board-facing text never says "S02", "v2" or file names |
| The ask is justified | Each part of the final ask is proven by a visible (not note-only) element earlier in the deck |
