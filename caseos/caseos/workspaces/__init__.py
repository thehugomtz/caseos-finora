"""Analytics workspace adapters. A case binds (case.yaml › workspace) to the exploration workspace it uses.

Today there is one adapter: the Business Exploration Workspace (finora-eda), reused in-process. A new workspace is a
module exposing `adapter(cfg)` with the same surface as finora_eda.FinoraWorkspace (available, info, canonical,
canonical_table, run, runs, claim_table, new_investigation, run_investigation, mount); see ARCHITECTURE.md › Workspaces.
Cases without a workspace still get Business Research, Measurement and Data Engineering; Analytics shows as unavailable.
"""
from __future__ import annotations

from ..store import CaseStore


def for_case(store: CaseStore):
    ws = (store.meta().get("workspace") or {})
    if ws.get("type") == "finora-eda":
        from . import finora_eda
        return finora_eda.adapter(ws)
    return None
