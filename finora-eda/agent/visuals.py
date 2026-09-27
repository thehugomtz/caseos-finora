"""Gramática visual determinista (arquitectura v1.2 §4): intención → forma, título = afirmación validada.

El agente solo pide la intención; la forma y los datos salen de la evidencia.
"""
from __future__ import annotations

INTENTS = {
    "tendencia": "Tendencia de una métrica (línea)",
    "crecimientos": "Crecimientos en unidades distintas (índice base 100)",
    "composicion": "Composición (barras apiladas al 100%)",
    "descomposicion": "Descomposición aditiva o puente (cascada)",
    "comparacion": "Segmentos en dos o tres periodos (puntos conectados)",
    "intervalo": "Estimación con intervalo (puntos con rango)",
    "distribucion": "Distribución (barras por banda)",
    "cifra": "Una cifra (tarjeta KPI)",
    "detalle": "Detalle (tabla)",
}


class VisualError(ValueError):
    pass


def _tabla(ev) -> dict:
    r = ev.result
    return {"tipo": "tabla", "columnas": r.get("columnas", []), "filas": r.get("filas", [])}


def build(ev, intent: str) -> dict:
    if intent not in INTENTS:
        raise VisualError(f"Intención '{intent}' inválida. Opciones: {list(INTENTS)}.")
    r, kind = ev.result, ev.kind
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
    if kind == "sql" and intent == "tendencia":
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
