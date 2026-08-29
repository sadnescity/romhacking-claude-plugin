"""Patches: distributing a translation without distributing the game.

A patch is a description of the difference between the original file and yours.
Players apply it to their own copy, which is what makes releasing a translation
possible at all.

IPS is implemented here because it is the simplest thing that works and the most
widely supported. Its limits are real and worth knowing rather than discovering:
offsets are three bytes, so it cannot describe a file past 16 MB, and it records
positions rather than content, so it cannot survive a layout change.
"""
from __future__ import annotations

import hashlib

HEADER = b"PATCH"
FOOTER = b"EOF"
MAX_OFFSET = 0xFFFFFF          # three bytes
MAX_CHUNK = 0xFFFF             # two bytes
EOF_OFFSET = int.from_bytes(FOOTER, "big")   # 0x454F46, the offset that collides
RLE_WORTH_IT = 8               # shorter runs cost more as RLE than as literals


def make_ips(original: bytes, modified: bytes, target_size: int | None = None) -> bytes:
    size = target_size if target_size is not None else len(modified)
    if size > MAX_OFFSET + 1:
        raise ValueError(
            f"IPS offsets are three bytes: it cannot describe a file past "
            f"0xFFFFFF ({MAX_OFFSET + 1} bytes, 16 MB). This file is {size}. "
            "Use BPS or xdelta."
        )
    out = bytearray(HEADER)
    for start, end in _differences(original, modified):
        for chunk_start, chunk_end in _splittable(start, end):
            if chunk_start >= chunk_end:
                continue
            out += _record(modified, chunk_start, chunk_end)
    out += FOOTER
    return bytes(out)


def apply_ips(original: bytes, patch: bytes) -> bytes:
    if not patch.startswith(HEADER):
        raise ValueError("not an IPS patch: missing PATCH header")
    out = bytearray(original)
    i = len(HEADER)
    while True:
        if patch[i:i + 3] == FOOTER:
            break
        offset = int.from_bytes(patch[i:i + 3], "big")
        i += 3
        length = int.from_bytes(patch[i:i + 2], "big")
        i += 2
        if length == 0:                       # RLE record
            run = int.from_bytes(patch[i:i + 2], "big")
            i += 2
            value = patch[i]
            i += 1
            payload = bytes([value]) * run
        else:
            payload = patch[i:i + length]
            i += length
        if offset + len(payload) > len(out):
            out.extend(b"\x00" * (offset + len(payload) - len(out)))
        out[offset:offset + len(payload)] = payload
    return bytes(out)


def verify(original: bytes, patch: bytes, expected: bytes) -> bool:
    """Applying the patch must produce exactly the build you tested."""
    return hashlib.sha1(apply_ips(original, patch)).digest() == hashlib.sha1(expected).digest()


# -- internals ---------------------------------------------------------
def _differences(original: bytes, modified: bytes):
    """Spans where the files differ, including anything appended."""
    shared = min(len(original), len(modified))
    start = None
    for i in range(shared):
        if original[i] != modified[i]:
            if start is None:
                start = i
        elif start is not None:
            yield start, i
            start = None
    if start is not None:
        yield start, shared
    if len(modified) > len(original):
        yield len(original), len(modified)


def _splittable(start: int, end: int):
    """Split spans so no record exceeds the format's limits or starts at the EOF offset.

    A record whose three-byte offset happens to be 0x454F46 is byte-identical to
    the footer, and every patcher stops reading there. It is the format's one
    genuine defect. The fix is to begin the record one byte earlier and include
    a byte that is not changing — harmless, and it moves the offset.
    """
    if start == EOF_OFFSET and start > 0:
        start -= 1
    while start < end:
        stop = min(end, start + MAX_CHUNK)
        yield start, stop
        start = stop
        if start == EOF_OFFSET and start < end:
            start -= 1


def _record(data: bytes, start: int, end: int) -> bytes:
    payload = data[start:end]
    run_value = payload[0]
    if len(payload) >= RLE_WORTH_IT and payload.count(run_value) == len(payload):
        return (start.to_bytes(3, "big") + (0).to_bytes(2, "big")
                + len(payload).to_bytes(2, "big") + bytes([run_value]))
    return start.to_bytes(3, "big") + len(payload).to_bytes(2, "big") + payload
