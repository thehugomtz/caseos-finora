"""Hugo's own quick edits to a finished deck: the order of the slides and the text on them.

The Visual Storyteller builds the deck; these are the small things Hugo fixes himself instead of asking for another run.
- Order: the renderer orders slides by file name (slides/NN.html), so a new order renumbers the files — and their
  renders — without touching the renderer. Page numbers are filled at runtime, so they follow.
- Text: an editable preview marks every element of the slide that carries its own text (never script, style or SVG:
  chart labels come from the data), and a save replaces the inner HTML of the marked elements in the source file.
  The previous version of the file is kept, and every edit is logged — a figure Hugo types no longer comes from a table,
  and the record says so.
After a change, presentation.html is rebuilt; the PDF is rebuilt on request (it takes Chrome and a minute).
"""
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import threading
from html.parser import HTMLParser
from pathlib import Path

from . import storyteller
from .store import CaseStore, StoreError
from .util import now_iso, stamp

SLIDE_FILE = re.compile(r"^\d{2}\.html$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
NO_TEXT = {"script", "style", "svg", "noscript", "template", "canvas"}
INLINE_OK = {"b", "strong", "i", "em", "span", "br", "sub", "sup", "small", "u", "mark"}


# ------------------------------------------------------------------------------------------ deck files
def _deck(store: CaseStore, deck_id: str) -> tuple[dict, Path]:
    d = next((x for x in storyteller.decks(store) if x["id"] == deck_id), None)
    if not d:
        raise StoreError("Deck no encontrado.")
    if d.get("status") == "running":
        raise StoreError("El Visual Storyteller está trabajando en este deck; espera a que termine.")
    return d, store.root / d["path"]


def slide_files(deck: Path) -> list[str]:
    return sorted(f.name for f in (deck / "slides").glob("*.html") if SLIDE_FILE.match(f.name))


MAIN_TAG = re.compile(r'<main\b[^>]*\bclass="slide"[^>]*>')


def paginate(deck: Path) -> list[str]:
    """The number a slide's footer shows is its `data-page`, written when the Storyteller drew it. Keep it equal to the
    slide's position, so moving or inserting slides never leaves an old number. Returns the slides that changed."""
    changed = []
    for i, f in enumerate(slide_files(deck), 1):
        p = deck / "slides" / f
        src = p.read_text(encoding="utf-8")
        m = MAIN_TAG.search(src)
        if not m:
            continue
        tag = m.group(0)
        if "data-page=" in tag:
            new = re.sub(r'\sdata-page="[^"]*"', f' data-page="{i}"', tag, count=1)
        elif 'class="page"' in src:                           # a footer that shows a number but was never given one
            new = tag[:-1] + f' data-page="{i}">'
        else:
            continue
        if new != tag:
            p.write_text(src[:m.start()] + new + src[m.end():], encoding="utf-8")
            changed.append(f[:2])
    return changed


def files(store: CaseStore, deck_id: str) -> list[dict]:
    d = next((x for x in storyteller.decks(store) if x["id"] == deck_id), None)
    if not d:
        raise StoreError("Deck no encontrado.")
    deck = store.root / d["path"]
    out = []
    for f in slide_files(deck):
        src = (deck / "slides" / f).read_text(encoding="utf-8")
        title = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", src) or re.search(r"<title>([\s\S]*?)</title>", src)
        n = f[:2]
        png = deck / "renders" / f"{n}.png"
        out.append({"file": f, "n": int(n), "title": html_lib.unescape(re.sub(r"<[^>]+>|\s+", " ", title.group(1))).strip() if title else f,
                    "render": f"renders/{n}.png" if png.exists() else None,
                    "v": int(max((deck / "slides" / f).stat().st_mtime, png.stat().st_mtime if png.exists() else 0))})
    return out


# ------------------------------------------------------------------------------------------ text: mark and replace
class _Tree(HTMLParser):
    """Elements inside <main class="slide"> with their source offsets and whether they carry text of their own."""

    def __init__(self, src: str):
        super().__init__(convert_charrefs=False)
        self.src, self.lines = src, [0]
        for m in re.finditer(r"\n", src):
            self.lines.append(m.end())
        self.stack, self.found, self.in_main = [], [], False

    def _off(self) -> int:
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self._off()
        text = self.get_starttag_text() or ""
        el = {"tag": tag, "start": start, "open_end": start + len(text), "text": False, "blocked": False, "children": []}
        cls = dict(attrs).get("class") or ""
        if tag == "main" and re.search(r"\bslide\b", cls):
            self.in_main, el["main"] = True, True
        parent = self.stack[-1] if self.stack else None
        el["blocked"] = tag in NO_TEXT or bool(parent and parent["blocked"])
        el["in_main"] = self.in_main
        if tag in VOID:
            return
        if parent:
            parent["children"].append(el)
        self.stack.append(el)
        self.found.append(el)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pos = self._off()
        for i in range(len(self.stack) - 1, -1, -1):          # tolerate a missing close tag inside
            if self.stack[i]["tag"] == tag:
                el = self.stack[i]
                el["close_start"] = pos
                del self.stack[i:]
                if el.get("main"):
                    self.in_main = False
                return

    def handle_data(self, data):
        if self.stack and data.strip():
            self.stack[-1]["text"] = True

    def handle_entityref(self, name):
        if self.stack:
            self.stack[-1]["text"] = True

    def handle_charref(self, name):
        if self.stack:
            self.stack[-1]["text"] = True


def editable(src: str) -> list[dict]:
    """The outermost elements inside the slide that carry their own text, in document order (their index is `k`)."""
    t = _Tree(src)
    t.feed(src)
    t.close()
    out, covered = [], []
    for el in t.found:
        if not el["in_main"] or el["blocked"] or el.get("main") or not el["text"] or "close_start" not in el:
            continue
        if any(c["start"] <= el["start"] and el["close_start"] <= c["close_start"] for c in covered):
            continue                                           # a descendant of an editable element edits with it
        covered.append(el)
        out.append(el)
    return out


def source_hash(src: str) -> str:
    return hashlib.sha1(src.encode("utf-8")).hexdigest()[:12]


def preview(store: CaseStore, slug: str, file: str) -> str:
    """The slide with data-ct="k" on every editable element, and its source hash, for the in-app editor."""
    if not SLIDE_FILE.match(file):
        raise StoreError("Lámina inválida.")
    p = storyteller.deck_file(store, slug, f"slides/{file}")
    src = p.read_text(encoding="utf-8")
    els = editable(src)
    out = src
    for k, el in sorted(enumerate(els), key=lambda x: -x[1]["start"]):
        tag_end = el["start"] + 1 + len(el["tag"])
        out = out[:tag_end] + f' data-ct="{k}"' + out[tag_end:]
    return out.replace("<html", f'<html data-ct-hash="{source_hash(src)}"', 1)


class _Clean(HTMLParser):
    """What a contenteditable hands back, reduced to text and simple inline tags (no scripts, no handlers)."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
            return
        if self.skip or tag not in INLINE_OK:
            if tag in ("div", "p") and self.out:
                self.out.append("<br>")                        # Enter in a contenteditable makes a block: keep the break
            return
        keep = [(a, v) for a, v in attrs if a in ("class", "style") and v is not None and "expression" not in v.lower()]
        self.out.append(f"<{tag}" + "".join(f' {a}="{v}"' for a, v in keep) + ">")

    def handle_startendtag(self, tag, attrs):
        if tag == "br" and not self.skip:
            self.out.append("<br>")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if not self.skip and tag in INLINE_OK and tag != "br":
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data.replace("<", "&lt;").replace(">", "&gt;"))

    def handle_entityref(self, name):
        if not self.skip:
            self.out.append(f"&{name};")

    def handle_charref(self, name):
        if not self.skip:
            self.out.append(f"&#{name};")


def clean(html: str) -> str:
    c = _Clean()
    c.feed(html or "")
    c.close()
    s = "".join(c.out).strip()
    return re.sub(r"(<br>)+$", "", s)


def _plain(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def _js_forms(s: str) -> list[str]:
    """How a text can sit in the slide's source: as markup, or inside a '…' or "…" JavaScript string."""
    return [s, s.replace("\\", "\\\\").replace("'", "\\'"), s.replace("\\", "\\\\").replace('"', '\\"')]


def _replace_literal(src: str, old: str, new: str, el_id: str = "") -> tuple[str | None, str]:
    """Text a script paints (s.label(x, y, 'text', {...})) lives as a string literal: replace that one occurrence."""
    for i, cand in enumerate(_js_forms(old)):
        if not cand.strip():
            continue
        hits = [m.start() for m in re.finditer(re.escape(cand), src)]
        if not hits:
            continue
        if len(hits) > 1 and el_id:                          # the call that carries the element's id disambiguates
            m = re.search(r"id\s*:\s*['\"]" + re.escape(el_id) + r"['\"]", src)
            if m:
                before = [x for x in hits if x < m.start()]
                hits = before[-1:] or hits
        if len(hits) != 1:
            return None, "aparece más de una vez en la lámina"
        return src[:hits[0]] + _js_forms(new)[i] + src[hits[0] + len(cand):], ""
    return None, "no lo encontré en el código de la lámina"


def locate(store: CaseStore, deck_id: str, file: str, texts: list) -> list[bool]:
    """Which texts a script paints can be found once in the slide's code (so an edit to them can be saved). A value
    that sits in a chart's data several times is not offered for editing: it would be a guess."""
    if not SLIDE_FILE.match(file):
        raise StoreError("Lámina inválida.")
    _, deck = _deck(store, deck_id)
    src = (deck / "slides" / file).read_text(encoding="utf-8")
    return [_replace_literal(src, t.get("old") or "", (t.get("old") or "") + "\u2063", t.get("id") or "")[0] is not None
            for t in texts if isinstance(t, dict)]


def save_text(store: CaseStore, deck_id: str, file: str, edits: list, *, source: str, actor: str = "hugo") -> dict:
    """Apply Hugo's text edits to the slide's source: `{"k", "html"}` for text written in the markup (by position),
    `{"old", "new", "id"}` for text a script paints (by its literal). Keeps the previous file; logs before → after."""
    if actor != "hugo":
        raise StoreError("Solo Hugo edita el texto del deck.")
    if not SLIDE_FILE.match(file):
        raise StoreError("Lámina inválida.")
    d, deck = _deck(store, deck_id)
    p = deck / "slides" / file
    src = p.read_text(encoding="utf-8")
    if source and source != source_hash(src):
        raise StoreError("La lámina cambió desde que la abriste; recárgala antes de guardar.")
    els = editable(src)
    changes, failed, out = [], [], src
    fixed = sorted((e for e in edits if isinstance(e, dict) and str(e.get("k", "")).isdigit() and int(e["k"]) < len(els)),
                   key=lambda e: -els[int(e["k"])]["start"])
    for e in fixed:                                          # from the end, so earlier offsets hold
        el = els[int(e["k"])]
        new, old = clean(e.get("html") or ""), src[el["open_end"]:el["close_start"]]
        if _plain(new) != _plain(old):
            out = out[:el["open_end"]] + new + out[el["close_start"]:]
            changes.append({"before": _plain(old), "after": _plain(new)})
    changes.reverse()                                        # back to the slide's reading order
    for e in edits:
        if not isinstance(e, dict) or "old" not in e:
            continue
        new = clean(e.get("new") or "").replace("\n", " ")
        if _plain(new) == _plain(e["old"]):
            continue
        res, why = _replace_literal(out, e["old"], new, e.get("id") or "")
        if res is None:
            failed.append({"text": _plain(e["old"])[:80], "why": why})
            continue
        out = res
        changes.append({"before": _plain(e["old"]), "after": _plain(new)})
    if not changes:
        return {"changed": [], "failed": failed, "file": file}
    hist = deck / "slides" / ".history"
    hist.mkdir(exist_ok=True)
    shutil.copy2(p, hist / f"{file[:2]}.{stamp()}.html")
    p.write_text(out, encoding="utf-8")
    _record(store, d, deck, {"kind": "text", "file": file, "changes": changes},
            f"Hugo editó el texto de la lámina {int(file[:2])} del deck {d['slug']}: "
            + "; ".join(f"«{c['before'][:50]}» → «{c['after'][:50]}»" for c in changes))
    rebuild(deck)                                            # the presentation shows the new text at once
    threading.Thread(target=render_one, args=(deck, file[:2]), daemon=True).start()   # the thumbnail follows (Chrome: ~1 min)
    return {"changed": changes, "failed": failed, "file": file}


# ------------------------------------------------------------------------------------------ order
def reorder(store: CaseStore, deck_id: str, order: list[str], *, actor: str = "hugo") -> dict:
    """New order = the files renumbered 01..NN (slides and their renders); the slides of the case follow."""
    if actor != "hugo":
        raise StoreError("Solo Hugo reordena el deck.")
    d, deck = _deck(store, deck_id)
    cur = slide_files(deck)
    if sorted(order) != cur:
        raise StoreError("El orden no coincide con las láminas del deck; recarga.")
    moves = {old: f"{i:02d}.html" for i, old in enumerate(order, 1)}
    moved = {o: n for o, n in moves.items() if o != n}
    if not moved:
        return {"moved": 0}
    pairs = [(deck / "slides", ".html"), (deck / "renders", ".png"), (deck / "renders" / "thumbs", ".png")]
    for base, ext in pairs:                                     # two passes through temporary names: no collisions
        for old in moved:
            f = base / (old[:2] + ext)
            if f.exists():
                f.rename(base / f"__mv_{old[:2]}{ext}")
        for old, new in moved.items():
            f = base / f"__mv_{old[:2]}{ext}"
            if f.exists():
                f.rename(base / (new[:2] + ext))
    rel = lambda n, sub, ext: str((deck / sub / f"{n}{ext}").relative_to(store.root))
    for e in store.list("slide"):
        if e.get("deck") != deck_id or not e.get("html"):
            continue
        old = Path(e["html"]).name
        if old in moved:
            n = moved[old][:2]
            store.update(e["id"], {"html": rel(n, "slides", ".html"), "render": rel(n, "renders", ".png")},
                         actor=actor, material=False, summary=f"{e['id']}: ahora es la lámina {int(n)}")
    repaged = paginate(deck)
    _record(store, d, deck, {"kind": "order", "before": cur, "order": order, "moved": moved},
            f"Hugo reordenó el deck {d['slug']}: " + ", ".join(f"{int(o[:2])}→{int(n[:2])}" for o, n in moved.items()))
    rebuild(deck)
    if repaged:                                                  # their thumbnails still show the old page number
        threading.Thread(target=render_one, args=(deck, ",".join(repaged)), daemon=True).start()
    return {"moved": len(moved), "order": [moves[o] for o in order]}


# ------------------------------------------------------------------------------------------ section dividers
DIVIDER = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{sid} · {title_html}</title>
<link rel="stylesheet" href="../assets/fonts/fonts.css">
<link rel="stylesheet" href="../assets/core.css">
<link rel="stylesheet" href="../assets/theme.css">
<script src="../assets/primitives.js"></script>
<style>
[data-slide="{sid}"] {{
  background: {color};
}}
</style>
</head>
<body>
<main class="slide" data-slide="{sid}" data-composition="section_divider" data-family="editorial" data-word-budget="3">
  <aside class="notes">Separador de sección: {title_html}.</aside>
</main>
<script>
P.draw('{sid}', (s, P) => {{
  // Separador de sección (agregado por Hugo desde CaseOS): color sólido, solo el nombre.
  s.label(112, 900, '{title_js}', {{ cls: 'statement', size: 144, anchor: 'bl', color: '{ink}', id: '{lid}', focal: true }});
}});
</script>
</body>
</html>
"""


def _luminance(hex_: str) -> float:
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _shift(deck: Path, frm: int, by: int = 1) -> dict:
    """Renumber slides (and renders) from position `frm` on, last first so nothing collides."""
    moved = {}
    for f in sorted((x for x in slide_files(deck) if int(x[:2]) >= frm), reverse=True):
        n, m = f[:2], f"{int(f[:2]) + by:02d}"
        for base, ext in ((deck / "slides", ".html"), (deck / "renders", ".png"), (deck / "renders" / "thumbs", ".png")):
            if (base / f"{n}{ext}").exists():
                (base / f"{n}{ext}").rename(base / f"{m}{ext}")
        moved[f] = f"{m}.html"
    return moved


def _insert(store: CaseStore, deck_id: str, deck: Path, pos: int, html: str) -> tuple[str, dict, str]:
    """Put a slide at position `pos`: the ones from there on move down one place (their case slides follow) and
    their page numbers follow. Returns the new file, the moves and the slides to re-render."""
    moved = _shift(deck, pos)
    rel = lambda n, sub, ext: str((deck / sub / f"{n}{ext}").relative_to(store.root))
    for e in store.list("slide"):
        if e.get("deck") == deck_id and e.get("html") and Path(e["html"]).name in moved:
            n = moved[Path(e["html"]).name][:2]
            store.update(e["id"], {"html": rel(n, "slides", ".html"), "render": rel(n, "renders", ".png")}, actor="hugo",
                         material=False, summary=f"{e['id']}: ahora es la lámina {int(n)}")
    file = f"{pos:02d}.html"
    (deck / "slides" / file).write_text(html, encoding="utf-8")
    return file, moved, ",".join(sorted({file[:2], *paginate(deck)}))


def _ids(deck: Path) -> set[str]:
    return {m for f in slide_files(deck) for m in re.findall(r'data-slide="([^"]+)"', (deck / "slides" / f).read_text(encoding="utf-8"))}


def copy_slide(store: CaseStore, deck_id: str, from_deck: str, from_file: str, *, after: str = "", via: str = "",
               actor: str = "hugo") -> dict:
    """Bring a slide from another deck of the case (e.g. one a newer run left out), placed after `after`. It takes the
    theme of the deck it lands in; if its id is already used there, it gets a new one."""
    if actor != "hugo":
        raise StoreError("Solo Hugo agrega láminas al deck.")
    if not SLIDE_FILE.match(from_file):
        raise StoreError("Lámina inválida.")
    d, deck = _deck(store, deck_id)
    src_d = next((x for x in storyteller.decks(store) if x["id"] == from_deck), None)
    if not src_d:
        raise StoreError("No encuentro el deck de origen.")
    src = store.root / src_d["path"] / "slides" / from_file
    if not src.exists():
        raise StoreError("No encuentro esa lámina en el deck de origen.")
    html = src.read_text(encoding="utf-8")
    files_ = slide_files(deck)
    if after and after not in files_:
        raise StoreError("No encuentro la lámina después de la cual va.")
    old = (re.search(r'data-slide="([^"]+)"', html) or [None, ""])[1]
    used, new = _ids(deck), old
    k = 2
    while new in used:
        new, k = f"{old}V{k}", k + 1
    if new != old:
        html = (html.replace(f'data-slide="{old}"', f'data-slide="{new}"').replace(f"P.draw('{old}'", f"P.draw('{new}'")
                .replace(f'P.draw("{old}"', f'P.draw("{new}"'))
    pos = (int(after[:2]) + 1) if after else len(files_) + 1
    file, moved, render = _insert(store, deck_id, deck, pos, html)
    png = store.root / src_d["path"] / "renders" / f"{from_file[:2]}.png"
    if png.exists():                                         # a thumbnail right away; the re-themed one follows
        shutil.copy2(png, deck / "renders" / f"{file[:2]}.png")
    title = re.search(r"<h1\b[^>]*>([\s\S]*?)</h1>", html)
    name = _plain(title.group(1)) if title else from_file
    _record(store, d, deck, {"kind": "copy", "file": file, "from": {"deck": src_d["slug"], "file": from_file}, "moved": moved},
            f"Hugo trajo «{name[:70]}» (lámina {int(from_file[:2]) + 1} de {src_d['slug']}) como lámina {pos} del deck {d['slug']}"
            + (f" · {via}" if via else ""))
    rebuild(deck)
    threading.Thread(target=render_one, args=(deck, render), daemon=True).start()
    return {"file": file, "position": pos, "slide_id": new, "moved": len(moved)}


def add_divider(store: CaseStore, deck_id: str, title: str, color: str, *, after: str = "", via: str = "",
                actor: str = "hugo") -> dict:
    """A solid-color section divider with only its name, like the ones the Storyteller drew, placed after `after`
    (a slide file; empty = at the end). The text is dark or light, whichever reads on that color."""
    if actor != "hugo":
        raise StoreError("Solo Hugo agrega láminas al deck.")
    title = re.sub(r"\s+", " ", title or "").strip()[:40]
    if not title:
        raise StoreError("El separador necesita un nombre.")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color or ""):
        raise StoreError("El color debe ser un hex como #FF6364.")
    d, deck = _deck(store, deck_id)
    files_ = slide_files(deck)
    if after and after not in files_:
        raise StoreError("No encuentro la lámina después de la cual va el separador.")
    pos = (int(after[:2]) + 1) if after else len(files_) + 1
    used = _ids(deck)
    base_id = "S" + (re.sub(r"[^A-Za-z0-9]", "", title).upper()[:12] or "SEC")
    sid, k = base_id, 2
    while sid in used:
        sid, k = f"{base_id}{k}", k + 1
    esc = html_lib.escape(title)
    js = title.replace("\\", "\\\\").replace("'", "\\'").replace("<", "&lt;")
    file, moved, render = _insert(store, deck_id, deck, pos, DIVIDER.format(sid=sid, title_html=esc, title_js=js, color=color.lower(),
                                                                    ink="bg" if _luminance(color) < 0.18 else "ink", lid=f"{sid.lower()}-name"))
    _record(store, d, deck, {"kind": "divider", "file": file, "title": title, "color": color.lower(), "moved": moved},
            f"Hugo agregó el separador «{title}» ({color.lower()}) como lámina {pos} del deck {d['slug']}" + (f" · {via}" if via else ""))
    rebuild(deck)
    threading.Thread(target=render_one, args=(deck, render), daemon=True).start()
    return {"file": file, "position": pos, "slide_id": sid, "moved": len(moved)}


# ------------------------------------------------------------------------------------------ record + rebuild
def _record(store: CaseStore, d: dict, deck: Path, entry: dict, summary: str) -> None:
    with (deck / "edits.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": now_iso(), "by": "hugo", **entry}, ensure_ascii=False) + "\n")
    d = {**d, "edited_at": now_iso(), "edits": int(d.get("edits") or 0) + 1}
    storyteller._upsert_deck(store, d)
    store.log("hugo", "edited", [d["id"]], summary, material=True)


def _node(args: list[str], timeout: int) -> tuple[bool, str]:
    if not shutil.which("node"):
        return False, "node no está instalado"
    try:
        p = subprocess.run(["node", *args], capture_output=True, text=True, timeout=timeout)
        return p.returncode == 0, (p.stderr or p.stdout)[-400:]
    except subprocess.TimeoutExpired:
        return False, "tardó demasiado"


_RENDERING = threading.Lock()


def render_one(deck: Path, n: str) -> bool:
    """Re-render a slide's PNG (`n` = "02", or several: "02,05,07") so the thumbnail follows the text; the deck's QA
    files are left as they were. One render at a time: they share those files."""
    script = storyteller.renderer_dir() / "scripts" / "render.mjs"
    if not script.exists():
        return False
    with _RENDERING:
        keep = {f: (deck / "renders" / f).read_bytes() for f in ("qa.json", "qa-summary.md") if (deck / "renders" / f).exists()}
        ok, _ = _node([str(script), str(deck), "--only", n, "--no-contact"], 120 + 15 * len(n.split(",")))
        for f, b in keep.items():
            (deck / "renders" / f).write_bytes(b)
    return ok


def rebuild(deck: Path, *, pdf: bool = False) -> dict:
    """presentation.html (and index.html) from slides/NN.html; the PDF only when asked."""
    script = storyteller.renderer_dir() / "scripts" / "bundle.mjs"
    if not script.exists():
        return {"ok": False, "error": "No encuentro html-slide-renderer."}
    ok, msg = _node([str(script), str(deck), "--no-verify"] + (["--pdf"] if pdf else []), 600 if pdf else 180)
    return {"ok": ok, **({} if ok else {"error": msg})}


def rebuild_pdf(store: CaseStore, deck_id: str) -> dict:
    d, deck = _deck(store, deck_id)
    out = rebuild(deck, pdf=True)
    if out["ok"]:
        store.log("hugo", "exported", [d["id"]], f"PDF del deck {d['slug']} regenerado con las ediciones de Hugo", material=False)
    return out
