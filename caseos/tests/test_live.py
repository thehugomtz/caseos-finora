"""Live eval (opt-in, uses the real model on your subscription): CASEOS_LIVE=1 pytest -q tests/test_live.py

Language adaptation: Hugo's messy Spanish goes in; the Framer must answer in his register, keep his vocabulary, avoid
performative jargon, classify his intuition as USER_INTUITION (not FACT) and give its hypothesis a falsifier."""
import asyncio
import os

import pytest

from caseos import language
from caseos.agents import framer
from caseos.util import append_jsonl, now_iso

pytestmark = pytest.mark.skipif(os.environ.get("CASEOS_LIVE") != "1", reason="eval en vivo: CASEOS_LIVE=1")

MESSY = ("Creo que están metiendo más leads pero esa madre no está convirtiendo. Y el MRR por cliente se está cayendo, "
         "yo creo que porque los nuevos entran pagando menos, no porque los viejos paguen menos.")


class FakeJob:
    def __init__(self, case_id):
        self.case_id, self.agent = case_id, "framer"

    async def event(self, kind, data=None):
        pass


def test_framer_adapts_to_hugo_language(case):
    append_jsonl(case.root / framer.CONV, {"turn_id": "T-live", "ts": now_iso(), "mode": "organize", "message": MESSY,
                                           "status": "pending"})
    res = asyncio.run(framer._job(FakeJob(case.id), {"turn_id": "T-live"}))
    rec = framer.conversation(case)[-1]
    ents = case.all()
    created = [ents[i] for i in res["created"]]
    check = language.assess(rec["reply"], case.meta()["language"], MESSY)
    assert check["ok"], check["issues"]
    assert check["english_ratio"] < 0.05
    kinds = {e.get("kind") if e["type"] == "note" else e["type"] for e in created}
    assert "USER_INTUITION" in kinds and "hypothesis" in kinds
    assert not any(e.get("kind") == "FACT" and "cayendo" in (e.get("text") or "") for e in created)
    assert all(h.get("falsifier") for h in created if h["type"] == "hypothesis")
    assert any(e.get("hugo_wording") for e in created)                    # his words kept next to the structure
    preserved = [t.lower() for t in case.meta()["language"]["observed"]["preserved_terms"]]
    assert "mrr" in preserved or "leads" in preserved
