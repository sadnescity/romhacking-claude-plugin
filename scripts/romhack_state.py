"""ROMHACK.md: what the project knows about itself, in a file a human can read.

A gate is never marked passed on request: it needs a date and the evidence that
made it pass.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import pathlib

SEPARATOR = "---"
NOTES_HEADING = "## Working notes"
PHASES = ["recon", "encoding", "accents", "space", "graphics", "glossary", "translation"]


class GateError(Exception):
    """Raised when a gate is asked to pass without evidence."""


class State:
    def __init__(self, data: dict, notes: str = ""):
        self.data = data
        self.notes = notes

    @property
    def phase(self) -> str:
        return self.data.get("phase", PHASES[0])

    @phase.setter
    def phase(self, value: str) -> None:
        if value not in PHASES:
            raise ValueError(f"unknown phase {value!r}; expected one of {PHASES}")
        self.data["phase"] = value

    @classmethod
    def new(cls, target_path, platform: str) -> "State":
        path = pathlib.Path(target_path)
        raw = path.read_bytes()
        return cls({
            "target": {
                "file": path.name,
                "platform": platform,
                "sha1": hashlib.sha1(raw).hexdigest(),
                "size": len(raw),
            },
            "phase": PHASES[0],
            "gates": {},
            "blocks": [],
        })

    def gate_passed(self, name: str) -> bool:
        return bool(self.data.get("gates", {}).get(name, {}).get("passed"))

    def pass_gate(self, name: str, evidence: str, when: str | None = None) -> None:
        if not evidence.strip():
            raise GateError(
                f"gate {name!r} cannot pass without evidence: record the command "
                "or the observation that proved it"
            )
        self.data.setdefault("gates", {})[name] = {
            "passed": when or datetime.date.today().isoformat(),
            "evidence": evidence.strip(),
        }

    # -- serialisation --------------------------------------------------
    def save(self, path) -> None:
        body = f"{SEPARATOR}\n{_dump(self.data)}{SEPARATOR}\n\n{NOTES_HEADING}\n{self.notes}"
        pathlib.Path(path).write_text(body, encoding="utf-8")

    @classmethod
    def load(cls, path) -> "State":
        text = pathlib.Path(path).read_text(encoding="utf-8")
        if not text.startswith(SEPARATOR):
            raise ValueError("ROMHACK.md must start with a YAML frontmatter block")
        _, frontmatter, rest = text.split(SEPARATOR, 2)
        return cls(_parse(frontmatter), _notes(rest))


def _notes(rest: str) -> str:
    """Free text after the frontmatter, without its heading, whatever it says."""
    rest = rest.lstrip("\n")
    if rest.startswith("## "):
        rest = rest.split("\n", 1)[1] if "\n" in rest else ""
    return rest.lstrip("\n")


def _dump(value: dict, indent: int = 0) -> str:
    pad = "  " * indent
    out = []
    for key, item in value.items():
        if isinstance(item, dict) and item:
            out.append(f"{pad}{key}:\n{_dump(item, indent + 1)}")
        elif isinstance(item, dict):
            out.append(f"{pad}{key}: {{}}\n")
        elif isinstance(item, list):
            if not item:
                out.append(f"{pad}{key}: []\n")
            else:
                out.append(f"{pad}{key}:\n")
                out.extend(f"{pad}  - {json.dumps(entry)}\n" for entry in item)
        else:
            out.append(f"{pad}{key}: {json.dumps(item)}\n")
    return "".join(out)


def _parse(text: str) -> dict:
    lines = [line for line in text.splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    pending_list: list | None = None
    for position, line in enumerate(lines):
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if stripped.startswith("- "):
            if pending_list is None:
                raise ValueError(f"list item outside a list: {line!r}")
            pending_list.append(json.loads(stripped[2:]))
            continue
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        key, _, raw = stripped.partition(":")
        raw = raw.strip()
        pending_list = None
        if raw == "":
            # A bare key opens either a mapping or a list, and only the next
            # line says which. Without this lookahead a list of blocks parses
            # as an empty dict and its items have nowhere to go.
            following = lines[position + 1] if position + 1 < len(lines) else ""
            opens_a_list = following.strip().startswith("- ") and \
                len(following) - len(following.lstrip()) > indent
            if opens_a_list:
                parent[key] = pending_list = []
            else:
                child: dict = {}
                parent[key] = child
                stack.append((indent, child))
        elif raw == "[]":
            parent[key] = pending_list = []
        elif raw == "{}":
            parent[key] = {}
        else:
            parent[key] = json.loads(raw)
    return root
