"""Hugo's format guide for the deck, in plain terms: title font, text font, a few colors and notes.

It becomes a custom theme for the existing html-slide-renderer: the chosen direction's theme plus token overrides
(fonts, background, ink scale, accent), exactly the "custom theme" path of the renderer's tokens-and-typography guide.
Fonts the renderer already vendors are used as they are; any other family is fetched from Google Fonts (OFL) into the
deck's assets/fonts so the bundled presentation.html stays self-contained. Contrast is checked (WCAG) and adjusted,
and every adjustment is reported back to Hugo.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from pathlib import Path

VENDORED = ["Newsreader", "Inter", "Archivo", "IBM Plex Sans", "IBM Plex Mono"]
SUGGESTED = ["Newsreader", "Inter", "Archivo", "IBM Plex Sans", "Playfair Display", "Lora", "Merriweather", "Source Serif 4",
             "Fraunces", "Libre Baskerville", "DM Serif Display", "Cormorant Garamond", "Montserrat", "Poppins", "DM Sans",
             "Space Grotesk", "Work Sans", "Manrope", "Plus Jakarta Sans", "Roboto", "Open Sans", "Lato", "Nunito Sans", "Raleway",
             "Outfit", "Sora"]
SERIFS = {"Newsreader", "Playfair Display", "Lora", "Merriweather", "Source Serif 4", "Fraunces", "Libre Baskerville",
          "DM Serif Display", "Cormorant Garamond"}
COLOR_KEYS = {"background": "Fondo", "text": "Texto", "accent": "Acento", "accent_2": "Acento 2"}
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def _ssl_context():
    """python.org builds on macOS ship without system CA roots; certifi (installed with httpx) provides them."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _get(url: str, timeout: int) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout, context=_ssl_context()).read()


# ------------------------------------------------------------------------------------------ input
def normalize(style: dict | None) -> dict:
    s = style or {}
    colors = {}
    for k in COLOR_KEYS:
        v = ((s.get("colors") or {}).get(k) or "").strip()
        if v:
            if not re.fullmatch(r"#?[0-9a-fA-F]{3}|#?[0-9a-fA-F]{6}", v):
                raise ValueError(f"{COLOR_KEYS[k]}: «{v}» no es un color hex (#1E2A5A).")
            v = v if v.startswith("#") else "#" + v
            if len(v) == 4:
                v = "#" + "".join(c * 2 for c in v[1:])
            colors[k] = v.lower()
    fam = lambda x: re.sub(r"\s+", " ", (x or "").strip().strip("'\""))[:60]
    return {"title_font": fam(s.get("title_font")), "text_font": fam(s.get("text_font")), "colors": colors,
            "notes": (s.get("notes") or "").strip()[:2000]}


def is_empty(style: dict | None) -> bool:
    s = normalize(style)
    return not (s["title_font"] or s["text_font"] or s["colors"] or s["notes"])


# ------------------------------------------------------------------------------------------ color math (WCAG)
def _rgb(h: str) -> tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _hex(rgb) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def mix(a: str, b: str, t: float) -> str:
    """t = 0 → a, t = 1 → b."""
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def luminance(h: str) -> float:
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ensure_contrast(fg: str, bg: str, target: float, toward: str) -> str:
    """Move fg toward `toward` until it reaches `target` contrast against bg."""
    if contrast(fg, bg) >= target:
        return fg
    for i in range(1, 21):
        c = mix(fg, toward, i / 20)
        if contrast(c, bg) >= target:
            return c
    return toward


# ------------------------------------------------------------------------------------------ theme
def theme_css(base_css: str, style: dict, base_direction: str) -> tuple[str, list[str]]:
    """Base direction theme + overrides. Returns (css, notes about adjustments)."""
    s = normalize(style)
    notes, tok = [], {}
    stack = lambda f: f"'{f}', " + ("Georgia, 'Times New Roman', serif" if f in SERIFS else "'Helvetica Neue', Arial, sans-serif")
    if s["title_font"]:
        tok["--font-display"] = stack(s["title_font"])
    if s["text_font"]:
        tok["--font-text"] = stack(s["text_font"])
    c = s["colors"]
    base_bg = _token(base_css, "--bg") or "#ffffff"
    base_ink = _token(base_css, "--ink") or "#0b1220"
    bg, ink = c.get("background") or base_bg, c.get("text") or base_ink
    if "background" in c or "text" in c:
        if contrast(ink, bg) < 7:
            fixed = ensure_contrast(ink, bg, 7, "#000000" if luminance(bg) > 0.4 else "#ffffff")
            notes.append(f"El texto {ink} tenía contraste {contrast(ink, bg):.1f}:1 sobre {bg}; lo ajusté a {fixed} ({contrast(fixed, bg):.1f}:1).")
            ink = fixed
        ink3 = ensure_contrast(mix(ink, bg, 0.42), bg, 4.5, ink)
        tok.update({"--bg": bg, "--surface": mix(bg, ink, 0.04), "--ink": ink, "--ink-2": mix(ink, bg, 0.22), "--ink-3": ink3,
                    "--ink-4": mix(ink, bg, 0.72), "--ink-5": mix(ink, bg, 0.9), "--rule": mix(ink, bg, 0.8)})
    if "accent" in c:
        a = c["accent"]
        at = ensure_contrast(a, bg, 4.5, ink)
        if at != a:
            notes.append(f"El acento {a} no alcanza 4.5:1 para texto chico sobre {bg}; en texto uso {at} (en marcas se queda {a}).")
        tok.update({"--accent": a, "--accent-text": at, "--accent-soft": mix(a, bg, 0.88), "--highlight": mix(a, bg, 0.8),
                    "--accent-ink": "#ffffff" if contrast("#ffffff", a) >= contrast("#0b1220", a) else "#0b1220"})
    if "accent_2" in c:
        tok["--accent-2"] = c["accent_2"]
    if not tok:
        return base_css, notes
    lines = "\n".join(f"    {k}: {v};" for k, v in tok.items())
    css = (base_css.rstrip() + f"\n\n/* CaseOS · guía de formato de Hugo sobre la dirección «{base_direction}».\n"
           f"   Tipografías: {s['title_font'] or '(las de la dirección)'} / {s['text_font'] or '(las de la dirección)'} · "
           f"colores: {', '.join(f'{COLOR_KEYS[k]} {v}' for k, v in c.items()) or '(los de la dirección)'} */\n"
           f"@layer theme {{\n  :root {{\n{lines}\n  }}\n}}\n")
    return css, notes


def _token(css: str, name: str) -> str | None:
    m = re.search(rf"{re.escape(name)}\s*:\s*(#[0-9a-fA-F]{{6}})", css)
    return m.group(1).lower() if m else None


# ------------------------------------------------------------------------------------------ fonts
def fetch_google_font(family: str, dest: Path, timeout: int = 15) -> list[str]:
    """Download the latin subset of a Google Font (OFL) into dest and return @font-face lines in the renderer's
    single-line format (html-slide-renderer/assets/fonts/fonts.css), so bundle.mjs can inline it."""
    q = urllib.parse.quote(family)
    tries = [f"family={q}:ital,wght@0,100..900;1,100..900", f"family={q}:wght@100..900", f"family={q}:ital,wght@0,400;0,600;0,700;1,400",
             f"family={q}:wght@400;500;600;700", f"family={q}"]
    css = None
    for t in tries:
        try:
            css = _get(f"https://fonts.googleapis.com/css2?{t}&display=block", timeout).decode("utf-8")
            break
        except Exception:  # noqa: BLE001 - try the next axis combination
            continue
    if not css:
        raise ValueError(f"No encontré «{family}» en Google Fonts.")
    blocks = re.findall(r"/\*\s*([\w\-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css)
    latin = [b for sub, b in blocks if sub == "latin"] or re.findall(r"@font-face\s*\{[^}]*\}", css)
    dest.mkdir(parents=True, exist_ok=True)
    out, saved = [], {}                                   # variable fonts: several weights point to one file
    for b in latin:
        style = (re.search(r"font-style:\s*(\w+)", b) or [None, "normal"])[1]
        weight = (re.search(r"font-weight:\s*([\d ]+)", b) or [None, "400"])[1].strip()
        url = re.search(r"url\((https://[^)]+)\)", b)
        rng = re.search(r"unicode-range:\s*([^;]+);", b)
        if not url:
            continue
        fname = saved.get(url.group(1)) or f"{re.sub(r'[^A-Za-z0-9]', '', family)}-{style}-{weight.replace(' ', '_')}.woff2"
        if url.group(1) not in saved:
            (dest / fname).write_bytes(_get(url.group(1), timeout))
            saved[url.group(1)] = fname
        out.append(f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};font-display:block;"
                   f"src:url('{fname}') format('woff2');" + (f"unicode-range:{rng.group(1).strip()};" if rng else "") + "}")
    if not out:
        raise ValueError(f"Google Fonts no devolvió archivos para «{family}».")
    return out


def apply_to_deck(deck: Path, style: dict, base_direction: str, *, fetch=fetch_google_font) -> dict:
    """Write assets/themes/caseos.css (+ fonts) into a scaffolded deck. Returns what was applied and any notes."""
    s = normalize(style)
    notes, fonts = [], {}
    fonts_css = deck / "assets" / "fonts" / "fonts.css"
    present = fonts_css.read_text(encoding="utf-8") if fonts_css.exists() else ""
    for role in ("title_font", "text_font"):
        fam = s[role]
        if not fam or f"font-family:'{fam}'" in present:
            fonts[role] = {"family": fam, "source": "renderer" if fam else None}
            continue
        try:
            lines = fetch(fam, deck / "assets" / "fonts")
            present += "\n" + "\n".join(lines)
            fonts_css.write_text(present.strip() + "\n", encoding="utf-8")
            fonts[role] = {"family": fam, "source": "Google Fonts (OFL)", "files": len(lines)}
        except Exception as e:  # noqa: BLE001 - the deck still renders with the direction's font
            notes.append(f"{fam}: {e} Uso la tipografía de la dirección.")
            s[role] = ""
            fonts[role] = {"family": fam, "source": None, "error": str(e)}
    base = (deck / "assets" / "themes" / f"{base_direction}.css").read_text(encoding="utf-8")
    css, cnotes = theme_css(base, s, base_direction)
    (deck / "assets" / "themes" / "caseos.css").write_text(css, encoding="utf-8")
    return {"style": s, "fonts": fonts, "notes": notes + cnotes, "theme": "assets/themes/caseos.css", "base_direction": base_direction}
