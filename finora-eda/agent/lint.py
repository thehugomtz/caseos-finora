"""Reglas de lenguaje compartidas: las usa el validador del agente y el pipeline para las respuestas redactadas.

Sin dependencias del resto del agente para que finora_eda.py pueda importarlo sin ciclos.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import yaml

BRAIN = Path(__file__).resolve().parent.parent / "brain"
GUARD = yaml.safe_load((BRAIN / "guardrails" / "causal_language_es.yaml").read_text(encoding="utf-8"))


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


PROHIBITED = [norm(w) for w in GUARD["prohibido"]]
PATTERNS = [re.compile(p) for p in GUARD.get("patrones", [])]
EXPLICA = re.compile(r"\bexplic(a|an|o|aron|ara|aria)\b")
# Tokens con dígitos que no son cifras medidas: años, meses, semestres, trimestres, tenencias e IDs.
ALLOWED_DIGITS = [r"\b20\d\d\s?[–-]\s?\d\d\b", r"\b20\d\d\s?[ST][1-4]\b", r"\b20\d\d\b",
                  r"\b(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)-\d\d\b", r"\bM\d{1,2}\b",
                  r"\b[HQC]-?\d+(\.\d+)*\b", r"\bS&M\b"]
# Cifras escritas con letras y calificativos que afirman una proporción sin ligarla a evidencia.
NUMBER_WORDS = re.compile(r"\b(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|veinte|"
                          r"treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|cientos|mil|millon|"
                          r"millones|mitad|tercio|tercios|doble|triple|cuadruple)\b")
QUALIFIERS = re.compile(r"\b(casi todos|casi todas|casi siempre|casi nunca|la mayoria|la mayor parte|la gran mayoria|"
                        r"siempre|nunca|sin excepcion|practicamente|claramente|sin duda|drasticamente|dramaticamente|masivamente|"
                        r"(en )?cada (mes|trimestre|semestre|ano)|todos los (meses|trimestres|semestres|anos))\b")
VARS = re.compile(r"\{\{?[a-zA-Z_][a-zA-Z0-9_]*\}\}?")


def _strip_vars(text: str) -> str:
    return VARS.sub(" ", text)


def number_words(text: str) -> list[str]:
    return NUMBER_WORDS.findall(norm(_strip_vars(text)))


def qualifiers(text: str) -> list[str]:
    return [m.group(0) for m in QUALIFIERS.finditer(norm(_strip_vars(text)))]


def causal_hits(text: str, allow_explica: bool) -> list[str]:
    t = norm(text)
    hits = [w for w in PROHIBITED if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", t)]
    hits += [m.group(0) for p in PATTERNS for m in [p.search(t)] if m and m.group(0) not in hits]
    if not allow_explica and EXPLICA.search(t):
        hits.append("explica (solo se permite en afirmaciones de descomposición)")
    return hits


def stray_digits(text: str) -> list[str]:
    t = _strip_vars(text)
    for pat in ALLOWED_DIGITS:
        t = re.sub(pat, " ", t)
    return re.findall(r"\d[\d.,]*", t)


def numbers_in(text: str) -> list[str]:
    """Cifras de un texto ya renderizado, sin años ni etiquetas de periodo."""
    t = text
    for pat in ALLOWED_DIGITS:
        t = re.sub(pat, " ", t)
    return [re.sub(r"[.,]$", "", n) for n in re.findall(r"\d[\d.,]*", t)]


def lint_text(text: str, allow_explica: bool = False) -> list[str]:
    """Problemas de un texto redactado con variables: cifras a mano o con letras, calificativos y lenguaje causal."""
    out = []
    for label, found in (("cifras escritas a mano", stray_digits(text)), ("cifras con letras", number_words(text)),
                         ("calificativos sin cifra", qualifiers(text)), ("lenguaje causal", causal_hits(text, allow_explica))):
        if found:
            out.append(f"{label}: {found}")
    return out
