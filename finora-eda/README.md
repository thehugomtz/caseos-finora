# Finora · Business Exploration Workspace

La herramienta de EDA del caso Finora: primero entender los datos y después explicarlos. Tiene dos capas.

1. **Fase 1, el pipeline exploratorio** (`finora_eda.py`). Toma los tres CSV que compartió Finora, sin tocarlos
   (`data/raw/`), y recalcula todo: la tabla analítica cliente × mes, las métricas mensuales, las tablas de soporte y el
   workspace `finora_eda.html`. Ninguna cifra se escribe a mano.
2. **La capa agéntica** (`agent/`, `app/`). Un agente investiga preguntas de negocio sobre el modelo de datos. El modelo
   es DuckDB (`warehouse/finora.duckdb`, se construye solo al arrancar). El agente consulta con SQL de solo lectura, un
   validador en código revisa cada afirmación y un compositor redacta la respuesta con su evidencia y su gráfica.

Lo que ya trabajó el agente viene en el repo:

- `investigations/golden/Q2.json`: la pregunta dorada, «¿Por qué disminuyó el MRR por cliente?».
- `investigations/caso/W0–W5`: las preguntas del caso (W6 y W7 no se pueden responder con estos datos; el agente dice qué falta).
- `investigations/runs/`: cada corrida, con modelo, pasos, consultas y tiempos.

## Cómo probarlo

El `./start.sh` de la raíz del repo ya deja esta herramienta lista. CaseOS la monta en su vista **Analytics**
(`/ws/finora`). Para correrla sola:

```bash
cd finora-eda
uv venv --python 3.13 .venv                       # o: python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m uvicorn app.server:app --host 127.0.0.1 --port 8765
```

Abre http://127.0.0.1:8765 y pulsa ⌘K. Una pregunta frecuente se responde al instante con lo ya verificado. Una pregunta
libre más Enter lanza al agente en vivo, que tarda entre 3 y 10 minutos y usa tu sesión de Claude o tu
`ANTHROPIC_API_KEY`. `finora_eda.html` se abre también sin servidor, con las respuestas verificadas embebidas.

Otras formas:

- `python finora_eda.py` vuelve a correr la Fase 1 desde los CSV.
- `python -m agent Q2` investiga la pregunta 2 desde la terminal; `python -m agent W2` investiga una pregunta del caso.
- `python -m evals.run_evals` corre 94 evaluaciones sin llamar al modelo.

**Modelo.** Las investigaciones de este repo corrieron con `claude-opus-5`, el modelo que está en sus registros. Se
cambia con `FINORA_MODEL` (por ejemplo `FINORA_MODEL=claude-opus-5-5`). El esfuerzo por rol está en `agent/config.py`.

## Documentos

- [docs/propuesta_arquitectura_v1.md](docs/propuesta_arquitectura_v1.md): la arquitectura v1.2 (cerebro, capa SQL,
  agente, validador, compositor y linaje).
- [docs/slice_q2.md](docs/slice_q2.md): la rebanada de punta a punta, la iteración «respuesta primero» y «Preparar
  narrativa».
- [finora_eda_notes.md](finora_eda_notes.md): definiciones, transformaciones, supuestos, anomalías y límites de la Fase 1.
