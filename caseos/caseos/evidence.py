"""Evidence tables (the slide data contract) and number discipline.

Every material number that travels to the Story Package and the Visual Storyteller travels as a structured table:
table_id · title · question · columns · rows · units · definitions · message · source · query/transformation ·
filters · period · grain · analysis_id · limitations · preferred_visual · visual_artifact · created_at.

`numbers_in` + `supported` check that a number written in a claim exists in one of its tables (tolerant to Spanish
formatting: "COP 92,8 mil", "−38%", "4,5×", "1.678"), so no figure reaches a slide buried only in prose.
Adapted from the Business Exploration Workspace's validator discipline (finora-eda/agent/lint.py).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .util import norm, now_iso

TABLE_REQUIRED = ["table_key", "title", "columns", "rows", "message", "source", "limitations"]
PREFERRED_VISUALS = ["annotated_line", "slope", "bar", "stacked_bar", "waterfall", "hero_metric", "split_comparison",
                     "dot_plot", "scatter", "distribution", "table"]


def validate_table(t: dict) -> list[str]:
    errs = []
    for k in TABLE_REQUIRED:
        v = t.get(k)
        if v in (None, "", []):
            errs.append(f"falta '{k}'")
    cols = t.get("columns") or []
    for i, r in enumerate(t.get("rows") or []):
        if not isinstance(r, list) or len(r) != len(cols):
            errs.append(f"la fila {i + 1} no tiene {len(cols)} columnas")
            break
    if t.get("preferred_visual") and t["preferred_visual"] not in PREFERRED_VISUALS:
        errs.append(f"preferred_visual desconocido: {t['preferred_visual']}")
    src = t.get("source") or {}
    if isinstance(src, dict) and not (src.get("system") or src.get("dataset") or src.get("url")):
        errs.append("la fuente no dice de dónde sale (system/dataset/url)")
    return errs


def make_table(*, table_key: str, title: str, question: str, columns: list[str], rows: list[list], message: str,
               source: dict, units: dict | str | None = None, definitions: dict | None = None, filters: list | None = None,
               period: dict | None = None, grain: str = "", analysis_id: str = "", limitations: list[str] | None = None,
               preferred_visual: str = "table", visual_artifact: dict | None = None, query: str = "",
               transformation: str = "") -> dict:
    return {"table_key": table_key, "title": title, "question": question, "columns": columns, "rows": rows,
            "units": units or {}, "definitions": definitions or {}, "message": message, "source": source,
            "query": query, "transformation": transformation, "filters": filters or [], "period": period or {},
            "grain": grain, "analysis_id": analysis_id, "limitations": limitations or [],
            "preferred_visual": preferred_visual, "visual_artifact": visual_artifact, "created_at": now_iso()}


# ------------------------------------------------------------------------------------------ numbers
@dataclass
class Num:
    value: float
    raw: str
    pct: bool = False
    times: bool = False
    decimals: int = 0


_SCALE = {"mil": 1e3, "k": 1e3, "millon": 1e6, "millones": 1e6, "mm": 1e6, "m": 1e6, "mil millones": 1e9, "bn": 1e9,
          "billones": 1e12}
_MONTHS = "ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|jan|apr|aug|dec"
_NUM = re.compile(
    r"(?<![\w.,])(?P<sign>[−\-–+])?\s?(?P<cur>COP|USD|US\$|\$)?\s?(?P<n>\d{1,3}(?:[.  ]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)"
    r"\s?(?P<suf>%|×|x\b|pp\b|p\.p\.|puntos?\b)?(?:\s?(?P<scale>mil millones|millones|millón|millon|mil|mm|bn|k)\b)?", re.I)


def _to_float(s: str) -> tuple[float, int]:
    s = s.replace(" ", ".").replace(" ", ".")
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", s):          # 1.678 or 1.234,5  (es thousands)
        ip, _, dp = s.partition(",")
        return float(ip.replace(".", "") + ("." + dp if dp else "")), len(dp)
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", s):           # 1,678 or 1,234.5 (en thousands)
        ip, _, dp = s.partition(".")
        return float(ip.replace(",", "") + ("." + dp if dp else "")), len(dp)
    if "," in s and "." not in s:                                    # 92,8 (es decimal)
        ip, dp = s.split(",", 1)
        return float(ip + "." + dp), len(dp)
    dp = s.split(".", 1)[1] if "." in s else ""
    return float(s), len(dp)


def numbers_in(text: str) -> list[Num]:
    """Material numbers in a sentence. Years, month-year labels and IDs are not material numbers."""
    t = text or ""
    t = re.sub(rf"\b(?:{_MONTHS})[-/ ]?\d{{2,4}}\b", " ", t, flags=re.I)        # oct-24, ene-2022
    t = re.sub(r"\b[A-Z]{1,4}-\d{2,4}(?:-[A-Z0-9]+)*\b", " ", t)                # C-004, FIN-GROWTH-01, W0
    t = re.sub(r"\b[WSMQHT]\d{1,2}\b", " ", t)                                   # W3, M12, Q2, S2
    out = []
    for m in _NUM.finditer(t):
        raw = m.group(0).strip()
        try:
            v, dec = _to_float(m.group("n"))
        except ValueError:
            continue
        suf = (m.group("suf") or "").lower()
        scale = (m.group("scale") or "").lower()
        if not suf and not scale and not m.group("cur") and 1990 <= v <= 2035 and float(v).is_integer():
            continue                                                               # a year
        if scale:
            v *= _SCALE.get(scale, 1)
        if m.group("sign") and m.group("sign") in "−-–":
            v = -v
        out.append(Num(v, raw, pct=suf in ("%", "pp", "p.p.", "punto", "puntos"), times=suf in ("×", "x"), decimals=dec))
    return out


def table_numbers(table: dict) -> list[float]:
    vals: list[float] = []
    for r in table.get("rows") or []:
        for c in r:
            if isinstance(c, bool):
                continue
            if isinstance(c, (int, float)):
                if not (isinstance(c, float) and math.isnan(c)):
                    vals.append(float(c))
            elif isinstance(c, str):
                vals += [n.value for n in numbers_in(c)]
    return vals


def _close(a: float, b: float, decimals: int) -> bool:
    if a == b:
        return True
    tol = max(abs(b) * 0.006, 0.5 * 10 ** (-decimals) if decimals else 0.5)
    return abs(a - b) <= tol


def supported(n: Num, pool: list[float]) -> bool:
    cands = [n.value]
    if n.pct:
        cands.append(n.value / 100)                     # 38% ↔ 0.38
    for p in pool:
        for c in cands:
            if _close(p, c, n.decimals) or _close(abs(p), abs(c), n.decimals):
                return True
            # absolute values expressed in thousands/millions in the table but not in text (and vice versa)
            for k in (1e3, 1e6):
                if _close(p * k, c, n.decimals) or _close(p, c * k, 0):
                    return True
    return False


def unsupported_numbers(text: str, tables: list[dict]) -> list[str]:
    pool = [v for t in tables for v in table_numbers(t)]
    return [n.raw for n in numbers_in(text) if not supported(n, pool)]


def is_material_numeric(text: str) -> bool:
    return bool(numbers_in(text))


def visual_to_preferred(spec: dict | None) -> str:
    if not spec:
        return "table"
    return {"linea": "annotated_line", "barras": "stacked_bar" if spec.get("apiladas") else "bar", "cascada": "waterfall",
            "puntos": "slope", "dispersion": "scatter", "kpi": "hero_metric", "intervalo": "dot_plot",
            "distribucion": "distribution"}.get(spec.get("tipo"), "table")


def label_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", norm(text).upper()).strip("-")[:28]
