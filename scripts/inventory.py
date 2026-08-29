"""What is in this file, and how much of it we cannot explain yet.

The inventory is the first artifact of a project. Its value is not the part it
identifies but the part it does not: a stated `unknown` share is something you
can plan against, "mostly understood" is not.
"""
from __future__ import annotations

import collections
import dataclasses

import ines


@dataclasses.dataclass(frozen=True)
class Region:
    start: int
    end: int
    kind: str
    note: str = ""

    @property
    def size(self) -> int:
        return self.end - self.start

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Region(0x{self.start:X}-0x{self.end:X}, {self.kind})"


def classify(data: bytes, platform: str) -> list[Region]:
    """Split the file into regions. Every byte belongs to exactly one."""
    if platform != "nes":
        raise NotImplementedError(
            f"no inventory rules for platform {platform!r}. Write them: the "
            "`tooling` skill explains how, and refusing beats guessing."
        )
    header = ines.parse_header(data)
    prg_start, prg_end = ines.prg_slice(data)
    regions = [Region(0, ines.HEADER_SIZE, "header", f"iNES, mapper {header.mapper}")]
    if header.has_trainer:
        regions.append(Region(ines.HEADER_SIZE, prg_start, "trainer"))
    regions.append(Region(prg_start, prg_end, "code", f"PRG, {header.prg_banks} banks"))
    chr_end = prg_end + header.chr_size
    if header.chr_size:
        regions.append(Region(prg_end, chr_end, "graphics", f"CHR, {header.chr_banks} banks"))
    if chr_end < len(data):
        regions.append(Region(chr_end, len(data), "unknown", "trailing data"))
    return regions


def mark(regions: list[Region], start: int, end: int, kind: str, note: str = "") -> list[Region]:
    """Carve a known span out of whatever regions it overlaps.

    Used as the project learns: a block of text found inside PRG stops being
    generic `code` and becomes `text`, without ever losing a byte.
    """
    if end <= start:
        raise ValueError("end must be greater than start")
    out: list[Region] = []
    for region in regions:
        if region.end <= start or region.start >= end:
            out.append(region)
            continue
        if region.start < start:
            out.append(Region(region.start, start, region.kind, region.note))
        if region.end > end:
            out.append(Region(end, region.end, region.kind, region.note))
    out.append(Region(start, end, kind, note))
    return sorted(out, key=lambda r: r.start)


def coverage(regions: list[Region], total: int) -> dict[str, float]:
    """Share of the file per kind. Sums to 1: nothing is silently dropped."""
    by_kind: dict[str, int] = collections.defaultdict(int)
    for region in regions:
        by_kind[region.kind] += region.size
    accounted = sum(by_kind.values())
    if accounted < total:
        by_kind["unknown"] += total - accounted
    return {kind: size / total for kind, size in sorted(by_kind.items())}


def report(regions: list[Region], total: int) -> str:
    lines = [f"{'region':<10} {'range':<20} {'size':>10}  note"]
    for region in sorted(regions, key=lambda r: r.start):
        span = f"0x{region.start:06X}-0x{region.end:06X}"
        lines.append(f"{region.kind:<10} {span:<20} {region.size:>10}  {region.note}")
    lines.append("")
    for kind, share in sorted(coverage(regions, total).items(), key=lambda kv: -kv[1]):
        lines.append(f"{kind:<10} {share * 100:5.1f}%")
    return "\n".join(lines)
