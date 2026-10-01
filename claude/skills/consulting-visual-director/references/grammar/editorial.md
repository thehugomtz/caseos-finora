# Editorial compositions

These are about *pacing and emphasis*. They make a deck feel designed rather than generated:
a single sentence given a whole canvas, a visual that is allowed to dominate, deliberate asymmetry.

### `single_big_statement`
- **Use when** the governing thought, a pivot in the story, or a decision request deserves the
  whole canvas (covers, section openers, the ask).
- **Anatomy** one sentence at display size (72–110px), left-aligned on the grid, max ~14 words;
  a kicker; optionally one small supporting fact or a single hairline element that echoes the
  idea (a gap, a break, a direction).
- **Encode** type scale does all the work; accent on one word or the supporting fact only.
- **Focal** the sentence.
- **Pitfalls** centered text over a stock photo; adding bullets "to fill".
- **Build** `.statement` in a column span of 8–10 columns; generous top offset (asymmetric vertical placement, not centered).

### `dominant_visual_plus_annotation`
- **Use when** one exhibit proves the point and needs 2–3 sentences to be read correctly.
- **Anatomy** exhibit on 8–9 columns; annotation column on 3–4 columns aligned to the exhibit's
  key features (leaders optional).
- **Focal** the exhibit's key feature.

### `split_narrative`
- **Use when** the argument (left) and the evidence (right) must be read together.
- **Anatomy** asymmetric split (5/7 or 4/8); the left carries the claim in 2–3 short statements,
  the right the exhibit.
- **Pitfalls** 50/50 symmetric halves with equal weight.

### `asymmetric_composition`
- **Use when** creating tension and a reading path: big element off-centre, small elements
  balancing it; generous negative space.
- **Guideline** focal object on the 1/3 or 2/3 lines; whitespace ≥ 30% of the canvas.

### `visual_metaphor`
- **Use when** — only when — the metaphor maps 1:1 to the structure of the argument (a gap that is
  literally a gap between two measured quantities; a bridge whose spans are the steps).
- **Pitfalls** icebergs, rockets, puzzle pieces, mountains, lightbulbs. If the metaphor needs
  explaining or decorates, drop it.

### `full_slide_framework`
- **Use when** the framework *is* the message (a model introduced once and reused as a tracker).
- **Anatomy** the framework uses the full content area; labels integrated into the geometry; one
  line of explanation.
- **Reuse** later slides can show a miniature of it as a tracker, with the current part highlighted.

### `progressive_build`
- **Use when** presenting live and the logic must unfold (context → tension → answer).
- **Build** add `data-build="1..n"` to elements; the deck viewer reveals them step by step;
  renders and PDF always show the final state, which must stand alone.

### `voice_quote`
- **Use when** a verbatim (customer, executive, field) proves a qualitative point.
- **Anatomy** the quote large (40–56px, display face), attribution small, and the implication
  written beneath as the "so what". ≤ 2 quotes per slide.
