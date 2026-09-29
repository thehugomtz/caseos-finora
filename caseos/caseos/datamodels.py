"""Data models a case binds to: real, layered, queryable read-only, and checkable.

Today there is one, Finora, from the Business Exploration Workspace (finora-eda), in three layers:

  raw      the three CSV files exactly as delivered: every column as text, with file hash, size and rows
  staging  typed views over raw with the Phase 1 typing rules (finora_eda.py · audit_*): numeric ID, month from
           M/D/AAAA, amount × 10.000 → COP, S&M money without "$", industry trimmed. No business logic.
  mart     the workspace's DuckDB mart (the layer its Analytics agent queries), attached read-only

The workspace builds the mart from its Phase 1 outputs, not from these staging views. The reconciliation checks prove
both paths agree (rows, monthly totals to the cent, customers, S&M) and re-run the workspace's own parity tests, so
"comprobable" is literal: every check carries the SQL that proves it.

Nothing here writes to finora-eda: one in-memory DuckDB per process, the warehouse attached READ_ONLY, external access
disabled and configuration locked after setup; queries are one SELECT over raw/staging/mart, row- and time-limited.
"""
from __future__ import annotations

import hashlib
import math
import re
import threading
import time
from decimal import Decimal
from pathlib import Path

import duckdb
import sqlglot
from sqlglot import exp

from . import config
from .evidence import Num, supported, table_numbers
from .util import now_iso

ROW_LIMIT = 500
TIMEOUT_S = 20
SCALE_TO_COP = 10_000
LAYERS = [
    {"id": "raw", "label": "Raw", "desc": "Los archivos tal como llegaron. Todo es texto; nada se corrige ni se interpreta."},
    {"id": "staging", "label": "Staging", "desc": "Tipado y limpieza mínima con las reglas de la Fase 1. Sin lógica de negocio."},
    {"id": "mart", "label": "Mart · procesado", "desc": "Tablas analíticas del workspace: banderas, movimientos, cohortes y métricas. "
                                                      "Es lo que consulta el agente de Analytics."},
]
SM_COLS = [("PaidMedia", "paid_media"), ("Travel", "travel"), ("PublicidadNoWeb", "publicidad_no_web"), ("Freelance", "freelance"),
           ("SoftwareTools", "software_tools"), ("Team", "team"), ("PayrollExpenses", "payroll_expenses")]

STAGING_SQL = {
    "stg_customers": r"""SELECT TRY_CAST(regexp_extract(trim("ID"), '^Cliente (\d+)$', 1) AS INTEGER) AS customer_id,
       trim("Industria") AS industry
FROM raw.industry
WHERE trim(coalesce("ID", '')) <> '' OR trim(coalesce("Industria", '')) <> ''""",
    "stg_customer_month": """SELECT TRY_CAST(trim("ID") AS INTEGER) AS customer_id,
       strftime(try_strptime(trim("month"), '%m/%d/%Y'), '%Y-%m') AS month,
       TRY_CAST(trim("amount") AS DECIMAL(18,6)) AS amount,
       TRY_CAST(trim("amount") AS DECIMAL(18,6)) * 10000 AS amount_cop
FROM raw.transactions""",
    "stg_sm_spend": "SELECT month, rubro, amount FROM (UNPIVOT (SELECT trim(\"Month\") AS month, "
                    + ", ".join(f"TRY_CAST(replace(trim(\"{src}\"), '$', '') AS DECIMAL(12,3)) AS {dst}" for src, dst in SM_COLS)
                    + " FROM raw.sm_spend) ON " + ", ".join(d for _, d in SM_COLS) + " INTO NAME rubro VALUE amount)",
}

TABLES = {
    "raw.transactions": {"file": "Transactions.csv", "grain": "fila del archivo · cliente × mes",
                         "desc": "Pagos mensuales por cliente tal cual llegaron: ID, month (M/D/AAAA) y amount sin escala."},
    "raw.industry": {"file": "Industry.csv", "grain": "fila del archivo · cliente",
                     "desc": "Industria de cada cliente («Cliente N» → industria), tal cual llegó."},
    "raw.sm_spend": {"file": "S&M_spend.csv", "grain": "fila del archivo · mes",
                     "desc": "Gasto mensual de Sales & Marketing por rubro, en texto con «$» (unidad no documentada)."},
    "staging.stg_customers": {"grain": "cliente", "parents": ["raw.industry"],
                              "desc": "ID numérico e industria limpia; se descartan las filas vacías."},
    "staging.stg_customer_month": {"grain": "cliente × mes", "parents": ["raw.transactions"],
                                   "desc": "Mes AAAA-MM, monto tipado y monto en COP (× 10.000)."},
    "staging.stg_sm_spend": {"grain": "mes × rubro", "parents": ["raw.sm_spend"],
                             "desc": "Gasto en formato largo y tipado, sin «$». Unidad no documentada: no se convierte a COP."},
    "mart.customer_month": {"grain": "cliente × mes", "parents": ["staging.stg_customer_month", "staging.stg_customers"],
                            "via": "Fase 1 (finora_eda.py) → finora_analytical_dataset.csv; los checks prueban que cuadra con staging",
                            "desc": "Panel analítico: monto observado, MRR pagado, banderas (alta, churn observado, reactivación, "
                                    "expansión, contracción), movimientos, tenure, cohorte y cosecha."},
    "mart.monthly_metrics_phase1": {"grain": "mes", "parents": ["mart.customer_month"], "via": "Fase 1 → finora_monthly_metrics.csv",
                                    "desc": "Métricas mensuales exactamente como las calculó la Fase 1 (referencia de paridad)."},
    "mart.monthly_metrics": {"grain": "mes", "parents": ["mart.customer_month"],
                             "desc": "Las métricas mensuales recalculadas en SQL desde customer_month; cuadran al centavo con la Fase 1."},
    "mart.sm_monthly": {"grain": "mes", "parents": ["mart.monthly_metrics_phase1", "staging.stg_sm_spend"],
                        "desc": "Gasto S&M por rubro y por grupo (generación de demanda, capacidad comercial, enablement)."},
    "mart.new_customers": {"grain": "alta", "parents": ["mart.customer_month"],
                           "desc": "Cada alta con su primer pago (M0), run-rate temprano, cohorte e industria."},
    "mart.vintage_month": {"grain": "cosecha × mes", "parents": ["mart.customer_month"],
                           "desc": "Clientes activos, MRR y MRR por cliente de cada cosecha."},
    "mart.churn_events": {"grain": "evento de churn observado", "parents": ["mart.customer_month"],
                          "desc": "Cada churn observado con su monto previo y los meses hasta volver a pagar."},
}
STAGING_COLS = {
    "customer_id": "ID numérico del cliente.", "industry": "Industria tal como viene en Industry.csv, sin espacios sobrantes.",
    "month": "Mes calendario AAAA-MM.", "amount": "Monto del archivo, tipado (sin escala).",
    "amount_cop": "amount × 10.000: monto en COP (la escala documentada del caso).", "rubro": "Rubro de gasto S&M.",
}


def _n(x) -> str:
    """12345 → 12.345 (Spanish thousands separator) without touching the surrounding text."""
    return f"{x:,}".replace(",", ".")


def _jsonable(v):
    if isinstance(v, Decimal):
        f = float(v)
        return f if math.isfinite(f) else None
    if isinstance(v, float):
        return v if math.isfinite(v) else None
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


# ------------------------------------------------------------------------------------------ SQL guard
ALLOWED_SCHEMAS = {"raw", "staging", "mart"}
ALLOWED_TABLE_FUNCS = {"range", "generate_series", "unnest"}


def guard_sql(sql: str) -> str | None:
    """None when the query is one read-only SELECT over raw/staging/mart; otherwise the reason it is refused."""
    s = (sql or "").strip().rstrip(";").strip()
    if not s:
        return "Escribe una consulta."
    try:
        stmts = [x for x in sqlglot.parse(s, read="duckdb") if x is not None]
    except sqlglot.errors.ParseError as e:
        return f"El SQL no se pudo leer: {str(e)[:300]}"
    if len(stmts) != 1:
        return "Una sola consulta SELECT a la vez."
    st = stmts[0]
    if not isinstance(st, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        return "Solo consultas SELECT: el modelo es de solo lectura."
    for bad in (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter, exp.Command):
        if st.find(bad):
            return "Solo consultas SELECT: el modelo es de solo lectura."
    ctes = {c.alias_or_name.lower() for c in st.find_all(exp.CTE)}
    for t in st.find_all(exp.Table):
        if isinstance(t.this, exp.Func) or isinstance(t.this, exp.Anonymous):
            fname = (t.this.sql_name() if hasattr(t.this, "sql_name") else str(t.this.this)).lower()
            if fname not in ALLOWED_TABLE_FUNCS:
                return f"Función de tabla no permitida: {fname}."
            continue
        name, db, catalog = (t.name or "").lower(), (t.db or "").lower(), (t.catalog or "").lower()
        if catalog and catalog != "memory":
            return "Consulta las capas raw, staging o mart (sin catálogos externos)."
        if not db and name in ctes:
            continue
        if db not in ALLOWED_SCHEMAS:
            return f"«{t.sql()}» no es una tabla del modelo: usa raw.*, staging.* o mart.*."
    return None


# ------------------------------------------------------------------------------------------ the Finora model
class FinoraModel:
    id = "finora"
    label = "Finora · modelo analítico"
    source = "finora-eda · Business Exploration Workspace"

    def __init__(self, root: Path | None = None):
        self.root = Path(root or config.FINORA_EDA_PATH)
        self.raw_dir = self.root / "data" / "raw"
        self.warehouse = self.root / "warehouse" / "finora.duckdb"
        self._con = None
        self._lock = threading.Lock()
        self._built_key = None
        self._catalog = None
        self._checks = None

    # ---------------------------------------------------------------- availability and setup
    @property
    def available(self) -> bool:
        return self.warehouse.exists() and all((self.raw_dir / TABLES[t]["file"]).exists() for t in TABLES if t.startswith("raw."))

    @property
    def workspace(self) -> dict:
        return {"type": "finora-eda", "path": str(self.root), "label": "Finora · Business Exploration Workspace"}

    def _key(self):
        files = [self.warehouse] + [self.raw_dir / TABLES[t]["file"] for t in TABLES if t.startswith("raw.")]
        return tuple((str(f), f.stat().st_mtime_ns, f.stat().st_size) for f in files)

    def _base(self):
        with self._lock:
            key = self._key()
            if self._con is not None and key == self._built_key:
                return self._con
            if self._con is not None:
                self._con.close()
            con = duckdb.connect()
            con.execute(f"ATTACH '{str(self.warehouse).replace(chr(39), chr(39) * 2)}' AS wh (READ_ONLY)")
            con.execute("CREATE SCHEMA raw; CREATE SCHEMA staging; CREATE SCHEMA mart;")
            self._files = {}
            for t, spec in TABLES.items():
                if not t.startswith("raw."):
                    continue
                p = self.raw_dir / spec["file"]
                con.execute(f"CREATE TABLE {t} AS SELECT * FROM read_csv('{str(p).replace(chr(39), chr(39) * 2)}', header = true, "
                            "all_varchar = true)")
                b = p.read_bytes()
                self._files[t] = {"file": spec["file"], "path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                                  "utf8_bom": b.startswith(b"\xef\xbb\xbf")}
            for name, sql in STAGING_SQL.items():
                con.execute(f"CREATE VIEW staging.{name} AS {sql}")
            for (name,) in con.execute("SELECT table_name FROM information_schema.tables WHERE table_catalog = 'wh' AND "
                                       "table_schema = 'mart' ORDER BY 1").fetchall():
                con.execute(f"CREATE VIEW mart.{name} AS SELECT * FROM wh.mart.{name}")
            con.execute("SET enable_external_access = false")
            con.execute("SET lock_configuration = true")
            self._con, self._built_key, self._catalog, self._checks = con, key, None, None
            self._loaded_at = now_iso()
            return con

    def cursor(self):
        return self._base().cursor()

    # ---------------------------------------------------------------- catalog
    def catalog(self) -> dict:
        self._base()
        if self._catalog is not None:
            return self._catalog
        cur = self.cursor()
        defs = self._metric_defs()
        mart_views = {r[0]: r[1] for r in cur.execute(
            "SELECT view_name, sql FROM duckdb_views() WHERE database_name = 'wh' AND schema_name = 'mart'").fetchall()}
        wh_tables = {r[0] for r in cur.execute("SELECT table_name FROM information_schema.tables WHERE table_catalog = 'wh' "
                                               "AND table_schema = 'mart'").fetchall()}
        tables = []
        for full in [t for t in TABLES if t.split(".")[0] != "mart"] + sorted(f"mart.{n}" for n in wh_tables):
            schema, name = full.split(".")
            spec = TABLES.get(full, {"grain": "", "desc": "Tabla del mart del workspace.", "parents": ["mart.customer_month"]})
            cols = cur.execute(f"DESCRIBE {full}").fetchall()
            rows = cur.execute(f"SELECT COUNT(*) FROM {full}").fetchone()[0]
            if schema == "raw":
                definition, kind = f"read_csv('data/raw/{spec['file']}', header = true, all_varchar = true)", "archivo"
            elif schema == "staging":
                definition, kind = STAGING_SQL[name], "vista"
            elif name in mart_views:
                definition, kind = mart_views[name], "vista"
            else:
                definition, kind = f"CREATE TABLE mart.{name} AS … ({spec.get('via', 'construida por el workspace')})", "tabla"
            tables.append({
                "id": full, "schema": schema, "name": name, "kind": kind, "grain": spec.get("grain", ""), "desc": spec.get("desc", ""),
                "rows": rows, "parents": spec.get("parents", []), "via": spec.get("via"), "definition": definition,
                "file": self._files.get(full),
                "columns": [{"name": c[0], "type": c[1], "definition": ("texto tal cual del archivo" if schema == "raw" else
                                                                        STAGING_COLS.get(c[0]) if schema == "staging" else
                                                                        defs.get(c[0], ""))} for c in cols]})
        self._catalog = {"id": self.id, "label": self.label, "source": self.source, "root": str(self.root),
                         "warehouse": str(self.warehouse), "loaded_at": self._loaded_at, "layers": LAYERS, "tables": tables,
                         "read_only": True, "row_limit": ROW_LIMIT, "timeout_s": TIMEOUT_S}
        return self._catalog

    def _metric_defs(self) -> dict:
        """Column definitions from the workspace's own documentation: the metric catalog (brain/semantic/metrics.yaml)
        and the customer × month column table in finora_eda_notes.md (§3.3)."""
        defs = {"vintage": "Cosecha: base previa (activos en ene-22), altas de feb-22 marcadas o cosecha del año de alta.",
                "year": "Año calendario del mes."}
        try:
            import yaml
            m = yaml.safe_load((self.root / "brain" / "semantic" / "metrics.yaml").read_text(encoding="utf-8")) or {}
            defs.update({x["id"]: x.get("definicion", "") for x in m.get("metrics", [])})
        except Exception:  # noqa: BLE001 - definitions are a nicety, never a failure
            pass
        try:
            for line in (self.root / "finora_eda_notes.md").read_text(encoding="utf-8").splitlines():
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if len(cells) == 2 and cells[0].startswith("`"):
                    for col in re.findall(r"`([a-z_0-9]+)`", cells[0]):
                        defs.setdefault(col, cells[1].replace("`", ""))
        except Exception:  # noqa: BLE001
            pass
        return defs

    def summary(self) -> dict:
        cat = self.catalog()
        by = {l["id"]: [t for t in cat["tables"] if t["schema"] == l["id"]] for l in LAYERS}
        chk = self.checks()
        return {"id": self.id, "label": self.label, "source": self.source, "available": True,
                "layers": [{"id": l["id"], "label": l["label"], "tables": len(by[l["id"]]),
                            "rows": sum(t["rows"] for t in by[l["id"]])} for l in LAYERS],
                "checks": {"ok": sum(1 for c in chk if c["status"] == "ok"), "total": len(chk),
                           "fail": sum(1 for c in chk if c["status"] == "fail")}}

    def brief_lines(self) -> list[str]:
        cat = self.catalog()
        s = self.summary()
        out = [f"Modelo de datos: {self.label} ({self.source}) — " + " · ".join(f"{l['label']} {l['tables']}" for l in s["layers"])
               + f"; {s['checks']['ok']}/{s['checks']['total']} checks de reconciliación OK."]
        for t in cat["tables"]:
            if t["schema"] in ("raw", "mart") and (t["schema"] == "raw" or t["name"] in ("customer_month", "monthly_metrics", "new_customers")):
                out.append(f"{t['id']} — {t['desc'].rstrip('.')} ({_n(t['rows'])} filas; grano {t['grain']})")
        return out

    # ---------------------------------------------------------------- data access
    def sample(self, table: str, limit: int = 20) -> dict:
        if table not in {t["id"] for t in self.catalog()["tables"]}:
            raise ValueError(f"{table} no es una tabla del modelo.")
        return self.query(f"SELECT * FROM {table}", limit=limit)

    def query(self, sql: str, limit: int = ROW_LIMIT) -> dict:
        problem = guard_sql(sql)
        if problem:
            raise ValueError(problem)
        limit = max(1, min(int(limit or ROW_LIMIT), 5000))
        cur = self.cursor()
        timer = threading.Timer(TIMEOUT_S, cur.interrupt)
        t0 = time.time()
        timer.start()
        try:
            rel = cur.execute(f"SELECT * FROM ({sql.strip().rstrip(';')}) AS q LIMIT {limit + 1}")
            cols = [d[0] for d in rel.description]
            rows = rel.fetchall()
        except duckdb.InterruptException:
            raise ValueError(f"La consulta tardó más de {TIMEOUT_S} s: agrega un filtro o agrega por mes.") from None
        except duckdb.Error as e:
            raise ValueError(f"DuckDB: {str(e).splitlines()[0][:400]}") from None
        finally:
            timer.cancel()
        return {"columns": cols, "rows": [[_jsonable(v) for v in r] for r in rows[:limit]], "truncated": len(rows) > limit,
                "ms": round((time.time() - t0) * 1000), "sql": sql.strip()}

    # ---------------------------------------------------------------- reconciliation checks
    def checks(self) -> list[dict]:
        self._base()
        if self._checks is not None:
            return self._checks
        cur = self.cursor()
        one = lambda q: cur.execute(q).fetchone()
        out = []

        def add(cid, title, status, detail, sql, numbers=None):
            out.append({"id": cid, "title": title, "status": status, "detail": detail, "sql": sql, "numbers": numbers or {}})

        q = ("SELECT (SELECT COUNT(*) FROM raw.transactions) AS raw_rows, COUNT(*) AS staging_rows,\n"
             "       COUNT(*) FILTER (WHERE customer_id IS NULL OR month IS NULL OR amount IS NULL) AS untyped\nFROM staging.stg_customer_month")
        raw_n, stg_n, bad = one(q)
        add("raw-staging-transactions", "Raw → staging: cada pago se tipa", "ok" if raw_n == stg_n and bad == 0 else "fail",
            f"{_n(raw_n)} filas en raw, {_n(stg_n)} en staging, {bad} sin tipar.", q,
            {"raw_rows": raw_n, "staging_rows": stg_n, "untyped": bad})

        q = ("SELECT (SELECT COUNT(*) FROM raw.industry) AS raw_rows, COUNT(*) AS staging_rows,\n"
             "       COUNT(*) FILTER (WHERE customer_id IS NULL) AS bad_ids, COUNT(DISTINCT customer_id) AS customers\nFROM staging.stg_customers")
        ir, isg, ibad, icust = one(q)
        add("raw-staging-industry", "Raw → staging: industrias", "ok" if ibad == 0 and icust == isg else "warn",
            f"{_n(ir)} filas en raw → {_n(isg)} clientes en staging ({ir - isg} vacía(s) descartada(s)); {ibad} ID con formato raro.",
            q, {"raw_rows": ir, "staging_rows": isg, "bad_ids": ibad})

        q = ("SELECT (SELECT COUNT(*) FROM staging.stg_customer_month) AS staging_rows,\n"
             "       (SELECT COUNT(*) FROM mart.customer_month) AS mart_rows,\n"
             "       (SELECT COUNT(DISTINCT customer_id) FROM staging.stg_customer_month) AS staging_customers,\n"
             "       (SELECT COUNT(DISTINCT customer_id) FROM mart.customer_month) AS mart_customers")
        sr, mr, sc, mc = one(q)
        add("staging-mart-rows", "Staging ↔ mart: mismas filas cliente × mes", "ok" if sr == mr and sc == mc else "fail",
            f"{_n(sr)} vs {_n(mr)} filas; {_n(sc)} vs {_n(mc)} clientes.", q,
            {"staging_rows": sr, "mart_rows": mr, "staging_customers": sc, "mart_customers": mc})

        q = ("WITH s AS (SELECT month, SUM(amount_cop) AS v FROM staging.stg_customer_month GROUP BY month),\n"
             "     m AS (SELECT month, total_paid_mrr_cop AS v FROM mart.monthly_metrics)\n"
             "SELECT COUNT(*) AS months, MAX(ABS(s.v - m.v)) AS max_diff_cop,\n"
             "       COUNT(*) FILTER (WHERE s.month IS NULL OR m.month IS NULL) AS unmatched\nFROM s FULL JOIN m USING (month)")
        months, diff, unmatched = one(q)
        diff = float(diff or 0)
        add("staging-mart-amount", "Staging ↔ mart: monto por mes al centavo", "ok" if unmatched == 0 and diff < 0.005 else "fail",
            f"{months} meses; diferencia máxima COP {diff:.2f}; {unmatched} mes(es) sin pareja.", q,
            {"months": months, "max_diff_cop": diff, "unmatched": unmatched})

        q = ("SELECT COUNT(DISTINCT t.customer_id) AS customers_without_industry\nFROM staging.stg_customer_month t\n"
             "LEFT JOIN staging.stg_customers c USING (customer_id)\nWHERE c.customer_id IS NULL")
        (noind,) = one(q)
        add("industry-coverage", "Cobertura: cada cliente con pagos tiene industria", "ok" if noind == 0 else "warn",
            f"{noind} cliente(s) con pagos sin industria.", q, {"customers_without_industry": noind})

        q = ("WITH s AS (SELECT month, SUM(amount) AS v FROM staging.stg_sm_spend GROUP BY month),\n"
             "     m AS (SELECT month, total_sm_spend AS v FROM mart.sm_monthly)\n"
             "SELECT COUNT(*) AS months, MAX(ABS(s.v - m.v)) AS max_diff,\n"
             "       COUNT(*) FILTER (WHERE s.month IS NULL OR m.month IS NULL) AS unmatched\nFROM s FULL JOIN m USING (month)")
        sm_m, sm_d, sm_u = one(q)
        sm_d = float(sm_d or 0)
        add("staging-mart-sm", "Staging ↔ mart: gasto S&M por mes", "ok" if sm_u == 0 and sm_d < 0.0005 else "fail",
            f"{sm_m} meses; diferencia máxima {sm_d:.4f} (unidad del archivo); {sm_u} mes(es) sin pareja.", q,
            {"months": sm_m, "max_diff": sm_d, "unmatched": sm_u})

        out.append(self._workspace_parity())
        self._checks = out
        return out

    def _workspace_parity(self) -> dict:
        title = "Mart ↔ Fase 1: pruebas de paridad del workspace"
        try:
            from .workspaces.finora_eda import FinoraWorkspace
            FinoraWorkspace(self.root).ensure_importable()
            from agent.warehouse import parity  # type: ignore
            con = duckdb.connect(str(self.warehouse), read_only=True)
            try:
                res = parity(con)
            finally:
                con.close()
            return {"id": "workspace-parity", "title": title, "status": "ok",
                    "detail": f"{res.get('pruebas_de_paridad')} pruebas del workspace pasan: conteos y montos al centavo contra la Fase 1 "
                              f"({_n(res.get('filas_cliente_mes'))} filas cliente × mes, {_n(res.get('altas'))} altas).",
                    "sql": "agent.warehouse.parity() — el mismo código que corre finora-eda al construir su mart", "numbers": res}
        except AssertionError as e:
            return {"id": "workspace-parity", "title": title, "status": "fail", "detail": f"Falló: {e}", "sql": "agent.warehouse.parity()",
                    "numbers": {}}
        except Exception as e:  # noqa: BLE001 - the model still works; the check says why it could not run
            return {"id": "workspace-parity", "title": title, "status": "warn", "detail": f"No se pudo correr: {type(e).__name__}: {e}",
                    "sql": "agent.warehouse.parity()", "numbers": {}}

    # ---------------------------------------------------------------- verify an evidence table against the model
    def verify_table(self, table: dict) -> dict:
        """Re-run the table's own SQL on the model and check every figure in its rows comes back."""
        q = (table.get("query") or "").strip()
        expected = table_numbers(table)
        if not q:
            return {"status": "no_query", "detail": "Esta tabla no trae consulta: su comprobación es la fuente citada "
                                                    f"({(table.get('source') or {}).get('dataset', '—')}).", "total": len(expected)}
        chunks = [c.strip() for c in re.split(r"\n\s*\n", q) if c.strip()]
        got, runs = [], []
        for c in chunks:
            try:
                r = self.query(c, limit=5000)
                runs.append({"sql": c, "ok": True, "rows": len(r["rows"]), "ms": r["ms"]})
                got += [float(v) for row in r["rows"] for v in row if isinstance(v, (int, float)) and not isinstance(v, bool)]
            except ValueError as e:
                runs.append({"sql": c, "ok": False, "error": str(e)})
        missing = []
        for x in expected:
            dec = len(repr(x).split(".")[1]) if "." in repr(x) and not float(x).is_integer() else 0
            if not supported(Num(float(x), repr(x), decimals=min(dec, 6)), got):
                missing.append(x)
        matched = len(expected) - len(missing)
        status = "ok" if expected and not missing and all(r["ok"] for r in runs) else ("partial" if matched else "fail")
        return {"status": status, "matched": matched, "total": len(expected), "missing": missing[:12], "queries": runs,
                "detail": f"{matched} de {len(expected)} cifras reaparecen al volver a correr su consulta sobre el modelo."}


# ------------------------------------------------------------------------------------------ registry and case binding
_MODELS: dict[str, FinoraModel] = {}


def _registry() -> dict:
    if not _MODELS:
        m = FinoraModel()
        _MODELS[m.id] = m
    return _MODELS


def available() -> list[dict]:
    out = []
    for m in _registry().values():
        if not m.available:
            out.append({"id": m.id, "label": m.label, "source": m.source, "available": False,
                        "note": f"No encuentro {m.warehouse} o los CSV de data/raw."})
            continue
        try:
            out.append(m.summary())
        except Exception as e:  # noqa: BLE001
            out.append({"id": m.id, "label": m.label, "source": m.source, "available": False, "note": f"{type(e).__name__}: {e}"})
    return out


def get(model_id: str) -> FinoraModel:
    m = _registry().get(model_id)
    if not m:
        raise ValueError(f"Modelo de datos desconocido: {model_id}")
    if not m.available:
        raise ValueError(f"{m.label} no está disponible en esta máquina.")
    return m


def for_case(store) -> FinoraModel | None:
    mid = (store.meta().get("data_model") or {}).get("id")
    return get(mid) if mid else None


def bind(store, model_id: str, *, actor: str = "hugo") -> dict:
    from . import briefing
    m = get(model_id)
    meta = store.meta()
    prev = (meta.get("data_model") or {}).get("id")
    meta["data_model"] = {"id": m.id, "label": m.label, "source": m.source, "bound_at": now_iso(), "bound_by": actor}
    meta["workspace"] = m.workspace                      # the Analytics agent consults the same model
    store.save_meta(meta)
    briefing.set_section(store, "data_available", m.brief_lines(), actor=actor, basis="modelo de datos elegido por Hugo")
    store.log(actor, "bound", [], f"Modelo de datos del caso: {m.label}" + (f" (antes {prev})" if prev and prev != m.id else ""),
              material=True, data={"model": m.id})
    return meta["data_model"]


def unbind(store, *, actor: str = "hugo") -> None:
    meta = store.meta()
    if not meta.get("data_model"):
        return
    old = meta.pop("data_model")
    if old.get("id") == "finora" and (meta.get("workspace") or {}).get("type") == "finora-eda":
        meta.pop("workspace", None)
    store.save_meta(meta)
    store.log(actor, "unbound", [], f"El caso ya no usa el modelo de datos {old.get('label')}", material=True)
