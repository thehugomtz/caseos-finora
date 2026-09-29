"""Framing & Shaping: the structured document that comes out of Framing.

The Shaping document is what Hugo approves at the end of Framing and what the rest of the case runs on:
  1. Problema — statement, situation, why it matters, inside / outside the scope (no-gos and rabbit holes)
  2. Pregunta ejecutiva — framing/current.yaml › executive_question (edited in place, versioned)
  3. Guion de la historia — sections → slides; each slide says which question it answers and what it must show
  4. Hipótesis — the H-xxx entities with their falsifiers
  5. Plan de investigación — one task per question of the guion that needs work: what comes out (investigación y
     propuesta · investigar datos · research externo), the agent that leads it, a starting answer written from the case
     context and Hugo's own words (a working hypothesis, never a fact), and the steps — "investigar datos en el modelo"
     names real tables of the case's data model. Approved tasks appear in Research, ready to launch; launching stays
     Hugo's click, and the specialist receives the starting answer to validate or refute.
  6. Lo que no afirmamos todavía · decisiones necesarias · riesgos

The Framer proposes; proposals wait in framing/current.yaml › pending until Hugo approves, edits or discards them (the
same discipline as the brief). Approved content lives in current.yaml › problem / storyline_guide / research_plan.
Pending keys: "problem", "guion:<section id>", "plan:<task id>".
"""
from __future__ import annotations

import re

from .store import CaseStore
from .util import clip, norm, now_iso

PROBLEM_FIELDS = ["statement", "situation", "why_it_matters", "in_scope", "out_of_scope"]
KINDS = {"data": {"label": "Datos", "specialty": "analytics", "agent": "Analytics"},
         "research": {"label": "Research", "specialty": "business", "agent": "Business Research"},
         "measurement": {"label": "Medición", "specialty": "measurement", "agent": "Measurement"},
         "data_model": {"label": "Modelo de datos", "specialty": "data_engineering", "agent": "Data Engineering"}}
INTENSITIES = ["L1", "L2", "L3"]
# what a task delivers, in Hugo's words: most questions of a guion are "investigación y propuesta", not a lookup
WORK = {"propuesta": {"label": "Investigación y propuesta",
                      "hint": "Se responde con una propuesta: contexto del caso, lo que ya dijiste, datos del modelo y research donde haga falta."},
        "datos": {"label": "Investigar datos", "hint": "La respuesta sale del modelo de datos del caso."},
        "research": {"label": "Research externo", "hint": "Hace falta información de afuera: prácticas, benchmarks, mercado."}}
STEP_KINDS = {"data": "Investigar datos en el modelo", "research": "Research", "proposal": "Proponer"}


PLAN_RUNS = "framing/plans.jsonl"          # the Framer's "plan desde el guion" runs (status, tasks proposed, notes)


def _fr(store: CaseStore) -> dict:
    return store.read_data("framing/current.yaml", {}) or {}


def _empty(v) -> bool:
    if isinstance(v, dict):
        return all(_empty(x) for x in v.values())
    return v in (None, "", []) or (isinstance(v, list) and not any(str(x).strip() for x in v))


def _lines(v) -> list[str]:
    if isinstance(v, str):
        v = v.split("\n")
    out = []
    for x in v or []:
        x = str(x).strip()
        if x and x not in out:
            out.append(x)
    return out


# ------------------------------------------------------------------------------------------ normalization
def clean_problem(v: dict) -> dict:
    v = v or {}
    return {"statement": (v.get("statement") or "").strip(), "situation": (v.get("situation") or "").strip(),
            "why_it_matters": (v.get("why_it_matters") or "").strip(), "in_scope": _lines(v.get("in_scope")),
            "out_of_scope": _lines(v.get("out_of_scope"))}


def clean_section(v: dict, sid: str) -> dict:
    slides = []
    for i, s in enumerate((v or {}).get("slides") or [], 1):
        title = (s.get("title") or "").strip()
        if not (title or (s.get("question") or "").strip()):
            continue
        slides.append({"id": f"{sid}.{len(slides) + 1}", "title": title, "question": (s.get("question") or "").strip(),
                       "intent": (s.get("intent") or "").strip(), "notes": (s.get("notes") or "").strip(),
                       "links": [x for x in (s.get("links") or []) if isinstance(x, str) and x.strip()]})
    return {"id": sid, "title": ((v or {}).get("title") or "").strip(), "purpose": ((v or {}).get("purpose") or "").strip(),
            "slides": slides}


def clean_steps(v) -> list[dict]:
    out = []
    for x in v or []:
        if not isinstance(x, dict) or x.get("kind") not in STEP_KINDS or not (x.get("what") or "").strip():
            continue
        where = x.get("where") or []
        where = [w.strip() for w in (where.split(",") if isinstance(where, str) else where) if isinstance(w, str) and w.strip()]
        out.append({"kind": x["kind"], "what": x["what"].strip(), "where": where if x["kind"] == "data" else []})
    return out[:6]


def clean_said(v) -> list[dict]:
    out = []
    for x in v or []:
        x = {"text": x, "ref": ""} if isinstance(x, str) else (x or {})
        if (x.get("text") or "").strip():
            out.append({"text": x["text"].strip(), "ref": (x.get("ref") or "").strip()})
    return out[:4]


def infer_work(kind: str, steps: list[dict]) -> str:
    if kind == "data":
        return "datos"
    if kind == "research" and "proposal" not in {x["kind"] for x in steps}:
        return "research"
    return "propuesta"


def clean_task(v: dict, tid: str) -> dict:
    v = v or {}
    kind = v.get("kind") if v.get("kind") in KINDS else "research"
    inten = v.get("intensity")
    inten = "analytics" if kind == "data" else (inten if inten in INTENSITIES else "L2")
    steps = clean_steps(v.get("steps"))
    return {"id": tid, "question": (v.get("question") or "").strip(), "kind": kind, "agent": KINDS[kind]["specialty"],
            "intensity": inten, "work": v.get("work") if v.get("work") in WORK else infer_work(kind, steps),
            "draft_answer": (v.get("draft_answer") or "").strip(), "hugo_said": clean_said(v.get("hugo_said")), "steps": steps,
            "why": (v.get("why") or "").strip(),
            "links": [x for x in (v.get("links") or []) if isinstance(x, str) and x.strip()],
            "slides": [x for x in (v.get("slides") or []) if isinstance(x, str) and x.strip()],
            "flags": [x for x in (v.get("flags") or []) if isinstance(x, str) and x.strip()]}


def next_section_id(fr: dict) -> str:
    # ids are never reused: a discarded or removed one keeps meaning what the activity log says it meant
    used = {s["id"] for s in fr.get("storyline_guide") or []} | {k.split(":", 1)[1] for k in (fr.get("pending") or {}) if k.startswith("guion:")}
    used |= set(fr.get("retired_ids") or [])
    n = 1
    while f"S{n}" in used:
        n += 1
    return f"S{n}"


def next_task_id(fr: dict) -> str:
    used = {t["id"] for t in fr.get("research_plan") or []} | {k.split(":", 1)[1] for k in (fr.get("pending") or {}) if k.startswith("plan:")}
    used |= set(fr.get("retired_ids") or [])
    n = 1
    while f"RT-{n:03d}" in used:
        n += 1
    return f"RT-{n:03d}"


def _num(oid: str) -> int:
    return int(re.sub(r"\D", "", oid or "") or 0)


def _approved(fr: dict, key: str):
    if key == "problem":
        return fr.get("problem") or {}
    kind, _, oid = key.partition(":")
    coll = fr.get("storyline_guide" if kind == "guion" else "research_plan") or []
    return next((x for x in coll if x.get("id") == oid), None)


def _same(a, b) -> bool:
    import json
    strip = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False) if x is not None else ""
    return norm(strip(a)) == norm(strip(b))


# ------------------------------------------------------------------------------------------ proposals and approvals
def propose(store: CaseStore, key: str, value, *, basis: str = "framer", why: str = "", hugo_wording: str = "",
            turn_id: str = "", actor: str = "framer", fr: dict | None = None, save: bool = True) -> bool:
    """An agent's proposal for a Shaping section: stored as pending, never applied. False when nothing is new."""
    own = fr is None
    fr = fr if fr is not None else _fr(store)
    if key == "problem":
        val = clean_problem(value)
        cur = fr.get("problem") or {}
        # empty fields in a proposal mean "no change"
        val = {k: (val[k] if not _empty(val[k]) else cur.get(k, [] if k in ("in_scope", "out_of_scope") else "")) for k in PROBLEM_FIELDS}
    elif key.startswith("guion:"):
        val = clean_section(value, key.split(":", 1)[1])
    elif key.startswith("plan:"):
        val = clean_task(value, key.split(":", 1)[1])
    else:
        raise ValueError(f"Sección de shaping desconocida: {key}")
    if _empty({k: v for k, v in val.items() if k != "id"}) or (key.startswith("plan:") and not val["question"]):
        return False
    cur = _approved(fr, key)
    pend = fr.setdefault("pending", {})
    if cur is not None and _same({k: v for k, v in (cur or {}).items() if k not in ("status", "research_id", "approved_at", "sent_at")},
                                 {k: v for k, v in val.items() if k not in ("status", "research_id")}):
        pend.pop(key, None)
        if own and save:
            store.write_data("framing/current.yaml", fr)
        return False
    pend[key] = {"value": val, "basis": basis, "why": (why or "").strip(), "hugo_wording": (hugo_wording or "").strip(),
                 "turn_id": turn_id, "by": actor, "at": now_iso(), "revises": cur is not None and not _empty(cur)}
    if own and save:
        store.write_data("framing/current.yaml", fr)
    return True


def _apply(fr: dict, key: str, val, *, actor: str, via: str = "") -> None:
    st = fr.setdefault("shaping_state", {})
    prev = st.get(key) or {}
    if key == "problem":
        fr["problem"] = clean_problem(val)
    elif key.startswith("guion:"):
        sec = clean_section(val, key.split(":", 1)[1])
        before = _approved(fr, key) or ((fr.get("pending") or {}).get(key) or {}).get("value")
        _retarget_slides(fr, *_slide_map(before, val, sec))
        guide = fr.setdefault("storyline_guide", [])
        i = next((n for n, s in enumerate(guide) if s["id"] == sec["id"]), None)
        guide.__setitem__(i, sec) if i is not None else guide.append(sec)
        guide.sort(key=lambda x: _num(x["id"]))                   # the story reads in section order, whatever was approved first
    elif key.startswith("plan:"):
        t = clean_task(val, key.split(":", 1)[1])
        plan = fr.setdefault("research_plan", [])
        i = next((n for n, x in enumerate(plan) if x["id"] == t["id"]), None)
        old = plan[i] if i is not None else {}
        t.update({"status": old.get("status") if old.get("status") == "sent" else "approved", "research_id": old.get("research_id"),
                  "approved_at": now_iso()})
        plan.__setitem__(i, t) if i is not None else plan.append(t)
        plan.sort(key=lambda x: _num(x["id"]))
    st[key] = {"state": "approved", "by": actor, "at": now_iso(), "version": int(prev.get("version") or 0) + 1}
    if via:
        st[key]["via"] = via                  # Hugo delegated the click (e.g. to Claude in the chat): recorded, not hidden
    (fr.get("pending") or {}).pop(key, None)


def _slide_map(before: dict | None, raw: dict, after: dict) -> tuple[dict, set]:
    """Slide ids are positions (S2.3 = third slide of S2), so an edit that reorders, inserts or removes slides moves
    them. Returns old id → new id (by the editor's prev_id, else by the same title) and the old ids that are gone."""
    if not before:
        return {}, set()
    by_title = {norm(x.get("title", "")): x["id"] for x in before.get("slides") or [] if x.get("title")}
    kept_raw = [x for x in (raw or {}).get("slides") or [] if (x.get("title") or "").strip() or (x.get("question") or "").strip()]
    mapping, kept = {}, set()
    for rs, ns in zip(kept_raw, after["slides"]):
        prev = rs.get("prev_id") or by_title.get(norm(rs.get("title", "")))
        if prev:
            kept.add(prev)
            if prev != ns["id"]:
                mapping[prev] = ns["id"]
    gone = {x["id"] for x in before.get("slides") or []} - kept
    return mapping, gone


def _retarget_slides(fr: dict, mapping: dict, gone: set) -> None:
    if not mapping and not gone:
        return
    tasks = list(fr.get("research_plan") or []) + [p["value"] for k, p in (fr.get("pending") or {}).items() if k.startswith("plan:")]
    for t in tasks:
        t["slides"] = list(dict.fromkeys(mapping.get(x, x) for x in t.get("slides") or [] if x not in gone or x in mapping))


def _save(store: CaseStore, fr: dict, *, actor: str, summary: str, material: bool = True) -> None:
    from . import framing_doc, phases
    framing_doc.save(store, fr, actor=actor, summary=summary, material=material)
    phases.touch(store, "framing", actor=actor)
    if actor == "hugo" and material and store.meta()["phases"]["framing"].get("status") == "ready":
        phases.set_status(store, "framing", "needs_review", actor=actor, note="el shaping cambió después de aprobarse")


def label(key: str, fr: dict | None = None) -> str:
    if key == "problem":
        return "Problema"
    kind, _, oid = key.partition(":")
    if kind == "guion":
        sec = _approved(fr or {}, key) or ((fr or {}).get("pending") or {}).get(key, {}).get("value") or {}
        return f"Guion · {oid}{' ' + sec.get('title') if sec.get('title') else ''}"
    return f"Tarea {oid}"


def approve(store: CaseStore, key: str, *, actor: str = "hugo") -> dict:
    if actor != "hugo":
        raise ValueError("Solo Hugo aprueba el shaping.")
    fr = _fr(store)
    p = (fr.get("pending") or {}).get(key)
    if not p:
        raise ValueError(f"No hay propuesta pendiente para {label(key, fr)}.")
    _apply(fr, key, p["value"], actor=actor)
    _save(store, fr, actor=actor, summary=f"Shaping · {label(key, fr)} aprobado")
    return state(store)


def approve_all(store: CaseStore, *, actor: str = "hugo", via: str = "", only: str = "") -> dict:
    """Approve every pending proposal (or only those whose key starts with `only`, e.g. "plan:")."""
    if actor != "hugo":
        raise ValueError("Solo Hugo aprueba el shaping.")
    fr = _fr(store)
    keys = [k for k in (fr.get("pending") or {}) if k.startswith(only)]
    for key in keys:
        _apply(fr, key, fr["pending"][key]["value"], actor=actor, via=via)
    if keys:
        _save(store, fr, actor=actor, summary=f"Shaping · {len(keys)} propuesta(s) aprobadas" + (f" ({via})" if via else ""))
    return state(store)


def discard(store: CaseStore, key: str, *, actor: str = "hugo") -> dict:
    fr = _fr(store)
    p = (fr.get("pending") or {}).pop(key, None)
    if not p:
        raise ValueError("No hay propuesta pendiente.")
    if key != "problem" and not _approved(fr, key):
        fr.setdefault("retired_ids", []).append(key.split(":", 1)[1])
    store.write_data("framing/current.yaml", fr)
    store.log(actor, "discarded", ["framing"], f"Shaping · Hugo descartó la propuesta para {label(key, fr)}", material=False)
    return state(store)


def set_section(store: CaseStore, key: str, value, *, actor: str = "hugo") -> dict:
    """Hugo writes (or rewrites) a Shaping section directly: approved as his."""
    fr = _fr(store)
    if key in ("guion:new", "plan:new"):
        key = f"guion:{next_section_id(fr)}" if key == "guion:new" else f"plan:{next_task_id(fr)}"
    if not (key == "problem" or key.startswith(("guion:", "plan:"))):
        raise ValueError(f"Sección de shaping desconocida: {key}")
    if key.startswith("plan:") and not ((value or {}).get("question") or "").strip():
        raise ValueError("La tarea necesita una pregunta.")
    if key.startswith("plan:"):
        value = {**value, "flags": []}
    _apply(fr, key, value, actor=actor)
    _save(store, fr, actor=actor, summary=f"Shaping · Hugo escribió {label(key, fr)}")
    return state(store)


def remove(store: CaseStore, key: str, *, actor: str = "hugo") -> dict:
    """Hugo removes an approved guion section or research task (the previous framing version keeps it)."""
    fr = _fr(store)
    kind, _, oid = key.partition(":")
    coll = "storyline_guide" if kind == "guion" else "research_plan" if kind == "plan" else None
    if not coll:
        raise ValueError("Solo se quitan secciones del guion o tareas del plan.")
    item = next((x for x in fr.get(coll) or [] if x.get("id") == oid), None)
    if not item:
        raise ValueError(f"{oid} no existe.")
    if item.get("status") == "sent":
        raise ValueError(f"{oid} ya se lanzó a Research ({item.get('research_id')}): recházala allá si ya no sirve.")
    fr[coll] = [x for x in fr[coll] if x.get("id") != oid]
    (fr.get("shaping_state") or {}).pop(key, None)
    fr.setdefault("retired_ids", []).append(oid)
    _save(store, fr, actor=actor, summary=f"Shaping · Hugo quitó {label(key, fr)}")
    return state(store)


# ------------------------------------------------------------------------------------------ research plan → Research
def send_task(store: CaseStore, task_id: str, *, actor: str = "hugo", via: str = "") -> dict:
    from . import research
    from .model import type_of
    fr = _fr(store)
    t = next((x for x in fr.get("research_plan") or [] if x["id"] == task_id), None)
    if not t:
        raise ValueError(f"{task_id} no está aprobada en el plan.")
    if t.get("status") == "sent":
        return {"task": t, "research_id": t.get("research_id"), "already": True}
    spec = KINDS[t["kind"]]["specialty"]
    route = {"specialty": spec, "intensity": "analytics" if spec == "analytics" else t.get("intensity") or "L2"}
    links = [x for x in t.get("links") or [] if type_of(x) in ("question", "hypothesis", "decision", "claim") and store.get(x)]
    out = research.create_request(store, t["question"], links=links, route=route, actor=actor, force_purpose=True, launch=True)
    r = out["research"]
    # an approved plan task has case purpose by construction: Hugo approved it in the Shaping document
    store.update(r["id"], {"shaping_task": task_id, "slides": t.get("slides") or [], "task_why": t.get("why", ""),
                           "task": {"work": t.get("work") or infer_work(t["kind"], t.get("steps") or []),
                                    "draft_answer": t.get("draft_answer", ""), "hugo_said": t.get("hugo_said") or [],
                                    "steps": t.get("steps") or []},
                           "purpose_ok": True, "purpose_note": "", "forced_without_purpose": False,
                           **({"requested_via": via} if via else {}),
                           "case_question": r.get("case_question") or f"Plan de investigación {task_id}"
                           + (f" · láminas {', '.join(t['slides'])}" if t.get("slides") else "")},
                 actor="system", material=False, summary=f"{r['id']} viene de la tarea {task_id} del shaping")
    fr = _fr(store)
    for x in fr.get("research_plan") or []:
        if x["id"] == task_id:
            x.update({"status": "sent", "research_id": r["id"], "sent_at": now_iso()})
    store.write_data("framing/current.yaml", fr)
    from . import framing_doc
    framing_doc.render_md(store)
    return {"task": task_id, "research_id": r["id"], "launched": out.get("launched"), "job_id": out.get("job_id")}


def send_all(store: CaseStore, *, actor: str = "hugo", via: str = "") -> list[dict]:
    return [send_task(store, t["id"], actor=actor, via=via) for t in (_fr(store).get("research_plan") or []) if t.get("status") == "approved"]


# ------------------------------------------------------------------------------------------ guards for agent-written tasks
def slide_ids(fr: dict) -> set[str]:
    """Every slide of the guion, approved or still proposed (tasks can be planned before Hugo approves the guion)."""
    ids = {sl["id"] for sec in fr.get("storyline_guide") or [] for sl in sec.get("slides") or []}
    for k, p in (fr.get("pending") or {}).items():
        if k.startswith("guion:"):
            ids |= {sl["id"] for sl in (p.get("value") or {}).get("slides") or []}
    return ids


def data_model(store: CaseStore):
    """The case's data model: the one Hugo chose in Briefing, else the one behind its analytics workspace; None if none."""
    from . import datamodels
    try:
        m = datamodels.for_case(store)
        if m is None and (store.meta().get("workspace") or {}).get("type") == "finora-eda":
            m = datamodels.get("finora")
        return m
    except ValueError:
        return None


def model_tables(store: CaseStore) -> set[str] | None:
    """Tables of the case's data model, or None when the case has none."""
    m = data_model(store)
    return {t["id"] for t in m.catalog()["tables"]} if m else None


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-záéíóúñü0-9]{4,}", norm(text or "")))


def quote_matches(quote: str, entity: dict) -> bool:
    """A quote attributed to Hugo must come from what he said in that item (his words, their history, or the item)."""
    q = _tokens(quote)
    if not q:
        return False
    said = " ".join([entity.get("hugo_wording") or "", *[h.get("text", "") for h in entity.get("hugo_wording_history") or []],
                     entity.get("text") or "", entity.get("statement") or "", entity.get("structured") or ""])
    return len(q & _tokens(said)) / len(q) >= 0.6


def guard_tasks(store: CaseStore, tasks: list[dict], fr: dict, *, context: str = "",
                fresh: list[str] = ()) -> tuple[list[dict], list[str]]:
    """What an agent writes into a task is checked before it becomes a proposal: slides and IDs must exist, a quote of
    Hugo must be his, "investigar datos" can only name tables the model has, and a number in the starting answer that
    the case context does not contain is flagged (the answer is a working hypothesis, not evidence). `fresh` are the
    items recorded in this same turn: the agent cannot know their IDs yet, so a quote of what Hugo just said is pointed
    to the item that holds those words."""
    from . import evidence
    ents = store.all()
    fresh = [ents[i] for i in fresh if i in ents and ents[i].get("verbatim") is not False and (ents[i].get("hugo_wording") or "").strip()]
    sids = slide_ids(fr)
    tables = model_tables(store)
    pool = [n.value for n in evidence.numbers_in(context)]
    out, notes = [], []
    for t in tasks:
        q = (t.get("question") or "").strip()
        if not q:
            continue
        flags = []
        bad = [x for x in t.get("slides") or [] if x not in sids]
        if bad:
            notes.append(f"«{clip(q, 60)}»: láminas que no existen en el guion ({', '.join(bad)}) se quitaron.")
        said = []
        for x in clean_said(t.get("hugo_said")):
            e = ents.get(x["ref"])
            if not (e and quote_matches(x["text"], e)):
                home = next((f for f in fresh if quote_matches(x["text"], {"hugo_wording": f["hugo_wording"]})), None)
                if home:
                    x, e = {**x, "ref": home["id"]}, home
            if not e:
                notes.append(f"Una cita atribuida a Hugo no tenía referencia válida ({x['ref'] or 'sin ID'}): se quitó.")
            elif e.get("verbatim") is False:
                notes.append(f"{x['ref']} es una paráfrasis del Framer, no palabras de Hugo: no se cita como suya.")
            elif not quote_matches(x["text"], e):
                notes.append(f"La cita atribuida a {x['ref']} no coincide con lo que Hugo dijo ahí: se quitó.")
            else:
                said.append(x)
        steps = []
        for st in clean_steps(t.get("steps")):
            if st["kind"] == "data":
                if tables is None:
                    flags.append("El caso no tiene modelo de datos: el paso de datos queda como dato por pedir.")
                    st = {**st, "where": []}
                else:
                    unknown = [w for w in st["where"] if w not in tables]
                    if unknown:
                        notes.append(f"«{clip(q, 50)}»: tablas que no existen en el modelo ({', '.join(unknown)}) se quitaron.")
                    st = {**st, "where": [w for w in st["where"] if w in tables]}
            steps.append(st)
        kind = t.get("kind") if t.get("kind") in KINDS else "research"
        if kind == "data" and tables is None:
            notes.append(f"«{clip(q, 50)}» pedía datos y el caso no tiene modelo de datos: queda como research.")
            kind = "research"
        draft = (t.get("draft_answer") or "").strip()
        loose = [n.raw for n in evidence.numbers_in(draft) if not evidence.supported(n, pool)] if draft else []
        if loose:
            flags.append("Cifra sin fuente en el contexto del caso: " + ", ".join(loose))
        out.append({**t, "question": q, "kind": kind, "draft_answer": draft, "hugo_said": said, "steps": steps,
                    "slides": [x for x in t.get("slides") or [] if x in sids],
                    "links": [x for x in t.get("links") or [] if x in ents], "flags": flags})
    return out, notes


def supersede_pending_tasks(fr: dict) -> list[str]:
    """A new plan replaces every task proposal Hugo has not approved yet — new tasks and proposed changes to approved
    ones alike (the previous framing version keeps them). Approved tasks stay as they are."""
    gone = [k for k in list((fr.get("pending") or {})) if k.startswith("plan:")]
    for k in gone:
        fr["pending"].pop(k)
        if not _approved(fr, k):
            fr.setdefault("retired_ids", []).append(k.split(":", 1)[1])
    return [k.split(":", 1)[1] for k in gone]


# ------------------------------------------------------------------------------------------ view
def state(store: CaseStore) -> dict:
    fr = _fr(store)
    pend = fr.get("pending") or {}
    st = fr.get("shaping_state") or {}
    guide_ids = [s["id"] for s in fr.get("storyline_guide") or []]
    new_secs = [k.split(":", 1)[1] for k in pend if k.startswith("guion:") and k.split(":", 1)[1] not in guide_ids]
    sections = [{"key": f"guion:{s['id']}", "approved": s, "pending": pend.get(f"guion:{s['id']}"), "meta": st.get(f"guion:{s['id']}")}
                for s in fr.get("storyline_guide") or []]
    sections += [{"key": f"guion:{sid}", "approved": None, "pending": pend[f"guion:{sid}"], "meta": None} for sid in new_secs]
    sections.sort(key=lambda e: _num(e["key"].split(":", 1)[1]))
    plan_ids = [t["id"] for t in fr.get("research_plan") or []]
    tasks = [{"key": f"plan:{t['id']}", "approved": t, "pending": pend.get(f"plan:{t['id']}"), "meta": st.get(f"plan:{t['id']}")}
             for t in fr.get("research_plan") or []]
    tasks += [{"key": k, "approved": None, "pending": v, "meta": None} for k, v in pend.items()
              if k.startswith("plan:") and k.split(":", 1)[1] not in plan_ids]
    tasks.sort(key=lambda e: _num(e["key"].split(":", 1)[1]))
    approved_tasks = [t for t in fr.get("research_plan") or []]
    from . import briefing
    b = briefing.get(store)
    structural = _structural(b.get("deliverables"))
    legacy_rn = [r for r in fr.get("research_needed") or [] if r.get("status", "pending") == "pending"]
    migratable = {"guion": len(parse_structure(structural)) if structural and not fr.get("storyline_guide") and not new_secs else 0,
                  "plan": len(legacy_rn) if legacy_rn and not fr.get("research_plan") and not any(k.startswith("plan:") for k in pend) else 0,
                  "brief_structure": len(structural), "brief_pending": bool((b.get("pending") or {}).get("deliverables"))}
    slide_tasks: dict[str, list[dict]] = {}
    for e in tasks:
        v = e["approved"] or e["pending"]["value"]
        status = ("sent" if (e["approved"] or {}).get("status") == "sent" else "approved") if e["approved"] else "proposed"
        for sl in v.get("slides") or []:
            slide_tasks.setdefault(sl, []).append({"id": v["id"], "status": status})
    from .util import read_jsonl
    runs = read_jsonl(store.root / PLAN_RUNS, limit=10)
    return {"problem": {"key": "problem", "approved": fr.get("problem") or None, "pending": pend.get("problem"), "meta": st.get("problem")},
            "guion": sections, "plan": tasks, "pending": len(pend), "kinds": KINDS, "work": WORK, "step_kinds": STEP_KINDS,
            "slide_tasks": slide_tasks, "plan_run": runs[-1] if runs else None,
            "progress": {"problem": not _empty(fr.get("problem") or {}), "guion_sections": len(fr.get("storyline_guide") or []),
                         "slides": sum(len(s.get("slides") or []) for s in fr.get("storyline_guide") or []),
                         "tasks_approved": sum(1 for t in approved_tasks if t.get("status") == "approved"),
                         "tasks_sent": sum(1 for t in approved_tasks if t.get("status") == "sent"),
                         "tasks_proposed": sum(1 for k in pend if k.startswith("plan:"))},
            "legacy_storyline": fr.get("initial_storyline") or [], "migratable": migratable}


def guide_text(store: CaseStore, *, limit: int = 6000) -> str:
    """The approved Guion as plain text for other agents (COS, Storyteller)."""
    fr = _fr(store)
    lines = []
    for s in fr.get("storyline_guide") or []:
        lines.append(f"{s['id']} · {s.get('title')}" + (f" — {' · '.join(x.strip() for x in s['purpose'].splitlines() if x.strip())}" if s.get("purpose") else ""))
        for sl in s.get("slides") or []:
            lines.append(f"  {sl['id']} · {sl.get('title')}" + (f" | pregunta: {sl['question']}" if sl.get("question") else "")
                         + (f" | debe mostrar: {clip(sl['intent'], 400)}" if sl.get("intent") else "")
                         + (f" | notas de Hugo: {clip(sl['notes'], 200)}" if sl.get("notes") else ""))
    return clip("\n".join(lines), limit)


# ------------------------------------------------------------------------------------------ migration (proposals only)
_SEC = re.compile(r"(?:^|[·•])\s*(\d+)\s+([^—–-]+?)\s*[—–-]\s*(.+)$", re.S)
_SLIDE = re.compile(r"\bL(\d+)\s*:\s*")
_ASK = re.compile(r"^(qué|que|cómo|como|dónde|donde|cuánto|cuanto|cuál|cual|por qué|hasta dónde|hasta donde|quién|quien)\b", re.I)


def _structural(deliverables) -> list[str]:
    """Deliverables items that are really the storyline (sections and slides), not something to hand in."""
    return [d for d in deliverables or [] if _SEC.search(d or "") and ("L1:" in d or re.search(r"[·•]\s*\d+\s+\w", d or ""))]


def parse_structure(items: list[str]) -> list[dict]:
    """Deliverables items shaped like '… · 2 Growth — L1: … L2: …' → guion sections with slides (deterministic)."""
    out = []
    for it in items or []:
        m = _SEC.search(it or "")
        if not m:
            continue
        title, body = m.group(2).strip(), m.group(3).strip()
        parts = _SLIDE.split(body)
        slides = []
        if len(parts) > 1:
            for num, text in zip(parts[1::2], parts[2::2]):
                text = text.strip().rstrip(".").strip()
                first = re.split(r"[:;(]|\. ", text, maxsplit=1)[0].strip()
                t = first if 12 <= len(first) <= 120 else clip(text, 90)
                q = (f"¿{t[0].upper()}{t[1:]}?" if _ASK.match(t) else "")
                slides.append({"title": t[0].upper() + t[1:] if t else f"Lámina {num}", "question": q, "intent": text,
                               "notes": f"Migrado de Entregables del brief (L{num})."})
        else:
            text = body.rstrip(".")
            slides.append({"title": title, "question": "", "intent": text, "notes": "Migrado de Entregables del brief."})
        out.append({"title": title, "purpose": clip(parts[0].strip(), 300) if len(parts) > 1 and parts[0].strip() else "", "slides": slides})
    return out


def migrate(store: CaseStore, *, actor: str = "caseos") -> dict:
    """Hugo asked (29-sep) to move his storyline out of the brief's deliverables and to turn 'research needed' into typed
    research tasks. Everything lands as PENDING proposals: nothing approved changes until Hugo approves."""
    from . import briefing
    from .research import heuristic_route
    fr = _fr(store)
    b = briefing.get(store)
    made = {"guion": [], "plan": [], "deliverables": False}
    structural = _structural(b.get("deliverables"))
    if structural and not fr.get("storyline_guide") and not any(k.startswith("guion:") for k in fr.get("pending") or {}):
        legacy = fr.get("initial_storyline") or []
        for sec in parse_structure(structural):
            # a provisional storyline line belongs to a section when it opens with its name ("Growth, lo que sí vemos: …")
            t = norm(sec["title"])
            hint = [x for x in legacy if t and t in norm(re.split(r"[:—–]", x, maxsplit=1)[0])]
            if hint and not sec["purpose"]:
                sec["purpose"] = clip("\n".join(hint), 900)
            sid = next_section_id(fr)
            if propose(store, f"guion:{sid}", sec, basis="brief · Entregables aprobados", fr=fr, save=False,
                       why="Tu estructura estaba dentro de Entregables del brief; aquí queda como Guion para que el COS y el Storyteller la sigan.",
                       actor=actor):
                made["guion"].append(sid)
    rn = [r for r in fr.get("research_needed") or [] if r.get("status", "pending") == "pending"]
    if rn and not fr.get("research_plan") and not any(k.startswith("plan:") for k in fr.get("pending") or {}):
        spec_to_kind = {v["specialty"]: k for k, v in KINDS.items()}
        for r in rn:
            route = heuristic_route(store, r.get("question", ""), r.get("links"))
            kind = spec_to_kind.get(route["specialty"], "research")
            tid = next_task_id(fr)
            if propose(store, f"plan:{tid}", {"question": r.get("question", ""), "kind": kind, "intensity": route.get("intensity"),
                                              "why": r.get("why", ""), "links": r.get("links") or [], "slides": []},
                       basis="research necesario del Framer", why=f"Tipo sugerido por el Router: {KINDS[kind]['label']}. Cámbialo si no es.",
                       fr=fr, save=False, actor=actor):
                made["plan"].append(tid)
    store.write_data("framing/current.yaml", fr)
    if structural:
        keep = [d for d in b.get("deliverables") or [] if d not in structural]
        keep.insert(1 if keep else 0, "Material de soporte: estructura de secciones y láminas en Framing & Shaping › Guion de la historia.")
        made["deliverables"] = briefing.propose(store, "deliverables", keep, basis="reorganizado", actor=actor,
                                                why="Tu guion se movió al Shaping; Entregables vuelve a decir solo qué se entrega.")
    from . import framing_doc
    framing_doc.render_md(store)
    store.log(actor, "proposed", ["framing"], f"Migración pedida por Hugo: {len(made['guion'])} sección(es) del guion y "
              f"{len(made['plan'])} tarea(s) de investigación propuestas" + (" · Entregables limpios propuestos en el brief" if made["deliverables"] else ""),
              material=True)
    return made
