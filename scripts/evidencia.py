#!/usr/bin/env python3
"""Resumen de lo que corrió de verdad en el caso Finora, leído de los archivos del repo (no llama a ningún modelo).

    python3 scripts/evidencia.py            # o .venv/bin/python scripts/evidencia.py
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASE = ROOT / "caseos" / "cases" / "finora"
EDA = ROOT / "finora-eda"


def jload(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def field(path: str, key: str) -> str | None:
    """A top-level YAML scalar without PyYAML (enough for ids, states and actors)."""
    try:
        for line in open(path, encoding="utf-8"):
            m = re.match(rf"^{key}:\s*(.*)$", line)
            if m:
                return m.group(1).strip().strip("'\"")
    except OSError:
        pass
    return None


def review(path: str) -> tuple[str | None, str | None]:
    state = by = None
    inside = False
    for line in open(path, encoding="utf-8"):
        if re.match(r"^review:\s*$", line):
            inside = True
            continue
        if inside:
            if not line.startswith("  "):
                break
            m = re.match(r"^\s+(state|by):\s*(.*)$", line)
            if m:
                if m.group(1) == "state":
                    state = m.group(2).strip()
                else:
                    by = m.group(2).strip()
    return state, by


def money(x: float) -> str:
    return f"US${x:,.2f}"


def main() -> None:
    print("Caso Finora · lo que corrió\n")

    runs = [jload(p) for p in sorted(glob.glob(str(CASE / "audit" / "runs" / "*.json")))]
    runs = [r for r in runs if r]
    if runs:
        models = collections.Counter(r.get("model") for r in runs)
        effort = collections.Counter(r.get("effort") for r in runs)
        agents = collections.Counter(r.get("agent") or r.get("role") for r in runs)
        cost = sum(r.get("cost_usd") or 0 for r in runs if isinstance(r.get("cost_usd"), (int, float)))
        ts = sorted(r.get("started_at") for r in runs if r.get("started_at"))
        print(f"CaseOS · {len(runs)} corridas de agentes, de {ts[0][:16]} a {ts[-1][:16]}")
        print(f"  modelos: {dict(models)} · esfuerzo: {dict(effort)}")
        print(f"  por agente: {dict(agents.most_common())}")
        print(f"  costo equivalente (lo reporta el SDK; con suscripción no se cobra por corrida): {money(cost)}")
    decks = sorted(glob.glob(str(CASE / "slides" / "decks" / "*" / "caseos-run.json")))
    for p in decks:
        r = jload(p)
        u = r.get("usage") or {}
        mins = f", {u['ms'] / 60000:.0f} min" if u.get("ms") and u["ms"] > 60000 else ""
        c = r.get("cost_usd")
        print(f"  Visual Storyteller · {Path(p).parent.name}: {money(c) if isinstance(c, (int, float)) else 's/d'}{mins}")
    jobs = glob.glob(str(CASE / "audit" / "jobs" / "*.json"))
    print(f"  trabajos en segundo plano con su traza: {len(jobs)}")

    acts = []
    act = CASE / "audit" / "activity.jsonl"
    if act.exists():
        acts = [json.loads(line) for line in act.read_text(encoding="utf-8").splitlines() if line.strip()]
    if acts:
        who = collections.Counter(a.get("actor") for a in acts)
        delegated = sum(1 for a in acts if "vía Claude" in (a.get("summary") or ""))
        print(f"\nBitácora · {len(acts)} eventos, de {acts[0]['ts'][:16]} a {acts[-1]['ts'][:16]}")
        print(f"  por autor: {dict(who.most_common(10))}")
        print(f"  acciones que Hugo delegó en Claude Code (marcadas «vía Claude»): {delegated}")

    print("\nEntidades del caso")
    for d, label in [("evidence/findings", "hallazgos"), ("evidence/tables", "tablas de evidencia"),
                     ("hypotheses", "hipótesis"), ("questions", "preguntas"), ("research", "investigaciones"),
                     ("cos/alerts", "alertas del Chief of Staff"), ("decisions", "decisiones"),
                     ("story/claims", "afirmaciones de la historia"), ("slides/specs", "láminas registradas")]:
        files = glob.glob(str(CASE / d / "*.yaml"))
        extra = ""
        if d == "evidence/findings":
            states = collections.Counter(review(p) for p in files)
            acc = sum(v for (s, b), v in states.items() if s == "accepted")
            extra = f" · aceptados: {acc}, por revisar: {sum(v for (s, _), v in states.items() if s == 'proposed')}"
        if d == "decisions":
            actors = collections.Counter()
            for p in files:
                txt = open(p, encoding="utf-8").read()
                m = re.search(r"^origin:\s*\n\s+actor:\s*(\S+)", txt, re.M)
                actors[m.group(1) if m else "?"] += 1
            extra = f" · por autor: {dict(actors)}"
        print(f"  {label}: {len(files)}{extra}")
    snaps = [d for d in glob.glob(str(CASE / "snapshots" / "*" / "*")) if os.path.isdir(d)]
    print(f"  snapshots al marcar cada fase como lista: {len(snaps)}")

    eda = [jload(p) for p in sorted(glob.glob(str(EDA / "investigations" / "runs" / "*.json")))]
    eda = [r for r in eda if r]
    if eda:
        models = collections.Counter()

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in ("model", "modelo") and isinstance(v, str):
                        models[v] += 1
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        for r in eda:
            walk(r)
        names = sorted(Path(p).stem for p in glob.glob(str(EDA / "investigations" / "runs" / "*.json")))
        print(f"\nBusiness Exploration Workspace · {len(eda)} corridas del agente de EDA ({names[0][4:12]} a {names[-1][4:12]})")
        print(f"  modelos en sus registros: {dict(models)}")
        print(f"  investigación dorada: {len(glob.glob(str(EDA / 'investigations' / 'golden' / '*.json')))} · "
              f"preguntas del caso: {len(glob.glob(str(EDA / 'investigations' / 'caso' / '*.json')))}")


if __name__ == "__main__":
    main()
