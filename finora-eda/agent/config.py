"""Configuración de la vertical slice agentic (pregunta dorada 2).

Todo lo que cambia entre corridas vive aquí: modelo, esfuerzo por rol, presupuestos y rutas.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "brain"
RAW = ROOT / "data" / "raw"
DB_PATH = ROOT / "warehouse" / "finora.duckdb"
INVESTIGATIONS = ROOT / "investigations"
GOLDEN = INVESTIGATIONS / "golden"
RUNS = INVESTIGATIONS / "runs"
PROMPTS = Path(__file__).resolve().parent / "prompts"

# Modelo único para agente y compositor (arquitectura v1.2 §3.5); se puede cambiar sin tocar código.
MODEL = os.environ.get("FINORA_MODEL", "claude-opus-5")
EFFORT = {"investigador": "high", "compositor": "medium"}

# Presupuesto de análisis: llamadas que calculan evidencia nueva (query_metric, run_sql, run_analysis).
ANALYSIS_BUDGET = int(os.environ.get("FINORA_ANALYSIS_BUDGET", "15"))
# Tope duro de llamadas a tools de cualquier tipo y de turnos del loop.
MAX_TOOL_CALLS = 60
MAX_TURNS = 80

# Ventanas (Fase 1): ene-22 censurado; feb-22 con arrastre; flujos desde mar-22.
WINDOW_START = "2022-01"
CLEAN_START = "2022-03"
WINDOW_END = "2024-10"

SQL_ROW_LIMIT = 200
SQL_TIMEOUT_S = 10


def file_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def data_version() -> str:
    return "sha256:" + file_hash(list(RAW.glob("*.csv")))[:16]


def brain_version() -> str:
    return "sha256:" + file_hash([p for p in BRAIN.rglob("*.yaml")])[:16]
