"""Skill registry and loader.

Skills are not a flat bag: each agent has core, dynamic, challenge-only and lens bindings (skills/manifest.yaml).
The loader picks the minimum set for one request and composes it into the agent's system prompt, recording exactly
which skills (and which file hashes) were loaded so the run is traceable in "Under the hood".
"""
from __future__ import annotations

import functools
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config
from .util import norm, read_yaml

LENS_LABELS = {"ceo": "CEO", "cro": "CRO", "cfo": "CFO", "cpo": "CPO", "cdo": "CDO"}


@dataclass
class Binding:
    mode: str
    modes: list[str] = field(default_factory=list)
    intensity: list[str] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)


@dataclass
class Skill:
    id: str
    kind: str
    path: Path
    source: str
    license: str
    purpose: str
    adapter_note: str
    lens: str | None
    triggers: list[str]
    bindings: dict[str, Binding]
    adapted_into: list[str]

    @property
    def exists(self) -> bool:
        return (self.path / "SKILL.md").exists()

    def body(self) -> str:
        text = (self.path / "SKILL.md").read_text(encoding="utf-8")
        return _strip_frontmatter(text).strip()

    def digest(self) -> str:
        if not self.exists:
            return "missing"
        return hashlib.sha256((self.path / "SKILL.md").read_bytes()).hexdigest()[:12]

    def public(self) -> dict:
        return {"id": self.id, "kind": self.kind, "path": _display_path(self.path), "source": self.source,
                "license": self.license, "purpose": self.purpose, "lens": self.lens, "exists": self.exists,
                "agents": {a: {"mode": b.mode, "modes": b.modes, "intensity": b.intensity,
                               "triggers": b.triggers or ([] if b.mode != "lens" else self.triggers)}
                           for a, b in self.bindings.items()},
                "adapted_into": self.adapted_into, "adapter_note": self.adapter_note}


def _display_path(p: Path) -> str:
    try:
        return str(p.relative_to(config.ROOT))
    except ValueError:
        return str(p).replace(str(Path.home()), "~")


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def _resolve(path: str) -> Path:
    if path.startswith("~/.claude/skills/"):
        return config.USER_SKILLS_DIR / path.split("~/.claude/skills/", 1)[1]
    p = Path(path).expanduser()
    return p if p.is_absolute() else config.ROOT / p


@functools.lru_cache(maxsize=1)
def registry() -> dict[str, Skill]:
    man = read_yaml(config.SKILLS_DIR / "manifest.yaml", {}) or {}
    out: dict[str, Skill] = {}
    for s in man.get("skills", []):
        binds = {}
        for agent, b in (s.get("agents") or {}).items():
            binds[agent] = Binding(mode=b.get("mode", "core"), modes=b.get("modes") or [], intensity=b.get("intensity") or [],
                                   triggers=b.get("triggers") or [])
        out[s["id"]] = Skill(id=s["id"], kind=s.get("kind", "custom"), path=_resolve(s["path"]), source=s.get("source", ""),
                             license=s.get("license", ""), purpose=s.get("purpose", ""), adapter_note=s.get("adapter_note", ""),
                             lens=s.get("lens"), triggers=s.get("triggers") or [], bindings=binds,
                             adapted_into=s.get("adapted_into") or [])
    return out


def policy() -> dict:
    return (read_yaml(config.SKILLS_DIR / "manifest.yaml", {}) or {}).get("policy", {})


def _hits(text_n: str, triggers: list[str]) -> int:
    n = 0
    for t in triggers:
        tn = norm(t)
        if not tn:
            continue
        if len(tn) <= 4:  # short acronyms (mrr, sql, tam) must match as words
            if re.search(rf"\b{re.escape(tn)}\b", text_n):
                n += 1
        elif tn in text_n:
            n += 1
    return n


def route_lenses(text: str, *, mode: str, explicit: list[str] | None = None) -> list[dict]:
    """Choose advisor lenses: explicit request wins; ORGANIZE uses none unless asked; ADVISE/CHALLENGE use 0–1,
    2 only when two domains are both clearly present (cross-functional)."""
    reg = registry()
    lens_skills = [s for s in reg.values() if s.lens]
    tn = norm(text)
    asked = set(explicit or [])
    for s in lens_skills:
        if re.search(rf"\b(lente|lens|advisor|asesor)?\s*{s.lens}\b", tn) and re.search(r"\b(que diria|qué diría|como lo veria|lente|lens|pregunta(le)? al|opina)\b", tn):
            asked.add(s.lens)
    if asked:
        chosen = [s for s in lens_skills if s.lens in asked][: policy().get("advisors_max", 2)]
        return [{"lens": s.lens, "skill": s.id, "why": "pedido explícito", "score": 99} for s in chosen]
    if mode == "organize":
        return []
    scored = sorted(((_hits(tn, s.triggers), s) for s in lens_skills), key=lambda x: -x[0])
    scored = [(h, s) for h, s in scored if h > 0]
    if not scored:
        return []
    picks = [scored[0]]
    if len(scored) > 1 and scored[1][0] >= 2 and scored[0][0] >= 2:
        picks.append(scored[1])  # genuinely cross-functional
    return [{"lens": s.lens, "skill": s.id, "score": h,
             "why": f"{h} señal(es) de dominio {LENS_LABELS.get(s.lens, s.lens)} en la pregunta"} for h, s in picks]


def select(agent: str, *, mode: str | None = None, intensity: str | None = None, text: str = "",
           lenses: list[dict] | None = None, force: list[str] | None = None) -> list[dict]:
    """Minimum skill set for one request. Returns [{skill, mode, why}] in prompt order."""
    reg = registry()
    tn = norm(text)
    core, dyn, chal, lens_out = [], [], [], []
    for s in reg.values():
        b = s.bindings.get(agent)
        if not b or b.mode in ("reference", "linked") or not s.exists:
            continue
        if b.modes and mode not in b.modes:
            continue
        if b.intensity and intensity not in b.intensity:
            continue
        if b.mode == "core":
            core.append({"skill": s, "mode": "core", "why": "núcleo del agente"})
        elif b.mode == "challenge" and mode == "challenge":
            chal.append({"skill": s, "mode": "challenge", "why": "modo Challenge"})
        elif b.mode == "dynamic":
            h = _hits(tn, b.triggers)
            if h:
                dyn.append({"skill": s, "mode": "dynamic", "why": f"{h} disparador(es) en la pregunta", "score": h})
    for l in lenses or []:
        s = reg.get(l["skill"])
        if s and s.exists and agent in s.bindings:
            lens_out.append({"skill": s, "mode": "lens", "why": l.get("why", "lente elegida")})
    for sid in force or []:
        sid = sid.get("id") if isinstance(sid, dict) else sid   # routes store {"id", "mode", "why"}; the router agent returns ids
        s = reg.get(sid)
        if s and s.exists and not any(x["skill"].id == sid for x in core + dyn + chal + lens_out):
            dyn.append({"skill": s, "mode": "dynamic", "why": "pedido explícito", "score": 99})
    dyn = sorted(dyn, key=lambda x: -x.get("score", 0))[: policy().get("max_dynamic_per_request", 3)]
    return core + dyn + lens_out + chal


def compose(selected: list[dict]) -> str:
    blocks = []
    for x in selected:
        s: Skill = x["skill"]
        note = f"\n\n[CaseOS adapter] {s.adapter_note}" if s.adapter_note else ""
        blocks.append(f'<skill id="{s.id}" source="{s.source}" mode="{x["mode"]}">\n{s.body()}{note}\n</skill>')
    return "\n\n".join(blocks)


def record(selected: list[dict]) -> list[dict]:
    return [{"id": x["skill"].id, "mode": x["mode"], "why": x.get("why", ""), "source": x["skill"].source,
             "kind": x["skill"].kind, "digest": x["skill"].digest()} for x in selected]


def for_agent(agent: str) -> list[dict]:
    """All skills an agent can use (for the topology / under-the-hood views)."""
    out = []
    for s in registry().values():
        b = s.bindings.get(agent)
        if b:
            out.append({**s.public(), "binding": {"mode": b.mode, "modes": b.modes, "intensity": b.intensity,
                                                   "triggers": b.triggers or (s.triggers if b.mode == "lens" else [])}})
    order = {"core": 0, "dynamic": 1, "lens": 2, "challenge": 3, "linked": 4, "reference": 5}
    return sorted(out, key=lambda x: (order.get(x["binding"]["mode"], 9), x["id"]))


def check_links() -> list[dict]:
    """Linked skills (the Visual Storyteller) must exist on this machine."""
    return [{"id": s.id, "path": _display_path(s.path), "exists": s.exists} for s in registry().values() if s.kind == "linked"]


# ------------------------------------------------------------------------------------------ human view (SKILLS.md)
AGENT_NAMES = {"framer": "Framer", "cos": "Chief of Staff", "router": "Research Router", "business_research": "Business Research",
               "measurement": "Measurement", "data_engineering": "Data Engineering", "analytics": "Analytics",
               "visual_storyteller": "Visual Storyteller"}
MODE_ORDER = ["core", "dynamic", "challenge", "lens", "linked", "reference"]


def render_md() -> str:
    """SKILLS.md is generated from skills/manifest.yaml (`python -m caseos skills --md`), so the two never drift."""
    reg = registry()
    rows = []
    for s in reg.values():
        uses = []
        for a, b in s.bindings.items():
            extra = []
            if b.modes:
                extra.append("modos " + "/".join(b.modes))
            if b.intensity:
                extra.append("/".join(b.intensity))
            if b.mode == "dynamic" and b.triggers:
                extra.append("si: " + ", ".join(b.triggers[:4]) + ("…" if len(b.triggers) > 4 else ""))
            uses.append(f"{AGENT_NAMES.get(a, a)} · **{b.mode}**" + (f" ({'; '.join(extra)})" if extra else ""))
        if not uses:
            uses = [f"— · **{s.kind}**" + (f" → adaptada en {', '.join(s.adapted_into)}" if s.adapted_into else "")]
        rows.append((min((MODE_ORDER.index(b.mode) for b in s.bindings.values()), default=len(MODE_ORDER)), s, uses))
    rows.sort(key=lambda r: (r[0], r[1].id))
    esc = lambda x: str(x or "").replace("|", "\\|").replace("\n", " ")
    out = ["# Skills de CaseOS", "",
           "Generado desde `skills/manifest.yaml` con `python -m caseos skills --md`. No lo edites a mano.", "",
           "Las skills no son una bolsa plana: cada agente tiene skills **core** (siempre), **dynamic** (por disparadores, máx. 3 "
           "por solicitud), **challenge** (solo en Challenge o crítica), **lens** (advisors C-level como lentes: 0–1, máx. 2), "
           "**linked** (capacidad existente de Hugo, enlazada sin copiar) y **reference** (se conservan por procedencia; su "
           "contenido se adaptó a una skill de CaseOS y no se cargan).", "",
           "Cada corrida registra qué skills cargó y el hash de cada SKILL.md (ver *Under the hood* y `audit/runs/`).", "",
           "| Skill | Fuente | Agente · modo | Propósito | Ruta | Licencia | Presente |", "|---|---|---|---|---|---|---|"]
    for _, s, uses in rows:
        out.append(f"| `{s.id}` | {esc(s.source)} | {'<br>'.join(esc(u) for u in uses)} | {esc(s.purpose)} | "
                   f"`{esc(_display_path(s.path))}` | {esc(s.license)} | {'sí' if s.exists else '**falta**'} |")
    notes = [s for s in reg.values() if s.adapter_note]
    if notes:
        out += ["", "## Notas de adaptación (se inyectan al cargar la skill)", ""]
        out += [f"- `{s.id}` — {esc(s.adapter_note)}" for s in sorted(notes, key=lambda s: s.id)]
    return "\n".join(out) + "\n"
