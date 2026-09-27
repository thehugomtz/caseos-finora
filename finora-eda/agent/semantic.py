"""Capa semántica: compila métricas del catálogo a SQL sobre el mart (nivel 2 de la escalera, §3.3).

El agente elige métrica, grano, periodo, cortes y comparación; el código decide el SQL y aplica las
reglas de cada métrica: ventana limpia para flujos, comparaciones no comparables marcadas y caveats.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import CLEAN_START, WINDOW_END, WINDOW_START
from .render import period_label


@dataclass(frozen=True)
class MetricSpec:
    kind: str          # stock · flow · ratio · distribution · rate
    expr: str
    fmt: str
    label: str


SPECS = {
    "active_customers": MetricSpec("stock", "SUM(active_customer)", "int", "Clientes activos"),
    "total_paid_mrr_cop": MetricSpec("stock", "SUM(paid_mrr_cop)::DOUBLE", "cop", "MRR pagado"),
    "mrr_per_active_customer_cop": MetricSpec(
        "ratio", "SUM(paid_mrr_cop)::DOUBLE / NULLIF(SUM(active_customer), 0)", "cop", "MRR por cliente activo"),
    "vintage_arpa": MetricSpec(
        "ratio", "SUM(paid_mrr_cop)::DOUBLE / NULLIF(SUM(active_customer), 0)", "cop", "MRR por cliente de la cosecha"),
    "new_customers": MetricSpec("flow", "SUM(new_customer)", "int", "Altas"),
    "churned_customers": MetricSpec("flow", "SUM(churned_customer)", "int", "Churn observado"),
    "reactivated_customers": MetricSpec("flow", "SUM(reactivated_customer)", "int", "Reactivaciones"),
    "net_customer_adds": MetricSpec(
        "flow", "SUM(new_customer) + SUM(reactivated_customer) - SUM(churned_customer)", "int", "Altas netas"),
    "new_mrr_cop": MetricSpec("flow", "COALESCE(SUM(new_mrr_cop), 0)::DOUBLE", "cop", "MRR nuevo"),
    "expansion_mrr_cop": MetricSpec("flow", "COALESCE(SUM(expansion_mrr_cop), 0)::DOUBLE", "cop", "MRR de expansión"),
    "reactivation_mrr_cop": MetricSpec(
        "flow", "COALESCE(SUM(reactivation_mrr_cop), 0)::DOUBLE", "cop", "MRR de reactivación"),
    "contraction_mrr_cop": MetricSpec(
        "flow", "COALESCE(SUM(contraction_mrr_cop), 0)::DOUBLE", "cop", "MRR de contracción"),
    "churned_mrr_cop": MetricSpec("flow", "COALESCE(SUM(churned_mrr_cop), 0)::DOUBLE", "cop", "MRR de churn"),
    "net_mrr_change_cop": MetricSpec(
        "flow", "(COALESCE(SUM(new_mrr_cop), 0) + COALESCE(SUM(expansion_mrr_cop), 0) + COALESCE(SUM(reactivation_mrr_cop), 0)"
                " + COALESCE(SUM(contraction_mrr_cop), 0) + COALESCE(SUM(churned_mrr_cop), 0))::DOUBLE", "cop",
        "Cambio neto del MRR"),
    "entry_ticket": MetricSpec("distribution", "paid_mrr_cop::DOUBLE", "cop", "Ticket de entrada (M0)"),
    "logo_churn_rate": MetricSpec("rate", "", "pct", "Churn mensual de logos"),
}

# Métricas del catálogo que existen pero no se compilan en esta versión (se responden con otra tool).
OUT_OF_SCOPE = {
    "cohort_logo_retention": "usa run_analysis (curvas de cohortes: no incluido en esta slice)",
    "cohort_revenue_retention": "usa run_analysis (curvas de cohortes: no incluido en esta slice)",
    "total_sm_spend": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "demand_gen_spend": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "sales_capacity_spend": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "enablement_spend": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "paid_media": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "sm_per_new_customer": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
    "sm_per_new_mrr_mm": "el gasto de S&M se consulta con run_sql sobre mart.sm_monthly (unidad u, nunca COP; techo Direccional)",
}

DIMS = {"industry": "industry", "vintage": "vintage"}
GRAINS = {
    "month": "month",
    "quarter": "substr(month, 1, 4) || ' T' || CAST((CAST(substr(month, 6, 2) AS INTEGER) + 2) // 3 AS VARCHAR)",
    "half": "substr(month, 1, 4) || ' S' || CASE WHEN CAST(substr(month, 6, 2) AS INTEGER) <= 6 THEN '1' ELSE '2' END",
    "year": "substr(month, 1, 4)",
    "total": "'total'",
}
COMPARES = ("none", "yoy", "mom", "index")


class MetricError(ValueError):
    """Error tipado con pista de corrección para el agente."""


def _months_back(ym: str, k: int) -> str:
    p = pd.Period(ym, freq="M") - k
    return str(p)


def _q(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


def compile_and_run(con, metric_id: str, grain: str = "month", period: dict | None = None,
                    filters: dict | None = None, group_by: list | None = None, compare: str = "none",
                    catalog: dict | None = None) -> dict:
    """Devuelve {sql, columnas, filas, valores, formatos, notas, caveats, no_comparable}."""
    if metric_id in OUT_OF_SCOPE:
        raise MetricError(f"La métrica '{metric_id}' existe en el catálogo pero no se compila aquí: {OUT_OF_SCOPE[metric_id]}.")
    if metric_id not in SPECS:
        raise MetricError(f"Métrica desconocida '{metric_id}'. Usa un id del catálogo: {', '.join(sorted(SPECS))}.")
    spec = SPECS[metric_id]
    if grain not in GRAINS:
        raise MetricError(f"Grano inválido '{grain}'. Opciones: {', '.join(GRAINS)}.")
    if compare not in COMPARES:
        raise MetricError(f"Comparación inválida '{compare}'. Opciones: {', '.join(COMPARES)}.")
    if compare == "mom" and grain != "month":
        raise MetricError("La comparación 'mom' solo aplica con grano 'month'.")
    group_by = list(group_by or [])
    if metric_id == "vintage_arpa" and "vintage" not in group_by:
        group_by.append("vintage")
    for d in group_by:
        if d not in DIMS:
            raise MetricError(f"Dimensión inválida '{d}'. Opciones: {', '.join(DIMS)}.")
    filters = dict(filters or {})
    period = dict(period or {})
    p_from = period.get("from", WINDOW_START)
    p_to = period.get("to", WINDOW_END)
    for v in (p_from, p_to):
        if not (isinstance(v, str) and len(v) == 7 and v[4] == "-"):
            raise MetricError(f"Periodo inválido '{v}'. Usa 'AAAA-MM' entre {WINDOW_START} y {WINDOW_END}.")
    if p_from > p_to or p_from < WINDOW_START or p_to > WINDOW_END:
        raise MetricError(f"Periodo fuera de la ventana: {p_from} → {p_to}. La ventana es {WINDOW_START} → {WINDOW_END}.")

    notas, caveats, no_comparable = [], [], []
    cat = (catalog or {}).get(metric_id, {})
    caveats.extend(cat.get("caveats", []))
    is_flow = spec.kind in ("flow", "distribution", "rate")
    eff_from = p_from
    if is_flow and p_from < CLEAN_START:
        eff_from = CLEAN_START
        notas.append("Los flujos solo se miden en la ventana limpia: el periodo empieza en mar-22 "
                     "(ene-22 censurado; feb-22 con arrastre).")
        if "CV-VENTANA" not in caveats:
            caveats.append("CV-VENTANA")
    if metric_id == "entry_ticket" and eff_from <= "2022-12":
        if "CV-M0-PICOS-2022" not in caveats:
            caveats.append("CV-M0-PICOS-2022")
        notas.append("El ticket de entrada de 2022 incluye pagos iniciales grandes: compáralo con su precaución.")

    where = []
    for d, vals in filters.items():
        if d not in DIMS:
            raise MetricError(f"Filtro inválido '{d}'. Opciones: {', '.join(DIMS)}.")
        vals = vals if isinstance(vals, list) else [vals]
        valid = {r[0] for r in con.execute(f"SELECT DISTINCT {DIMS[d]} FROM mart.customer_month").fetchall()}
        bad = [v for v in vals if v not in valid]
        if bad:
            raise MetricError(f"Valores inválidos para {d}: {bad}. Válidos: {sorted(valid)}.")
        where.append(f"{DIMS[d]} IN ({', '.join(_q(v) for v in vals)})")
    fwhere = (" AND " + " AND ".join(where)) if where else ""
    dims_sel = "".join(f", {DIMS[d]} AS {d}" for d in group_by)
    dims_cols = "".join(f", {d}" for d in group_by)
    pexpr = GRAINS[grain]
    # para YoY y variaciones se necesitan periodos previos: se consulta desde el inicio de la ventana
    q_from = WINDOW_START if compare in ("yoy", "mom") else eff_from
    if is_flow and compare in ("yoy", "mom"):
        q_from = CLEAN_START

    if spec.kind in ("stock", "ratio"):
        sql = (f"WITH m AS (SELECT month, {pexpr} AS periodo{dims_sel}, {spec.expr} AS valor "
               f"FROM mart.customer_month WHERE month BETWEEN {_q(q_from)} AND {_q(p_to)}{fwhere} "
               f"GROUP BY ALL) "
               f"SELECT periodo{dims_cols}, arg_max(valor, month) AS valor, max(month) AS mes_cierre, "
               f"COUNT(*) AS meses FROM m GROUP BY ALL ORDER BY periodo{dims_cols}")
        value_cols = [("valor", spec.label, spec.fmt)]
        if grain != "month":
            notas.append("Es un stock: cada periodo muestra el valor de su último mes (cierre).")
    elif spec.kind == "flow":
        sql = (f"SELECT {pexpr} AS periodo{dims_sel}, {spec.expr} AS valor, COUNT(DISTINCT month) AS meses, "
               f"({spec.expr}) / COUNT(DISTINCT month) AS promedio_mensual "
               f"FROM mart.customer_month WHERE month BETWEEN {_q(q_from)} AND {_q(p_to)}{fwhere} "
               f"GROUP BY ALL ORDER BY periodo{dims_cols}")
        value_cols = [("valor", spec.label, spec.fmt), ("promedio_mensual", spec.label + " por mes", spec.fmt)]
    elif spec.kind == "distribution":
        sql = (f"SELECT {pexpr} AS periodo{dims_sel}, COUNT(*) AS altas, AVG(m0) AS valor, MEDIAN(m0) AS mediana, "
               f"quantile_cont(m0, 0.25) AS p25, quantile_cont(m0, 0.75) AS p75, quantile_cont(m0, 0.9) AS p90 "
               f"FROM (SELECT month, industry, vintage, {spec.expr} AS m0 FROM mart.customer_month "
               f"WHERE new_customer = 1) WHERE month BETWEEN {_q(q_from)} AND {_q(p_to)}{fwhere} "
               f"GROUP BY ALL ORDER BY periodo{dims_cols}")
        value_cols = [("valor", "Ticket de entrada promedio", "cop"), ("mediana", "Mediana", "cop"),
                      ("p25", "P25", "cop"), ("p75", "P75", "cop"), ("p90", "P90", "cop"), ("altas", "Altas", "int")]
    else:  # rate: churn(t) ÷ activos(t−1), agregado como Σ churn ÷ Σ activos del mes anterior
        part = ", ".join(DIMS[d] for d in group_by) or "1"
        sql = (f"WITH m AS (SELECT month{dims_sel}, SUM(churned_customer) AS churn, SUM(active_customer) AS activos "
               f"FROM mart.customer_month WHERE TRUE{fwhere} GROUP BY ALL), "
               f"l AS (SELECT *, LAG(activos) OVER (PARTITION BY {part} ORDER BY month) AS activos_prev FROM m) "
               f"SELECT {pexpr} AS periodo{dims_cols}, SUM(churn)::DOUBLE / NULLIF(SUM(activos_prev), 0) AS valor, "
               f"SUM(churn) AS churn, SUM(activos_prev) AS activos_mes_anterior, COUNT(*) AS meses FROM l "
               f"WHERE month BETWEEN {_q(q_from)} AND {_q(p_to)} GROUP BY ALL ORDER BY periodo{dims_cols}")
        value_cols = [("valor", spec.label, "pct"), ("churn", "Churn observado", "int")]
        if "CV-CHURN-PAUSAS" not in caveats:
            caveats.append("CV-CHURN-PAUSAS")

    df = con.execute(sql).df()
    df["periodo"] = df["periodo"].astype(str)
    key_of = lambda r: str(r["periodo"]) + "".join("|" + str(r[d]) for d in group_by)  # noqa: E731

    # comparaciones
    extra_cols = []
    if compare in ("yoy", "mom"):
        lag = {"month": 12, "quarter": 4, "half": 2, "year": 1}[grain] if compare == "yoy" else 1
        if grain == "total":
            raise MetricError("La comparación YoY no aplica con grano 'total'.")
        # etiqueta del periodo base: mismo periodo del año anterior (o mes anterior en 'mom')
        def base_label(p: str) -> str | None:
            if grain == "month":
                return _months_back(p, lag)
            if grain == "year":
                return str(int(p) - 1)
            y, part = p.split(" ")
            return f"{int(y) - 1} {part}"
        vals = {key_of(r): r for _, r in df.iterrows()}
        base_vals, variaciones = [], []
        use = "promedio_mensual" if spec.kind == "flow" and grain != "month" else "valor"
        for _, r in df.iterrows():
            b = base_label(r["periodo"])
            bk = b + "".join("|" + str(r[d]) for d in group_by) if b else None
            br = vals.get(bk) if bk else None
            if br is None:
                base_vals.append(None)
                variaciones.append(None)
                continue
            bv, cv_ = br[use], r[use]
            base_vals.append(bv)
            variaciones.append(None if not bv else cv_ / bv - 1)
            if spec.kind == "flow" and grain != "month" and br["meses"] != r["meses"]:
                notas.append(f"{period_label(r['periodo'])} vs {period_label(b)}: distinta cantidad de meses; "
                             "la variación compara el promedio mensual.")
        df["valor_base"] = base_vals
        df["variacion"] = variaciones
        extra_cols = [("valor_base", "Valor base", spec.fmt), ("variacion", "Variación", "pct_signed")]
        # la consulta se amplió para tener bases: se recorta al periodo pedido
        df = df[df["periodo"] >= _period_of(eff_from, grain)].reset_index(drop=True)
        if is_flow and grain == "month":
            for _, r in df.iterrows():
                b = _months_back(r["periodo"], lag)
                if b < CLEAN_START:
                    k = key_of(r)
                    if k not in no_comparable:
                        no_comparable.append(k)
        if no_comparable:
            notas.append("Hay comparaciones no comparables: su periodo base cae antes de la ventana limpia "
                         "(por ejemplo, feb-22 está inflado por el arrastre). No se pueden usar en afirmaciones.")
    elif compare == "index":
        base_rows = {}
        idx = []
        for _, r in df.iterrows():
            gk = "".join("|" + str(r[d]) for d in group_by)
            if gk not in base_rows:
                base_rows[gk] = r["valor"]
            b = base_rows[gk]
            idx.append(None if not b else 100 * r["valor"] / b)
        df["indice"] = idx
        extra_cols = [("indice", "Índice (primer periodo = 100)", "idx")]

    if len(df) > 400:
        raise MetricError(f"La consulta devuelve {len(df)} filas; usa un grano más grueso o menos cortes.")

    columnas = [{"id": "periodo", "nombre": "Periodo"}] + [{"id": d, "nombre": d} for d in group_by]
    columnas += [{"id": c, "nombre": n, "formato": f} for c, n, f in value_cols + extra_cols]
    valores, formatos, filas = {}, {}, []
    for _, r in df.iterrows():
        k = key_of(r)
        fila = {"periodo": period_label(r["periodo"]), **{d: r[d] for d in group_by}}
        for c, _n, f in value_cols + extra_cols:
            v = r.get(c)
            v = None if v is None or pd.isna(v) else float(v)
            fila[c] = v
            if v is not None:
                valores[f"{c}[{k}]"] = v
                formatos[f"{c}[{k}]"] = f
        if "meses" in df.columns:
            fila["meses"] = int(r["meses"])
        fila["_clave"] = k
        filas.append(fila)
    return {"sql": sql, "columnas": columnas, "filas": filas, "valores": valores, "formatos": formatos,
            "notas": list(dict.fromkeys(notas)), "caveats": caveats, "no_comparable": no_comparable,
            "metric": metric_id, "label": spec.label, "kind": spec.kind}


def _period_of(ym: str, grain: str) -> str:
    y, m = ym[:4], int(ym[5:7])
    return {"month": ym, "quarter": f"{y} T{(m + 2) // 3}", "half": f"{y} S{1 if m <= 6 else 2}",
            "year": y, "total": "total"}[grain]
