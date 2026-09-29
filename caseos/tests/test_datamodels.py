"""The Finora data model: three real layers, reconciliation checks, read-only queries, case binding and verification of
an evidence table against the model (skipped when finora-eda is not next to caseos)."""
import pytest

from caseos import briefing, cases, datamodels, evidence

pytestmark = pytest.mark.skipif(not datamodels.FinoraModel().available, reason="finora-eda no está junto a caseos")


@pytest.fixture(scope="module")
def model():
    return datamodels.get("finora")


def test_three_layers_and_every_check_passes(model):
    cat = model.catalog()
    by = {l["id"]: [t for t in cat["tables"] if t["schema"] == l["id"]] for l in cat["layers"]}
    assert {t["name"] for t in by["raw"]} == {"transactions", "industry", "sm_spend"}
    assert {t["name"] for t in by["staging"]} == {"stg_customers", "stg_customer_month", "stg_sm_spend"}
    assert "customer_month" in {t["name"] for t in by["mart"]}
    assert all(t["rows"] > 0 and t["columns"] for t in cat["tables"])
    raw_tx = next(t for t in by["raw"] if t["name"] == "transactions")
    assert raw_tx["file"]["sha256"] and all(c["type"] == "VARCHAR" for c in raw_tx["columns"])   # raw stays text
    checks = model.checks()
    assert [c["status"] for c in checks] == ["ok"] * len(checks) and len(checks) >= 7
    assert all(c["sql"] for c in checks)                                                         # each check can be re-run


def test_queries_are_read_only_and_limited(model):
    r = model.query("SELECT month, total_paid_mrr_cop FROM mart.monthly_metrics ORDER BY month", limit=5)
    assert r["columns"] == ["month", "total_paid_mrr_cop"] and len(r["rows"]) == 5 and r["truncated"]
    for bad in ("DROP TABLE mart.customer_month", "SELECT * FROM read_csv('/etc/hosts')", "SELECT 1; SELECT 2",
                "CREATE TABLE raw.x AS SELECT 1", "SELECT * FROM information_schema.tables", "COPY mart.customer_month TO '/tmp/x.csv'"):
        with pytest.raises(ValueError):
            model.query(bad)
    assert model.sample("staging.stg_customer_month", limit=3)["columns"] == ["customer_id", "month", "amount", "amount_cop"]


def test_binding_the_model_fills_the_brief_and_enables_analytics(cases_root):
    s = cases.create_case(name="Con datos", case_id="con-datos")
    datamodels.bind(s, "finora")
    meta = s.meta()
    assert meta["data_model"]["id"] == "finora" and meta["workspace"]["type"] == "finora-eda"
    b = briefing.get(s)
    assert b["sections"]["data_available"]["state"] == "approved" and b["data_available"][0].startswith("Modelo de datos")


def test_an_evidence_table_is_verified_against_the_model(model):
    sql = "SELECT month, total_paid_mrr_cop FROM mart.monthly_metrics WHERE month >= '2024-08' ORDER BY month"
    rows = model.query(sql)["rows"]
    t = evidence.make_table(table_key="V", title="t", question="q", columns=["mes", "monto"], rows=rows, message="m",
                            source={"dataset": "mart.monthly_metrics"}, limitations=["l"], query=sql)
    ok = model.verify_table(t)
    assert ok["status"] == "ok" and ok["matched"] == ok["total"] == 3
    tampered = {**t, "rows": [rows[0], [rows[1][0], rows[1][1] * 1.07], rows[2]]}
    bad = model.verify_table(tampered)
    assert bad["status"] == "partial" and bad["matched"] == 2
    assert model.verify_table({**t, "query": ""})["status"] == "no_query"
