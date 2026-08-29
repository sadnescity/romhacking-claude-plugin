"""Minimal JSON-RPC transport to MesenCE's built-in MCP server.

If the `mesence` plugin is loaded, use its MCP tools directly — they are typed
and documented. This module exists only for sessions where it is not, and does
not reimplement any of them: it carries calls and returns answers.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

DEFAULT_URL = "http://localhost:9100/mcp"
PROTOCOL = "2025-11-25"


class MesenError(Exception):
    """Raised when the server answers with an error."""


class MesenRPC:
    def __init__(self, url: str = DEFAULT_URL, timeout: float = 10.0):
        self.url = url
        self.timeout = timeout
        self.session: str | None = None
        self._id = 0

    def _post(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        payload = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or {}}
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )
        if self.session:
            request.add_header("MCP-Session-Id", self.session)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            session = response.headers.get("MCP-Session-Id")
            if session:
                self.session = session
            body = response.read().decode("utf-8", "replace")
        return _decode(body)

    def initialize(self) -> dict:
        result = self._post("initialize", {
            "protocolVersion": PROTOCOL,
            "capabilities": {},
            "clientInfo": {"name": "romhacking", "version": "1.0.0"},
        })
        try:
            self._post("notifications/initialized")
        except Exception:
            pass  # some servers do not answer notifications; harmless
        return result

    def list_tools(self) -> list[dict]:
        return self._post("tools/list").get("tools", [])

    def call(self, name: str, **arguments):
        return self._post("tools/call", {"name": name, "arguments": arguments})

    def available(self) -> bool:
        try:
            self.initialize()
            return True
        except (urllib.error.URLError, OSError, ValueError, MesenError):
            return False


def _decode(body: str) -> dict:
    """Accept both a plain JSON body and an SSE stream of `data:` lines."""
    text = body.strip()
    if text.startswith("event:") or text.startswith("data:"):
        chunks = [line[5:].strip() for line in text.splitlines() if line.startswith("data:")]
        if not chunks:
            raise MesenError(f"no data in SSE response: {body[:200]}")
        text = chunks[-1]
    message = json.loads(text)
    if "error" in message:
        raise MesenError(str(message["error"]))
    return message.get("result", {})
