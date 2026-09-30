"""Adapter to the existing Executive Visual Storyteller (agents/visual-storyteller.md). Not rebuilt: invoked.

prepare(): Story Ready required → deck folder scaffolded with the storyteller's own `new-deck.mjs` → storyline.md
pre-filled from the approved Story Package (its Stage 1 contract) → data/<table>.yaml (slide data contract) →
caseos-handoff.yaml. run(): the storyteller skills run through the Claude Agent SDK with project settings only
(skills linked from ~/.claude/skills into .claude/skills), writes fenced to the deck folder, Bash limited to the
renderer scripts and read-only commands. import_deck(): slides come back as S- entities with their claim lineage.
"""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

from . import cases, config, jobs, phases, slidestyle
from .llm import AgentError
from .model import title_of
from .store import CaseStore, StoreError
from .util import clip, now_iso, now_ms, read_yaml, slugify, stamp, write_json, yaml_dump

DIRECTIONS = {"editorial": "Editorial — serif display, mucho aire, un acento",
              "modern": "Modern — sans geométrica, contraste alto",
              "blueprint": "Blueprint — técnico, líneas finas, rejilla visible",
              "auto": "Elige tú (el Storyteller decide y justifica)"}


def renderer_dir() -> Path:
    return config.USER_SKILLS_DIR / "html-slide-renderer"


def ensure_links() -> list[dict]:
    """Link Hugo's storyteller skills + agents into the project's .claude/ (never copies, never forks)."""
    out = []
    sk = config.ROOT / ".claude" / "skills"
    sk.mkdir(parents=True, exist_ok=True)
    for name in config.STORYTELLER_SKILLS:
        src, dst = config.USER_SKILLS_DIR / name, sk / name
        if src.exists() and not dst.exists():
            dst.symlink_to(src, target_is_directory=True)
        out.append({"skill": name, "linked": dst.exists(), "target": str(src).replace(str(Path.home()), "~")})
    ag = config.ROOT / ".claude" / "agents"
    ag.mkdir(parents=True, exist_ok=True)
    for name in ("executive-visual-storyteller.md", "independent-slide-critic.md"):
        src, dst = config.USER_AGENTS_DIR / name, ag / name
        if src.exists() and not dst.exists():
            dst.symlink_to(src)
        out.append({"agent": name, "linked": dst.exists()})
    return out


def decks(store: CaseStore) -> list[dict]:
    return (store.read_data("slides/decks.yaml", {}) or {}).get("decks", [])


def _save_decks(store: CaseStore, items: list[dict]) -> None:
    store.write_data("slides/decks.yaml", {"decks": items})


def _upsert_deck(store: CaseStore, deck: dict) -> None:
    items = [d for d in decks(store) if d["id"] != deck["id"]] + [deck]
    _save_decks(store, sorted(items, key=lambda d: d["created_at"]))


# ------------------------------------------------------------------------------------------ prepare
def reuse_index(store: CaseStore, prev_dir: Path, since: str = "") -> list[dict]:
    """The slides of a previous deck by claim: a claim whose headline and answer are the ones that deck drew (its
    caseos-handoff.yaml) keeps its slide, re-themed; anything new or changed is drawn again. Content, not timestamps:
    accepting or rescoring a claim touches it without changing what the slide says."""
    before = {c.get("claim_id"): c for c in (read_yaml(prev_dir / "caseos-handoff.yaml", {}) or {}).get("claims") or []}
    out = []
    for sp in sorted((prev_dir / "slide-specs").glob("S*.yaml")) if (prev_dir / "slide-specs").is_dir() else []:
        spec = _spec(sp)
        s = spec.get("slide") or spec
        num = re.sub(r"\D", "", s.get("id") or sp.stem) or "0"
        cid = s.get("claim_id") or spec.get("claim_id") or ""
        c = store.get(cid) if cid else None
        out.append({"claim_id": cid or None, "spec": f"slide-specs/{sp.name}", "slide": f"slides/{int(num):02d}.html",
                    "render": f"renders/{int(num):02d}.png", "headline": s.get("headline") or s.get("title") or "",
                    "unchanged": bool(c) and cid in before and all((c.get(k) or "") == (before[cid].get(k) or "")
                                                                   for k in ("headline", "answer"))})
    return out


def prepare(store: CaseStore, *, direction: str = "editorial", critic: bool = True, title: str = "",
            actor: str = "hugo", style: dict | None = None, reuse_from: str = "") -> dict:
    meta = store.meta()
    if meta["phases"]["story"].get("status") != "ready":
        raise StoreError("El Story Package tiene que estar aprobado (Story Ready) antes de pasarlo al Visual Storyteller.")
    pkg = store.read_data("story/package.yaml")
    if not pkg or not (pkg.get("validation") or {}).get("ok"):
        raise StoreError("El Story Package no pasó la validación.")
    if direction not in DIRECTIONS:
        raise StoreError(f"Dirección desconocida: {direction}")
    ensure_links()
    brief = store.read_data("brief/brief.yaml", {}) or {}
    title = title or f"{meta.get('name')} · {clip(pkg.get('governing_thought', ''), 70)}"
    slug = f"{slugify(meta.get('name', store.id), 16)}-v{pkg.get('version', 1)}-{stamp()}"
    deck = store.root / "slides" / "decks" / slug
    deck.parent.mkdir(parents=True, exist_ok=True)
    script = renderer_dir() / "scripts" / "new-deck.mjs"
    if not script.exists():
        raise StoreError("No encuentro html-slide-renderer en ~/.claude/skills: el Visual Storyteller no está instalado aquí.")
    theme = direction if direction != "auto" else "editorial"
    p = subprocess.run(["node", str(script), str(deck), "--title", title, "--direction", theme, "--lang",
                        (meta.get("language") or {}).get("primary", "es")], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        raise StoreError(f"new-deck.mjs falló: {p.stderr[-400:]}")
    reuse = None
    if reuse_from:
        # the previous deck's slides travel with the new one so the Storyteller redraws only what changed
        prev = next((x for x in decks(store) if x["id"] == reuse_from), None)
        if not prev:
            raise StoreError(f"No encuentro el deck {reuse_from} para reutilizar.")
        prev_dir = store.root / prev["path"]
        dst = deck / "reuse" / prev["slug"]
        for sub in ("slides", "slide-specs"):
            if (prev_dir / sub).is_dir():
                shutil.copytree(prev_dir / sub, dst / sub)
        (dst / "renders").mkdir(parents=True, exist_ok=True)
        for png in (prev_dir / "renders").glob("[0-9][0-9].png") if (prev_dir / "renders").is_dir() else []:
            shutil.copy2(png, dst / "renders" / png.name)
        idx = reuse_index(store, prev_dir)
        (dst / "index.yaml").write_text(yaml_dump({"from": prev["slug"], "slides": idx}), encoding="utf-8")
        reuse = {"from": prev["slug"], "dir": f"reuse/{prev['slug']}", "index": f"reuse/{prev['slug']}/index.yaml",
                 "unchanged": sum(1 for x in idx if x["unchanged"]), "slides": len(idx)}
    applied = None
    if style and not slidestyle.is_empty(style):
        base_dir = theme if theme in ("editorial", "modern", "blueprint") else "editorial"
        applied = slidestyle.apply_to_deck(deck, style, base_dir)
        q = subprocess.run(["node", str(script), str(deck), "--set-direction", str(deck / applied["theme"])], capture_output=True,
                           text=True, timeout=60)
        if q.returncode != 0:
            raise StoreError(f"No pude aplicar la guía de formato: {q.stderr[-300:]}")
        meta = store.meta()
        meta["slides_style"] = {**applied["style"], "saved_at": now_iso()}
        store.save_meta(meta)
    ents = store.all()
    tables = {}
    for c in pkg.get("claims") or []:
        for tid in c.get("table_ids") or []:
            t = ents.get(tid)
            if t:
                tables[tid] = t
    data_dir = deck / "data"
    data_dir.mkdir(exist_ok=True)
    for tid, t in tables.items():
        (data_dir / f"{t.get('table_key') or tid}.yaml").write_text(yaml_dump(slide_table(t)), encoding="utf-8")
    (deck / "storyline.md").write_text(storyline_md(store, pkg, tables, title, brief), encoding="utf-8")
    handoff = {"caseos_handoff": True, "case": store.id, "created_at": now_iso(), "created_by": actor,
               "story_package_version": pkg.get("version"), "direction": direction, "independent_critic": critic,
               "audience": pkg.get("audience"), "objective": pkg.get("objective"), "language_profile": pkg.get("language_profile"),
               "governing_thought": pkg.get("governing_thought"), "claims": pkg.get("claims"),
               "tables": {tid: f"data/{t.get('table_key') or tid}.yaml" for tid, t in tables.items()},
               "frameworks": [{"id": d, "title": title_of(ents[d])} for c in pkg.get("claims") or [] for d in c.get("framework_ids") or [] if d in ents],
               "research": sorted({r for c in pkg.get("claims") or [] for r in c.get("research_ids") or []}),
               "limitations": sorted({l for c in pkg.get("claims") or [] for l in c.get("limitations") or []}),
               "appendix_candidates": pkg.get("appendix_candidates"), "visual_references": pkg.get("visual_references"),
               "guion": (store.read_data("framing/current.yaml", {}) or {}).get("storyline_guide") or [],
               "guion_map": pkg.get("guion_map") or [],
               "brand_system": ({"note": "Guía de formato de Hugo aplicada como tokens del tema (assets/theme.css).", **applied}
                                if applied else {"note": "Sin marca impuesta: tokens del tema elegido."}),
               "rules": ["No cambies el argumento ni las cifras del Story Package; si algo no se sostiene, anótalo en storyline.md §7.",
                         "Toda cifra de una slide sale de data/*.yaml (usa los valores literales).",
                         "Conserva claim_id en cada slide spec (campo claim_id) para el linaje CaseOS."]
                        + (["Reutiliza: en " + reuse["index"] + " están las láminas del deck anterior por claim_id; si una dice "
                            "unchanged: true, copia su spec y su HTML a tu numeración nueva y adáptalos al tema nuevo en vez de "
                            "rehacerlos. Rehaz solo lo nuevo, lo que cambió y lo que la guía de formato pide (portadas, separadores)."]
                           if reuse else []),
               **({"reuse": reuse} if reuse else {})}
    (deck / "caseos-handoff.yaml").write_text(yaml_dump(handoff), encoding="utf-8")
    rec = {"id": f"DECK-{stamp()}", "slug": slug, "path": str(deck.relative_to(store.root)), "title": title,
           "direction": "caseos" if applied else direction, "critic": critic, "status": "prepared", "created_at": now_iso(),
           "style": applied,
           "package_version": pkg.get("version"), "tables": len(tables), "claims": len(pkg.get("claims") or []),
           **({"reuse_from": reuse_from, "reused_unchanged": reuse["unchanged"]} if reuse else {})}
    _upsert_deck(store, rec)
    phases.touch(store, "slides", actor=actor)
    store.log(actor, "handoff", [rec["id"]], f"Story Package v{pkg.get('version')} preparado para el Visual Storyteller ({slug})",
              material=True)
    return rec


def slide_table(t: dict) -> dict:
    """§62 slide data contract."""
    return {"table_id": t.get("table_key") or t["id"], "caseos_id": t["id"], "title": t.get("title"), "columns": t.get("columns"),
            "rows": t.get("rows"), "units": t.get("units"), "definitions": t.get("definitions"), "message": t.get("message"),
            "source": t.get("source"), "limitations": t.get("limitations"), "preferred_visual": t.get("preferred_visual"),
            "analysis_reference": t.get("analysis_id"), "period": t.get("period"), "grain": t.get("grain")}


def guion_block(store: CaseStore, pkg: dict) -> list[str]:
    """Hugo's approved storyline guide (Shaping) with the COS's coverage per slide: the order and the question of each
    slide come from Hugo; the claims and figures come from the Story Package."""
    fr = store.read_data("framing/current.yaml", {}) or {}
    guide = fr.get("storyline_guide") or []
    if not guide:
        return []
    cov = {g.get("slide_id"): g for g in pkg.get("guion_map") or []}
    L = ["## 1b. Guion de Hugo (orden de secciones y láminas: respétalo)", "",
         "| Lámina | Pregunta que responde | Qué debe mostrar | Claims | Cobertura |", "|---|---|---|---|---|"]
    for sec in guide:
        L.append(f"| **{sec['id']} · {sec.get('title')}** | {sec.get('purpose', '')} | | | |")
        for sl in sec.get("slides") or []:
            g = cov.get(sl["id"], {})
            L.append(f"| {sl['id']} {sl.get('title', '')} | {sl.get('question', '')} | {clip(sl.get('intent', ''), 220)} | "
                     f"{', '.join(g.get('claim_ids') or []) or '—'} | {g.get('coverage', 'sin mapear')} |")
    L += ["", "Las láminas `missing` no se diseñan con cifras: si Hugo las quiere en el deck, van como pregunta abierta o se "
              "quedan fuera; anótalo en §7.", ""]
    return L


def storyline_md(store: CaseStore, pkg: dict, tables: dict, title: str, brief: dict) -> str:
    ents = store.all()
    claims = pkg.get("claims") or []
    ft = pkg.get("from_to") or {}
    fmt = "; ".join(brief.get("deliverables") or [])[:300]
    L = [f"# Storyline — {title}", "",
         f"> Pre-llenado por CaseOS desde el **Story Package v{pkg.get('version')}** aprobado por Hugo "
         f"({str(pkg.get('generated_at', ''))[:10]}). Es el Stage 1 del Executive Visual Storyteller: puedes pulir títulos y "
         "recortar texto, **no cambies el argumento ni las cifras**; lo que no se sostenga va a §7 para Hugo. Las cifras de cada "
         "slide están en `data/*.yaml`. Conserva `claim_id` en cada spec.", "",
         "## 1. Audiencia y decisión", "", "| | |", "|---|---|",
         f"| **Audiencia** | {', '.join(pkg.get('audience') or [])} |",
         f"| **Objetivo / decisión** | {pkg.get('objective', '')} |",
         f"| **Qué creen hoy (From)** | {ft.get('from', '—')} |",
         f"| **Qué deben creer al salir (To)** | {ft.get('to', '—')} |",
         f"| **Formato** | {fmt or 'presentado + pre-lectura'} |",
         f"| **Idioma** | {(pkg.get('language_profile') or {}).get('primary', 'es')} — tono directo y conversacional; conservar términos de Hugo |", "",
         *guion_block(store, pkg),
         "## 2. Governing thought", "", f"> **{pkg.get('governing_thought', '')}**", "",
         "## 3. Pirámide", "", f"Lógica: {(pkg.get('story_arc') or {}).get('archetype', '')} — {(pkg.get('story_arc') or {}).get('logic', '')}", "",
         "```", f"Governing thought: {pkg.get('governing_thought', '')}"]
    for s in pkg.get("sections") or []:
        L.append(f"├─ {s.get('name')}")
        for cid in s.get("claim_ids") or []:
            c = next((x for x in claims if x["claim_id"] == cid), None)
            if c:
                L.append(f"│   └─ {cid}: {c['headline']}")
    L += ["```", "", "## 4. Secuencia", "", "| # | Pregunta de la audiencia | Título (conclusión) | Rol | Claim |", "|---|---|---|---|---|"]
    for i, c in enumerate(claims, 1):
        L.append(f"| S{i:02d} | {c.get('question', '')} | {c['headline']} | {c.get('role_in_story')} | {c['claim_id']} |")
    L += ["", "**Read-through (solo títulos):** " + " → ".join(c["headline"] for c in claims), "", "## 5. Slide briefs", ""]
    for i, c in enumerate(claims, 1):
        support = []
        for fid in c.get("evidence_ids") or []:
            f = ents.get(fid)
            if f:
                support.append({"claim": clip(title_of(f), 300), "type": "FACT",
                                "source": f"{fid}{' · ' + f['alias'] if f.get('alias') else ''}",
                                "strength": {"high": "strong", "medium": "partial"}.get(f.get("confidence"), "partial")})
        if c.get("role_in_story") == "recommendation":
            support.append({"claim": c.get("answer", ""), "type": "PROPOSAL", "logic": "recomendación condicional del Story Package"})
        elif c.get("answer"):
            support.append({"claim": c.get("answer", ""), "type": "INFERENCE", "logic": "síntesis del COS sobre la evidencia citada"})
        data = [tables[t].get("table_key") or t for t in c.get("table_ids") or [] if t in tables]
        brief_ = {"slide_id": f"S{i:02d}", "claim_id": c["claim_id"], "question": c.get("question", ""), "message": c["headline"],
                  "role_in_story": c.get("role_in_story"), "support": support, "data": [f"data/{d}.yaml" for d in data],
                  "visual_intent": c.get("visual_intent", ""),
                  "must_show": [x for x in re.findall(r"[−\-]?\d[\d.,]*\s?(?:%|×|mil|millones)?", c["headline"])][:4] or ["la relación de la intención visual"],
                  "must_not_do": ["No tres cards con bullets.", "No convertirlo en una tabla.", "No cifras que no estén en data/."],
                  "takeaway": c["headline"], "notes": "; ".join(c.get("limitations") or []),
                  "evidence_gaps": [] if c.get("strength") == "supported" else [f"fuerza: {c.get('strength')}"]}
        if c.get("hugo_wording"):
            brief_["notes"] = (brief_["notes"] + f" · En palabras de Hugo: “{c['hugo_wording']}”").strip(" ·")
        L += ["```yaml", yaml_dump(brief_).strip(), "```", ""]
    L += ["## 6. Lo que NO aparece (cortes) y apéndice", ""]
    L += [f"- {a.get('title')} — {a.get('why')}" for a in pkg.get("appendix_candidates") or []] or ["- —"]
    L += ["", "## 7. Claims sin evidencia / supuestos / preguntas abiertas", ""]
    L += [f"- {q}" for q in pkg.get("unresolved_questions") or []]
    L += [f"- Limitación: {l}" for l in sorted({l for c in claims for l in c.get("limitations") or []})]
    L += ["- (El Storyteller anota aquí lo que no se sostenga al diseñar.)", ""]
    return "\n".join(L)


# ------------------------------------------------------------------------------------------ run (existing skills via SDK)
def submit_run(store: CaseStore, deck_id: str, *, via: str = "") -> dict:
    d = next((x for x in decks(store) if x["id"] == deck_id), None)
    if not d:
        raise StoreError("Deck no encontrado.")
    busy = [x["slug"] for x in decks(store) if x.get("status") == "running"]
    if busy:
        raise StoreError(f"El Visual Storyteller ya está trabajando ({', '.join(busy)}); espera a que termine.")
    job = jobs.submit(store.id, "storyteller", f"Visual Storyteller · {d['slug']}", {"deck_id": deck_id}, agent="visual_storyteller")
    d.update({"status": "running", "job_id": job.id, "started_at": now_iso(), "error": None})
    _upsert_deck(store, d)
    store.log("hugo", "handoff", [deck_id], f"Hugo envió el Story Package al Visual Storyteller ({d['slug']})" + (f" · {via}" if via else ""),
              material=True)
    return {"job_id": job.id}


def recover_decks(store: CaseStore) -> int:
    """Decks left 'running' by a previous server process are marked interrupted (the deck folder is kept; re-run it)."""
    items, n = decks(store), 0
    for d in items:
        if d.get("status") == "running" and d.get("job_id") not in jobs.LIVE:
            d.update({"status": "interrupted", "error": "El servidor se reinició durante la corrida; la carpeta del deck se conservó."})
            n += 1
    if n:
        _save_decks(store, items)
    return n


def _guard(deck: Path, on_deny=None):
    """Permission callback for the Storyteller run. Every denial is reported through `on_deny` (trace + UI)."""
    from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny as _Deny
    deck = deck.resolve()

    async def PermissionResultDeny(message: str):  # noqa: N802 - keeps the call sites below readable
        if on_deny:
            await on_deny(message)
        return _Deny(message=message)
    rend = renderer_dir().resolve()
    allowed_roots = [deck, (config.USER_SKILLS_DIR).resolve(), (config.ROOT / ".claude").resolve()]
    ok_cmds = {"ls", "cat", "head", "tail", "wc", "grep", "find", "mkdir", "cp", "mv", "echo", "pwd", "node", "sed", "diff", "stat", "file"}

    def inside(p: str, roots) -> bool:
        try:
            rp = Path(p).expanduser().resolve()
        except Exception:  # noqa: BLE001
            return False
        return any(rp == r or r in rp.parents for r in roots)

    async def can_use(tool: str, inp: dict, _ctx):
        if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
            fp = inp.get("file_path") or inp.get("notebook_path") or ""
            if inside(fp, [deck]):
                return PermissionResultAllow()
            return await PermissionResultDeny(f"CaseOS: solo puedes escribir dentro de {deck}")
        if tool == "Bash":
            cmd = inp.get("command", "")
            if re.search(r"\brm\b|\bsudo\b|curl |wget |\bgit\b|>\s*/(?!dev/null)|\bchmod\b|\bkill\b", cmd):
                return await PermissionResultDeny("CaseOS: comando no permitido en la corrida del Storyteller.")
            try:
                parts = shlex.split(cmd)
            except ValueError:
                return await PermissionResultDeny("CaseOS: comando no interpretable.")
            first = [p for p in parts if not re.match(r"^[A-Z_]+=", p)][:1]
            if not first or os.path.basename(first[0]) not in ok_cmds:
                return await PermissionResultDeny(f"CaseOS: solo node (scripts del renderer) y comandos de lectura. Recibí: {cmd[:80]}")
            if os.path.basename(first[0]) == "node":
                scripts = [p for p in parts if p.endswith(".mjs") or p.endswith(".js")]
                if not scripts or not all(inside(s, [rend, deck]) for s in scripts):
                    return await PermissionResultDeny("CaseOS: node solo puede correr scripts de html-slide-renderer.")
            for p in parts:
                if p.startswith("/") and not inside(p, allowed_roots + [Path("/dev/null")]):
                    return await PermissionResultDeny(f"CaseOS: ruta fuera del deck: {p}")
            return PermissionResultAllow()
        if tool in ("Agent", "Task"):
            return PermissionResultAllow()
        return await PermissionResultDeny(f"CaseOS: herramienta {tool} no habilitada para el Storyteller.")
    return can_use


@jobs.handler("storyteller")
async def _run_job(job, params):
    from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage,
                                  ToolUseBlock, query)
    store = cases.get(job.case_id)
    d = next((x for x in decks(store) if x["id"] == params["deck_id"]), None)
    if not d:
        raise StoreError("Deck no encontrado.")
    deck = store.root / d["path"]
    links = ensure_links()
    missing = [l for l in links if l.get("skill") and not l["linked"]]
    if missing:
        raise StoreError("Faltan skills del Storyteller: " + ", ".join(m["skill"] for m in missing))
    direction = d.get("direction", "editorial")
    st = d.get("style") or {}
    if st:
        sg = st.get("style") or {}
        dir_text = ("Dirección visual: **la guía de formato de Hugo**, ya aplicada como tokens en assets/theme.css sobre la base "
                    f"«{st.get('base_direction')}»: tipografía de títulos {sg.get('title_font') or '(la de la base)'}, de texto "
                    f"{sg.get('text_font') or '(la de la base)'}, colores " + (", ".join(f"{k} {v}" for k, v in (sg.get('colors') or {}).items()) or "(los de la base)")
                    + ". No cambies tipografías ni colores y no corras el board de direcciones; usa el acento solo para el insight."
                    + (f" Notas de Hugo sobre el formato: «{sg['notes']}»." if sg.get("notes") else "")
                    + (" Ajustes de contraste ya hechos: " + " ".join(st.get("notes") or []) if st.get("notes") else ""))
    else:
        dir_text = ("Dirección visual: **elige tú** (Hugo dijo «autónomo»): corre el board de direcciones, elige y justifica en visual-direction.md."
                    if direction == "auto" else f"Dirección visual elegida por Hugo: **{direction}** (ya aplicada en assets/theme.css; no pidas elegir).")
    critic_text = ("Antes de terminar, pasa la crítica independiente con el agente `independent-slide-critic` y aplica sus veredictos."
                   if d.get("critic") else "No uses el agente de crítica independiente en esta corrida (Hugo lo desactivó); sí tu propio loop de QA.")
    append = f"""
# CaseOS handoff — Executive Visual Storyteller
Trabajas para CaseOS en la carpeta del deck: {deck}
Carga y sigue la skill `executive-visual-storyteller` (pipeline completo: Story → Visual direction → Concept → Render → QA loop → Package).
- Stage 1 ya está hecho: `storyline.md` viene pre-llenado desde el Story Package que Hugo aprobó. Puedes pulir títulos y recortar texto, pero NO cambies el argumento ni las cifras. Si algo no se sostiene, anótalo en storyline.md §7.
- {dir_text}
- Las cifras de cada slide están en `data/*.yaml` (contrato de datos de slides): usa esos valores literalmente; no calcules cifras nuevas.
- En cada `slide-specs/Sxx.yaml` conserva el campo `claim_id` del brief (linaje CaseOS).
- {critic_text}
- Termina con `bundle.mjs <deck> --pdf`. Escribe solo dentro de la carpeta del deck. No hay usuario disponible para preguntas: decide y documenta.
- Mensaje final: ruta del deck, archivos producidos, veredictos por slide, iteraciones, fidelidad, supuestos.
"""
    agents = None
    if d.get("critic"):
        critic_md = config.USER_AGENTS_DIR / "independent-slide-critic.md"
        if critic_md.exists():
            text = critic_md.read_text(encoding="utf-8")
            body = text.split("---", 2)[2] if text.startswith("---") else text
            agents = {"independent-slide-critic": AgentDefinition(
                description="Fresh-eyes visual critic for executive HTML decks; never edits files.",
                prompt=body.strip(), tools=["Read", "Bash", "Glob", "Grep", "Skill"], skills=["slide-critic"])}
    denials: list[dict] = []

    async def on_deny(message: str):
        denials.append({"t": now_iso(), "message": message})
        await job.event("denied", {"summary": message})

    tools = ["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep"] + (["Agent"] if agents else [])
    opts = ClaudeAgentOptions(
        tools=tools, allowed_tools=["Read", "Glob", "Grep"], skills=list(config.STORYTELLER_SKILLS),
        setting_sources=["project"], strict_mcp_config=True,
        system_prompt={"type": "preset", "preset": "claude_code", "append": append},
        model=config.model_for("storyteller"), effort=config.EFFORT.get("storyteller", config.DEFAULT_EFFORT),
        max_turns=300, max_budget_usd=config.BUDGET_USD.get("storyteller"), cwd=str(config.ROOT),
        add_dirs=[str(deck)], can_use_tool=_guard(deck, on_deny), agents=agents,
        # it reads rendered slides back (screenshots, whole HTML): one message passed the SDK's 1 MB default (29-sep, 21:51)
        max_buffer_size=64 * 1024 * 1024)
    started = now_ms()
    trace, final, usage, cost = [], "", {}, None

    # a run that was cut (a technical error, a restart) resumes from the deck folder instead of starting over
    specs = sorted((deck / "slide-specs").glob("*.yaml")) if (deck / "slide-specs").is_dir() else []
    built = sorted((deck / "slides").glob("*.html")) if (deck / "slides").is_dir() else []
    resume = ((deck / "storyline.md").exists() and specs)
    ask = f"Construye el deck ejecutivo de CaseOS en {deck} siguiendo la skill executive-visual-storyteller y el handoff."
    if resume:
        ask += (f" Esta carpeta trae el trabajo de una corrida anterior que se cortó por un error técnico, no por calidad: "
                f"storyline.md, visual-direction.md, {len(specs)} specs de lámina y {len(built)} láminas en slides/. Retoma desde ahí: "
                "conserva lo hecho salvo que la crítica visual pida cambiarlo y termina el render, la crítica y el deck final. "
                "Revisa los renders de a una lámina a la vez.")
    elif (deck / "reuse").is_dir():
        ask += (" En reuse/ están las láminas del deck anterior por claim (caseos-handoff.yaml › reuse): reutiliza las que no "
                "cambiaron, re-tematizadas; rehaz solo lo nuevo o cambiado. Revisa los renders de a una lámina a la vez.")

    async def prompt_stream():
        yield {"type": "user", "message": {"role": "user", "content": ask}}
    try:
        async for m in query(prompt=prompt_stream(), options=opts):
            if isinstance(m, SystemMessage) and getattr(m, "subtype", "") == "init":
                await job.event("session", {"skills": (m.data or {}).get("skills"), "tools": (m.data or {}).get("tools")})
            elif isinstance(m, AssistantMessage):
                for b in m.content:
                    if isinstance(b, ToolUseBlock):
                        summ = _tool_line(b.name, b.input, deck)
                        trace.append({"t": now_ms() - started, "tool": b.name, "summary": summ})
                        await job.event("tool", {"tool": b.name, "summary": summ})
            elif isinstance(m, ResultMessage):
                usage = {"turns": m.num_turns, "ms": m.duration_ms, "terminal_reason": getattr(m, "terminal_reason", None)}
                cost = m.total_cost_usd
                final = m.result or ""
                if m.is_error:
                    raise AgentError("unknown", f"{m.subtype}: {'; '.join(m.errors or []) or final[:300]}")
    except Exception as e:
        d.update({"status": "failed", "error": str(e)[:600], "finished_at": now_iso()})
        _upsert_deck(store, d)
        write_json(deck / "caseos-run.json", {"trace": trace, "denials": denials, "usage": usage, "cost_usd": cost, "error": str(e)})
        raise
    write_json(deck / "caseos-run.json", {"trace": trace, "denials": denials, "usage": usage, "cost_usd": cost, "final": final})
    result = import_deck(store, d["id"], final=final, usage=usage, cost=cost)
    return result


def _tool_line(name: str, inp: dict, deck: Path) -> str:
    deck = deck.resolve()

    def rel(p):
        return str(p).replace(str(deck) + "/", "").replace(str(Path.home()), "~")
    if name == "Skill":
        return f"Skill · {inp.get('skill', '')}"
    if name in ("Write", "Edit"):
        return f"{name} · {rel(inp.get('file_path', ''))}"
    if name == "Read":
        return f"Lee · {rel(inp.get('file_path', ''))}"
    if name == "Bash":
        return f"Bash · {rel(inp.get('command', ''))[:140]}"
    if name in ("Agent", "Task"):
        return f"Agente · {inp.get('subagent_type', '')} {clip(inp.get('description', ''), 60)}"
    return name


def _spec(path: Path) -> dict:
    """A slide spec written by the Storyteller. It is YAML written for people, so an unquoted value with «: » inside must
    not stop the import (29-sep: the finished deck failed to import): the fields CaseOS needs are then read line by line."""
    try:
        return read_yaml(path, {}) or {}
    except Exception:  # noqa: BLE001 - any YAML error falls back to the line reader
        out = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s{0,4}(id|claim_id|headline|title|composition|family|relationship):\s*(.*)$", line)
            if m and m.group(1) not in out:
                out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        return out


def import_deck(store: CaseStore, deck_id: str, *, final: str = "", usage: dict | None = None, cost=None) -> dict:
    d = next((x for x in decks(store) if x["id"] == deck_id), None)
    if not d:
        raise StoreError("Deck no encontrado.")
    deck = store.root / d["path"]
    specs = sorted((deck / "slide-specs").glob("S*.yaml")) if (deck / "slide-specs").exists() else []
    slides = sorted((deck / "slides").glob("*.html")) if (deck / "slides").exists() else []
    qa = (deck / "qa-report.md").read_text(encoding="utf-8") if (deck / "qa-report.md").exists() else ""
    created = []
    ents = store.all()
    with store.batch():
        for e in ents.values():
            if e.get("type") == "slide" and e.get("deck") == deck_id:
                store.update(e["id"], {"status": "draft", "superseded_by_run": now_iso()}, actor="system", material=False)
        for i, sp in enumerate(specs, 1):
            spec = _spec(sp)
            s = spec.get("slide") or spec
            sid = s.get("id") or sp.stem
            cid = s.get("claim_id") or (spec.get("claim_id"))
            verdict = _verdict(qa, sid)
            num = re.sub(r"\D", "", sid) or f"{i:02d}"
            html = deck / "slides" / f"{int(num):02d}.html"
            render = deck / "renders" / f"{int(num):02d}.png"
            e = store.create("slide", {
                "title": s.get("headline") or s.get("title") or sid, "slide_ref": sid, "deck": deck_id, "claim_id": cid,
                "composition": s.get("composition"), "family": s.get("family"), "relationship": s.get("relationship"),
                "html": str(html.relative_to(store.root)) if html.exists() else None,
                "render": str(render.relative_to(store.root)) if render.exists() else None,
                "status": {"PASS": "passed", "ESCALATED": "escalated"}.get(verdict, "rendered"), "qa_verdict": verdict,
                "links": [x for x in [cid] if x and x in ents]},
                actor="visual_storyteller", summary=f"Slide {sid} importada del deck", material=False)
            created.append(e["id"])
        pres = deck / "presentation.html"
        d.update({"status": "completed" if pres.exists() else "incomplete", "finished_at": now_iso(), "slides": len(slides),
                  "specs": len(specs), "presentation": str(pres.relative_to(store.root)) if pres.exists() else None,
                  "index": str((deck / "index.html").relative_to(store.root)) if (deck / "index.html").exists() else None,
                  "pdf": str((deck / "renders" / "deck.pdf").relative_to(store.root)) if (deck / "renders" / "deck.pdf").exists() else None,
                  "qa_report": "qa-report.md" if qa else None, "usage": usage or {}, "cost_usd": cost, "final_message": clip(final, 2000)})
        _upsert_deck(store, d)
        if d["status"] == "completed":
            phases.propose_review(store, "slides", actor="visual_storyteller", note="deck terminado; pendiente de revisión de Hugo")
        store.log("visual_storyteller", "completed", [deck_id] + created[:8],
                  f"Deck {d['slug']}: {len(slides)} slides · {d['status']}" + (f" · US${cost:.2f} equivalente" if cost else ""), material=True)
    return {"deck": d, "slides": created}


def _verdict(qa: str, sid: str) -> str | None:
    m = re.search(rf"{re.escape(sid)}[^\n]*?\b(PASS|PATCH|RECOMPOSE|ESCALATED)\b", qa or "")
    return m.group(1) if m else None


def deck_file(store: CaseStore, deck_slug: str, rel: str) -> Path:
    base = (store.root / "slides" / "decks" / deck_slug).resolve()
    p = (base / rel).resolve()
    if base not in p.parents and p != base:
        raise StoreError("Ruta fuera del deck.")
    return p


def shutil_which_node() -> str | None:
    return shutil.which("node")
