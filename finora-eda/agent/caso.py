"""Preguntas del caso: el workplan W0–W7 del brief de trabajo v0.3 como cola de investigación.

Una pregunta respondible o parcial se investiga con el mismo agente, las mismas tools y el mismo validador de
afirmaciones; al cerrar, el compositor del caso entrega siete partes obligatorias que este módulo valida en código.
Una pregunta bloqueada no se investiga: no hay sustituto válido. Su respuesta es determinista y explica qué evidencia
falta, qué la distinguiría y dónde podría estar.

Sin dependencias del SDK al importar: el pipeline de la Fase 1 lo usa para validar y embeber la cola.
"""
from __future__ import annotations

import json
import re
import shutil

import yaml

from .config import BRAIN, EFFORT, INVESTIGATIONS, PROMPTS, RUNS
from .lint import causal_hits, norm, number_words, numbers_in, qualifiers, stray_digits

CASE_DIR = INVESTIGATIONS / "caso"
DOC = yaml.safe_load((BRAIN / "business" / "case_questions.yaml").read_text(encoding="utf-8"))
QUESTIONS = {q["id"]: q for q in DOC["preguntas"]}
ORDER = [q["id"] for q in DOC["preguntas"]]
MISSING = {m["id"]: m for m in yaml.safe_load((BRAIN / "guardrails" / "missing_data.yaml").read_text(encoding="utf-8"))["faltantes"]}
LEVELS = {3: "respondible", 2: "parcial", 0: "bloqueada"}
STATUSES = ["pendiente", "investigando", "respondida", "bloqueada"]
STRONG = {"Hecho observado", "Evidencia fuerte"}
# efecto de la investigación sobre cada hipótesis: lo deriva el código del estado, no lo declara el modelo
EFFECT = {"Soportada": "fortalecida", "No soportada": "debilitada", "Direccional": "señal direccional",
          "No evaluable": "no evaluable", "No evaluada por presupuesto": "sin evaluar", "Pendiente": "sin evaluar"}
# IDs que sí pueden aparecer en los textos: preguntas del caso e hipótesis del caso o de la investigación
CASE_IDS = re.compile(r"\b(W\d|H[A-Z]{1,3}\d*[a-z]?(/[a-z])*|H\d+(\.\d+)*)\b")
FOREIGN_IDS = re.compile(r"\b(EC?-[A-Z0-9]+(-\d+)*|C-\d{3}|C-[A-Z]{3}-\d{2})\b")

_ITEM = {"type": "object", "additionalProperties": False, "required": ["texto", "claim_ids"],
         "properties": {"texto": {"type": "string"}, "claim_ids": {"type": "array", "items": {"type": "string"}}}}
CASE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "respuesta": {"type": "object", "additionalProperties": False, "required": ["titular", "texto", "claim_ids"],
                      "properties": {"titular": {"type": "string"}, "texto": {"type": "string"},
                                     "claim_ids": {"type": "array", "items": {"type": "string"}}}},
        "hechos_observados": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "interpretacion_permitida": {"type": "array", "items": _ITEM, "minItems": 1, "maxItems": 4},
        "no_podemos_concluir": {"type": "array", "items": _ITEM, "minItems": 1, "maxItems": 5},
        "hipotesis": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False, "required": ["hipotesis_id", "hipotesis_caso", "lectura", "claim_ids"],
            "properties": {"hipotesis_id": {"type": "string"}, "hipotesis_caso": {"type": "string"}, "lectura": {"type": "string"},
                           "claim_ids": {"type": "array", "items": {"type": "string"}}}}},
        "preguntas_abiertas": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
        "siguiente_pregunta": {"type": "object", "additionalProperties": False, "required": ["id", "pregunta", "por_que"],
                               "properties": {"id": {"type": "string"}, "pregunta": {"type": "string"}, "por_que": {"type": "string"}}}},
    "required": ["respuesta", "hechos_observados", "interpretacion_permitida", "no_podemos_concluir", "hipotesis",
                 "preguntas_abiertas", "siguiente_pregunta"],
}


class CaseError(ValueError):
    """Pregunta inexistente o bloqueada."""


def can_investigate(qid: str) -> bool:
    return qid in QUESTIONS and QUESTIONS[qid]["capacidad_nivel"] != "bloqueada"


def lens(q: dict) -> str:
    return {"CRO": "Comercial (CRO)", "CFO": "Finanzas (CFO)"}.get(q.get("frente", ""), "CEO · CRO · CFO")


def _strip_ids(text: str) -> str:
    return CASE_IDS.sub(" ", text or "")


def _vetoes(q: dict) -> list[tuple[re.Pattern, str]]:
    return [(re.compile(p["patron"]), p["por_que"]) for p in q.get("proxies_invalidos") or []]


def veto_hits(text: str, vetoes) -> list[str]:
    t = norm(text or "")
    return [why for rx, why in vetoes if rx.search(t)]


# ---------------------------------------------------------------------------- integridad del catálogo
def check_questions(canon_ids: set[str], missing_ids: set[str] | None = None) -> list[str]:
    """Integridad de brain/business/case_questions.yaml: la corre el pipeline y las evaluaciones."""
    missing_ids = missing_ids if missing_ids is not None else set(MISSING)
    errors = []
    if ORDER != [f"W{i}" for i in range(len(ORDER))]:
        errors.append(f"las preguntas deben ser W0…W{len(ORDER) - 1} en orden: {ORDER}")
    need = ["prioridad", "prioridad_etiqueta", "frente", "pregunta", "por_que_importa", "capacidad_texto", "metodo",
            "entregable", "criterio_cierre"]
    for q in DOC["preguntas"]:
        qid = q["id"]
        for k in need:
            if not isinstance(q.get(k), str) or not q[k].strip():
                errors.append(f"{qid}: falta '{k}' como texto")
        if LEVELS.get(q.get("capacidad")) != q.get("capacidad_nivel"):
            errors.append(f"{qid}: capacidad {q.get('capacidad')} no corresponde a '{q.get('capacidad_nivel')}'")
        if not q.get("hipotesis"):
            errors.append(f"{qid}: sin hipótesis asociada")
        if not q.get("no_concluir"):
            errors.append(f"{qid}: sin límites (no_concluir)")
        for t in q.get("no_concluir") or []:
            if stray_digits(_strip_ids(t)) or number_words(_strip_ids(t)):
                errors.append(f"{qid}: un límite lleva cifras: {t}")
        for d in q.get("depende_de") or []:
            if d not in QUESTIONS:
                errors.append(f"{qid}: depende de una pregunta inexistente {d}")
        nxt = q.get("siguiente")
        if nxt and (nxt not in QUESTIONS or nxt == qid):
            errors.append(f"{qid}: siguiente inválida {nxt}")
        if not nxt and not (q.get("siguiente_libre") or {}).get("pregunta"):
            errors.append(f"{qid}: sin siguiente pregunta")
        for c in q.get("afirmaciones_relacionadas") or []:
            if c not in canon_ids:
                errors.append(f"{qid}: afirmación relacionada desconocida {c}")
        for e in q.get("evidencia_faltante") or []:
            bad = [m for m in e.get("catalogo") or [] if m not in missing_ids]
            if bad or not e.get("dato") or not e.get("fuente"):
                errors.append(f"{qid}: evidencia faltante mal formada {e.get('dato')} {bad}")
        for p in q.get("proxies_invalidos") or []:
            try:
                re.compile(p["patron"])
            except (re.error, KeyError) as ex:
                errors.append(f"{qid}: patrón de sustituto inválido: {ex}")
            if not p.get("terminos") or not p.get("por_que"):
                errors.append(f"{qid}: sustituto inválido sin términos o sin motivo")
        blocked = q.get("capacidad_nivel") == "bloqueada"
        if blocked:
            b = q.get("bloqueo") or {}
            if q.get("afirmaciones_relacionadas"):
                errors.append(f"{qid}: una pregunta bloqueada no lista hechos de pagos: serían un sustituto")
            if not b.get("matriz"):
                errors.append(f"{qid}: bloqueada sin matriz de evidencia faltante")
            for r in b.get("matriz") or []:
                for k in ("hipotesis", "pregunta", "comparacion", "evidencia_minima", "fuente", "bloqueada"):
                    if not str(r.get(k, "")).strip():
                        errors.append(f"{qid}: fila {r.get('hipotesis')} sin '{k}'")
                bad = [m for m in r.get("catalogo") or [] if m not in missing_ids]
                if bad:
                    errors.append(f"{qid}: fila {r.get('hipotesis')} con datos faltantes desconocidos {bad}")
            texts = [b.get("respuesta_titular", ""), b.get("respuesta_texto", "")] + list(b.get("hechos_de_datos") or []) + \
                    list(b.get("interpretacion_permitida") or [])
            if not all(t.strip() for t in texts) or len(texts) < 4:
                errors.append(f"{qid}: la respuesta de bloqueo está incompleta")
            for t in texts:
                clean = _strip_ids(t)
                if stray_digits(clean) or number_words(clean) or causal_hits(clean, allow_explica=False) or qualifiers(clean):
                    errors.append(f"{qid}: texto de bloqueo con cifras, calificativos o lenguaje causal: {t[:80]}")
        elif q.get("bloqueo"):
            errors.append(f"{qid}: solo una pregunta bloqueada lleva 'bloqueo'")
    return errors


# ---------------------------------------------------------------------------- contexto para el investigador
def case_prompt(qid: str) -> str:
    """Bloque de contexto de la pregunta del caso para el investigador: es contexto, no evidencia."""
    q = QUESTIONS[qid]
    lines = [f"Pregunta del caso {q['id']} ({q['prioridad_etiqueta']}), del workplan del brief de trabajo v0.3. Es contexto "
             "del caso, no evidencia: toda cifra que afirmes debe venir de evidencia registrada en esta investigación.",
             "Hipótesis del caso que esta pregunta contrasta:"]
    for h in q["hipotesis"]:
        lines.append(f"- {h['id']}: {h['texto']}" + (f" Qué la distingue: {h['discrimina']}" if h.get("discrimina") else "")
                     + (f" Alcance permitido: {h['alcance']}" if h.get("alcance") else ""))
    lines += [f"Capacidad con los datos actuales: {q['capacidad_texto']}", f"Método que propone el brief: {q['metodo']}",
              f"Criterio de cierre: {q['criterio_cierre']}"]
    if q.get("escenarios_del_caso"):
        lines.append("Escenarios del caso: " + " ".join(q["escenarios_del_caso"]))
    lines.append("No se puede concluir: " + " ".join(q["no_concluir"]))
    if q.get("proxies_invalidos"):
        lines.append("Sustitutos inválidos en esta pregunta (no respondas con ellos): "
                     + " ".join(f"{p['terminos']}: {p['por_que']}" for p in q["proxies_invalidos"]))
    if q.get("afirmaciones_relacionadas"):
        lines.append("Hechos canónicos ya verificados que conviene reutilizar (regístralos con search_evidence ids=[...]): "
                     + ", ".join(q["afirmaciones_relacionadas"]))
    lines.append("Registra la hipótesis del caso y su explicación rival como hipótesis de primer nivel, con firmas que las "
                 "distingan. Lo que dependa de datos que no existen va al nodo datos_faltantes y se cierra como No evaluable.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------- validación de la respuesta de siete partes
def validate_case_answer(doc: dict, claims: dict[str, dict], hyps: list[dict], q: dict) -> list[str]:
    """Las siete partes, con las reglas del compositor más las de la pregunta del caso."""
    errors = []
    vet = _vetoes(q)
    acc = {k: v for k, v in claims.items() if v.get("aceptada")}

    def check(where: str, text: str, ids: list[str], vetoes=None, allow_causal=False):
        if not (text or "").strip():
            errors.append(f"{where}: está vacío.")
            return
        bad = [i for i in ids if i not in acc]
        if bad:
            errors.append(f"{where}: cita afirmaciones inexistentes o rechazadas {bad}.")
        cited = " ".join(acc[i]["texto"] for i in ids if i in acc and acc[i].get("texto"))
        clean = _strip_ids(text)
        allowed = set(numbers_in(cited))
        loose = [n for n in numbers_in(clean) if n not in allowed]
        loose += [w for w in number_words(clean) if w not in number_words(cited)]
        if loose:
            errors.append(f"{where}: cifras que no están en las afirmaciones citadas {loose}.")
        quals = [x for x in qualifiers(clean) if x not in qualifiers(cited)]
        if quals:
            errors.append(f"{where}: calificativos sin respaldo en las afirmaciones citadas {quals}.")
        if not allow_causal:
            hits = causal_hits(clean, allow_explica=any(acc[i].get("tipo") == "descomposicion" for i in ids if i in acc))
            if hits:
                errors.append(f"{where}: lenguaje causal no permitido {hits}.")
        if FOREIGN_IDS.search(text):
            errors.append(f"{where}: no escribas IDs de afirmaciones ni de evidencia en el texto.")
        hits = veto_hits(text, vetoes or [])
        if hits:
            errors.append(f"{where}: usa un sustituto inválido para esta pregunta ({'; '.join(hits)}). Si hace falta "
                          "decirlo, va en no_podemos_concluir.")

    r = doc.get("respuesta") or {}
    if not r.get("claim_ids"):
        errors.append("respuesta: debe citar al menos una afirmación.")
    check("respuesta.titular", r.get("titular", ""), r.get("claim_ids", []), vet)
    check("respuesta.texto", r.get("texto", ""), r.get("claim_ids", []), vet)

    hechos = doc.get("hechos_observados") or []
    if any(v.get("estado") in STRONG for v in acc.values()) and not hechos:
        errors.append("hechos_observados: hay afirmaciones con estado Hecho observado o Evidencia fuerte; cita al menos una.")
    if len(set(hechos)) != len(hechos):
        errors.append("hechos_observados: IDs repetidos.")
    for cid in hechos:
        c = acc.get(cid)
        if not c:
            errors.append(f"hechos_observados: {cid} no existe o fue rechazada.")
        elif c.get("estado") not in STRONG:
            errors.append(f"hechos_observados: {cid} tiene estado {c.get('estado')}; aquí solo van Hecho observado o Evidencia "
                          "fuerte (lo direccional va en la interpretación y lo no evaluable en lo que no podemos concluir).")
        elif veto_hits(c.get("texto", ""), vet):
            errors.append(f"hechos_observados: {cid} usa un sustituto inválido para esta pregunta ({'; '.join(veto_hits(c['texto'], vet))}).")

    interp = doc.get("interpretacion_permitida") or []
    if not interp:
        errors.append("interpretacion_permitida: escribe al menos una lectura.")
    for i, it in enumerate(interp, 1):
        if not it.get("claim_ids"):
            errors.append(f"interpretación {i}: cita al menos una afirmación.")
        check(f"interpretación {i}", it.get("texto", ""), it.get("claim_ids", []), vet)

    limits = doc.get("no_podemos_concluir") or []
    if not limits:
        errors.append("no_podemos_concluir: escribe al menos un límite de esta investigación.")
    for i, it in enumerate(limits, 1):
        check(f"límite {i}", it.get("texto", ""), it.get("claim_ids", []), allow_causal=True)

    hids = {h["id"] for h in hyps}
    case_ids = {h["id"] for h in q.get("hipotesis", [])} | {"rival", ""}
    hy = doc.get("hipotesis") or []
    if not hy:
        errors.append("hipotesis: incluye las hipótesis de la investigación.")
    seen = set()
    for i, h in enumerate(hy, 1):
        hid = h.get("hipotesis_id")
        if hid not in hids:
            errors.append(f"hipótesis {i}: {hid} no existe en el árbol registrado ({sorted(hids)}).")
            continue
        if hid in seen:
            errors.append(f"hipótesis {i}: {hid} está repetida.")
        seen.add(hid)
        if h.get("hipotesis_caso", "") not in case_ids:
            errors.append(f"hipótesis {i}: hipotesis_caso '{h.get('hipotesis_caso')}' no es de esta pregunta; usa "
                          f"{sorted(case_ids - {''})} o vacío.")
        unlinked = [c for c in h.get("claim_ids", []) if c not in acc or not any(l.get("id") == hid for l in acc[c].get("hipotesis") or [])]
        if unlinked:
            errors.append(f"hipótesis {i}: {unlinked} no son afirmaciones aceptadas ligadas a {hid}.")
        check(f"hipótesis {i}.lectura", h.get("lectura", ""), h.get("claim_ids", []), vet)

    opens = doc.get("preguntas_abiertas") or []
    if not opens:
        errors.append("preguntas_abiertas: escribe al menos una.")
    for i, t in enumerate(opens, 1):
        clean = _strip_ids(t)
        if not clean.strip() or stray_digits(clean) or number_words(clean):
            errors.append(f"pregunta abierta {i}: sin cifras y no vacía.")

    sp = doc.get("siguiente_pregunta") or {}
    sid = (sp.get("id") or "").strip()
    if sid and sid not in QUESTIONS:
        errors.append(f"siguiente_pregunta: {sid} no existe; usa uno de {ORDER} o deja el ID vacío y escribe la pregunta.")
    if sid == q["id"]:
        errors.append("siguiente_pregunta: no puede ser la misma pregunta.")
    if not sid and not (sp.get("pregunta") or "").strip():
        errors.append("siguiente_pregunta: elige un ID de la cola o escribe la pregunta.")
    if not (sp.get("por_que") or "").strip():
        errors.append("siguiente_pregunta.por_que: di por qué es la siguiente.")
    for k in ("pregunta", "por_que"):
        clean = _strip_ids(sp.get(k, ""))
        if stray_digits(clean) or number_words(clean):
            errors.append(f"siguiente_pregunta.{k}: sin cifras.")
        if causal_hits(clean, allow_explica=False):
            errors.append(f"siguiente_pregunta.{k}: lenguaje causal no permitido {causal_hits(clean, allow_explica=False)}.")
    return errors


# ---------------------------------------------------------------------------- respuesta final, respaldo y bloqueadas
def _next(q: dict, sp: dict | None = None) -> dict:
    sp = dict(sp or {})
    sid = (sp.get("id") or "").strip()
    if sid in QUESTIONS:
        return {"id": sid, "pregunta": QUESTIONS[sid]["pregunta"], "por_que": sp.get("por_que", "")}
    if sp.get("pregunta"):
        return {"id": "", "pregunta": sp["pregunta"], "por_que": sp.get("por_que", "")}
    if q.get("siguiente"):
        return {"id": q["siguiente"], "pregunta": QUESTIONS[q["siguiente"]]["pregunta"], "por_que": "Es la que sigue en el orden del brief de trabajo."}
    free = q.get("siguiente_libre") or {}
    return {"id": "", "pregunta": free.get("pregunta", ""), "por_que": free.get("por_que", "")}


def _hypotheses(inv, listed: dict) -> list[dict]:
    out = []
    for h in inv.hipotesis:
        x = listed.get(h["id"], {})
        out.append({"hipotesis_id": h["id"], "pregunta": h["pregunta"], "padre": h.get("padre"), "estado": h.get("estado"),
                    "efecto": EFFECT.get(h.get("estado"), "sin evaluar"), "motivo": h.get("estado_motivo", ""),
                    "hipotesis_caso": x.get("hipotesis_caso", ""), "lectura": x.get("lectura", ""),
                    "claim_ids": x.get("claim_ids", [])})
    return out


def _states(inv, ids: list[str]) -> list[str]:
    return list(dict.fromkeys(inv.claims[c]["estado"] for c in ids if c in inv.claims and inv.claims[c].get("estado")))


def finalize(doc: dict, inv, q: dict, intentos: list, degradada: bool) -> dict:
    listed = {h["hipotesis_id"]: h for h in doc.get("hipotesis") or []}
    return {"caso_id": q["id"], "respuesta": doc["respuesta"], "estados": _states(inv, doc["respuesta"].get("claim_ids", [])),
            "hechos_observados": list(doc.get("hechos_observados") or []),
            "interpretacion_permitida": doc.get("interpretacion_permitida") or [],
            "no_podemos_concluir": doc.get("no_podemos_concluir") or [], "limites_del_brief": list(q["no_concluir"]),
            "hipotesis": _hypotheses(inv, listed), "preguntas_abiertas": doc.get("preguntas_abiertas") or [],
            "siguiente_pregunta": _next(q, doc.get("siguiente_pregunta")), "degradada": degradada, "intentos": intentos}


def fallback(inv, q: dict, intentos: list) -> dict:
    """Respuesta sin texto libre si el compositor no pasa el validador: solo afirmaciones validadas y el brief."""
    vet = _vetoes(q)
    acc = {k: v for k, v in inv.claims.items() if v.get("aceptada")}
    ok = [k for k, v in acc.items() if not veto_hits(v.get("texto", ""), vet)]
    p = inv.paquete or {}
    main = [c for c in p.get("respuesta_ejecutiva_claim_ids", []) if c in ok] or \
           [c for c in p.get("respuesta_ejecutiva_claim_ids", []) if c in acc] or ok[:1]
    hechos = [k for k in ok if acc[k].get("estado") in STRONG][:8]
    interp = [{"texto": acc[k]["texto"], "claim_ids": [k]} for k in ok if acc[k].get("estado") == "Direccional"][:3]
    interp += [{"texto": h["alcance"], "claim_ids": []} for h in q["hipotesis"] if h.get("alcance") and not veto_hits(h["alcance"], vet)]
    interp = interp or [{"texto": "Sin lectura adicional: se muestran solo las afirmaciones validadas.", "claim_ids": []}]
    lim_ids = [k for k in p.get("limites_claim_ids", []) if k in acc]
    lim_ids += [k for k, v in acc.items() if v.get("estado") == "No evaluable" and k not in lim_ids]
    doc = {"respuesta": {"titular": "", "texto": " ".join(acc[c]["texto"] for c in main), "claim_ids": main},
           "hechos_observados": hechos, "interpretacion_permitida": interp,
           "no_podemos_concluir": [{"texto": acc[k]["texto"], "claim_ids": [k]} for k in lim_ids],
           "hipotesis": [], "preguntas_abiertas": list(p.get("proximas_preguntas") or []) or [h["texto"] for h in q["hipotesis"]],
           "siguiente_pregunta": {}}
    return finalize(doc, inv, q, intentos, True)


def blocked_answer(q: dict) -> dict:
    """Respuesta determinista de una pregunta bloqueada: qué falta, qué lo distinguiría y dónde podría estar."""
    b = q["bloqueo"]
    campos = lambda ids: [{"id": m, "nombre": MISSING[m]["nombre"], "campos": MISSING[m].get("campos_necesarios", [])}  # noqa: E731
                          for m in ids if m in MISSING]
    return {"caso_id": q["id"], "bloqueada": True,
            "respuesta": {"titular": b["respuesta_titular"], "texto": b["respuesta_texto"], "claim_ids": []},
            "estados": ["No evaluable"], "hechos_de_datos": list(b["hechos_de_datos"]),
            "interpretacion_permitida": [{"texto": t, "claim_ids": []} for t in b["interpretacion_permitida"]],
            "no_podemos_concluir": [], "limites_del_brief": list(q["no_concluir"]),
            "hipotesis": [{"hipotesis_id": h["id"], "pregunta": h["texto"], "estado": "No evaluable",
                           "efecto": "sigue abierta", "motivo": "capacidad 0 con los datos actuales: falta evidencia indispensable",
                           "hipotesis_caso": h["id"], "lectura": "", "claim_ids": []} for h in q["hipotesis"]],
            "preguntas_abiertas": [r["pregunta"] for r in b["matriz"]], "siguiente_pregunta": _next(q),
            "matriz": [{**r, "catalogo": campos(r.get("catalogo") or [])} for r in b["matriz"]],
            "evidencia_faltante": [{**e, "catalogo": campos(e.get("catalogo") or [])} for e in q.get("evidencia_faltante") or []],
            "degradada": False, "intentos": []}


# ---------------------------------------------------------------------------- compositor del caso (usa el modelo)
def _brief(inv, q: dict) -> dict:
    from .validator import ISSUES
    acc = {k: v for k, v in inv.claims.items() if v.get("aceptada")}
    return {
        "pregunta_caso": {"id": q["id"], "pregunta": q["pregunta"], "prioridad": q["prioridad_etiqueta"],
                          "capacidad": q["capacidad_texto"], "criterio_cierre": q["criterio_cierre"],
                          "hipotesis_caso": [{"id": h["id"], "texto": h["texto"], "alcance": h.get("alcance", "")} for h in q["hipotesis"]],
                          "limites_del_brief": q["no_concluir"],
                          "proxies_invalidos": [{"terminos": p["terminos"], "por_que": p["por_que"]} for p in q.get("proxies_invalidos") or []]},
        "investigacion": {"pregunta": inv.pregunta, "encuadre": inv.encuadre},
        "hipotesis": [{"id": h["id"], "padre": h.get("padre"), "pregunta": h["pregunta"], "estado": h.get("estado"),
                       "motivo": h.get("estado_motivo", "")} for h in inv.hipotesis],
        "afirmaciones": [{"id": k, "texto": v["texto"], "estado": v["estado"], "tipo": v["tipo"], "hipotesis": v["hipotesis"],
                          "datos_faltantes": v.get("datos_faltantes") or [],
                          "precauciones": [ISSUES[x]["titulo"] for x in v.get("caveats") or [] if x in ISSUES]} for k, v in acc.items()],
        "paquete": inv.paquete,
        "otras_preguntas": [{"id": x["id"], "pregunta": x["pregunta"], "prioridad": x["prioridad_etiqueta"],
                             "capacidad": x["capacidad_nivel"], "depende_de": x.get("depende_de") or []}
                            for x in DOC["preguntas"] if x["id"] != q["id"]],
        "siguiente_segun_brief": q.get("siguiente") or (q.get("siguiente_libre") or {}).get("pregunta", ""),
    }


async def compose_case(inv) -> dict:
    """Siete partes obligatorias; el reintento corrige la respuesta anterior; si no pasa, respuesta sin texto libre."""
    from claude_agent_sdk import ResultMessage, query

    from .orchestrator import _add_usage, _base_options
    q = QUESTIONS[inv.caso_id]
    system = (PROMPTS / "caso.md").read_text(encoding="utf-8")
    base = "Pregunta del caso e investigación (JSON):\n" + json.dumps(_brief(inv, q), ensure_ascii=False, indent=1)
    prompt, intentos = base, []
    for attempt in (1, 2, 3):
        out = None
        async for m in query(prompt=prompt, options=_base_options(system, EFFORT["compositor"], 4, CASE_SCHEMA)):
            if isinstance(m, ResultMessage):
                _add_usage(inv, f"compositor_caso_{attempt}", m)
                out = m.structured_output
        errors = validate_case_answer(out or {}, inv.claims, inv.hipotesis, q) if out else ["el compositor no entregó salida estructurada"]
        intentos.append({"intento": attempt, "errores": errors})
        inv.composicion_intentos.append({"intento": attempt, "errores": errors})
        inv.emit("composicion", {"intento": attempt, "errores": errors})
        if not errors:
            return finalize(out, inv, q, intentos, False)
        prompt = base
        if out:
            prompt += "\n\nTu respuesta anterior (JSON):\n" + json.dumps(out, ensure_ascii=False, indent=1)
        prompt += ("\n\nNo pasó el validador. Devuélvela completa cambiando solo lo necesario para corregir estos puntos "
                   "(no reescribas lo que ya estaba bien):\n- " + "\n- ".join(errors))
    return fallback(inv, q, intentos)


# ---------------------------------------------------------------------------- respuestas vigentes y estado de la cola
def save_answer(inv, path) -> None:
    """La última respuesta publicada de cada pregunta queda en investigations/caso/<W>.json (se embebe en el HTML)."""
    CASE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(path, CASE_DIR / f"{inv.caso_id}.json")


_CACHE: dict[str, tuple[float, dict]] = {}


def load_answer(qid: str) -> dict | None:
    p = CASE_DIR / f"{qid}.json"
    if qid not in QUESTIONS or not p.exists():
        return None
    mt = p.stat().st_mtime
    if qid not in _CACHE or _CACHE[qid][0] != mt:
        _CACHE[qid] = (mt, json.loads(p.read_text(encoding="utf-8")))
    return _CACHE[qid][1]


_RUNS_CACHE: dict[str, tuple[float, dict]] = {}


def last_attempts() -> dict[str, dict]:
    """El último intento guardado de cada pregunta del caso (lee investigations/runs con caché por fecha)."""
    out = {}
    for p in RUNS.glob("INV-*.json"):
        mt = p.stat().st_mtime
        if p.name not in _RUNS_CACHE or _RUNS_CACHE[p.name][0] != mt:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            _RUNS_CACHE[p.name] = (mt, {"id": d.get("id"), "caso_id": d.get("caso_id"), "status": d.get("status"),
                                        "error": d.get("error"), "started_ms": d.get("started_ms") or 0})
        r = _RUNS_CACHE[p.name][1]
        if r["caso_id"] and r["started_ms"] >= (out.get(r["caso_id"]) or {}).get("started_ms", -1):
            out[r["caso_id"]] = r
    return out


def statuses(live: dict) -> list[dict]:
    """Estado de cada pregunta: bloqueada por capacidad, investigando si hay una corrida en curso, respondida si hay
    respuesta publicada, pendiente si no."""
    from .orchestrator import friendly_error
    running = {i.caso_id: i.id for i in live.values() if getattr(i, "caso_id", None) and i.status not in ("publicada", "error")}
    failed = {q: friendly_error(r["error"] or "") for q, r in last_attempts().items() if r["status"] == "error"}
    failed.update({i.caso_id: friendly_error(i.error or "") for i in live.values() if getattr(i, "caso_id", None) and i.status == "error"})
    out = []
    for qid in ORDER:
        q, d = QUESTIONS[qid], load_answer(qid)
        if q["capacidad_nivel"] == "bloqueada":
            st = "bloqueada"
        elif qid in running:
            st = "investigando"
        elif d:
            st = "respondida"
        else:
            st = "pendiente"
        row = {"id": qid, "estado": st, "en_curso": running.get(qid)}
        if d:
            rc = d.get("respuesta_caso") or {}
            row["respuesta"] = {"run_id": d["id"], "finished_ms": d.get("finished_ms"), "degradada": rc.get("degradada", False),
                                "titular": (rc.get("respuesta") or {}).get("titular", "")}
        if qid in failed and qid not in running:
            row["ultimo_error"] = failed[qid]
        out.append(row)
    return out
