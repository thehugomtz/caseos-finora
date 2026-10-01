"""Gramática visual determinista (arquitectura v1.2 §4): intención → forma, título = afirmación validada.

El agente solo pide la intención; la forma y los datos salen de la evidencia.
"""
from __future__ import annotations

import functools
import math
import re

INTENTS = {
    "tendencia": "Tendencia de una métrica (línea)",
    "crecimientos": "Crecimientos en unidades distintas (índice base 100)",
    "composicion": "Composición (barras apiladas al 100%)",
    "descomposicion": "Descomposición aditiva o puente (cascada)",
    "comparacion": "Segmentos en dos o tres periodos (puntos conectados)",
    "intervalo": "Estimación con intervalo (puntos con rango)",
    "distribucion": "Distribución (barras por banda)",
    "cifra": "Una cifra (tarjeta KPI)",
    "dispersion": "Relación entre dos medidas por segmento (dispersión; burbujas si hay una tercera medida de tamaño)",
    "detalle": "Detalle (tabla)",
}


class VisualError(ValueError):
    pass


AVAILABLE = [("Monto pagado por cliente y mes (amount)", "Disponible"), ("Industria del cliente", "Disponible"),
             ("Gasto de S&M por mes y rubro", "Disponible, sin unidad documentada")]
DEFAULT_INTENT = {"mix_within_decomposition": "descomposicion", "vintage_arpa": "descomposicion",
                  "churn_selection": "intervalo", "ticket_distribution": "distribucion"}


def data_gap(missing_ids: list[str]) -> dict:
    """Visual de lo No evaluable: qué datos existen y cuáles faltan para responder."""
    from .validator import MISSING
    filas = [{"dato": d, "estado": e, "campos": ""} for d, e in AVAILABLE]
    filas += [{"dato": MISSING[m]["nombre"], "estado": "No existe", "campos": ", ".join(MISSING[m].get("campos_necesarios", []))}
              for m in missing_ids if m in MISSING]
    return {"tipo": "datos", "filas": filas}


@functools.lru_cache(maxsize=1)
def _cards() -> tuple[dict, dict]:
    """Tarjetas del workspace de la Fase 1: sus afirmaciones (linaje) y sus gráficas (template)."""
    import yaml
    from .config import BRAIN, ROOT
    cards = yaml.safe_load((BRAIN / "evidence" / "workspace_cards.yaml").read_text(encoding="utf-8"))["cards"]
    tpl = (ROOT / "templates" / "finora_eda_template.html").read_text(encoding="utf-8")
    charts = {}
    for m in re.finditer(r'data-card="([0-9.]+)"', tpl):
        end = tpl.find('class="foot"', m.end())
        charts[m.group(1)] = re.findall(r'data-chart="([a-zA-Z]+)"', tpl[m.end():end if end != -1 else None])
    return cards, charts


def workspace_card(evs) -> dict:
    """Evidencia canónica de la Fase 1: su gráfica ya existe en el workspace y se reutiliza.

    Entre las tarjetas con gráfica elige la que cubre más afirmaciones canónicas de la evidencia; en empate, la de la
    primera evidencia y después la más específica (con menos afirmaciones).
    """
    cids = [(e.params or {}).get("claim_id") for e in evs if e.kind == "canonical"]
    cards, charts = _cards()
    best = None
    for k, v in cards.items():
        own = v.get("claims") or []
        cover = [c for c in cids if c in own]
        if not cover or not charts.get(k):
            continue
        rank = (len(cover), -cids.index(cover[0]), -len(own))
        if best is None or rank > best[0]:
            best = (rank, k, cover)
    if not best:
        raise VisualError(f"Las afirmaciones {cids} de la Fase 1 no tienen una tarjeta con gráfica en el workspace.")
    _, key, cover = best
    return {"tipo": "tarjeta", "tarjeta": key, "claim_fase1": cover[0], "cubre": cover}


@functools.lru_cache(maxsize=1)
def _canon() -> dict:
    import yaml
    from .config import BRAIN
    return {h["id"]: h for h in yaml.safe_load((BRAIN / "evidence" / "canonical_findings.yaml").read_text(encoding="utf-8"))["hallazgos"]}


def canonical_visual(evs) -> dict:
    """Evidencia canónica de la Fase 1: la gráfica propia del hallazgo (su idea) o, si no tiene, la de su tarjeta del
    workspace. Nunca una tabla de cifras sueltas."""
    for e in evs:
        cid = (e.params or {}).get("claim_id")
        g = (_canon().get(cid) or {}).get("grafica") if e.kind == "canonical" else None
        if g:
            return {**g, "claim_fase1": cid}
    return workspace_card(evs)


PERIOD = re.compile(r"^20\d\d(-\d\d|\s?[ST][1-4])?$")


def _periodic(ev) -> bool:
    """Un resultado que se puede leer en el tiempo: al menos tres filas y la primera columna son periodos."""
    r = ev.result or {}
    cols = r.get("columnas") or []
    rows = r.get("filas") or []
    return len(rows) >= 3 and bool(cols) and all(PERIOD.match(str(f.get(cols[0]["id"], ""))) for f in rows)


def default_intent(ev) -> str | None:
    if ev.kind == "analysis":
        return DEFAULT_INTENT.get(ev.params.get("analysis_id"))
    if ev.kind == "metric":
        return "tendencia"
    if ev.kind == "sql" and _periodic(ev):
        return "tendencia"
    return None


def _tabla(ev) -> dict:
    r = ev.result
    return {"tipo": "tabla", "columnas": r.get("columnas", []), "filas": r.get("filas", [])}


def build(ev, intent: str, ejes: dict | None = None) -> dict:
    if intent not in INTENTS:
        raise VisualError(f"Intención '{intent}' inválida. Opciones: {list(INTENTS)}.")
    r, kind = ev.result, ev.kind
    if intent == "dispersion":
        return dispersion(ev, ejes)
    if kind == "canonical":   # la idea ya tiene su gráfica en la Fase 1; la tabla sigue en el linaje
        try:
            return canonical_visual([ev])
        except VisualError:
            if intent == "detalle":
                return _tabla(ev)
            raise
    if intent == "detalle":
        return _tabla(ev)
    if kind == "metric":
        return _from_metric(ev, intent)
    if kind == "analysis":
        aid = ev.params.get("analysis_id")
        fn = {"mix_within_decomposition": _from_mix, "vintage_arpa": _from_vintage,
              "churn_selection": _from_churn, "ticket_distribution": _from_ticket}.get(aid)
        if fn:
            return fn(ev, intent)
    if kind == "sql" and intent == "tendencia" and _periodic(ev):
        cols = [c["id"] for c in r.get("columnas", [])]
        num = [c for c in cols[1:] if all(isinstance(f.get(c), (int, float)) or f.get(c) is None for f in r["filas"])]
        if num:
            return {"tipo": "linea", "x": [str(f[cols[0]]) for f in r["filas"]],
                    "series": [{"nombre": c, "valores": [f.get(c) for f in r["filas"]]} for c in num[:3]], "formato": "num2"}
    raise VisualError(f"La evidencia {ev.id} ({kind}) no admite la intención '{intent}'. Usa 'detalle' o elige otra evidencia.")


def _from_metric(ev, intent):
    r = ev.result
    filas = r["filas"]
    fmt = next((c.get("formato") for c in r["columnas"] if c["id"] == "valor"), "num2")
    dims = [c["id"] for c in r["columnas"] if c["id"] in ("industry", "vintage")]
    label = r.get("label", ev.params.get("metric_id"))
    periods = list(dict.fromkeys(f["periodo"] for f in filas))
    if intent == "cifra":
        f = filas[-1]
        return {"tipo": "kpi", "valor": f.get("valor"), "formato": fmt, "etiqueta": f"{label} · {f['periodo']}"}
    col = "indice" if (intent == "crecimientos" and any("indice" in f for f in filas)) else "valor"
    if intent == "crecimientos" and col != "indice":
        raise VisualError("Para 'crecimientos' pide la métrica con comparacion='index'.")
    if intent in ("tendencia", "crecimientos"):
        if not dims:
            return {"tipo": "linea", "x": periods, "series": [{"nombre": label, "valores": [f.get(col) for f in filas]}],
                    "formato": "idx" if col == "indice" else fmt}
        d = dims[0]
        groups = list(dict.fromkeys(f[d] for f in filas))
        return {"tipo": "linea", "x": periods, "formato": "idx" if col == "indice" else fmt,
                "series": [{"nombre": g, "valores": [next((f.get(col) for f in filas if f["periodo"] == p and f[d] == g), None)
                                                      for p in periods]} for g in groups]}
    if intent == "composicion":
        if not dims or r.get("kind") in ("ratio", "rate", "distribution"):
            raise VisualError("La composición necesita una métrica aditiva (clientes o MRR) con un corte.")
        d = dims[0]
        groups = list(dict.fromkeys(f[d] for f in filas))
        tot = {p: sum(f["valor"] or 0 for f in filas if f["periodo"] == p) for p in periods}
        return {"tipo": "barras", "apiladas": True, "x": periods, "formato": "pct",
                "series": [{"nombre": g, "valores": [next(((f["valor"] or 0) / tot[p] for f in filas if f["periodo"] == p and f[d] == g), 0)
                                                      if tot[p] else None for p in periods]} for g in groups]}
    if intent == "comparacion":
        if not dims or len(periods) > 3:
            raise VisualError("La comparación necesita un corte y como máximo tres periodos (usa grano 'year' o un periodo corto).")
        d = dims[0]
        groups = list(dict.fromkeys(f[d] for f in filas))
        return {"tipo": "puntos", "filas": groups, "formato": fmt,
                "series": [{"nombre": p, "valores": [next((f.get("valor") for f in filas if f["periodo"] == p and f[d] == g), None)
                                                      for g in groups]} for p in periods]}
    raise VisualError(f"La evidencia {ev.id} no admite la intención '{intent}'.")


def _from_mix(ev, intent):
    v, p = ev.result["valores"], ev.params
    b, c = p.get("base", "2022"), p.get("comparacion", "2024")
    if intent == "descomposicion":
        return {"tipo": "cascada", "formato": "cop", "pasos": [
            {"etiqueta": f"{b}", "valor": v["ticket_base"], "tipo": "total"},
            {"etiqueta": "Mix de\nindustrias", "corta": "Mix", "valor": v["mix"], "tipo": "delta"},
            {"etiqueta": "Dentro de las\nindustrias", "corta": "Dentro", "valor": v["dentro"], "tipo": "delta"},
            {"etiqueta": f"{c}", "valor": v["ticket_comparacion"], "tipo": "total"}]}
    if intent == "comparacion":
        filas = ev.result["filas"]
        return {"tipo": "puntos", "filas": [f["industria"] for f in filas], "formato": "cop",
                "series": [{"nombre": b, "valores": [f["ticket_base"] for f in filas]},
                           {"nombre": c, "valores": [f["ticket_comparacion"] for f in filas]}]}
    raise VisualError("La descomposición mix/dentro admite 'descomposicion', 'comparacion' o 'detalle'.")


def _from_vintage(ev, intent):
    v, filas, p = ev.result["valores"], ev.result["filas"], ev.params
    from .render import period_label
    d, h = period_label(p["desde"]), period_label(p["hasta"])
    if intent == "descomposicion":
        return {"tipo": "cascada", "formato": "cop", "pasos": [
            {"etiqueta": d, "valor": v["mrr_por_cliente_desde"], "tipo": "total"},
            {"etiqueta": "Composición", "corta": "Comp.", "valor": v["composicion"], "tipo": "delta"},
            {"etiqueta": "Dentro de\ncada cosecha", "corta": "Dentro", "valor": v["dentro"], "tipo": "delta"},
            {"etiqueta": h, "valor": v["mrr_por_cliente_hasta"], "tipo": "total"}]}
    if intent == "composicion":
        return {"tipo": "barras", "apiladas": True, "x": [d, h], "formato": "pct",
                "series": [{"nombre": f["cosecha"], "valores": [f["participacion_desde"], f["participacion_hasta"]]} for f in filas]}
    if intent == "comparacion":
        rows = [f for f in filas if f["mrr_por_cliente_hasta"] is not None]
        return {"tipo": "puntos", "filas": [f["cosecha"] for f in rows], "formato": "cop",
                "series": [{"nombre": d, "valores": [f["mrr_por_cliente_desde"] for f in rows]},
                           {"nombre": h, "valores": [f["mrr_por_cliente_hasta"] for f in rows]}]}
    raise VisualError("MRR por cosecha admite 'descomposicion', 'composicion', 'comparacion' o 'detalle'.")


def _from_churn(ev, intent):
    filas = ev.result["filas"]
    if intent in ("intervalo", "comparacion"):
        rows, lo, mid, hi = [], [], [], []
        for f in filas:
            for m, lab in (("razon_medias", "medias"), ("razon_medianas", "medianas")):
                rows.append(f"{f['periodo']} · {lab}")
                lo.append(f[f"{m}_ic90_inf"])
                mid.append(f[m])
                hi.append(f[f"{m}_ic90_sup"])
        return {"tipo": "puntos", "filas": rows, "formato": "num2", "referencia": 1.0,
                "series": [{"nombre": "IC 90% inferior", "valores": lo}, {"nombre": "Razón", "valores": mid},
                           {"nombre": "IC 90% superior", "valores": hi}]}
    raise VisualError("La selección de salida admite 'intervalo', 'comparacion' o 'detalle'.")


def _from_ticket(ev, intent):
    filas = ev.result["filas"]
    years = [f["año"] for f in filas]
    if intent == "distribucion":
        bands = [k.replace("banda ", "") for k in filas[0] if k.startswith("banda ")]
        return {"tipo": "barras", "apiladas": False, "x": bands, "formato": "pct",
                "series": [{"nombre": y, "valores": [f[f"banda {b}"] for b in bands]} for y, f in zip(years, filas)]}
    if intent == "comparacion":
        return {"tipo": "puntos", "filas": years, "formato": "cop",
                "series": [{"nombre": n, "valores": [f[k] for f in filas]} for k, n in (("p25", "P25"), ("mediana", "Mediana"), ("p75", "P75"))]}
    raise VisualError("La distribución del ticket admite 'distribucion', 'comparacion' o 'detalle'.")



# ---------------------------------------------------------------------------- la gráfica de una idea
def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def _label(key: str) -> tuple[str, str | None]:
    """'pct_baja_persiste[28581]' → ('baja persiste', None); 'eventos_ambiguos[bajas]' → ('eventos ambiguos', 'bajas')."""
    col, row = (key.split("[", 1) + [""])[:2]
    row = row.rstrip("]") or None
    if row and re.fullmatch(r"[\d.]+", row) and not PERIOD.match(row):   # índice de fila, no un periodo
        row = None
    col = re.sub(r"^(pct|n|num|share|porc|total)_", "", col)
    return col.replace("_", " ").strip(), row


def claim_visual(c: dict, registry) -> dict | None:
    """La gráfica de una afirmación, derivada de las cifras que liga (el código elige la forma, no el agente):

    1. No evaluable → tabla de datos disponibles contra faltantes.
    2. Si liga sobre todo cifras de hallazgos de la Fase 1 → la gráfica propia de ese hallazgo o de su tarjeta.
       Si liga un análisis del catálogo → la forma de ese análisis.
    3. Métricas por periodo → una serie por métrica (barras si son pocos periodos, línea si son muchos).
    4. Participaciones de un mismo todo → barra apilada al 100%.
    5. Cifras del mismo tipo de una misma evidencia → barras (filas × columnas si hay cortes).
    6. Si nada de eso aplica, ninguna: una tabla de cifras sueltas no es una idea.
    """
    if c.get("estado") == "No evaluable":
        return data_gap(c.get("datos_faltantes") or [])
    tpl = c.get("plantilla") or ""
    binds = []
    for var, ref in (c.get("variables") or {}).items():
        ref0, fmt = (str(ref).split("|", 1) + [None])[:2]
        try:
            ev, key, value, efmt = registry.resolve(ref0)
        except KeyError:
            continue
        binds.append({"var": var, "ev": ev, "key": key, "value": value, "fmt": fmt or efmt,
                      "pp": ("{" + var + "}%") in tpl})
    canon = [b for b in binds if b["ev"].kind == "canonical"]
    num = [b for b in binds if b["ev"].kind != "canonical" and _is_num(b["value"])]
    if canon and len(canon) >= len(num):
        weight = {}
        for b in canon:
            weight[b["ev"].id] = weight.get(b["ev"].id, 0) + 1
        for eid in sorted(weight, key=lambda k: -weight[k]):
            try:
                return canonical_visual([registry.get(eid)])
            except VisualError:
                continue
    if not num:
        sup = [registry.get(e) for e in c.get("apoyo") or []]
        can = [e for e in sup if e is not None and e.kind == "canonical"]
        if can:
            try:
                return canonical_visual(can)
            except VisualError:
                return None
        return None
    # 2b · un análisis del catálogo ya tiene su forma (cascada, intervalo, distribución)
    for b in num:
        it = default_intent(b["ev"]) if b["ev"].kind == "analysis" else None
        if it:
            try:
                return build(b["ev"], it)
            except VisualError:
                pass
    # 3 · métricas por periodo (p. ej. expansión frente a reactivación por año)
    per = [b for b in num if b["ev"].kind == "metric" and PERIOD.match(_label(b["key"])[1] or "")]
    if len({b["ev"].id for b in per}) >= 2 and len({b["fmt"] for b in per}) == 1:
        from .render import period_label
        xs = sorted({_label(b["key"])[1] for b in per})
        series = []
        for eid in dict.fromkeys(b["ev"].id for b in per):
            ev = registry.get(eid)
            vals = {_label(b["key"])[1]: b["value"] for b in per if b["ev"].id == eid}
            series.append({"nombre": (ev.result or {}).get("label") or eid, "valores": [vals.get(x) for x in xs]})
        return {"tipo": "barras" if len(xs) <= 6 else "linea", "x": [period_label(x) for x in xs], "series": series,
                "formato": per[0]["fmt"] or "num2"}
    # 4 · participaciones (en fracción o en puntos porcentuales con % en la plantilla)
    shares = [b for b in num if b["fmt"] in ("pct", "pct0") or b["pp"]]
    if shares and len({b["ev"].id for b in shares}) == 1:
        vals = [b["value"] / 100 if b["pp"] else b["value"] for b in shares]
        tot = sum(vals)
        if all(0 <= v <= 1 for v in vals) and (len(vals) == 1 or 0.97 <= tot <= 1.03):
            series = [{"nombre": _label(b["key"])[0], "valores": [v]} for b, v in zip(shares, vals)]
            if len(vals) == 1:
                series.append({"nombre": "Resto", "valores": [1 - vals[0]]})
            return {"tipo": "barras", "apiladas": True, "x": [""], "series": series, "formato": "pct"}
    # 4b · dos o tres medidas distintas sobre los mismos segmentos (tres o más) de una evidencia → dispersión
    cells = {}
    for b in num:
        col, row = _label(b["key"])
        if row and not PERIOD.match(row):
            cells.setdefault(b["ev"].id, {}).setdefault(b["key"].split("[", 1)[0], {})[b["key"].split("[", 1)[1].rstrip("]")] = b
    for eid, bycol in cells.items():
        names = list(bycol)
        common = set.intersection(*(set(bycol[c]) for c in names)) if names else set()
        if 2 <= len(names) <= 3 and len(common) >= 3 and len({bycol[c][next(iter(common))]["fmt"] for c in names}) >= 2:
            try:
                return dispersion(registry.get(eid), dict(zip(("x", "y", "tamano"), names)))
            except VisualError:
                pass
    # 5 · cifras del mismo tipo de una misma evidencia
    groups = {}
    for b in num:
        g = groups.setdefault((b["ev"].id, b["fmt"]), {})
        g.setdefault(b["key"], b)                        # la misma cifra ligada dos veces cuenta una vez
    best = list(max(groups.values(), key=len).values())
    vals = [abs(b["value"]) for b in best if b["value"]]
    if len(best) < 2 or len(best) > 8 or (vals and max(vals) / min(vals) > 100):
        return None
    ev = best[0]["ev"]
    from .render import period_label
    labels = [_label(b["key"]) for b in best]
    rows = list(dict.fromkeys(r for _, r in labels if r))
    cols = list(dict.fromkeys(cl for cl, _ in labels))
    name = lambda cl: (ev.result or {}).get("label") or cl if cl == "valor" else cl   # noqa: E731
    xlab = lambda r: period_label(r) if PERIOD.match(r) else r                        # noqa: E731
    fmt = best[0]["fmt"] if best[0]["fmt"] in ("int", "cop", "cop2", "pct", "pct0", "num1", "num2", "x") else "num2"
    if rows and len(rows) * len(cols) == len(best):
        return {"tipo": "barras", "x": [xlab(r) for r in rows], "formato": fmt,
                "series": [{"nombre": name(cl), "valores": [next(b["value"] for b, (c2, r2) in zip(best, labels) if c2 == cl and r2 == r)
                                                            for r in rows]} for cl in cols]}
    # sin cortes, solo si miden lo mismo: las etiquetas comparten una palabra (p. ej. "clientes", "meses")
    toks = [{w for w in cl.split() if len(w) >= 4} for cl, _ in labels]
    if not set.intersection(*toks):
        return None
    return {"tipo": "barras", "x": [cl + (f" · {r}" if r else "") for cl, r in labels], "formato": fmt,
            "series": [{"nombre": "", "valores": [b["value"] for b in best]}]}



# ---------------------------------------------------------------------------- dispersión (y burbujas)
def _axis(col: str, vals: list[float], fmt: str | None) -> tuple[list[float], str]:
    """Formato de un eje: puntos porcentuales (p. ej. churn_pct = 1,84) pasan a fracción para mostrarse como %."""
    name = col.lower()
    if re.search(r"pct|porc|share|tasa|rate", name) and vals and max(abs(v) for v in vals) <= 100 and max(abs(v) for v in vals) > 1:
        return [v / 100 for v in vals], "pct2"
    if re.search(r"pct|porc|share|tasa|rate", name) and vals and max(abs(v) for v in vals) <= 1:
        return vals, "pct2"
    if fmt in ("cop", "cop2", "pct", "pct0", "int", "x"):
        return vals, fmt
    if re.search(r"cop|mrr|ticket|monto|arpa", name):
        return vals, "cop"
    if all(float(v).is_integer() for v in vals):
        return vals, "int"
    return vals, fmt if fmt in ("num1", "num2") else "num2"


def _axis_name(col: str) -> str:
    """'churn_obs_2024_pct' → 'churn obs 2024' (sin la unidad, que ya muestra el eje)."""
    words = [w for w in col.split("_") if w.lower() not in ("cop", "pct", "porc")]
    return " ".join(words) or col


def dispersion(ev, ejes: dict | None = None) -> dict:
    """Una fila por punto (segmento): x e y numéricas, tamaño opcional (burbujas) y una etiqueta por punto.

    Los ejes vienen de las columnas de una sola evidencia, así que cada punto es una fila registrada. Sin ejes
    explícitos: la primera columna de texto es la etiqueta y las primeras numéricas son x, y y tamaño.
    """
    r = ev.result or {}
    cols = r.get("columnas") or []
    rows = r.get("filas") or []
    ids = [c["id"] for c in cols]
    numeric = [c for c in ids if rows and all(_is_num(f.get(c)) for f in rows)]
    text = [c for c in ids if c not in numeric]
    ejes = {k: v for k, v in dict(ejes or {}).items() if v}
    ejes.setdefault("etiqueta", text[0] if text else None)
    free = [c for c in numeric if c not in [ejes.get(k) for k in ("x", "y", "tamano")]]
    for k in ("x", "y", "tamano"):
        if not ejes.get(k) and free and (k != "tamano" or len(numeric) >= 3):
            ejes[k] = free.pop(0)
    for k in ("x", "y", "tamano", "etiqueta"):
        if ejes.get(k) and ejes[k] not in ids:
            raise VisualError(f"La columna '{ejes[k]}' ({k}) no existe en {ev.id}. Columnas: {ids}.")
    if not ejes.get("x") or not ejes.get("y"):
        raise VisualError(f"La dispersión necesita dos columnas numéricas en {ev.id} (una fila por punto). Arma una consulta con una fila "
                          "por segmento y una columna por eje (run_sql).")
    for k in ("x", "y", "tamano"):
        if ejes.get(k) and ejes[k] not in numeric:
            raise VisualError(f"La columna '{ejes[k]}' ({k}) no es numérica en todas las filas de {ev.id}.")
    if len(rows) < 3:
        raise VisualError("Una dispersión necesita al menos tres puntos.")
    if ejes.get("tamano") and any(float(f[ejes["tamano"]]) < 0 for f in rows):
        raise VisualError("El tamaño de la burbuja no puede ser negativo.")
    fmts = {c.get("id"): c.get("formato") for c in cols}
    axes, pts = {}, [{"etiqueta": str(f.get(ejes["etiqueta"])) if ejes.get("etiqueta") else str(i + 1)} for i, f in enumerate(rows)]
    for k, key in (("x", "x"), ("y", "y"), ("tamano", "tam")):
        col = ejes.get(k)
        if not col:
            continue
        vals, fmt = _axis(col, [float(f[col]) for f in rows], fmts.get(col))
        axes[k] = {"columna": col, "nombre": str(ejes.get(f"nombre_{k}") or _axis_name(col))[:80], "formato": fmt}
        for p, val in zip(pts, vals):
            p[key] = val
    return {"tipo": "dispersion", "puntos": pts, "ejes": axes, "etiqueta": (ejes.get("etiqueta") or "punto").replace("_", " ")}
