"""Command layer: talk to CaseOS in natural language; it routes.

Deterministic patterns first (instant, free); a small model call classifies only what the patterns miss. Gated
actions (Mark Ready, Reopen, sending to the Visual Storyteller) never execute from text: they come back as a
confirmation the UI shows to Hugo with the impact radius.
"""
from __future__ import annotations

import re

from . import cos, decisions, phases, research
from .agents import framer
from .llm import RunSpec, get_llm
from .model import PHASE_LABELS, PHASES, title_of, type_of
from .store import CaseStore
from .util import clip, norm

AGENT_ALIASES = {"measurement": "measurement", "medicion": "measurement", "medición": "measurement", "metricas": "measurement",
                 "analytics": "analytics", "analitica": "analytics", "analítica": "analytics", "datos del caso": "analytics",
                 "framer": "framer", "cos": "cos", "chief of staff": "cos", "research": "business", "business": "business",
                 "negocio": "business", "investigacion": "business", "investigación": "business", "data engineering": "data_engineering",
                 "data": "data_engineering", "datos": "data_engineering", "modelado": "data_engineering", "data modeling": "data_engineering"}
PHASE_ALIASES = {"briefing": "briefing", "brief": "briefing", "framing": "framing", "encuadre": "framing", "research": "research",
                 "investigacion": "research", "investigación": "research", "synthesis": "synthesis", "sintesis": "synthesis",
                 "síntesis": "synthesis", "story": "story", "historia": "story", "slides": "slides", "deck": "slides", "growth": None}

COMMANDS = [
    {"id": "ask_framer", "label": "Ask Framer", "hint": "Organiza, aconseja o desafía una idea", "template": "Pregúntale al Framer: "},
    {"id": "ask_research", "label": "Ask Research", "hint": "Investigación de negocio con fuentes", "template": "Mándale esto a Research: "},
    {"id": "ask_analytics", "label": "Ask Analytics", "hint": "Pregunta cuantitativa al workspace", "template": "Pregúntale a Analytics: "},
    {"id": "ask_measurement", "label": "Ask Measurement", "hint": "Cómo medirlo", "template": "Pregúntale a Measurement: "},
    {"id": "ask_data", "label": "Ask Data Engineering", "hint": "Cómo modelar los datos", "template": "Pregúntale a Data Engineering: "},
    {"id": "send_cos", "label": "Send to COS", "hint": "Evalúa el impacto del elemento abierto", "template": "Pásale esto al COS"},
    {"id": "ask_cos", "label": "Ask COS", "hint": "Pregunta sobre el caso completo", "template": "¿Qué falta para cerrar "},
    {"id": "save_decision", "label": "Save decision", "hint": "Registra una decisión tuya", "template": "Guarda esto como decisión: "},
    {"id": "mark_ready", "label": "Mark ready", "hint": "Gate humano de una fase", "template": "Marca Framing ready"},
    {"id": "reopen", "label": "Reopen phase", "hint": "Calcula el radio de impacto primero", "template": "Reabre framing"},
    {"id": "story_package", "label": "Generate Story", "hint": "El COS prepara el Story Package", "template": "Prepara Story Package"},
    {"id": "slides", "label": "Generate slides", "hint": "Handoff al Visual Storyteller", "template": "Genera slides"},
]


def _phase_in(text: str) -> str | None:
    tn = norm(text)
    for k, v in PHASE_ALIASES.items():
        if re.search(rf"\b{re.escape(norm(k))}\b", tn) and v:
            return v
    return None


def route(store: CaseStore, text: str, *, context_id: str | None = None) -> dict:
    t = (text or "").strip()
    tn = norm(t)
    ctx = store.get(context_id) if context_id and type_of(context_id) else None

    m = re.match(r"^\s*(?:preg[uú]ntale|pregunta|dile|ask)\s+(?:a|al|a la)?\s*(measurement|medici[oó]n|analytics|anal[ií]tica|framer|cos|chief of staff|research|business|negocio|data engineering|data modeling|data|datos|modelado)\b[\s,:]*(.*)$", t, re.I)
    if m:
        agent = AGENT_ALIASES.get(norm(m.group(1)), "business")
        q = (m.group(2) or "").strip() or (title_of(ctx) if ctx else "")
        if not q:
            return _reply("ask", "¿Qué le pregunto?", {})
        if agent == "framer":
            turn = framer.start_turn(store, q, "advise" if re.search(r"\b(como lo|cómo lo|aborda|harías|harias)\b", tn) else "organize")
            return _reply("ask_framer", "Se lo pasé al Framer.", {"kind": "open", "route": "#/framing", "job_id": turn["job_id"]})
        if agent == "cos":
            out = cos.submit_ask(store, q, context_id=context_id)
            return _reply("ask_cos", "El COS está revisando el caso.", {"kind": "open", "route": "#/cos", **out})
        links = [context_id] if ctx and type_of(context_id) in ("question", "hypothesis", "decision", "claim") else []
        rt = {"specialty": agent, "intensity": "analytics" if agent == "analytics" else research.heuristic_route(store, q)["intensity"]}
        res = research.create_request(store, q, links=links, route=rt, actor="hugo", force_purpose=bool(ctx))
        r = res["research"]
        msg = (f"Lancé {r['id']} con {research.SPECIALTIES[agent]}." if res["launched"] else
               f"Creé {r['id']}, pero no está enlazada a ninguna Q/H/D/C: {res['purpose'].get('note', '')}")
        return _reply("ask_" + agent, msg, {"kind": "open", "id": r["id"], "job_id": res.get("job_id")})

    if re.search(r"\b(m[aá]ndale|manda|env[ií]a|p[aá]sale|pasa)\b.*\b(a|al)\s+research\b|\binvestiga\b", tn):
        q = re.sub(r"^.*?\b(research|investiga)\b[:,\s]*", "", t, flags=re.I).strip() or (title_of(ctx) if ctx else "")
        links = [context_id] if ctx and type_of(context_id) in ("question", "hypothesis", "decision", "claim") else []
        if not q:
            return _reply("ask_research", "¿Qué investigo?", {})
        res = research.create_request(store, q, links=links, actor="hugo", force_purpose=bool(ctx))
        r = res["research"]
        return _reply("ask_research", f"{r['id']} → {res['research'].get('intensity')} · {research.SPECIALTIES[r['specialty']]}"
                      + ("" if res["launched"] else " (espera tu decisión: sin propósito de caso)"), {"kind": "open", "id": r["id"]})

    if re.search(r"\b(p[aá]sale|pasa|manda|m[aá]ndale|env[ií]a)\b.*\bcos\b", tn) or re.search(r"cambia la historia", tn):
        if not ctx:
            return _reply("send_cos", "Abre primero el finding o la investigación que quieres pasarle al COS.", {})
        if ctx.get("type") == "finding":
            from . import analytics
            out = analytics.send_to_cos(store, ctx["id"])
        else:
            cos.flag_impact(store, ctx["id"])
            out = cos.submit_assessment(store, ctx["id"], reason=t)
        return _reply("send_cos", f"El COS está evaluando el impacto de {ctx['id']}.", {"kind": "open", "route": "#/cos", **out})

    m = re.search(r"guarda (?:esto )?como decisi[oó]n[:,\s]*(.*)$", t, re.I)
    if m:
        title = (m.group(1) or "").strip() or (f"Decisión sobre {ctx['id']}: {clip(title_of(ctx), 90)}" if ctx else "")
        if not title:
            return _reply("save_decision", "¿Cuál es la decisión?", {})
        d = decisions.record_decision(store, title=title, context=f"Registrada desde el command layer{' mirando ' + ctx['id'] if ctx else ''}.",
                                      options={}, agent_recommendation="", user_choice=title, user_rationale="",
                                      affected_items=[ctx["id"]] if ctx else [], downstream_impact="", kind="other", actor="hugo")
        return _reply("save_decision", f"Guardada como {d['id']}.", {"kind": "open", "id": d["id"]})

    if re.search(r"no estoy convencid|busca otra explicaci|challenge|rompe esto|intenta romper", tn):
        if ctx and ctx.get("type") == "research":
            out = research.challenge(store, ctx["id"], objection=t)
            return _reply("challenge", f"Abrí {out['research']['id']} para buscar la explicación alternativa.", {"kind": "open", "id": out["research"]["id"]})
        turn = framer.start_turn(store, t + (f" (sobre {ctx['id']}: {clip(title_of(ctx), 200)})" if ctx else ""), "challenge")
        return _reply("challenge", "El Framer va a intentar romperlo (modo Challenge).", {"kind": "open", "route": "#/framing", "job_id": turn["job_id"]})

    if re.search(r"qu[eé] claims?.*d[eé]bil|claims? m[aá]s d[eé]biles", tn):
        ents = store.all()
        rows = []
        for c in ents.values():
            if c.get("type") == "claim" and (c.get("review") or {}).get("state") != "rejected":
                s = cos.claim_strength(store, c, ents)
                rows.append((["unsupported", "weak", "proposal", "supported"].index(s["level"]), c["id"], title_of(c), s))
        rows.sort()
        if not rows:
            return _reply("weak_claims", "Todavía no hay claims en la story.", {"kind": "open", "route": "#/story"})
        lines = [f"{cid} · {s['level']}: {clip(tt, 90)}" for _, cid, tt, s in rows[:5]]
        return _reply("weak_claims", "Los más débiles:\n" + "\n".join(lines), {"kind": "open", "route": "#/story"})

    if re.search(r"^(reabre|reabrir|reopen)\b", tn):
        p = _phase_in(t)
        if not p:
            return _reply("reopen", "¿Qué fase reabro? (briefing, framing, research, synthesis, story, slides)", {})
        imp = phases.impact(store, p)
        return _reply("reopen", imp["headline"], {"kind": "confirm", "confirm": "reopen", "phase": p, "impact": imp})

    if re.search(r"\bmarca\b.*\bready\b|\bmark\b.*\bready\b", tn):
        p = _phase_in(t)
        if not p:
            return _reply("mark_ready", "¿Qué fase marco Ready?", {})
        rd = phases.readiness(store, p)
        return _reply("mark_ready", f"{PHASE_LABELS[p]}: " + ("lista para tu aprobación." if rd["ok"] else "tiene bloqueos."),
                      {"kind": "confirm", "confirm": "mark_ready", "phase": p, "readiness": rd})

    if re.search(r"prepara.*story package|genera.*story|story package", tn):
        from . import story
        out = story.submit_package(store)
        return _reply("story_package", "El COS está preparando el Story Package.", {"kind": "open", "route": "#/story", **out})

    if re.search(r"genera.*(slides|deck|presentaci)", tn):
        return _reply("slides", "Elige la dirección visual para el Visual Storyteller.", {"kind": "confirm", "confirm": "slides", "route": "#/slides"})

    m = re.search(r"qu[eé] falta para cerrar\b(.*)$", t, re.I)
    if m or t.endswith("?"):
        out = cos.submit_ask(store, t, context_id=context_id)
        return _reply("ask_cos", "El COS está revisando el caso completo.", {"kind": "open", "route": "#/cos", **out})

    return _reply("fallback", "", {"kind": "classify", "text": t})


def _reply(intent: str, message: str, action: dict) -> dict:
    return {"intent": intent, "message": message, "action": action}


_S = {"type": "string"}
CLASSIFY_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["intent", "text", "agent", "phase"],
                   "properties": {"intent": {"type": "string", "enum": ["ask_framer", "ask_agent", "ask_cos", "save_decision", "challenge",
                                                                         "reopen", "mark_ready", "story_package", "slides", "send_cos"]},
                                  "text": _S, "agent": {"type": "string", "enum": ["framer", "business", "analytics", "measurement", "data_engineering", "cos", ""]},
                                  "phase": {"type": "string", "enum": PHASES + [""]}}}


async def classify(store: CaseStore, text: str, *, context_id: str | None = None) -> dict:
    """Model fallback for free text the patterns did not catch. Rewrites to a canonical command and routes it."""
    system = ("Clasifica la instrucción de Hugo para CaseOS en una intención. Reescribe `text` como la pregunta o contenido "
              "que debe recibir el agente. No ejecutes nada.")
    spec = RunSpec(agent="command", role="command", system=system, prompt=f"Instrucción: {text}\nContexto abierto: {context_id or '—'}",
                   schema=CLASSIFY_SCHEMA, max_turns=2, purpose="Command layer", case_id=store.id, case_root=store.root)
    res = await get_llm().run(spec)
    o = res.output
    canon = {"ask_framer": f"Pregúntale al Framer: {o['text']}", "ask_agent": f"Pregúntale a {o['agent'] or 'research'}: {o['text']}",
             "ask_cos": o["text"] if o["text"].endswith("?") else o["text"] + "?", "save_decision": f"Guarda esto como decisión: {o['text']}",
             "challenge": f"No estoy convencido: {o['text']}", "reopen": f"Reabre {o['phase']}", "mark_ready": f"Marca {o['phase']} ready",
             "story_package": "Prepara Story Package", "slides": "Genera slides", "send_cos": "Pásale esto al COS"}[o["intent"]]
    out = route(store, canon, context_id=context_id)
    out["classified_as"] = o
    return out
