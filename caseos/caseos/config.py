"""CaseOS configuration: paths, models and budgets. Everything that changes between machines lives here.

Secrets never live in the repo. The agent runtime uses the local Claude Code session (Hugo's subscription) unless
ANTHROPIC_API_KEY is set in the environment, in which case the same code runs against the API.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_cases = Path(os.environ.get("CASEOS_CASES_DIR", ROOT / "cases")).expanduser()
CASES_DIR = _cases if _cases.is_absolute() else (ROOT / _cases).resolve()   # relative paths are relative to caseos/
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"
SCHEMAS_DIR = ROOT / "schemas"
WEB_DIR = ROOT / "web"
RUNTIME_DIR = ROOT / ".runtime"          # scratch cwd for agent subprocesses (gitignored)

# Existing Business Exploration Workspace (optional adapter). Relative to the repo by default.
FINORA_EDA_PATH = Path(os.environ.get("CASEOS_FINORA_EDA_PATH", ROOT.parent / "finora-eda"))

# Existing Executive Visual Storyteller (Hugo's skills). Linked, never forked.
USER_SKILLS_DIR = Path(os.environ.get("CASEOS_USER_SKILLS_DIR", Path.home() / ".claude" / "skills"))
USER_AGENTS_DIR = Path(os.environ.get("CASEOS_USER_AGENTS_DIR", Path.home() / ".claude" / "agents"))
STORYTELLER_SKILLS = ["executive-visual-storyteller", "executive-storyline", "consulting-visual-director",
                      "html-slide-renderer", "slide-critic"]

# One model and one effort for every agent: Hugo asked for Opus 5.5 at maximum effort (28-sep-2026). Nothing is
# downgraded silently. Overrides: CASEOS_MODEL / CASEOS_EFFORT for all agents, CASEOS_MODEL_<AGENT> /
# CASEOS_EFFORT_<ROLE> for one (e.g. CASEOS_EFFORT_ROUTER=high).
DEFAULT_MODEL = os.environ.get("CASEOS_MODEL", "claude-opus-5-5")
DEFAULT_EFFORT = os.environ.get("CASEOS_EFFORT", "max")
ROLES = ["framer", "briefer", "cos", "cos_impact", "router", "command", "business_research", "deep_research", "peer_review",
         "measurement", "data_engineering", "synthesis", "story", "storyteller"]
EFFORT = {r: os.environ.get(f"CASEOS_EFFORT_{r.upper()}", DEFAULT_EFFORT) for r in ROLES}
# Soft spend caps per run (API-equivalent USD, reported by the SDK; on the subscription nothing is billed per call).
# Sized for max effort: they stop a runaway run, not a normal one.
BUDGET_USD = {
    "framer": 4.0, "briefer": 3.0, "cos": 4.0, "cos_impact": 3.0, "router": 1.0, "command": 1.0, "business_research": 8.0,
    "deep_research": 8.0, "peer_review": 4.0, "measurement": 8.0, "data_engineering": 8.0, "synthesis": 4.0,
    "story": 6.0, "storyteller": 45.0,
}


def model_for(agent: str) -> str:
    return os.environ.get(f"CASEOS_MODEL_{agent.upper()}", DEFAULT_MODEL)


# After research completes the COS assesses its impact automatically (a small model call). CASEOS_AUTO_COS=0 disables it.
AUTO_COS = os.environ.get("CASEOS_AUTO_COS", "1") != "0"

HOST = os.environ.get("CASEOS_HOST", "127.0.0.1")
PORT = int(os.environ.get("CASEOS_PORT", "8780"))
