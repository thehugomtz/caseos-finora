#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finora · Phase 1 Exploratory Data Analysis pipeline
===================================================
Understand first. Explain later. Decide last.

Everything in the HTML workspace, the CSV outputs and the notes is recalculated
here, directly from the three raw CSV files. No number is typed by hand.

Reproduce
---------
    python3 finora_eda.py                      # reads ./data/raw, writes next to this file
    python3 finora_eda.py --raw-dir <folder>   # alternative input folder

Inputs (unaltered copies of the files shared by Finora)
    Transactions.csv   ID, month, amount          -> customer x month snapshot
    Industry.csv       ID ("Cliente N"), Industria
    S&M_spend.csv      Month + 7 spend components  ("$1.040" strings)

Outputs
    finora_analytical_dataset.csv   customer-month analytical table
    finora_monthly_metrics.csv      company-level monthly metrics, S&M and efficiency
    finora_eda.html                 self-contained exploration workspace
    finora_eda_notes.md             definitions, transformations, assumptions, anomalies,
                                    questions and limitations
    supporting/*.csv                industry, cohort, correlation, decomposition, audit tables

Requirements: Python 3.10+, pandas, numpy, scipy.

Three layers are kept apart on purpose:
    observed    -> `observed_amount` exactly as delivered
    derived     -> `paid_mrr_cop` = observed_amount x 10,000 and the movement flags
    interpreted -> only in the notes/HTML, always labelled as hypothesis
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
from datetime import datetime
from functools import reduce
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------------
# Constants and explicit assumptions
# ----------------------------------------------------------------------------------
SCALE_TO_COP = 10_000        # stated by Finora: amount x 10,000 = COP
MICRO = 1_000_000            # amounts carry <= 6 decimals -> exact integer micro-units
TOL_MULT = 0.005             # 0.5 % tolerance for "k x usual amount" payment signatures
BOOT_N = 2000                # bootstrap resamples for the mix/within decomposition
SEED = 20241031
SPEND_UNIT = "u"             # S&M unit is undocumented: values kept as reported ("$" units)

SM_COMPONENTS = ["PaidMedia", "Travel", "PublicidadNoWeb", "Freelance",
                 "SoftwareTools", "Team", "PayrollExpenses"]
SM_GROUPS = {
    "demand_gen_spend": ["PaidMedia", "PublicidadNoWeb"],
    "sales_capacity_spend": ["Team", "PayrollExpenses", "Travel"],
    "enablement_spend": ["SoftwareTools", "Freelance"],
}
SM_SNAKE = {"PaidMedia": "paid_media", "Travel": "travel", "PublicidadNoWeb": "publicidad_no_web",
            "Freelance": "freelance", "SoftwareTools": "software_tools", "Team": "team",
            "PayrollExpenses": "payroll_expenses"}

BRAIN = HERE / "brain"
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MINUS = "−"


# ----------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------
def ascii_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def month_label(p: pd.Period) -> str:
    """Etiqueta de mes en español: ene-22."""
    p = pd.Period(p, freq="M")
    return f"{MESES[p.month - 1]}-{p.strftime('%y')}"


def half_label(p: pd.Period) -> str:
    """Semestre: 2022 S1."""
    return f"{p.year} S{1 if p.month <= 6 else 2}"


def quarter_label(p: pd.Period) -> str:
    """Trimestre: 2022 T1."""
    return f"{p.year} T{p.quarter}"


def safe_div(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    out = np.full(np.broadcast(a, b).shape, np.nan)
    np.divide(a, b, out=out, where=(b != 0) & ~np.isnan(b))
    return out


def jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [jsonable(v) for v in obj.tolist()]
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return None if not np.isfinite(obj) else float(round(float(obj), 6))
    if isinstance(obj, pd.Period):
        return str(obj)
    if obj is pd.NA or obj is None:
        return None
    return obj


def tidy(df: pd.DataFrame) -> pd.DataFrame:
    """Round floats for CSV output: COP amounts to cents, everything else to 6 decimals."""
    out = df.copy()
    for c in out.columns:
        if pd.api.types.is_float_dtype(out[c]):
            cop = c.endswith("_cop") or "_cop_" in c or c in ("previous_month_mrr", "mrr_change", "paid_mrr_cop")
            out[c] = out[c].round(2 if cop else 6)
    return out


# ---- formatos es-CO: punto de miles, coma decimal, signo menos tipográfico
def _n(x, d=0) -> str:
    s = f"{abs(x):,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return (MINUS if x < 0 and float(s.replace(".", "").replace(",", ".")) != 0 else "") + s


def fmt_int(x) -> str:
    return _n(round(x), 0)


def fmt_num(x, d=1) -> str:
    return _n(x, d)


def fmt_pct(x, d=1) -> str:
    return _n(x * 100, d) + "%"


def fmt_pct_signed(x, d=0) -> str:
    return ("+" if x >= 0 else "") + fmt_pct(x, d)


def fmt_cop(x, d=1) -> str:
    """Montos en texto con palabras (sin K/M ambiguas): COP 97,0 millones · COP 57,8 mil."""
    a = abs(x)
    sign = MINUS if x < 0 else ""
    if a >= 1e9:
        return f"{sign}COP {_n(a / 1e9, d)} mil millones"
    if a >= 1e6:
        return f"{sign}COP {_n(a / 1e6, d)} millones"
    if a >= 1e3:
        return f"{sign}COP {_n(a / 1e3, d)} mil"
    return f"{sign}COP {_n(a, 0)}"


def fmt_x(x, d=1) -> str:
    return _n(x, d) + "×"


def fmt_u(x, d=2) -> str:
    return _n(x, d) + " u"


def fmt_r(x, d=2) -> str:
    return ("+" if x >= 0 else MINUS) + _n(abs(x), d)


# ----------------------------------------------------------------------------------
# 1 · Load raw files (as text) and audit them
# ----------------------------------------------------------------------------------
def read_raw(raw_dir: Path) -> dict:
    files = {"transactions": "Transactions.csv", "industry": "Industry.csv", "sm": "S&M_spend.csv"}
    raw = {}
    for key, name in files.items():
        path = raw_dir / name
        b = path.read_bytes()
        raw[key] = {
            "file": name,
            "sha256": hashlib.sha256(b).hexdigest(),
            "bytes": len(b),
            "utf8_bom": b.startswith(b"\xef\xbb\xbf"),
            "ends_with_newline": b.endswith(b"\n"),
            "df": pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig"),
        }
    return raw


def audit_industry(r: dict):
    df = r["df"].copy()
    stripped = df.apply(lambda s: s.str.strip())
    blank = (stripped == "").all(axis=1)
    pattern_ok = df["ID"].str.fullmatch(r"Cliente \d+")
    clean = df[~blank].copy()
    clean["customer_id"] = clean["ID"].str.extract(r"^Cliente (\d+)$")[0].astype(int)
    clean["industry"] = clean["Industria"].str.strip()
    norm = clean["industry"].map(ascii_key)
    variants = (clean.groupby(norm)["industry"].nunique() > 1).sum()
    ids = clean["customer_id"]
    counts = clean["industry"].value_counts()
    audit = {
        "file": r["file"], "sha256": r["sha256"], "bytes": r["bytes"], "utf8_bom": r["utf8_bom"],
        "columns": list(df.columns), "rows_read": len(df), "blank_rows": int(blank.sum()),
        "blank_row_positions": [int(i) + 2 for i in np.where(blank)[0]],   # 1-based incl. header
        "rows_valid": int(len(clean)),
        "id_pattern_violations_non_blank": int((~pattern_ok & ~blank).sum()),
        "duplicate_ids": int(ids.duplicated().sum()),
        "id_min": int(ids.min()), "id_max": int(ids.max()), "unique_ids": int(ids.nunique()),
        "ids_contiguous_1_to_n": bool(ids.min() == 1 and ids.max() == len(ids) and ids.nunique() == len(ids)),
        "missing_industry_non_blank": int((clean["industry"] == "").sum()),
        "whitespace_issues": int(((df["ID"] != df["ID"].str.strip()) | (df["Industria"] != df["Industria"].str.strip())).sum()),
        "case_or_accent_variants": int(variants),
        "industries": {k: int(v) for k, v in counts.items()},
        "n_industries": int(counts.size),
        "dtypes_raw": {c: "text" for c in df.columns},
        "dtypes_parsed": {"customer_id": "int64", "industry": "category (text)"},
    }
    return clean[["customer_id", "industry"]].sort_values("customer_id").reset_index(drop=True), audit


def audit_transactions(r: dict):
    df = r["df"].copy()
    fmt_mask = df["month"].str.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}")
    t = pd.DataFrame({
        "customer_id": pd.to_numeric(df["ID"], errors="coerce"),
        "date": pd.to_datetime(df["month"], format="%m/%d/%Y", errors="coerce"),
        "amount": pd.to_numeric(df["amount"], errors="coerce"),
    })
    decimals = df["amount"].str.split(".").str[1].fillna("").str.len()
    t["month"] = t["date"].dt.to_period("M")
    pos = t.loc[t.amount > 0, "amount"]
    q1, q3 = pos.quantile([0.25, 0.75])
    iqr_fence = q3 + 3 * (q3 - q1)
    per_id = t.groupby("customer_id").size()
    audit = {
        "file": r["file"], "sha256": r["sha256"], "bytes": r["bytes"], "utf8_bom": r["utf8_bom"],
        "columns": list(df.columns), "rows": len(df),
        "unparseable_id": int(t.customer_id.isna().sum()),
        "unparseable_date": int(t.date.isna().sum()),
        "unparseable_amount": int(t.amount.isna().sum()),
        "empty_strings": {c: int((df[c] == "").sum()) for c in df.columns},
        "date_format": "M/D/AAAA (último día del mes; mes con 1 o 2 dígitos)",
        "date_format_violations": int((~fmt_mask).sum()),
        "all_dates_month_end": bool((t.date == t.date + pd.offsets.MonthEnd(0)).all()),
        "customers": int(t.customer_id.nunique()),
        "months": int(t.month.nunique()),
        "first_month": str(t.month.min()), "last_month": str(t.month.max()),
        "rows_per_customer": {str(k): int(v) for k, v in per_id.value_counts().items()},
        "balanced_panel": bool(len(df) == t.customer_id.nunique() * t.month.nunique() and per_id.nunique() == 1),
        "duplicate_customer_month": int(t.duplicated(["customer_id", "month"]).sum()),
        "duplicate_full_rows": int(df.duplicated().sum()),
        "negative_amounts": int((t.amount < 0).sum()),
        "zero_amount_rows": int((t.amount == 0).sum()),
        "positive_amount_rows": int((t.amount > 0).sum()),
        "zero_share": float((t.amount == 0).mean()),
        "amount_min_positive": float(pos.min()), "amount_max": float(pos.max()),
        "amount_p50_positive": float(pos.median()), "amount_p99_positive": float(pos.quantile(0.99)),
        "amount_p999_positive": float(pos.quantile(0.999)),
        "iqr_fence_q3_plus_3iqr": float(iqr_fence),
        "rows_above_iqr_fence": int((pos > iqr_fence).sum()),
        "customers_above_iqr_fence": int(t.loc[t.amount > iqr_fence, "customer_id"].nunique()),
        "decimal_places": {str(k): int(v) for k, v in decimals.value_counts().sort_index().items()},
        "dtypes_raw": {c: "text" for c in df.columns},
        "dtypes_parsed": {"customer_id": "int64", "month": "period[M]", "amount": "float64 (exact at 1e-6)"},
    }
    return t, audit


def parse_money(s: pd.Series) -> pd.Series:
    """'$1.040' -> 1.040 ; '-$0.016' -> -0.016 (dot is the decimal separator: '$0.120')."""
    txt = s.str.strip()
    ok = txt.str.fullmatch(r"-?\$\d+\.\d+")
    if not ok.all():
        raise ValueError(f"Unexpected money format: {txt[~ok].tolist()}")
    return txt.str.replace("$", "", regex=False).astype(float)


def audit_sm(r: dict):
    df = r["df"].copy()
    sm = pd.DataFrame({"month": pd.PeriodIndex(df["Month"], freq="M")})
    for c in SM_COMPONENTS:
        sm[c] = parse_money(df[c]).values
    total = sm[SM_COMPONENTS].sum(axis=1)
    team_share = sm["Team"] / total
    team_fixed = np.isclose(team_share, 0.12, atol=5e-4)
    # months where each component is (close to) a whole-percent share of the total
    shares = sm[SM_COMPONENTS].div(total, axis=0) * 100
    whole_pct = (np.abs(shares - shares.round()) < 0.05).all(axis=1)
    first_team_break = sm.loc[~team_fixed, "month"].min()
    comp = {}
    for c in SM_COMPONENTS:
        v = sm[c]
        comp[c] = {
            "min": float(v.min()), "max": float(v.max()), "mean": float(v.mean()),
            "zeros": int((v == 0).sum()), "negatives": int((v < 0).sum()),
            "negative_months": [str(m) for m in sm.loc[v < 0, "month"]],
            "zero_months": [str(m) for m in sm.loc[v == 0, "month"]],
        }
    audit = {
        "file": r["file"], "sha256": r["sha256"], "bytes": r["bytes"], "utf8_bom": r["utf8_bom"],
        "columns": list(df.columns), "rows": len(df), "months": int(sm.month.nunique()),
        "first_month": str(sm.month.min()), "last_month": str(sm.month.max()),
        "duplicate_months": int(sm.month.duplicated().sum()),
        "missing_values": int((df == "").sum().sum()),
        "value_format": "texto con prefijo '$', punto decimal y 3 decimales; negativos como '-$0.016'",
        "unit": "no documentada (sin factor de escala; no convertible a COP)",
        "components": comp,
        "team_share_fixed_12pct_months": int(team_fixed.sum()),
        "team_share_fixed_until": str(sm.loc[team_fixed, "month"].max()),
        "team_share_first_break": str(first_team_break),
        "whole_percent_share_months": int(whole_pct.sum()),
        "dtypes_raw": {c: "text" for c in df.columns},
        "dtypes_parsed": {"month": "period[M]", **{c: "float64" for c in SM_COMPONENTS}},
    }
    return sm, team_share, audit


# ----------------------------------------------------------------------------------
# 2 · Customer-month analytical table
# ----------------------------------------------------------------------------------
def build_customer_month(tx: pd.DataFrame, industry: pd.DataFrame):
    wide = tx.pivot(index="customer_id", columns="month", values="amount").sort_index()
    assert not wide.isna().any().any(), "panel is not complete"
    months = list(wide.columns)
    ids = wide.index.to_numpy()
    n, T = wide.shape

    A = np.rint(wide.to_numpy() * MICRO).astype(np.int64)          # exact micro-units
    P = np.zeros_like(A)
    P[:, 1:] = A[:, :-1]
    has_prev = np.zeros((n, T), dtype=bool)
    has_prev[:, 1:] = True
    pos = A > 0
    ever_before = np.zeros((n, T), dtype=bool)
    ever_before[:, 1:] = np.maximum.accumulate(pos, axis=1)[:, :-1]
    first_idx = pos.argmax(axis=1)
    assert pos.any(axis=1).all(), "some customer never has a positive amount"

    new = has_prev & pos & ~ever_before
    react = has_prev & pos & (P == 0) & ever_before
    churn = has_prev & ~pos & (P > 0)
    expand = has_prev & pos & (P > 0) & (A > P)
    contract = has_prev & pos & (P > 0) & (A < P)
    flat = has_prev & pos & (P > 0) & (A == P)

    # movement values in COP (1 micro-unit = 1e-6 amount = 0.01 COP)
    to_cop = SCALE_TO_COP / MICRO
    cur_cop = A * to_cop
    prev_cop = P * to_cop
    new_mrr = np.where(new, cur_cop, 0.0)
    react_mrr = np.where(react, cur_cop, 0.0)
    exp_mrr = np.where(expand, cur_cop - prev_cop, 0.0)
    con_mrr = np.where(contract, cur_cop - prev_cop, 0.0)        # negative
    churn_mrr = np.where(churn, -prev_cop, 0.0)                  # negative
    change = cur_cop - prev_cop
    comp_sum = new_mrr + react_mrr + exp_mrr + con_mrr + churn_mrr
    assert np.allclose(comp_sum[:, 1:], change[:, 1:], atol=1e-6), "row-level bridge does not close"

    # next positive month (for time-to-return of churn events)
    next_pos = np.full((n, T), -1, dtype=int)
    for t in range(T - 2, -1, -1):
        next_pos[:, t] = np.where(pos[:, t + 1], t + 1, next_pos[:, t + 1])
    tt = np.tile(np.arange(T), (n, 1))
    months_to_return = np.where(churn & (next_pos >= 0), next_pos - tt, np.nan)
    nxt = np.zeros_like(A)
    nxt[:, :-1] = A[:, 1:]
    has_next = tt < T - 1
    returned_next = np.where(churn & has_next, np.pad(pos[:, 1:], ((0, 0), (0, 1))).astype(float), np.nan)
    reverts = np.where((expand | contract) & has_next, (nxt == P).astype(float), np.nan)
    same_amount_return = np.where(churn & has_next, ((nxt == P) & (nxt > 0)).astype(float), np.nan)

    # usual (modal) amount per customer and multi-month payment signature
    usual = np.zeros(n, dtype=np.int64)
    usual_count = np.zeros(n, dtype=int)
    for i in range(n):
        vals = A[i][A[i] > 0]
        u, c = np.unique(vals, return_counts=True)
        j = np.lexsort((u, -c))[0]           # most frequent; ties -> smallest amount
        usual[i], usual_count[i] = u[j], c[j]
    ratio_usual = np.where(pos, A / usual[:, None], np.nan)
    k_int = np.rint(ratio_usual)
    signature = np.where(pos & (usual_count[:, None] >= 3) & (k_int >= 2) & (k_int <= 12)
                         & (np.abs(ratio_usual - k_int) <= TOL_MULT * k_int), k_int, 0).astype(int)

    tenure = np.where(tt >= first_idx[:, None], tt - first_idx[:, None], np.nan)
    ind_map = industry.set_index("customer_id")["industry"]
    ind_arr = ind_map.reindex(ids).to_numpy()
    assert not pd.isna(ind_arr).any(), "customer without industry"

    first_month = np.array([str(months[i]) for i in first_idx])
    cohort_flag = np.where(first_idx == 0, "left_censored",
                           np.where(first_idx == 1, "suspected_spillover", "clean"))

    movement = np.full((n, T), "", dtype=object)
    movement[:, 0] = np.where(pos[:, 0], "window_start_active", "window_start_inactive")
    movement[new] = "new"
    movement[react] = "reactivation"
    movement[churn] = "churn"
    movement[expand] = "expansion"
    movement[contract] = "contraction"
    movement[flat] = "flat"
    rest = has_prev & ~pos & (P == 0)
    movement[rest & ~ever_before] = "not_yet_active"
    movement[rest & ever_before] = "inactive_after_churn"
    assert (movement != "").all()

    ym = np.array([str(m) for m in months])
    df = pd.DataFrame({
        "customer_id": np.repeat(ids, T),
        "industry": np.repeat(ind_arr, T),
        "month": np.tile(ym, n),
        "month_index": np.tile(np.arange(T), n),
        "observed_amount": (A / MICRO).ravel(),
        "paid_mrr_cop": cur_cop.ravel(),
        "active_customer": pos.ravel().astype(int),
        "previous_month_mrr": np.where(has_prev, prev_cop, np.nan).ravel(),
        "mrr_change": np.where(has_prev, change, np.nan).ravel(),
        "first_positive_month": np.repeat(first_month, T),
        "cohort_month": np.repeat(first_month, T),
        "cohort_flag": np.repeat(cohort_flag, T),
        "tenure_month": tenure.ravel(),
        "movement_type": movement.ravel(),
        "new_customer": new.ravel().astype(int),
        "churned_customer": churn.ravel().astype(int),
        "reactivated_customer": react.ravel().astype(int),
        "expanded_customer": expand.ravel().astype(int),
        "contracted_customer": contract.ravel().astype(int),
        "flat_customer": flat.ravel().astype(int),
        "new_mrr_cop": new_mrr.ravel(),
        "expansion_mrr_cop": exp_mrr.ravel(),
        "reactivation_mrr_cop": react_mrr.ravel(),
        "contraction_mrr_cop": con_mrr.ravel(),
        "churned_mrr_cop": churn_mrr.ravel(),
        "months_to_return": months_to_return.ravel(),
        "returned_next_month": returned_next.ravel(),
        "returned_same_amount_next_month": same_amount_return.ravel(),
        "reverts_next_month": reverts.ravel(),
        "usual_amount_cop": np.repeat(usual * to_cop, T),
        "amount_vs_usual_ratio": ratio_usual.ravel(),
        "multi_month_payment_signature": signature.ravel(),
    })
    df["tenure_month"] = df["tenure_month"].astype("Int64")
    df["months_to_return"] = df["months_to_return"].astype("Int64")
    for c in ["returned_next_month", "returned_same_amount_next_month", "reverts_next_month"]:
        df[c] = df[c].astype("Int64")

    arrays = dict(A=A, P=P, pos=pos, new=new, react=react, churn=churn, expand=expand,
                  contract=contract, flat=flat, ever_before=ever_before, first_idx=first_idx,
                  new_mrr=new_mrr, react_mrr=react_mrr, exp_mrr=exp_mrr, con_mrr=con_mrr,
                  churn_mrr=churn_mrr, cur_cop=cur_cop, months_to_return=months_to_return,
                  returned_next=returned_next, reverts=reverts, signature=signature,
                  same_amount_return=same_amount_return, usual=usual, usual_count=usual_count,
                  ind=ind_arr, ids=ids, months=months, tenure=tenure)
    return df, arrays


# ----------------------------------------------------------------------------------
# 3 · Monthly metrics (company level)
# ----------------------------------------------------------------------------------
def build_monthly(ar: dict, sm: pd.DataFrame, clean_start: int):
    months = ar["months"]
    T = len(months)
    pos, new, react, churn = ar["pos"], ar["new"], ar["react"], ar["churn"]
    cur = ar["cur_cop"]
    m = pd.DataFrame({"month": [str(x) for x in months], "month_label": [month_label(x) for x in months],
                      "month_index": np.arange(T)})
    m["window_flag"] = np.where(m.month_index == 0, "left_censored_start",
                                np.where(m.month_index < clean_start, "suspected_spillover", "clean"))
    m["active_customers"] = pos.sum(0)
    m["new_customers"] = new.sum(0)
    m["churned_customers"] = churn.sum(0)
    m["reactivated_customers"] = react.sum(0)
    m["expanded_customers"] = ar["expand"].sum(0)
    m["contracted_customers"] = ar["contract"].sum(0)
    m["flat_customers"] = ar["flat"].sum(0)
    m["net_customer_adds"] = m.new_customers + m.reactivated_customers - m.churned_customers
    m["delta_active_customers"] = m.active_customers.diff()
    m["customer_bridge_diff"] = m.delta_active_customers - m.net_customer_adds
    dormant = ar["ever_before"] & ~np.pad(pos, ((0, 0), (1, 0)))[:, :T]   # inactive at t-1, active before
    dormant[:, 0] = False
    m["dormant_pool_prev"] = dormant.sum(0)

    m["total_paid_mrr_cop"] = cur.sum(0)
    m["new_mrr_cop"] = ar["new_mrr"].sum(0)
    m["expansion_mrr_cop"] = ar["exp_mrr"].sum(0)
    m["reactivation_mrr_cop"] = ar["react_mrr"].sum(0)
    m["contraction_mrr_cop"] = ar["con_mrr"].sum(0)
    m["churned_mrr_cop"] = ar["churn_mrr"].sum(0)
    comps = ["new_mrr_cop", "expansion_mrr_cop", "reactivation_mrr_cop", "contraction_mrr_cop", "churned_mrr_cop"]
    m["net_mrr_change_cop"] = m[comps].sum(axis=1)
    m["delta_mrr_cop"] = m.total_paid_mrr_cop.diff()
    m["mrr_bridge_diff_cop"] = m.delta_mrr_cop - m.net_mrr_change_cop
    m.loc[0, comps + ["net_mrr_change_cop", "net_customer_adds", "new_customers", "churned_customers",
                      "reactivated_customers", "expanded_customers", "contracted_customers",
                      "flat_customers"]] = np.nan

    m["mrr_per_active_customer_cop"] = safe_div(m.total_paid_mrr_cop, m.active_customers)
    m["new_mrr_per_new_customer_cop"] = safe_div(m.new_mrr_cop, m.new_customers)
    pct = {"p25": 25, "median": 50, "p75": 75, "p90": 90}
    for k, q in pct.items():
        vals = []
        for t in range(T):
            v = cur[new[:, t], t]
            vals.append(np.percentile(v, q) if (t > 0 and v.size) else np.nan)
        m[f"{k}_new_customer_mrr_cop"] = vals

    prev_active = m.active_customers.shift(1)
    prev_mrr = m.total_paid_mrr_cop.shift(1)
    m["logo_churn_rate"] = safe_div(m.churned_customers, prev_active)
    m["gross_mrr_churn_rate"] = safe_div(-m.churned_mrr_cop, prev_mrr)
    m["contraction_rate"] = safe_div(-m.contraction_mrr_cop, prev_mrr)
    m["expansion_rate"] = safe_div(m.expansion_mrr_cop, prev_mrr)
    m["reactivation_rate"] = safe_div(m.reactivated_customers, m.dormant_pool_prev)
    m["net_mrr_retention_existing"] = safe_div(prev_mrr + m.expansion_mrr_cop + m.contraction_mrr_cop
                                               + m.churned_mrr_cop, prev_mrr)
    m["quick_ratio"] = safe_div(m.new_mrr_cop + m.expansion_mrr_cop + m.reactivation_mrr_cop,
                                -(m.contraction_mrr_cop + m.churned_mrr_cop))
    m["churn_events_returning_next_month"] = [np.nansum(ar["returned_next"][:, t]) if t > 0 else np.nan for t in range(T)]
    m["share_churn_returning_next_month"] = [
        (np.nanmean(ar["returned_next"][churn[:, t], t]) if (t > 0 and t < T - 1 and churn[:, t].any()) else np.nan)
        for t in range(T)]
    m["multi_month_payment_signatures"] = (ar["signature"] > 0).sum(0)

    # S&M (units as reported)
    s = sm.copy()
    s["month"] = s["month"].astype(str)
    s = s.rename(columns=SM_SNAKE)
    m = m.merge(s, on="month", how="left", validate="one_to_one")
    assert not m[list(SM_SNAKE.values())].isna().any().any(), "S&M months do not align"
    for g, cols in SM_GROUPS.items():
        m[g] = m[[SM_SNAKE[c] for c in cols]].sum(axis=1)
    m["total_sm_spend"] = m[list(SM_SNAKE.values())].sum(axis=1)
    m["total_sm_ex_payroll"] = m.total_sm_spend - m.payroll_expenses
    m["team_share_of_total_sm"] = m.team / m.total_sm_spend
    assert np.allclose(m[list(SM_GROUPS)].sum(axis=1), m.total_sm_spend)

    # efficiency (computed only where the numerator/denominator are interpretable)
    ok = (m.window_flag == "clean").to_numpy()
    newc = m.new_customers.to_numpy(dtype=float)
    newmrr_mm = m.new_mrr_cop.to_numpy(dtype=float) / 1e6
    for num, lab in [("total_sm_spend", "total_sm"), ("demand_gen_spend", "demand_gen"), ("paid_media", "paid_media")]:
        v = m[num].to_numpy(dtype=float)
        m[f"{lab}_per_new_customer"] = np.where(ok, safe_div(v, newc), np.nan)
        m[f"{lab}_per_new_mrr_mm_cop"] = np.where(ok, safe_div(v, newmrr_mm), np.nan)
        # trailing 3 months (all three months inside the clean window)
        v3 = pd.Series(v).rolling(3).sum().to_numpy()
        n3 = pd.Series(newc).rolling(3).sum().to_numpy()
        r3 = pd.Series(newmrr_mm).rolling(3).sum().to_numpy()
        ok3 = np.array([t >= clean_start + 2 for t in range(T)])
        m[f"{lab}_per_new_customer_t3m"] = np.where(ok3, safe_div(v3, n3), np.nan)
        m[f"{lab}_per_new_mrr_mm_cop_t3m"] = np.where(ok3, safe_div(v3, r3), np.nan)
    m["new_customers_per_sm_unit"] = np.where(ok, safe_div(newc, m.total_sm_spend), np.nan)
    m["new_mrr_cop_per_sm_unit"] = np.where(ok, safe_div(m.new_mrr_cop, m.total_sm_spend), np.nan)
    m["new_customers_per_demand_gen_unit"] = np.where(ok, safe_div(newc, m.demand_gen_spend), np.nan)
    m["new_mrr_cop_per_demand_gen_unit"] = np.where(ok, safe_div(m.new_mrr_cop, m.demand_gen_spend), np.nan)
    status = np.where(m.month_index == 0, "not_computable_new_customers_unidentifiable",
                      np.where(m.month_index < clean_start, "excluded_suspected_spillover", "ok"))
    status = np.where((status == "ok") & (newc == 0), "undefined_zero_denominator", status)
    m["efficiency_status"] = status

    for c in ["total_paid_mrr_cop", "new_customers", "new_mrr_cop", "net_customer_adds", "active_customers"]:
        m[f"{c}_3m_avg"] = m[c].rolling(3).mean()
    m.loc[m.month_index < clean_start + 2, ["new_customers_3m_avg", "new_mrr_cop_3m_avg", "net_customer_adds_3m_avg"]] = np.nan
    return m


# ----------------------------------------------------------------------------------
# 4 · Lag relationships (association only, never attribution)
# ----------------------------------------------------------------------------------
def lag_correlations(m: pd.DataFrame, clean_start: int, include_spillover: bool = False):
    spend = {"Paid Media": m.paid_media, "Generación de demanda": m.demand_gen_spend, "S&M total": m.total_sm_spend}
    outcome = {"Altas": m.new_customers, "MRR nuevo": m.new_mrr_cop}
    start = 1 if include_spillover else clean_start
    T = len(m)
    rows = []
    for sname, s in spend.items():
        s = s.to_numpy(dtype=float)
        for oname, o in outcome.items():
            o = o.to_numpy(dtype=float)
            for k in range(4):
                for transform in ["levels", "mom_change"]:
                    xs, ys, ts = [], [], []
                    for t in range(start, T):
                        if transform == "levels":
                            if t - k < 0:
                                continue
                            xs.append(s[t - k]); ys.append(o[t]); ts.append(t)
                        else:
                            if t - 1 < start or t - k - 1 < 0:
                                continue
                            xs.append(s[t - k] - s[t - k - 1]); ys.append(o[t] - o[t - 1]); ts.append(t)
                    x, y = np.array(xs), np.array(ys)
                    pr = stats.pearsonr(x, y)
                    sr = stats.spearmanr(x, y)
                    rows.append({"spend": sname, "outcome": oname, "lag_months": k, "transform": transform,
                                 "window": f"{m.month[ts[0]]}..{m.month[ts[-1]]}", "n": len(x),
                                 "pearson_r": pr.statistic, "pearson_p": pr.pvalue,
                                 "spearman_rho": sr.statistic, "spearman_p": sr.pvalue})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------
# 5 · Industries
# ----------------------------------------------------------------------------------
def industry_tables(ar: dict, m: pd.DataFrame, order: list[str], clean_start: int):
    months = ar["months"]
    T = len(months)
    rows = []
    for ind in order:
        mask = ar["ind"] == ind
        pos = ar["pos"][mask]
        prev_active = np.concatenate([[np.nan], pos.sum(0)[:-1]])
        d = {
            "active_customers": pos.sum(0),
            "new_customers": ar["new"][mask].sum(0),
            "churned_customers": ar["churn"][mask].sum(0),
            "reactivated_customers": ar["react"][mask].sum(0),
            "expanded_customers": ar["expand"][mask].sum(0),
            "contracted_customers": ar["contract"][mask].sum(0),
            "total_paid_mrr_cop": ar["cur_cop"][mask].sum(0),
            "new_mrr_cop": ar["new_mrr"][mask].sum(0),
            "expansion_mrr_cop": ar["exp_mrr"][mask].sum(0),
            "reactivation_mrr_cop": ar["react_mrr"][mask].sum(0),
            "contraction_mrr_cop": ar["con_mrr"][mask].sum(0),
            "churned_mrr_cop": ar["churn_mrr"][mask].sum(0),
        }
        df = pd.DataFrame(d)
        df.insert(0, "industry", ind)
        df.insert(0, "month", [str(x) for x in months])
        df["month_index"] = np.arange(T)
        df["mrr_per_active_customer_cop"] = safe_div(df.total_paid_mrr_cop, df.active_customers)
        df["new_mrr_per_new_customer_cop"] = safe_div(df.new_mrr_cop, df.new_customers)
        df["logo_churn_rate"] = safe_div(df.churned_customers, prev_active)
        flows = ["new_customers", "churned_customers", "reactivated_customers", "expanded_customers",
                 "contracted_customers", "new_mrr_cop", "expansion_mrr_cop", "reactivation_mrr_cop",
                 "contraction_mrr_cop", "churned_mrr_cop", "new_mrr_per_new_customer_cop", "logo_churn_rate"]
        df.loc[df.month_index == 0, flows] = np.nan
        rows.append(df)
    im = pd.concat(rows, ignore_index=True)

    # shares of company totals
    tot = im.groupby("month")[["active_customers", "total_paid_mrr_cop", "new_customers", "new_mrr_cop"]].transform("sum")
    im["share_active_customers"] = safe_div(im.active_customers, tot.active_customers)
    im["share_mrr"] = safe_div(im.total_paid_mrr_cop, tot.total_paid_mrr_cop)
    im["share_new_customers"] = safe_div(im.new_customers, tot.new_customers)
    im["share_new_mrr"] = safe_div(im.new_mrr_cop, tot.new_mrr_cop)

    # half-year flows (clean window only) and year summary
    per = pd.PeriodIndex(im.month, freq="M")
    im["half"] = [half_label(p) for p in per]
    im["year"] = per.year
    clean = im[im.month_index >= clean_start]
    agg = {"new_customers": "sum", "new_mrr_cop": "sum", "churned_customers": "sum",
           "reactivated_customers": "sum", "expansion_mrr_cop": "sum", "contraction_mrr_cop": "sum",
           "churned_mrr_cop": "sum", "reactivation_mrr_cop": "sum"}
    half = clean.groupby(["half", "industry"], sort=True).agg(agg).reset_index()
    half["new_mrr_per_new_customer_cop"] = safe_div(half.new_mrr_cop, half.new_customers)
    htot = half.groupby("half")[["new_customers", "new_mrr_cop"]].transform("sum")
    half["share_new_customers"] = safe_div(half.new_customers, htot.new_customers)
    half["share_new_mrr"] = safe_div(half.new_mrr_cop, htot.new_mrr_cop)

    # yearly scorecard
    ys = []
    for (y, ind), g in clean.groupby(["year", "industry"]):
        last = g.sort_values("month_index").iloc[-1]
        prev_active_sum = im[(im.industry == ind) & (im.month_index.isin(g.month_index - 1))].active_customers.sum()
        ys.append({"year": int(y), "industry": ind, "months": int(g.shape[0]),
                   "period": f"{g.month.min()}..{g.month.max()}",
                   "active_customers_end": int(last.active_customers),
                   "mrr_end_cop": float(last.total_paid_mrr_cop),
                   "arpa_end_cop": float(last.mrr_per_active_customer_cop),
                   "new_customers": int(g.new_customers.sum()),
                   "new_mrr_cop": float(g.new_mrr_cop.sum()),
                   "new_mrr_per_new_customer_cop": float(g.new_mrr_cop.sum() / g.new_customers.sum()),
                   "churned_customers": int(g.churned_customers.sum()),
                   "avg_monthly_logo_churn_rate": float(g.churned_customers.sum() / prev_active_sum),
                   "reactivated_customers": int(g.reactivated_customers.sum()),
                   "expansion_mrr_cop": float(g.expansion_mrr_cop.sum()),
                   "contraction_mrr_cop": float(g.contraction_mrr_cop.sum()),
                   "churned_mrr_cop": float(g.churned_mrr_cop.sum())})
    ysum = pd.DataFrame(ys)
    tot_end = ysum.groupby("year")[["active_customers_end", "mrr_end_cop", "new_customers", "new_mrr_cop"]].transform("sum")
    ysum["share_active_end"] = ysum.active_customers_end / tot_end.active_customers_end
    ysum["share_mrr_end"] = ysum.mrr_end_cop / tot_end.mrr_end_cop
    ysum["share_new_customers"] = ysum.new_customers / tot_end.new_customers
    ysum["share_new_mrr"] = ysum.new_mrr_cop / tot_end.new_mrr_cop
    return im, half, ysum


# ----------------------------------------------------------------------------------
# 6 · Mix vs within-segment decomposition of New MRR per new customer
# ----------------------------------------------------------------------------------
def shapley(df0: pd.DataFrame, df1: pd.DataFrame, value: str, order: list[str]):
    """Exact two-factor (Shapley / midpoint) decomposition of a change in a weighted mean.
    A = sum_i s_i * a_i  (s = share of new customers, a = mean value within industry)
    dA = sum (s1-s0)(a0+a1)/2  [mix]  +  sum (a1-a0)(s0+s1)/2  [within]   -- no residual."""
    g0 = df0.groupby("industry")[value].agg(["size", "mean"]).reindex(order)
    g1 = df1.groupby("industry")[value].agg(["size", "mean"]).reindex(order)
    if g0["size"].isna().any() or g1["size"].isna().any():
        raise ValueError("an industry has no new customers in one period")
    s0, s1 = g0["size"] / g0["size"].sum(), g1["size"] / g1["size"].sum()
    a0, a1 = g0["mean"], g1["mean"]
    A0, A1 = float((s0 * a0).sum()), float((s1 * a1).sum())
    mix_i = (s1 - s0) * (a0 + a1) / 2
    within_i = (a1 - a0) * (s0 + s1) / 2
    las_mix = float(((s1 - s0) * a0).sum())
    las_within = float((s0 * (a1 - a0)).sum())
    las_inter = float(((s1 - s0) * (a1 - a0)).sum())
    res = {"A0": A0, "A1": A1, "delta": A1 - A0, "mix": float(mix_i.sum()), "within": float(within_i.sum()),
           "laspeyres_mix": las_mix, "laspeyres_within": las_within, "laspeyres_interaction": las_inter,
           "counterfactual_A1_at_base_mix": float((s0 * a1).sum()),
           "n0": int(g0["size"].sum()), "n1": int(g1["size"].sum())}
    assert abs(res["mix"] + res["within"] - res["delta"]) < 1e-6
    assert abs(las_mix + las_within + las_inter - res["delta"]) < 1e-6
    detail = pd.DataFrame({"industry": order, "n0": g0["size"].values, "n1": g1["size"].values,
                           "share0": s0.values, "share1": s1.values, "mean0": a0.values, "mean1": a1.values,
                           "mix_contribution": mix_i.values, "within_contribution": within_i.values})
    return res, detail


def bootstrap_decomp(df0, df1, value, order, n_boot=BOOT_N, seed=SEED):
    rng = np.random.default_rng(seed)
    codes = {k: i for i, k in enumerate(order)}
    c0, v0 = df0.industry.map(codes).to_numpy(), df0[value].to_numpy()
    c1, v1 = df1.industry.map(codes).to_numpy(), df1[value].to_numpy()
    K = len(order)
    out = np.empty((n_boot, 3))
    for b in range(n_boot):
        i0 = rng.integers(0, len(c0), len(c0))
        i1 = rng.integers(0, len(c1), len(c1))
        n0 = np.bincount(c0[i0], minlength=K).astype(float)
        n1 = np.bincount(c1[i1], minlength=K).astype(float)
        if (n0 == 0).any() or (n1 == 0).any():
            out[b] = np.nan
            continue
        a0 = np.bincount(c0[i0], weights=v0[i0], minlength=K) / n0
        a1 = np.bincount(c1[i1], weights=v1[i1], minlength=K) / n1
        s0, s1 = n0 / n0.sum(), n1 / n1.sum()
        mix = ((s1 - s0) * (a0 + a1) / 2).sum()
        within = ((a1 - a0) * (s0 + s1) / 2).sum()
        out[b] = (mix, within, mix + within)
    out = out[~np.isnan(out).any(axis=1)]
    lo, hi = np.percentile(out, [5, 95], axis=0)
    share_within = out[:, 1] / out[:, 2]
    return {"mix_ci90": [float(lo[0]), float(hi[0])], "within_ci90": [float(lo[1]), float(hi[1])],
            "delta_ci90": [float(lo[2]), float(hi[2])],
            "within_share_ci90": [float(np.percentile(share_within, 5)), float(np.percentile(share_within, 95))],
            "n_boot_valid": int(out.shape[0])}


def new_customer_frame(ar: dict, clean_start: int):
    A, pos, first = ar["A"], ar["pos"], ar["first_idx"]
    months = ar["months"]
    T = len(months)
    to_cop = SCALE_TO_COP / MICRO
    rows = []
    for i in range(A.shape[0]):
        f = first[i]
        if f == 0:
            continue
        early = A[i, f:min(f + 3, T)]
        early_pos = early[early > 0]
        rows.append({"customer_id": int(ar["ids"][i]), "industry": ar["ind"][i], "cohort_index": int(f),
                     "cohort_month": months[f], "m0_cop": A[i, f] * to_cop,
                     "early_run_rate_cop": float(np.median(early_pos)) * to_cop,
                     "early_months_observed": int(early.size),
                     "m1_cop": A[i, f + 1] * to_cop if f + 1 < T else np.nan})
    nc = pd.DataFrame(rows)
    nc["year"] = [p.year for p in nc.cohort_month]
    nc["half"] = [half_label(p) for p in nc.cohort_month]
    nc["quarter"] = [quarter_label(p) for p in nc.cohort_month]
    nc["clean"] = nc.cohort_index >= clean_start
    return nc


def decomposition(nc: pd.DataFrame, order: list[str]):
    clean = nc[nc.clean].copy()
    cap = clean.m0_cop.quantile(0.99)
    clean["m0_winsor_cop"] = clean.m0_cop.clip(upper=cap)
    out = {"winsor_cap_cop": float(cap)}
    periods = {"2022": clean[clean.year == 2022], "2023": clean[clean.year == 2023], "2024": clean[clean.year == 2024]}
    comparisons = [("2022", "2023"), ("2023", "2024"), ("2022", "2024")]
    variants = {"m0_cop": "Ticket de entrada observado (M0) · principal",
                "m0_winsor_cop": "M0 winsorizado en P99",
                "early_run_rate_cop": "Run-rate temprano (mediana de M0–M2 positivos)"}
    main, details, robust = {}, {}, []
    for a, b in comparisons:
        for v, vlabel in variants.items():
            res, det = shapley(periods[a], periods[b], v, order)
            boot = bootstrap_decomp(periods[a], periods[b], v, order)
            row = {"comparison": f"{a} vs {b}", "variant": vlabel, "value_col": v, **res, **{
                "mix_ci90_lo": boot["mix_ci90"][0], "mix_ci90_hi": boot["mix_ci90"][1],
                "within_ci90_lo": boot["within_ci90"][0], "within_ci90_hi": boot["within_ci90"][1],
                "within_share_ci90_lo": boot["within_share_ci90"][0],
                "within_share_ci90_hi": boot["within_share_ci90"][1]}}
            row["within_share"] = row["within"] / row["delta"] if row["delta"] else np.nan
            row["mix_share"] = row["mix"] / row["delta"] if row["delta"] else np.nan
            robust.append(row)
            if v == "m0_cop":
                main[f"{a}_{b}"] = row
                det = det.copy()
                det.insert(0, "comparison", f"{a} vs {b}")
                details[f"{a}_{b}"] = det
    # medians (not additive -> descriptive only)
    med = clean.groupby(["year", "industry"]).m0_cop.median().unstack().reindex(columns=order)
    # evolution by half-year vs 2022 base (Mar–Dec 2022)
    base = periods["2022"]
    evo = []
    for h, g in clean.groupby("half"):
        res, _ = shapley(base, g, "m0_cop", order)
        evo.append({"half": h, "n": res["n1"], "mean_m0_cop": res["A1"], "gap_vs_2022_cop": res["delta"],
                    "mix_cop": res["mix"], "within_cop": res["within"],
                    "median_m0_cop": float(g.m0_cop.median())})
    out.update({"main": main, "details": details, "robust": pd.DataFrame(robust), "medians": med,
                "evolution": pd.DataFrame(evo)})
    return out


# ----------------------------------------------------------------------------------
# 7 · Cohorts
# ----------------------------------------------------------------------------------
def cohorts(ar: dict, clean_start: int):
    months = ar["months"]
    T = len(months)
    pos, cur, first = ar["pos"], ar["cur_cop"], ar["first_idx"]
    n = pos.shape[0]
    # tenure-aligned matrices (customers x tenure), NaN when not observable
    act_t = np.full((n, T), np.nan)
    mrr_t = np.full((n, T), np.nan)
    for i in range(n):
        f = first[i]
        L = T - f
        act_t[i, :L] = pos[i, f:]
        mrr_t[i, :L] = cur[i, f:]
    cohort_month = np.array([months[f] for f in first])
    cq = np.array([quarter_label(p) for p in cohort_month])
    cy = np.array([p.year for p in cohort_month])

    def curve(mask, with_arpu=False):
        obs = ~np.isnan(act_t[mask])
        logo = np.nansum(act_t[mask], 0) / obs.sum(0).clip(min=1)
        # revenue retention over the SAME customers that are observable at tenure k
        rev, arpu = [], []
        m0 = mrr_t[mask][:, 0]
        for k in range(T):
            o = obs[:, k]
            rev.append(np.nansum(mrr_t[mask][o, k]) / m0[o].sum() if o.any() and m0[o].sum() > 0 else np.nan)
            arpu.append(np.nansum(mrr_t[mask][o, k]) / o.sum() if o.any() else np.nan)
        size = obs.sum(0)
        logo = np.where(size > 0, logo, np.nan)
        if with_arpu:
            return logo, np.array(rev), size, np.array(arpu)
        return logo, np.array(rev), size

    monthly = []
    for c in range(1, T):
        mask = first == c
        if not mask.any():
            continue
        logo, rev, size, arpu = curve(mask, with_arpu=True)
        monthly.append({"cohort": str(months[c]), "cohort_index": c, "flag": "suspected_spillover" if c < clean_start else "clean",
                        "size": int(mask.sum()), "m0_mrr_cop": float(mrr_t[mask][:, 0].sum()),
                        "m0_mean_cop": float(mrr_t[mask][:, 0].mean()), "m0_median_cop": float(np.median(mrr_t[mask][:, 0])),
                        "logo": logo[: T - c].tolist(), "revenue": rev[: T - c].tolist(), "arpu": arpu[: T - c].tolist()})
    quarterly = []
    for q in sorted(set(cq[first >= clean_start])):
        mask = (cq == q) & (first >= clean_start)
        logo, rev, size, arpu = curve(mask, with_arpu=True)
        kmax = int((size > 0).sum())
        cms = sorted({str(cohort_month[i]) for i in np.where(mask)[0]})
        quarterly.append({"cohort": q, "months_in_cohort": cms, "partial": len(cms) < 3,
                          "size": int(mask.sum()), "m0_mean_cop": float(mrr_t[mask][:, 0].mean()),
                          "m0_median_cop": float(np.median(mrr_t[mask][:, 0])),
                          "logo": logo[:kmax].tolist(), "revenue": rev[:kmax].tolist(), "arpu": arpu[:kmax].tolist(),
                          "observable": size[:kmax].tolist()})
    yearly = []
    for y in [2022, 2023, 2024]:
        mask = (cy == y) & (first >= clean_start)
        logo, rev, size, arpu = curve(mask, with_arpu=True)
        kmax = int((size > 0).sum())
        yearly.append({"cohort": f"{y}" + (" (mar–dic)" if y == 2022 else (" (ene–oct)" if y == 2024 else "")),
                       "size": int(mask.sum()), "logo": logo[:kmax].tolist(), "revenue": rev[:kmax].tolist(),
                       "arpu": arpu[:kmax].tolist(), "observable": size[:kmax].tolist()})
    # separately flagged groups
    feb = first == 1
    lf, rf, sf = curve(feb)
    base = first == 0
    base_logo = pos[base].mean(0)
    base_rev = cur[base].sum(0) / cur[base][:, 0].sum()
    flagged = {"spillover_feb22": {"size": int(feb.sum()), "logo": lf[: T - 1].tolist(), "revenue": rf[: T - 1].tolist()},
               "left_censored_base": {"size": int(base.sum()), "logo_calendar": base_logo.tolist(),
                                      "revenue_calendar": base_rev.tolist(),
                                      "mrr_calendar_cop": cur[base].sum(0).tolist()}}
    # summary per quarterly cohort
    summ = []
    exp_any = np.zeros(n, dtype=bool)
    for i in range(n):
        f = first[i]
        exp_any[i] = ar["expand"][i, f + 1:min(f + 7, T)].any()
    for q in quarterly:
        mask = (cq == q["cohort"]) & (first >= clean_start)
        row = {"cohort": q["cohort"], "partial": q["partial"], "size": q["size"],
               "m0_mean_cop": q["m0_mean_cop"], "m0_median_cop": q["m0_median_cop"]}
        for k in [1, 2, 3, 6, 12]:
            row[f"logo_m{k}"] = q["logo"][k] if k < len(q["logo"]) else np.nan
            row[f"revenue_m{k}"] = q["revenue"][k] if k < len(q["revenue"]) else np.nan
            row[f"observable_m{k}"] = q["observable"][k] if k < len(q["observable"]) else 0
        full6 = mask & (first + 6 <= T - 1)
        row["share_expanding_within_m6"] = float(exp_any[full6].mean()) if full6.any() else np.nan
        summ.append(row)
    return {"monthly": monthly, "quarterly": quarterly, "yearly": yearly, "flagged": flagged,
            "summary": pd.DataFrame(summ)}


# ----------------------------------------------------------------------------------
# 8 · Movement diagnostics (how much of the observed movement is transient)
# ----------------------------------------------------------------------------------
def movement_diagnostics(ar: dict, m: pd.DataFrame):
    months = ar["months"]
    T = len(months)
    churn = ar["churn"]
    mtr = ar["months_to_return"]
    ev = []
    for t in range(1, T):
        idx = np.where(churn[:, t])[0]
        for i in idx:
            g = mtr[i, t]
            ev.append({"month": str(months[t]), "year": months[t].year, "months_to_return": g,
                       "months_observable_after": T - 1 - t,
                       "churned_mrr_cop": -ar["churn_mrr"][i, t],
                       "same_amount_return": ar["same_amount_return"][i, t]})
    ev = pd.DataFrame(ev)

    def bucket(g):
        if np.isnan(g):
            return "Sin volver a oct-24"
        g = int(g)
        return "1 mes" if g == 1 else ("2 meses" if g == 2 else ("3–5 meses" if g <= 5 else "6+ meses"))
    ev["return_bucket"] = ev.months_to_return.map(bucket)
    by_year = ev.groupby(["year", "return_bucket"]).size().unstack(fill_value=0)
    exp_rev = ar["exp_mrr"][:, 1:-1]
    rev_mask = ar["reverts"][:, 1:-1] == 1
    con_rev = ar["con_mrr"][:, 1:-1]
    churn_next = ar["returned_next"][:, 1:-1] == 1
    res = {
        "events": ev,
        "by_year": by_year,
        "n_churn_events": int(len(ev)),
        "share_return_1m": float((ev.months_to_return == 1).mean()),
        "share_return_any": float(ev.months_to_return.notna().mean()),
        "share_return_1m_excl_last_month": float((ev[ev.month != str(months[-1])].months_to_return == 1).mean()),
        "share_churned_mrr_back_1m": float(ev.loc[ev.months_to_return == 1, "churned_mrr_cop"].sum() / ev.churned_mrr_cop.sum()),
        "share_expansion_mrr_reverting_1m": float(exp_rev[rev_mask].sum() / exp_rev.sum()),
        "share_contraction_mrr_reverting_1m": float(con_rev[rev_mask].sum() / con_rev.sum()),
        "share_expansion_events_reverting_1m": float(np.nanmean(ar["reverts"][:, 1:-1][ar["expand"][:, 1:-1]])),
        "share_contraction_events_reverting_1m": float(np.nanmean(ar["reverts"][:, 1:-1][ar["contract"][:, 1:-1]])),
        "multi_month_signatures": int((ar["signature"] > 0).sum()),
        "multi_month_signature_customers": int(((ar["signature"] > 0).any(axis=1)).sum()),
        "signature_k_counts": {int(k): int(v) for k, v in zip(*np.unique(ar["signature"][ar["signature"] > 0], return_counts=True))},
    }
    # contraction that only normalises a one-month spike: A[t] == A[t-2] and A[t-1] > A[t-2] > 0
    A, P = ar["A"], ar["P"]
    A2 = np.zeros_like(A)
    A2[:, 2:] = A[:, :-2]
    post_spike = ar["contract"] & (A == A2) & (A2 > 0)
    post_spike[:, :2] = False
    res["share_contraction_mrr_post_spike"] = float(ar["con_mrr"][post_spike].sum() / ar["con_mrr"].sum())
    # small proportional adjustments (|change| < 10 %) by half-year
    ratio = np.where(ar["expand"] | ar["contract"], A / np.where(P > 0, P, 1), np.nan)
    small = np.abs(ratio - 1) < 0.10
    halves = np.array([half_label(p) for p in months])
    rows = []
    for h in dict.fromkeys(halves[1:]):
        cols = np.where(halves == h)[0]
        cols = cols[cols > 0]
        e, c = ar["expand"][:, cols], ar["contract"][:, cols]
        s = small[:, cols]
        rows.append({"half": h, "expansion_events": int(e.sum()), "expansion_small": int((e & s).sum()),
                     "contraction_events": int(c.sum()), "contraction_small": int((c & s).sum()),
                     "expansion_mrr_cop": float(ar["exp_mrr"][:, cols].sum()),
                     "expansion_small_mrr_cop": float(ar["exp_mrr"][:, cols][e & s].sum()),
                     "contraction_mrr_cop": float(ar["con_mrr"][:, cols].sum()),
                     "contraction_small_mrr_cop": float(ar["con_mrr"][:, cols][c & s].sum())})
    sa = pd.DataFrame(rows)
    sa["expansion_small_share"] = sa.expansion_small / sa.expansion_events
    sa["contraction_small_share"] = sa.contraction_small / sa.contraction_events
    res["small_adjustments"] = sa
    # share of active customer-months on the COP 2,100 amount grid (0.21 x 10,000), exact in micro-units
    grid = (A % 210_000 == 0) & (A > 0)
    res["grid_share_monthly"] = grid.sum(0) / ar["pos"].sum(0)
    res["grid_share_half"] = pd.Series(grid.sum(0), index=halves).groupby(level=0, sort=False).sum() / \
        pd.Series(ar["pos"].sum(0), index=halves).groupby(level=0, sort=False).sum()
    # gross vs net over the window
    comps = ["new_mrr_cop", "expansion_mrr_cop", "reactivation_mrr_cop", "contraction_mrr_cop", "churned_mrr_cop"]
    res["gross_movement_cop"] = float(m[comps].abs().sum().sum())
    res["net_movement_cop"] = float(m[comps].sum().sum())
    return res


# ----------------------------------------------------------------------------------
# 9 · Assemble, validate, write
# ----------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-dir", default=str(HERE / "data" / "raw"))
    ap.add_argument("--out-dir", default=str(HERE))
    args = ap.parse_args()
    raw_dir, out_dir = Path(args.raw_dir), Path(args.out_dir)
    sup_dir = out_dir / "supporting"
    sup_dir.mkdir(parents=True, exist_ok=True)

    raw = read_raw(raw_dir)
    industry, a_ind = audit_industry(raw["industry"])
    tx, a_tx = audit_transactions(raw["transactions"])
    sm, team_share, a_sm = audit_sm(raw["sm"])

    # consistency across sources
    tx_ids, ind_ids = set(tx.customer_id.astype(int)), set(industry.customer_id)
    tx_months = sorted(set(tx.month))
    consistency = {
        "tx_ids_without_industry": sorted(tx_ids - ind_ids),
        "industry_ids_without_tx": sorted(ind_ids - tx_ids),
        "id_match_rate": len(tx_ids & ind_ids) / len(tx_ids),
        "sm_months_equal_tx_months": [str(x) for x in sm.month] == [str(x) for x in tx_months],
        "customers_never_positive": None,
    }
    assert not consistency["tx_ids_without_industry"], "IDs without industry"

    cm, ar = build_customer_month(tx.assign(customer_id=tx.customer_id.astype(int)), industry)
    months = ar["months"]
    T = len(months)
    consistency["customers_never_positive"] = int((~ar["pos"].any(axis=1)).sum())

    # evidence for the spillover flag on the second month (catch-up signature at entry)
    sig_entry = []
    for c in range(1, T - 1):
        idx = np.where(ar["first_idx"] == c)[0]
        a0, a1 = ar["A"][idx, c], ar["A"][idx, c + 1]
        dbl = (a1 > 0) & (np.abs(a0 - 2 * a1) <= 0.001 * a0)
        sig_entry.append({"cohort": str(months[c]), "new_customers": int(idx.size),
                          "first_amount_2x_next": int(dbl.sum()), "share": float(dbl.mean()) if idx.size else np.nan})
    sig_entry = pd.DataFrame(sig_entry)
    later_median = sig_entry.loc[sig_entry.cohort != str(months[1]), "share"].median()
    feb_share = float(sig_entry.loc[sig_entry.cohort == str(months[1]), "share"].iloc[0])
    assert feb_share > 5 * max(later_median, 0.01), "spillover evidence no longer holds - review CLEAN_START"
    clean_start = 2

    mm = build_monthly(ar, sm, clean_start)
    # ---- validations (bridges must close exactly)
    assert mm.mrr_bridge_diff_cop.iloc[1:].abs().max() < 1e-4, "MRR bridge does not close"
    assert mm.customer_bridge_diff.iloc[1:].abs().max() == 0, "customer bridge does not close"
    assert abs(mm.total_paid_mrr_cop.sum() - tx.amount.sum() * SCALE_TO_COP) < 1, "MRR total != raw total"
    assert int(cm.active_customer.sum()) == a_tx["positive_amount_rows"]
    flag_sum = cm[["new_customer", "churned_customer", "reactivated_customer", "expanded_customer",
                   "contracted_customer", "flat_customer"]].sum(axis=1)
    assert flag_sum.max() <= 1, "movement flags are not mutually exclusive"

    corr = lag_correlations(mm, clean_start)
    corr_sens = lag_correlations(mm, clean_start, include_spillover=True)

    order = list(pd.Series(ar["ind"]).value_counts().index)     # by customer count, fixes colour slots
    im, ihalf, iyear = industry_tables(ar, mm, order, clean_start)
    for col in ["active_customers", "new_customers", "total_paid_mrr_cop", "new_mrr_cop"]:
        chk = im.groupby("month")[col].sum().reindex(mm.month).fillna(0).to_numpy()
        ref = mm[col].fillna(0).to_numpy()
        assert np.allclose(chk, ref), f"industry split does not add up for {col}"

    nc = new_customer_frame(ar, clean_start)
    dec = decomposition(nc, order)
    coh = cohorts(ar, clean_start)
    mov = movement_diagnostics(ar, mm)

    # ------------------------------------------------------------------ outputs: CSV
    cm_out = cm.copy()
    tidy(cm_out).to_csv(out_dir / "finora_analytical_dataset.csv", index=False)
    tidy(mm).to_csv(out_dir / "finora_monthly_metrics.csv", index=False)
    tidy(im).to_csv(sup_dir / "industry_monthly.csv", index=False)
    tidy(ihalf).to_csv(sup_dir / "industry_halfyear_new_customers.csv", index=False)
    tidy(iyear).to_csv(sup_dir / "industry_scorecard_by_year.csv", index=False)
    tidy(corr).to_csv(sup_dir / "lag_correlations.csv", index=False)
    tidy(corr_sens).to_csv(sup_dir / "lag_correlations_incl_feb22.csv", index=False)
    tidy(dec["robust"]).to_csv(sup_dir / "mix_within_decomposition.csv", index=False)
    tidy(pd.concat(dec["details"].values())).to_csv(sup_dir / "mix_within_by_industry.csv", index=False)
    tidy(dec["evolution"]).to_csv(sup_dir / "mix_within_evolution_halfyear.csv", index=False)
    tidy(coh["summary"]).to_csv(sup_dir / "cohort_summary_quarterly.csv", index=False)
    lm = pd.DataFrame([dict(cohort=c["cohort"], flag=c["flag"], size=c["size"], **{f"M{k}": v for k, v in enumerate(c["logo"])}) for c in coh["monthly"]])
    rm = pd.DataFrame([dict(cohort=c["cohort"], flag=c["flag"], size=c["size"], **{f"M{k}": v for k, v in enumerate(c["revenue"])}) for c in coh["monthly"]])
    tidy(lm).to_csv(sup_dir / "cohort_logo_retention_monthly.csv", index=False)
    tidy(rm).to_csv(sup_dir / "cohort_revenue_retention_monthly.csv", index=False)
    tidy(mov["events"]).to_csv(sup_dir / "churn_events.csv", index=False)
    tidy(sig_entry).to_csv(sup_dir / "entry_catchup_signature_by_cohort.csv", index=False)
    tidy(nc.assign(cohort_month=nc.cohort_month.astype(str))).to_csv(sup_dir / "new_customers.csv", index=False)
    audit = {"transactions": a_tx, "industry": a_ind, "sm": a_sm, "consistency": consistency}
    (sup_dir / "data_audit.json").write_text(json.dumps(jsonable(audit), indent=2, ensure_ascii=False))

    ctx = dict(raw=raw, audit=audit, cm=cm, ar=ar, mm=mm, corr=corr, corr_sens=corr_sens, im=im,
               ihalf=ihalf, iyear=iyear, nc=nc, dec=dec, coh=coh, mov=mov, order=order,
               sig_entry=sig_entry, team_share=team_share, sm=sm, clean_start=clean_start,
               out_dir=out_dir, sup_dir=sup_dir)
    ctx["ev"] = extra_views(ctx)
    ev = ctx["ev"]
    tidy(ev["ticket_by_year"]).to_csv(sup_dir / "new_customer_ticket_by_year.csv", index=False)
    tidy(ev["annual_bridge"]).to_csv(sup_dir / "mrr_bridge_annual.csv", index=False)
    tidy(ev["vintage_arpa"]).to_csv(sup_dir / "arpa_by_vintage_monthly.csv", index=False)
    tidy(mov["small_adjustments"]).to_csv(sup_dir / "small_adjustments_by_half.csv", index=False)

    facts, raw_facts = build_facts(ctx)
    claims = check_claims(ctx, raw_facts)
    brain = load_brain()
    validate_brain(brain, claims, facts)
    payload = build_payload(ctx, facts, claims, brain)
    render_outputs(ctx, payload, facts, claims, brain)
    return ctx


# ----------------------------------------------------------------------------------
# 10 · Extra descriptive views used by the workspace
# ----------------------------------------------------------------------------------
# Hand-picked, clearly labelled illustrations of payment-timing patterns (prevalence is
# measured separately; these are NOT a representative sample).
EXAMPLE_CUSTOMERS = [
    (14, "Monto doble en may-22, cero en jun-22 y regreso al monto anterior"),
    (40, "Cuatro meses sin pago y luego ~5 veces el monto usual en dic-22"),
    (637, "Pagos cada dos meses por ~2 veces el monto mensual posterior"),
    (516, "El mismo monto grande ({amt}) en abr-22, abr-23 y jun-24, casi nada entre medio"),
]
PRICE_BANDS = [0, 15_000, 30_000, 45_000, 60_000, 75_000, 100_000, 150_000, np.inf]
PRICE_BAND_LABELS = ["<15 mil", "15–30 mil", "30–45 mil", "45–60 mil", "60–75 mil", "75–100 mil", "100–150 mil", "≥150 mil"]
AMOUNT_BINS = [1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6, 2e6, 5e6, 1e7]
VINT_BASE, VINT_FEB = "Base previa (activos en ene-22)", "Altas de feb-22 (marcadas)"
VINT_2022, VINT_2023, VINT_2024 = "Cosecha 2022 (mar–dic)", "Cosecha 2023", "Cosecha 2024"


def extra_views(ctx: dict) -> dict:
    ar, mm, nc, cs = ctx["ar"], ctx["mm"], ctx["nc"], ctx["clean_start"]
    months = ar["months"]
    T = len(months)
    idx = {str(m): i for i, m in enumerate(months)}
    ev = {}

    # ticket metrics by year (clean window)
    rows = []
    cap = ctx["dec"]["winsor_cap_cop"]
    for y, g in nc[nc.clean].groupby("year"):
        m1_obs = g[g.m1_cop.notna()]
        spike = (m1_obs.m1_cop > 0) & (m1_obs.m0_cop > 1.5 * m1_obs.m1_cop)
        rows.append({"year": int(y), "period": f"{g.cohort_month.min()}..{g.cohort_month.max()}", "new_customers": len(g),
                     "m0_mean_cop": g.m0_cop.mean(), "m0_median_cop": g.m0_cop.median(),
                     "m0_p25_cop": g.m0_cop.quantile(.25), "m0_p75_cop": g.m0_cop.quantile(.75),
                     "m0_p90_cop": g.m0_cop.quantile(.90), "m0_winsor_mean_cop": g.m0_cop.clip(upper=cap).mean(),
                     "early_run_rate_mean_cop": g.early_run_rate_cop.mean(),
                     "early_run_rate_median_cop": g.early_run_rate_cop.median(),
                     "m1_mean_cop": m1_obs.m1_cop.mean(), "share_first_month_spike": spike.mean()})
    ev["ticket_by_year"] = pd.DataFrame(rows)

    # price bands of the first observed amount (clean window)
    band = pd.cut(nc.loc[nc.clean, "m0_cop"], PRICE_BANDS, right=False, labels=PRICE_BAND_LABELS)
    bt = pd.crosstab(nc.loc[nc.clean, "year"], band).reindex(columns=PRICE_BAND_LABELS, fill_value=0)
    ev["price_bands"] = {"labels": PRICE_BAND_LABELS, "years": [int(y) for y in bt.index],
                         "counts": bt.to_numpy().tolist(),
                         "shares": (bt.div(bt.sum(axis=1), axis=0)).to_numpy().tolist()}

    # ARPA by acquisition vintage (calendar time)
    first = ar["first_idx"]
    years = np.array([months[f].year for f in first])
    groups = {VINT_BASE: first == 0, VINT_FEB: first == 1,
              VINT_2022: (first >= cs) & (years == 2022), VINT_2023: years == 2023, VINT_2024: years == 2024}
    vrows = []
    for gname, mask in groups.items():
        act = ar["pos"][mask].sum(0)
        mrr = ar["cur_cop"][mask].sum(0)
        for t in range(T):
            vrows.append({"month": str(months[t]), "vintage": gname, "active_customers": int(act[t]),
                          "mrr_cop": float(mrr[t]), "arpa_cop": float(mrr[t] / act[t]) if act[t] else np.nan})
    ev["vintage_arpa"] = pd.DataFrame(vrows)

    # distribution of positive monthly amounts (COP, log bins)
    pos_cop = ar["cur_cop"][ar["pos"]]
    cnt, _ = np.histogram(pos_cop, bins=AMOUNT_BINS)
    ev["amount_hist"] = {"edges": AMOUNT_BINS, "counts": cnt.tolist(),
                         "p50": float(np.median(pos_cop)), "p99": float(np.percentile(pos_cop, 99)),
                         "iqr_fence": ctx["audit"]["transactions"]["iqr_fence_q3_plus_3iqr"] * SCALE_TO_COP}

    # illustrative timelines (validated so the captions stay true)
    ex = []
    ids = list(ar["ids"])
    for cid, caption in EXAMPLE_CUSTOMERS:
        i = ids.index(cid)
        caption = caption.replace("{amt}", fmt_cop(ar["cur_cop"][i, idx["2022-04"]], 2))
        ex.append({"id": cid, "industry": ar["ind"][i], "caption": caption,
                   "amounts_cop": ar["cur_cop"][i].tolist(), "usual_cop": float(ar["usual"][i] * SCALE_TO_COP / MICRO)})
    A = ar["A"]
    r14, r40, r516 = ids.index(14), ids.index(40), ids.index(516)
    assert A[r14, idx["2022-05"]] == 2 * A[r14, idx["2022-04"]] and A[r14, idx["2022-06"]] == 0
    assert (A[r40, idx["2022-09"]:idx["2022-12"]] == 0).all() and abs(A[r40, idx["2022-12"]] / A[r40, idx["2023-01"]] - 5) < 0.05
    assert len({A[r516, idx[m]] for m in ["2022-04", "2023-04", "2024-06"]}) == 1
    ev["examples"] = ex

    # MRR bridge: annual and last period
    comps = ["new_mrr_cop", "expansion_mrr_cop", "reactivation_mrr_cop", "contraction_mrr_cop", "churned_mrr_cop"]
    brows = []
    for y in [2022, 2023, 2024]:
        g = mm[(mm.month.str[:4] == str(y)) & (mm.month_index > 0)]
        open_i = g.month_index.min() - 1
        opening = float(mm.total_paid_mrr_cop[open_i])
        closing = float(mm.total_paid_mrr_cop[g.month_index.max()])
        row = {"year": y, "period": f"{g.month.min()}..{g.month.max()}", "opening_mrr_cop": opening,
               **{c: float(g[c].sum()) for c in comps}, "closing_mrr_cop": closing}
        row["net_change_cop"] = sum(row[c] for c in comps)
        row["check_diff_cop"] = closing - opening - row["net_change_cop"]
        assert abs(row["check_diff_cop"]) < 1e-3
        brows.append(row)
    ev["annual_bridge"] = pd.DataFrame(brows)
    last = mm.iloc[-1]
    prev = mm.iloc[-2]
    ev["last_bridge"] = {"from_month": prev.month, "to_month": last.month,
                         "opening_mrr_cop": float(prev.total_paid_mrr_cop), "closing_mrr_cop": float(last.total_paid_mrr_cop),
                         **{c: float(last[c]) for c in comps},
                         "net_change_cop": float(last.net_mrr_change_cop),
                         "check_diff_cop": float(last.total_paid_mrr_cop - prev.total_paid_mrr_cop - last.net_mrr_change_cop)}
    assert abs(ev["last_bridge"]["check_diff_cop"]) < 1e-3

    # efficiency pooled by year (clean months only)
    erows = []
    clean = mm[mm.window_flag == "clean"]
    for y, g in clean.groupby(clean.month.str[:4]):
        erows.append({"year": int(y), "months": len(g), "new_customers": g.new_customers.sum(), "new_mrr_cop": g.new_mrr_cop.sum(),
                      "total_sm": g.total_sm_spend.sum(), "demand_gen": g.demand_gen_spend.sum(), "paid_media": g.paid_media.sum(),
                      "total_sm_per_new_customer": g.total_sm_spend.sum() / g.new_customers.sum(),
                      "demand_gen_per_new_customer": g.demand_gen_spend.sum() / g.new_customers.sum(),
                      "paid_media_per_new_customer": g.paid_media.sum() / g.new_customers.sum(),
                      "total_sm_per_new_mrr_mm": g.total_sm_spend.sum() / (g.new_mrr_cop.sum() / 1e6),
                      "demand_gen_per_new_mrr_mm": g.demand_gen_spend.sum() / (g.new_mrr_cop.sum() / 1e6),
                      "paid_media_per_new_mrr_mm": g.paid_media.sum() / (g.new_mrr_cop.sum() / 1e6),
                      "avg_monthly_total_sm": g.total_sm_spend.mean(), "avg_monthly_paid_media": g.paid_media.mean(),
                      "avg_monthly_new_customers": g.new_customers.mean(), "avg_monthly_new_mrr_cop": g.new_mrr_cop.mean()})
    ev["efficiency_by_year"] = pd.DataFrame(erows)

    # index series (base = clean 2022 average) for single-axis comparisons
    base_mask = (mm.window_flag == "clean") & (mm.month.str[:4] == "2022")
    idx_series = {}
    for c in ["paid_media", "demand_gen_spend", "total_sm_spend", "sales_capacity_spend", "enablement_spend",
              "new_customers", "new_mrr_cop", "total_paid_mrr_cop", "active_customers"]:
        s = mm[c].astype(float)
        base = s[base_mask].mean()
        idx_series[c] = (100 * s / base).where(mm.window_flag == "clean").tolist()
        s3 = s.rolling(3).mean()
        ok3 = mm.month_index >= cs + 2
        idx_series[c + "_t3m"] = (100 * s3 / base).where(ok3).tolist()
    ev["index_series"] = idx_series
    return ev


# ----------------------------------------------------------------------------------
# 10b · Verified findings (analytical verification, sep-2026)
# ----------------------------------------------------------------------------------
def verification_views(ar: dict, clean_start: int) -> dict:
    """Raw numbers behind the findings confirmed in the verification phase.

    Everything runs on the exact micro-unit panel; each block states its definition and window. The sensitivity
    tests (thresholds, bases, tolerances, horizons, windows) are in docs/evidence_pack.py.
    """
    A, first, eb = ar["A"], ar["first_idx"], ar["ever_before"]
    n, T = A.shape
    months = [str(m) for m in ar["months"]]
    yr = np.array([m[:4] for m in months])
    cop = A * (SCALE_TO_COP / MICRO)
    years = ("2022", "2023", "2024")
    flow_months = {y: sum(1 for t in range(clean_start, T) if yr[t] == y) for y in years}
    V = {}

    # 1 · new customers by entry level. Early run-rate = median of the positive amounts in M0-M2
    #     (robust to first-month spikes and one-month gaps); cut = 2022 median (splits 2022 in half).
    ids = np.where(first >= clean_start)[0]
    rr = np.array([np.median(seg[seg > 0]) for seg in (cop[i, first[i]:first[i] + 3] for i in ids)])
    cy = yr[first[ids]]
    med22 = float(np.median(rr[cy == "2022"]))
    V["adq_rr_median_2022"] = med22
    for y in years:
        V[f"adq_above_{y}"] = float(((rr >= med22) & (cy == y)).sum() / flow_months[y])
        V[f"adq_below_{y}"] = float(((rr < med22) & (cy == y)).sum() / flow_months[y])
    increase = (V["adq_above_2024"] + V["adq_below_2024"]) - (V["adq_above_2022"] + V["adq_below_2022"])
    V["adq_below_share_increase"] = (V["adq_below_2024"] - V["adq_below_2022"]) / increase

    # 2 · value incorporated per month under three normalizations vs the number of new customers
    def per_month(values, last_t):
        out = {}
        for y in years:
            ts = [t for t in range(clean_start, last_t + 1) if yr[t] == y]
            out[y] = values[np.isin(first[ids], ts)].sum() / len(ts)
        return out
    m13 = np.array([np.median(seg[seg > 0]) if (seg > 0).any() else 0.0
                    for seg in (cop[i, first[i] + 1:first[i] + 4] for i in ids)])      # M1-M3, excludes M0
    vals = {"rr": per_month(rr, T - 1), "usual": per_month(ar["usual"][ids] * (SCALE_TO_COP / MICRO), T - 1),
            "m1to3": per_month(m13, T - 4)}                                           # M3 observable: until jul-24
    cnt = per_month(np.ones(ids.size), T - 1)
    V["cnt_22_24"], V["cnt_23_24"] = cnt["2024"] / cnt["2022"] - 1, cnt["2024"] / cnt["2023"] - 1
    for k, d in vals.items():
        V[f"val_{k}_22_24"], V[f"val_{k}_23_24"] = d["2024"] / d["2022"] - 1, d["2024"] / d["2023"] - 1

    # 3 · growth accounting ene-22 -> oct-24: customers active in ene-22 vs everyone who started later
    base = first == 0
    V["ga_total_start"], V["ga_total_end"] = float(cop[:, 0].sum()), float(cop[:, -1].sum())
    V["ga_base_end"], V["ga_new_end"] = float(cop[base, -1].sum()), float(cop[~base, -1].sum())
    surv = base & (A[:, -1] > 0)
    V["ga_base_survivors"] = float(surv.sum() / base.sum())
    V["ga_base_survivor_ratio"] = float(cop[surv, -1].sum() / cop[surv, 0].sum())

    # 4 · one-month round trips: movement at t (no new customers) whose level returns exactly to t-1 in t+1,
    #     or that is the return leg of such a deviation. Window mar-22..sep-24 (t+1 observable).
    gross = rt = 0.0
    for t in range(clean_start, T - 1):
        a0, a1 = A[:, t - 1], A[:, t]
        mv = (a0 != a1) & ((a0 > 0) | eb[:, t])
        v = np.abs(a1 - a0) * (SCALE_TO_COP / MICRO)
        back = A[:, t + 1] == a0
        leg2 = ((A[:, t] == A[:, t - 2]) & (A[:, t - 1] != A[:, t - 2])) if t - 1 >= clean_start else np.zeros(n, bool)
        gross += v[mv].sum()
        rt += v[mv & (back | leg2)].sum()
    V["rt_gross"], V["rt_share"] = float(gross), float(rt / gross)

    # 5 · observed vs durable churn (no payment in the next 3 months); events with 3 months of future only
    h = 3
    for y in years:
        ts = [t for t in range(clean_start, T - h) if yr[t] == y]
        den = sum(int((A[:, t - 1] > 0).sum()) for t in ts)
        evs = dur = 0
        for t in ts:
            c = (A[:, t - 1] > 0) & (A[:, t] == 0)
            evs += int(c.sum())
            dur += int((c & ~(A[:, t + 1:t + 1 + h] > 0).any(axis=1)).sum())
        V[f"churn_obs_{y}"], V[f"churn_dur3_{y}"] = evs / den, dur / den

    # 6 · returns that settle exactly the unpaid months: back after g months paying (g + 1) x the prior amount
    returns = settle = 0
    per_month_churn = []
    for t in range(clean_start, T):
        c = np.flatnonzero((A[:, t - 1] > 0) & (A[:, t] == 0))
        per_month_churn.append(c.size)
        for i in c:
            nxt = np.flatnonzero(A[i, t + 1:] > 0)
            if nxt.size == 0:
                continue
            g = int(nxt[0]) + 1
            returns += 1
            settle += abs(int(A[i, t + g]) - (g + 1) * int(A[i, t - 1])) <= 0.01 * (g + 1) * int(A[i, t - 1])
    V["catchup_n"], V["catchup_returns"], V["catchup_share"] = returns, int(settle), settle / returns
    tj = months.index("2022-06")
    cj = (A[:, tj - 1] > 0) & (A[:, tj] == 0)
    V["jun22_churn"], V["churn_month_median"] = int(cj.sum()), float(np.median(per_month_churn))
    V["jun22_back_next"] = float((A[cj, tj + 1] > 0).mean())

    # 7 · synchronized adjustments with exact retroactive billing: the amount rises k·x (k = 2..6) and the
    #     next month settles at +x, which then persists (tolerance 0.05 pp per step)
    events, custs = 0, set()
    up = {y: 0.0 for y in years}
    net = {y: 0.0 for y in years}
    for t in range(clean_start, T - 1):
        p, a, nx = A[:, t - 1].astype(float), A[:, t].astype(float), A[:, t + 1].astype(float)
        ok = (p > 0) & (a > 0) & (nx > 0) & (a != p)
        persists = (A[:, t + 2] == A[:, t + 1]) if t + 2 < T else np.ones(n, bool)
        hit = np.zeros(n, bool)
        with np.errstate(divide="ignore", invalid="ignore"):
            r1, r2 = a / p - 1, nx / p - 1
            for k in (2, 3, 4, 5, 6):
                hit |= ok & persists & (r2 >= 0.001) & (np.abs(r1 - k * r2) <= 0.0005 * k)
        events += int(hit.sum())
        custs.update(np.flatnonzero(hit).tolist())
        up[yr[t]] += float(((a - p)[hit]).sum()) * (SCALE_TO_COP / MICRO)
        net[yr[t]] += float(((nx - p)[hit]).sum()) * (SCALE_TO_COP / MICRO)
    V["retro_events"], V["retro_customers"] = events, len(custs)
    for y in ("2023", "2024"):
        exp_y = ar["exp_mrr"][:, [t for t in range(clean_start, T) if yr[t] == y]].sum()
        V[f"retro_exp_share_{y}"], V[f"retro_net_{y}"] = up[y] / exp_y, net[y]

    # 8 · 2023 cohorts: logo retention at M12 below vs above the 2022 median (cohorts with M13 observable)
    sel = (cy == "2023") & (first[ids] + 13 <= T - 1)
    act12 = np.array([A[i, first[i] + 12] > 0 for i in ids[sel]])
    low = rr[sel] < med22
    V["ret12_low_2023"], V["ret12_high_2023"] = float(act12[low].mean()), float(act12[~low].mean())
    V["ret12_n_low"], V["ret12_n_high"] = int(low.sum()), int((~low).sum())

    # 9 · acquisition plateau: monthly new customers since ene-23, OLS slope with 95% interval
    ts = [t for t in range(clean_start, T) if yr[t] >= "2023"]
    y_ = np.array([(first == t).sum() for t in ts], dtype=float)
    X = np.c_[np.ones(len(ts)), np.arange(len(ts), dtype=float)]
    b = np.linalg.lstsq(X, y_, rcond=None)[0]
    res = y_ - X @ b
    se = float(np.sqrt(res @ res / (len(ts) - 2) * np.linalg.inv(X.T @ X)[1, 1]))
    V["plateau_slope"], V["plateau_lo"], V["plateau_hi"] = float(b[1]), float(b[1] - 1.96 * se), float(b[1] + 1.96 * se)
    V["new_2022_pm"] = float(((first >= clean_start) & (yr[first] == "2022")).sum() / flow_months["2022"])
    V["new_2324_pm"] = float(y_.mean())
    return V


# ----------------------------------------------------------------------------------
# 11 · Facts (formatted numbers used in the HTML/notes) and verified claims
# ----------------------------------------------------------------------------------
def build_facts(ctx: dict):
    ar, mm, au, ev, dec, coh, mov, corr = (ctx[k] for k in ["ar", "mm", "audit", "ev", "dec", "coh", "mov", "corr"])
    months = ar["months"]
    T = len(months)
    first, last = mm.iloc[0], mm.iloc[-1]
    clean = mm[mm.window_flag == "clean"]
    yr = clean.month.str[:4]
    R = {}   # raw numbers (for claims)
    F = {}   # formatted strings

    def put(key, raw, text):
        R[key] = raw
        F[key] = text

    at, ai, asm = au["transactions"], au["industry"], au["sm"]
    put("n_customers", at["customers"], fmt_int(at["customers"]))
    put("n_months", at["months"], str(at["months"]))
    put("n_rows_tx", at["rows"], fmt_int(at["rows"]))
    put("window_start", str(months[0]), month_label(months[0]))
    put("window_end", str(months[-1]), month_label(months[-1]))
    put("n_industries", ai["n_industries"], str(ai["n_industries"]))
    put("ind_rows_read", ai["rows_read"], fmt_int(ai["rows_read"]))
    put("ind_blank_rows", ai["blank_rows"], str(ai["blank_rows"]))
    put("ind_valid", ai["rows_valid"], fmt_int(ai["rows_valid"]))
    put("id_match_rate", au["consistency"]["id_match_rate"], fmt_pct(au["consistency"]["id_match_rate"], 0))
    put("zero_share", at["zero_share"], fmt_pct(at["zero_share"]))
    put("zero_rows", at["zero_amount_rows"], fmt_int(at["zero_amount_rows"]))
    put("pos_rows", at["positive_amount_rows"], fmt_int(at["positive_amount_rows"]))
    put("amount_min_cop", at["amount_min_positive"] * SCALE_TO_COP, fmt_cop(at["amount_min_positive"] * SCALE_TO_COP, 1))
    put("amount_max_cop", at["amount_max"] * SCALE_TO_COP, fmt_cop(at["amount_max"] * SCALE_TO_COP, 2))
    put("amount_p50_cop", at["amount_p50_positive"] * SCALE_TO_COP, fmt_cop(at["amount_p50_positive"] * SCALE_TO_COP, 1))
    put("amount_p99_cop", at["amount_p99_positive"] * SCALE_TO_COP, fmt_cop(at["amount_p99_positive"] * SCALE_TO_COP, 1))
    put("iqr_fence_cop", at["iqr_fence_q3_plus_3iqr"] * SCALE_TO_COP, fmt_cop(at["iqr_fence_q3_plus_3iqr"] * SCALE_TO_COP, 1))
    put("rows_above_fence", at["rows_above_iqr_fence"], fmt_int(at["rows_above_iqr_fence"]))
    put("customers_above_fence", at["customers_above_iqr_fence"], fmt_int(at["customers_above_iqr_fence"]))
    put("rows_6_decimals", at["decimal_places"].get("6", 0), fmt_int(at["decimal_places"].get("6", 0)))

    # growth
    put("active_start", int(first.active_customers), fmt_int(first.active_customers))
    put("active_end", int(last.active_customers), fmt_int(last.active_customers))
    put("active_multiple", last.active_customers / first.active_customers, fmt_x(last.active_customers / first.active_customers))
    put("mrr_start", first.total_paid_mrr_cop, fmt_cop(first.total_paid_mrr_cop))
    put("mrr_end", last.total_paid_mrr_cop, fmt_cop(last.total_paid_mrr_cop))
    put("mrr_multiple", last.total_paid_mrr_cop / first.total_paid_mrr_cop, fmt_x(last.total_paid_mrr_cop / first.total_paid_mrr_cop))
    arpa_chg = last.mrr_per_active_customer_cop / first.mrr_per_active_customer_cop - 1
    put("arpa_start", first.mrr_per_active_customer_cop, fmt_cop(first.mrr_per_active_customer_cop))
    put("arpa_end", last.mrr_per_active_customer_cop, fmt_cop(last.mrr_per_active_customer_cop))
    put("arpa_change", arpa_chg, fmt_pct(arpa_chg, 0))
    put("arpa_change_abs", -arpa_chg, fmt_pct(-arpa_chg, 0))
    nm = mm.iloc[1:]
    neg = nm[nm.net_customer_adds < 0]
    put("net_adds_negative_months", len(neg), str(len(neg)))
    put("net_adds_negative_list", ", ".join(month_label(pd.Period(m)) for m in neg.month), ", ".join(month_label(pd.Period(m)) for m in neg.month))
    put("net_adds_positive_months", int((nm.net_customer_adds > 0).sum()), str(int((nm.net_customer_adds > 0).sum())))
    put("months_with_flows", len(nm), str(len(nm)))
    for y in ["2022", "2023", "2024"]:
        g = clean[yr == y]
        put(f"new_avg_{y}", g.new_customers.mean(), fmt_int(g.new_customers.mean()))
        put(f"new_mrr_avg_{y}", g.new_mrr_cop.mean(), fmt_cop(g.new_mrr_cop.mean()))
        put(f"churn_rate_{y}", g.churned_customers.sum() / mm.active_customers.shift(1)[g.index].sum(),
            fmt_pct(g.churned_customers.sum() / mm.active_customers.shift(1)[g.index].sum()))
        put(f"sm_avg_{y}", g.total_sm_spend.mean(), fmt_u(g.total_sm_spend.mean(), 2))
        put(f"pm_avg_{y}", g.paid_media.mean(), fmt_u(g.paid_media.mean(), 2))
        put(f"netadds_avg_{y}", g.net_customer_adds.mean(), fmt_int(g.net_customer_adds.mean()))
    put("new_growth_multiple", R["new_avg_2024"] / R["new_avg_2022"], fmt_x(R["new_avg_2024"] / R["new_avg_2022"]))
    jun = mm[mm.month == "2022-06"].iloc[0]
    may = mm[mm.month == "2022-05"].iloc[0]
    put("mrr_jun22_change", jun.total_paid_mrr_cop / may.total_paid_mrr_cop - 1,
        fmt_pct(jun.total_paid_mrr_cop / may.total_paid_mrr_cop - 1, 0))
    mom = mm.total_paid_mrr_cop.pct_change().iloc[1:]
    put("mrr_mom_negative_months", int((mom < 0).sum()), str(int((mom < 0).sum())))

    # ticket
    tb = ev["ticket_by_year"].set_index("year")
    for y in [2022, 2023, 2024]:
        r = tb.loc[y]
        put(f"m0_mean_{y}", r.m0_mean_cop, fmt_cop(r.m0_mean_cop))
        put(f"m0_median_{y}", r.m0_median_cop, fmt_cop(r.m0_median_cop))
        put(f"m0_winsor_{y}", r.m0_winsor_mean_cop, fmt_cop(r.m0_winsor_mean_cop))
        put(f"err_mean_{y}", r.early_run_rate_mean_cop, fmt_cop(r.early_run_rate_mean_cop))
        put(f"m1_mean_{y}", r.m1_mean_cop, fmt_cop(r.m1_mean_cop))
        put(f"spike_share_{y}", r.share_first_month_spike, fmt_pct(r.share_first_month_spike, 0))
        put(f"new_n_{y}", int(r.new_customers), fmt_int(r.new_customers))
    for key, col in [("m0_mean", "m0_mean_cop"), ("m0_median", "m0_median_cop"), ("err_mean", "early_run_rate_mean_cop"),
                     ("m1_mean", "m1_mean_cop"), ("m0_winsor", "m0_winsor_mean_cop")]:
        ch = tb.loc[2024, col] / tb.loc[2022, col] - 1
        put(f"{key}_chg_22_24", ch, fmt_pct(ch, 0))
    va = ev["vintage_arpa"]
    def varpa(v, m):
        return float(va[(va.vintage == v) & (va.month == m)].arpa_cop.iloc[0])
    put("base_arpa_start", varpa(VINT_BASE, str(months[0])), fmt_cop(varpa(VINT_BASE, str(months[0]))))
    put("base_arpa_end", varpa(VINT_BASE, str(months[-1])), fmt_cop(varpa(VINT_BASE, str(months[-1]))))
    put("base_arpa_change", R["base_arpa_end"] / R["base_arpa_start"] - 1, fmt_pct_signed(R["base_arpa_end"] / R["base_arpa_start"] - 1, 0))
    for v, k in [(VINT_2022, "v2022"), (VINT_2023, "v2023"), (VINT_2024, "v2024")]:
        put(f"{k}_arpa_end", varpa(v, str(months[-1])), fmt_cop(varpa(v, str(months[-1]))))
    oct_ = va[va.month == str(months[-1])].set_index("vintage")
    recent = oct_.loc[[VINT_2023, VINT_2024]]
    put("recent_vintage_customer_share", recent.active_customers.sum() / oct_.active_customers.sum(),
        fmt_pct(recent.active_customers.sum() / oct_.active_customers.sum(), 0))
    put("recent_vintage_mrr_share", recent.mrr_cop.sum() / oct_.mrr_cop.sum(), fmt_pct(recent.mrr_cop.sum() / oct_.mrr_cop.sum(), 0))
    # first month from which EVERY later monthly median entry ticket stays below the 2022 pooled median
    med22 = R["m0_median_2022"]
    mmed = mm.loc[mm.window_flag == "clean", ["month", "median_new_customer_mrr_cop"]].reset_index(drop=True)
    below = (mmed.median_new_customer_mrr_cop < med22).to_numpy()
    step = next(i for i in range(len(below)) if below[i:].all())
    put("step_month", mmed.month[step], month_label(pd.Period(mmed.month[step])))
    put("step_prev_month", mmed.month[step - 1], month_label(pd.Period(mmed.month[step - 1])))

    # data quality evidence
    se = ctx["sig_entry"]
    feb = se[se.cohort == str(months[1])].iloc[0]
    later = se[se.cohort != str(months[1])]
    put("feb_new", int(feb.new_customers), fmt_int(feb.new_customers))
    put("feb_sig_n", int(feb.first_amount_2x_next), str(int(feb.first_amount_2x_next)))
    put("feb_sig_share", feb.share, fmt_pct(feb.share, 0))
    put("later_sig_share", later.first_amount_2x_next.sum() / later.new_customers.sum(),
        fmt_pct(later.first_amount_2x_next.sum() / later.new_customers.sum(), 1))
    put("feb_vs_typical_new", feb.new_customers / clean[yr == "2022"].new_customers.mean(),
        fmt_x(feb.new_customers / clean[yr == "2022"].new_customers.mean()))
    put("multi_sig_rows", mov["multi_month_signatures"], fmt_int(mov["multi_month_signatures"]))
    put("multi_sig_customers", mov["multi_month_signature_customers"], fmt_int(mov["multi_month_signature_customers"]))
    put("churn_events", mov["n_churn_events"], fmt_int(mov["n_churn_events"]))
    put("churn_back_1m", mov["share_return_1m"], fmt_pct(mov["share_return_1m"], 0))
    put("churn_back_1m_excl_last", mov["share_return_1m_excl_last_month"], fmt_pct(mov["share_return_1m_excl_last_month"], 0))
    put("churn_back_any", mov["share_return_any"], fmt_pct(mov["share_return_any"], 0))
    put("churn_mrr_back_1m", mov["share_churned_mrr_back_1m"], fmt_pct(mov["share_churned_mrr_back_1m"], 0))
    put("exp_mrr_revert", mov["share_expansion_mrr_reverting_1m"], fmt_pct(mov["share_expansion_mrr_reverting_1m"], 0))
    put("exp_events_revert", mov["share_expansion_events_reverting_1m"], fmt_pct(mov["share_expansion_events_reverting_1m"], 0))
    put("con_mrr_post_spike", mov["share_contraction_mrr_post_spike"], fmt_pct(mov["share_contraction_mrr_post_spike"], 0))
    put("con_events_revert", mov["share_contraction_events_reverting_1m"], fmt_pct(mov["share_contraction_events_reverting_1m"], 1))
    put("gross_movement", mov["gross_movement_cop"], fmt_cop(mov["gross_movement_cop"], 0))
    put("net_movement", mov["net_movement_cop"], fmt_cop(mov["net_movement_cop"], 0))
    put("gross_net_ratio", mov["gross_movement_cop"] / mov["net_movement_cop"], fmt_x(mov["gross_movement_cop"] / mov["net_movement_cop"]))
    sa = mov["small_adjustments"].set_index("half")
    h0, h1 = sa.index[0], sa.index[-1]
    put("small_exp_first", sa.loc[h0, "expansion_small_share"], fmt_pct(sa.loc[h0, "expansion_small_share"], 0))
    put("small_exp_last", sa.loc[h1, "expansion_small_share"], fmt_pct(sa.loc[h1, "expansion_small_share"], 0))
    put("small_con_first", sa.loc[h0, "contraction_small_share"], fmt_pct(sa.loc[h0, "contraction_small_share"], 0))
    put("small_con_last", sa.loc[h1, "contraction_small_share"], fmt_pct(sa.loc[h1, "contraction_small_share"], 0))
    put("small_half_first", h0, h0)
    put("small_half_last", h1, h1)
    gh = mov["grid_share_half"]
    put("grid_2022h2", gh["2022 S2"], fmt_pct(gh["2022 S2"], 0))
    put("grid_2024h2", gh["2024 S2"], fmt_pct(gh["2024 S2"], 0))
    put("offgrid_2022s2", 1 - gh["2022 S2"], fmt_pct(1 - gh["2022 S2"], 0))
    put("offgrid_2024s2", 1 - gh["2024 S2"], fmt_pct(1 - gh["2024 S2"], 0))
    put("grid_last", mov["grid_share_monthly"][-1], fmt_pct(mov["grid_share_monthly"][-1], 0))

    # S&M
    s = ctx["mm"]
    comp = asm["components"]
    put("team_fixed_months", asm["team_share_fixed_12pct_months"], str(asm["team_share_fixed_12pct_months"]))
    put("team_fixed_until", asm["team_share_fixed_until"], month_label(pd.Period(asm["team_share_fixed_until"])))
    put("team_break", asm["team_share_first_break"], month_label(pd.Period(asm["team_share_first_break"])))
    fz = comp["Freelance"]["zero_months"]
    put("freelance_zero_from", fz[0], month_label(pd.Period(fz[0])))
    put("freelance_zero_n", len(fz), str(len(fz)))
    after = [str(m) for m in months if str(m) >= fz[0]]
    exceptions = [m for m in after if m not in fz]
    put("freelance_months_since", len(after), str(len(after)))
    put("freelance_exceptions", ", ".join(month_label(pd.Period(m)) for m in exceptions) or "ninguna",
        ", ".join(month_label(pd.Period(m)) for m in exceptions) or "ninguna")
    pn = comp["PayrollExpenses"]["negative_months"]
    put("payroll_neg_n", len(pn), str(len(pn)))
    put("payroll_neg_list", ", ".join(month_label(pd.Period(m)) for m in pn), ", ".join(month_label(pd.Period(m)) for m in pn))
    put("whole_pct_months", asm["whole_percent_share_months"], str(asm["whole_percent_share_months"]))
    peak_i = int(s.loc[s.month.str[:4] == "2023", "total_sm_spend"].idxmax())
    trough_i = int(s.loc[(s.index > peak_i) & (s.month <= "2023-12"), "total_sm_spend"].idxmin())
    put("sm_peak_month", s.month[peak_i], month_label(pd.Period(s.month[peak_i])))
    put("sm_trough_month", s.month[trough_i], month_label(pd.Period(s.month[trough_i])))
    put("sm_peak", s.total_sm_spend[peak_i], fmt_u(s.total_sm_spend[peak_i], 2))
    put("sm_trough", s.total_sm_spend[trough_i], fmt_u(s.total_sm_spend[trough_i], 2))
    put("sm_drop", s.total_sm_spend[trough_i] / s.total_sm_spend[peak_i] - 1,
        fmt_pct(s.total_sm_spend[trough_i] / s.total_sm_spend[peak_i] - 1, 0))
    pm_peak_i = int(s.loc[s.month.str[:4] == "2023", "paid_media"].idxmax())
    pm_trough_i = int(s.loc[(s.index > pm_peak_i) & (s.month <= "2023-12"), "paid_media"].idxmin())
    put("pm_drop", s.paid_media[pm_trough_i] / s.paid_media[pm_peak_i] - 1,
        fmt_pct(s.paid_media[pm_trough_i] / s.paid_media[pm_peak_i] - 1, 0))
    put("pm_trough_month", s.month[pm_trough_i], month_label(pd.Period(s.month[pm_trough_i])))
    put("sm_chg_22_24", R["sm_avg_2024"] / R["sm_avg_2022"] - 1, fmt_pct(R["sm_avg_2024"] / R["sm_avg_2022"] - 1, 0))
    eb = ev["efficiency_by_year"].set_index("year")
    for y in [2022, 2023, 2024]:
        put(f"cac_sm_{y}", eb.loc[y, "total_sm_per_new_customer"], fmt_u(eb.loc[y, "total_sm_per_new_customer"], 3))
        put(f"cac_dg_{y}", eb.loc[y, "demand_gen_per_new_customer"], fmt_u(eb.loc[y, "demand_gen_per_new_customer"], 3))
        put(f"cac_pm_{y}", eb.loc[y, "paid_media_per_new_customer"], fmt_u(eb.loc[y, "paid_media_per_new_customer"], 3))
        put(f"sm_per_mrr_{y}", eb.loc[y, "total_sm_per_new_mrr_mm"], fmt_u(eb.loc[y, "total_sm_per_new_mrr_mm"], 2))
    for k in ["total_sm_per_new_customer", "total_sm_per_new_mrr_mm", "paid_media_per_new_customer", "paid_media_per_new_mrr_mm",
              "demand_gen_per_new_customer", "demand_gen_per_new_mrr_mm"]:
        ch = eb.loc[2024, k] / eb.loc[2022, k] - 1
        put(f"{k}_chg", ch, fmt_pct(ch, 0))

    # relationships
    lv = corr[(corr["transform"] == "levels") & (corr.outcome == "Altas") & (corr.lag_months == 0)].set_index("spend")
    for sname, key in [("Paid Media", "pm"), ("Generación de demanda", "dg"), ("S&M total", "sm")]:
        put(f"r_new_{key}_l0", lv.loc[sname, "pearson_r"], fmt_r(lv.loc[sname, "pearson_r"]))
    lvl_new = corr[(corr["transform"] == "levels") & (corr.outcome == "Altas")]
    lvl_mrr = corr[(corr["transform"] == "levels") & (corr.outcome == "MRR nuevo")]
    mom = corr[corr["transform"] == "mom_change"]
    put("r_new_levels_min", lvl_new.pearson_r.min(), fmt_r(lvl_new.pearson_r.min()))
    put("r_new_levels_max", lvl_new.pearson_r.max(), fmt_r(lvl_new.pearson_r.max()))
    put("r_mrr_levels_absmax", lvl_mrr.pearson_r.abs().max(), fmt_num(lvl_mrr.pearson_r.abs().max(), 2))
    put("r_mom_absmax", mom.pearson_r.abs().max(), fmt_num(mom.pearson_r.abs().max(), 2))
    put("r_mom_minp", mom.pearson_p.min(), fmt_num(mom.pearson_p.min(), 2))
    put("corr_n_levels", int(corr[corr["transform"] == "levels"].n.max()), str(int(corr[corr["transform"] == "levels"].n.max())))
    put("corr_n_min", int(corr.n.min()), str(int(corr.n.min())))

    # industries
    iy = ctx["iyear"]
    def iv(y, ind, col):
        return float(iy[(iy.year == y) & (iy.industry == ind)][col].iloc[0])
    put("retail_new_share_2022", iv(2022, "Retail", "share_new_customers"), fmt_pct(iv(2022, "Retail", "share_new_customers"), 0))
    put("retail_new_share_2023", iv(2023, "Retail", "share_new_customers"), fmt_pct(iv(2023, "Retail", "share_new_customers"), 0))
    put("retail_new_share_2024", iv(2024, "Retail", "share_new_customers"), fmt_pct(iv(2024, "Retail", "share_new_customers"), 0))
    put("retail_ticket_2024", iv(2024, "Retail", "new_mrr_per_new_customer_cop"), fmt_cop(iv(2024, "Retail", "new_mrr_per_new_customer_cop")))
    put("rest_mrr_share_2022", iv(2022, "Restaurantes", "share_mrr_end"), fmt_pct(iv(2022, "Restaurantes", "share_mrr_end"), 0))
    put("rest_mrr_share_2024", iv(2024, "Restaurantes", "share_mrr_end"), fmt_pct(iv(2024, "Restaurantes", "share_mrr_end"), 0))
    put("retail_active_share_2022", iv(2022, "Retail", "share_active_end"), fmt_pct(iv(2022, "Retail", "share_active_end"), 1))
    put("retail_active_share_2024", iv(2024, "Retail", "share_active_end"), fmt_pct(iv(2024, "Retail", "share_active_end"), 1))
    rp = [iv(y, "Restaurantes", "share_new_mrr") + iv(y, "Producción", "share_new_mrr") for y in (2022, 2023, 2024)]
    put("restprod_new_mrr_min", min(rp), fmt_pct(min(rp), 0))
    R["rest_is_top_mrr_2024"] = iy[iy.year == 2024].sort_values("share_mrr_end").industry.iloc[-1] == "Restaurantes"
    arpa_end = iy.pivot(index="industry", columns="year", values="arpa_end_cop")
    R["industries_arpa_fell"] = int((arpa_end[2024] < arpa_end[2022]).sum())
    F["industries_arpa_fell"] = str(R["industries_arpa_fell"])
    tick = iy.pivot(index="industry", columns="year", values="new_mrr_per_new_customer_cop")
    R["industries_ticket_fell_22_24"] = int((tick[2024] < tick[2022]).sum())
    F["industries_ticket_fell_22_24"] = str(R["industries_ticket_fell_22_24"])
    med = dec["medians"]
    R["industries_median_fell_22_24"] = int((med.loc[2024] < med.loc[2022]).sum())
    F["industries_median_fell_22_24"] = str(R["industries_median_fell_22_24"])
    R["industries_median_fell_22_23"] = int((med.loc[2023] < med.loc[2022]).sum())
    F["industries_median_fell_22_23"] = str(R["industries_median_fell_22_23"])

    # decomposition
    d = dec["main"]["2022_2024"]
    put("dec_a0", d["A0"], fmt_cop(d["A0"]))
    put("dec_a1", d["A1"], fmt_cop(d["A1"]))
    put("dec_delta", d["delta"], fmt_cop(d["delta"]))
    put("dec_delta_pct", d["delta"] / d["A0"], fmt_pct(d["delta"] / d["A0"], 0))
    put("dec_mix", d["mix"], fmt_cop(d["mix"]))
    put("dec_within", d["within"], fmt_cop(d["within"]))
    put("dec_within_share", d["within_share"], fmt_pct(d["within_share"], 0))
    put("dec_mix_share", d["mix_share"], fmt_pct(d["mix_share"], 0))
    put("dec_within_ci", (d["within_share_ci90_lo"], d["within_share_ci90_hi"]),
        f"{d['within_share_ci90_lo'] * 100:.0f}–{d['within_share_ci90_hi'] * 100:.0f}%")
    put("dec_cf", d["counterfactual_A1_at_base_mix"], fmt_cop(d["counterfactual_A1_at_base_mix"]))
    rb = dec["robust"]
    r24 = rb[rb.comparison == "2022 vs 2024"]
    put("dec_within_share_min", r24.within_share.min(), fmt_pct(r24.within_share.min(), 0))
    put("dec_within_share_max", r24.within_share.max(), fmt_pct(r24.within_share.max(), 0))
    d23 = dec["main"]["2022_2023"]
    put("dec23_within_share", d23["within_share"], fmt_pct(d23["within_share"], 0))
    d34 = dec["main"]["2023_2024"]
    put("dec34_delta", d34["delta"], fmt_cop(d34["delta"]))
    put("dec34_ci", (d34["within_ci90_lo"], d34["within_ci90_hi"]),
        f"{fmt_cop(d34['within_ci90_lo'])} a {fmt_cop(d34['within_ci90_hi'])}")
    put("dec_n0", d["n0"], fmt_int(d["n0"]))
    put("dec_n1", d["n1"], fmt_int(d["n1"]))
    put("winsor_cap", dec["winsor_cap_cop"], fmt_cop(dec["winsor_cap_cop"]))
    evo = dec["evolution"].set_index("half")
    put("evo_2022h2", evo.loc["2022 S2", "mean_m0_cop"], fmt_cop(evo.loc["2022 S2", "mean_m0_cop"]))
    put("evo_2023h1", evo.loc["2023 S1", "mean_m0_cop"], fmt_cop(evo.loc["2023 S1", "mean_m0_cop"]))

    # cohorts
    sq = coh["summary"].set_index("cohort")
    q22 = [q for q in sq.index if q.startswith("2022") and not sq.loc[q, "partial"]]
    q2324 = [q for q in sq.index if (q.startswith("2023") or q.startswith("2024")) and pd.notna(sq.loc[q, "logo_m1"]) and not sq.loc[q, "partial"]]
    put("m1_logo_2022_min", sq.loc[q22, "logo_m1"].min(), fmt_pct(sq.loc[q22, "logo_m1"].min(), 0))
    put("m1_logo_2022_max", sq.loc[q22, "logo_m1"].max(), fmt_pct(sq.loc[q22, "logo_m1"].max(), 0))
    put("m1_logo_recent_min", sq.loc[q2324, "logo_m1"].min(), fmt_pct(sq.loc[q2324, "logo_m1"].min(), 0))
    put("m1_logo_recent_max", sq.loc[q2324, "logo_m1"].max(), fmt_pct(sq.loc[q2324, "logo_m1"].max(), 0))
    q12 = [q for q in sq.index if pd.notna(sq.loc[q, "logo_m12"]) and sq.loc[q, "observable_m12"] >= 0.9 * sq.loc[q, "size"] and not sq.loc[q, "partial"]]
    put("m12_logo_min", sq.loc[q12, "logo_m12"].min(), fmt_pct(sq.loc[q12, "logo_m12"].min(), 0))
    put("m12_logo_max", sq.loc[q12, "logo_m12"].max(), fmt_pct(sq.loc[q12, "logo_m12"].max(), 0))
    put("rev_m1_2022_max", sq.loc[q22, "revenue_m1"].max(), fmt_pct(sq.loc[q22, "revenue_m1"].max(), 0))
    put("rev_m1_recent_min", sq.loc[q2324, "revenue_m1"].min(), fmt_pct(sq.loc[q2324, "revenue_m1"].min(), 0))
    base = coh["flagged"]["left_censored_base"]
    put("base_size", base["size"], fmt_int(base["size"]))
    put("base_logo_end", base["logo_calendar"][-1], fmt_pct(base["logo_calendar"][-1], 0))
    put("base_rev_end", base["revenue_calendar"][-1], fmt_pct(base["revenue_calendar"][-1], 0))

    # bridge
    lb = ev["last_bridge"]
    put("lb_from", lb["from_month"], month_label(pd.Period(lb["from_month"])))
    put("lb_to", lb["to_month"], month_label(pd.Period(lb["to_month"])))
    for k in ["opening_mrr_cop", "closing_mrr_cop", "new_mrr_cop", "expansion_mrr_cop", "reactivation_mrr_cop",
              "contraction_mrr_cop", "churned_mrr_cop", "net_change_cop"]:
        put(f"lb_{k}", lb[k], fmt_cop(lb[k]))
    put("lb_check", lb["check_diff_cop"], fmt_num(abs(lb["check_diff_cop"]), 2))
    put("bridge_max_diff", float(mm.mrr_bridge_diff_cop.iloc[1:].abs().max()), fmt_num(mm.mrr_bridge_diff_cop.iloc[1:].abs().max(), 2))
    ab = ev["annual_bridge"].set_index("year")
    for y in [2022, 2023, 2024]:
        put(f"ab_net_{y}", ab.loc[y, "net_change_cop"], fmt_cop(ab.loc[y, "net_change_cop"]))
    import platform, scipy
    put("py_version", platform.python_version(), platform.python_version())
    put("pandas_version", pd.__version__, pd.__version__)
    put("numpy_version", np.__version__, np.__version__)
    put("scipy_version", scipy.__version__, scipy.__version__)
    for k, key in [("transactions", "hash_tx"), ("industry", "hash_ind"), ("sm", "hash_sm")]:
        put(key, ctx["raw"][k]["sha256"], ctx["raw"][k]["sha256"])
    n_corr = len(corr)
    put("n_corr_tests", n_corr, str(n_corr))
    put("n_corr_false_pos", n_corr * 0.05, fmt_num(n_corr * 0.05, 1))
    sig = corr[corr.pearson_p < 0.05]
    put("n_corr_sig", len(sig), str(len(sig)))
    put("n_corr_sig_levels_new", int(((corr["transform"] == "levels") & (corr.outcome == "Altas") & (corr.pearson_p < 0.05)).sum()),
        str(int(((corr["transform"] == "levels") & (corr.outcome == "Altas") & (corr.pearson_p < 0.05)).sum())))
    # largest account by median positive monthly amount
    med_pos = np.array([np.median(ar["cur_cop"][i][ar["pos"][i]]) for i in range(len(ar["ids"]))])
    ti = int(np.argmax(med_pos))
    put("top_account_id", int(ar["ids"][ti]), str(int(ar["ids"][ti])))
    put("top_account_median", float(med_pos[ti]), fmt_cop(float(med_pos[ti])))
    put("top_account_industry", ar["ind"][ti], ar["ind"][ti])
    put("top_account_x_median", float(med_pos[ti]) / R["amount_p50_cop"], fmt_x(float(med_pos[ti]) / R["amount_p50_cop"], 0))
    ex516 = next(e for e in ev["examples"] if e["id"] == 516)
    put("periodic_amount", ex516["amounts_cop"][[str(m) for m in months].index("2022-04")], fmt_cop(ex516["amounts_cop"][[str(m) for m in months].index("2022-04")], 2))
    for k in ["sm_drop", "pm_drop", "total_sm_per_new_customer_chg", "total_sm_per_new_mrr_mm_chg", "sm_chg_22_24"]:
        put(k + "_abs", abs(R[k]), fmt_pct(abs(R[k]), 0))
    put("lb_contraction_abs", -lb["contraction_mrr_cop"], fmt_cop(-lb["contraction_mrr_cop"]))
    put("lb_churn_abs", -lb["churned_mrr_cop"], fmt_cop(-lb["churned_mrr_cop"]))
    cut_s = s.month[peak_i + 1]
    put("cut_start", cut_s, month_label(pd.Period(cut_s)))
    put("cut_end", "2023-12", month_label(pd.Period("2023-12")))
    for k in ["step_month", "team_break", "cut_start", "cut_end", "team_fixed_until", "sm_peak_month", "sm_trough_month"]:
        F[k + "_ym"] = R[k]

    # verified findings (analytical verification, sep-2026)
    vv = verification_views(ar, ctx["clean_start"])
    put("adq_rr_median_2022", vv["adq_rr_median_2022"], fmt_cop(vv["adq_rr_median_2022"]))
    for y in ("2022", "2023", "2024"):
        put(f"adq_above_{y}", vv[f"adq_above_{y}"], fmt_num(vv[f"adq_above_{y}"], 1))
        put(f"adq_below_{y}", vv[f"adq_below_{y}"], fmt_num(vv[f"adq_below_{y}"], 1))
        put(f"churn_obs_{y}", vv[f"churn_obs_{y}"], fmt_pct(vv[f"churn_obs_{y}"], 2))
        put(f"churn_dur3_{y}", vv[f"churn_dur3_{y}"], fmt_pct(vv[f"churn_dur3_{y}"], 2))
    put("adq_below_share_increase", vv["adq_below_share_increase"], fmt_pct(vv["adq_below_share_increase"], 0))
    for k in ("cnt_22_24", "cnt_23_24", "val_rr_22_24", "val_rr_23_24", "val_usual_22_24", "val_usual_23_24",
              "val_m1to3_22_24", "val_m1to3_23_24"):
        put(k, vv[k], fmt_pct_signed(vv[k], 0))
    for k in ("ga_total_start", "ga_total_end", "ga_base_end", "ga_new_end", "rt_gross"):
        put(k, vv[k], fmt_cop(vv[k]))
    put("ga_base_survivors", vv["ga_base_survivors"], fmt_pct(vv["ga_base_survivors"], 0))
    put("ga_base_survivor_ratio", vv["ga_base_survivor_ratio"], fmt_x(vv["ga_base_survivor_ratio"], 2))
    put("rt_share", vv["rt_share"], fmt_pct(vv["rt_share"], 1))
    for k in ("catchup_n", "catchup_returns", "jun22_churn", "retro_events", "retro_customers", "ret12_n_low", "ret12_n_high"):
        put(k, vv[k], fmt_int(vv[k]))
    put("catchup_share", vv["catchup_share"], fmt_pct(vv["catchup_share"], 0))
    put("churn_month_median", vv["churn_month_median"], fmt_num(vv["churn_month_median"], 0))
    put("jun22_back_next", vv["jun22_back_next"], fmt_pct(vv["jun22_back_next"], 0))
    for y in ("2023", "2024"):
        put(f"retro_exp_share_{y}", vv[f"retro_exp_share_{y}"], fmt_pct(vv[f"retro_exp_share_{y}"], 1))
        put(f"retro_net_{y}", vv[f"retro_net_{y}"], fmt_cop(vv[f"retro_net_{y}"], 2))
    put("ret12_low_2023", vv["ret12_low_2023"], fmt_pct(vv["ret12_low_2023"], 0))
    put("ret12_high_2023", vv["ret12_high_2023"], fmt_pct(vv["ret12_high_2023"], 0))
    put("new_2022_pm", vv["new_2022_pm"], fmt_num(vv["new_2022_pm"], 1))
    put("new_2324_pm", vv["new_2324_pm"], fmt_num(vv["new_2324_pm"], 1))
    for k in ("plateau_slope", "plateau_lo", "plateau_hi"):
        put(k, vv[k], fmt_r(vv[k], 2))
    now = datetime.now()
    put("generated", now.strftime("%Y-%m-%d %H:%M"), f"{now.day} {MESES[now.month - 1]} {now.year}, {now:%H:%M}")
    return F, R


# Qué mide cada cifra citada por una afirmación del registro. Lo usan el agente (search_evidence) y el compositor de
# narrativas para no confundir significados; toda cifra citada debe tener etiqueta (check_claims lo exige).
FACT_LABELS = {
    "active_multiple": "Clientes activos oct-24 / ene-22 (veces)",
    "mrr_multiple": "MRR pagado oct-24 / ene-22 (veces)",
    "arpa_start": "MRR por cliente activo, ene-22",
    "arpa_end": "MRR por cliente activo, oct-24",
    "arpa_change": "Cambio del MRR por cliente activo, ene-22 a oct-24",
    "net_adds_negative_list": "Meses con altas netas negativas",
    "net_adds_positive_months": "Meses con altas netas positivas (de 33)",
    "gross_movement": "Movimiento bruto de MRR del periodo (entradas más salidas)",
    "net_movement": "Cambio neto de MRR del periodo",
    "gross_net_ratio": "Movimiento bruto / cambio neto (veces)",
    "lb_reactivation_mrr_cop": "MRR de reactivación del último mes (oct-24)",
    "lb_new_mrr_cop": "MRR nuevo del último mes (oct-24)",
    "lb_expansion_mrr_cop": "MRR de expansión del último mes (oct-24)",
    "rest_mrr_share_2022": "Participación de Restaurantes en el MRR, dic-22",
    "rest_mrr_share_2024": "Participación de Restaurantes en el MRR, oct-24",
    "retail_active_share_2022": "Participación de Retail en los clientes activos, dic-22",
    "retail_active_share_2024": "Participación de Retail en los clientes activos, oct-24",
    "m0_median_2022": "Mediana del primer pago de las altas, 2022 (mar–dic)",
    "m0_median_2023": "Mediana del primer pago de las altas, 2023",
    "m0_median_2024": "Mediana del primer pago de las altas, 2024 (ene–oct)",
    "m0_mean_chg_22_24": "Cambio del primer pago promedio de las altas, 2022 a 2024",
    "m0_median_chg_22_24": "Cambio de la mediana del primer pago de las altas, 2022 a 2024",
    "m1_mean_chg_22_24": "Cambio del pago promedio del segundo mes (M1) de las altas, 2022 a 2024",
    "step_month": "Mes del escalón del ticket de entrada",
    "dec_within_share": "Parte del cambio del ticket de entrada 2022→2024 que ocurre dentro de las industrias",
    "dec_within_ci": "Intervalo bootstrap de 90% de la parte dentro de las industrias",
    "dec_within_share_min": "Parte dentro de las industrias: mínimo entre variantes",
    "dec_within_share_max": "Parte dentro de las industrias: máximo entre variantes",
    "industries_ticket_fell_22_24": "Industrias donde bajó el ticket de entrada promedio, 2022 a 2024 (de 6)",
    "industries_median_fell_22_24": "Industrias donde bajó la mediana del ticket de entrada, 2022 a 2024 (de 6)",
    "restprod_new_mrr_min": "Participación mínima anual de Restaurantes más Producción en el MRR nuevo",
    "m1_logo_2022_min": "Retención de logos al M1, trimestres de 2022 (mínimo)",
    "m1_logo_2022_max": "Retención de logos al M1, trimestres de 2022 (máximo)",
    "m1_logo_recent_min": "Retención de logos al M1, trimestres completos de 2023–24 (mínimo)",
    "m1_logo_recent_max": "Retención de logos al M1, trimestres completos de 2023–24 (máximo)",
    "churn_back_1m": "Churns observados que vuelven a pagar al mes siguiente",
    "churn_events": "Eventos de churn observado (mar-22 a oct-24)",
    "base_arpa_start": "MRR por cliente de la base previa (activos en ene-22), ene-22",
    "base_arpa_end": "MRR por cliente de la base previa (activos en ene-22), oct-24",
    "base_arpa_change": "Cambio del MRR por cliente de la base previa, ene-22 a oct-24",
    "v2022_arpa_end": "MRR por cliente de la cosecha 2022, oct-24",
    "v2023_arpa_end": "MRR por cliente de la cosecha 2023, oct-24",
    "v2024_arpa_end": "MRR por cliente de la cosecha 2024, oct-24",
    "recent_vintage_customer_share": "Participación de las cosechas 2023–24 en los clientes activos, oct-24",
    "recent_vintage_mrr_share": "Participación de las cosechas 2023–24 en el MRR, oct-24",
    "industries_arpa_fell": "Industrias donde bajó el MRR por cliente activo, dic-22 a oct-24 (de 6)",
    "sm_peak": "S&M total en su pico, may-23 (unidad reportada, sin escala en COP)",
    "sm_trough": "S&M total en su valle, ago-23 (unidad reportada)",
    "sm_drop": "Caída del S&M total de pico a valle",
    "cac_sm_2022": "S&M total por alta, 2022 (unidad reportada)",
    "cac_sm_2024": "S&M total por alta, 2024 (unidad reportada)",
    "total_sm_per_new_customer_chg": "Cambio del S&M total por alta, 2022 a 2024",
    "r_new_sm_l0": "Correlación en niveles entre S&M total y altas del mismo mes (r de Pearson)",
    "r_mom_absmax": "Mayor |r| en cambios mes a mes entre gasto y resultados",
    "r_mom_minp": "Menor valor p en cambios mes a mes",
    "n_corr_sig": "Correlaciones con p < 0,05",
    "n_corr_tests": "Pruebas de correlación hechas",
    "team_fixed_months": "Meses en que Team es exactamente 12% del S&M total",
    "team_fixed_until": "Último mes con Team fijo en 12%",
    "feb_sig_share": "Altas de feb-22 cuyo primer pago es el doble del segundo",
    "later_sig_share": "Misma proporción en cohortes posteriores (mediana)",
    "exp_mrr_revert": "MRR de expansión que se revierte al mes siguiente",
    "small_exp_first": "Expansiones menores a 10%, primer semestre (2022 S1)",
    "small_exp_last": "Expansiones menores a 10%, último semestre (2024 S2)",
    "offgrid_2022s2": "Meses-cliente activos con monto fuera de la grilla de COP 2.100, 2022 S2",
    "offgrid_2024s2": "Meses-cliente activos con monto fuera de la grilla de COP 2.100, 2024 S2",
    "adq_rr_median_2022": "Mediana 2022 del run-rate inicial (M0–M2) de las altas: corte entre ticket alto y bajo",
    "adq_above_2022": "Altas por mes con run-rate inicial igual o mayor a la mediana 2022, en 2022",
    "adq_above_2023": "Altas por mes con run-rate inicial igual o mayor a la mediana 2022, en 2023",
    "adq_above_2024": "Altas por mes con run-rate inicial igual o mayor a la mediana 2022, en 2024",
    "adq_below_2022": "Altas por mes con run-rate inicial menor a la mediana 2022, en 2022",
    "adq_below_2023": "Altas por mes con run-rate inicial menor a la mediana 2022, en 2023",
    "adq_below_2024": "Altas por mes con run-rate inicial menor a la mediana 2022, en 2024",
    "adq_below_share_increase": "Parte del aumento de altas por mes 2022→2024 que corresponde a ticket bajo",
    "ga_total_start": "Monto pagado total, ene-22",
    "ga_total_end": "Monto pagado total, oct-24",
    "ga_base_end": "Monto pagado en oct-24 por los clientes activos en ene-22",
    "ga_new_end": "Monto pagado en oct-24 por los clientes que empezaron después de ene-22",
    "ga_base_survivors": "Clientes activos en ene-22 que siguen pagando en oct-24",
    "ga_base_survivor_ratio": "Monto oct-24 / ene-22 de esos clientes que siguen pagando (veces)",
    "rt_gross": "Movimiento bruto total del monto pagado sin altas, mar-22 a sep-24 (no es lo revertido)",
    "rt_share": "Parte de ese movimiento bruto que vuelve exacto al nivel previo al mes siguiente",
    "churn_obs_2022": "Churn observado mensual de logos, 2022 (mar–dic)",
    "churn_obs_2023": "Churn observado mensual de logos, 2023",
    "churn_obs_2024": "Churn observado mensual de logos, 2024 (ene–jul)",
    "churn_dur3_2022": "Churn mensual que no vuelve a pagar en 3 meses, 2022",
    "churn_dur3_2023": "Churn mensual que no vuelve a pagar en 3 meses, 2023",
    "churn_dur3_2024": "Churn mensual que no vuelve a pagar en 3 meses, 2024 (ene–jul)",
    "retro_events": "Eventos de ajuste sincronizado con cobro retroactivo exacto",
    "retro_customers": "Clientes con ese ajuste",
    "retro_exp_share_2023": "Tramo de subida de esos ajustes como parte de la expansión de 2023",
    "retro_exp_share_2024": "Tramo de subida de esos ajustes como parte de la expansión de 2024",
    "retro_net_2023": "Aumento mensual neto que persiste por esos ajustes, 2023",
    "retro_net_2024": "Aumento mensual neto que persiste por esos ajustes, 2024",
    "catchup_returns": "Retornos que pagan exactamente los meses pendientes",
    "catchup_n": "Retornos después de uno o más meses sin pago",
    "catchup_share": "Parte de los retornos que liquidan exactamente los meses pendientes",
    "jun22_churn": "Churns observados en jun-22",
    "churn_month_median": "Mediana mensual de churns observados (mar-22 a oct-24)",
    "jun22_back_next": "Churns de jun-22 que vuelven a pagar al mes siguiente",
    "cnt_22_24": "Cambio de las altas por mes, 2022 a 2024",
    "cnt_23_24": "Cambio de las altas por mes, 2023 a 2024",
    "val_rr_22_24": "Cambio del valor inicial incorporado por mes (run-rate M0–M2), 2022 a 2024",
    "val_rr_23_24": "Cambio del valor inicial incorporado por mes (run-rate M0–M2), 2023 a 2024",
    "val_usual_22_24": "Cambio del valor inicial incorporado por mes (monto habitual), 2022 a 2024",
    "val_usual_23_24": "Cambio del valor inicial incorporado por mes (monto habitual), 2023 a 2024",
    "val_m1to3_22_24": "Cambio del valor inicial incorporado por mes (mediana M1–M3), 2022 a 2024",
    "val_m1to3_23_24": "Cambio del valor inicial incorporado por mes (mediana M1–M3), 2023 a 2024",
    "ret12_low_2023": "Retención de logos al M12, altas de 2023 con ticket bajo (bajo la mediana 2022)",
    "ret12_high_2023": "Retención de logos al M12, altas de 2023 con ticket alto",
    "ret12_n_low": "Altas de 2023 con ticket bajo observables al M13",
    "ret12_n_high": "Altas de 2023 con ticket alto observables al M13",
    "new_2022_pm": "Altas por mes, 2022 (mar–dic)",
    "new_2324_pm": "Altas por mes, ene-23 a oct-24",
    "plateau_slope": "Pendiente de las altas por mes desde ene-23 (cambio por mes)",
    "plateau_lo": "Límite inferior del intervalo de 95% de esa pendiente",
    "plateau_hi": "Límite superior del intervalo de 95% de esa pendiente",
}


def check_claims(ctx: dict, R: dict) -> list[dict]:
    """Cada título con conclusión del workspace está respaldado por una de estas verificaciones.
    Si los datos cambian y una afirmación deja de ser cierta, el pipeline se detiene en lugar de publicarla."""
    corr, coh, ev, dec, iy = ctx["corr"], ctx["coh"], ctx["ev"], ctx["dec"], ctx["iyear"]
    lb = ev["last_bridge"]
    mom = corr[corr["transform"] == "mom_change"]
    lvl_new = corr[(corr["transform"] == "levels") & (corr.outcome == "Altas") & (corr.lag_months <= 1)]
    r24 = dec["robust"][dec["robust"].comparison == "2022 vs 2024"]
    va = ev["vintage_arpa"]
    base = va[va.vintage == VINT_BASE].arpa_cop
    base_ok = abs(base.iloc[-1] / base.iloc[0] - 1) < 0.10
    vint_ok = max(R["v2023_arpa_end"], R["v2024_arpa_end"]) < min(R["v2022_arpa_end"], R["base_arpa_end"])
    share = lambda y, ind, col: float(iy[(iy.year == y) & (iy.industry == ind)][col].iloc[0])
    H, E, D = "Hecho observado", "Evidencia fuerte", "Direccional"
    claims = [
        ("C-RES-01", "growth_gap", "Resultado", H,
         "Los clientes activos crecieron más rápido que el MRR pagado entre ene-22 y oct-24.",
         R["active_multiple"] > R["mrr_multiple"] * 1.3, ["active_multiple", "mrr_multiple"]),
        ("C-RES-02", "arpa_down", "Resultado", H,
         "El MRR por cliente activo de oct-24 es más de 30% menor que el de ene-22.",
         R["arpa_change"] < -0.30, ["arpa_start", "arpa_end", "arpa_change"]),
        ("C-RES-03", "net_adds_positive", "Resultado", H,
         "Las altas netas fueron negativas en un solo mes.",
         R["net_adds_negative_months"] == 1, ["net_adds_negative_list", "net_adds_positive_months"]),
        ("C-RES-04", "gross_vs_net", "Resultado", H,
         "Los movimientos brutos de MRR superan 5 veces el cambio neto del periodo.",
         R["gross_net_ratio"] > 5, ["gross_movement", "net_movement", "gross_net_ratio"]),
        ("C-RES-05", "last_react_largest", "Resultado", H,
         "En el último mes, la reactivación fue la mayor entrada de MRR.",
         lb["reactivation_mrr_cop"] > max(lb["new_mrr_cop"], lb["expansion_mrr_cop"]),
         ["lb_reactivation_mrr_cop", "lb_new_mrr_cop", "lb_expansion_mrr_cop"]),
        ("C-RES-06", "rest_mrr_share_down", "Resultado", H,
         "Restaurantes sigue siendo el mayor bloque de MRR, con menor participación en oct-24 que en dic-22.",
         R["rest_is_top_mrr_2024"] and R["rest_mrr_share_2024"] < R["rest_mrr_share_2022"],
         ["rest_mrr_share_2022", "rest_mrr_share_2024"]),
        ("C-RES-07", "retail_active_share_up", "Resultado", H,
         "Retail tiene mayor participación en los clientes activos en oct-24 que en dic-22.",
         R["retail_active_share_2024"] > R["retail_active_share_2022"],
         ["retail_active_share_2022", "retail_active_share_2024"]),
        ("C-ADQ-01", "entry_ticket_down", "Adquisición", H,
         "La mediana del ticket de entrada es menor en 2023 y en 2024 que en 2022.",
         R["m0_median_2023"] < R["m0_median_2022"] and R["m0_median_2024"] < R["m0_median_2022"],
         ["m0_median_2022", "m0_median_2023", "m0_median_2024"]),
        ("C-ADQ-02", "ticket_all_metrics", "Adquisición", H,
         "Todas las métricas de ticket de entrada (promedio, mediana, winsorizado, run-rate temprano y M1) son menores en 2024 que en 2022.",
         all(R[k] < 0 for k in ["m0_mean_chg_22_24", "m0_median_chg_22_24", "err_mean_chg_22_24", "m1_mean_chg_22_24", "m0_winsor_chg_22_24"]),
         ["m0_mean_chg_22_24", "m0_median_chg_22_24", "m1_mean_chg_22_24"]),
        ("C-ADQ-03", "ticket_step", "Adquisición", H,
         "El mes del escalón (desde el cual toda mediana mensual del ticket queda bajo la de 2022) cae en el primer trimestre de 2023.",
         "2023-01" <= R["step_month"] <= "2023-03", ["step_month", "m0_median_2022"]),
        ("C-ADQ-04", "within_dominates", "Adquisición", E,
         "El efecto dentro de las industrias explica más de 80% del cambio del ticket 2022→2024 en las tres variantes, y el límite inferior del intervalo bootstrap de 90% supera 50%.",
         bool((r24.within_share > 0.8).all() and (r24.within_share_ci90_lo > 0.5).all()),
         ["dec_within_share", "dec_within_ci", "dec_within_share_min", "dec_within_share_max"]),
        ("C-ADQ-05", "all_industries_down", "Adquisición", H,
         "El ticket de entrada (promedio y mediana) bajó en las seis industrias entre 2022 y 2024.",
         R["industries_ticket_fell_22_24"] == 6 and R["industries_median_fell_22_24"] == 6,
         ["industries_ticket_fell_22_24", "industries_median_fell_22_24"]),
        ("C-ADQ-06", "restprod_new_mrr_majority", "Adquisición", H,
         "Restaurantes y Producción aportan más de la mitad del MRR nuevo en cada año.",
         R["restprod_new_mrr_min"] > 0.5, ["restprod_new_mrr_min"]),
        ("C-RET-01", "recent_cohorts_m1", "Retención", H,
         "La menor retención de logos al M1 entre los trimestres completos de 2023–24 supera la mayor entre los trimestres completos de 2022.",
         R["m1_logo_recent_min"] > R["m1_logo_2022_max"],
         ["m1_logo_2022_min", "m1_logo_2022_max", "m1_logo_recent_min", "m1_logo_recent_max"]),
        ("C-RET-02", "churn_transient", "Retención", H,
         "Más de 40% de los churns observados vuelve a pagar al mes siguiente.",
         R["churn_back_1m"] > 0.40, ["churn_back_1m", "churn_events"]),
        ("C-MON-01", "base_stable", "Monetización de la base", H,
         "El MRR por cliente de la base previa en oct-24 está dentro de ±10% del de ene-22.",
         base_ok, ["base_arpa_start", "base_arpa_end", "base_arpa_change"]),
        ("C-MON-02", "vintage_order", "Monetización de la base", H,
         "En oct-24, las cosechas 2023 y 2024 tienen menor MRR por cliente que la cosecha 2022 y que la base previa.",
         vint_ok, ["v2022_arpa_end", "v2023_arpa_end", "v2024_arpa_end", "base_arpa_end"]),
        ("C-MON-03", "cohorts_stay_lower", "Monetización de la base", H,
         "El MRR por cliente original de las cohortes 2023 está por debajo del de las cohortes 2022 en M1, M6 y M12.",
         all(c23 < c22 for c22, c23 in [(coh["yearly"][0]["arpu"][k], coh["yearly"][1]["arpu"][k]) for k in (1, 6, 12)]),
         []),
        ("C-MON-04", "composition", "Monetización de la base", E,
         "Los clientes existentes no pagan menos y las cosechas 2023–24, de menor ticket, ya son la mayoría de los clientes activos.",
         base_ok and vint_ok and R["recent_vintage_customer_share"] > 0.5,
         ["base_arpa_change", "recent_vintage_customer_share", "recent_vintage_mrr_share"]),
        ("C-MON-05", "industries_arpa_fell", "Monetización de la base", H,
         "El MRR por cliente activo bajó en las seis industrias entre dic-22 y oct-24.",
         R["industries_arpa_fell"] == 6, ["industries_arpa_fell"]),
        ("C-INV-01", "sm_cut", "Inversión comercial", H,
         "El S&M total cayó más de 60% entre su pico y su valle de 2023.",
         R["sm_drop"] < -0.60, ["sm_peak", "sm_trough", "sm_drop"]),
        ("C-INV-02", "spend_per_customer_down", "Inversión comercial", H,
         "El S&M total por cliente nuevo es más de 50% menor en 2024 que en 2022.",
         R["total_sm_per_new_customer_chg"] < -0.50, ["cac_sm_2022", "cac_sm_2024", "total_sm_per_new_customer_chg"]),
        ("C-INV-03", "no_positive_assoc", "Inversión comercial", D,
         "Las correlaciones en niveles entre gasto y altas (rezagos 0–1) son todas negativas, y ninguna correlación de cambios mes a mes alcanza |r| ≥ 0,3 ni p < 0,05.",
         bool((lvl_new.pearson_r < 0).all() and (mom.pearson_r.abs() < 0.3).all() and (mom.pearson_p > 0.05).all()),
         ["r_new_sm_l0", "r_mom_absmax", "r_mom_minp"]),
        ("C-INV-04", "sig_only_negative_levels", "Inversión comercial", D,
         "Toda correlación con p < 0,05 es una correlación negativa en niveles con las altas.",
         bool(((corr.pearson_p >= 0.05) | ((corr["transform"] == "levels") & (corr.outcome == "Altas") & (corr.pearson_r < 0))).all()),
         ["n_corr_sig", "n_corr_tests"]),
        ("C-DAT-01", "team_fixed", "Datos", H,
         "Team equivale a 12,0% del S&M total en todos los meses hasta may-23.",
         R["team_fixed_months"] == 17 and R["team_fixed_until"] == "2023-05", ["team_fixed_months", "team_fixed_until"]),
        ("C-DAT-02", "feb_spillover", "Datos", H,
         "Las altas de feb-22 muestran la firma de pago doble a más de 5 veces la tasa conjunta de las cohortes posteriores.",
         R["feb_sig_share"] > 5 * R["later_sig_share"], ["feb_sig_share", "later_sig_share"]),
        ("C-DAT-03", "exp_revert", "Datos", H,
         "Más de 25% del MRR de expansión se revierte al mes siguiente.",
         R["exp_mrr_revert"] > 0.25, ["exp_mrr_revert"]),
        ("C-DAT-04", "small_adjust_rise", "Datos", H,
         "Los ajustes menores a 10% pasaron de menos de 15% a más de 60% de los eventos de expansión entre el primer y el último semestre.",
         R["small_exp_first"] < 0.15 and R["small_exp_last"] > 0.60, ["small_exp_first", "small_exp_last"]),
        ("C-DAT-05", "offgrid_rise", "Datos", H,
         "La proporción de meses-cliente activos con montos fuera de la grilla de COP 2.100 es mayor en 2024 S2 que en 2022 S2.",
         R["offgrid_2024s2"] > R["offgrid_2022s2"], ["offgrid_2022s2", "offgrid_2024s2"]),
        # verificación analítica (sep-2026): definiciones en verification_views(), sensibilidad en docs/evidence_pack.py
        ("C-ADQ-07", "growth_below_2022_median", "Adquisición", H,
         "El aumento de altas por mes entre 2022 y 2024 corresponde a clientes con run-rate inicial menor que la mediana "
         "de 2022; por encima de esa mediana, las altas por mes no aumentaron.",
         R["adq_below_share_increase"] >= 0.9 and R["adq_above_2024"] <= R["adq_above_2022"],
         ["adq_rr_median_2022", "adq_above_2022", "adq_above_2023", "adq_above_2024", "adq_below_2022", "adq_below_2023",
          "adq_below_2024", "adq_below_share_increase"]),
        ("C-RES-08", "growth_from_new_customers", "Resultado", H,
         "Todo el aumento del monto pagado entre ene-22 y oct-24 proviene de clientes que empezaron a pagar después de "
         "ene-22; los clientes activos en ene-22 terminan con menos monto que al inicio.",
         R["ga_new_end"] > R["ga_total_end"] - R["ga_total_start"] and R["ga_base_end"] < R["ga_total_start"],
         ["ga_total_start", "ga_total_end", "ga_base_end", "ga_new_end", "ga_base_survivors", "ga_base_survivor_ratio"]),
        ("C-DAT-06", "one_month_round_trips", "Datos", H,
         "Más de 20% del movimiento bruto del monto pagado entre mar-22 y sep-24, sin contar altas, se revierte "
         "exactamente al nivel previo al mes siguiente.",
         R["rt_share"] > 0.20, ["rt_gross", "rt_share"]),
        ("C-RET-03", "durable_churn_flat", "Retención", H,
         "El churn observado bajó más de un punto entre 2022 y 2024, mientras el churn que no vuelve a pagar en tres "
         "meses cambió menos de 0,3 puntos.",
         R["churn_obs_2022"] - R["churn_obs_2024"] > 0.01 and abs(R["churn_dur3_2024"] - R["churn_dur3_2022"]) < 0.003,
         ["churn_obs_2022", "churn_obs_2023", "churn_obs_2024", "churn_dur3_2022", "churn_dur3_2023", "churn_dur3_2024"]),
        ("C-DAT-07", "retroactive_adjustments", "Datos", H,
         "Más de 200 clientes muestran un ajuste sincronizado con cobro retroactivo exacto: el monto sube k veces un "
         "porcentaje y al mes siguiente queda en ese porcentaje.",
         R["retro_customers"] > 200,
         ["retro_events", "retro_customers", "retro_exp_share_2023", "retro_exp_share_2024", "retro_net_2023", "retro_net_2024"]),
        ("C-DAT-08", "catchup_returns", "Datos", H,
         "Más de 25% de los retornos después de meses sin pago liquidan exactamente los meses pendientes (±1%).",
         R["catchup_share"] > 0.25, ["catchup_returns", "catchup_n", "catchup_share"]),
        ("C-DAT-09", "jun22_event", "Datos", H,
         "En jun-22 los churns observados fueron más del doble de la mediana mensual y más de 70% volvió a pagar al mes siguiente.",
         R["jun22_churn"] > 2 * R["churn_month_median"] and R["jun22_back_next"] > 0.70,
         ["jun22_churn", "churn_month_median", "jun22_back_next"]),
        ("C-ADQ-08", "value_lags_count", "Adquisición", H,
         "El valor inicial incorporado por mes creció menos que las altas entre 2022 y 2024 en las tres normalizaciones "
         "probadas, y entre 2023 y 2024 cambió menos de 10% en todas.",
         all(R[f"val_{k}_22_24"] < R["cnt_22_24"] for k in ("rr", "usual", "m1to3"))
         and all(abs(R[f"val_{k}_23_24"]) < 0.10 for k in ("rr", "usual", "m1to3")),
         ["cnt_22_24", "val_rr_22_24", "val_usual_22_24", "val_m1to3_22_24", "cnt_23_24", "val_rr_23_24",
          "val_usual_23_24", "val_m1to3_23_24"]),
        ("C-RET-04", "low_ticket_retention_m12", "Retención", D,
         "En las cohortes de 2023, la retención de logos al M12 de las altas bajo la mediana de 2022 está a menos de "
         "5 puntos de la de las altas por encima.",
         abs(R["ret12_low_2023"] - R["ret12_high_2023"]) < 0.05,
         ["ret12_low_2023", "ret12_high_2023", "ret12_n_low", "ret12_n_high"]),
        ("C-ADQ-09", "acquisition_plateau", "Adquisición", D,
         "Las altas por mes se duplicaron con un escalón a inicios de 2023 y desde ene-23 no muestran una tendencia "
         "distinguible de cero.",
         R["new_2324_pm"] > 1.8 * R["new_2022_pm"] and R["plateau_lo"] < 0 < R["plateau_hi"],
         ["new_2022_pm", "new_2324_pm", "plateau_slope", "plateau_lo", "plateau_hi"]),
    ]
    unlabeled = sorted({k for *_, evid in claims for k in evid if k not in FACT_LABELS})
    assert not unlabeled, f"cifras citadas sin etiqueta en FACT_LABELS: {unlabeled}"
    out = [{"id": cid, "key": key, "dominio": dom, "estado": est, "claim": text, "verified": bool(ok), "evidence": evid,
            "etiquetas": {k: FACT_LABELS[k] for k in evid}}
           for cid, key, dom, est, text, ok, evid in claims]
    failed = [c for c in out if not c["verified"]]
    if failed:
        raise AssertionError("Afirmaciones que los datos ya no sostienen: " + "; ".join(f"{c['id']} {c['claim']}" for c in failed))
    return out


# ----------------------------------------------------------------------------------
# 12 · Business Brain (brain/) y payload del workspace
# ----------------------------------------------------------------------------------
def load_brain() -> dict:
    import yaml
    rd = lambda rel: yaml.safe_load((BRAIN / rel).read_text(encoding="utf-8"))
    return {"metrics": rd("semantic/metrics.yaml")["metrics"],
            "issues": rd("data/known_quality_issues.yaml")["issues"],
            "questions": rd("business/stakeholder_questions.yaml"),
            "cards": rd("evidence/workspace_cards.yaml")["cards"],
            "answers": rd("business/answers.yaml"),
            "missing": rd("guardrails/missing_data.yaml")["faltantes"]}


PLACEHOLDER = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


def fill_facts(text: str, facts: dict) -> str:
    return PLACEHOLDER.sub(lambda mt: str(facts[mt.group(1)]), text)


def answer_texts(entry: dict):
    """Textos redactados de una respuesta (para validarlos y rellenarlos)."""
    for k in ("titular", "respuesta", "que_pasa", "por_que", "no_sabemos", "visual_titulo"):
        if isinstance(entry.get(k), str):
            yield k, entry[k]
    lec = entry.get("lectura")
    if isinstance(lec, dict):
        yield "lectura", lec.get("texto", "")
    elif isinstance(lec, str):
        yield "lectura", lec
    for k in ("sabemos", "no_sabemos"):
        if isinstance(entry.get(k), list):
            for i, t in enumerate(entry[k]):
                yield f"{k}[{i}]", t


def validate_answers(brain: dict, claims: list, facts: dict):
    """La capa de respuestas cumple las mismas reglas que el agente: cifras solo como facts, afirmaciones que
    existen, gráficas que existen, datos faltantes del catálogo y lenguaje sin causalidad ni calificativos."""
    from agent.lint import lint_text
    ans = brain["answers"]
    claim_ids = {c["id"] for c in claims}
    missing = {m["id"] for m in brain["missing"]}
    golden = {g["id"] for g in brain["questions"]["preguntas_doradas"]}
    tpl = (HERE / "templates" / "finora_eda_template.html").read_text(encoding="utf-8")
    entries = [("esencial", ans["esencial"])] + [(f"secciones.{k}", v) for k, v in ans["secciones"].items()] + \
              [(f"preguntas.{k}", v) for k, v in ans["preguntas"].items()]
    for where, e in entries:
        for field, text in answer_texts(e):
            for key in PLACEHOLDER.findall(text):
                assert key in facts, f"respuesta {where}.{field}: fact desconocido {key}"
            problems = lint_text(text, allow_explica=bool(e.get("explica")))
            assert not problems, f"respuesta {where}.{field}: {problems}"
        for cid in e.get("claims", []):
            assert cid in claim_ids, f"respuesta {where}: afirmación desconocida {cid}"
        for mid in e.get("necesitariamos", []):
            assert mid in missing, f"respuesta {where}: dato faltante desconocido {mid}"
        if e.get("visual"):
            assert f'data-chart="{e["visual"]}"' in tpl, f"respuesta {where}: gráfica desconocida {e['visual']}"
        lec = e.get("lectura")
        if isinstance(lec, dict):
            assert f'data-card="{lec["tarjeta"]}"' in tpl, f"respuesta {where}: tarjeta desconocida {lec['tarjeta']}"
    for sid in ans["secciones"]:
        assert f'<section class="section" id="{sid}">' in tpl, f"respuesta de sección desconocida {sid}"
    for qid in list(ans["preguntas"]) + list(ans["esencial"].get("profundizar", [])):
        assert qid in golden, f"pregunta dorada desconocida {qid}"


def render_answers(brain: dict, facts: dict) -> dict:
    ans, missing = brain["answers"], {m["id"]: m for m in brain["missing"]}

    def one(e: dict) -> dict:
        out = dict(e)
        for k in ("titular", "respuesta", "que_pasa", "por_que", "no_sabemos", "visual_titulo"):
            if isinstance(out.get(k), str):
                out[k] = fill_facts(out[k], facts)
        if isinstance(out.get("lectura"), dict):
            out["lectura"] = {**out["lectura"], "texto": fill_facts(out["lectura"]["texto"], facts)}
        elif isinstance(out.get("lectura"), str):
            out["lectura"] = fill_facts(out["lectura"], facts)
        for k in ("sabemos", "no_sabemos"):
            if isinstance(out.get(k), list):
                out[k] = [fill_facts(t, facts) for t in out[k]]
        if out.get("necesitariamos"):
            out["necesitariamos"] = [{"id": m, "nombre": missing[m]["nombre"], "campos": missing[m].get("campos_necesarios", [])}
                                     for m in out["necesitariamos"]]
        return out
    return {"esencial": one(ans["esencial"]),
            "secciones": {k: one(v) for k, v in ans["secciones"].items()},
            "preguntas": {k: one(v) for k, v in ans["preguntas"].items()}}


def validate_brain(brain: dict, claims: list, facts: dict):
    validate_answers(brain, claims, facts)
    from agent import caso
    problems = caso.check_questions({c["id"] for c in claims}, {m["id"] for m in brain["missing"]})
    assert not problems, "preguntas del caso (brain/business/case_questions.yaml): " + "; ".join(problems)
    # en YAML, "- texto: más texto" se lee como diccionario; los textos que se muestran deben ser str
    for k, q in enumerate(brain["questions"]["preguntas_para_finora"], 1):
        assert isinstance(q, str), f"pregunta para Finora {k} no es texto (¿falta entrecomillar un ': '?)"
    for g in brain["questions"]["preguntas_doradas"]:
        assert all(isinstance(g[k], str) for k in ("id", "dominio", "pregunta", "tipo")), f"pregunta dorada mal formada: {g}"
    metric_ids = {m["id"] for m in brain["metrics"]}
    issue_ids = {i["id"] for i in brain["issues"]}
    claim_ids = {c["id"] for c in claims}
    for m in brain["metrics"]:
        for cv in m.get("caveats", []):
            assert cv in issue_ids, f"métrica {m['id']}: caveat desconocido {cv}"
    for i in brain["issues"]:
        for fk in i.get("evidencia", []):
            assert fk in facts, f"issue {i['id']}: fact desconocido {fk}"
    for cid, c in brain["cards"].items():
        for mid in c.get("metricas", []):
            assert mid in metric_ids, f"tarjeta {cid}: métrica desconocida {mid}"
        for cv in c.get("caveats", []):
            assert cv in issue_ids, f"tarjeta {cid}: caveat desconocido {cv}"
        for cl in c.get("claims", []):
            assert cl in claim_ids, f"tarjeta {cid}: claim desconocido {cl}"


def load_golden_investigations() -> dict:
    """Investigaciones doradas de la capa agentic (investigations/golden/*.json), embebidas para que el demo corra sin red."""
    out = {}
    folder = HERE / "investigations" / "golden"
    for p in sorted(folder.glob("*.json")) if folder.exists() else []:
        inv = json.loads(p.read_text(encoding="utf-8"))
        inv.pop("events", None)
        out[p.stem] = inv
    return out


def load_case() -> dict:
    """Preguntas del caso (W0–W7): la cola, las respuestas deterministas de las bloqueadas y las respuestas publicadas
    (investigations/caso/W*.json), embebidas para que la cola se navegue sin servidor."""
    from agent import caso
    answers = {}
    for qid in caso.ORDER:
        d = caso.load_answer(qid)
        if d and d.get("respuesta_caso"):
            answers[qid] = {k: v for k, v in d.items() if k != "events"}
    return {"fuente": caso.DOC["fuente"], "escala": caso.DOC["escala"], "orden": caso.DOC["orden_de_trabajo"],
            "preguntas": caso.DOC["preguntas"], "respuestas": answers,
            "bloqueadas": {q["id"]: caso.blocked_answer(q) for q in caso.DOC["preguntas"] if not caso.can_investigate(q["id"])}}


def build_payload(ctx: dict, facts: dict, claims: list, brain: dict) -> dict:
    ar, mm, ev, dec, coh, mov, corr, im, ihalf, iyear = (ctx[k] for k in
        ["ar", "mm", "ev", "dec", "coh", "mov", "corr", "im", "ihalf", "iyear"])
    order = ctx["order"]
    months = ar["months"]
    P = {}
    P["meta"] = {"months": [str(m) for m in months], "labels": [month_label(m) for m in months],
                 "cleanStart": ctx["clean_start"], "generated": facts["generated"], "spendUnit": SPEND_UNIT,
                 "scaleToCop": SCALE_TO_COP,
                 "hashes": {k: v["sha256"][:12] for k, v in ctx["raw"].items()}}
    keep = [c for c in mm.columns if c not in ("month", "month_label", "window_flag", "efficiency_status")]
    P["monthly"] = {c: mm[c].tolist() for c in keep}
    P["monthly"]["window_flag"] = mm.window_flag.tolist()
    P["monthly"]["efficiency_status"] = mm.efficiency_status.tolist()
    P["index"] = ev["index_series"]

    P["industry"] = {"order": order, "monthly": {}, "half": {}, "year": iyear.to_dict("records")}
    for ind in order:
        g = im[im.industry == ind].sort_values("month_index")
        P["industry"]["monthly"][ind] = {c: g[c].tolist() for c in
            ["active_customers", "new_customers", "total_paid_mrr_cop", "new_mrr_cop", "mrr_per_active_customer_cop",
             "new_mrr_per_new_customer_cop", "logo_churn_rate", "share_active_customers", "share_mrr",
             "reactivated_customers", "expansion_mrr_cop", "contraction_mrr_cop", "churned_customers"]}
    halves = sorted(ihalf.half.unique())
    P["industry"]["halves"] = halves
    for ind in order:
        g = ihalf[ihalf.industry == ind].set_index("half").reindex(halves)
        P["industry"]["half"][ind] = {c: g[c].tolist() for c in
            ["new_customers", "new_mrr_cop", "new_mrr_per_new_customer_cop", "share_new_customers", "share_new_mrr"]}

    P["decomp"] = {"main": dec["main"], "details": {k: v.to_dict("records") for k, v in dec["details"].items()},
                   "robust": dec["robust"].to_dict("records"), "evolution": dec["evolution"].to_dict("records"),
                   "medians": {int(y): {ind: float(dec["medians"].loc[y, ind]) for ind in order} for y in dec["medians"].index},
                   "winsorCap": dec["winsor_cap_cop"]}
    P["cohorts"] = {"quarterly": coh["quarterly"], "monthly": coh["monthly"], "yearly": coh["yearly"],
                    "summary": coh["summary"].to_dict("records"), "flagged": coh["flagged"]}
    P["corr"] = {"rows": corr.to_dict("records"),
                 "sens": ctx["corr_sens"].to_dict("records"),
                 "spend": {"Paid Media": mm.paid_media.tolist(), "Generación de demanda": mm.demand_gen_spend.tolist(),
                           "S&M total": mm.total_sm_spend.tolist()},
                 "outcome": {"Altas": mm.new_customers.tolist(), "MRR nuevo": mm.new_mrr_cop.tolist()}}
    P["bridge"] = {"annual": ev["annual_bridge"].to_dict("records"), "last": ev["last_bridge"]}
    by_year = mov["by_year"]
    buckets = ["1 mes", "2 meses", "3–5 meses", "6+ meses", "Sin volver a oct-24"]
    by_year = by_year.reindex(columns=buckets, fill_value=0)
    P["movements"] = {"returnBuckets": buckets, "returnYears": [int(y) for y in by_year.index],
                      "returnCounts": by_year.to_numpy().tolist(),
                      "small": mov["small_adjustments"].to_dict("records"),
                      "gridMonthly": list(mov["grid_share_monthly"]),
                      "gridHalf": [{"half": h, "share": float(v)} for h, v in mov["grid_share_half"].items()],
                      "stats": {k: mov[k] for k in ["n_churn_events", "share_return_1m", "share_return_any",
                                                    "share_churned_mrr_back_1m", "share_expansion_mrr_reverting_1m",
                                                    "share_contraction_mrr_post_spike", "multi_month_signatures",
                                                    "multi_month_signature_customers", "gross_movement_cop",
                                                    "net_movement_cop"]},
                      "signatureK": mov["signature_k_counts"]}
    P["ticket"] = {"byYear": ev["ticket_by_year"].to_dict("records"), "bands": ev["price_bands"]}
    va = ev["vintage_arpa"]
    P["vintage"] = {v: {"arpa": g.sort_values("month").arpa_cop.tolist(), "active": g.sort_values("month").active_customers.tolist(),
                        "mrr": g.sort_values("month").mrr_cop.tolist()} for v, g in va.groupby("vintage", sort=False)}
    P["vintageNames"] = {"base": VINT_BASE, "feb": VINT_FEB, "v2022": VINT_2022, "v2023": VINT_2023, "v2024": VINT_2024}
    P["audit"] = ctx["audit"]
    P["entrySignature"] = ctx["sig_entry"].to_dict("records")
    P["examples"] = ev["examples"]
    P["amountHist"] = ev["amount_hist"]
    P["efficiencyByYear"] = ev["efficiency_by_year"].to_dict("records")
    P["claims"] = claims
    P["facts"] = facts
    P["brain"] = {"metrics": {m["id"]: m for m in brain["metrics"]},
                  "issues": {i["id"]: i for i in brain["issues"]},
                  "golden": brain["questions"]["preguntas_doradas"],
                  "questionsFinora": brain["questions"]["preguntas_para_finora"],
                  "cards": brain["cards"],
                  "missing": {m["id"]: m for m in brain["missing"]}}
    P["investigations"] = load_golden_investigations()
    P["answers"] = render_answers(brain, facts)
    P["caso"] = load_case()
    return jsonable(P)


def write_canonical_findings(claims: list, facts: dict, path: Path):
    """Siembra brain/evidence/canonical_findings.yaml desde el registro de claims (arquitectura §14.6)."""
    import yaml
    doc = {"version": 1,
           "generado_por": "finora_eda.py · check_claims()",
           "nota": "Archivo generado. Un hallazgo pasa a canónico después de revisión humana.",
           "hallazgos": [{"id": c["id"], "clave": c["key"], "dominio": c["dominio"], "estado": c["estado"],
                          "afirmacion": c["claim"], "verificado_en_codigo": c["verified"],
                          "evidencia": {k: facts[k] for k in c["evidence"]},
                          "etiquetas": c["etiquetas"],
                          "revision_humana": "pendiente"} for c in claims]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def render_outputs(ctx: dict, payload: dict, facts: dict, claims: list, brain: dict):
    out_dir = ctx["out_dir"]
    tpl_dir = HERE / "templates"

    def fill(text: str) -> str:
        def rep(mt):
            key = mt.group(1)
            if key not in facts:
                raise KeyError(f"placeholder sin fact: {key}")
            return str(facts[key])
        text = re.sub(r"\{\{([a-zA-Z0-9_]+)\}\}", rep, text)
        assert "{{" not in text, "placeholder sin resolver"
        return text

    html = (tpl_dir / "finora_eda_template.html").read_text(encoding="utf-8")
    html = fill(html)
    data_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    data_json = data_json.replace("</", "<\\/")
    marker = "/*__DATA__*/null"
    assert html.count(marker) == 1
    html = html.replace(marker, data_json)
    app_js = (tpl_dir / "finora_eda_app.js").read_text(encoding="utf-8")
    assert "</script" not in app_js.lower()
    assert html.count("/*__APP_JS__*/") == 1
    html = html.replace("/*__APP_JS__*/", app_js)
    (out_dir / "finora_eda.html").write_text(html, encoding="utf-8")

    notes = (tpl_dir / "finora_eda_notes_template.md").read_text(encoding="utf-8")
    notes = fill(notes)
    esc = lambda t: str(t).replace("|", "\\|")
    claim_lines = "\n".join(f"| `{c['id']}` | {c['dominio']} | {c['estado']} | {esc(c['claim'])} | {'✅ verificado' if c['verified'] else '❌'} |"
                            for c in claims)
    metric_lines = "\n".join(f"| {m['nombre']} (`{m['id']}`) | {esc(m['definicion'])} | `{esc(m['formula'])}` | {m['ventana']} |"
                             for m in brain["metrics"])
    issue_lines = "\n".join(f"| `{i['id']}` | {esc(i['titulo'])} | {i['estado']} | {esc(i['tratamiento'])} |" for i in brain["issues"])
    question_lines = "\n".join(f"{k}. {q}" for k, q in enumerate(brain["questions"]["preguntas_para_finora"], 1))
    for marker in ("<!--CLAIMS-->", "<!--METRICS-->", "<!--ISSUES-->", "<!--QUESTIONS-->"):
        assert notes.count(marker) == 1, f"marcador {marker} ausente o repetido en las notas"
    notes = (notes.replace("<!--CLAIMS-->", claim_lines).replace("<!--METRICS-->", metric_lines)
             .replace("<!--ISSUES-->", issue_lines).replace("<!--QUESTIONS-->", question_lines))
    (out_dir / "finora_eda_notes.md").write_text(notes, encoding="utf-8")
    write_canonical_findings(claims, facts, BRAIN / "evidence" / "canonical_findings.yaml")


if __name__ == "__main__":
    ctx = main()
    print("Finora EDA pipeline finished ·", ctx["out_dir"])
