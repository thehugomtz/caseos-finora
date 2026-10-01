"""Estado de una investigación (arquitectura v1.2 §3.4 y §5.2): objetos tipados, no conversación."""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field

from .config import MODEL, RUNS, brain_version, data_version
from .evidence import Registry
from .validator import hypothesis_status

STATUSES = ["encuadre", "hipotesis", "evidencia", "validacion", "composicion", "publicada", "error"]


def now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class Investigation:
    pregunta: str
    pregunta_id: str | None = None
    lente: str = "Finanzas"
    playbook_id: str = "arpa_decline"
    contexto: dict | None = None                     # pieza de narrativa desde la que se profundiza
    caso_id: str | None = None                       # pregunta del caso (W0–W5) que responde esta investigación
    id: str = field(default_factory=lambda: "INV-" + time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4])
    status: str = "encuadre"
    registry: Registry = field(default_factory=Registry)
    encuadre: dict | None = None
    hipotesis: list = field(default_factory=list)
    hipotesis_registradas_ms: int | None = None
    claims: dict = field(default_factory=dict)
    visuals: dict = field(default_factory=dict)
    log: list = field(default_factory=list)          # registro de análisis: todo lo ejecutado, incluido lo descartado
    events: list = field(default_factory=list)       # para streaming (SSE)
    budget_used: int = 0
    tool_calls: int = 0
    paquete: dict | None = None
    narrativa: dict | None = None
    respuesta_caso: dict | None = None               # siete partes de la pregunta del caso
    composicion_intentos: list = field(default_factory=list)
    notas_agente: list = field(default_factory=list)
    uso: dict = field(default_factory=dict)
    started_ms: int = field(default_factory=now_ms)
    finished_ms: int | None = None
    error: str | None = None
    modelo: str = MODEL

    # ---------------------------------------------------------------- eventos
    def emit(self, tipo: str, data: dict | None = None):
        self.events.append({"n": len(self.events), "t": now_ms() - self.started_ms, "tipo": tipo, "data": data or {}})

    def set_status(self, s: str):
        if s != self.status:
            self.status = s
            self.emit("estado", {"estado": s})

    # ---------------------------------------------------------------- hipótesis
    def refresh_hypotheses(self):
        claims = list(self.claims.values())
        for h in self.hipotesis:
            st, why = hypothesis_status(h["id"], claims)
            h["estado"], h["estado_motivo"] = st, why

    def close_hypotheses(self):
        self.refresh_hypotheses()
        for h in self.hipotesis:
            if h["estado"] == "Pendiente":
                h["estado"], h["estado_motivo"] = "No evaluada por presupuesto", "quedó pendiente al cerrar la investigación"

    # ---------------------------------------------------------------- serialización
    def to_dict(self) -> dict:
        return {"id": self.id, "pregunta": self.pregunta, "pregunta_id": self.pregunta_id, "lente": self.lente,
                "playbook_id": self.playbook_id, "contexto": self.contexto, "caso_id": self.caso_id, "status": self.status,
                "encuadre": self.encuadre,
                "hipotesis": self.hipotesis, "hipotesis_registradas_ms": self.hipotesis_registradas_ms,
                "claims": self.claims, "visuals": self.visuals, "evidencia": self.registry.to_list(),
                "log": self.log, "paquete": self.paquete, "narrativa": self.narrativa, "respuesta_caso": self.respuesta_caso,
                "composicion_intentos": self.composicion_intentos, "notas_agente": self.notas_agente,
                "presupuesto": {"analisis_usado": self.budget_used, "llamadas_tools": self.tool_calls},
                "uso": self.uso, "modelo": self.modelo, "data_version": data_version(),
                "brain_version": brain_version(), "started_ms": self.started_ms, "finished_ms": self.finished_ms,
                "error": self.error, "events": self.events}

    @classmethod
    def from_dict(cls, d: dict) -> "Investigation":
        from .evidence import Evidence
        inv = cls(pregunta=d["pregunta"], pregunta_id=d.get("pregunta_id"), lente=d.get("lente", "Finanzas"),
                  playbook_id=d.get("playbook_id", "arpa_decline"), contexto=d.get("contexto"), caso_id=d.get("caso_id"))
        for k in ("id", "status", "encuadre", "hipotesis", "hipotesis_registradas_ms", "claims", "visuals", "log", "paquete",
                  "narrativa", "respuesta_caso", "composicion_intentos", "notas_agente", "uso", "started_ms", "finished_ms", "error", "modelo"):
            if k in d:
                setattr(inv, k, d[k])
        inv.events = d.get("events", [])
        inv.budget_used = d.get("presupuesto", {}).get("analisis_usado", 0)
        inv.tool_calls = d.get("presupuesto", {}).get("llamadas_tools", 0)
        for e in d.get("evidencia", []):
            e = dict(e)
            for k in ("metric_ids", "caveat_ids", "no_comparable"):
                e[k] = tuple(e.get(k) or ())
            inv.registry.items[e["id"]] = Evidence(**e)
        inv.registry._n = sum(1 for k in inv.registry.items if k.startswith("E-"))
        return inv

    def save(self, path=None):
        path = path or (RUNS / f"{self.id}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        return path
