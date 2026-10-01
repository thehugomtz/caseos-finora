# Para agentes de IA

Si eres un asistente de IA (Claude Code, Codex, Cursor, Gemini u otro) y te pidieron probar este repo, sigue
[CLAUDE.md](CLAUDE.md). Resumen:

1. Pregunta si la persona solo quiere ver el caso, que no necesita modelo, o correr agentes. Si va a correrlos, pregunta
   con qué modelo. En este ejercicio se usó Claude Opus 5.5 (`claude-opus-5-5`) con esfuerzo `max`.
2. Corre `./start.sh --model <id> --effort <max|high> --yes`. En Windows sin WSL, usa los comandos de CLAUDE.md.
3. Abre http://127.0.0.1:8780 y guíala con el README.
4. No corras `import-finora --force` ni edites `caseos/cases/finora/`: es la evidencia. Para experimentar, usa
   `./start.sh --copia`.

`caseos/AGENTS.md` es otra cosa: el contrato de los agentes de CaseOS.
