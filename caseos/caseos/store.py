"""Filesystem case store: the single source of truth for a case.

- One YAML file per entity (questions/Q-001.yaml, research/R-014.yaml, ...), written atomically.
- Every update keeps the previous version under audit/versions/<ID>/v<n>.yaml (nothing is overwritten silently).
- Every change is an activity entry in audit/activity.jsonl (the operational trace shown in the UI).
- Material changes re-render brain.md through a registered hook (see brain.py).

The in-memory index is a cache keyed by file mtime, so hand edits on disk are picked up on the next read.
"""
from __future__ import annotations

import copy
import re
import threading
from pathlib import Path
from typing import Any, Callable

from . import bus
from .model import PHASES, TYPES, type_of
from .util import (append_jsonl, atomic_write, now_iso, read_jsonl, read_yaml, stamp, write_yaml)

_ID_RE = re.compile(r"^([A-Z])-(\d{3,})$")


class StoreError(Exception):
    pass


class CaseStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.id = self.root.name
        self._lock = threading.RLock()
        self._cache: dict[str, tuple[float, dict]] = {}     # path -> (mtime, entity)
        self.material_hooks: list[Callable[["CaseStore", str], None]] = []
        self._muted = 0                                       # batch mode: defer brain re-render

    # ------------------------------------------------------------------ case metadata
    @property
    def meta_path(self) -> Path:
        return self.root / "case.yaml"

    def meta(self) -> dict:
        m = read_yaml(self.meta_path, {}) or {}
        m.setdefault("id", self.id)
        m.setdefault("phases", {})
        for p in PHASES:
            m["phases"].setdefault(p, {"status": "not_started", "ready_count": 0, "history": []})
        return m

    def save_meta(self, meta: dict) -> None:
        with self._lock:
            meta["updated_at"] = now_iso()
            write_yaml(self.meta_path, meta)

    # ------------------------------------------------------------------ files
    def path(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if self.root.resolve() not in p.parents and p != self.root.resolve():
            raise StoreError(f"Ruta fuera del caso: {rel}")
        return p

    def read_text(self, rel: str, default: str = "") -> str:
        p = self.path(rel)
        return p.read_text(encoding="utf-8") if p.exists() else default

    def write_text(self, rel: str, text: str) -> Path:
        p = self.path(rel)
        atomic_write(p, text)
        return p

    def read_data(self, rel: str, default: Any = None) -> Any:
        return read_yaml(self.path(rel), default)

    def write_data(self, rel: str, data: Any) -> Path:
        p = self.path(rel)
        write_yaml(p, data)
        return p

    # ------------------------------------------------------------------ entities
    def _entity_dir(self, etype: str) -> Path:
        return self.root / TYPES[etype]["dir"]

    def _entity_path(self, eid: str) -> Path:
        etype = type_of(eid)
        if not etype:
            raise StoreError(f"ID inválido: {eid}")
        return self._entity_dir(etype) / f"{eid}.yaml"

    def _scan(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        seen: set[str] = set()
        for etype, spec in TYPES.items():
            d = self.root / spec["dir"]
            if not d.exists():
                continue
            for p in d.glob(f"{spec['prefix']}-*.yaml"):
                key = str(p)
                seen.add(key)
                try:
                    mt = p.stat().st_mtime
                except FileNotFoundError:
                    continue
                hit = self._cache.get(key)
                if hit and hit[0] == mt:
                    e = hit[1]
                else:
                    e = read_yaml(p, {}) or {}
                    e.setdefault("id", p.stem)
                    e.setdefault("type", etype)
                    self._cache[key] = (mt, e)
                out[e["id"]] = e
        for k in list(self._cache):
            if k not in seen:
                self._cache.pop(k, None)
        return out

    def all(self) -> dict[str, dict]:
        with self._lock:
            return self._scan()

    def list(self, etype: str | None = None, **filters) -> list[dict]:
        items = [e for e in self.all().values() if etype is None or e.get("type") == etype]
        for k, v in filters.items():
            items = [e for e in items if e.get(k) == v]
        return sorted(items, key=lambda e: _id_key(e["id"]))

    def get(self, eid: str) -> dict | None:
        p = self._entity_path(eid)
        if not p.exists():
            return None
        with self._lock:
            key, mt = str(p), p.stat().st_mtime
            hit = self._cache.get(key)
            if hit and hit[0] == mt:
                return hit[1]
            e = read_yaml(p, {}) or {}
            e.setdefault("id", eid)
            e.setdefault("type", type_of(eid))
            self._cache[key] = (mt, e)
            return e

    def require(self, eid: str) -> dict:
        e = self.get(eid)
        if e is None:
            raise StoreError(f"{eid} no existe en el caso {self.id}")
        return e

    def next_id(self, etype: str) -> str:
        prefix = TYPES[etype]["prefix"]
        d = self._entity_dir(etype)
        n = 0
        if d.exists():
            for p in d.glob(f"{prefix}-*.yaml"):
                m = _ID_RE.match(p.stem)
                if m:
                    n = max(n, int(m.group(2)))
        # versions directory also reserves IDs of anything that ever existed
        vd = self.root / "audit" / "versions"
        if vd.exists():
            for p in vd.glob(f"{prefix}-*"):
                m = _ID_RE.match(p.name)
                if m:
                    n = max(n, int(m.group(2)))
        return f"{prefix}-{n + 1:03d}"

    def create(self, etype: str, data: dict, *, actor: str, origin: dict | None = None, summary: str | None = None,
               material: bool = True, run_id: str | None = None) -> dict:
        if etype not in TYPES:
            raise StoreError(f"Tipo desconocido: {etype}")
        with self._lock:
            eid = data.get("id") if data.get("id") and type_of(data["id"]) == etype and not self.get(data["id"]) else self.next_id(etype)
            ts = now_iso()
            e = {"id": eid, "type": etype}
            e.update({k: v for k, v in data.items() if k not in ("id", "type")})
            e.setdefault("phase", TYPES[etype]["phase"])
            e.setdefault("links", [])
            e.setdefault("review", {"state": "proposed"})
            e["origin"] = {"actor": actor, **(origin or {})}
            if run_id:
                e["origin"]["run_id"] = run_id
            e["created_at"] = e.get("created_at") or ts
            e["updated_at"] = ts
            e["version"] = 1
            write_yaml(self._entity_path(eid), e)
            self._cache.pop(str(self._entity_path(eid)), None)
        self.log(actor, "created", [eid], summary or f"{actor} creó {eid}", material=material, run_id=run_id)
        return e

    def update(self, eid: str, patch: dict, *, actor: str, summary: str | None = None, material: bool = True,
               run_id: str | None = None, verb: str = "updated") -> dict:
        with self._lock:
            cur = self.require(eid)
            old = copy.deepcopy(cur)
            new = copy.deepcopy(cur)
            for k, v in patch.items():
                if k in ("id", "type", "created_at", "origin"):
                    continue
                new[k] = v
            new["version"] = int(old.get("version") or 1) + 1
            new["updated_at"] = now_iso()
            self._save_version(eid, old)
            write_yaml(self._entity_path(eid), new)
            self._cache.pop(str(self._entity_path(eid)), None)
        self.log(actor, verb, [eid], summary or f"{actor} actualizó {eid}", material=material, run_id=run_id)
        return new

    def _save_version(self, eid: str, entity: dict) -> None:
        v = int(entity.get("version") or 1)
        write_yaml(self.root / "audit" / "versions" / eid / f"v{v}.yaml", entity)

    def history(self, eid: str) -> list[dict]:
        d = self.root / "audit" / "versions" / eid
        if not d.exists():
            return []
        vs = []
        for p in sorted(d.glob("v*.yaml"), key=lambda p: int(p.stem[1:])):
            e = read_yaml(p, {}) or {}
            vs.append({"version": int(p.stem[1:]), "updated_at": e.get("updated_at"), "entity": e})
        return vs

    def add_links(self, eid: str, ids: list[str], *, actor: str, summary: str | None = None) -> dict:
        e = self.require(eid)
        links = list(dict.fromkeys([*(e.get("links") or []), *[i for i in ids if i and i != eid]]))
        if links == (e.get("links") or []):
            return e
        return self.update(eid, {"links": links}, actor=actor, summary=summary or f"{eid} enlazado con {', '.join(ids)}",
                           material=False, verb="linked")

    def set_review(self, eid: str, state: str, *, actor: str, note: str = "") -> dict:
        e = self.require(eid)
        review = {"state": state, "by": actor, "at": now_iso()}
        if note:
            review["note"] = note
        patch = {"review": review}
        if state in ("accepted", "rejected") and e.get("stale"):
            patch["stale"] = None
        verbs = {"accepted": "accepted", "rejected": "rejected", "proposed": "reproposed"}
        label = {"accepted": "aceptó", "rejected": "rechazó", "proposed": "volvió a proponer"}[state]
        return self.update(eid, patch, actor=actor, summary=f"{_who(actor)} {label} {eid}" + (f" — {note}" if note else ""),
                           verb=verbs[state])

    def mark_stale(self, eid: str, *, reason: str, actor: str, phase: str | None = None) -> dict:
        return self.update(eid, {"stale": {"reason": reason, "since": now_iso(), "by": actor, "phase": phase}},
                           actor=actor, summary=f"{eid} marcado needs_review: {reason}", material=False,
                           verb="flagged")

    # ------------------------------------------------------------------ activity (operational trace)
    def log(self, actor: str, verb: str, targets: list[str], summary: str, *, material: bool = False,
            data: dict | None = None, run_id: str | None = None) -> dict:
        entry = {"ts": now_iso(), "actor": actor, "verb": verb, "targets": targets, "summary": summary,
                 "material": material}
        if data:
            entry["data"] = data
        if run_id:
            entry["run_id"] = run_id
        append_jsonl(self.root / "audit" / "activity.jsonl", entry)
        bus.publish(self.id, {"kind": "activity", "entry": entry})
        if material and not self._muted:
            for hook in self.material_hooks:
                try:
                    hook(self, summary)
                except Exception as e:  # noqa: BLE001 - brain rendering must never break a write
                    append_jsonl(self.root / "audit" / "errors.jsonl", {"ts": now_iso(), "where": "material_hook",
                                                                        "error": repr(e)})
        return entry

    def activity(self, limit: int = 200) -> list[dict]:
        return read_jsonl(self.root / "audit" / "activity.jsonl", limit=limit)

    # ------------------------------------------------------------------ batching
    def batch(self):
        store = self

        class _Batch:
            def __enter__(self_inner):
                store._muted += 1
                return store

            def __exit__(self_inner, *exc):
                store._muted -= 1
                if not store._muted and not exc[0]:
                    for hook in store.material_hooks:
                        hook(store, "cambios en lote")
                return False

        return _Batch()

    # ------------------------------------------------------------------ snapshots
    def snapshot_dir(self, phase: str) -> Path:
        return self.root / "snapshots" / phase / stamp()


def _who(actor: str) -> str:
    return "Hugo" if actor == "hugo" else actor


def _id_key(eid: str):
    m = _ID_RE.match(eid or "")
    return (m.group(1), int(m.group(2))) if m else (eid, 0)
