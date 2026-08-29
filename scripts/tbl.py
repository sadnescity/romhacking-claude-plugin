"""Table files: the mapping between raw bytes and readable text.

Implements the TBL format as specified by Nightcrawler (TransCorp), version 1.0
draft. A table is the first artifact of a translation project and the one
everything else rests on: its correctness is proved by round-trip, never
asserted.

Directives, from the specification:

    ``HH=text``            normal entry; hex is even-length and big-endian
    ``$HH=[Label],p1,p2``  control code, one raw byte per parameter string
    ``/HH=[Label]``        end token, no parameters
    ``!HH=[ID],fallback``  table switching (parsed, see SWITCHING below)
    ``@ID``                table identifier
    ``#``                  comment, whole line
    ``[$HH]``              raw byte with no table entry

A trailing ``\\n`` in a non-normal label affects dump formatting only and is
ignored on insertion.

SWITCHING: ``!`` and ``@`` are parsed and recorded, but switching between
tables while decoding is not implemented. Encountering a switch entry while
decoding raises TableError rather than silently producing wrong text. A game
whose contexts use different charsets can still be handled with one table file
per context. See references/SOURCES.md.
"""
from __future__ import annotations

import pathlib
import re

ENTRY_RE = re.compile(r"^(?P<prefix>[$/!])?(?P<hex>[0-9A-Fa-f]+)=(?P<value>.*)$")
TABLE_ID_RE = re.compile(r"^@(?P<id>[0-9A-Za-z]+)\s*$")
LABEL_RE = re.compile(r"^\[(?P<label>[^\[\]]*)\]")
TOKEN_RE = re.compile(r"\[[^\[\]]*\]")
RAW_TOKEN_RE = re.compile(r"^\[\$(?P<hex>[0-9A-Fa-f]+)\]$")


class TableError(Exception):
    """Raised when bytes cannot be decoded or text cannot be encoded."""


class Entry:
    """One table entry: the bytes, the text it stands for, and its kind."""

    __slots__ = ("raw", "text", "kind", "params")

    def __init__(self, raw: bytes, text: str, kind: str = "normal", params: int = 0):
        self.raw = raw
        self.text = text
        self.kind = kind
        self.params = params

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Entry({self.raw.hex().upper()}, {self.text!r}, {self.kind})"


class Table:
    def __init__(self, entries):
        if isinstance(entries, dict):
            entries = [Entry(raw, text) for raw, text in entries.items()]
        self._entries: list[Entry] = list(entries)
        self.table_id: str | None = None
        self.entries: dict[bytes, str] = {e.raw: e.text for e in self._entries}
        self._by_raw: dict[bytes, Entry] = {e.raw: e for e in self._entries}
        self.max_len = max((len(e.raw) for e in self._entries), default=1)
        # Text collisions resolve to the shortest hex sequence; when two are the
        # same length the last occurrence wins (specification, Text Collisions).
        self._to_bytes: dict[str, bytes] = {}
        for entry in self._entries:
            current = self._to_bytes.get(entry.text)
            if current is None or len(entry.raw) <= len(current):
                self._to_bytes[entry.text] = entry.raw
        self._max_text = max((len(t) for t in self._to_bytes), default=1)

    # -- parsing --------------------------------------------------------
    @classmethod
    def parse(cls, text: str) -> "Table":
        if text.startswith("﻿"):  # BOM is optional but must be accepted
            text = text[1:]
        entries: list[Entry] = []
        seen: set[bytes] = set()
        table_id: str | None = None
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            id_match = TABLE_ID_RE.match(stripped)
            if id_match:
                table_id = id_match["id"]
                continue
            match = ENTRY_RE.match(line.rstrip("\n"))
            if not match:
                raise TableError(f"line {lineno}: cannot parse {line!r}")
            hex_part = match["hex"]
            if len(hex_part) % 2:
                raise TableError(f"line {lineno}: hex sequence must have an even length")
            raw = bytes.fromhex(hex_part)
            if raw in seen:
                raise TableError(f"line {lineno}: duplicate entry for {raw.hex().upper()}")
            seen.add(raw)
            entries.append(_make_entry(raw, match["prefix"], match["value"], lineno))
        if not entries:
            raise TableError("table is empty")
        table = cls(entries)
        table.table_id = table_id
        return table

    @classmethod
    def load(cls, path) -> "Table":
        return cls.parse(pathlib.Path(path).read_text(encoding="utf-8"))

    # -- conversion -----------------------------------------------------
    def decode(self, data: bytes, strict: bool = True) -> str:
        """Bytes to text.

        With ``strict`` an unmapped byte is an error, which is what you want
        while building a table. With ``strict=False`` it becomes ``[$HH]``, the
        raw-hex form the specification defines for dumping mismatches.
        """
        out: list[str] = []
        i = 0
        while i < len(data):
            entry = self._longest_entry(data, i)
            if entry is None:
                if strict:
                    raise TableError(f"byte {data[i]:02X} at offset {i} is not in the table")
                out.append(f"[${data[i]:02X}]")
                i += 1
                continue
            if entry.kind == "switch":
                raise TableError(
                    f"table switching at offset {i} ({entry.raw.hex().upper()}) "
                    "is not supported in this version"
                )
            i += len(entry.raw)
            if entry.params:
                if i + entry.params > len(data):
                    raise TableError(
                        f"control code {entry.raw.hex().upper()} at offset {i} wants "
                        f"{entry.params} parameter byte(s) but the data ends"
                    )
                args = data[i:i + entry.params]
                i += entry.params
                out.append(_label_with_params(entry.text, args))
            else:
                out.append(entry.text)
        return "".join(out)

    def encode(self, text: str) -> bytes:
        out = bytearray()
        i = 0
        while i < len(text):
            if text[i] == "[":
                match = TOKEN_RE.match(text, i)
                if not match:
                    raise TableError(f"unterminated token at offset {i}")
                out += self._encode_token(match.group(0), i)
                i = match.end()
                continue
            for length in range(min(self._max_text, len(text) - i), 0, -1):
                chunk = text[i:i + length]
                if "[" in chunk:
                    continue
                if chunk in self._to_bytes:
                    out += self._to_bytes[chunk]
                    i += length
                    break
            else:
                raise TableError(f"character {text[i]!r} at offset {i} is not in the table")
        return bytes(out)

    # -- internals ------------------------------------------------------
    def _longest_entry(self, data: bytes, i: int):
        for length in range(min(self.max_len, len(data) - i), 0, -1):
            entry = self._by_raw.get(data[i:i + length])
            if entry is not None:
                return entry
        return None

    def _encode_token(self, token: str, offset: int) -> bytes:
        raw_match = RAW_TOKEN_RE.match(token)
        if raw_match:
            return bytes.fromhex(raw_match["hex"])
        label, _, args = token[1:-1].partition(":")
        base = f"[{label}]"
        if base not in self._to_bytes:
            raise TableError(f"unknown token {token} at offset {offset}")
        raw = self._to_bytes[base]
        entry = self._by_raw[raw]
        values = [a for a in args.split(",") if a] if args else []
        if len(values) != entry.params:
            raise TableError(
                f"token {token} at offset {offset} carries {len(values)} parameter(s), "
                f"the table declares {entry.params}"
            )
        return raw + bytes(int(v, 16) for v in values)


def _make_entry(raw: bytes, prefix: str | None, value: str, lineno: int) -> Entry:
    if prefix is None:
        if "[" in value or "]" in value:
            raise TableError(f"line {lineno}: a normal entry cannot contain '[' or ']'")
        return Entry(raw, value)
    label_match = LABEL_RE.match(value)
    if not label_match:
        raise TableError(f"line {lineno}: a '{prefix}' entry needs a [label]")
    label = f"[{label_match['label']}]"
    rest = value[label_match.end():]
    rest = rest.replace("\\n", "")  # dump formatting only, ignored on insertion
    if prefix == "/":
        if rest.strip(", "):
            raise TableError(f"line {lineno}: an end token takes no parameters")
        return Entry(raw, label, kind="end")
    if prefix == "!":
        return Entry(raw, label, kind="switch")
    params = [p for p in rest.split(",") if p.strip()]
    return Entry(raw, label, kind="control", params=len(params))


def _label_with_params(label: str, args: bytes) -> str:
    """Round-trippable rendering: ``[Label:0A,05]``.

    The specification renders parameters through %D/%X/%B placeholders. That
    output is not unambiguously reversible — an unpadded %D cannot be told from
    the text around it — and a dump that cannot be reinserted byte-identical
    fails the only test that matters here. See references/SOURCES.md.
    """
    return f"[{label[1:-1]}:" + ",".join(f"{b:02X}" for b in args) + "]"
