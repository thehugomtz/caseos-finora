"""Story Package: from a mature case to the contract the Executive Visual Storyteller consumes.

The COS drafts the package (skill story-package); code assembles, validates and persists it:
story/package.yaml (the contract), story/current.md (readable), claims as C- entities with lineage to evidence (F),
tables (T), research (R) and frameworks (D). Validation blocks Story Ready when a claim has no accepted evidence,
a number has no table, or something it depends on is marked needs_review.
"""
from __future__ import annotations

import re

from . import cases, cos, jobs, phases, skills
from .agents import base
from .evidence import numbers_in, unsupported_numbers, validate_table, verbal_ratio_issues
from .llm import RunSpec, get_llm
from .model import title_of, type_of
from .store import CaseStore
from .util import clip, norm, now_iso, yaml_dump

ROLES = ["context", "evidence", "diagnosis", "implication", "recommendation", "limitation"]
CAUSAL = re.compile(r"\b(causa(do|n|ron)?|provoc[aó]|debido a|porque|gracias a|result[oó] en|impuls[aó]|genera(ron)?)\b", re.I)

_S = {"type": "string"}
_SA = {"type": "array", "items": _S}


def _obj(props):
    return {"type": "object", "additionalProperties": False, "required": list(props), "properties": props}


SCHEMA = _obj({
    "audience": _SA, "objective": _S, "from_to": _obj({"from": _S, "to": _S}),
    "governing_thought": _S,
    "executive_questions": {"type": "array", "items": _obj({"id": _S, "text": _S})},
    "story_arc": _obj({"archetype": _S, "logic": _S}),
    "sections": {"type": "array", "items": _obj({"name": _S, "purpose": _S, "claim_keys": _SA})},
    "claims": {"type": "array", "items": _obj({
        "key": _S, "question": _S, "headline": _S, "answer": _S,
        "role_in_story": {"type": "string", "enum": ROLES}, "evidence_ids": _SA, "table_ids": _SA, "research_ids": _SA,
        "framework_ids": _SA, "confidence": {"type": "string", "enum": ["high", "medium", "low"]}, "limitations": _SA,
        "visual_intent": _S, "hugo_wording": _S})},
    "recommendations": {"type": "array", "items": _obj({"text": _S, "condition": _S,
                                                         "type": {"type": "string", "enum": ["validate", "request_data", "experiment", "decide", "act"]},
                                                         "claim_keys": _SA})},
    "appendix_candidates": {"type": "array", "items": _obj({"title": _S, "why": _S, "ids": _SA})},
    "unresolved_questions": _SA, "visual_references": _SA,
})


# ------------------------------------------------------------------------------------------ validation
def validate_package(store: CaseStore, pkg: dict) -> tuple[list[str], list[str]]:
    ents = store.all()
    errors, warnings = [], []
    for k in ("audience", "objective", "governing_thought", "claims"):
        if not pkg.get(k):
            errors.append(f"El Story Package no tiene '{k}'.")
    claims = pkg.get("claims") or []
    all_tables = []
    for c in claims:
        cid = c.get("claim_id") or c.get("key")
        role = c.get("role_in_story")
        ev = c.get("evidence_ids") or []
        tb = c.get("table_ids") or []
        for i in ev + tb + (c.get("research_ids") or []) + (c.get("framework_ids") or []):
            if i not in ents:
                errors.append(f"{cid}: {i} no existe.")
        acc = [i for i in ev if i in ents and (ents[i].get("review") or {}).get("state") == "accepted"]
        if role not in ("recommendation", "limitation") and not acc:
            errors.append(f"{cid}: claim sin evidencia aceptada (unsupported claim).")
        notacc = [i for i in ev if i in ents and (ents[i].get("review") or {}).get("state") != "accepted"]
        if notacc:
            errors.append(f"{cid}: evidencia no aceptada {', '.join(notacc)}.")
        tables = [ents[t] for t in tb if t in ents]
        all_tables += tables
        for t in tables:
            errs = validate_table(t)
            if errs:
                errors.append(f"{cid}: la tabla {t['id']} no cumple el contrato ({'; '.join(errs[:2])}).")
        text = f"{c.get('headline', '')} {c.get('answer', '')}"
        unsup = unsupported_numbers(text, tables)
        if unsup:
            errors.append(f"{cid}: cifra(s) sin tabla que las respalde: {', '.join(unsup[:5])}.")
        verr, vwarn = verbal_ratio_issues(text, tables)
        errors += [f"{cid}: cantidad con letras {e}." for e in verr]
        warnings += [f"{cid}: cantidad con letras {w}." for w in vwarn]
        stale = [i for i in ev + tb if i in ents and ents[i].get("stale")]
        if stale:
            errors.append(f"{cid}: depende de elementos marcados needs_review ({', '.join(stale)}).")
        if c.get("confidence") in ("medium", "low") and not c.get("limitations"):
            warnings.append(f"{cid}: confianza {c.get('confidence')} sin limitaciones escritas.")
        if CAUSAL.search(text) and role not in ("recommendation",):
            warnings.append(f"{cid}: lenguaje causal («{CAUSAL.search(text).group(0)}») — la evidencia es observacional.")
        if len((c.get("headline") or "").split()) > 18:
            warnings.append(f"{cid}: titular largo ({len(c['headline'].split())} palabras); el Storyteller lo recortará.")
    gt = pkg.get("governing_thought") or ""
    gt_unsup = unsupported_numbers(gt, all_tables)
    if gt_unsup:
        errors.append(f"Governing thought con cifras sin tabla: {', '.join(gt_unsup)}.")
    if len(gt.split()) > 30:
        warnings.append(f"Governing thought de {len(gt.split())} palabras (objetivo ≤ 25).")
    if not pkg.get("language_profile"):
        warnings.append("El paquete no incluye el perfil de lenguaje.")
    return errors, warnings


# ------------------------------------------------------------------------------------------ generation (COS)
def submit_package(store: CaseStore, *, instructions: str = "") -> dict:
    job = jobs.submit(store.id, "story_package", "COS prepara el Story Package", {"instructions": instructions}, agent="cos")
    store.log("hugo", "requested", ["story"], "Hugo pidió preparar el Story Package")
    return {"job_id": job.id}


def _evidence_block(store: CaseStore) -> str:
    ents = store.all()
    acc_f = [f for f in ents.values() if f.get("type") == "finding" and (f.get("review") or {}).get("state") == "accepted"]
    tabs = [t for t in ents.values() if t.get("type") == "table" and (t.get("review") or {}).get("state") != "rejected" and t.get("status") == "valid"]
    lines = ["## Findings aceptados (solo estos pueden sostener claims)"]
    for f in sorted(acc_f, key=lambda e: e["id"]):
        tids = [l for l in f.get("links") or [] if type_of(l) == "table"]
        lines.append(f"- {f['id']}{' (' + f['alias'] + ')' if f.get('alias') else ''} [{f.get('confidence', '')}] {clip(title_of(f), 260)}"
                     + (f" · tablas: {', '.join(tids)}" if tids else " · sin tabla"))
    lines.append("\n## Tablas canónicas válidas (toda cifra que escribas debe estar en una de las tablas del claim)")
    for t in sorted(tabs, key=lambda e: e["id"]):
        cols = t.get("columns") or []
        rows = t.get("rows") or []
        preview = rows if len(rows) <= 8 else rows[:3] + [["…"]] + rows[-3:]
        lines.append(f"- {t['id']} `{t.get('table_key')}` — {t.get('title')}\n  columnas: {cols}\n  filas: {preview}\n  mensaje: {t.get('message')}")
    return "\n".join(lines)


@jobs.handler("story_package")
async def _job(job, params):
    store = cases.get(job.case_id)
    selected = skills.select("cos", text="story package storyline historia")
    system = base.system_prompt("cos", selected, store.meta().get("language"),
                                extra="Tarea: redacta el Story Package para el Executive Visual Storyteller (skill story-package).")
    prev = store.read_data("story/package.yaml") or {}
    fr = store.read_data("framing/current.yaml", {}) or {}
    prompt = (f"Instrucciones de Hugo: {params.get('instructions') or '—'}\n\n"
              f"Pregunta ejecutiva: {fr.get('executive_question')}\nNo afirmar todavía: {'; '.join(fr.get('should_not_claim') or [])}\n\n"
              + _evidence_block(store) + "\n\n" + cos.digest(store) +
              ("\n\n## Paquete anterior (mejóralo, conserva las keys de los claims que sigan vigentes)\n" + yaml_dump(prev)[:12000] if prev else "") +
              "\n\nReglas: cada claim de evidencia cita findings ACEPTADOS (evidence_ids) y las tablas (table_ids) donde está cada cifra "
              "que escribas; si una cifra no está en una tabla, no la escribas. Nada de cantidades con letras («a la mitad», «el doble», "
              "«por cuatro») salvo que coincidan con las cifras de la tabla: prefiere la cifra. Lenguaje asociativo, no causal. Recomendaciones condicionales. "
              "keys de claims estables y cortas (p. ej. 'arpa-mix'). Máximo 8 claims.")
    spec = RunSpec(agent="cos", role="story", system=system, prompt=prompt, schema=SCHEMA, max_turns=4,
                   skills=skills.record(selected), purpose="Story Package", case_id=store.id, case_root=store.root)
    res = await get_llm().run(spec, lambda k, d: job.event(k, d))
    return apply_package(store, res.output, run_id=res.run_id, actor="cos")


def apply_package(store: CaseStore, out: dict, *, run_id: str | None = None, actor: str = "cos") -> dict:
    ents = store.all()
    existing = {c.get("key"): c for c in ents.values() if c.get("type") == "claim" and c.get("key")}
    claim_ids, key_to_id = [], {}
    with store.batch():
        for c in out.get("claims") or []:
            ev = [i for i in c.get("evidence_ids") or [] if i in ents]
            tb = [i for i in c.get("table_ids") or [] if i in ents]
            rs = [i for i in c.get("research_ids") or [] if i in ents]
            fw = [i for i in c.get("framework_ids") or [] if i in ents]
            data = {"key": c["key"], "question": c.get("question", ""), "headline": c["headline"], "answer": c.get("answer", ""),
                    "role_in_story": c.get("role_in_story"), "evidence_ids": ev, "table_ids": tb, "research_ids": rs,
                    "framework_ids": fw, "confidence": c.get("confidence"), "limitations": c.get("limitations") or [],
                    "visual_intent": c.get("visual_intent", ""), "hugo_wording": c.get("hugo_wording", ""),
                    "links": list(dict.fromkeys(ev + tb + rs + fw)), "phase": "story"}
            if c["key"] in existing:
                e = existing[c["key"]]
                changed = any(e.get(k) != data[k] for k in ("headline", "answer", "evidence_ids", "table_ids"))
                if changed:
                    e = store.update(e["id"], {**data, "review": {"state": "proposed"}}, actor=actor, run_id=run_id,
                                     summary=f"{e['id']} actualizado en el Story Package")
            else:
                e = store.create("claim", data, actor=actor, run_id=run_id, summary=f"Claim propuesto: {clip(c['headline'], 90)}")
            claim_ids.append(e["id"])
            key_to_id[c["key"]] = e["id"]
        for e in ents.values():
            if e.get("type") == "claim" and e.get("key") and e["key"] not in key_to_id and e.get("status") != "superseded":
                store.update(e["id"], {"status": "superseded"}, actor=actor, summary=f"{e['id']} fuera del paquete nuevo",
                             material=False)
        ents = store.all()
        for cid in claim_ids:
            s = cos.claim_strength(store, ents[cid], ents)
            store.update(cid, {"status": {"supported": "supported", "weak": "weak", "unsupported": "unsupported",
                                          "proposal": "supported"}[s["level"]], "strength": s}, actor="system", material=False,
                         verb="scored", summary=f"{cid}: {s['level']}")
        meta = store.meta()
        pkg = {"story_package": True, "version": int((store.read_data("story/package.yaml") or {}).get("version") or 0) + 1,
               "generated_at": now_iso(), "generated_by": actor, "run_id": run_id,
               "audience": out.get("audience") or [], "objective": out.get("objective", ""), "from_to": out.get("from_to") or {},
               "governing_thought": out.get("governing_thought", ""),
               "executive_questions": out.get("executive_questions") or [], "story_arc": out.get("story_arc") or {},
               "sections": [{**s, "claim_ids": [key_to_id[k] for k in s.get("claim_keys") or [] if k in key_to_id]} for s in out.get("sections") or []],
               "claims": [], "recommendations": [{**r, "claim_ids": [key_to_id[k] for k in r.get("claim_keys") or [] if k in key_to_id]}
                                                 for r in out.get("recommendations") or []],
               "appendix_candidates": out.get("appendix_candidates") or [], "unresolved_questions": out.get("unresolved_questions") or [],
               "language_profile": meta.get("language") or {}, "visual_references": out.get("visual_references") or []}
        ents = store.all()
        for cid in claim_ids:
            c = ents[cid]
            pkg["claims"].append({"claim_id": cid, "key": c.get("key"), "question": c.get("question"), "headline": c.get("headline"),
                                  "answer": c.get("answer"), "role_in_story": c.get("role_in_story"),
                                  "evidence_ids": c.get("evidence_ids") or [], "table_ids": c.get("table_ids") or [],
                                  "research_ids": c.get("research_ids") or [], "framework_ids": c.get("framework_ids") or [],
                                  "confidence": c.get("confidence"), "limitations": c.get("limitations") or [],
                                  "visual_intent": c.get("visual_intent"), "hugo_wording": c.get("hugo_wording") or "",
                                  "strength": (c.get("strength") or {}).get("level")})
        errors, warnings = validate_package(store, pkg)
        pkg["validation"] = {"ok": not errors, "errors": errors, "warnings": warnings, "checked_at": now_iso()}
        prev = store.read_data("story/package.yaml")
        if prev:
            store.write_data(f"story/versions/package.v{prev.get('version', 0)}.yaml", prev)
        store.write_data("story/package.yaml", pkg)
        render_md(store)
        phases.touch(store, "story", actor=actor)
        if not errors:
            phases.propose_review(store, "story", actor=actor, note="Story Package válido listo para revisión")
        store.log(actor, "story", claim_ids, f"Story Package v{pkg['version']}: {len(claim_ids)} claims · "
                  + ("válido" if not errors else f"{len(errors)} problema(s) a resolver"), material=True, run_id=run_id)
    return {"version": pkg["version"], "claims": claim_ids, "errors": errors, "warnings": warnings}


def revalidate(store: CaseStore) -> dict:
    pkg = store.read_data("story/package.yaml")
    if not pkg:
        return {"ok": False, "errors": ["No hay Story Package."], "warnings": []}
    ents = store.all()
    for c in pkg.get("claims") or []:
        e = ents.get(c.get("claim_id"))
        if e:
            for k in ("headline", "answer", "evidence_ids", "table_ids", "limitations", "confidence", "visual_intent"):
                c[k] = e.get(k, c.get(k))
            c["strength"] = cos.claim_strength(store, e, ents)["level"]
    errors, warnings = validate_package(store, pkg)
    pkg["validation"] = {"ok": not errors, "errors": errors, "warnings": warnings, "checked_at": now_iso()}
    store.write_data("story/package.yaml", pkg)
    render_md(store)
    return pkg["validation"]


def render_md(store: CaseStore) -> str:
    pkg = store.read_data("story/package.yaml", {}) or {}
    ents = store.all()
    md = [f"# CURRENT STORY — v{pkg.get('version', 0)}", f"> Generado {str(pkg.get('generated_at', ''))[:16]} · "
          + ("válido" if (pkg.get("validation") or {}).get("ok") else "con problemas de validación"), "",
          "## Audiencia", ", ".join(pkg.get("audience") or []) or "_—_", "",
          "## Objetivo", pkg.get("objective") or "_—_", ""]
    ft = pkg.get("from_to") or {}
    if ft:
        md += ["## De → A", f"- **Hoy creen:** {ft.get('from', '')}", f"- **Deben salir creyendo:** {ft.get('to', '')}", ""]
    md += ["## Governing thought", f"> {pkg.get('governing_thought') or '—'}", "",
           "## Preguntas ejecutivas"] + [f"- {q.get('id') + ' ' if q.get('id') else ''}{q.get('text')}" for q in pkg.get("executive_questions") or []]
    arc = pkg.get("story_arc") or {}
    md += ["", "## Arco", f"{arc.get('archetype', '')} — {arc.get('logic', '')}", ""]
    for s in pkg.get("sections") or []:
        md += [f"### {s.get('name')}", f"_{s.get('purpose', '')}_", ""]
        for cid in s.get("claim_ids") or []:
            c = next((x for x in pkg.get("claims") or [] if x["claim_id"] == cid), None)
            if not c:
                continue
            md += [f"**{cid} · {c['headline']}**", "", f"{c.get('answer', '')}", "",
                   f"- Pregunta: {c.get('question', '')}", f"- Rol: {c.get('role_in_story')} · confianza {c.get('confidence')} · fuerza {c.get('strength')}",
                   f"- Evidencia: {', '.join(c.get('evidence_ids') or []) or '—'} · Tablas: {', '.join(c.get('table_ids') or []) or '—'}",
                   f"- Intención visual: {c.get('visual_intent', '')}"]
            md += [f"- Limitación: {x}" for x in c.get("limitations") or []]
            if c.get("hugo_wording"):
                md.append(f"- En palabras de Hugo: “{c['hugo_wording']}”")
            md.append("")
    md += ["## Recomendaciones"] + [f"- {r.get('text')} _(si {r.get('condition')})_" if r.get("condition") else f"- {r.get('text')}"
                                    for r in pkg.get("recommendations") or []]
    md += ["", "## Apéndice candidato"] + [f"- {a.get('title')} — {a.get('why')}" for a in pkg.get("appendix_candidates") or []]
    md += ["", "## Preguntas sin resolver"] + [f"- {q}" for q in pkg.get("unresolved_questions") or []]
    v = pkg.get("validation") or {}
    if v.get("errors") or v.get("warnings"):
        md += ["", "## Validación"] + [f"- ✖ {e}" for e in v.get("errors") or []] + [f"- ⚠ {w}" for w in v.get("warnings") or []]
    text = "\n".join(md) + "\n"
    store.write_text("story/current.md", text)
    return text


def claim_numbers(c: dict) -> list[str]:
    return [n.raw for n in numbers_in(f"{c.get('headline', '')} {c.get('answer', '')}")]


def words(text: str) -> int:
    return len(norm(text).split())
