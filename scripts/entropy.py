"""Where the data stops looking like data.

Entropy does not tell you that a region is compressed. It tells you that it does
not look like the regions around it, which is where you start looking.
"""
from __future__ import annotations

import collections
import dataclasses
import math

# The Nintendo BIOS family, used across GB, GBA and DS and copied widely
# elsewhere: one type byte, then the decompressed size as 24-bit little-endian.
BIOS_TYPES = {
    0x10: "LZ77 (Nintendo BIOS)",
    0x11: "LZ11 (Nintendo BIOS)",
    0x20: "Huffman 4-bit (Nintendo BIOS)",
    0x28: "Huffman 8-bit (Nintendo BIOS)",
    0x30: "RLE (Nintendo BIOS)",
    0x40: "Diff filter (Nintendo BIOS)",
}
MAX_PLAUSIBLE_SIZE = 4 * 1024 * 1024


@dataclasses.dataclass(frozen=True)
class Signature:
    name: str
    decompressed_size: int
    header_len: int = 4


MIN_WINDOW = 512


def shannon(data: bytes) -> float:
    """Bits of entropy per byte. 0 is uniform, 8 is indistinguishable from noise.

    Bounded by log2(len(data)): with 64 bytes you cannot exceed 6 bits no matter
    how random the source. Measuring short regions therefore makes compressed
    data look uncompressed — see `suspects`, which refuses small windows.
    """
    if not data:
        return 0.0
    counts = collections.Counter(data)
    total = len(data)
    return abs(-sum((n / total) * math.log2(n / total) for n in counts.values()))


def profile(data: bytes, window: int = 512) -> list[tuple[int, float]]:
    """Entropy of each window, so you can see the shape of the file."""
    return [(i, shannon(data[i:i + window])) for i in range(0, len(data), window)]


def suspects(data: bytes, window: int = 512, threshold: float = 6.5,
             min_windows: int = 2) -> list[tuple[int, int, float]]:
    """Runs of windows above `threshold`: candidates, never conclusions.

    Compressed data is high entropy, but so is audio, so are some graphics, and
    so is anything encrypted. A hit here means "look at this", not "this is
    compressed".
    """
    if window < MIN_WINDOW:
        raise ValueError(
            f"window {window} is too small to measure: entropy is bounded by "
            f"log2(window) = {math.log2(window):.1f} bits, so compressed data "
            f"would score low. Use at least {MIN_WINDOW}."
        )
    runs: list[tuple[int, int, float]] = []
    start = None
    scores: list[float] = []
    for offset, score in profile(data, window):
        if score >= threshold:
            if start is None:
                start = offset
            scores.append(score)
        elif start is not None:
            if len(scores) >= min_windows:
                runs.append((start, offset, sum(scores) / len(scores)))
            start, scores = None, []
    if start is not None and len(scores) >= min_windows:
        runs.append((start, len(data), sum(scores) / len(scores)))
    return runs


def signature(data: bytes) -> Signature | None:
    """Recognise a known compression header.

    Checks the declared size for plausibility: a lone `$10` byte means nothing,
    and treating every one as a compressed block wastes a day.
    """
    if len(data) < 4:
        return None
    name = BIOS_TYPES.get(data[0])
    if name is None:
        return None
    size = int.from_bytes(data[1:4], "little")
    if size == 0 or size > MAX_PLAUSIBLE_SIZE or size < len(data) // 4:
        return None
    return Signature(name=name, decompressed_size=size)


def ratio_hint(compressed_len: int, decompressed_len: int) -> str:
    """What a ratio suggests. Sanity, not certainty."""
    if decompressed_len <= 0:
        return "unknown"
    ratio = compressed_len / decompressed_len
    if ratio > 0.95:
        return "barely smaller: probably not compressed, or stored uncompressed"
    if ratio > 0.6:
        return "modest: RLE, or a dictionary scheme on varied data"
    if ratio > 0.3:
        return "typical of LZ on text or tiles"
    return "aggressive: entropy coding, or highly repetitive source"
