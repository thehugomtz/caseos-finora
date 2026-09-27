"""Capa SQL de la slice (DuckDB) con paridad exacta contra la Fase 1.

Arquitectura v1.2 §9, plan B: DuckDB con el mismo modelo (mart) en lugar de PostgreSQL.
El mart se construye desde las salidas del pipeline de la Fase 1 y se verifica contra ellas:
si una cifra no cuadra, la construcción se detiene.
"""
from __future__ import annotations

import duckdb
import pandas as pd

from .config import CLEAN_START, DB_PATH, ROOT

MONEY = ["paid_mrr_cop", "previous_month_mrr", "mrr_change", "new_mrr_cop", "expansion_mrr_cop",
         "reactivation_mrr_cop", "contraction_mrr_cop", "churned_mrr_cop", "usual_amount_cop"]

VINTAGE_SQL = """
CASE cohort_flag
  WHEN 'left_censored' THEN 'Base previa (activos en ene-22)'
  WHEN 'suspected_spillover' THEN 'Altas de feb-22 (marcadas)'
  ELSE 'Cosecha ' || substr(cohort_month, 1, 4) || CASE WHEN substr(cohort_month, 1, 4) = '2022' THEN ' (mar–dic)' ELSE '' END
END"""

MONTHLY_SQL = """
SELECT month,
       SUM(active_customer)::BIGINT AS active_customers,
       SUM(new_customer)::BIGINT AS new_customers,
       SUM(churned_customer)::BIGINT AS churned_customers,
       SUM(reactivated_customer)::BIGINT AS reactivated_customers,
       SUM(expanded_customer)::BIGINT AS expanded_customers,
       SUM(contracted_customer)::BIGINT AS contracted_customers,
       SUM(paid_mrr_cop) AS total_paid_mrr_cop,
       COALESCE(SUM(new_mrr_cop), 0) AS new_mrr_cop,
       COALESCE(SUM(expansion_mrr_cop), 0) AS expansion_mrr_cop,
       COALESCE(SUM(reactivation_mrr_cop), 0) AS reactivation_mrr_cop,
       COALESCE(SUM(contraction_mrr_cop), 0) AS contraction_mrr_cop,
       COALESCE(SUM(churned_mrr_cop), 0) AS churned_mrr_cop,
       SUM(paid_mrr_cop)::DOUBLE / NULLIF(SUM(active_customer), 0) AS mrr_per_active_customer_cop,
       MEDIAN(paid_mrr_cop::DOUBLE) FILTER (WHERE new_customer = 1) AS median_new_customer_mrr_cop
FROM mart.customer_month
GROUP BY month
ORDER BY month"""


def _csv(name: str) -> str:
    return str(ROOT / name).replace("'", "''")


def build(db_path=DB_PATH, verbose: bool = True) -> dict:
    """Construye el mart y corre las pruebas de paridad. Devuelve un resumen."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    try:
        con.execute("CREATE SCHEMA mart")
        types = ", ".join(f"'{c}': 'DECIMAL(18,2)'" for c in MONEY)
        con.execute(f"""
            CREATE TABLE mart.customer_month AS
            SELECT *, {VINTAGE_SQL} AS vintage, CAST(substr(month, 1, 4) AS INTEGER) AS year
            FROM read_csv('{_csv("finora_analytical_dataset.csv")}', header = true,
                          types = {{'observed_amount': 'DECIMAL(18,6)', {types}}})""")
        con.execute(f"""
            CREATE TABLE mart.monthly_metrics_phase1 AS
            SELECT * FROM read_csv('{_csv("finora_monthly_metrics.csv")}', header = true)""")
        con.execute(f"CREATE VIEW mart.monthly_metrics AS {MONTHLY_SQL}")
        con.execute(f"""
            CREATE VIEW mart.new_customers AS
            WITH n AS (
                SELECT customer_id, industry, vintage, month AS cohort_month, paid_mrr_cop::DOUBLE AS m0_cop
                FROM mart.customer_month WHERE new_customer = 1),
            e AS (
                SELECT customer_id,
                       MEDIAN(paid_mrr_cop::DOUBLE) FILTER (WHERE paid_mrr_cop > 0) AS early_run_rate_cop,
                       COUNT(*) AS early_months_observed,
                       MAX(CASE WHEN tenure_month = 1 THEN paid_mrr_cop::DOUBLE END) AS m1_cop
                FROM mart.customer_month WHERE tenure_month BETWEEN 0 AND 2 GROUP BY customer_id)
            SELECT n.*, e.early_run_rate_cop, e.early_months_observed, e.m1_cop,
                   CAST(substr(n.cohort_month, 1, 4) AS INTEGER) AS year,
                   n.cohort_month >= '{CLEAN_START}' AS clean
            FROM n JOIN e USING (customer_id)""")
        con.execute("""
            CREATE VIEW mart.vintage_month AS
            SELECT month, vintage, SUM(active_customer)::BIGINT AS active_customers,
                   SUM(paid_mrr_cop) AS mrr_cop,
                   SUM(paid_mrr_cop)::DOUBLE / NULLIF(SUM(active_customer), 0) AS arpa_cop
            FROM mart.customer_month GROUP BY month, vintage""")
        con.execute("""
            CREATE VIEW mart.churn_events AS
            SELECT customer_id, industry, vintage, month, year, -churned_mrr_cop::DOUBLE AS prev_mrr_cop,
                   months_to_return, returned_next_month
            FROM mart.customer_month WHERE churned_customer = 1""")
        summary = parity(con)
    finally:
        con.close()
    if verbose:
        print("Capa SQL construida ·", db_path.name, "·", summary)
    return summary


def parity(con) -> dict:
    """Paridad exacta contra la Fase 1: conteos iguales y montos iguales al centavo."""
    sql = con.execute("SELECT * FROM mart.monthly_metrics").df()
    ph1 = pd.read_csv(ROOT / "finora_monthly_metrics.csv")
    assert list(sql.month) == list(ph1.month), "los meses no coinciden"
    checked = 0
    # Donde la Fase 1 deja un flujo vacío (ene-22: no identificable), el mart debe dar cero.
    for c in ["active_customers", "new_customers", "churned_customers", "reactivated_customers",
              "expanded_customers", "contracted_customers", "total_paid_mrr_cop", "new_mrr_cop",
              "expansion_mrr_cop", "reactivation_mrr_cop", "contraction_mrr_cop", "churned_mrr_cop"]:
        a = sql[c].astype(float).round(2)
        b = ph1[c].astype(float).round(2)
        known = b.notna()
        assert (abs(a[known] - b[known]) < 0.005).all(), f"paridad falló en {c}"
        assert (a[~known] == 0).all(), f"paridad falló en {c} (meses no identificables)"
        checked += 1
    for c in ["mrr_per_active_customer_cop", "median_new_customer_mrr_cop"]:
        a, b = sql[c].astype(float), ph1[c].astype(float)
        both = a.notna() & b.notna()
        assert (a.isna() == b.isna()).all() or c == "median_new_customer_mrr_cop", f"paridad falló (nulos) en {c}"
        assert ((a[both] - b[both]).abs() <= 0.01).all(), f"paridad falló en {c}"
        checked += 1
    nc = con.execute("SELECT * FROM mart.new_customers").df()
    nc1 = pd.read_csv(ROOT / "supporting" / "new_customers.csv")
    assert len(nc) == len(nc1), "paridad falló en el número de altas"
    for c in ["m0_cop", "early_run_rate_cop", "m1_cop"]:
        a = nc.groupby("year")[c].sum().round(2)
        b = nc1.groupby("year")[c].sum().round(2)
        assert (abs(a - b) < 0.01).all(), f"paridad falló en new_customers.{c}"
        checked += 1
    vm = con.execute("SELECT * FROM mart.vintage_month").df()
    vm1 = pd.read_csv(ROOT / "supporting" / "arpa_by_vintage_monthly.csv")
    m = vm.merge(vm1, on=["month", "vintage"], suffixes=("", "_1"))
    assert len(m) == len(vm1), "paridad falló en las cosechas (llaves)"
    assert (m.active_customers == m.active_customers_1).all(), "paridad falló en activos por cosecha"
    assert (abs(m.mrr_cop.astype(float) - m.mrr_cop_1) < 0.01).all(), "paridad falló en MRR por cosecha"
    checked += 2
    return {"pruebas_de_paridad": checked, "filas_cliente_mes": int(con.execute(
        "SELECT COUNT(*) FROM mart.customer_month").fetchone()[0]), "altas": len(nc)}


def connect_ro(db_path=DB_PATH):
    """Conexión de solo lectura y sin acceso a archivos externos (rol agent_ro del §9)."""
    if not db_path.exists():
        build(db_path)
    con = duckdb.connect(str(db_path), read_only=True, config={"enable_external_access": False})
    return con


if __name__ == "__main__":
    build()
