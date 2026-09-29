"""Hugo's format guide for the deck: fonts and colors in plain terms become renderer tokens, with contrast checked and
fonts made available offline (Google Fonts fetch is simulated here)."""
import re
import shutil

import pytest
import yaml

from caseos import slidestyle, story, storyteller

BASE = """@layer theme {
  :root {
    --font-display: 'Newsreader', Georgia, serif;
    --font-text: 'Inter', Arial, sans-serif;
    --bg: #ffffff; --ink: #0b1220; --accent: #1846f5;
  }
}"""


def tok(css, name):
    """Value of the last declaration of a token (the override wins over the base theme)."""
    return re.findall(rf"{re.escape(name)}\s*:\s*([^;]+);", css)[-1].strip()


def test_colors_and_fonts_become_tokens_with_contrast_checked():
    css, notes = slidestyle.theme_css(BASE, {"title_font": "Playfair Display", "text_font": "Inter",
                                             "colors": {"background": "#FFFFFF", "text": "#1e2a5a", "accent": "#ff9f1c"}}, "editorial")
    assert "--font-display: 'Playfair Display', Georgia" in css and "--font-text: 'Inter'" in css
    assert "--bg: #ffffff" in css and "--ink: #1e2a5a" in css and "--accent: #ff9f1c" in css
    at = tok(css, "--accent-text")
    assert slidestyle.contrast(at, "#ffffff") >= 4.5                       # orange is too light for small text: adjusted
    assert any("acento" in n for n in notes)
    ink3 = tok(css, "--ink-3")
    assert slidestyle.contrast(ink3, "#ffffff") >= 4.5


def test_unreadable_text_color_is_fixed_and_reported():
    css, notes = slidestyle.theme_css(BASE, {"colors": {"background": "#ffffff", "text": "#bbbbbb"}}, "editorial")
    ink = tok(css, "--ink")
    assert slidestyle.contrast(ink, "#ffffff") >= 7 and notes


def test_bad_color_is_rejected_in_plain_words():
    with pytest.raises(ValueError):
        slidestyle.normalize({"colors": {"accent": "naranja"}})


def test_font_fetch_writes_renderer_format(tmp_path):
    deck = tmp_path / "deck"
    (deck / "assets" / "themes").mkdir(parents=True)
    (deck / "assets" / "fonts").mkdir(parents=True)
    (deck / "assets" / "themes" / "editorial.css").write_text(BASE)
    (deck / "assets" / "fonts" / "fonts.css").write_text("@font-face{font-family:'Inter';src:url('Inter.woff2')}\n")

    def fake_fetch(family, dest):
        (dest / "Fake.woff2").write_bytes(b"wOF2")
        return [f"@font-face{{font-family:'{family}';font-style:normal;font-weight:400 900;font-display:block;src:url('Fake.woff2') format('woff2');}}"]
    out = slidestyle.apply_to_deck(deck, {"title_font": "Playfair Display", "text_font": "Inter"}, "editorial", fetch=fake_fetch)
    fonts_css = (deck / "assets" / "fonts" / "fonts.css").read_text()
    assert "font-family:'Playfair Display'" in fonts_css and out["fonts"]["text_font"]["source"] == "renderer"
    assert (deck / "assets" / "themes" / "caseos.css").exists()

    def failing(family, dest):
        raise ValueError("no existe")
    out = slidestyle.apply_to_deck(deck, {"title_font": "Fuente Inventada"}, "editorial", fetch=failing)
    assert any("Fuente Inventada" in n for n in out["notes"]) and out["style"]["title_font"] == ""


@pytest.mark.skipif(not ((storyteller.renderer_dir() / "scripts" / "new-deck.mjs").exists() and shutil.which("node")),
                    reason="Executive Visual Storyteller no instalado en ~/.claude/skills")
def test_handoff_carries_the_format_guide(case):
    from tests.test_handoffs import _accepted_evidence, _package
    f, t = _accepted_evidence(case)
    story.apply_package(case, _package(f, t), actor="cos")
    meta = case.meta()
    meta["phases"]["story"]["status"] = "ready"
    case.save_meta(meta)
    rec = storyteller.prepare(case, direction="editorial", critic=False, style={
        "title_font": "Newsreader", "text_font": "Inter", "colors": {"background": "#ffffff", "text": "#1e2a5a", "accent": "#e4572e"},
        "notes": "Sobrio, tipo consultora, mucho blanco."})
    deck = case.root / rec["path"]
    theme = (deck / "assets" / "theme.css").read_text()
    assert "--ink: #1e2a5a" in theme and "--accent: #e4572e" in theme
    assert rec["direction"] == "caseos" and rec["style"]["style"]["notes"].startswith("Sobrio")
    handoff = yaml.safe_load((deck / "caseos-handoff.yaml").read_text())
    assert handoff["brand_system"]["style"]["colors"]["accent"] == "#e4572e"
    assert case.meta()["slides_style"]["text_font"] == "Inter"                              # remembered for the next deck
