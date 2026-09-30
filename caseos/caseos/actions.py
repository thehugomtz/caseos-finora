"""User actions on any entity (CaseOS §69). Every action is Hugo's: agents never call these."""
from __future__ import annotations

from . import analytics, cos, decisions, research, story
from .agents import framer
from .model import title_of, type_of
from .store import CaseStore, StoreError
from .util import clip, now_iso

HUGO = "hugo"

ACTIONS = {
    "accept": "Accept", "reject": "Reject", "challenge": "Challenge", "research": "Research", "research_deeper": "Research deeper",
    "send_to_cos": "Send to COS", "promote_to_finding": "Promote to finding", "create_hypothesis": "Create hypothesis",
    "create_question": "Create question", "update_story": "Update story", "to_table": "Send as table",
    "confirm": "Confirm decision", "revert": "Revert decision", "resolve": "Resolve alert", "follow_up": "Create follow-up",
    "retry": "Retry", "clear_stale": "Mark reviewed", "choose_frame": "Choose frame",
    "accept_with_evidence": "Accept with its evidence",
}


def available(e: dict) -> list[str]:
    t = e.get("type")
    rv = (e.get("review") or {}).get("state", "proposed")
    base = []
    if t in ("finding", "hypothesis", "question", "note", "claim", "table"):
        base += ["accept"] if rv != "accepted" else []
        base += ["reject"] if rv != "rejected" else []
    if t == "research":
        if e.get("status") == "completed":
            base += (["accept"] if rv != "accepted" else []) + ["challenge", "research_deeper", "follow_up", "send_to_cos"] + (["reject"] if rv != "rejected" else [])
        if e.get("status") in ("failed", "draft"):
            base += ["retry"]
    if t == "finding":
        base += ["challenge", "send_to_cos", "create_hypothesis", "research"]
        if e.get("kind") == "analytics":
            base += ["to_table"]
    if t in ("hypothesis", "question"):
        base += ["research", "challenge"]
    if t == "note":
        base += ["create_hypothesis", "create_question", "research"]
    if t == "claim":
        base += ["update_story", "challenge"]
        if rv != "rejected":
            base += ["accept_with_evidence"]          # accepting the claim and the findings and tables it stands on, in one step
    if t == "decision":
        base += ["confirm"] if e.get("status") == "proposed" else (["revert"] if e.get("status") == "active" else [])
    if t == "alert" and e.get("status") == "open":
        base += ["resolve"]
    if e.get("stale"):
        base += ["clear_stale"]
    return list(dict.fromkeys(base))


def run(store: CaseStore, eid: str, action: str, payload: dict | None = None) -> dict:
    p = payload or {}
    e = store.require(eid)
    t = e.get("type")
    note = (p.get("note") or "").strip()
    if action == "accept":
        if t == "research":
            return {"entity": research.accept(store, eid, note=note)}
        out = store.set_review(eid, "accepted", actor=HUGO, note=note)
        if t == "claim" and store.read_data("story/package.yaml"):
            story.revalidate(store)
        return {"entity": out}
    if action == "reject":
        if not note:
            raise StoreError("Rechazar requiere una razón (queda en el historial).")
        if t == "research":
            return {"entity": research.reject(store, eid, note=note)}
        out = store.set_review(eid, "rejected", actor=HUGO, note=note)
        if t in ("claim", "finding", "table") and store.read_data("story/package.yaml"):
            return {"entity": out, "validation": story.revalidate(store)}   # a rejected claim leaves the story at once
        return {"entity": out}
    if action == "accept_with_evidence":
        return story.accept_with_evidence(store, [eid], note=note)
    if action == "challenge":
        objection = note or p.get("text") or "No estoy convencido; busca otra explicación."
        if t == "research":
            return research.challenge(store, eid, objection=objection)
        store.update(eid, {"challenges": (e.get("challenges") or []) + [{"by": HUGO, "at": now_iso(), "text": objection}]},
                     actor=HUGO, summary=f"Hugo cuestionó {eid}: {clip(objection, 90)}", verb="challenged")
        turn = framer.start_turn(store, f"{objection}\n\nSobre {eid}: {clip(title_of(e), 500)}", "challenge")
        return {"framer_turn": turn}
    if action == "research":
        q = p.get("question") or (f"{title_of(e)}" if t != "note" else f"¿Qué evidencia confirmaría o descartaría: {title_of(e)}?")
        links = [eid] if t in ("question", "hypothesis", "decision", "claim") else [i for i in e.get("links") or [] if type_of(i) in ("question", "hypothesis")][:3]
        return research.create_request(store, q, links=links, route=p.get("route"), actor=HUGO, force_purpose=bool(links))
    if action == "research_deeper":
        return research.deeper(store, eid, note=note)
    if action == "follow_up":
        if not p.get("question"):
            raise StoreError("Falta la pregunta de seguimiento.")
        return research.follow_up(store, eid, question=p["question"], launch=bool(p.get("launch")))
    if action == "retry":
        return research.retry(store, eid)
    if action == "reverify":
        return research.reverify_model_sources(store, eid)
    if action == "recover":
        return analytics.recover_research(store, eid)
    if action == "send_to_cos":
        if t == "finding":
            return analytics.send_to_cos(store, eid)
        flagged = cos.flag_impact(store, eid)
        return {"alerts": [x["id"] for x in flagged], **cos.submit_assessment(store, eid, reason=note or "Hugo lo envió al COS")}
    if action == "to_table":
        return {"table": analytics.to_table(store, eid)}
    if action == "promote_to_finding":
        return {"finding": analytics.promote_claim(store, p["run"], p["claim"])}
    if action == "create_hypothesis":
        h = store.create("hypothesis", {"statement": p.get("statement") or title_of(e), "falsifier": p.get("falsifier", ""),
                                        "status": "open", "links": [eid], "hugo_wording": e.get("hugo_wording", ""),
                                        "phase": "framing" if t == "note" else "synthesis"},
                         actor=HUGO, summary=f"Hugo creó una hipótesis desde {eid}")
        return {"entity": h}
    if action == "create_question":
        q = store.create("question", {"text": p.get("text") or title_of(e), "kind": "framing", "status": "open", "links": [eid]},
                         actor=HUGO, summary=f"Hugo creó una pregunta desde {eid}")
        return {"entity": q}
    if action == "update_story":
        patch = {k: v for k, v in p.items() if k in ("headline", "answer", "limitations", "visual_intent", "visual_finding", "confidence",
                                                      "evidence_ids", "table_ids") and v is not None}
        if not patch:
            raise StoreError("Nada que actualizar.")
        vf = patch.get("visual_finding")
        if vf and not ((store.get(vf) or {}).get("type") == "finding" and (store.get(vf) or {}).get("visual")):
            raise StoreError(f"{vf} no es un finding con gráfica.")
        if "evidence_ids" in patch or "table_ids" in patch:
            patch["links"] = list(dict.fromkeys((patch.get("evidence_ids") or e.get("evidence_ids") or []) + (patch.get("table_ids") or e.get("table_ids") or [])))
        via = (p.get("via") or "").strip()
        if via:
            # Hugo asked for the change; someone else made it: the claim keeps waiting for his review
            out = store.update(eid, patch, actor=HUGO, summary=f"Hugo pidió cambiar {eid} en la story · {via}", verb="edited")
        else:
            out = store.update(eid, {**patch, "review": {"state": "accepted", "by": HUGO, "at": now_iso(), "note": "editado por Hugo"}},
                               actor=HUGO, summary=f"Hugo actualizó {eid} en la story", verb="edited")
        return {"entity": out, "validation": story.revalidate(store)}
    if action == "confirm":
        return {"entity": decisions.confirm(store, eid, choice=p.get("choice") or e.get("title", ""), rationale=note)}
    if action == "revert":
        return {"entity": decisions.revert(store, eid, rationale=note or "revertida")}
    if action == "resolve":
        return cos.resolve_alert(store, eid, choice=p.get("choice", "ignore"), rationale=note)
    if action == "clear_stale":
        return {"entity": store.update(eid, {"stale": None, "review": {"state": "accepted", "by": HUGO, "at": now_iso(),
                                                                       "note": note or "revisado tras la reapertura"}},
                                       actor=HUGO, summary=f"Hugo revisó {eid} (needs_review resuelto)", verb="reviewed")}
    raise StoreError(f"Acción desconocida: {action}")
