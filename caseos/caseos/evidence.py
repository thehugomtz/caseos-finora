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
    t = re.sub(r"\b\d{4}-\d{2}(?:-\d{2})?\b", " ", t)                           # 2024-08, 2024-08-31 (ISO periods)
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


def _derived(n: Num, pairs: list[tuple[float, float]]) -> bool:
    """A multiple (4,5×) or a change/share (−38%, 84%) written next to its own figures — de 377 a 1.678 (4,5×) — is backed
    when those figures are: it is their ratio, rounded as written. Only consecutive figures of the claim count, never an
    arbitrary pair of table cells (that would let almost any ratio pass)."""
    tol = max(0.5 * 10 ** (-n.decimals), abs(n.value) * 0.006)
    for a, b in pairs:
        r = b / a
        if n.times and abs(r - n.value) <= tol:
            return True
        if n.pct and (abs((r - 1) * 100 - n.value) <= tol or (n.value > 0 and abs(r * 100 - n.value) <= tol)):
            return True
    return False


def unsupported_numbers(text: str, tables: list[dict], given: list[float] = ()) -> list[str]:
    """Numbers in `text` that no table backs. `given` are figures the case statement itself poses (an example of the
    question being answered, not data about the company)."""
    pool = [v for t in tables for v in table_numbers(t)] + list(given)
    nums = numbers_in(text)
    figs = [n for n in nums if not n.pct and not n.times and n.value and supported(n, pool)]
    pairs = [(a.value, b.value) for a, b in zip(figs, figs[1:]) if (a.value > 0) == (b.value > 0)]
    return [n.raw for n in nums if not supported(n, pool) and not ((n.times or n.pct) and _derived(n, pairs))]


# ------------------------------------------------------------------------------------------ quantities in words
# "cayó a la mitad", "se multiplicaron por cuatro", "el doble": a ratio written in words is still a number. It has to
# agree with the claim's own from → to figures (or its tables), or the headline says something the data does not.
_RATIO_WORDS = [
    (r"a la mitad|la mitad|se redujo a la mitad|se redujeron a la mitad", 0.5),
    (r"a un tercio|un tercio", 1 / 3), (r"dos tercios", 2 / 3), (r"a una cuarta parte|un cuarto", 0.25),
    (r"el doble|se duplic[oó]|se duplicaron|duplic[oó]|duplicaron|por dos", 2.0),
    (r"el triple|se triplic[oó]|se triplicaron|triplic[oó]|triplicaron|por tres", 3.0),
    (r"el cu[aá]druple|se cuadruplic[oó]|se cuadruplicaron|cuadruplic[oó]|cuadruplicaron|por cuatro", 4.0),
    (r"se quintuplic[oó]|se quintuplicaron|por cinco", 5.0),
]
_RATIO_RE = [(re.compile(rf"\b(?:{pat})\b", re.I), r) for pat, r in _RATIO_WORDS]
RATIO_TOLERANCE = 0.12        # relative: "por cuatro" accepts ×3.5–×4.5; "a la mitad" accepts ×0.44–×0.56


def ratio_phrases(text: str) -> list[tuple[str, float]]:
    out, taken = [], []
    for rx, r in _RATIO_RE:
        for m in rx.finditer(text or ""):
            if any(a <= m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            out.append((m.group(0), r))
    return out


def _ratios_available(text: str, tables: list[dict]) -> list[float]:
    """Ratios the claim can stand on: consecutive figures written in the claim (de X a Y) and first → last of each
    numeric column of its tables."""
    pool = [v for t in tables for v in table_numbers(t)]
    nums = [n for n in numbers_in(text) if not n.pct and not n.times and n.value and supported(n, pool)]
    out = [b.value / a.value for a, b in zip(nums, nums[1:]) if a.value and (a.value > 0) == (b.value > 0)]
    for t in tables:
        rows = [r for r in t.get("rows") or [] if isinstance(r, list)]
        for j in range(len(t.get("columns") or [])):
            col = [r[j] for r in rows if j < len(r) and isinstance(r[j], (int, float)) and not isinstance(r[j], bool)]
            if len(col) >= 2 and col[0]:
                out.append(col[-1] / col[0])
    return out


def verbal_ratio_issues(text: str, tables: list[dict]) -> tuple[list[str], list[str]]:
    """(errors, warnings) for quantities written in words."""
    errors, warnings = [], []
    phrases = ratio_phrases(text)
    if not phrases:
        return errors, warnings
    avail = _ratios_available(text, tables)
    for raw, r in phrases:
        if not avail:
            warnings.append(f"«{raw}» (≈×{r:g}) sin cifras que permitan comprobarlo")
        elif not any(abs(x - r) <= RATIO_TOLERANCE * r for x in avail):
            closest = min(avail, key=lambda x: abs(x - r))
            errors.append(f"«{raw}» (≈×{r:g}) no coincide con los datos del claim (lo más cercano: ×{closest:.2f})")
    return errors, warnings


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
