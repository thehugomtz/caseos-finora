"""Corre una investigación desde la terminal.

    .venv/bin/python -m agent Q2            # pregunta dorada 2
    .venv/bin/python -m agent Q2 --golden   # además la guarda como investigación dorada embebible
    .venv/bin/python -m agent "¿…?"         # pregunta libre (usa el playbook arpa_decline)
"""
from __future__ import annotations

import argparse

import anyio

from .config import DB_PATH
from .orchestrator import run
from .state import Investigation
from .warehouse import build

GOLDEN_Q = {"Q2": "¿Por qué disminuyó el MRR por cliente?"}


def _line(ev: dict) -> str | None:
    t, d, tipo = ev["t"] / 1000, ev["data"], ev["tipo"]
    txt = {
        "estado": lambda: f"estado → {d['estado']}",
        "sesion": lambda: f"sesión · {d['autenticacion']}",
        "encuadre": lambda: f"encuadre · {d.get('pregunta_analitica')}",
        "hipotesis": lambda: "hipótesis · " + " · ".join(f"{h['id']} {h['estado']}" for h in d["hipotesis"]),
        "tool": lambda: f"→ {d['tool']}",
        "tool_error": lambda: f"  ✗ {d['tool']}: {d['error'][:160]}",
        "evidencia": lambda: f"  evidencia {d['id']} · {d['resumen'][:110]}",
        "claim": lambda: f"  ✓ {d['id']} [{d['estado']}] {d['texto'][:150]}",
        "claim_rechazada": lambda: f"  ✗ afirmación rechazada: {'; '.join(d['motivos'])[:180]}",
        "visual": lambda: f"  visual {d['id']} ({d['tipo']}) para {d['claim_id']}",
        "nota": lambda: f"  analista: {d['texto'][:160]}",
        "composicion": lambda: f"composición intento {d['intento']}: " + ("ok" if not d["errores"] else f"{len(d['errores'])} errores"),
        "final": lambda: "fin" + (f" · ERROR {d['error']}" if d.get("error") else ""),
    }.get(tipo)
    return f"[{t:6.1f}s] {txt()}" if txt else None


async def main(pregunta: str, golden: bool, rebuild: bool):
    if rebuild or not DB_PATH.exists():
        build()
    inv = Investigation(pregunta=GOLDEN_Q.get(pregunta, pregunta), pregunta_id=pregunta if pregunta in GOLDEN_Q else None)
    seen = 0

    async def printer():
        nonlocal seen
        while True:
            while seen < len(inv.events):
                line = _line(inv.events[seen])
                if line:
                    print(line, flush=True)
                seen += 1
            if inv.status in ("publicada", "error") and seen >= len(inv.events):
                return
            await anyio.sleep(0.3)

    async with anyio.create_task_group() as tg:
        tg.start_soon(printer)
        await run(inv, save_golden=golden)
    print(f"\nInvestigación {inv.id} · {inv.status} · guardada en investigations/runs/{inv.id}.json")
    if inv.narrativa:
        print("\nRespuesta ejecutiva:", inv.narrativa["respuesta_ejecutiva"]["texto"])
    u = inv.uso
    print("Uso:", u.get("autenticacion"), "·", {k: v for k, v in u.items() if k != "autenticacion"})


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Investigación agentic de Finora")
    ap.add_argument("pregunta", help="Q2 o una pregunta en texto")
    ap.add_argument("--golden", action="store_true", help="guardar como investigación dorada")
    ap.add_argument("--rebuild", action="store_true", help="reconstruir la capa SQL antes de investigar")
    a = ap.parse_args()
    anyio.run(main, a.pregunta, a.golden, a.rebuild)
