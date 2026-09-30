"""Hugo's own quick edits to a finished deck: text on a slide and the order of the slides."""
import pytest

from caseos import deckedit, storyteller
from caseos.store import StoreError
from caseos.util import read_jsonl

SLIDE = """<!doctype html><html lang="es"><head><style>[data-slide="S{n}"] {{ }}</style></head><body>
<main class="slide" data-slide="S{n}">
  <div class="kicker">Growth · métricas</div>
  <h1 class="title">Los clientes crecen <b>4,5×</b></h1>
  <p class="body">Texto con <span class="hl">acento</span> y más.</p>
  <svg viewBox="0 0 10 10"><text x="1" y="1">45</text></svg>
  <footer class="footer"><span class="source">Fuente: T-001</span><span class="page"></span></footer>
</main>
<script>P.draw('S{n}', () => {{ document.title = "<h1>no</h1>"; }})</script>
</body></html>"""


@pytest.fixture
def deck(case, monkeypatch):
    d = case.root / "slides" / "decks" / "demo"
    (d / "slides").mkdir(parents=True)
    (d / "renders" / "thumbs").mkdir(parents=True)
    for i in (1, 2, 3):
        (d / "slides" / f"{i:02d}.html").write_text(SLIDE.format(n=i), encoding="utf-8")
        (d / "renders" / f"{i:02d}.png").write_bytes(b"png%d" % i)
    storyteller._upsert_deck(case, {"id": "DECK-1", "slug": "demo", "path": "slides/decks/demo", "status": "completed",
                                    "created_at": "2026-09-30T10:00:00"})
    monkeypatch.setattr(deckedit, "render_one", lambda deck, n: True)
    monkeypatch.setattr(deckedit.threading, "Thread", lambda target, args, daemon: type("T", (), {"start": lambda self: target(*args)})())
    monkeypatch.setattr(deckedit, "rebuild", lambda deck, pdf=False: {"ok": True})
    return d


def test_only_the_slides_own_text_is_editable():
    els = deckedit.editable(SLIDE.format(n=1))
    src = SLIDE.format(n=1)
    texts = [deckedit._plain(src[e["open_end"]:e["close_start"]]) for e in els]
    assert texts == ["Growth · métricas", "Los clientes crecen 4,5×", "Texto con acento y más.", "Fuente: T-001"]


def test_a_text_edit_changes_only_that_text_keeps_the_old_file_and_is_logged(case, deck):
    src = (deck / "slides" / "02.html").read_text(encoding="utf-8")
    pv = deckedit.preview(case, "demo", "02.html")
    assert 'data-ct="1"' in pv and "data-ct-hash" in pv and '<text x="1" y="1">45</text>' in pv
    out = deckedit.save_text(case, "DECK-1", "02.html", [{"k": 1, "html": "Los clientes crecen <b>4,6×</b><script>x</script>"},
                                                          {"k": 0, "html": "Growth · métricas"}], source=deckedit.source_hash(src))
    assert out["changed"] == [{"before": "Los clientes crecen 4,5×", "after": "Los clientes crecen 4,6×"}]
    new = (deck / "slides" / "02.html").read_text(encoding="utf-8")
    assert '<h1 class="title">Los clientes crecen <b>4,6×</b></h1>' in new and "<script>x</script>" not in new
    assert "P.draw('S2'" in new and "<text x=\"1\" y=\"1\">45</text>" in new                # scripts and charts untouched
    assert len(list((deck / "slides" / ".history").glob("02.*.html"))) == 1
    log = read_jsonl(case.root / "audit/activity.jsonl")
    assert any("Hugo editó el texto de la lámina 2" in (e.get("summary") or "") and "4,6×" in e["summary"] for e in log)
    with pytest.raises(StoreError):                                          # an editor opened on the old version
        deckedit.save_text(case, "DECK-1", "02.html", [{"k": 1, "html": "otra"}], source=deckedit.source_hash(src))


def test_text_a_script_paints_is_edited_in_its_literal(case, deck):
    p = deck / "slides" / "01.html"
    p.write_text(p.read_text(encoding="utf-8").replace("P.draw('S1', () => {",
                 "P.draw('S1', () => { s.label(1, 2, 'Business case: <b>Finora</b>', { id: 's01-title' }); s.label(3, 4, 'l\\'Oro', {});"),
                 encoding="utf-8")
    out = deckedit.save_text(case, "DECK-1", "01.html", [
        {"old": "Business case: <b>Finora</b>", "new": "Business case: <b>Finora 2026</b>", "id": "s01-title"},
        {"old": "l'Oro", "new": "l'Oro fino"},
        {"old": "texto que no existe", "new": "otro"}], source="")
    src = p.read_text(encoding="utf-8")
    assert "'Business case: <b>Finora 2026</b>'" in src and "'l\\'Oro fino'" in src
    assert [c["after"] for c in out["changed"]] == ["Business case: Finora 2026", "l'Oro fino"]
    assert out["failed"] == [{"text": "texto que no existe", "why": "no lo encontré en el código de la lámina"}]


def test_a_new_order_renumbers_slides_and_renders(case, deck):
    s = case.create("slide", {"title": "tres", "deck": "DECK-1", "html": "slides/decks/demo/slides/03.html",
                              "render": "slides/decks/demo/renders/03.png"}, actor="visual_storyteller")
    with pytest.raises(StoreError):
        deckedit.reorder(case, "DECK-1", ["01.html", "02.html"])            # not a permutation of the deck
    out = deckedit.reorder(case, "DECK-1", ["03.html", "01.html", "02.html"])
    assert out["moved"] == 3
    assert '<main class="slide" data-slide="S3" data-page="1">' in (deck / "slides" / "01.html").read_text(encoding="utf-8")
    assert 'data-slide="S2" data-page="3"' in (deck / "slides" / "03.html").read_text(encoding="utf-8")   # the footer number follows
    assert (deck / "renders" / "01.png").read_bytes() == b"png3" and (deck / "renders" / "03.png").read_bytes() == b"png2"
    assert case.get(s["id"])["html"].endswith("slides/01.html")
    assert [f["file"] for f in deckedit.files(case, "DECK-1")] == ["01.html", "02.html", "03.html"]


def test_only_text_found_once_in_the_code_is_offered(case, deck):
    p = deck / "slides" / "03.html"
    p.write_text(p.read_text(encoding="utf-8").replace("P.draw('S3', () => {",
                 "P.draw('S3', () => { s.label(1, 2, 'Único', {}); const steps = [{ v: 100 }, { v: 100 }]; s.label(3, 4, '100', {});"),
                 encoding="utf-8")
    assert deckedit.locate(case, "DECK-1", "03.html", [{"old": "Único"}, {"old": "100"}, {"old": "nada"}]) == [True, False, False]


def test_a_divider_goes_where_hugo_says_and_the_rest_moves_down(case, deck):
    s = case.create("slide", {"title": "dos", "deck": "DECK-1", "html": "slides/decks/demo/slides/02.html",
                              "render": "slides/decks/demo/renders/02.png"}, actor="visual_storyteller")
    out = deckedit.add_divider(case, "DECK-1", "Data", "#FF6364", after="01.html", via="vía Claude (pedido de Hugo)")
    assert out == {"file": "02.html", "position": 2, "slide_id": "SDATA", "moved": 2}
    new = (deck / "slides" / "02.html").read_text(encoding="utf-8")
    assert "'Data'" in new and "background: #ff6364;" in new and "color: 'ink'" in new           # dark text reads on coral
    assert '<main class="slide" data-slide="S2" data-page="3">' in (deck / "slides" / "03.html").read_text(encoding="utf-8")
    assert (deck / "renders" / "04.png").read_bytes() == b"png3" and case.get(s["id"])["html"].endswith("slides/03.html")
    assert "color: 'bg'" in (deck / "slides" / f"{deckedit.add_divider(case, 'DECK-1', 'Anexos', '#101010')['position']:02d}.html").read_text(encoding="utf-8")
    with pytest.raises(StoreError):
        deckedit.add_divider(case, "DECK-1", "", "#FF6364")


def test_a_slide_from_an_earlier_deck_comes_back_where_hugo_says(case, deck):
    old = case.root / "slides" / "decks" / "old"
    (old / "slides").mkdir(parents=True)
    (old / "renders").mkdir(parents=True)
    (old / "slides" / "00.html").write_text(SLIDE.format(n=2).replace("Los clientes crecen", "La brecha se asocia a quién entra; crecen"),
                                            encoding="utf-8")
    (old / "renders" / "00.png").write_bytes(b"old0")
    storyteller._upsert_deck(case, {"id": "DECK-0", "slug": "old", "path": "slides/decks/old", "status": "completed",
                                    "created_at": "2026-09-29T21:00:00"})
    out = deckedit.copy_slide(case, "DECK-1", "DECK-0", "00.html", after="01.html", via="vía Claude (pedido de Hugo)")
    assert out == {"file": "02.html", "position": 2, "slide_id": "S2V2", "moved": 2}          # S2 was taken: new id
    new = (deck / "slides" / "02.html").read_text(encoding="utf-8")
    assert 'data-slide="S2V2"' in new and "P.draw('S2V2'" in new and "quién entra" in new
    assert '<main class="slide" data-slide="S2" data-page="3">' in (deck / "slides" / "03.html").read_text(encoding="utf-8")
    assert (deck / "renders" / "02.png").read_bytes() == b"old0" and (deck / "renders" / "04.png").read_bytes() == b"png3"
    log = read_jsonl(case.root / "audit/activity.jsonl")
    assert any("Hugo trajo «La brecha se asocia a quién entra" in (e.get("summary") or "") and "lámina 1 de old" in e["summary"]
               and "vía Claude" in e["summary"] for e in log)
    with pytest.raises(StoreError):
        deckedit.copy_slide(case, "DECK-1", "DECK-9", "00.html")


def test_page_numbers_follow_the_position(deck):
    p = deck / "slides" / "02.html"
    p.write_text(p.read_text(encoding="utf-8").replace('data-slide="S2">', 'data-slide="S2" data-page="7">'), encoding="utf-8")
    (deck / "slides" / "03.html").write_text('<main class="slide" data-slide="S3"><p>sin pie</p></main>', encoding="utf-8")
    assert deckedit.paginate(deck) == ["01", "02"]                  # 03 shows no number: left alone
    assert 'data-page="2"' in p.read_text(encoding="utf-8") and deckedit.paginate(deck) == []


def test_hugo_asks_the_storyteller_for_changes_on_some_slides(case, deck, monkeypatch):
    submitted = []
    monkeypatch.setattr(storyteller.jobs, "submit", lambda cid, kind, title, params, agent="": submitted.append((title, params))
                        or type("J", (), {"id": "JOB-1"})())
    with pytest.raises(StoreError):
        storyteller.submit_revision(case, "DECK-1", [{"file": "02.html", "request": "más claro"}])     # not finished yet
    (deck / "presentation.html").write_text("<html></html>", encoding="utf-8")
    for bad in ([{"file": "09.html", "request": "x"}], [{"file": "02.html", "request": " "}],
                [{"file": "02.html", "request": "a"}, {"file": "02.html", "request": "b"}], []):
        with pytest.raises(StoreError):
            storyteller.submit_revision(case, "DECK-1", bad)
    out = storyteller.submit_revision(case, "DECK-1", [{"file": "02.html", "request": "Explica la decisión 2: «¿para qué?»"},
                                                        {"file": "03.html", "request": "Pon un ribbon con volumen y tiempo"}],
                                      via="vía Claude (pedido de Hugo)")
    rid = out["revision"]
    assert submitted[0][0].startswith("Visual Storyteller · cambios en láminas 2, 3") and submitted[0][1]["revision"] == rid
    assert (deck / "slides" / ".history" / f"02.{rid}.html").exists()                  # the version before the change
    d = next(x for x in storyteller.decks(case) if x["id"] == "DECK-1")
    assert d["status"] == "running" and d["revising"]["files"] == ["02.html", "03.html"]
    with pytest.raises(StoreError):                                                    # one Storyteller job at a time
        storyteller.submit_revision(case, "DECK-1", [{"file": "01.html", "request": "x"}])
    rev = storyteller.read_yaml(deck / "revisions" / f"{rid}.yaml")
    ask = storyteller.revision_ask(deck, rev, critic=True)
    assert "### slides/02.html" in ask and "«¿para qué?»" in ask and "--only 02,03" in ask and "independent-slide-critic" in ask

    p = deck / "slides" / "02.html"                                                     # the Storyteller edits one of them
    p.write_text(p.read_text(encoding="utf-8").replace("Growth · métricas", "Growth · métricas y decisiones"), encoding="utf-8")
    rebuilt = []
    monkeypatch.setattr(deckedit, "rebuild", lambda deck, pdf=False: rebuilt.append(pdf) or {"ok": True})
    res = storyteller.finish_revision(case, "DECK-1", rid, final="02: kicker → «Growth · métricas y decisiones»", cost=1.25)
    assert res["revision"]["changed"] == ["02.html"] and res["revision"]["untouched"] == ["03.html"]
    assert rebuilt == [True]                                                           # its bundle was older than the edit
    d = next(x for x in storyteller.decks(case) if x["id"] == "DECK-1")
    assert d["status"] == "completed" and d["revising"] is None and d["revisions"] == 1
    edits = read_jsonl(deck / "edits.jsonl")
    assert edits[-1]["kind"] == "revision" and edits[-1]["files"] == ["02.html"] and edits[-1]["by"] == "visual_storyteller"
    log = read_jsonl(case.root / "audit/activity.jsonl")
    assert any("Hugo pidió al Visual Storyteller cambios en las láminas 2, 3" in (e.get("summary") or "") and "vía Claude" in e["summary"]
               for e in log)
    assert any(e["actor"] == "visual_storyteller" and "aplicados en las láminas 2 del deck" in e["summary"] for e in log)


def test_a_revision_cut_by_a_restart_gives_the_deck_back(case, deck, monkeypatch):
    monkeypatch.setattr(storyteller.jobs, "submit", lambda *a, **k: type("J", (), {"id": "JOB-X"})())
    (deck / "presentation.html").write_text("<html></html>", encoding="utf-8")
    rid = storyteller.submit_revision(case, "DECK-1", [{"file": "01.html", "request": "x"}])["revision"]
    assert storyteller.recover_decks(case) == 1
    d = next(x for x in storyteller.decks(case) if x["id"] == "DECK-1")
    assert d["status"] == "completed" and d["revising"] is None and "slides/.history" in d["revision_error"]
    assert storyteller.read_yaml(deck / "revisions" / f"{rid}.yaml")["status"] == "interrupted"
