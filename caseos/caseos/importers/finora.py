"""Instantiate Finora as the first CaseOS case — from what actually exists, with lineage.

Sources (read-only):
- Hugo's working brief v0.3 (source of truth, 28-sep-2026) → brief, framing, questions, hypotheses, Hugo's points,
  structure decisions (transcribed in finora_seed.yaml with section-level provenance).
- finora-eda (Business Exploration Workspace) → case-question answers W0–W5 (+ blocked W6/W7), golden Q2
  investigation, 39 canonical findings verified in code, supporting CSVs → research, findings, evidence tables.
- Project notes (Claude's session memory) → four decisions, imported as PROPOSED for Hugo to confirm.

Nothing is invented: what is missing is declared as a gap. Imported work is proposed for Hugo's review; phases stay
where Hugo left them (brief and framing in review, research in progress).

    .venv/bin/python -m caseos import-finora [--force]
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .. import brain, cases, framing_doc, phases
from ..decisions import record_decision
from ..evidence import make_table, validate_table
from ..store import CaseStore
from ..util import now_iso, read_yaml
from ..workspaces.finora_eda import FinoraWorkspace

SEED = Path(__file__).with_name("finora_seed.yaml")
BRIEF_HTML = Path.home() / "Documents" / "Codex" / "2026-09-28" / "new-chat" / "outputs" / "alegra_brief_de_trabajo.html"
BRIEF_V04 = BRIEF_HTML.with_name("alegra_brief_v0_4_archivo.html")
ACTOR = "import"
CONF = {"Hecho observado": "high", "Evidencia fuerte": "high", "Direccional": "medium", "Exploratorio": "low",
        "Precaución": "low"}


def _prov(source: str, **kw) -> dict:
    return {"source": source, "imported_at": now_iso(), **kw}


def run(force: bool = False, ws_path: Path | None = None) -> CaseStore:
    seed = read_yaml(SEED)
    root = cases.cases_dir() / "finora"
    if root.exists():
        if not force:
            raise SystemExit("El caso 'finora' ya existe. Usa --force para reimportarlo (se borra y se vuelve a crear).")
        shutil.rmtree(root)
        cases.forget("finora")
    ws = FinoraWorkspace(ws_path or (cases.config.FINORA_EDA_PATH))
    b = seed["brief"]
    store = cases.create_case(
        name="Finora", title=b["title"], client=b["client"], objective=b["objective"], audience=b["audience"],
        context=b["context"], deliverables=b["deliverables"], constraints=b["constraints"], case_id="finora",
        language={"primary": "es", "tone": "direct, conversational", "technical_level": "adaptive",
                  "preserve_user_vocabulary": True, "avoid_unnecessary_jargon": True, "structured_language": "es",
                  "observed": {"register": "conversacional, directo; mezcla español con términos de negocio en inglés",
                               "technical_level": "analítico", "formality": "tú",
                               "preserved_terms": ["leads", "funnel", "MRR", "churn", "self-serve", "SQL directo", "post-SQL",
                                                   "New", "primer pagador observado", "monto observado", "MECE",
                                                   "impacto × capacidad", "CRO", "CFO"],
                               "notes": ["Perfil inicial derivado del brief v0.3 (sección «Lo tuyo») y de las notas del proyecto."]}},
        workspace={"type": "finora-eda", "path": "../finora-eda", "label": "Finora · Business Exploration Workspace"},
        actor=ACTOR)
    with store.batch():
        _brief(store, seed)
        ids = _framing(store, seed, ws)
        _research(store, ws, ids)
        _tables(store, ws, ids)
        _artifacts(store, ws)
        phases.set_status(store, "briefing", "review", actor=ACTOR, note="brief importado; pendiente de Mark Ready")
        phases.set_status(store, "framing", "review", actor=ACTOR, note="framing v0.3 importado; pendiente de Mark Ready")
        phases.set_status(store, "research", "in_progress", actor=ACTOR,
                          note="W0–W5 respondidas en el workspace antes de CaseOS; W6/W7 bloqueadas")
        store.log(ACTOR, "imported", ["finora"], "Caso Finora importado desde el brief v0.3 y el Business Exploration Workspace",
                  material=True, data={"entities": len(store.all())})
    brain.update(store, "importación inicial del caso Finora")
    return store


# ------------------------------------------------------------------------------------------ brief
def _brief(store: CaseStore, seed: dict) -> None:
    b = seed["brief"]
    src_dir = store.root / "brief" / "sources"
    src_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    for p, label in ((BRIEF_HTML, "Brief de trabajo v0.3 en lenguaje claro (fuente de verdad, 28-sep-2026)"),
                     (BRIEF_V04, "Brief v0.4 corto (archivo)")):
        if p.exists():
            shutil.copy2(p, src_dir / p.name)
            sources.append({"title": label, "path": f"brief/sources/{p.name}", "origin": str(p).replace(str(Path.home()), "~")})
        else:
            sources.append({"title": label, "path": None, "origin": str(p).replace(str(Path.home()), "~"),
                            "note": "no encontrado en esta máquina"})
    sources.append({"title": "Notas del proyecto (memoria de sesión de Claude, 27–28 sep 2026)", "path": None,
                    "note": "resumen del enunciado de Alegra; el enunciado literal no está en el repositorio"})
    brief = store.read_data("brief/brief.yaml", {})
    brief.update({"title": b["title"], "client": b["client"], "company": b["company"], "objective": b["objective"],
                  "audience": b["audience"], "audience_note": b["audience_note"], "context": b["context"],
                  "deliverables": b["deliverables"], "constraints": b["constraints"], "data_available": b["data_available"],
                  "success_criteria": b["success_criteria"], "gaps": b["gaps"], "sources": sources,
                  "provenance": {"objective": b["objective_source"], "context": b["context_source"],
                                 "deliverables": b["deliverables_source"]}})
    store.write_data("brief/brief.yaml", brief)
    from ..briefing import render_md
    render_md(store)


# ------------------------------------------------------------------------------------------ framing
def _framing(store: CaseStore, seed: dict, ws: FinoraWorkspace) -> dict:
    ids: dict[str, str] = {}
    src = seed["source_doc"]
    for q in seed["executive_questions"]:
        e = store.create("question", {"text": q["text"], "kind": "executive", "audience": q["audience"], "status": "open",
                                      "alias": q["key"], "note": q.get("note", "")},
                         actor=ACTOR, origin=_prov(q["source"]), summary=f"Pregunta ejecutiva {q['key']} importada", material=False)
        ids[q["key"]] = e["id"]
    for br in seed["branches"]:
        e = store.create("question", {"text": br["text"], "kind": "branch", "scope": br["scope"], "status": "open",
                                      "alias": br["key"], "links": [ids[br["parent"]]]},
                         actor=ACTOR, origin=_prov(br["source"]), material=False)
        ids[br["key"]] = e["id"]
    for h in seed["hypotheses"]:
        parent = ids.get(h["branch"]) or ids.get({"OBS": "CEO"}.get(h["branch"], ""), "")
        links = [x for x in [parent] if x]
        if h["branch"] == "OBS":
            links = [ids["CRO"], ids["CFO"]]
        e = store.create("hypothesis", {
            "statement": h["statement"], "question": h["question"], "alternative": h["alternative"],
            "evidence_needed": h["evidence_needed"], "falsifier": h["falsifier"], "capacity": h["capacity"],
            "priority": h["priority"], "idea_origin": h["origin"], "status": "open", "alias": h["alias"], "links": links},
            actor=ACTOR, origin=_prov(h["source"]), material=False)
        ids[h["alias"]] = e["id"]
    # workplan questions W0–W9 (W0–W7 from finora-eda brain/business/case_questions.yaml, built from v0.3 §08–09)
    cq = ws.case_questions()
    hyp_by_w = {}
    for w in cq.get("preguntas", []):
        hyps = [ids[h["id"]] for h in w.get("hipotesis", []) if h["id"] in ids]
        if w["id"] == "W6":
            hyps = [ids[a] for a in ("HC1", "HC2a", "HC2b", "HC3ab", "HC3q", "HC3s", "HC3p") if a in ids]
        if w["id"] == "W7":
            hyps = [ids[a] for a in ("HF1a", "HF1b", "HF2a", "HF2b", "HF3a", "HF3b", "HF3c") if a in ids]
        hyp_by_w[w["id"]] = hyps
        e = store.create("question", {
            "text": w["pregunta"], "kind": "workplan", "status": "open", "alias": w["id"],
            "priority": w.get("prioridad_etiqueta"), "impact": w.get("impacto"), "capacity": w.get("capacidad"),
            "capacity_level": w.get("capacidad_nivel"), "why_it_matters": w.get("por_que_importa"),
            "method": w.get("metodo"), "deliverable": w.get("entregable"), "close_criteria": w.get("criterio_cierre"),
            "front": w.get("frente"), "do_not_conclude": w.get("no_concluir") or [], "links": hyps},
            actor=ACTOR, origin=_prov("finora-eda/brain/business/case_questions.yaml#" + w["id"],
                                      derived_from="brief v0.3 §08–09"), material=False)
        ids[w["id"]] = e["id"]
    for key, text, hyp, prio in (("W8", "¿Gasto y resultados pagados se mueven distinto de una forma relevante?", "HO5",
                                  "P3 · pendiente por defecto"),
                                 ("W9", "¿Qué cambió en la respuesta y qué sigue abierto? (volver a las hipótesis y escribir qué aprendimos)",
                                  None, "Al terminar el trabajo autorizado")):
        e = store.create("question", {"text": text, "kind": "workplan", "status": "open", "alias": key, "priority": prio,
                                      "links": [ids[hyp]] if hyp else []},
                         actor=ACTOR, origin=_prov(f"brief v0.3 §09 · {key}"), material=False)
        ids[key] = e["id"]
    # Hugo's points: dual representation (his point · what was added)
    for u in seed["hugo_points"]:
        common = {"hugo_wording": u["hugo"], "structured": u["added"], "verbatim": False, "alias": u["alias"],
                  "title": f"{u['alias']} · {u['title']}", "basis": "hugo"}
        if u["kind"] == "QUESTION":
            e = store.create("question", {**common, "text": u["title"], "kind": "framing", "status": "open"},
                             actor=ACTOR, origin=_prov(f"brief v0.3 §02 · {u['alias']}", note="paráfrasis del brief, no cita textual"),
                             material=False)
        else:
            e = store.create("note", {**common, "kind": u["kind"], "text": u["title"], "status": "active"},
                             actor=ACTOR, origin=_prov(f"brief v0.3 §02 · {u['alias']}", note="paráfrasis del brief, no cita textual"),
                             material=False)
        ids[u["alias"]] = e["id"]
    for i, text in enumerate(seed["unknowns"], 1):
        e = store.create("note", {"kind": "UNKNOWN", "text": text, "structured": text, "status": "active",
                                  "alias": f"A{i:02d}", "basis": "brief"},
                         actor=ACTOR, origin=_prov("brief v0.3 §03 · Cosas que todavía tenemos que aclarar"), material=False)
        ids[f"A{i:02d}"] = e["id"]
    # decisions (brief v0.3 §11) — active, imported with their origin
    for d in seed["decisions"]:
        dec = record_decision(store, title=d["title"], context=f"Origen: {d['origin']}", options={},
                              agent_recommendation="", user_choice=d["choice"], user_rationale="",
                              affected_items=[], downstream_impact="", kind=d["kind"], phase="framing", actor="hugo",
                              origin=_prov("brief v0.3 §11 · decisiones de estructura", idea_origin=d["origin"]))
        patch = {"review": {"state": "accepted", "by": "import", "at": now_iso(),
                            "note": "Decisión del brief v0.3 (fuente de verdad declarada por Hugo el 28-sep-2026)."},
                 "phase": "framing"}
        if d.get("superseded_note"):
            patch.update({"status": "superseded", "superseded_note": d["superseded_note"]})
        store.update(dec["id"], patch, actor=ACTOR, material=False, summary=f"{dec['id']} importada del brief v0.3")
    for d in seed["memory_decisions"]:
        dec = record_decision(store, title=d["title"], context=d["note"], options={}, agent_recommendation="",
                              user_choice="", user_rationale="", affected_items=[], downstream_impact="",
                              kind="scope", phase="framing", actor="import",
                              origin=_prov("notas del proyecto (memoria de sesión de Claude)", date=d["date"]))
        store.update(dec["id"], {"date": d["date"], "confirm_note": "Confirmar: viene de notas de sesión, no de un documento de Hugo."},
                     actor=ACTOR, material=False)
    # framing document
    should_not = []
    for w in cq.get("preguntas", []):
        for x in w.get("no_concluir") or []:
            if x not in should_not:
                should_not.append(x)
    fr = cases.empty_framing()
    fr.update({"executive_question": seed["executive_question"], "executive_question_note": seed["executive_question_note"],
               "candidate_frames": seed["candidate_frames"], "initial_storyline": seed["initial_storyline"],
               "decisions_needed": seed["decisions_needed"], "should_not_claim": should_not[:14],
               "stress_test": seed["stress_test"], "perspectives": seed["perspectives"], "parked": seed["parked"],
               "language_notes": ["Hugo usa «monto observado» y «primer pagador observado» en lugar de MRR y cliente nuevo mientras la semántica no esté confirmada.",
                                  "Términos en inglés que Hugo usa tal cual: leads, funnel, churn, self-serve, SQL, MRR."],
               "research_needed": [
                   {"id": "RN-W6", "question": "¿Qué información mínima falta para contestar al CRO (entradas únicas con fecha, señales iniciales, recorrido, atención, vínculo con pago)?",
                    "why": "HC1–HC3 tienen capacidad 0 con los datos actuales: sin esto la respuesta al CRO queda como propuesta.",
                    "links": [ids["W6"]] + hyp_by_w.get("W6", [])[:3], "status": "pending", "proposed_by": "import (brief v0.3 W6)"},
                   {"id": "RN-W7", "question": "¿Qué evidencia confirmaría vigencia, características contratadas, tarifa y descuento aplicado?",
                    "why": "HF1–HF3 tienen capacidad 0: sin componentes explícitos no se separa suscripción, tarifa y descuento.",
                    "links": [ids["W7"]] + hyp_by_w.get("W7", [])[:3], "status": "pending", "proposed_by": "import (brief v0.3 W7)"}],
               "source": "brief v0.3 (importado)", "mode": "organize"})
    framing_doc.save(store, fr, actor=ACTOR, summary="Framing v0.3 importado", material=False)
    return ids


# ------------------------------------------------------------------------------------------ research + findings
def _research(store: CaseStore, ws: FinoraWorkspace, ids: dict) -> None:
    canon = {h["id"]: h for h in ws.canonical()}
    fid_by_canon: dict[str, str] = {}
    related: dict[str, list[str]] = {}
    for w in ws.case_questions().get("preguntas", []):
        for cid in w.get("afirmaciones_relacionadas") or []:
            related.setdefault(cid, []).append(w["id"])
    for cid, h in canon.items():
        f = store.create("finding", {
            "headline": h["afirmacion"], "domain": h.get("dominio"), "epistemic_state": h.get("estado"),
            "confidence": CONF.get(h.get("estado"), "medium"), "evidence_values": h.get("evidencia") or {},
            "evidence_labels": h.get("etiquetas") or {}, "verified_in_code": bool(h.get("verificado_en_codigo")),
            "alias": cid, "kind": "analytics", "visual": h.get("grafica"),
            "source_ref": {"workspace": "finora-eda", "canonical_id": cid},
            "limitations": ["Monto pagado observado: no es MRR contractual validado."],
            "links": [ids[w] for w in related.get(cid, []) if w in ids]},
            actor=ACTOR, origin=_prov("finora-eda/brain/evidence/canonical_findings.yaml#" + cid,
                                      note="verificado en código por el pipeline; revisión humana pendiente en origen"),
            material=False)
        fid_by_canon[cid] = f["id"]

    def import_answer(wid: str, d: dict, q_id: str | None, hyps: list[str]):
        rc = d.get("respuesta_caso") or {}
        claims = d.get("claims") or {}
        evs = {e["id"]: e for e in d.get("evidencia", [])}
        finding_ids = []
        for cid in rc.get("hechos_observados") or []:
            c = claims.get(cid)
            if not c:
                continue
            canon_refs = [evs[e]["params"].get("claim_id") for e in c.get("apoyo", []) if e in evs and evs[e]["kind"] == "canonical"]
            only_canon = canon_refs and all(evs[e]["kind"] == "canonical" for e in c.get("apoyo", []) if e in evs)
            if only_canon and canon_refs[0] in fid_by_canon:
                finding_ids.append(fid_by_canon[canon_refs[0]])
                continue
            vis = next((v for v in (d.get("visuals") or {}).values() if v.get("claim_id") == cid), None)
            f = store.create("finding", {
                "headline": c["texto"], "epistemic_state": c.get("estado"), "confidence": CONF.get(c.get("estado"), "medium"),
                "kind": "analytics", "alias": f"{wid}·{cid}", "visual": (vis or {}).get("spec"),
                "visual_title": (vis or {}).get("titulo"),
                "source_ref": {"workspace": "finora-eda", "run": d["id"], "claim": cid, "answer": wid,
                               "evidence": c.get("apoyo", [])},
                "limitations": ["Monto pagado observado: no es MRR contractual validado."],
                "links": [fid_by_canon[x] for x in canon_refs if x in fid_by_canon]},
                actor=ACTOR, origin=_prov(f"finora-eda/investigations/caso/{wid}.json#{cid}"), material=False)
            finding_ids.append(f["id"])
        resp = rc.get("respuesta") or {}
        hyp_eff = []
        for h in rc.get("hipotesis") or []:
            alias = h.get("hipotesis_caso")
            hid = ids.get(alias) if alias else None
            hyp_eff.append({"id": hid, "alias": alias, "question": h.get("pregunta"), "state": h.get("estado"),
                            "effect": h.get("efecto"), "reading": h.get("lectura")})
            if hid:
                store.update(hid, {"assessed": {"by": f"finora-eda investigador ({wid})", "state": h.get("estado"),
                                                "effect": h.get("efecto"), "reading": h.get("lectura"),
                                                "note": "evaluación del agente del workspace; pendiente de revisión de Hugo"}},
                             actor=ACTOR, material=False, summary=f"{hid} con evaluación importada de {wid}")
        visuals = [{"id": k, "title": v.get("titulo"), "spec": v.get("spec"), "claim": v.get("claim_id")}
                   for k, v in list((d.get("visuals") or {}).items())[:10] if (v.get("spec") or {}).get("tipo") not in (None, "tarjeta")]
        links = [x for x in [q_id] + hyps if x] + finding_ids
        store.create("research", {
            "research_question": d.get("pregunta"), "case_question": d.get("pregunta"),
            "specialty": "analytics", "intensity": "analytics", "status": "completed", "alias": wid,
            "why_it_matters": next((w.get("por_que_importa") for w in ws.case_questions().get("preguntas", []) if w["id"] == wid), ""),
            "short_answer": (resp.get("titular") + ". " if resp.get("titular") else "") + (resp.get("texto") or ""),
            "headline": resp.get("titular"), "answer_states": rc.get("estados"),
            "findings": finding_ids,
            "what_is_established": [x.get("texto") for x in rc.get("interpretacion_permitida") or []],
            "what_is_contested": [],
            "what_remains_unknown": [x.get("texto") for x in rc.get("no_podemos_concluir") or []],
            "cannot_claim": rc.get("limites_del_brief") or [],
            "alternative_explanations": [],
            "case_implication": " ".join(x.get("texto", "") for x in (rc.get("interpretacion_permitida") or [])[:1]),
            "changes_current_story": "maybe",
            "affected_hypotheses": hyp_eff, "affected_claims": [],
            "suggested_action": ((rc.get("siguiente_pregunta") or {}).get("por_que") or ""),
            "next_question": (rc.get("siguiente_pregunta") or {}).get("id"),
            "new_questions": rc.get("preguntas_abiertas") or [],
            "handoff_to_cos": {"summary": resp.get("titular") or "", "recommended_next": (rc.get("siguiente_pregunta") or {}).get("pregunta", "")},
            "visuals": visuals, "purpose_ok": True,
            "workspace_run": {"workspace": "finora-eda", "run_id": d.get("id"), "path": f"investigations/caso/{wid}.json",
                              "modelo": d.get("modelo"), "finished_ms": d.get("finished_ms")},
            "sources": [{"id": "SRC-1", "title": f"Investigación del workspace {d.get('id')}", "type": "internal_analysis",
                         "quality": "A", "path": f"finora-eda/investigations/caso/{wid}.json",
                         "note": "Evidencia interna registrada por las tools del workspace (DuckDB, solo lectura)"}],
            "links": links},
            actor=ACTOR, origin=_prov(f"finora-eda/investigations/caso/{wid}.json", run_id=d.get("id")), material=False)

    cq = {w["id"]: w for w in ws.case_questions().get("preguntas", [])}
    for wid in ("W0", "W1", "W2", "W3", "W4", "W5"):
        d = ws.case_answer(wid)
        if d and d.get("status") == "publicada":
            qid = ids.get(wid)
            hyps = (store.get(qid) or {}).get("links", []) if qid else []
            import_answer(wid, d, qid, hyps)
    for wid in ("W6", "W7"):
        w = cq.get(wid)
        if not w:
            continue
        missing = [{"dato": m.get("dato"), "fuente": m.get("fuente"), "catalogo": m.get("catalogo")} for m in w.get("evidencia_faltante") or []]
        store.create("research", {
            "research_question": w["pregunta"], "specialty": "analytics", "intensity": "analytics", "status": "blocked",
            "alias": wid, "why_it_matters": w.get("por_que_importa"),
            "short_answer": "Bloqueada: no hay sustituto válido con los datos actuales. La respuesta es la lista de evidencia que falta.",
            "blocked_reason": w.get("capacidad_texto"), "missing_evidence": missing,
            "cannot_claim": w.get("no_concluir") or [], "purpose_ok": True,
            "links": [x for x in [ids.get(wid)] + ((store.get(ids.get(wid)) or {}).get("links") or [])[:4] if x]},
            actor=ACTOR, origin=_prov("finora-eda/brain/business/case_questions.yaml#" + wid), material=False)
    g = ws.golden("Q2")
    if g and g.get("status") == "publicada":
        n = g.get("narrativa") or {}
        claims = g.get("claims") or {}
        fids = []
        for h in n.get("hallazgos") or []:
            for cid in h.get("claim_ids", [])[:2]:
                c = claims.get(cid)
                if not c or any(store.get(x) and (store.get(x) or {}).get("alias") == f"Q2·{cid}" for x in fids):
                    continue
                vis = next((v for v in (g.get("visuals") or {}).values() if v.get("claim_id") == cid), None)
                f = store.create("finding", {
                    "headline": c["texto"], "epistemic_state": c.get("estado"), "confidence": CONF.get(c.get("estado"), "medium"),
                    "kind": "analytics", "alias": f"Q2·{cid}", "visual": (vis or {}).get("spec"),
                    "source_ref": {"workspace": "finora-eda", "run": g["id"], "claim": cid, "answer": "Q2", "evidence": c.get("apoyo", [])},
                    "limitations": ["Monto pagado observado: no es MRR contractual validado."]},
                    actor=ACTOR, origin=_prov(f"finora-eda/investigations/golden/Q2.json#{cid}"), material=False)
                fids.append(f["id"])
        re_ = n.get("respuesta_ejecutiva") or {}
        store.create("research", {
            "research_question": g["pregunta"], "specialty": "analytics", "intensity": "analytics", "status": "completed",
            "alias": "Q2", "short_answer": f"{re_.get('titular', '')}. {re_.get('texto', '')}".strip(". "),
            "headline": re_.get("titular"), "findings": fids,
            "what_is_established": [h.get("interpretacion") for h in n.get("hallazgos") or [] if h.get("interpretacion")],
            "what_remains_unknown": [x.get("texto") for x in n.get("limites") or []],
            "case_implication": " ".join(x.get("texto", "") for x in (n.get("implicaciones") or [])[:2]),
            "new_questions": n.get("proximas_preguntas") or [], "changes_current_story": "maybe", "purpose_ok": True,
            "visuals": [{"id": k, "title": v.get("titulo"), "spec": v.get("spec"), "claim": v.get("claim_id")}
                        for k, v in list((g.get("visuals") or {}).items())[:8] if (v.get("spec") or {}).get("tipo") not in (None, "tarjeta")],
            "workspace_run": {"workspace": "finora-eda", "run_id": g["id"], "path": "investigations/golden/Q2.json"},
            "sources": [{"id": "SRC-1", "title": f"Investigación dorada del workspace {g['id']}", "type": "internal_analysis",
                         "quality": "A", "path": "finora-eda/investigations/golden/Q2.json"}],
            "links": [ids["CFO"]] + fids},
            actor=ACTOR, origin=_prov("finora-eda/investigations/golden/Q2.json", run_id=g["id"]), material=False)


# ------------------------------------------------------------------------------------------ evidence tables
def _num(s):
    from ..evidence import numbers_in
    n = numbers_in(str(s))
    return n[0].value if n else None


def _tables(store: CaseStore, ws: FinoraWorkspace, ids: dict) -> None:
    by_alias = {e.get("alias"): e["id"] for e in store.list("finding")}
    metrics = ws.metrics
    rows = ws.csv_rows("finora_monthly_metrics.csv")
    specs = []
    growth = [[r["month"], int(float(r["active_customers"])), round(float(r["total_paid_mrr_cop"]), 2),
               round(float(r["mrr_per_active_customer_cop"]), 2)] for r in rows]
    specs.append(({"table_key": "FIN-GROWTH-01", "title": "Clientes activos y monto observado por cliente activo",
                   "question": "¿Cómo evolucionó la monetización frente a los clientes activos?",
                   "columns": ["period", "active_customers", "total_paid_amount_cop", "amount_per_active_cop"], "rows": growth,
                   "units": {"active_customers": "clientes", "total_paid_amount_cop": "COP", "amount_per_active_cop": "COP"},
                   "definitions": {"active_customers": metrics.get("active_customers", {}).get("definicion", ""),
                                   "total_paid_amount_cop": metrics.get("total_paid_mrr_cop", {}).get("definicion", ""),
                                   "amount_per_active_cop": metrics.get("mrr_per_active_customer_cop", {}).get("definicion", "")},
                   "message": "Los clientes activos crecieron de 377 a 1.678 mientras el monto observado por cliente activo bajó de COP 92,8 mil a COP 57,8 mil (ene-22 → oct-24).",
                   "source": {"system": "finora-eda (Business Exploration Workspace)", "dataset": "finora_monthly_metrics.csv",
                              "generated_by": "finora_eda.py · build_monthly()"},
                   "transformation": "Suma mensual de amount por cliente; activos = clientes con monto > 0; monto por activo = total / activos.",
                   "filters": ["ene-22 censurado a la izquierda (CV-VENTANA)"], "period": {"from": "2022-01", "to": "2024-10"},
                   "grain": "mes", "analysis_id": "Fase 1 · canonical C-RES-01 / C-RES-02",
                   "limitations": ["El monto observado no es MRR contractual validado (CV-AMOUNT-COBRO).",
                                   "Ene-22 está censurado a la izquierda y feb-22 tiene arrastre (CV-VENTANA)."],
                   "preferred_visual": "annotated_line"}, ["C-RES-01", "C-RES-02"]))
    ret = next((h for h in ws.canonical() if h["id"] == "C-RET-03"), None)
    if ret:
        ev = ret["evidencia"]
        churn = [[y, _num(ev[f"churn_obs_{y}"]), _num(ev[f"churn_dur3_{y}"])] for y in (2022, 2023, 2024)]
        specs.append(({"table_key": "CFO-03", "title": "Churn observado vs churn persistente",
                       "question": "¿El churn mejoró o solo bajaron las ausencias temporales de pago?",
                       "columns": ["year", "observed_churn", "persistent_churn"], "rows": churn,
                       "units": {"observed_churn": "percent", "persistent_churn": "percent"},
                       "definitions": {"observed_churn": "Clientes que pagaban el mes anterior y este mes pagan cero, sobre activos (churn observado, no cancelación confirmada).",
                                       "persistent_churn": "Churn observado que no vuelve a pagar en los tres meses siguientes."},
                       "message": "El churn observado bajó de 3,52% en 2022 a 2,04% en 2024 mientras el churn persistente se mantuvo casi plano (0,98% → 0,96%).",
                       "source": {"system": "finora-eda (Business Exploration Workspace)", "dataset": "brain/evidence/canonical_findings.yaml#C-RET-03",
                                  "generated_by": "finora_eda.py · verification_views"},
                       "transformation": "Tasas anuales promedio de churn observado y de churn sin retorno a 3 meses.",
                       "period": {"from": "2022-03", "to": "2024-10"}, "grain": "año", "analysis_id": "Verificación 28-sep · C-RET-03",
                       "limitations": ["El churn observado no representa cancelación confirmada (CV-CHURN-PAUSAS)."],
                       "preferred_visual": "slope"}, ["C-RET-03", "C-RET-02"]))
    bridge = ws.csv_rows("supporting/mrr_bridge_annual.csv")
    specs.append(({"table_key": "FIN-BRIDGE-01", "title": "Puente anual del monto observado",
                   "question": "¿Qué componentes explican el cambio del monto observado cada año?",
                   "columns": ["year", "opening_cop", "new_cop", "expansion_cop", "reactivation_cop", "contraction_cop", "churn_cop", "closing_cop"],
                   "rows": [[int(r["year"]), round(float(r["opening_mrr_cop"])), round(float(r["new_mrr_cop"])), round(float(r["expansion_mrr_cop"])),
                             round(float(r["reactivation_mrr_cop"])), round(float(r["contraction_mrr_cop"])), round(float(r["churned_mrr_cop"])),
                             round(float(r["closing_mrr_cop"]))] for r in bridge],
                   "units": "COP", "definitions": {"new_cop": metrics.get("new_mrr_cop", {}).get("definicion", ""),
                                                   "reactivation_cop": metrics.get("reactivation_mrr_cop", {}).get("definicion", "")},
                   "message": "Cada año los movimientos brutos de entrada y salida son varias veces mayores que el cambio neto del monto observado.",
                   "source": {"system": "finora-eda (Business Exploration Workspace)", "dataset": "supporting/mrr_bridge_annual.csv"},
                   "transformation": "Suma anual de los componentes mensuales del puente; check_diff = 0.",
                   "period": {"from": "2022-02", "to": "2024-10"}, "grain": "año", "analysis_id": "Fase 1 · mrr_bridge_annual",
                   "limitations": ["Los componentes mezclan cambios del cliente, decisiones comerciales y timing de cobro (CV-AMOUNT-COBRO)."],
                   "preferred_visual": "waterfall"}, ["C-RES-04"]))
    ticket = ws.csv_rows("supporting/new_customer_ticket_by_year.csv")
    specs.append(({"table_key": "CRO-TICKET-01", "title": "Ticket de entrada de los nuevos pagadores por año",
                   "question": "¿Cambió lo que pagan los nuevos pagadores al entrar?",
                   "columns": ["year", "new_customers", "m0_mean_cop", "m0_median_cop", "early_run_rate_median_cop"],
                   "rows": [[int(r["year"]), int(r["new_customers"]), round(float(r["m0_mean_cop"])), round(float(r["m0_median_cop"])),
                             round(float(r["early_run_rate_median_cop"]))] for r in ticket],
                   "units": {"new_customers": "clientes", "m0_mean_cop": "COP", "m0_median_cop": "COP", "early_run_rate_median_cop": "COP"},
                   "definitions": {"m0_median_cop": "Mediana del primer pago observado de las altas del año."},
                   "message": "La mediana del ticket de entrada bajó de COP 63,0 mil en 2022 a COP 36,8 mil en 2023 y COP 42,0 mil en 2024.",
                   "source": {"system": "finora-eda (Business Exploration Workspace)", "dataset": "supporting/new_customer_ticket_by_year.csv"},
                   "period": {"from": "2022-03", "to": "2024-10"}, "grain": "año de alta", "analysis_id": "Fase 1 · C-ADQ-01",
                   "limitations": ["2022 incluye pagos iniciales grandes (CV-M0-PICOS-2022); primer pago ≠ hito de adquisición del CRO."],
                   "preferred_visual": "bar"}, ["C-ADQ-01", "C-ADQ-02"]))
    for spec, canon_ids in specs:
        errs = validate_table(spec)
        fids = [by_alias[c] for c in canon_ids if c in by_alias]
        t = store.create("table", {**make_table(**{k: v for k, v in spec.items()}), "status": "valid" if not errs else "invalid",
                                   "validation_errors": errs, "title": spec["title"], "links": fids},
                         actor=ACTOR, origin=_prov(spec["source"].get("dataset", "")), material=False,
                         summary=f"Tabla {spec['table_key']} importada")
        for fid in fids:
            store.add_links(fid, [t["id"]], actor=ACTOR)


# ------------------------------------------------------------------------------------------ artifacts
def _artifacts(store: CaseStore, ws: FinoraWorkspace) -> None:
    store.create("artifact", {"title": "Brief de trabajo v0.3 (fuente de verdad)", "path": "brief/sources/alegra_brief_de_trabajo.html",
                              "kind": "source_document", "status": "approved"},
                 actor=ACTOR, origin=_prov("~/Documents/Codex/2026-09-28/new-chat/outputs/alegra_brief_de_trabajo.html"), material=False)
    store.create("artifact", {"title": "Business Exploration Workspace (Finora)", "path": "/ws/finora/",
                              "kind": "workspace", "status": "approved", "workspace_head": ws.info().get("git_head")},
                 actor=ACTOR, origin=_prov("finora-eda"), material=False)
    store.create("artifact", {"title": "Propuesta de arquitectura v1.2 del workspace agentic", "path": "finora-eda/docs/propuesta_arquitectura_v1.md",
                              "kind": "reference", "status": "approved"},
                 actor=ACTOR, origin=_prov("finora-eda/docs/propuesta_arquitectura_v1.md"), material=False)
    for n in ws.narratives():
        store.create("artifact", {"title": f"Narrativa en borrador: {n['titulo']}", "path": f"finora-eda/{n['path']}",
                                  "kind": "story_draft", "status": "draft", "audience": n.get("audiencia"),
                                  "note": "Borrador del estudio «Preparar narrativa» del workspace; no es el Story Package."},
                     actor=ACTOR, origin=_prov(f"finora-eda/{n['path']}"), material=False)


if __name__ == "__main__":  # pragma: no cover
    import sys
    s = run(force="--force" in sys.argv)
    print(json.dumps({"case": s.id, "entities": len(s.all())}, ensure_ascii=False))
