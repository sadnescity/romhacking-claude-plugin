"""Text back into the game, with every overflow reported and nothing truncated.

Truncating is how a translation loses a line that nobody notices until someone
plays that scene. This module refuses to do it: what does not fit comes back as
a list of problems, and deciding what to do about it belongs to the `space`
phase.
"""
from __future__ import annotations

import dump


def insert_block(data: bytes, table, entries, start: int, end: int,
                 newline_token: str | None = None) -> tuple[bytes, list[str]]:
    """Rebuild `data[start:end]` from `entries`.

    Entries carry script-form text — `<CODES>` and real newlines — so this is
    where it turns back into table form. Returns the whole image with the block
    replaced, plus one message per entry that did not fit.
    """
    payload = bytearray()
    overflow: list[str] = []
    capacity = end - start
    for entry in entries:
        encoded = table.encode(dump.to_table(entry.text, newline_token))
        if len(payload) + len(encoded) > capacity:
            spare = max(capacity - len(payload), 0)
            overflow.append(
                f"entry {entry.index} at 0x{entry.offset:X}: needs {len(encoded)} bytes, "
                f"{spare} left in the block ({len(encoded) - spare} over)"
            )
            continue
        payload += encoded
    rebuilt = bytearray(data)
    rebuilt[start:start + len(payload)] = payload
    return bytes(rebuilt), overflow


def measure(table, entries, newline_token: str | None = None) -> dict[int, int]:
    """Bytes each entry will occupy. Useful before touching the ROM at all."""
    return {
        entry.index: len(table.encode(dump.to_table(entry.text, newline_token)))
        for entry in entries
    }
