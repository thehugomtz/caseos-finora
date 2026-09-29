"""Small shared helpers: YAML/JSON IO with atomic writes, timestamps, text utilities."""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

try:  # libyaml when available (fast), pure Python otherwise
    _Loader = yaml.CSafeLoader
    _Dumper = yaml.CSafeDumper
except AttributeError:  # pragma: no cover
    _Loader = yaml.SafeLoader
    _Dumper = yaml.SafeDumper


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def now_ms() -> int:
    return int(time.time() * 1000)


def stamp() -> str:
    """Filesystem-safe timestamp, sortable: 20260928-213455."""
    return time.strftime("%Y%m%d-%H%M%S")


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def plain(obj: Any) -> Any:
    """Values from pandas/numpy (np.float64, arrays, Decimal…) as plain Python, so any result can be written to YAML."""
    if isinstance(obj, dict):
        return {k: plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [plain(v) for v in obj]
    if type(obj).__module__ == "numpy":         # np.float64 subclasses float, yet YAML cannot write it: convert first
        return plain(obj.tolist() if hasattr(obj, "tolist") else obj.item())
    if obj is None or type(obj) in (str, int, float, bool):
        return obj
    for t in (bool, int, float, str):           # subclasses of the plain types
        if isinstance(obj, t):
            return t(obj)
    if type(obj).__name__ == "Decimal":
        return float(obj)
    return obj


def yaml_dump(data: Any) -> str:
    return yaml.dump(plain(data), Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=110, default_flow_style=False)


def yaml_load(text: str) -> Any:
    return yaml.load(text, Loader=_Loader)


def read_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return yaml_load(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, data: Any) -> None:
    atomic_write(path, yaml_dump(data))


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=1, default=str))


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


def write_jsonl_replace(path: Path, rows: list[dict]) -> None:
    atomic_write(path, "".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows))


def read_jsonl(path: Path, limit: int | None = None) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    if limit:
        lines = lines[-limit:]
    out = []
    for ln in lines:
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    return out


def norm(text: str) -> str:
    """Lowercase, no accents, single spaces: for matching, never for display."""
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.lower()).strip()


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", norm(text)).strip("-")
    return (s[:max_len].rstrip("-")) or "caso"


def clip(text: str | None, n: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"
