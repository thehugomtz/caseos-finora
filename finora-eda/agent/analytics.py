"""Catálogo cerrado de análisis de la slice (arquitectura v1.2 §4, run_analysis).

Cada análisis devuelve una o más evidencias (una por variante). Los métodos salen de finora_eda.py
cuando ya existían, para que el agente obtenga exactamente las cifras de la Fase 1.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from finora_eda import BOOT_N, PRICE_BAND_LABELS, PRICE_BANDS, SEED, bootstrap_decomp, shapley

from .config import CLEAN_START, WINDOW_END
from .render import period_label

CATALOG = {
    "mix_within_decomposition": {
        "descripcion": "Descompone el cambio del ticket de entrada promedio entre dos años en mix de industrias "
                       "y efecto dentro de cada industria (Shapley punto medio, exacto) con intervalos bootstrap de 90%.",
        "params": {"base": "'2022' | '2023' | '2024' (por defecto '2022')",
                   "comparacion": "'2022' | '2023' | '2024' (por defecto '2024')",
                   "variantes": "lista de 'm0', 'm0_winsor', 'early_run_rate' (por defecto las tres; cada una es una evidencia)"},
    },
    "vintage_arpa": {
        "descripcion": "MRR por cliente activo por cosecha (año de alta) en dos fechas y descomposición del cambio "
                       "del MRR por cliente en composición (quién entra y pesa más) y efecto dentro de cada cosecha.",
        "params": {"hasta": "'AAAA-MM' (por defecto '2024-10')",
                   "desde": "lista de fechas base 'AAAA-MM' (por defecto ['2022-01', '2022-12']; cada una es una evidencia)"},
    },
    "churn_selection": {
        "descripcion": "¿Se van los clientes de mayor ticket? Compara el monto usual de quienes hacen churn contra el de "
                       "los activos del mes previo, por año: razón de medias y razón de medianas con intervalos "
                       "bootstrap de 90%. Razón > 1: quienes se van pagaban más que el promedio.",
        "params": {"persistente_meses": "entero (por defecto 3): además mide solo churns que no vuelven en ese plazo"},
    },
    "ticket_distribution": {
        "descripcion": "Distribución del ticket de entrada (M0) por año: percentiles y participación por banda de precio.",
        "params": {},
    },
}
NOT_IN_SLICE = ["lag_correlation", "cohort_curves", "mrr_bridge", "movement_transience", "segment_compare", "step_change"]


class AnalysisError(ValueError):
    pass


def _payload(method, variant, valores, formatos, filas, columnas, notas, caveats, n, robust, params, code):
    return {"method": method, "variant": variant, "valores": valores, "formatos": formatos, "filas": filas,
            "columnas": columnas, "notas": notas, "caveats": caveats, "n": n, "robustez": robust,
            "params": params, "code": code}


def run(con, analysis_id: str, params: dict | None = None) -> list[dict]:
    params = dict(params or {})
    if analysis_id in NOT_IN_SLICE:
        raise AnalysisError(f"'{analysis_id}' está en el catálogo de la arquitectura pero no en esta slice. "
                            f"Disponibles: {', '.join(CATALOG)}.")
    if analysis_id not in CATALOG:
        raise AnalysisError(f"Análisis desconocido '{analysis_id}'. Disponibles: {', '.join(CATALOG)}.")
    return {"mix_within_decomposition": mix_within, "vintage_arpa": vintage_arpa,
            "churn_selection": churn_selection, "ticket_distribution": ticket_distribution}[analysis_id](con, params)


# ---------------------------------------------------------------------------- mix vs. dentro
def mix_within(con, p):
    base, comp = str(p.get("base", "2022")), str(p.get("comparacion", "2024"))
    for y in (base, comp):
        if y not in ("2022", "2023", "2024"):
            raise AnalysisError("base y comparacion deben ser '2022', '2023' o '2024'.")
    if base == comp:
        raise AnalysisError("base y comparacion deben ser años distintos.")
    variantes = p.get("variantes") or ["m0", "m0_winsor", "early_run_rate"]
    labels = {"m0": "Ticket de entrada observado (M0) · principal", "m0_winsor": "M0 winsorizado en P99",
              "early_run_rate": "Run-rate temprano (mediana de M0–M2 positivos)"}
    bad = [v for v in variantes if v not in labels]
    if bad:
        raise AnalysisError(f"Variantes inválidas {bad}. Opciones: {list(labels)}.")
    nc = con.execute("SELECT customer_id, industry, year, m0_cop, early_run_rate_cop FROM mart.new_customers "
                     "WHERE clean ORDER BY customer_id").df()
    cap = float(nc.m0_cop.quantile(0.99))
    nc["m0_winsor"] = nc.m0_cop.clip(upper=cap)
    nc = nc.rename(columns={"m0_cop": "m0", "early_run_rate_cop": "early_run_rate"})
    order = list(nc.industry.value_counts().index)
    d0, d1 = nc[nc.year == int(base)], nc[nc.year == int(comp)]
    out = []
    for v in variantes:
        res, det = shapley(d0, d1, v, order)
        boot = bootstrap_decomp(d0, d1, v, order)
        delta = res["delta"]
        val = {"ticket_base": res["A0"], "ticket_comparacion": res["A1"], "cambio": delta,
               "cambio_pct": res["A1"] / res["A0"] - 1, "mix": res["mix"], "dentro": res["within"],
               "participacion_dentro": res["within"] / delta if delta else None,
               "participacion_mix": res["mix"] / delta if delta else None,
               "participacion_dentro_ic90_inf": boot["within_share_ci90"][0],
               "participacion_dentro_ic90_sup": boot["within_share_ci90"][1],
               "dentro_ic90_inf": boot["within_ci90"][0], "dentro_ic90_sup": boot["within_ci90"][1],
               "mix_ic90_inf": boot["mix_ci90"][0], "mix_ic90_sup": boot["mix_ci90"][1],
               "ticket_comparacion_con_mix_base": res["counterfactual_A1_at_base_mix"],
               "altas_base": res["n0"], "altas_comparacion": res["n1"], "tope_winsor": cap}
        fmt = {k: "cop" for k in val}
        fmt.update({"cambio_pct": "pct_signed", "participacion_dentro": "pct0", "participacion_mix": "pct0",
                    "participacion_dentro_ic90_inf": "pct0", "participacion_dentro_ic90_sup": "pct0",
                    "altas_base": "int", "altas_comparacion": "int"})
        filas = []
        for _, r in det.iterrows():
            ind = r["industry"]
            for k, col, f in [("participacion_base", "share0", "pct"), ("participacion_comparacion", "share1", "pct"),
                              ("ticket_base", "mean0", "cop"), ("ticket_comparacion", "mean1", "cop"),
                              ("contribucion_mix", "mix_contribution", "cop"),
                              ("contribucion_dentro", "within_contribution", "cop")]:
                val[f"{k}[{ind}]"] = float(r[col])
                fmt[f"{k}[{ind}]"] = f
            filas.append({"industria": ind, "altas_base": int(r["n0"]), "altas_comparacion": int(r["n1"]),
                          "participacion_base": float(r["share0"]), "participacion_comparacion": float(r["share1"]),
                          "ticket_base": float(r["mean0"]), "ticket_comparacion": float(r["mean1"]),
                          "contribucion_mix": float(r["mix_contribution"]),
                          "contribucion_dentro": float(r["within_contribution"])})
        cols = [{"id": "industria", "nombre": "Industria"}, {"id": "altas_base", "nombre": f"Altas {base}", "formato": "int"},
                {"id": "altas_comparacion", "nombre": f"Altas {comp}", "formato": "int"},
                {"id": "participacion_base", "nombre": f"% {base}", "formato": "pct"},
                {"id": "participacion_comparacion", "nombre": f"% {comp}", "formato": "pct"},
                {"id": "ticket_base", "nombre": f"Ticket {base}", "formato": "cop"},
                {"id": "ticket_comparacion", "nombre": f"Ticket {comp}", "formato": "cop"},
                {"id": "contribucion_mix", "nombre": "Contribución del mix", "formato": "cop"},
                {"id": "contribucion_dentro", "nombre": "Contribución dentro", "formato": "cop"}]
        lo = boot["within_share_ci90"][0]
        notas = ["Dentro de la industria no es lo mismo que precio: agrupa planes, tamaño del cliente, descuentos y "
                 "timing de cobro dentro de cada industria.",
                 "Mix y dentro suman exactamente el cambio (Shapley, sin residuo)."]
        caveats = ["CV-M0-PICOS-2022"] if "2022" in (base, comp) else []
        if v == "m0":
            caveats.append("CV-OUTLIERS")
        out.append(_payload(
            "Shapley (punto medio) de un promedio ponderado + bootstrap " + f"{BOOT_N:,}".replace(",", "."),
            labels[v], val, fmt, filas, cols, notas, caveats, int(res["n0"] + res["n1"]),
            {"bootstrap": BOOT_N, "semilla": SEED, "ic90_participacion_dentro": [lo, boot["within_share_ci90"][1]],
             "dominante_en_ic": bool(lo > 0.5 or boot["within_share_ci90"][1] < 0.5)},
            {"base": base, "comparacion": comp, "variante": v},
            "agent/analytics.py · mix_within() sobre mart.new_customers → finora_eda.shapley() + finora_eda.bootstrap_decomp()"))
    return out


# ---------------------------------------------------------------------------- MRR por cosecha
def vintage_arpa(con, p):
    hasta = p.get("hasta", WINDOW_END)
    desdes = p.get("desde") or ["2022-01", "2022-12"]
    if isinstance(desdes, str):
        desdes = [desdes]
    months = [r[0] for r in con.execute("SELECT DISTINCT month FROM mart.customer_month").fetchall()]
    for m in [hasta, *desdes]:
        if m not in months:
            raise AnalysisError(f"Mes inválido '{m}'. Usa 'AAAA-MM' entre ene-22 y oct-24.")
    vm = con.execute("SELECT month, vintage, active_customers, mrr_cop::DOUBLE AS mrr_cop FROM mart.vintage_month").df()
    out = []
    for desde in desdes:
        if desde >= hasta:
            raise AnalysisError("'desde' debe ser anterior a 'hasta'.")
        g0 = vm[(vm.month == desde) & (vm.active_customers > 0)].set_index("vintage")
        g1 = vm[(vm.month == hasta) & (vm.active_customers > 0)].set_index("vintage")
        groups = sorted(set(g0.index) | set(g1.index), key=_vint_order)
        n0, n1 = g0.active_customers.sum(), g1.active_customers.sum()
        A0, A1 = g0.mrr_cop.sum() / n0, g1.mrr_cop.sum() / n1
        mix = within = 0.0
        filas, val, fmt = [], {}, {}
        for gname in groups:
            s0 = g0.active_customers.get(gname, 0) / n0
            s1 = g1.active_customers.get(gname, 0) / n1
            a1 = g1.mrr_cop.get(gname) / g1.active_customers.get(gname) if gname in g1.index else None
            a0 = g0.mrr_cop.get(gname) / g0.active_customers.get(gname) if gname in g0.index else None
            # convención de entrada/salida: el grupo que no existe en una fecha toma el MRR por cliente de la otra
            a0e = a0 if a0 is not None else a1
            a1e = a1 if a1 is not None else a0
            m_i = (s1 - s0) * (a0e + a1e) / 2
            w_i = (a1e - a0e) * (s0 + s1) / 2
            mix += m_i
            within += w_i
            mrr_share1 = g1.mrr_cop.get(gname, 0) / g1.mrr_cop.sum()
            fila = {"cosecha": gname, "participacion_desde": s0, "participacion_hasta": s1,
                    "mrr_por_cliente_desde": a0, "mrr_por_cliente_hasta": a1, "participacion_mrr_hasta": mrr_share1,
                    "contribucion_composicion": m_i, "contribucion_dentro": w_i}
            filas.append(fila)
            for k, f in [("participacion_desde", "pct"), ("participacion_hasta", "pct"), ("mrr_por_cliente_desde", "cop"),
                         ("mrr_por_cliente_hasta", "cop"), ("participacion_mrr_hasta", "pct"),
                         ("contribucion_composicion", "cop"), ("contribucion_dentro", "cop")]:
                if fila[k] is not None:
                    val[f"{k}[{gname}]"] = float(fila[k])
                    fmt[f"{k}[{gname}]"] = f
        delta = A1 - A0
        assert abs(mix + within - delta) < 1e-6, "la descomposición por cosecha no cuadra"
        recent = [g for g in groups if g in ("Cosecha 2023", "Cosecha 2024")]
        val.update({"mrr_por_cliente_desde": A0, "mrr_por_cliente_hasta": A1, "cambio": delta,
                    "cambio_pct": A1 / A0 - 1, "composicion": mix, "dentro": within,
                    "participacion_composicion": mix / delta, "participacion_dentro": within / delta,
                    "clientes_desde": float(n0), "clientes_hasta": float(n1),
                    "participacion_clientes_cosechas_2023_24": float(sum(g1.active_customers.get(g, 0) for g in recent) / n1),
                    "participacion_mrr_cosechas_2023_24": float(sum(g1.mrr_cop.get(g, 0) for g in recent) / g1.mrr_cop.sum())})
        fmt.update({"mrr_por_cliente_desde": "cop", "mrr_por_cliente_hasta": "cop", "cambio": "cop",
                    "cambio_pct": "pct_signed", "composicion": "cop", "dentro": "cop",
                    "participacion_composicion": "pct0", "participacion_dentro": "pct0",
                    "clientes_desde": "int", "clientes_hasta": "int",
                    "participacion_clientes_cosechas_2023_24": "pct0", "participacion_mrr_cosechas_2023_24": "pct0"})
        cols = [{"id": "cosecha", "nombre": "Cosecha"},
                {"id": "participacion_desde", "nombre": f"% clientes {period_label(desde)}", "formato": "pct"},
                {"id": "participacion_hasta", "nombre": f"% clientes {period_label(hasta)}", "formato": "pct"},
                {"id": "mrr_por_cliente_desde", "nombre": f"MRR / cliente {period_label(desde)}", "formato": "cop"},
                {"id": "mrr_por_cliente_hasta", "nombre": f"MRR / cliente {period_label(hasta)}", "formato": "cop"},
                {"id": "contribucion_composicion", "nombre": "Contribución composición", "formato": "cop"},
                {"id": "contribucion_dentro", "nombre": "Contribución dentro", "formato": "cop"}]
        notas = ["Composición y dentro suman exactamente el cambio. Una cosecha que no existe en la fecha base entra "
                 "completa como composición.",
                 "Cosecha = año del primer pago; la base previa son los clientes activos en ene-22 (alta real desconocida)."]
        out.append(_payload(
            "Descomposición de Shapley (punto medio) del MRR por cliente por cosecha", f"Base {period_label(desde)}",
            val, fmt, filas, cols, notas, ["CV-VENTANA", "CV-AMOUNT-COBRO"], int(n0 + n1),
            {"composicion_domina": bool(mix / delta > 0.8) if delta else None},
            {"desde": desde, "hasta": hasta},
            "agent/analytics.py · vintage_arpa() sobre mart.vintage_month"))
    return out


def _vint_order(g):
    order = ["Base previa (activos en ene-22)", "Altas de feb-22 (marcadas)", "Cosecha 2022 (mar–dic)", "Cosecha 2023", "Cosecha 2024"]
    return order.index(g) if g in order else 99


# ---------------------------------------------------------------------------- ¿se van los de mayor ticket?
def churn_selection(con, p):
    """Ticket de quienes hacen churn contra el de los activos del mismo mes (análisis nuevo, §4).

    Se mide con el monto usual de cada cliente (su monto positivo más frecuente) y no con el último pago,
    porque `amount` se comporta como cobro: un pago acumulado justo antes de salir inflaría la comparación.
    """
    k = int(p.get("persistente_meses", 3))
    if not 1 <= k <= 12:
        raise AnalysisError("persistente_meses debe estar entre 1 y 12.")
    cm = con.execute("SELECT customer_id, month, year, active_customer, paid_mrr_cop::DOUBLE AS mrr, churned_customer, "
                     "-churned_mrr_cop::DOUBLE AS prev_mrr, months_to_return, usual_amount_cop::DOUBLE AS usual "
                     "FROM mart.customer_month").df()
    act = cm[cm.active_customer == 1]
    pool_mean, pool_med = act.groupby("month").usual.mean(), act.groupby("month").usual.median()
    ev = cm[(cm.churned_customer == 1) & (cm.month >= CLEAN_START)].copy()
    ev["prev_month"] = [str(pd.Period(m, freq="M") - 1) for m in ev.month]
    ev["pool_mean"], ev["pool_med"] = ev.prev_month.map(pool_mean), ev.prev_month.map(pool_med)
    last_ok = str(pd.Period(WINDOW_END, freq="M") - k)
    ev["persistente"] = (ev.month <= last_ok) & (ev.months_to_return.isna() | (ev.months_to_return > k))
    ev["ultimo_pago_inflado"] = ev.prev_mrr > 1.5 * ev.usual
    rng = np.random.default_rng(SEED)

    def boot(g, stat):
        x, pm, pd_ = g.usual.to_numpy(), g.pool_mean.to_numpy(), g.pool_med.to_numpy()
        f = (lambda i: x[i].mean() / pm[i].mean()) if stat == "media" else (lambda i: np.median(x[i]) / pd_[i].mean())
        r = f(np.arange(len(x)))
        rs = np.array([f(rng.integers(0, len(x), len(x))) for _ in range(BOOT_N)])
        return float(r), float(np.percentile(rs, 5)), float(np.percentile(rs, 95))

    filas, val, fmt = [], {}, {}
    for label, g in [(str(y), g) for y, g in ev.groupby("year")] + [("total", ev)]:
        rm, rm_lo, rm_hi = boot(g, "media")
        rd, rd_lo, rd_hi = boot(g, "mediana")
        gp = g[g.persistente]
        rp = boot(gp, "media")[0] if len(gp) >= 30 else None
        fila = {"periodo": label, "churns": len(g), "usual_quienes_se_van": g.usual.mean(),
                "usual_activos": g.pool_mean.mean(), "razon_medias": rm, "razon_medias_ic90_inf": rm_lo,
                "razon_medias_ic90_sup": rm_hi, "razon_medianas": rd, "razon_medianas_ic90_inf": rd_lo,
                "razon_medianas_ic90_sup": rd_hi, "churns_persistentes": len(gp), "razon_medias_persistentes": rp,
                "ultimo_pago_inflado": float(g.ultimo_pago_inflado.mean())}
        filas.append(fila)
        for key, f in [("churns", "int"), ("usual_quienes_se_van", "cop"), ("usual_activos", "cop"),
                       ("razon_medias", "num2"), ("razon_medias_ic90_inf", "num2"), ("razon_medias_ic90_sup", "num2"),
                       ("razon_medianas", "num2"), ("razon_medianas_ic90_inf", "num2"), ("razon_medianas_ic90_sup", "num2"),
                       ("churns_persistentes", "int"), ("razon_medias_persistentes", "num2"), ("ultimo_pago_inflado", "pct0")]:
            if fila[key] is not None:
                val[f"{key}[{label}]"] = float(fila[key])
                fmt[f"{key}[{label}]"] = f
    cols = [{"id": "periodo", "nombre": "Año del churn"}, {"id": "churns", "nombre": "Churns", "formato": "int"},
            {"id": "usual_quienes_se_van", "nombre": "Monto usual de quienes se van", "formato": "cop"},
            {"id": "usual_activos", "nombre": "Monto usual de los activos (mes previo)", "formato": "cop"},
            {"id": "razon_medias", "nombre": "Razón de medias", "formato": "num2"},
            {"id": "razon_medias_ic90_inf", "nombre": "IC 90% inf.", "formato": "num2"},
            {"id": "razon_medias_ic90_sup", "nombre": "IC 90% sup.", "formato": "num2"},
            {"id": "razon_medianas", "nombre": "Razón de medianas", "formato": "num2"},
            {"id": "razon_medianas_ic90_inf", "nombre": "IC 90% inf.", "formato": "num2"},
            {"id": "razon_medianas_ic90_sup", "nombre": "IC 90% sup.", "formato": "num2"},
            {"id": "ultimo_pago_inflado", "nombre": "Último pago > 1,5× el usual", "formato": "pct0"}]
    notas = ["Se compara el monto usual (monto positivo más frecuente de cada cliente), no el último pago: el último "
             "pago antes de salir a veces es un cobro acumulado.",
             "Razón > 1: quienes se van pagaban más que el cliente activo del mismo mes; su salida baja el promedio. "
             "Si la razón de medias es > 1 pero la de medianas ≈ 1, la diferencia la hacen pocos clientes grandes.",
             f"'Persistentes' = churns que no vuelven en {k} meses (solo eventos con {k} meses observables).",
             "El churn es observado: incluye pausas y atrasos."]
    return [_payload("Razón de medias y de medianas del monto usual, bootstrap " + f"{BOOT_N:,}".replace(",", ".") + " (IC 90%)",
                     "Churn observado (monto usual)", val, fmt, filas, cols, notas,
                     ["CV-CHURN-PAUSAS", "CV-AMOUNT-COBRO", "CV-OUTLIERS"], int(len(ev)),
                     {"bootstrap": BOOT_N, "semilla": SEED}, {"persistente_meses": k},
                     "agent/analytics.py · churn_selection() sobre mart.customer_month (análisis nuevo de la arquitectura §4)")]


# ---------------------------------------------------------------------------- distribución del ticket
def ticket_distribution(con, p):
    nc = con.execute("SELECT year, m0_cop FROM mart.new_customers WHERE clean").df()
    filas, val, fmt = [], {}, {}
    for y, g in nc.groupby("year"):
        q = g.m0_cop.quantile([0.25, 0.5, 0.75, 0.9])
        bands = pd.cut(g.m0_cop, PRICE_BANDS, right=False, labels=PRICE_BAND_LABELS).value_counts(normalize=True)
        fila = {"año": str(y), "altas": len(g), "promedio": g.m0_cop.mean(), "p25": q[0.25], "mediana": q[0.5],
                "p75": q[0.75], "p90": q[0.9], **{f"banda {b}": float(bands.get(b, 0)) for b in PRICE_BAND_LABELS}}
        filas.append(fila)
        for key in ["altas", "promedio", "p25", "mediana", "p75", "p90"]:
            val[f"{key}[{y}]"] = float(fila[key])
            fmt[f"{key}[{y}]"] = "int" if key == "altas" else "cop"
        for b in PRICE_BAND_LABELS:
            val[f"banda[{b}|{y}]"] = float(bands.get(b, 0))
            fmt[f"banda[{b}|{y}]"] = "pct"
        val[f"bajo_45_mil[{y}]"] = float((g.m0_cop < 45_000).mean())
        fmt[f"bajo_45_mil[{y}]"] = "pct0"
    cols = [{"id": "año", "nombre": "Año de alta"}, {"id": "altas", "nombre": "Altas", "formato": "int"},
            {"id": "promedio", "nombre": "Promedio", "formato": "cop"}, {"id": "p25", "nombre": "P25", "formato": "cop"},
            {"id": "mediana", "nombre": "Mediana", "formato": "cop"}, {"id": "p75", "nombre": "P75", "formato": "cop"},
            {"id": "p90", "nombre": "P90", "formato": "cop"}]
    return [_payload("Percentiles y bandas de precio del primer monto pagado", "Ventana limpia", val, fmt, filas, cols,
                     ["2022 = mar–dic; 2024 = ene–oct.", "Promedio sensible a pocos primeros pagos grandes; mediana no."],
                     ["CV-M0-PICOS-2022", "CV-OUTLIERS"], int(len(nc)), {}, {},
                     "agent/analytics.py · ticket_distribution() sobre mart.new_customers")]
