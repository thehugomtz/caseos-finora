"""Agent runtime — one place where CaseOS talks to Claude.

Reuses the isolation pattern proven in the Business Exploration Workspace (finora-eda/agent/orchestrator.py):
Claude Agent SDK over the local Claude Code session (Hugo's subscription; the API if ANTHROPIC_API_KEY is set),
no built-in tools unless the agent needs them, no user settings or MCP servers leaking in, structured output via
JSON Schema. Every run is recorded (prompt hash, skills, tools, usage, tool trace) for "Under the hood".

Tests swap the runtime for FakeLLM (scripted outputs), so the product never needs a fake agent at runtime.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from . import config
from .util import now_iso, now_ms, stamp, write_json

URL_RE = re.compile(r"https?://[^\s\"'<>\)\]]+")

EventFn = Callable[[str, dict], Awaitable[None] | None]


class AgentError(RuntimeError):
    def __init__(self, kind: str, message: str, *, run_id: str | None = None):
        super().__init__(message)
        self.kind = kind          # auth · limit · timeout · schema · tool · interrupted · unknown
        self.run_id = run_id


@dataclass
class RunSpec:
    agent: str
    role: str
    system: str
    prompt: str
    schema: dict | None = None
    tools: list[str] = field(default_factory=list)        # built-in tools, e.g. ["WebSearch", "WebFetch"]
    max_turns: int = 8
    skills: list[dict] = field(default_factory=list)      # skills.record(...) of what was loaded
    lenses: list[dict] = field(default_factory=list)
    purpose: str = ""
    case_id: str | None = None
    case_root: Path | None = None
    budget_usd: float | None = None
    timeout_s: float = 900


@dataclass
class RunResult:
    run_id: str
    output: Any
    usage: dict
    cost_usd: float | None
    duration_ms: int
    tool_trace: list[dict]
    seen_urls: list[str]
    auth: str
    model: str


def _prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def save_run(spec: RunSpec, result: RunResult | None, error: str | None, started: int, run_id: str) -> None:
    """audit/runs/<run>.json + audit/prompts/<hash>.md (each distinct system prompt stored once)."""
    if not spec.case_root:
        return
    h = _prompt_hash(spec.system)
    pdir = spec.case_root / "audit" / "prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    pp = pdir / f"{h}.md"
    if not pp.exists():
        pp.write_text(spec.system, encoding="utf-8")
    rec = {"run_id": run_id, "agent": spec.agent, "role": spec.role, "purpose": spec.purpose, "started_at": now_iso(),
           "duration_ms": now_ms() - started, "model": config.model_for(spec.role),
           "effort": config.EFFORT.get(spec.role, config.DEFAULT_EFFORT), "system_prompt": f"audit/prompts/{h}.md", "system_prompt_hash": h,
           "prompt": spec.prompt, "schema": spec.schema, "tools": spec.tools, "skills": spec.skills,
           "lenses": spec.lenses, "max_turns": spec.max_turns, "status": "error" if error else "ok", "error": error}
    if result:
        rec.update({"output": result.output, "usage": result.usage, "cost_usd": result.cost_usd,
                    "tool_trace": result.tool_trace, "seen_urls": result.seen_urls, "auth": result.auth,
                    "model": result.model})
    write_json(spec.case_root / "audit" / "runs" / f"{run_id}.json", rec)


class AgentSDKLLM:
    """Claude Agent SDK runtime (the same library the existing workspace uses)."""

    def __init__(self, concurrency: int = 3):
        self._sem = asyncio.Semaphore(concurrency)

    async def run(self, spec: RunSpec, on_event: EventFn | None = None) -> RunResult:
        from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage, ToolResultBlock,
                                      ToolUseBlock, UserMessage, query)
        try:
            from claude_agent_sdk import ServerToolResultBlock, ServerToolUseBlock
        except ImportError:  # pragma: no cover
            ServerToolResultBlock = ServerToolUseBlock = ()  # type: ignore

        run_id = f"RUN-{stamp()}-{spec.agent}-{uuid.uuid4().hex[:4]}"
        started = now_ms()
        config.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        model = config.model_for(spec.role)
        opts = ClaudeAgentOptions(
            tools=list(spec.tools), allowed_tools=list(spec.tools), setting_sources=[], strict_mcp_config=True,
            system_prompt=spec.system, model=model, effort=config.EFFORT.get(spec.role, config.DEFAULT_EFFORT),
            max_turns=spec.max_turns, cwd=str(config.RUNTIME_DIR), verbatim_prompts=True,
            max_budget_usd=spec.budget_usd or config.BUDGET_USD.get(spec.role),
            output_format={"type": "json_schema", "schema": spec.schema} if spec.schema else None)
        trace: list[dict] = []
        seen: list[str] = []
        pending: dict[str, dict] = {}
        auth = "desconocida"
        output, usage, cost = None, {}, None

        async def emit(kind, data):
            if on_event:
                r = on_event(kind, data)
                if asyncio.iscoroutine(r):
                    await r

        async def consume():
            nonlocal auth, output, usage, cost
            async for m in query(prompt=spec.prompt, options=opts):
                if isinstance(m, SystemMessage) and getattr(m, "subtype", "") == "init":
                    src = (m.data or {}).get("apiKeySource")
                    auth = "suscripción de Claude (sesión de Claude Code)" if src in (None, "none") else f"API key ({src})"
                    await emit("session", {"auth": auth, "model": model})
                elif isinstance(m, AssistantMessage):
                    for b in m.content:
                        if (isinstance(b, ToolUseBlock) or (ServerToolUseBlock and isinstance(b, ServerToolUseBlock))) and b.name != "StructuredOutput":
                            item = {"id": b.id, "tool": b.name, "input": _small(b.input), "t": now_ms() - started}
                            for u in URL_RE.findall(json.dumps(b.input, ensure_ascii=False)):
                                seen.append(u)
                            pending[b.id] = item
                            trace.append(item)
                            await emit("tool", {"tool": b.name, "summary": _tool_summary(b.name, b.input)})
                        if (ServerToolResultBlock and isinstance(b, ServerToolResultBlock)):
                            txt = json.dumps(b.content, ensure_ascii=False)[:200000]
                            seen.extend(URL_RE.findall(txt))
                            if b.tool_use_id in pending:
                                pending[b.tool_use_id]["result_chars"] = len(txt)
                elif isinstance(m, UserMessage):
                    content = m.content if isinstance(m.content, list) else []
                    for b in content:
                        if isinstance(b, ToolResultBlock):
                            txt = b.content if isinstance(b.content, str) else json.dumps(b.content, ensure_ascii=False)
                            txt = (txt or "")[:200000]
                            seen.extend(URL_RE.findall(txt))
                            if b.tool_use_id in pending:
                                pending[b.tool_use_id]["result_chars"] = len(txt)
                                pending[b.tool_use_id]["is_error"] = bool(b.is_error)
                elif isinstance(m, ResultMessage):
                    usage = {"turns": m.num_turns, "ms": m.duration_ms, "input_tokens": (m.usage or {}).get("input_tokens"),
                             "output_tokens": (m.usage or {}).get("output_tokens"),
                             "cache_read": (m.usage or {}).get("cache_read_input_tokens"),
                             "cache_write": (m.usage or {}).get("cache_creation_input_tokens"),
                             "terminal_reason": getattr(m, "terminal_reason", None), "subtype": m.subtype}
                    cost = m.total_cost_usd
                    if m.is_error:
                        raise AgentError(_classify(m), f"{m.subtype}: {'; '.join(m.errors or []) or m.result or 'error'}", run_id=run_id)
                    output = m.structured_output if spec.schema else (m.result or "")
                    if spec.schema and output is None:
                        raise AgentError("schema", "El agente terminó sin salida estructurada.", run_id=run_id)

        error = None
        result = None
        try:
            async with self._sem:
                await emit("start", {"run_id": run_id, "agent": spec.agent, "model": model})
                await asyncio.wait_for(consume(), timeout=spec.timeout_s)
            result = RunResult(run_id=run_id, output=output, usage=usage, cost_usd=cost, duration_ms=now_ms() - started,
                               tool_trace=trace, seen_urls=sorted(set(_clean_url(u) for u in seen)), auth=auth, model=model)
            return result
        except AgentError as e:
            error = f"{e.kind}: {e}"
            raise
        except asyncio.TimeoutError:
            error = "timeout"
            raise AgentError("timeout", f"El agente tardó más de {int(spec.timeout_s)} s.", run_id=run_id)
        except asyncio.CancelledError:
            error = "interrupted"
            raise
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            kind = "interrupted" if ("exit code 143" in msg or "SIGTERM" in msg) else ("auth" if "auth" in msg.lower() or "login" in msg.lower() else "unknown")
            error = f"{kind}: {msg}"
            raise AgentError(kind, msg, run_id=run_id) from e
        finally:
            save_run(spec, result, error, started, run_id)


def _classify(m) -> str:
    text = " ".join(m.errors or []) + " " + (m.result or "") + " " + (m.subtype or "")
    t = text.lower()
    if "budget" in t:
        return "limit"
    if "rate" in t or "limit" in t or getattr(m, "api_error_status", None) in (429, 529):
        return "limit"
    if "max_turns" in t:
        return "tool"
    if "auth" in t or "login" in t or getattr(m, "api_error_status", None) == 401:
        return "auth"
    return "unknown"


def _clean_url(u: str) -> str:
    return u.rstrip(".,;:)]}'\"\\")


def _small(obj: Any, n: int = 600) -> Any:
    s = json.dumps(obj, ensure_ascii=False)
    return obj if len(s) <= n else s[:n] + "…"


def _tool_summary(name: str, inp: dict) -> str:
    if name in ("WebSearch", "web_search"):
        return f"Buscando: “{(inp or {}).get('query', '')}”"
    if name in ("WebFetch", "web_fetch"):
        return f"Leyendo: {(inp or {}).get('url', '')}"
    if name == "Read":
        return f"Leyendo archivo {(inp or {}).get('file_path', '')}"
    if name in ("Write", "Edit"):
        return f"Escribiendo {(inp or {}).get('file_path', '')}"
    if name == "Bash":
        return f"Ejecutando: {str((inp or {}).get('command', ''))[:120]}"
    if name == "Skill":
        return f"Cargando skill {(inp or {}).get('skill', '')}"
    return name


# ------------------------------------------------------------------------------------------ fake runtime (tests)
class FakeLLM:
    """Scripted runtime for tests: responders keyed by agent (callable(spec) -> output or exception)."""

    def __init__(self, responders: dict[str, Callable[[RunSpec], Any]] | None = None):
        self.responders = responders or {}
        self.calls: list[RunSpec] = []

    async def run(self, spec: RunSpec, on_event: EventFn | None = None) -> RunResult:
        self.calls.append(spec)
        run_id = f"RUN-{stamp()}-{spec.agent}-{uuid.uuid4().hex[:4]}"
        fn = self.responders.get(spec.agent) or self.responders.get(spec.role)
        if fn is None:
            raise AgentError("unknown", f"FakeLLM sin respuesta para {spec.agent}", run_id=run_id)
        out = fn(spec)
        if isinstance(out, Exception):
            save_run(spec, None, str(out), now_ms(), run_id)
            raise out
        urls = out.pop("__seen_urls", []) if isinstance(out, dict) else []
        res = RunResult(run_id=run_id, output=out, usage={"turns": 1}, cost_usd=0.0, duration_ms=1, tool_trace=[],
                        seen_urls=urls, auth="fake", model="fake")
        save_run(spec, res, None, now_ms(), run_id)
        return res


_llm: Any = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = AgentSDKLLM()
    return _llm


def set_llm(llm) -> None:
    global _llm
    _llm = llm
