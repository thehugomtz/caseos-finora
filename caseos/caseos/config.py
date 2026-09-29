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

# One model for every agent (the default the existing workspace also uses); cost is tuned with effort, not by
# silently downgrading models. Override per agent with CASEOS_MODEL_<AGENT> (e.g. CASEOS_MODEL_ROUTER).
DEFAULT_MODEL = os.environ.get("CASEOS_MODEL", "claude-opus-5")
EFFORT = {
    "framer": "high",
    "cos": "high",
    "cos_impact": "medium",
    "router": "low",
    "command": "low",
    "business_research": "high",
    "deep_research": "high",
    "peer_review": "high",
    "measurement": "high",
    "data_engineering": "high",
    "synthesis": "high",
    "story": "high",
    "storyteller": "high",
}
# Soft spend caps per run (API-equivalent USD, reported by the SDK; on the subscription nothing is billed per call).
BUDGET_USD = {
    "framer": 1.5, "cos": 1.5, "cos_impact": 0.8, "router": 0.3, "command": 0.3, "business_research": 3.0,
    "deep_research": 3.0, "peer_review": 1.5, "measurement": 2.0, "data_engineering": 2.0, "synthesis": 1.5,
    "story": 2.5, "storyteller": 25.0,
}


def model_for(agent: str) -> str:
    return os.environ.get(f"CASEOS_MODEL_{agent.upper()}", DEFAULT_MODEL)


# After research completes the COS assesses its impact automatically (a small model call). CASEOS_AUTO_COS=0 disables it.
AUTO_COS = os.environ.get("CASEOS_AUTO_COS", "1") != "0"

HOST = os.environ.get("CASEOS_HOST", "127.0.0.1")
PORT = int(os.environ.get("CASEOS_PORT", "8780"))
