"""Formato es-CO para cifras ligadas (mismas reglas que la Fase 1)."""
from __future__ import annotations

import math

from finora_eda import MINUS, fmt_cop, fmt_int, fmt_num, fmt_pct, fmt_pct_signed, fmt_x, month_label  # noqa: F401
import pandas as pd

FORMATS = ("int", "cop", "cop2", "pct", "pct0", "pct_signed", "num1", "num2", "x", "idx", "u", "texto")


def fmt_value(v, f: str) -> str:
    if isinstance(v, str):
        return v
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return "–"
    if f == "int":
        return fmt_int(v)
    if f == "cop":
        return fmt_cop(v)
    if f == "cop2":
        return fmt_cop(v, 2)
    if f == "pct":
        return fmt_pct(v, 1)
    if f == "pct0":
        return fmt_pct(v, 0)
    if f == "pct_signed":
        return fmt_pct_signed(v, 0)
    if f == "num1":
        return fmt_num(v, 1)
    if f == "num2":
        return fmt_num(v, 2)
    if f == "x":
        return fmt_x(v)
    if f == "idx":
        return fmt_num(v, 0)
    if f == "u":
        return fmt_num(v, 2) + " u"
    return str(v)


def period_label(p: str) -> str:
    """'2024-10' → 'oct-24'; otros periodos ('2022 S1', '2023', 'total') quedan igual."""
    if isinstance(p, str) and len(p) == 7 and p[4] == "-":
        return month_label(pd.Period(p, freq="M"))
    return str(p)
