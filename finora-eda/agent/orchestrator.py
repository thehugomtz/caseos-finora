"""Orquestador determinista de la slice (arquitectura v1.2 §3.4).

encuadre → hipótesis → evidencia → validación → composición → publicada

El agente corre con el Claude Agent SDK sobre la sesión local de Claude Code (tu suscripción si no hay
ANTHROPIC_API_KEY en el entorno). Aislamiento: sin tools integradas, sin MCP ni ajustes del usuario;
solo las tools de Finora y la salida estructurada.
"""
from __future__ import annotations

import json
import shutil

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage, TextBlock,
                              query)

from . import visuals
from .config import EFFORT, GOLDEN, MAX_TURNS, MODEL, PROMPTS, RUNS
from .state import Investigation, now_ms
from .tools import ALLOWED_TOOLS, CANON, METRICS, make_server
from .validator import ISSUES, MISSING, PLAYBOOKS, validate_composition
from .warehouse import connect_ro

PACKAGE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "respuesta_ejecutiva_claim_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
        "hallazgos": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
            "hipotesis_id": {"type": "string"}, "claim_ids": {"type": "array", "items": {"type": "string"}},
            "visual_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["hipotesis_id", "claim_ids", "visual_ids"]}},
        "limites_claim_ids": {"type": "array", "items": {"type": "string"}},
        "proximas_preguntas": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
        "nota_de_cierre": {"type": "string"}},
    "required": ["respuesta_ejecutiva_claim_ids", "hallazgos", "limites_claim_ids", "proximas_preguntas", "nota_de_cierre"],
}
_BLOCK = {"type": "object", "additionalProperties": False, "required": ["texto", "claim_ids"],
          "properties": {"texto": {"type": "string"}, "claim_ids": {"type": "array", "items": {"type": "string"}}}}
_ANSWER = {"type": "object", "additionalProperties": False, "required": ["titular", "texto", "claim_ids"],
           "properties": {"titular": {"type": "string"}, "texto": {"type": "string"},
                          "claim_ids": {"type": "array", "items": {"type": "string"}}}}
COMPOSITION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "respuesta_ejecutiva": _ANSWER,
        "hallazgos": {"type": "array", "items": {"type": "object", "additionalProperties": False, "properties": {
            "hipotesis_id": {"type": "string"}, "titular": {"type": "string"}, "pregunta": {"type": "string"},
            "claim_ids": {"type": "array", "items": {"type": "string"}}, "visual_ids": {"type": "array", "items": {"type": "string"}},
            "interpretacion": {"type": "string"}, "implicacion": {"type": "string"}, "por_que": {"type": "string"}},
            "required": ["hipotesis_id", "titular", "pregunta", "claim_ids", "visual_ids", "interpretacion", "implicacion", "por_que"]}},
        "limites": {"type": "array", "items": _BLOCK},
        "implicaciones": {"type": "array", "items": _BLOCK},
        "proximas_preguntas": {"type": "array", "items": {"type": "string"}}},
    "required": ["respuesta_ejecutiva", "hallazgos", "limites", "implicaciones", "proximas_preguntas"],
}


def brain_core(playbook_id: str | None = None) -> str:
    """Núcleo estable del cerebro para el prefijo del prompt (ordenado, sin fechas). Incluye todos los playbooks."""
    out = ["## Catálogo de métricas (id · nombre · ventana)"]
    out += [f"- {m['id']} · {m['nombre']} · {m['ventana']}" for m in METRICS.values()]
    out += ["", "## Problemas de datos conocidos (id · título · estado)"]
    out += [f"- {i['id']} · {i['titulo']} · {i['estado']}" for i in ISSUES.values()]
    for pid, pb in PLAYBOOKS.items():
        req = "requeridos" if any(n.get("requerido") for n in pb["nodos"]) else f"sugeridos (mínimo {pb.get('minimo_hipotesis', 1)} hipótesis)"
        out += ["", f"## Playbook {pid} · aplica a: {'; '.join(pb.get('aplica_a', []))}", pb["identidad"].strip(), f"Nodos {req}:"]
        for n in pb["nodos"]:
            out.append(f"- {n['id']}: {n['pregunta']}" + (f" Nota: {n['nota']}" if n.get("nota") else "")
                       + f" Evidencia sugerida: {'; '.join(n.get('evidencia_sugerida', [])) or '—'}")
            for c in n.get("hijos", []):
                out.append(f"  - {c['id']}: {c['pregunta']}" + (f" Nota: {c['nota']}" if c.get("nota") else "")
                           + (f" Evidencia sugerida: {'; '.join(c['evidencia_sugerida'])}" if c.get("evidencia_sugerida") else ""))
    out += ["", "## Hallazgos canónicos de la Fase 1 (id · estado · afirmación)"]
    out += [f"- {cid} · {h['estado']} · {h['afirmacion']}" for cid, h in CANON.items()]
    out += ["", "## Datos faltantes (IDs para No evaluable)"]
    out += [f"- {k}: {v['nombre']}" for k, v in MISSING.items()]
    return "\n".join(out)


def _base_options(system: str, effort: str, max_turns: int, schema: dict, **kw) -> ClaudeAgentOptions:
    RUNS.mkdir(parents=True, exist_ok=True)
    return ClaudeAgentOptions(
        tools=[], setting_sources=[], strict_mcp_config=True, system_prompt=system, model=MODEL, effort=effort,
        max_turns=max_turns, output_format={"type": "json_schema", "schema": schema}, cwd=str(RUNS), **kw)


def _add_usage(inv: Investigation, role: str, m: ResultMessage):
    u = m.usage or {}
    inv.uso[role] = {"turnos": m.num_turns, "ms": m.duration_ms, "costo_equivalente_usd": m.total_cost_usd,
                     "tokens_entrada": u.get("input_tokens"), "tokens_salida": u.get("output_tokens"),
                     "cache_lectura": u.get("cache_read_input_tokens"), "cache_escritura": u.get("cache_creation_input_tokens")}


async def investigate(inv: Investigation):
    con = connect_ro()
    server, _ = make_server(inv, con)
    system = (PROMPTS / "investigador.md").read_text(encoding="utf-8").replace("{{BRAIN_CORE}}", brain_core(inv.playbook_id))
    opts = _base_options(system, EFFORT["investigador"], MAX_TURNS, PACKAGE_SCHEMA,
                         mcp_servers={"finora": server}, allowed_tools=ALLOWED_TOOLS)
    prompt = (f"Pregunta: {inv.pregunta}\nLente: {inv.lente}\nContexto del hilo: ninguno (investigación nueva).\n"
              "Investiga y entrega el paquete.")
    inv.emit("inicio", {"pregunta": inv.pregunta, "modelo": MODEL})
    async for m in query(prompt=prompt, options=opts):
        if isinstance(m, SystemMessage) and m.subtype == "init":
            src = m.data.get("apiKeySource")
            inv.uso["autenticacion"] = "suscripción de Claude (sesión de Claude Code)" if src == "none" else f"API key ({src})"
            inv.emit("sesion", {"autenticacion": inv.uso["autenticacion"], "tools": m.data.get("tools")})
        elif isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, TextBlock) and b.text.strip():
                    inv.notas_agente.append({"t": now_ms() - inv.started_ms, "texto": b.text.strip()})
                    inv.emit("nota", {"texto": b.text.strip()[:600]})
        elif isinstance(m, ResultMessage):
            _add_usage(inv, "investigador", m)
            if m.is_error or not m.structured_output:
                raise RuntimeError(f"El investigador terminó sin paquete ({m.subtype}; {m.errors or m.result})")
            inv.paquete = m.structured_output


def _check_package(inv: Investigation) -> list[str]:
    """Deja en el paquete solo referencias válidas y anota lo que se descartó."""
    notes, p = [], inv.paquete or {}
    ok = lambda cid: cid in inv.claims and inv.claims[cid].get("aceptada")  # noqa: E731
    for k in ("respuesta_ejecutiva_claim_ids", "limites_claim_ids"):
        bad = [c for c in p.get(k, []) if not ok(c)]
        if bad:
            notes.append(f"{k}: se descartaron referencias inválidas {bad}")
        p[k] = [c for c in p.get(k, []) if ok(c)]
    hyp = {h["id"] for h in inv.hipotesis}
    for h in p.get("hallazgos", []):
        if h["hipotesis_id"] not in hyp:
            notes.append(f"hallazgo con hipótesis inexistente {h['hipotesis_id']}")
        h["claim_ids"] = [c for c in h["claim_ids"] if ok(c)]
        h["visual_ids"] = [v for v in h["visual_ids"] if v in inv.visuals]
    p["hallazgos"] = [h for h in p.get("hallazgos", []) if h["hipotesis_id"] in hyp and h["claim_ids"]]
    inv.paquete = p
    return notes


def _auto_visuals(inv: Investigation) -> int:
    """Toda conclusión con su visual: la gramática visual asigna una gráfica a cada hallazgo que no la tenga.

    Determinista: toma la primera afirmación del hallazgo que admite una forma y que no tiene ya gráfica en otro
    hallazgo (sin duplicar). La evidencia del agente usa su intención por defecto; la canónica de la Fase 1 reutiliza
    la gráfica de su tarjeta del workspace; lo No evaluable se muestra como la tabla de datos disponibles contra
    faltantes. Si todas sus afirmaciones ya tienen gráfica, el hallazgo remite a la existente. El título es el texto
    validado de la afirmación.
    """
    def pick_for(c):
        if c.get("estado") == "No evaluable":
            return None, "datos_faltantes", visuals.data_gap(c.get("datos_faltantes") or [])
        evs = [inv.registry.get(eid) for eid in c.get("apoyo", [])]
        for ev in evs:
            intent = visuals.default_intent(ev) if ev else None
            if intent:
                try:
                    return ev.id, intent, visuals.build(ev, intent)
                except visuals.VisualError:
                    continue
        canon = [ev for ev in evs if ev and ev.kind == "canonical"]
        if canon:
            try:
                return canon[0].id, "tarjeta", visuals.workspace_card(canon)
            except visuals.VisualError:
                pass
        return None

    added = 0
    for hz in (inv.paquete or {}).get("hallazgos", []):
        if hz.get("visual_ids"):
            continue
        by_claim = {v["claim_id"]: k for k, v in inv.visuals.items()}
        pick = None
        for cid in hz["claim_ids"]:
            c = inv.claims[cid]
            if cid in by_claim:
                continue
            got = pick_for(c)
            if got:
                pick = (c,) + got
                break
        if pick:
            c, eid, intent, spec = pick
            vid = f"V-{len(inv.visuals) + 1:02d}"
            inv.visuals[vid] = {"id": vid, "claim_id": c["id"], "evidence_id": eid, "intencion": intent,
                                "titulo": c["texto"], "spec": spec, "auto": True}
            hz["visual_ids"] = [vid]
            added += 1
        else:
            reuse = next((by_claim[cid] for cid in hz["claim_ids"] if cid in by_claim), None)
            if reuse:
                hz["visual_ids"] = [reuse]
    return added


def _deterministic_composition(inv: Investigation) -> dict:
    """Composición sin texto libre: solo afirmaciones validadas (respaldo si el compositor falla dos veces)."""
    c = inv.claims
    hyp = {h["id"]: h for h in inv.hipotesis}
    return {"respuesta_ejecutiva": {"titular": "", "texto": " ".join(c[i]["texto"] for i in inv.paquete["respuesta_ejecutiva_claim_ids"]),
                                    "claim_ids": inv.paquete["respuesta_ejecutiva_claim_ids"]},
            "hallazgos": [{"hipotesis_id": h["hipotesis_id"], "titular": "", "pregunta": hyp[h["hipotesis_id"]]["pregunta"],
                           "claim_ids": h["claim_ids"], "visual_ids": h["visual_ids"], "interpretacion": "",
                           "implicacion": "", "por_que": ""} for h in inv.paquete["hallazgos"]],
            "limites": [{"texto": c[i]["texto"], "claim_ids": [i]} for i in inv.paquete["limites_claim_ids"]],
            "implicaciones": [], "proximas_preguntas": inv.paquete["proximas_preguntas"], "degradada": True}


async def compose(inv: Investigation):
    accepted = {k: v for k, v in inv.claims.items() if v.get("aceptada")}
    brief = {"pregunta": inv.pregunta, "lente": inv.lente, "encuadre": inv.encuadre,
             "hipotesis": [{"id": h["id"], "pregunta": h["pregunta"], "estado": h["estado"], "motivo": h["estado_motivo"]}
                           for h in inv.hipotesis],
             "afirmaciones": [{"id": k, "texto": v["texto"], "estado": v["estado"], "tipo": v["tipo"],
                               "hipotesis": v["hipotesis"], "precauciones": [ISSUES[x]["titulo"] for x in v["caveats"] if x in ISSUES]}
                              for k, v in accepted.items()],
             "visuales": [{"id": k, "claim_id": v["claim_id"]} for k, v in inv.visuals.items()],
             "paquete": inv.paquete}
    system = (PROMPTS / "compositor.md").read_text(encoding="utf-8")
    base_prompt = "Brief de la investigación (JSON):\n" + json.dumps(brief, ensure_ascii=False, indent=1)
    prompt = base_prompt
    for attempt in (1, 2):
        doc = None
        async for m in query(prompt=prompt, options=_base_options(system, EFFORT["compositor"], 4, COMPOSITION_SCHEMA)):
            if isinstance(m, ResultMessage):
                _add_usage(inv, f"compositor_{attempt}", m)
                doc = m.structured_output
        errors = validate_composition(doc or {}, inv.claims) if doc else ["el compositor no entregó salida estructurada"]
        inv.composicion_intentos.append({"intento": attempt, "errores": errors})
        inv.emit("composicion", {"intento": attempt, "errores": errors})
        if not errors:
            doc["degradada"] = False
            return doc
        prompt = (base_prompt + "\n\nTu composición anterior no pasó el validador. Corrige estos puntos y vuelve a "
                  "entregarla completa:\n- " + "\n- ".join(errors))
    return _deterministic_composition(inv)


async def run(inv: Investigation, save_golden: bool = False) -> Investigation:
    try:
        await investigate(inv)
        notes = _check_package(inv)
        if notes:
            inv.emit("aviso", {"paquete": notes})
        _auto_visuals(inv)
        inv.close_hypotheses()
        used = {e for c in inv.claims.values() if c.get("aceptada") for e in c["apoyo"] + c["en_contra"]}
        for entry in inv.log:
            entry["usada"] = any(e in used for e in entry["evidencias"])
        inv.emit("hipotesis", {"hipotesis": inv.hipotesis})
        inv.set_status("composicion")
        inv.narrativa = await compose(inv)
        inv.finished_ms = now_ms()
        inv.set_status("publicada")
        inv.emit("final", {"id": inv.id})
    except Exception as e:  # noqa: BLE001 - se publica el error con el estado parcial
        inv.error = f"{type(e).__name__}: {e}"
        inv.finished_ms = now_ms()
        inv.set_status("error")
        inv.emit("final", {"id": inv.id, "error": inv.error})
    path = inv.save()
    if save_golden and inv.status == "publicada" and inv.pregunta_id:
        GOLDEN.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, GOLDEN / f"{inv.pregunta_id}.json")
    return inv


def revisual(path) -> Investigation:
    """Reasigna las gráficas automáticas de una investigación guardada con la gramática visual vigente.

    Determinista y sin modelo: no toca hipótesis, evidencia, afirmaciones ni el texto de la narrativa; solo las
    gráficas que asignó `_auto_visuals` y los visual_ids de los hallazgos que las usan.
    """
    from pathlib import Path
    path = Path(path)
    inv = Investigation.from_dict(json.loads(path.read_text(encoding="utf-8")))
    auto = {k for k, v in inv.visuals.items() if v.get("auto")}
    for k in auto:
        inv.visuals.pop(k)
    for hz in (inv.paquete or {}).get("hallazgos", []):
        hz["visual_ids"] = [v for v in hz.get("visual_ids") or [] if v not in auto]
    added = _auto_visuals(inv)
    by_h = {h["hipotesis_id"]: h["visual_ids"] for h in inv.paquete["hallazgos"]}
    for h in (inv.narrativa or {}).get("hallazgos", []):
        h["visual_ids"] = list(by_h.get(h["hipotesis_id"]) or [])
    inv.emit("recomposicion", {"visuales_reasignados": added, "narrativa": "sin cambios"})
    inv.save(path)
    return inv


async def recompose(path) -> Investigation:
    """Vuelve a componer una investigación guardada con los mismos datos: gráficas automáticas y narrativa nueva.

    No vuelve a investigar: hipótesis, evidencia y afirmaciones quedan intactas.
    """
    from pathlib import Path
    path = Path(path)
    inv = Investigation.from_dict(json.loads(path.read_text(encoding="utf-8")))
    added = _auto_visuals(inv)
    inv.emit("recomposicion", {"visuales_agregados": added})
    inv.composicion_intentos = []
    for k in [k for k in inv.uso if k.startswith("compositor_")]:
        inv.uso.pop(k)  # el uso reportado corresponde a la narrativa vigente
    inv.narrativa = await compose(inv)
    inv.save(path)
    return inv
