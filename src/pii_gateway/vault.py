"""Mapowanie token <-> oryginal w obrebie sesji, z TTL.

Interfejs jest prosty, zeby pozniej latwo podmienic implementacje na Redis.
"""
import re
import time
from collections import defaultdict

TOKEN_RE = re.compile(r"<[A-Z_]+_\d+>")


class Vault:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._forward: dict[str, dict[tuple[str, str], str]] = defaultdict(dict)
        self._reverse: dict[str, dict[str, str]] = defaultdict(dict)
        self._counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._expires: dict[str, float] = {}

    def _touch(self, session_id: str) -> None:
        self._purge()
        self._expires[session_id] = time.time() + self.ttl

    def _purge(self) -> None:
        now = time.time()
        for sid in [s for s, exp in self._expires.items() if exp < now]:
            self.drop(sid)

    def drop(self, session_id: str) -> None:
        for store in (self._forward, self._reverse, self._counters, self._expires):
            store.pop(session_id, None)

    def get_token(self, session_id: str, entity_type: str, value: str) -> str:
        """Ten sam oryginal w tej samej sesji dostaje ten sam token."""
        self._touch(session_id)
        key = (entity_type, value)
        if key in self._forward[session_id]:
            return self._forward[session_id][key]
        self._counters[session_id][entity_type] += 1
        token = f"<{entity_type}_{self._counters[session_id][entity_type]}>"
        self._forward[session_id][key] = token
        self._reverse[session_id][token] = value
        return token

    def restore(self, session_id: str, text: str) -> str:
        self._purge()
        mapping = self._reverse.get(session_id, {})
        return TOKEN_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), text)
