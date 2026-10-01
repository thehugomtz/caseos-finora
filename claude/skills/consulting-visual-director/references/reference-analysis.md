# Reference analysis — screenshots → abstract rules

Goal: learn *why* reference slides work and turn that into transferable rules and tokens.
Never copy a slide, clone a signature layout, reuse a logo, or reproduce a proprietary brand
(palette + typeface + layout signature). Proprietary typefaces are mapped to OFL equivalents.

## Procedure

1. **Look at every image** with the Read tool. For each, note what kind of slide it is
   (framework, chart, statement, process…) and the one thing it does well.
2. **Measure, per dimension** (estimate proportions against the canvas width W and height H):

| Dimension | What to extract |
|---|---|
| Typography hierarchy | headline size as % of H; headline:body ratio; weights; case; tracking; serif/sans roles; line length |
| Spacing | side margins as % of W; gutter; vertical rhythm; distance headline → content |
| Density | words on canvas; number of visual objects; share of canvas with ink |
| Composition | dominant visual's share of canvas; symmetric vs asymmetric; reading path; where the focal point sits |
| Color relationships | background; ink levels; how many accents; what the accent marks; saturation |
| Line treatment | weights; caps; dashes; arrowheads; connectors straight/curved/orthogonal |
| Shape language | sharp vs rounded; filled vs outlined; boxes vs rules; node markers |
| Chart style | gridlines; axes; labels direct vs legend; bar thickness; annotation style |
| Whitespace | where the empty space is and whether it is structural |
| Information hierarchy | what is read 1st/2nd/3rd; how the takeaway is signalled |

3. **Write rules**, abstract and numeric where possible:

```yaml
reference_learning:
  sources: ["ref-01.png (framework)", "ref-02.png (annotated chart)"]
  rules:
    - "large conclusion-led serif headline, ~5% of canvas height, ≤ 2 lines"
    - "diagram dominates canvas (≥ 60% of content area)"
    - "thin blue connectors (≈1.5px), small filled arrowheads"
    - "few visual objects (≤ 12), labels integrated into the diagram"
    - "high whitespace (≥ 35%), asymmetric placement of the focal object"
    - "one accent color used only for the insight; everything else in 3 grays"
    - "charts without borders; direct labels; one annotated data point"
  tokens:
    --font-display: "serif, transitional/modern (map: Newsreader)"
    --accent: "#1a4cff-ish electric blue"
    --structure-w: 1.5px
  composition_tendencies: ["dominant_visual_plus_annotation", "concentric/system diagrams", "asymmetric statements"]
  do_not_copy: ["the firm's logo and tracker style", "exact layout of ref-03"]
```

4. **Map rules → direction**: tokens into a theme CSS; composition tendencies into the
   visual-director's candidate preferences; density into the default `text_budget`.
5. **Check for conflicts** between references (e.g. one dense, one sparse) and state which wins
   and why.

## Anti-cloning checklist

- [ ] No logo, trademark, firm name or tracker imitation.
- [ ] No 1:1 reproduction of any reference layout (positions, proportions and content together).
- [ ] Proprietary fonts mapped to OFL equivalents.
- [ ] A brand palette reused only if it is the user's own brand.
- [ ] Rules are stated as principles that would produce *different* slides for different content.
