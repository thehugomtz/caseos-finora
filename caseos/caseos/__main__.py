"""CaseOS command line.

    .venv/bin/python -m caseos serve            # app on http://127.0.0.1:8780  (--port N to change it)
    .venv/bin/python -m caseos import-finora    # first case, from brief v0.3 + finora-eda (use --force to redo)
    .venv/bin/python -m caseos skills           # skill manifest check (linked storyteller skills present?)
    .venv/bin/python -m caseos brain <case>     # re-render brain.md
"""
from __future__ import annotations

import json
import sys


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else "serve"
    if cmd == "serve":
        import uvicorn
        from . import config
        port = int(argv[argv.index("--port") + 1]) if "--port" in argv else config.PORT
        uvicorn.run("caseos.server:app", host=config.HOST, port=port, log_level="info")
        return 0
    if cmd == "import-finora":
        from .importers import finora
        s = finora.run(force="--force" in argv)
        counts = {}
        for e in s.all().values():
            counts[e["type"]] = counts.get(e["type"], 0) + 1
        print(json.dumps({"case": s.id, "entities": counts}, ensure_ascii=False, indent=1))
        return 0
    if cmd == "skills":
        from . import config, skills
        if "--md" in argv:
            (config.ROOT / "SKILLS.md").write_text(skills.render_md(), encoding="utf-8")
            print("SKILLS.md regenerado desde skills/manifest.yaml")
            return 0
        reg = skills.registry()
        missing = [s.id for s in reg.values() if not s.exists]
        print(f"{len(reg)} skills en el manifest · faltan: {missing or 'ninguna'}")
        for l in skills.check_links():
            print(f"  linked {l['id']:32} {'OK' if l['exists'] else 'NO ENCONTRADA'}  {l['path']}")
        return 1 if missing else 0
    if cmd == "brain":
        from . import brain, cases
        s = cases.get(argv[1])
        brain.update(s, "regeneración manual")
        print(f"brain.md regenerado para {s.id}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
