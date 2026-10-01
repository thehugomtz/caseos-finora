#!/usr/bin/env bash
# Finora · CaseOS + Business Exploration Workspace, listo en un comando (macOS y Linux; en Windows, WSL o CLAUDE.md).
#
#   ./start.sh                         instala lo que falte, pregunta el modelo y abre CaseOS con el caso Finora
#   ./start.sh --model claude-opus-5-5 --effort max --yes      sin preguntas
#   ./start.sh --copia                 además crea «finora-prueba», una copia para experimentar sin tocar el original
#   ./start.sh --port 8790 --no-open   otro puerto, sin abrir el navegador
#   ./start.sh --solo-instalar         instala y sale
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

MODEL=""; EFFORT=""; YES=0; OPEN=1; PORT="${CASEOS_PORT:-8780}"; COPY=0; INSTALL_ONLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --effort) EFFORT="$2"; shift 2 ;;
    --yes|-y) YES=1; shift ;;
    --no-open) OPEN=0; shift ;;
    --port) PORT="$2"; shift 2 ;;
    --copia|--copy) COPY=1; shift ;;
    --solo-instalar|--install-only) INSTALL_ONLY=1; shift ;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Opción desconocida: $1 (usa --help)"; exit 1 ;;
  esac
done

say() { printf '\033[1m%s\033[0m\n' "$*"; }
note() { printf '  %s\n' "$*"; }

# ---------------------------------------------------------------- 1. Python 3.11+
PY=""
for c in python3.13 python3.12 python3.11 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
    PY="$(command -v "$c")"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Necesitas Python 3.11 o más nuevo (se probó con 3.13): https://www.python.org/downloads/"; exit 1
fi

# ---------------------------------------------------------------- 2. entorno e instalación (una sola vez)
REQ_HASH="$(cksum < caseos/requirements.txt | cut -d" " -f1)"
if [ ! -x .venv/bin/python ] || [ "$(cat .venv/.instalado 2>/dev/null)" != "$REQ_HASH" ]; then
  say "Instalando dependencias (la primera vez tarda unos minutos: el SDK de agentes trae su propio CLI de Claude)…"
  if command -v uv >/dev/null 2>&1; then
    [ -x .venv/bin/python ] || uv venv --quiet --python "$PY" .venv
    uv pip install --quiet --python .venv/bin/python -r caseos/requirements.txt
  else
    [ -x .venv/bin/python ] || "$PY" -m venv .venv
    .venv/bin/python -m pip install --quiet --upgrade pip
    .venv/bin/python -m pip install --quiet -r caseos/requirements.txt
  fi
  echo "$REQ_HASH" > .venv/.instalado
fi

# La base DuckDB del workspace de EDA (CaseOS la consulta en Datos y Analytics)
if [ ! -f finora-eda/warehouse/finora.duckdb ]; then
  say "Construyendo el modelo de datos del workspace de EDA…"
  (cd finora-eda && ../.venv/bin/python -c "from agent.warehouse import build; build(verbose=False)")
fi
[ "$INSTALL_ONLY" = 1 ] && { say "Listo. Para arrancar: ./start.sh"; exit 0; }

# ---------------------------------------------------------------- 3. modelo de los agentes
[ -f .env ] && set -a && . ./.env && set +a
if [ -z "$MODEL" ] && [ -n "${CASEOS_MODEL:-}" ] && [ "$YES" = 1 ]; then MODEL="$CASEOS_MODEL"; fi
if [ -z "$MODEL" ]; then
  if [ "$YES" = 1 ]; then
    MODEL="claude-opus-5-5"
  else
    say "¿Con qué modelo quieres que trabajen los agentes?"
    note "1) claude-opus-5-5           Opus 5.5 — el que se usó en este ejercicio (recomendado)"
    note "2) claude-sonnet-5           Sonnet 5 — más rápido y barato"
    note "3) claude-haiku-4-5-20251001 Haiku 4.5 — para recorrer el flujo rápido"
    note "4) otro                      escribes el ID"
    [ -n "${CASEOS_MODEL:-}" ] && note "Enter = el de la vez pasada (${CASEOS_MODEL})"
    read -r -p "  > " ans
    case "$ans" in
      "") MODEL="${CASEOS_MODEL:-claude-opus-5-5}" ;;
      1) MODEL="claude-opus-5-5" ;;
      2) MODEL="claude-sonnet-5" ;;
      3) MODEL="claude-haiku-4-5-20251001" ;;
      4) read -r -p "  ID del modelo: " MODEL ;;
      *) MODEL="$ans" ;;
    esac
  fi
fi
if [ -z "$EFFORT" ]; then
  if [ "$YES" = 1 ]; then
    EFFORT="${CASEOS_EFFORT:-max}"
  else
    say "¿Esfuerzo? 1) max — el del ejercicio; un turno puede tardar varios minutos · 2) high — más rápido (1–2 min por turno)"
    read -r -p "  > [1] " ans
    case "$ans" in 2|high) EFFORT="high" ;; *) EFFORT="max" ;; esac
  fi
fi
printf 'CASEOS_MODEL=%s\nCASEOS_EFFORT=%s\nFINORA_MODEL=%s\n' "$MODEL" "$EFFORT" "$MODEL" > .env
export CASEOS_MODEL="$MODEL" CASEOS_EFFORT="$EFFORT" FINORA_MODEL="$MODEL" CASEOS_PORT="$PORT"

# ---------------------------------------------------------------- 4. copia para experimentar (opcional)
if [ "$COPY" = 1 ] && [ ! -d caseos/cases/finora-prueba ]; then
  cp -R caseos/cases/finora caseos/cases/finora-prueba
  .venv/bin/python - <<'EOF'
import re
from pathlib import Path
p = Path("caseos/cases/finora-prueba/case.yaml")
s = p.read_text(encoding="utf-8")
s = re.sub(r"^id: .*$", "id: finora-prueba", s, count=1, flags=re.M)
s = re.sub(r"^name: .*$", "name: Finora (prueba)", s, count=1, flags=re.M)
p.write_text(s, encoding="utf-8")
EOF
  note "Copia creada: elige «Finora (prueba)» en el selector de caso. El original queda intacto."
fi

# ---------------------------------------------------------------- 5. avisos útiles
say "Agentes: $MODEL · esfuerzo $EFFORT"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  note "Los agentes usarán tu ANTHROPIC_API_KEY (se factura por API)."
else
  note "Los agentes usan tu sesión de Claude Code en esta computadora. Si nunca iniciaste sesión: corre «claude» y /login,"
  note "o exporta ANTHROPIC_API_KEY antes de ./start.sh. Recorrer el caso no llama a ningún modelo."
fi
command -v node >/dev/null 2>&1 || note "Sin Node: puedes ver todo; regenerar láminas o el PDF necesita Node 18+ y Google Chrome."

# ---------------------------------------------------------------- 6. arrancar CaseOS
URL="http://127.0.0.1:$PORT"
say "CaseOS en $URL  (Ctrl+C para detenerlo)"
(cd caseos && exec ../.venv/bin/python -m caseos serve --port "$PORT") &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 60); do
  if curl -s -o /dev/null "$URL/" 2>/dev/null; then break; fi
  kill -0 $SERVER 2>/dev/null || { echo "CaseOS no arrancó (¿el puerto $PORT está ocupado? prueba --port 8790)"; exit 1; }
  sleep 1
done
if [ "$OPEN" = 1 ]; then
  if command -v open >/dev/null 2>&1; then open "$URL"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1 || true; fi
fi
wait $SERVER
