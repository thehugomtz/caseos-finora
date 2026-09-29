import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def cases_root(tmp_path, monkeypatch):
    """Isolated cases/ directory per test."""
    from caseos import cases, config
    d = tmp_path / "cases"
    d.mkdir()
    monkeypatch.setattr(config, "CASES_DIR", d)
    cases._stores.clear()
    yield d
    cases._stores.clear()


@pytest.fixture()
def case(cases_root):
    from caseos import cases
    return cases.create_case(name="Caso Prueba", objective="Entender por qué cae el ingreso por cliente",
                             audience=["CEO", "CFO"], deliverables=["Deck ejecutivo"], context="SaaS B2B",
                             case_id="prueba")
