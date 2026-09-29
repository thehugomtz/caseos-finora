"""Analytics Agent integration (agents/analytics.md).

Two contracts:
- Analytics → Hugo: visual, interactive, narrative (the workspace's own investigations and charts, rendered in CaseOS
  with the chart kit ported from the workspace; the full workspace is mounted at /ws/finora/).
- Analytics → COS: structured, tabular, traceable (EvidenceTable built in code from the registered evidence).
"""
from __future__ import annotations

import asyncio

from . import cos, workspaces
from .evidence import validate_table
from .model import title_of
from .store import CaseStore, StoreError
from .util import clip, now_iso

CONF = {"Hecho observado": "high", "Evidencia fuerte": "high", "Direccional": "medium", "Exploratorio": "low"}


def adapter_or_fail(store: CaseStore):
    ws = workspaces.for_case(store)
    if not ws:
        raise StoreError("Este caso no tiene un workspace analítico enlazado (case.yaml › workspace).")
    return ws


def info(store: CaseStore) -> dict:
    ws = workspaces.for_case(store)
    if not ws:
        return {"available": False, "kind": "none",
                "note": "Sin workspace: enlaza uno en case.yaml › workspace para habilitar Analytics."}
    return ws.info()


def runs(store: CaseStore) -> list[dict]:
    ws = workspaces.for_case(store)
    if not ws or not ws.available:
        return []
    linked = {}
    for e in store.list():
        ref = e.get("source_ref") or {}
        run = ref.get("run") or (e.get("workspace_run") or {}).get("run_id")
        if run:
            linked.setdefault(run, []).append(e["id"])
    out = []
    for r in ws.runs():
        r["linked"] = sorted(set(linked.get(r["id"], [])))
        out.append(r)
    return out


def run_detail(store: CaseStore, inv_id: str) -> dict:
    ws = adapter_or_fail(store)
    d = ws.run(inv_id)
    if not d:
        raise StoreError(f"La investigación {inv_id} no existe en el workspace.")
    claims = d.get("claims") or {}
    promoted = {}
    for f in store.list("finding"):
        ref = f.get("source_ref") or {}
        if ref.get("run") == inv_id and ref.get("claim"):
            promoted[ref["claim"]] = f["id"]
    comp = d.get("narrativa") or {}
    rc = d.get("respuesta_caso") or {}
    head = (comp.get("respuesta_ejecutiva") or {}) or (rc.get("respuesta") or {})
    return {
        "id": d["id"], "pregunta": d.get("pregunta"), "status": d.get("status"), "caso_id": d.get("caso_id"),
        "headline": head.get("titular", ""), "answer": head.get("texto", ""),
        "hallazgos": comp.get("hallazgos") or [], "limites": comp.get("limites") or [], "implicaciones": comp.get("implicaciones") or [],
        "proximas_preguntas": comp.get("proximas_preguntas") or rc.get("preguntas_abiertas") or [],
        "respuesta_caso": rc or None,
        "claims": [{"id": k, "texto": v.get("texto"), "estado": v.get("estado"), "tipo": v.get("tipo"), "apoyo": v.get("apoyo"),
                    "promoted": promoted.get(k)} for k, v in claims.items() if v.get("aceptada")],
        "visuals": [{"id": k, "claim_id": v.get("claim_id"), "titulo": v.get("titulo"), "spec": v.get("spec"),
                     "intencion": v.get("intencion")} for k, v in (d.get("visuals") or {}).items()],
        "hipotesis": d.get("hipotesis") or [],
        "uso": d.get("uso") or {}, "modelo": d.get("modelo"), "started_ms": d.get("started_ms"), "finished_ms": d.get("finished_ms"),
        "error": d.get("error"), "data_version": d.get("data_version"), "brain_version": d.get("brain_version"),
    }


def promote_claim(store: CaseStore, inv_id: str, claim_id: str, *, actor: str = "hugo") -> dict:
    """Promote to finding: a validated claim of a workspace investigation becomes a case finding (proposed)."""
    ws = adapter_or_fail(store)
    d = ws.run(inv_id)
    c = (d or {}).get("claims", {}).get(claim_id)
    if not c or not c.get("aceptada"):
        raise StoreError(f"{claim_id} no es una afirmación validada de {inv_id}.")
    for f in store.list("finding"):
        ref = f.get("source_ref") or {}
        if ref.get("run") == inv_id and ref.get("claim") == claim_id:
            return f
    vis = next((v for v in (d.get("visuals") or {}).values() if v.get("claim_id") == claim_id), None)
    rid = next((r["id"] for r in store.list("research") if (r.get("workspace_run") or {}).get("run_id") == inv_id), None)
    return store.create("finding", {
        "headline": c["texto"], "epistemic_state": c.get("estado"), "confidence": CONF.get(c.get("estado"), "medium"),
        "kind": "analytics", "visual": (vis or {}).get("spec"), "visual_title": (vis or {}).get("titulo"),
        "source_ref": {"workspace": ws.kind, "run": inv_id, "claim": claim_id, "evidence": c.get("apoyo", [])},
        "limitations": ["Monto pagado observado: no es MRR contractual validado."], "links": [x for x in [rid] if x]},
        actor=actor, summary=f"Hugo promovió {claim_id} de {inv_id} a finding")


def to_table(store: CaseStore, fid: str, *, actor: str = "hugo") -> dict:
    """Analytics → COS handoff: the finding becomes a canonical EvidenceTable with full data lineage."""
    f = store.require(fid)
    existing = [l for l in f.get("links") or [] if l.startswith("T-") and store.get(l)]
    if existing:
        return store.get(existing[0])
    ref = f.get("source_ref") or {}
    ws = adapter_or_fail(store)
    key = f"{store.id.upper()[:3]}-{fid}"
    if ref.get("run") and ref.get("claim"):
        run = ws.run(ref["run"])
        if not run:
            raise StoreError(f"No encuentro la investigación {ref['run']} en el workspace.")
        table = ws.claim_table(run, ref["claim"], table_key=key)
    elif ref.get("canonical_id"):
        canon = next((h for h in ws.canonical() if h["id"] == ref["canonical_id"]), None)
        if not canon:
            raise StoreError(f"El hallazgo canónico {ref['canonical_id']} ya no existe en el workspace.")
        table = ws.canonical_table(canon, table_key=key)
    else:
        raise StoreError(f"{fid} no viene del workspace analítico; su evidencia es externa (ver sus fuentes).")
    errs = validate_table(table)
    t = store.create("table", {**table, "status": "valid" if not errs else "invalid", "validation_errors": errs,
                               "finding": fid, "links": [fid]},
                     actor=actor, summary=f"{fid} → tabla canónica {key} ({len(table['rows'])} filas)")
    store.add_links(fid, [t["id"]], actor=actor, summary=f"{fid} enlazado con su tabla {t['id']}")
    return t


def send_to_cos(store: CaseStore, fid: str, *, actor: str = "hugo") -> dict:
    f = store.require(fid)
    out = {"finding": fid}
    if f.get("kind") == "analytics":
        t = to_table(store, fid, actor=actor)
        out["table"] = t["id"]
    flagged = cos.flag_impact(store, fid)
    out["alerts"] = [x["id"] for x in flagged]
    out.update(cos.submit_assessment(store, fid, reason="Hugo envió el finding al COS"))
    store.log(actor, "sent", [fid] + ([out["table"]] if out.get("table") else []), f"Hugo envió {fid} al COS", material=True)
    return out


async def investigate_for_research(store: CaseStore, r: dict, job) -> dict:
    """Live analytics: the workspace's own investigator answers the research question; results map to the case."""
    ws = adapter_or_fail(store)
    if not ws.available:
        raise StoreError("El workspace analítico no está disponible en esta máquina.")
    from .research import task_lines
    ctx = {"titulo": f"CaseOS · {r['id']}", "texto": r["research_question"],
           "nota": "\n".join(["Pregunta enviada desde CaseOS; responde con evidencia del workspace.", *task_lines(r)]),
           "claim_ids": [], "narrativa_id": "", "pieza_id": ""}
    inv = ws.new_investigation(r["research_question"], ctx)
    task = asyncio.create_task(ws.run_investigation(inv))
    sent = 0
    await job.event("workspace", {"summary": f"Investigación en vivo {inv.id} en el Business Exploration Workspace"})
    while not task.done():
        await asyncio.sleep(1.0)
        while sent < len(inv.events):
            await job.event("workspace", {"summary": _event_text(inv.events[sent])})
            sent += 1
    task.result()
    d = inv.to_dict()
    if d.get("status") != "publicada":
        from .llm import AgentError
        raise AgentError("unknown", d.get("error") or "La investigación del workspace no se publicó.")
    comp = d.get("narrativa") or {}
    head = comp.get("respuesta_ejecutiva") or {}
    fids = []
    for h in comp.get("hallazgos") or []:
        for cid in (h.get("claim_ids") or [])[:3]:
            try:
                f = promote_claim(store, d["id"], cid, actor="analytics")
            except StoreError:
                continue
            if f["id"] not in fids:
                fids.append(f["id"])
    return {
        "research_question": r["research_question"], "case_question": r.get("case_question", ""),
        "why_it_matters": "", "short_answer": f"{head.get('titular', '')}. {head.get('texto', '')}".strip(". "),
        "headline": head.get("titular", ""),
        "what_is_established": [h.get("interpretacion") for h in comp.get("hallazgos") or [] if h.get("interpretacion")],
        "what_is_contested": [], "what_remains_unknown": [x.get("texto") for x in comp.get("limites") or []],
        "alternative_explanations": [], "case_implication": " ".join(x.get("texto", "") for x in (comp.get("implicaciones") or [])[:2]),
        "changes_current_story": {"value": "maybe", "why": "El COS evalúa el efecto sobre las hipótesis y claims enlazados."},
        "affected_hypotheses": [], "affected_claims": [], "suggested_action": "", "new_questions": comp.get("proximas_preguntas") or [],
        "handoff_to_cos": {"summary": head.get("titular", ""), "recommended_next": ""},
        "sources": [{"id": "SRC-1", "title": f"Investigación del workspace {d['id']}", "url": "", "publisher": "finora-eda",
                     "date": now_iso()[:10], "source_type": "internal", "quality": "A",
                     "note": "Evidencia interna registrada por las tools del workspace (solo lectura)"}],
        "visuals": [{"id": k, "title": v.get("titulo"), "spec": v.get("spec"), "claim": v.get("claim_id")}
                    for k, v in list((d.get("visuals") or {}).items())[:10] if (v.get("spec") or {}).get("tipo") not in (None, "tarjeta")],
        "workspace_run": {"workspace": ws.kind, "run_id": d["id"], "path": f"investigations/runs/{d['id']}.json", "modelo": d.get("modelo")},
        "_finding_ids": fids, "_run_ids": [d["id"]], "_usage": {d["id"]: {"cost_usd": sum((u or {}).get("costo_equivalente_usd") or 0 for u in (d.get("uso") or {}).values() if isinstance(u, dict))}},
        "_skills": [{"id": "finora-eda brain + playbooks", "mode": "core", "why": "agente del workspace existente"}],
    }


def _event_text(e: dict) -> str:
    t, d = e.get("tipo"), e.get("data") or {}
    if t == "estado":
        return f"Workspace · {d.get('estado')}"
    if t == "tool":
        return f"Workspace · {d.get('tool', '')} {clip(str(d.get('resumen') or d.get('params') or ''), 100)}"
    if t == "claim":
        return f"Workspace · afirmación {d.get('id', '')} {'validada' if d.get('aceptada') else 'rechazada'}"
    if t == "hipotesis":
        return "Workspace · hipótesis actualizadas"
    if t == "composicion":
        return f"Workspace · composición (intento {d.get('intento')})"
    return f"Workspace · {t}"


def finding_view(store: CaseStore, fid: str) -> dict:
    f = store.require(fid)
    tables = [store.get(l) for l in f.get("links") or [] if l.startswith("T-") and store.get(l)]
    return {"finding": f, "tables": tables, "headline": title_of(f)}
