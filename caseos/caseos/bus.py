"""In-process event bus for the live UI (Server-Sent Events).

Stores and jobs publish from any thread; subscribers are asyncio queues living on the server loop.
Nothing here is durable: the durable trace is audit/activity.jsonl.
"""
from __future__ import annotations

import asyncio
import threading
from collections import defaultdict, deque

_loop: asyncio.AbstractEventLoop | None = None
_subs: dict[str, set[asyncio.Queue]] = defaultdict(set)
_recent: dict[str, deque] = defaultdict(lambda: deque(maxlen=200))
_lock = threading.Lock()


def bind_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _loop
    _loop = loop


def publish(channel: str, event: dict) -> None:
    with _lock:
        _recent[channel].append(event)
        queues = list(_subs.get(channel, ())) + list(_subs.get("*", ()))
    if not queues or _loop is None or _loop.is_closed():
        return

    def _push():
        for q in queues:
            if q.qsize() < 1000:
                q.put_nowait({"channel": channel, **event})

    try:
        running = asyncio.get_running_loop()
    except RuntimeError:
        running = None
    if running is _loop:
        _push()
    else:
        _loop.call_soon_threadsafe(_push)


def subscribe(channel: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    with _lock:
        _subs[channel].add(q)
    return q


def unsubscribe(channel: str, q: asyncio.Queue) -> None:
    with _lock:
        _subs[channel].discard(q)


def recent(channel: str) -> list[dict]:
    with _lock:
        return list(_recent.get(channel, ()))
