"""Narrativas: piezas guardadas, esqueleto desde un contexto y presentación consolidada en láminas web.

Una pieza es un fragmento validado del workspace o de una investigación (texto, afirmaciones con su estado, cifras,
gráfica e IDs) más el papel que cumple en la historia y una nota del usuario. El agente solo arma la historia con
piezas guardadas: toda cifra de una lámina tiene que estar en las piezas que esa lámina cita, y lo que falta aparece
como pendiente; nunca se rellena. Las notas del usuario orientan la historia, pero no cuentan como evidencia.
"""
from __future__ import annotations

import json
import re
import time
import uuid

from claude_agent_sdk import ResultMessage, query

from .config import EFFORT, PROMPTS, ROOT
from .lint import causal_hits, norm, number_words, numbers_in, qualifiers, stray_digits
from .tools import CANON

NARRATIVES = ROOT / "narratives"
ROLES = ["Situación", "Hallazgo", "Implicación", "Decisión", "Acción"]
AUDIENCES = ["CEO", "CRO", "CFO", "Mixta"]
PIECE_TYPES = ["respuesta", "seccion", "tarjeta", "hallazgo", "respuesta_inv", "afirmacion", "nota"]
ID_RE = re.compile(r"^NAR-\d{8}-\d{6}-[0-9a-f]{4}$")
MAX_TEXT = 4000

PLAN_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["resumen", "secciones"],
    "properties": {
        "resumen": {"type": "string"},
        "secciones": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["rol", "mensaje", "preguntas", "piezas", "afirmaciones", "huecos"],
            "properties": {"rol": {"type": "string", "enum": ROLES}, "mensaje": {"type": "string"},
                           "preguntas": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                           "piezas": {"type": "array", "items": {"type": "string"}},
                           "afirmaciones": {"type": "array", "items": {"type": "string"}},
                           "huecos": {"type": "array", "items": {"type": "string"}, "maxItems": 4}}}}},
}
DECK_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["titulo", "subtitulo", "laminas", "pendientes"],
    "properties": {
        "titulo": {"type": "string"}, "subtitulo": {"type": "string"},
        "laminas": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False,
            "required": ["rol", "titulo", "mensaje", "puntos", "piezas", "visual", "notas"],
            "properties": {"rol": {"type": "string", "enum": ROLES}, "titulo": {"type": "string"},
                           "mensaje": {"type": "string"},
                           "puntos": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                           "piezas": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                           "visual": {"type": "string"}, "notas": {"type": "string"}}}},
        "pendientes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["rol", "que_falta", "pregunta"],
            "properties": {"rol": {"type": "string", "enum": ROLES}, "que_falta": {"type": "string"},
                           "pregunta": {"type": "string"}}}}},
}
CONDITIONAL = re.compile(r"\b(si|podria|podrian|convendria|convendrian|valdria|seria|sugiere|sugieren|proponemos|"
                         r"recomendamos|proponer|recomendar|antes de)\b")


class NarrativeError(ValueError):
    pass


# ------------------------------------------------------------------ almacenamiento (JSON local, como las investigaciones)
def _now() -> int:
    return int(time.time() * 1000)


def _path(nid: str):
    if not ID_RE.match(nid or ""):
        raise NarrativeError("ID de narrativa inválido.")
    return NARRATIVES / f"{nid}.json"


def load(nid: str) -> dict:
    p = _path(nid)
    if not p.exists():
        raise KeyError(nid)
    return json.loads(p.read_text(encoding="utf-8"))


def save(doc: dict) -> dict:
    NARRATIVES.mkdir(parents=True, exist_ok=True)
    doc["actualizada_ms"] = _now()
    _path(doc["id"]).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return doc


def list_all() -> list[dict]:
    out = []
    for p in sorted(NARRATIVES.glob("NAR-*.json"), reverse=True):
        d = json.loads(p.read_text(encoding="utf-8"))
        out.append({"id": d["id"], "titulo": d["titulo"], "audiencia": d.get("audiencia"), "piezas": len(d["piezas"]),
                    "presentacion": bool(d.get("presentacion")), "actualizada_ms": d.get("actualizada_ms")})
    return out


def _clean(s, limit=MAX_TEXT) -> str:
    return str(s or "").strip()[:limit]


def create(titulo: str, audiencia: str | None = None, objetivo: str = "", contexto: str = "") -> dict:
    titulo = _clean(titulo, 140)
    if not titulo:
        raise NarrativeError("La narrativa necesita un título.")
    if audiencia and audiencia not in AUDIENCES:
        raise NarrativeError(f"Audiencia inválida; usa {AUDIENCES}.")
    doc = {"id": "NAR-" + time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4], "titulo": titulo,
           "audiencia": audiencia or "Mixta", "objetivo": _clean(objetivo, 600), "contexto": _clean(contexto, 20000),
           "piezas": [], "esqueleto": None, "presentacion": None, "uso": {}, "creada_ms": _now(), "origen": []}
    return save(doc)


def _check_piece(p: dict) -> dict:
    if p.get("tipo") not in PIECE_TYPES:
        raise NarrativeError(f"Tipo de pieza inválido; usa {PIECE_TYPES}.")
    if p.get("rol") not in ROLES:
        raise NarrativeError(f"Papel inválido; usa {ROLES}.")
    piece = {"tipo": p["tipo"], "rol": p["rol"], "titulo": _clean(p.get("titulo"), 300), "texto": _clean(p.get("texto")),
             "estado": _clean(p.get("estado"), 40), "nota": _clean(p.get("nota"), 2000),
             "afirmaciones": [], "visual": p.get("visual") if isinstance(p.get("visual"), dict) else None,
             "fuente": p.get("fuente") if isinstance(p.get("fuente"), dict) else {}}
    if not piece["titulo"] or (piece["tipo"] != "nota" and not piece["texto"]):
        raise NarrativeError("La pieza necesita título y texto.")
    for a in (p.get("afirmaciones") or [])[:12]:
        cifras = {str(k)[:60]: str(v)[:80] for k, v in list((a.get("cifras") or {}).items())[:20]}
        piece["afirmaciones"].append({"id": _clean(a.get("id"), 40), "texto": _clean(a.get("texto"), 1200),
                                      "estado": _clean(a.get("estado"), 40), "cifras": cifras})
    if piece["visual"] and len(json.dumps(piece["visual"])) > 60000:
        piece["visual"] = None
    return piece


def add_piece(nid: str, p: dict) -> dict:
    doc = load(nid)
    piece = _check_piece(p)
    n = max([int(x["id"][2:]) for x in doc["piezas"]] + [0]) + 1
    piece.update({"id": f"P-{n:02d}", "creada_ms": _now()})
    doc["piezas"].append(piece)
    return save(doc)


def remove_piece(nid: str, pid: str) -> dict:
    doc = load(nid)
    doc["piezas"] = [x for x in doc["piezas"] if x["id"] != pid]
    return save(doc)


def update(nid: str, patch: dict) -> dict:
    doc = load(nid)
    for k, lim in (("titulo", 140), ("objetivo", 600), ("contexto", 20000)):
        if k in patch and patch[k] is not None:
            doc[k] = _clean(patch[k], lim)
    if patch.get("audiencia"):
        if patch["audiencia"] not in AUDIENCES:
            raise NarrativeError(f"Audiencia inválida; usa {AUDIENCES}.")
        doc["audiencia"] = patch["audiencia"]
    by_id = {x["id"]: x for x in doc["piezas"]}
    for ch in patch.get("piezas") or []:
        x = by_id.get(ch.get("id"))
        if not x:
            continue
        if ch.get("rol"):
            if ch["rol"] not in ROLES:
                raise NarrativeError(f"Papel inválido; usa {ROLES}.")
            x["rol"] = ch["rol"]
        if "nota" in ch:
            x["nota"] = _clean(ch["nota"], 2000)
    if patch.get("orden"):
        order = [i for i in patch["orden"] if i in by_id]
        doc["piezas"] = [by_id[i] for i in order] + [x for x in doc["piezas"] if x["id"] not in order]
    return save(doc)


def delete(nid: str):
    p = _path(nid)
    if p.exists():
        p.unlink()


def merge(ids: list[str], titulo: str) -> dict:
    """Une narrativas en una nueva: todas las piezas (sin duplicar la misma fuente), en el orden de la historia."""
    docs = [load(i) for i in ids]
    if len(docs) < 2:
        raise NarrativeError("Elige al menos dos narrativas para unir.")
    new = create(titulo or " + ".join(d["titulo"] for d in docs), "Mixta",
                 " · ".join(d["objetivo"] for d in docs if d.get("objetivo"))[:600],
                 "\n\n".join(f"[{d['titulo']}]\n{d['contexto']}" for d in docs if d.get("contexto"))[:20000])
    seen, pieces = set(), []
    for d in docs:
        for x in d["piezas"]:
            key = json.dumps(x.get("fuente") or {}, sort_keys=True) if x.get("fuente") else x["id"] + d["id"]
            if key in seen and x["tipo"] != "nota":
                continue
            seen.add(key)
            pieces.append((ROLES.index(x["rol"]), len(pieces), {**x, "nota": (f"[{d['titulo']}] " + x.get("nota", "")).strip()}))
    for k, (_, _, x) in enumerate(sorted(pieces, key=lambda z: (z[0], z[1])), start=1):
        new["piezas"].append({**x, "id": f"P-{k:02d}"})
    new["origen"] = [d["id"] for d in docs]
    return save(new)


# ------------------------------------------------------------------ evidencia de una pieza
def evidence_text(p: dict) -> str:
    """Texto validado de la pieza: su texto, sus afirmaciones y sus cifras. La nota del usuario no es evidencia."""
    if p["tipo"] == "nota":
        return ""
    parts = [p.get("texto", ""), (p.get("visual") or {}).get("titulo", "")]
    lab = _labels()
    for a in p.get("afirmaciones", []):
        parts.append(a.get("texto", ""))
        for k, v in (a.get("cifras") or {}).items():   # la etiqueta (qué mide) también es texto verificado
            parts += [str(v), lab.get(k, k)]
    return " ".join(x for x in parts if x)


def _labels() -> dict:
    return {k: lab for h in CANON.values() for k, lab in (h.get("etiquetas") or {}).items()}


def _brief(doc: dict, with_evidence: bool) -> dict:
    pieces = []
    for p in doc["piezas"]:
        item = {"id": p["id"], "tipo": p["tipo"], "papel": p["rol"], "titulo": p["titulo"], "estado": p.get("estado"),
                "nota_del_usuario": p.get("nota", ""), "texto": p.get("texto", "")[:1500],
                "tiene_grafica": bool(p.get("visual"))}
        if with_evidence:
            lab = _labels()
            item["afirmaciones"] = [{"texto": a["texto"], "estado": a["estado"],
                                     "cifras": {lab.get(k, k): v for k, v in (a.get("cifras") or {}).items()}}
                                    for a in p.get("afirmaciones", [])]
        pieces.append(item)
    return {"titulo": doc["titulo"], "audiencia": doc.get("audiencia"), "objetivo": doc.get("objetivo", ""),
            "contexto": doc.get("contexto", "")[:12000], "piezas": pieces}


# ------------------------------------------------------------------ validación
def validate_plan(plan: dict, piece_ids: set[str]) -> list[str]:
    errors = []
    for i, s in enumerate(plan.get("secciones", []), start=1):
        if s.get("rol") not in ROLES:
            errors.append(f"sección {i}: papel inválido.")
        bad = [x for x in s.get("piezas", []) if x not in piece_ids]
        if bad:
            errors.append(f"sección {i}: piezas inexistentes {bad}.")
        bad = [x for x in s.get("afirmaciones", []) if x not in CANON]
        if bad:
            errors.append(f"sección {i}: afirmaciones canónicas inexistentes {bad}.")
        for fld, texts in (("mensaje", [s.get("mensaje", "")]), ("preguntas", s.get("preguntas", [])), ("huecos", s.get("huecos", []))):
            for t in texts:
                if stray_digits(t) or number_words(t):
                    errors.append(f"sección {i}.{fld}: el esqueleto no lleva cifras (viven en las piezas): «{t[:80]}».")
                if causal_hits(t, allow_explica=False):
                    errors.append(f"sección {i}.{fld}: lenguaje causal {causal_hits(t, allow_explica=False)}.")
    if stray_digits(plan.get("resumen", "")):
        errors.append("resumen: el esqueleto no lleva cifras.")
    return errors


def validate_story(deck: dict, pieces: dict[str, dict]) -> list[str]:
    """Cada cifra, calificativo o verbo de una lámina debe estar respaldado por las piezas que la lámina cita."""
    errors = []
    ev = {k: evidence_text(p) for k, p in pieces.items()}

    def check(where: str, text: str, ids: list[str]):
        if not text:
            return
        cited = " ".join(ev[i] for i in ids if i in ev)
        loose = [n for n in numbers_in(text) if n not in set(numbers_in(cited))]
        loose += [w for w in number_words(text) if w not in number_words(cited)]
        if loose:
            errors.append(f"{where}: cifras que no están en las piezas citadas {loose}.")
        quals = [q for q in qualifiers(text) if q not in qualifiers(cited)]
        if quals:
            errors.append(f"{where}: calificativos sin respaldo en las piezas citadas {quals}.")
        hits = causal_hits(text, allow_explica=bool(re.search(r"\bexplic", norm(cited))))
        if hits:
            errors.append(f"{where}: lenguaje causal no permitido {hits}.")
        if re.search(r"\b(E|EC|C|P)-[A-Z]*-?\d{2,3}\b", text):
            errors.append(f"{where}: la lámina no cita IDs en el texto.")

    all_ids = list(pieces)
    check("titulo", deck.get("titulo", ""), all_ids)
    check("subtitulo", deck.get("subtitulo", ""), all_ids)
    for i, s in enumerate(deck.get("laminas", []), start=1):
        ids = s.get("piezas", [])
        bad = [x for x in ids if x not in pieces]
        if bad or not ids:
            errors.append(f"lámina {i}: cita piezas inexistentes o ninguna {bad}.")
        if s.get("visual") and (s["visual"] not in ids or not pieces.get(s["visual"], {}).get("visual")):
            errors.append(f"lámina {i}: la gráfica debe venir de una pieza citada que tenga gráfica.")
        for fld in ("titulo", "mensaje", "notas"):
            check(f"lámina {i}.{fld}", s.get(fld, ""), ids)
        for j, b in enumerate(s.get("puntos", []), start=1):
            check(f"lámina {i}.punto {j}", b, ids)
        if s.get("rol") in ("Implicación", "Decisión", "Acción"):
            own = any(pieces.get(x, {}).get("rol") in ("Decisión", "Acción") for x in ids)
            if not own and not CONDITIONAL.search(norm(s.get("mensaje", ""))):
                errors.append(f"lámina {i}: una {s.get('rol')} sin pieza de decisión del usuario debe ser condicional "
                              "(si…, convendría…, proponemos…).")
    for i, q in enumerate(deck.get("pendientes", []), start=1):
        if stray_digits(q.get("que_falta", "")) or stray_digits(q.get("pregunta", "")):
            errors.append(f"pendiente {i}: no lleva cifras.")
    return errors


def fallback_deck(doc: dict) -> dict:
    """Presentación sin texto libre: una lámina por pieza, en el orden de la historia. Respaldo si el agente falla."""
    slides = []
    for p in sorted(doc["piezas"], key=lambda x: ROLES.index(x["rol"])):
        if p["tipo"] == "nota":        # decisión o acción del usuario: se muestra tal cual, no es evidencia
            slides.append({"rol": p["rol"], "titulo": p["titulo"], "mensaje": p.get("nota", ""), "puntos": [],
                           "piezas": [p["id"]], "visual": "", "notas": ""})
            continue
        claims = [a["texto"] for a in p.get("afirmaciones", []) if a.get("texto") and a["texto"] != p["texto"]]
        slides.append({"rol": p["rol"], "titulo": p["titulo"], "mensaje": p["texto"][:600], "puntos": claims[:3],
                       "piezas": [p["id"]], "visual": p["id"] if p.get("visual") else "", "notas": p.get("nota", "")})
    missing = [r for r in ROLES if r not in {s["rol"] for s in slides}]
    return {"titulo": doc["titulo"], "subtitulo": doc.get("objetivo", ""), "laminas": slides or [],
            "pendientes": [{"rol": r, "que_falta": "No hay piezas para esta parte de la historia.",
                            "pregunta": ""} for r in missing], "degradada": True}


# ------------------------------------------------------------------ agente: esqueleto y consolidación
async def _structured(system_file: str, prompt: str, schema: dict, doc: dict, role: str):
    from .orchestrator import _base_options
    system = (PROMPTS / system_file).read_text(encoding="utf-8")
    out, uso = None, {}
    async for m in query(prompt=prompt, options=_base_options(system, EFFORT["compositor"], 4, schema)):
        if isinstance(m, ResultMessage):
            u = m.usage or {}
            uso = {"ms": m.duration_ms or 0, "costo_equivalente_usd": m.total_cost_usd or 0,
                   "tokens_salida": u.get("output_tokens")}
            doc.setdefault("uso", {})[f"{role}@{_now()}"] = uso   # una entrada por llamada: el historial no se pisa
            out = m.structured_output
    return out, uso


def _total(usos: list[dict]) -> dict:
    return {"ms": sum(u.get("ms", 0) for u in usos), "costo_equivalente_usd": round(sum(u.get("costo_equivalente_usd", 0) for u in usos), 4)}


async def plan(nid: str) -> dict:
    """Esqueleto de la historia desde el contexto: secciones con su mensaje, preguntas, piezas, hechos y huecos."""
    doc = load(nid)
    if not (doc.get("contexto") or doc.get("objetivo") or doc["piezas"]):
        raise NarrativeError("Pega un contexto, escribe un objetivo o guarda alguna pieza antes de pedir el esqueleto.")
    canon = [{"id": cid, "estado": h["estado"], "afirmacion": h["afirmacion"]} for cid, h in CANON.items()]
    base = ("Narrativa (JSON):\n" + json.dumps(_brief(doc, with_evidence=False), ensure_ascii=False, indent=1)
            + "\n\nHechos verificados disponibles (JSON):\n" + json.dumps(canon, ensure_ascii=False, indent=1))
    prompt, errors, usos = base, [], []
    for attempt in (1, 2):
        out, uso = await _structured("narrador_plan.md", prompt, PLAN_SCHEMA, doc, f"esqueleto_{attempt}")
        usos.append(uso)
        errors = validate_plan(out or {}, {p["id"] for p in doc["piezas"]}) if out else ["sin salida estructurada"]
        if not errors:
            doc["esqueleto"] = {**out, "generado_ms": _now(), "uso": _total(usos)}
            return save(doc)
        prompt = base + "\n\nTu esqueleto anterior no pasó el validador. Corrige y entrégalo completo:\n- " + "\n- ".join(errors)
    save(doc)
    raise NarrativeError("El esqueleto no pasó el validador: " + "; ".join(errors[:4]))


async def consolidate(nid: str) -> dict:
    """Presentación en láminas con solo las piezas guardadas; lo que falta queda como pendiente."""
    doc = load(nid)
    if not [p for p in doc["piezas"] if p["tipo"] != "nota"]:
        raise NarrativeError("Guarda al menos una pieza con evidencia antes de consolidar.")
    pieces = {p["id"]: p for p in doc["piezas"]}
    base = "Narrativa con sus piezas (JSON):\n" + json.dumps(_brief(doc, with_evidence=True), ensure_ascii=False, indent=1)
    if doc.get("esqueleto"):
        base += "\n\nEsqueleto propuesto antes (JSON):\n" + json.dumps(doc["esqueleto"], ensure_ascii=False, indent=1)
    prompt, intentos, usos = base, [], []
    for attempt in (1, 2, 3):
        deck, uso = await _structured("narrador.md", prompt, DECK_SCHEMA, doc, f"presentacion_{attempt}")
        usos.append(uso)
        errors = validate_story(deck or {}, pieces) if deck else ["sin salida estructurada"]
        intentos.append({"intento": attempt, "errores": errors})
        if not errors:
            doc["presentacion"] = {**deck, "degradada": False, "intentos": intentos, "generado_ms": _now(), "uso": _total(usos)}
            return save(doc)
        prompt = base
        if deck:
            prompt += "\n\nTu presentación anterior (JSON):\n" + json.dumps(deck, ensure_ascii=False, indent=1)
        prompt += ("\n\nNo pasó el validador. Devuélvela completa cambiando solo lo necesario para corregir estos puntos "
                   "(no reescribas lo que ya estaba bien):\n- " + "\n- ".join(errors))
    doc["presentacion"] = {**fallback_deck(doc), "intentos": intentos, "generado_ms": _now(), "uso": _total(usos)}
    return save(doc)
