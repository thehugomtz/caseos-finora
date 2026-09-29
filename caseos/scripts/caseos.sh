#!/bin/sh
# CaseOS launcher: ./scripts/caseos.sh [serve|test|import-finora|skills] …
set -e
cd "$(dirname "$0")/.."
PY=.venv/bin/python
if [ ! -x "$PY" ]; then
  echo "Falta el entorno: uv venv --system-site-packages --python 3.13 .venv && uv pip install --python $PY -r requirements.txt" >&2
  exit 1
fi
cmd="${1:-serve}"
[ $# -gt 0 ] && shift
case "$cmd" in
  test) exec "$PY" -m pytest -q tests "$@" ;;
  *)    exec "$PY" -m caseos "$cmd" "$@" ;;
esac
