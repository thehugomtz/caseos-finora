"""Registro de evidencia (arquitectura v1.2 §5.2–5.3).

La evidencia es inmutable: la registran las tools al calcular, nunca el agente. Guarda la consulta o los
parámetros, el resultado, su hash y las versiones de datos y cerebro con que se produjo.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from .config import brain_version, data_version


@dataclass(frozen=True)
class Evidence:
    id: str
    kind: str                 # metric · sql · analysis · canonical
    tool: str
    params: dict
    method: str
    variant: str | None
    query_text: str | None    # SQL o referencia al código del análisis
    code: str | None
    result: dict              # columnas, filas, valores, formatos, notas
    result_hash: str
    metric_ids: tuple
    caveat_ids: tuple
    n: int | None
    robustness: dict
    marker: str | None        # "Cálculo ad hoc" para run_sql
    ceiling: str              # estado máximo que esta evidencia puede sostener sola
    no_comparable: tuple
    data_version: str
    brain_version: str
    canonical: bool
    created_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["metric_ids"], d["caveat_ids"], d["no_comparable"] = list(self.metric_ids), list(self.caveat_ids), list(self.no_comparable)
        return d


def _hash(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:16]


class Registry:
    def __init__(self):
        self.items: dict[str, Evidence] = {}
        self._n = 0
        self._dv, self._bv = data_version(), brain_version()

    def add(self, *, kind, tool, params, method, result, variant=None, query_text=None, code=None, metric_ids=(),
            caveat_ids=(), n=None, robustness=None, marker=None, ceiling="Hecho observado", no_comparable=(),
            canonical=False, fixed_id: str | None = None) -> Evidence:
        if fixed_id and fixed_id in self.items:
            return self.items[fixed_id]
        if not fixed_id:
            self._n += 1
        eid = fixed_id or f"E-{self._n:03d}"
        ev = Evidence(id=eid, kind=kind, tool=tool, params=params, method=method, variant=variant,
                      query_text=query_text, code=code, result=result, result_hash=_hash(result),
                      metric_ids=tuple(metric_ids), caveat_ids=tuple(dict.fromkeys(caveat_ids)), n=n,
                      robustness=robustness or {}, marker=marker, ceiling=ceiling, no_comparable=tuple(no_comparable),
                      data_version=self._dv, brain_version=self._bv, canonical=canonical)
        self.items[eid] = ev
        return ev

    def get(self, eid: str) -> Evidence | None:
        return self.items.get(eid)

    def resolve(self, ref: str):
        """'E-004.valor[2024-10]' → (evidencia, clave, valor, formato). Lanza KeyError con pista."""
        if "." not in ref:
            raise KeyError(f"Referencia '{ref}' inválida: usa 'E-004.<clave>'.")
        eid, key = ref.split(".", 1)
        ev = self.items.get(eid)
        if ev is None:
            raise KeyError(f"La evidencia {eid} no existe en esta investigación.")
        vals = ev.result.get("valores", {})
        if key not in vals:
            close = [k for k in vals if key.split("[")[0] in k][:6]
            raise KeyError(f"La clave '{key}' no existe en {eid}." + (f" Claves parecidas: {close}." if close else ""))
        return ev, key, vals[key], ev.result.get("formatos", {}).get(key, "texto")

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self.items.values()]
