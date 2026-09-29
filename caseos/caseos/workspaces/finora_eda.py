"""Adapter to the existing Business Exploration Workspace (finora-eda).

CaseOS never modifies finora-eda. It reads the workspace's own artifacts (brain/, investigations/, supporting CSVs)
and, when live analytics is requested, runs the workspace's own investigator in-process (agent.orchestrator.run)
and mounts the workspace UI + API under /ws/finora. Everything the workspace produces keeps its own lineage
(evidence IDs, data and brain versions); CaseOS adds the handoff contract (EvidenceTable) on top.
"""
from __future__ import annotations

import csv
import functools
import json
import sys
from pathlib import Path

from .. import config
from ..evidence import make_table, visual_to_preferred
from ..util import read_yaml

SYSTEM = "finora-eda (Business Exploration Workspace)"


class FinoraWorkspace:
    kind = "finora-eda"
    label = "Finora · Business Exploration Workspace"

    def __init__(self, path: Path):
        self.root = Path(path).resolve()

    # ------------------------------------------------------------------ status
    @property
    def available(self) -> bool:
        return (self.root / "agent" / "orchestrator.py").exists() and (self.root / "brain").exists()

    def info(self) -> dict:
        return {"kind": self.kind, "label": self.label, "path": str(self.root), "available": self.available,
                "ui": "/ws/finora/" if self.available else None,
                "git_head": _git_head(self.root), "reuse": "in-process: agent/ (investigador, tools, validador, gramática "
                                                           "visual), app/server.py, templates/ (UI)"}

    # ------------------------------------------------------------------ brain (read-only)
    @functools.cached_property
    def metrics(self) -> dict:
        m = read_yaml(self.root / "brain" / "semantic" / "metrics.yaml", {}) or {}
        return {x["id"]: x for x in m.get("metrics", [])}

    @functools.cached_property
    def issues(self) -> dict:
        m = read_yaml(self.root / "brain" / "data" / "known_quality_issues.yaml", {}) or {}
        items = m.get("issues") or m.get("problemas") or []
        return {x["id"]: x for x in items if isinstance(x, dict) and x.get("id")}

    def canonical(self) -> list[dict]:
        return (read_yaml(self.root / "brain" / "evidence" / "canonical_findings.yaml", {}) or {}).get("hallazgos", [])

    def case_questions(self) -> dict:
        return read_yaml(self.root / "brain" / "business" / "case_questions.yaml", {}) or {}

    def answers(self) -> dict:
        return read_yaml(self.root / "brain" / "business" / "answers.yaml", {}) or {}

    # ------------------------------------------------------------------ investigations (read-only)
    def case_answer(self, wid: str) -> dict | None:
        p = self.root / "investigations" / "caso" / f"{wid}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def golden(self, qid: str) -> dict | None:
        p = self.root / "investigations" / "golden" / f"{qid}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def run(self, inv_id: str) -> dict | None:
        for d in ("runs", "caso", "golden"):
            p = self.root / "investigations" / d / f"{inv_id}.json"
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        for p in (self.root / "investigations" / "caso").glob("*.json"):
            dct = json.loads(p.read_text(encoding="utf-8"))
            if dct.get("id") == inv_id:
                return dct
        return None

    def runs(self, limit: int = 40) -> list[dict]:
        out = []
        seen = set()
        for sub in ("caso", "golden", "runs"):
            d = self.root / "investigations" / sub
            if not d.exists():
                continue
            for p in sorted(d.glob("*.json"), reverse=True):
                try:
                    dct = json.loads(p.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                if dct.get("id") in seen:
                    continue
                seen.add(dct.get("id"))
                out.append(run_summary(dct, source=sub))
        return sorted(out, key=lambda r: r.get("finished_ms") or r.get("started_ms") or 0, reverse=True)[:limit]

    def narratives(self) -> list[dict]:
        d = self.root / "narratives"
        out = []
        if d.exists():
            for p in sorted(d.glob("NAR-*.json")):
                dct = json.loads(p.read_text(encoding="utf-8"))
                out.append({"id": dct["id"], "titulo": dct.get("titulo"), "audiencia": dct.get("audiencia"),
                            "objetivo": dct.get("objetivo"), "piezas": len(dct.get("piezas") or []),
                            "tiene_presentacion": bool(dct.get("presentacion")), "path": str(p.relative_to(self.root))})
        return out

    # ------------------------------------------------------------------ handoff: evidence → EvidenceTable
    def claim_table(self, run: dict, claim_id: str, *, table_key: str) -> dict:
        """Deterministic EvidenceTable for an accepted claim of a workspace investigation."""
        claim = run["claims"][claim_id]
        ev = {e["id"]: e for e in run.get("evidencia", [])}
        used = [ev[e] for e in claim.get("apoyo", []) if e in ev]
        columns, rows, units, defs, sources, queries, filters, periods = _merge_evidence(used, self)
        vis = next((v for v in (run.get("visuals") or {}).values() if v.get("claim_id") == claim_id), None)
        caveats = []
        for e in used:
            for cid in e.get("caveat_ids") or []:
                iss = self.issues.get(cid)
                caveats.append(f"{cid}: {iss.get('titulo') if iss else cid}")
        for cv in claim.get("caveats") or []:
            iss = self.issues.get(cv)
            caveats.append(f"{cv}: {iss.get('titulo') if iss else cv}")
        caveats = list(dict.fromkeys(caveats)) or ["Monto pagado observado: no es MRR contractual validado (sin precios, descuentos ni estado de suscripción)."]
        return make_table(
            table_key=table_key, title=_short(claim["texto"]), question=run.get("pregunta", ""), columns=columns,
            rows=rows, units=units, definitions=defs, message=claim["texto"],
            source={"system": SYSTEM, "dataset": "Transactions · Industry · S&M_spend (data/raw)",
                    "warehouse": "warehouse/finora.duckdb (mart de solo lectura)", "evidence_ids": [e["id"] for e in used],
                    "tools": sorted({e["tool"] for e in used}), "data_version": (used[0].get("data_version") if used else None),
                    "brain_version": (used[0].get("brain_version") if used else None)},
            query="\n\n".join(q for q in queries if q), transformation="; ".join(sources),
            filters=filters, period=periods[0] if periods else {}, grain=_grain(used),
            analysis_id=f"{run['id']} · {claim_id}", limitations=caveats,
            preferred_visual=visual_to_preferred((vis or {}).get("spec")), visual_artifact=(vis or {}).get("spec"))

    def canonical_table(self, h: dict, *, table_key: str) -> dict:
        labels = h.get("etiquetas") or {}
        rows = [[labels.get(k, k), str(v)] for k, v in (h.get("evidencia") or {}).items()]
        return make_table(
            table_key=table_key, title=_short(h["afirmacion"]), question=h.get("dominio", ""), columns=["Dato", "Valor"],
            rows=rows, units={"Valor": "según etiqueta"}, definitions={k: labels.get(k, k) for k in (h.get("evidencia") or {})},
            message=h["afirmacion"],
            source={"system": SYSTEM, "dataset": "brain/evidence/canonical_findings.yaml",
                    "generated_by": "finora_eda.py · check_claims()", "claim_id": h["id"]},
            transformation="Hallazgo canónico verificado en código por el pipeline de la Fase 1",
            analysis_id=f"canonical · {h['id']}", limitations=["Monto pagado observado: no es MRR contractual validado."],
            preferred_visual="table", visual_artifact=h.get("grafica"))

    def csv_rows(self, rel: str) -> list[dict]:
        p = self.root / rel
        with p.open(encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ------------------------------------------------------------------ live analytics (in-process reuse)
    def ensure_importable(self) -> None:
        root = str(self.root)
        if root not in sys.path:
            sys.path.insert(0, root)

    def new_investigation(self, question: str, context: dict | None = None):
        """The workspace's own Investigation object (events stream while it runs)."""
        self.ensure_importable()
        from agent.config import DB_PATH  # type: ignore
        from agent.state import Investigation  # type: ignore
        from agent.warehouse import build  # type: ignore
        if not DB_PATH.exists():
            build()
        return Investigation(pregunta=question, playbook_id="libre", contexto=context)

    async def run_investigation(self, inv):
        """Runs the workspace's own investigator (agent.orchestrator.run) to completion."""
        self.ensure_importable()
        from agent.orchestrator import run as finora_run  # type: ignore
        await finora_run(inv)
        return inv

    def mount(self, app) -> bool:
        if not self.available:
            return False
        self.ensure_importable()
        try:
            from app.server import app as finora_app  # type: ignore
        except Exception as e:  # noqa: BLE001
            print(f"[caseos] workspace finora-eda no se pudo montar: {e}")
            return False
        from fastapi.responses import HTMLResponse
        root = self.root

        @app.get("/ws/finora/", response_class=HTMLResponse, include_in_schema=False)
        def _workspace_html():
            html = (root / "finora_eda.html").read_text(encoding="utf-8")
            flag = ('<script>window.FINORA_LIVE = {"api": "/ws/finora/api", "preguntas": ["Q2"], "libre": true, '
                    '"narrativas": true, "caso": true};</script>\n')
            return html.replace("<script>\nconst DATA", flag + "<script>\nconst DATA", 1)

        app.mount("/ws/finora", finora_app)
        return True


def run_summary(d: dict, source: str = "runs") -> dict:
    comp = d.get("narrativa") or {}
    rc = d.get("respuesta_caso") or {}
    head = ((comp.get("respuesta_ejecutiva") or {}).get("titular") or (rc.get("respuesta") or {}).get("titular") or "")
    return {"id": d.get("id"), "pregunta": d.get("pregunta"), "status": d.get("status"), "caso_id": d.get("caso_id"),
            "source": source, "headline": head, "claims": len([c for c in (d.get("claims") or {}).values() if c.get("aceptada")]),
            "visuals": len(d.get("visuals") or {}), "started_ms": d.get("started_ms"), "finished_ms": d.get("finished_ms"),
            "error": d.get("error"), "cost": sum((u or {}).get("costo_equivalente_usd") or 0 for u in (d.get("uso") or {}).values() if isinstance(u, dict))}


def _short(text: str, n: int = 110) -> str:
    t = text.split(":")[0] if len(text) > n and ":" in text[:n] else text
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def _grain(evs: list[dict]) -> str:
    g = [((e.get("params") or {}).get("grano")) for e in evs if (e.get("params") or {}).get("grano")]
    return ", ".join(dict.fromkeys(g)) or "según evidencia"


def _merge_evidence(evs: list[dict], ws: FinoraWorkspace):
    """One table from the claim's evidence: same-shaped single-row metric results become rows of one table."""
    units, defs, sources, queries, filters, periods = {}, {}, [], [], [], []
    _dedupe = lambda xs: list(dict.fromkeys(xs))  # noqa: E731
    for e in evs:
        p = e.get("params") or {}
        for mid in [p.get("metric_id")] + list(e.get("metric_ids") or []):
            if mid and mid in ws.metrics:
                m = ws.metrics[mid]
                defs[m.get("nombre", mid)] = (m.get("definicion") or m.get("descripcion") or "").strip()
        if p.get("periodo"):
            periods.append(p["periodo"])
            filters.append(f"periodo {p['periodo'].get('desde')}–{p['periodo'].get('hasta')}")
        if p.get("segmento") or p.get("filtro"):
            filters.append(str(p.get("segmento") or p.get("filtro")))
        sources.append(f"{e['id']} · {e['tool']} · {e.get('method', '')}".strip(" ·"))
        if e.get("query_text"):
            queries.append(f"-- {e['id']}\n{e['query_text']}")
    single = [e for e in evs if len((e.get("result") or {}).get("filas") or []) == 1 and (e.get("result") or {}).get("columnas")]
    if len(evs) > 1 and len(single) == len(evs):
        # rows = one per evidence: [metric label, value columns...]
        width = max(len(e["result"]["columnas"]) for e in evs)
        first = evs[0]["result"]["columnas"]
        lead = first[1].get("nombre", "") if len(first) > 1 else ""
        generic = []
        for i, c in enumerate(first[1:]):
            name = c.get("nombre", c.get("id", ""))
            rest = name.replace(lead, "", 1).strip() if lead and name.startswith(lead) else name
            generic.append("Valor" if i == 0 else (rest[:1].upper() + rest[1:] if rest else f"Valor {i + 1}"))
        columns = ["Métrica"] + generic
        columns = columns + [f"col{i}" for i in range(len(columns), width)]
        rows = []
        for e in evs:
            cols = e["result"]["columnas"]
            r = e["result"]["filas"][0]
            label = cols[1].get("nombre") if len(cols) > 1 else e["id"]
            vals = [r.get(c["id"]) for c in cols[1:]]
            rows.append([label] + vals + [None] * (width - 1 - len(vals)))
            for c in cols[1:]:
                units[c.get("nombre", c["id"])] = c.get("formato", "")
        columns = [c for c in columns if not c.startswith("col")]
        rows = [r[: len(columns)] for r in rows]
        return columns, rows, units, defs, sources, queries, _dedupe(filters), periods
    columns, rows = [], []
    for e in evs[:1] or []:
        cols = (e.get("result") or {}).get("columnas") or []
        columns = [c.get("nombre", c.get("id")) for c in cols if c.get("id") != "_clave"]
        rows = [[r.get(c["id"]) for c in cols if c.get("id") != "_clave"] for r in (e.get("result") or {}).get("filas") or []]
        for c in cols:
            if c.get("formato"):
                units[c.get("nombre", c["id"])] = c["formato"]
    if not columns:
        vals = {}
        for e in evs:
            vals.update((e.get("result") or {}).get("valores") or {})
        columns = ["Dato", "Valor"]
        rows = [[k, v] for k, v in vals.items()]
    return columns, rows, units, defs, sources, queries, _dedupe(filters), periods


def _git_head(root: Path) -> str | None:
    try:
        head = (root / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref:"):
            ref = root / ".git" / head.split(" ", 1)[1]
            return ref.read_text().strip()[:7] if ref.exists() else None
        return head[:7]
    except OSError:
        return None


@functools.lru_cache(maxsize=4)
def _cached(path: str) -> FinoraWorkspace:
    return FinoraWorkspace(Path(path))


def adapter(ws: dict) -> FinoraWorkspace:
    p = ws.get("path") or str(config.FINORA_EDA_PATH)
    path = Path(p)
    if not path.is_absolute():
        path = (config.ROOT / path).resolve()
    return _cached(str(path))
