"""Validador determinista (arquitectura v1.2 §5.3–5.4).

El agente propone hipótesis, afirmaciones y estados; este módulo los acepta, los degrada o los rechaza
con motivos. Nada llega a la vista sin pasar por aquí.
"""
from __future__ import annotations

import re
import unicodedata

import yaml

from .config import BRAIN
from .render import FORMATS, fmt_value

ORDER = ["Hipótesis", "Direccional", "Hecho observado", "Evidencia fuerte"]
STATES = ORDER + ["No evaluable"]
CLAIM_TYPES = ["descriptivo", "comparativo", "asociativo", "descomposicion"]
STANCES = ["a_favor", "en_contra"]
STRONG = {"Hecho observado", "Evidencia fuerte"}


def _load(rel: str):
    return yaml.safe_load((BRAIN / rel).read_text(encoding="utf-8"))


GUARD = _load("guardrails/causal_language_es.yaml")
MISSING = {m["id"]: m for m in _load("guardrails/missing_data.yaml")["faltantes"]}
ISSUES = {i["id"]: i for i in _load("data/known_quality_issues.yaml")["issues"]}
PLAYBOOKS = {"arpa_decline": _load("frameworks/playbooks/arpa_decline.yaml")}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


PROHIBITED = [norm(w) for w in GUARD["prohibido"]]
EXPLICA = re.compile(r"\bexplic(a|an|o|aron|ara|aria)\b")
# Tokens con dígitos que no son cifras medidas: años, meses, semestres, trimestres, tenencias e IDs.
ALLOWED_DIGITS = [r"\b20\d\d\s?[–-]\s?\d\d\b", r"\b20\d\d\s?[ST][1-4]\b", r"\b20\d\d\b",
                  r"\b(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)-\d\d\b", r"\bM\d{1,2}\b",
                  r"\b[HQC]-?\d+(\.\d+)*\b", r"\bS&M\b"]


PATTERNS = [re.compile(p) for p in GUARD.get("patrones", [])]


# Cifras escritas con letras y calificativos que afirman una proporción sin ligarla a evidencia.
NUMBER_WORDS = re.compile(r"\b(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|veinte|"
                          r"treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|cientos|mil|millon|"
                          r"millones|mitad|tercio|tercios|doble|triple|cuadruple)\b")
QUALIFIERS = re.compile(r"\b(casi todos|casi todas|casi siempre|casi nunca|la mayoria|la mayor parte|la gran mayoria|"
                        r"siempre|nunca|sin excepcion|practicamente|claramente|sin duda|drasticamente|dramaticamente|masivamente|"
                        r"(en )?cada (mes|trimestre|semestre|ano)|todos los (meses|trimestres|semestres|anos))\b")


def number_words(text: str) -> list[str]:
    return NUMBER_WORDS.findall(norm(re.sub(r"\{[^}]+\}", " ", text)))


def qualifiers(text: str) -> list[str]:
    return [m.group(0) for m in QUALIFIERS.finditer(norm(re.sub(r"\{[^}]+\}", " ", text)))]


def causal_hits(text: str, allow_explica: bool) -> list[str]:
    t = norm(text)
    hits = [w for w in PROHIBITED if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", t)]
    hits += [m.group(0) for p in PATTERNS for m in [p.search(t)] if m and m.group(0) not in hits]
    if not allow_explica and EXPLICA.search(t):
        hits.append("explica (solo se permite en afirmaciones de descomposición)")
    return hits


def stray_digits(text: str) -> list[str]:
    t = re.sub(r"\{[^}]+\}", " ", text)
    for pat in ALLOWED_DIGITS:
        t = re.sub(pat, " ", t)
    return re.findall(r"\d[\d.,]*", t)


def numbers_in(text: str) -> list[str]:
    """Cifras de un texto ya renderizado, sin años ni etiquetas de periodo."""
    t = text
    for pat in ALLOWED_DIGITS:
        t = re.sub(pat, " ", t)
    return [re.sub(r"[.,]$", "", n) for n in re.findall(r"\d[\d.,]*", t)]


def rank(state: str) -> int:
    return ORDER.index(state) if state in ORDER else -1


def cap(state: str, ceiling: str) -> str:
    return state if rank(state) <= rank(ceiling) else ceiling


# ---------------------------------------------------------------------------- hipótesis
HYP_ID = re.compile(r"^H\d+(\.\d+)*$")


def validate_hypotheses(items: list[dict], playbook_id: str = "arpa_decline") -> list[str]:
    errors = []
    pb = PLAYBOOKS.get(playbook_id)
    if pb is None:
        return [f"Playbook desconocido '{playbook_id}'. Disponibles: {list(PLAYBOOKS)}."]
    nodes = {}
    for n in pb["nodos"]:
        nodes[n["id"]] = n
        for c in n.get("hijos", []):
            nodes[c["id"]] = c
    ids = [h.get("id") for h in items]
    if len(ids) != len(set(ids)):
        errors.append("Hay IDs de hipótesis repetidos.")
    for h in items:
        hid = h.get("id", "?")
        if not HYP_ID.match(str(hid)):
            errors.append(f"{hid}: el ID debe tener la forma H1, H1.1, H2…")
        q = str(h.get("pregunta", "")).strip()
        if not (q.startswith("¿") and q.endswith("?")):
            errors.append(f"{hid}: la hipótesis se formula como pregunta (¿…?).")
        if h.get("nodo") not in nodes:
            errors.append(f"{hid}: nodo '{h.get('nodo')}' no existe en el playbook. Nodos: {list(nodes)}.")
        f = h.get("firma") or {}
        if not str(f.get("si_es_cierta", "")).strip() or not str(f.get("si_es_falsa", "")).strip():
            errors.append(f"{hid}: falta la firma esperada (si_es_cierta y si_es_falsa) antes de mirar resultados.")
        p = h.get("padre")
        if p and p not in ids:
            errors.append(f"{hid}: el padre '{p}' no existe.")
    covered = {h.get("nodo") for h in items}
    missing = [nid for nid, n in nodes.items() if n.get("requerido") and nid not in covered]
    if missing:
        errors.append(f"El árbol no cubre la identidad completa: faltan los nodos {missing}.")
    return errors


def hypothesis_status(hid: str, claims: list[dict]) -> tuple[str, str]:
    """Deriva el estado de una hipótesis desde sus afirmaciones aceptadas. Devuelve (estado, motivo)."""
    linked = [(c, l["postura"]) for c in claims if c.get("aceptada") for l in c.get("hipotesis", []) if l.get("id") == hid]
    if not linked:
        return "Pendiente", "sin afirmaciones ligadas"
    fav = [c["estado"] for c, s in linked if s == "a_favor"]
    con = [c["estado"] for c, s in linked if s == "en_contra"]
    strong_for, strong_against = any(e in STRONG for e in fav), any(e in STRONG for e in con)
    weak_against = any(e == "Direccional" for e in con)
    if strong_for and strong_against:
        return "Direccional", "hay afirmaciones fuertes a favor y en contra: la señal depende de la medida"
    if strong_against:
        return "No soportada", "una afirmación en contra con estado Hecho observado o Evidencia fuerte"
    if strong_for and not weak_against:
        return "Soportada", "afirmación a favor con estado Hecho observado o Evidencia fuerte y ninguna en contra"
    if strong_for or any(e == "Direccional" for e in fav):
        return "Direccional", "solo hay apoyo direccional" if not strong_for else "apoyo fuerte con una señal direccional en contra"
    if any(c["estado"] == "No evaluable" for c, _ in linked):
        return "No evaluable", "depende de datos faltantes"
    return "Pendiente", "solo hipótesis sin evidencia"


# ---------------------------------------------------------------------------- afirmaciones
def validate_claim(c: dict, registry, hypothesis_ids: set[str]) -> dict:
    motivos, avisos = [], []
    tipo = c.get("tipo")
    if tipo not in CLAIM_TYPES:
        motivos.append(f"tipo '{tipo}' inválido; usa {CLAIM_TYPES}.")
    propuesto = c.get("estado_propuesto")
    if propuesto not in STATES:
        motivos.append(f"estado_propuesto '{propuesto}' inválido; usa {STATES}.")
    template = str(c.get("plantilla", "")).strip()
    if not template:
        motivos.append("falta la plantilla del texto.")
    stray = stray_digits(template)
    if stray:
        motivos.append(f"cifras escritas a mano en la plantilla: {stray}. Toda cifra debe ser una variable ligada.")
    words = number_words(template)
    if words:
        motivos.append(f"cifras escritas con letras: {words}. Liga la cifra a una evidencia (p. ej. '{{n}} de {{total}} industrias').")
    quals = qualifiers(template)
    if quals:
        motivos.append(f"calificativos sin cifra ligada: {quals}. Quítalos o liga la proporción a una evidencia.")
    hits = causal_hits(template, allow_explica=(tipo == "descomposicion"))
    if hits:
        motivos.append(f"lenguaje causal no permitido: {hits}. Usa 'se asocia con', 'coincide con', 'es consistente con'.")
    for l in c.get("hipotesis") or []:
        if l.get("id") not in hypothesis_ids:
            motivos.append(f"la hipótesis {l.get('id')} no existe en el árbol registrado.")
        if l.get("postura") not in STANCES:
            motivos.append(f"postura '{l.get('postura')}' inválida; usa {STANCES}.")
    if not c.get("hipotesis"):
        motivos.append("la afirmación debe ligarse al menos a una hipótesis (con postura a_favor o en_contra).")

    sup_ids, con_ids = list(c.get("apoyo") or []), list(c.get("en_contra") or [])
    for eid in sup_ids + con_ids:
        if registry.get(eid) is None:
            motivos.append(f"La evidencia {eid} no existe en esta investigación.")

    # variables ligadas
    vars_ = re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", template)
    bindings = dict(c.get("variables") or {})
    rendered = template
    used_ev = []
    for v in dict.fromkeys(vars_):
        ref = bindings.get(v)
        if not ref:
            motivos.append(f"la variable {{{v}}} no está ligada a ninguna evidencia.")
            continue
        fmt = None
        if "|" in ref:
            ref, fmt = ref.split("|", 1)
            if fmt not in FORMATS:
                motivos.append(f"formato '{fmt}' inválido en {{{v}}}; usa {list(FORMATS)}.")
                continue
        try:
            ev, key, value, efmt = registry.resolve(ref)
        except KeyError as e:
            motivos.append(str(e).strip("'\""))
            continue
        row = key[key.index("[") + 1:-1] if "[" in key else None
        if row and row.split("|")[0] in ev.no_comparable:
            motivos.append(f"{{{v}}} liga una comparación no comparable ({ref}): su base cae antes de la ventana limpia.")
            continue
        used_ev.append(ev)
        rendered = rendered.replace("{" + v + "}", fmt_value(value, fmt or efmt))
    extra = [v for v in bindings if v not in vars_]
    if extra:
        avisos.append(f"variables ligadas que la plantilla no usa: {extra}.")
    for ev in used_ev:
        if ev.id not in sup_ids and ev.id not in con_ids:
            sup_ids.append(ev.id)
            avisos.append(f"{ev.id} se agregó al apoyo porque la plantilla usa sus cifras.")

    # estado permitido
    estado = propuesto if propuesto in STATES else "Hipótesis"
    if propuesto == "No evaluable":
        faltan = c.get("datos_faltantes") or []
        bad = [f for f in faltan if f not in MISSING]
        if not faltan or bad:
            motivos.append(f"No evaluable exige citar datos faltantes del catálogo {list(MISSING)}" + (f"; inválidos: {bad}" if bad else "") + ".")
    elif propuesto == "Hipótesis":
        if not sup_ids and not str(c.get("fundamento", "")).strip():
            motivos.append("una Hipótesis necesita evidencia consistente o un fundamento.")
    elif propuesto in ORDER:
        sup = [registry.get(i) for i in sup_ids if registry.get(i)]
        if not sup:
            motivos.append("una afirmación sin evidencia de apoyo no puede pasar de Hipótesis.")
        else:
            bound_ceil = min((ev.ceiling for ev in used_ev), key=rank, default=max((e.ceiling for e in sup), key=rank))
            allowed = bound_ceil
            if propuesto == "Evidencia fuerte":
                sigs = {(e.tool, e.method, e.variant) for e in sup}
                enough_n = all((e.n or 999) >= 30 for e in sup)
                canonical_ef = any(e.canonical and e.ceiling == "Evidencia fuerte" for e in (used_ev or sup))
                if (len(sigs) >= 2 and enough_n and not con_ids and rank(bound_ceil) >= rank("Hecho observado")) or canonical_ef:
                    allowed = "Evidencia fuerte"
                else:
                    avisos.append("Evidencia fuerte exige dos evidencias de apoyo con método o variante distintos, n ≥ 30 "
                                  "y ninguna en contra; se degrada.")
            if tipo == "asociativo" and rank(allowed) > rank("Direccional"):
                allowed = "Direccional"
                avisos.append("las asociaciones tienen techo Direccional.")
            if con_ids and rank(allowed) > rank("Direccional"):
                allowed = "Direccional"
                avisos.append("hay evidencia en contra: el techo es Direccional.")
            estado = cap(propuesto, allowed)
            if estado != propuesto:
                avisos.append(f"estado degradado de {propuesto} a {estado}.")

    caveats = list(dict.fromkeys(list(c.get("caveats") or []) + [cv for ev in used_ev for cv in ev.caveat_ids]))
    unknown = [cv for cv in caveats if cv not in ISSUES]
    if unknown:
        hints = {cv: _issue_hint(cv) for cv in unknown}
        motivos.append(f"precauciones desconocidas {unknown}; usa IDs de known_quality_issues.yaml"
                       + ("" if not any(hints.values()) else " (¿quisiste decir " + ", ".join(f"{h}" for h in hints.values() if h) + "?)") + ".")
    marcadores = []
    if caveats:
        marcadores.append("Precaución")
    if any(ev.marker for ev in used_ev):
        marcadores.append("Cálculo ad hoc")
    if "{" in rendered:
        motivos.append("quedaron variables sin resolver en el texto.")
    motivos, avisos = list(dict.fromkeys(motivos)), list(dict.fromkeys(avisos))
    return {"aceptada": not motivos, "motivos": motivos, "avisos": avisos, "estado_propuesto": propuesto,
            "estado": estado if not motivos else None, "texto": rendered if not motivos else None,
            "apoyo": sup_ids, "en_contra": con_ids, "caveats": caveats, "marcadores": marcadores}


def _issue_hint(text: str) -> str | None:
    t = set(w for w in norm(text).split() if len(w) > 4)
    best = max(ISSUES.values(), key=lambda i: len(t & set(w for w in norm(i["titulo"]).split() if len(w) > 4)))
    return best["id"] if len(t & set(w for w in norm(best["titulo"]).split() if len(w) > 4)) >= 2 else None


# ---------------------------------------------------------------------------- composición
def validate_composition(doc: dict, claims: dict[str, dict]) -> list[str]:
    """Cada cifra del texto debe aparecer en alguna de las afirmaciones que el bloque cita."""
    errors = []

    def check(where: str, text: str, ids: list[str]):
        if not text:
            return
        bad = [i for i in ids if i not in claims or not claims[i].get("aceptada")]
        if bad:
            errors.append(f"{where}: cita afirmaciones inexistentes o rechazadas {bad}.")
        cited = " ".join(claims[i]["texto"] for i in ids if i in claims and claims[i].get("texto"))
        allowed_nums = set(numbers_in(cited))
        loose = [n for n in numbers_in(text) if n not in allowed_nums]
        loose += [w for w in number_words(text) if w not in number_words(cited)]
        if loose:
            errors.append(f"{where}: cifras que no están en las afirmaciones citadas {loose}.")
        quals = [q for q in qualifiers(text) if q not in qualifiers(cited)]
        if quals:
            errors.append(f"{where}: calificativos sin respaldo en las afirmaciones citadas {quals}.")
        explica_ok = any(claims[i].get("tipo") == "descomposicion" for i in ids if i in claims)
        hits = causal_hits(text, allow_explica=explica_ok)
        if hits:
            errors.append(f"{where}: lenguaje causal no permitido {hits}.")
        if re.search(r"\bE-\d{3}\b", text):
            errors.append(f"{where}: la narrativa no puede citar evidencias directamente.")

    ra = doc.get("respuesta_ejecutiva") or {}
    if not ra.get("claim_ids"):
        errors.append("respuesta_ejecutiva: debe citar al menos una afirmación.")
    check("respuesta_ejecutiva", ra.get("texto", ""), ra.get("claim_ids", []))
    for i, h in enumerate(doc.get("hallazgos", [])):
        ids = h.get("claim_ids", [])
        if not ids:
            errors.append(f"hallazgo {i + 1}: sin afirmaciones.")
        for fld in ("interpretacion", "implicacion", "por_que"):
            check(f"hallazgo {i + 1}.{fld}", h.get(fld, ""), ids)
    for i, b in enumerate(doc.get("limites", [])):
        check(f"límite {i + 1}", b.get("texto", ""), b.get("claim_ids", []))
    for i, b in enumerate(doc.get("implicaciones", [])):
        check(f"implicación {i + 1}", b.get("texto", ""), b.get("claim_ids", []))
        if not re.search(r"\b(si|podria|podrian|convendria|valdria|seria|sugiere)\b", norm(b.get("texto", ""))):
            errors.append(f"implicación {i + 1}: debe ser condicional (si…, podría…, convendría…).")
    for i, q in enumerate(doc.get("proximas_preguntas", [])):
        if stray_digits(q):
            errors.append(f"próxima pregunta {i + 1}: no lleva cifras.")
    return errors
