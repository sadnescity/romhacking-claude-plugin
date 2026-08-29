"""Pointer tables: find them, read them, rewrite them.

The value a pointer holds is the address the CPU sees after mapping, not the
offset in the file. `base` is the difference, and getting it wrong is the most
common way a repointing job fails: everything looks plausible and the game
shows the wrong line.
"""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class PointerTable:
    offset: int
    count: int
    width: int = 2
    endian: str = "little"
    base: int = 0

    @property
    def end(self) -> int:
        return self.offset + self.count * self.width


def _read(data: bytes, at: int, width: int, endian: str) -> int:
    return int.from_bytes(data[at:at + width], endian)


def read_pointers(data: bytes, table: PointerTable) -> list[int]:
    """Pointer values converted to offsets in `data`."""
    return [
        _read(data, table.offset + i * table.width, table.width, table.endian) - table.base
        for i in range(table.count)
    ]


def write_pointers(data: bytes, table: PointerTable, values: list[int]) -> bytes:
    if len(values) != table.count:
        raise ValueError(f"table holds {table.count} pointers, got {len(values)}")
    out = bytearray(data)
    for i, value in enumerate(values):
        raw = (value + table.base).to_bytes(table.width, table.endian)
        at = table.offset + i * table.width
        out[at:at + table.width] = raw
    return bytes(out)


def find_pointer_tables(
    data: bytes,
    targets: list[int],
    width: int = 2,
    endian: str = "little",
    base: int = 0,
    min_run: int = 3,
) -> list[PointerTable]:
    """Find runs of consecutive pointers aiming at `targets`.

    A single value matching is noise — with two bytes it happens by chance every
    few kilobytes. A run of consecutive slots all pointing into the set is a
    table.
    """
    wanted = {(t + base) for t in targets}
    encoded = {value.to_bytes(width, endian) for value in wanted if 0 <= value < 256 ** width}
    found: list[PointerTable] = []
    i = 0
    limit = len(data) - width
    while i <= limit:
        if data[i:i + width] not in encoded:
            i += 1
            continue
        run = 0
        j = i
        while j <= limit and data[j:j + width] in encoded:
            run += 1
            j += width
        if run >= min_run:
            found.append(PointerTable(offset=i, count=run, width=width, endian=endian, base=base))
        i = j if run else i + 1
    return found
