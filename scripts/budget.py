"""How much room a block has, and what to do when the translation needs more.

A dump that does not come with this is only half the work: the translator finds
out the text does not fit at the end, when every line is already written.
"""
from __future__ import annotations

import dataclasses

FIXED = "fixed"            # reached by hardcoded offsets: nothing may move
SEQUENTIAL = "sequential"  # reached by counting separators: entries may resize
POINTED = "pointed"        # a pointer table: entries may move, if repointed


@dataclasses.dataclass
class Plan:
    name: str
    start: int
    end: int
    used: int
    addressing: str
    pointer_table: object | None = None
    free_after: int = 0
    relocation: tuple[int, int] | None = None

    @property
    def capacity(self) -> int:
        return self.end - self.start

    @property
    def headroom(self) -> int:
        """Bytes the translation may grow by without moving anything."""
        return self.capacity - self.used + self.free_after

    def strategy(self) -> str:
        if self.addressing == FIXED:
            return ("nothing may move: every entry has to fit its original size, "
                    "or the code that addresses it must be patched")
        if self.addressing == SEQUENTIAL:
            return ("entries may take any size as long as the block total fits: "
                    "the game walks separators, so only the total matters")
        where = f" (table at 0x{self.pointer_table.offset:X})" if self.pointer_table else ""
        return (f"entries may move and grow: recompute the pointers{where} "
                "after any change")

    def for_translator(self) -> tuple[str, ...]:
        """The two or three lines a translator needs at the top of their file."""
        lines = [f"You have {self.headroom} bytes of headroom: "
                 f"the translation of this block must fit in {self.capacity + self.free_after} bytes."]
        lines.append(self.strategy().capitalize() + ".")
        if self.relocation and self.headroom <= 0:
            lines.append(f"There is no room left here, but {self.relocation[1]} bytes are free "
                         f"at 0x{self.relocation[0]:X}: this block can be relocated there.")
        return tuple(lines)

    def report(self) -> str:
        lines = [
            f"{self.name}: 0x{self.start:X}-0x{self.end:X}",
            f"  capacity   {self.capacity} bytes",
            f"  used       {self.used} bytes",
            f"  free after {self.free_after} bytes",
            f"  headroom   {self.headroom} bytes"
            + ("  ← the translation must not exceed this" if self.headroom >= 0 else "  ← ALREADY OVER"),
            f"  addressing {self.addressing}",
            f"  strategy   {self.strategy()}",
        ]
        if self.relocation:
            lines.append(f"  relocation available at 0x{self.relocation[0]:X} "
                         f"({self.relocation[1]} bytes)")
        elif self.headroom < self.capacity * 0.1:
            lines.append("  relocation NEEDED: less than 10% headroom and no free space after")
        return "\n".join(lines)


def free_run_after(data: bytes, end: int, fillers=(0xFF, 0x00)) -> int:
    i = end
    while i < len(data) and data[i] in fillers:
        i += 1
    return i - end


def largest_free_run(data: bytes, start: int, end: int, fillers=(0xFF, 0x00)) -> tuple[int, int]:
    """Biggest run of filler bytes in a region: the best relocation target."""
    best = (0, 0)
    run_start = None
    for i in range(start, end):
        if data[i] in fillers:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start > best[1]:
                best = (run_start, i - run_start)
            run_start = None
    if run_start is not None and end - run_start > best[1]:
        best = (run_start, end - run_start)
    return best


def plan(data: bytes, name: str, start: int, end: int, used: int,
         addressing: str, pointer_table=None, search: tuple[int, int] | None = None) -> Plan:
    relocation = None
    if search:
        found = largest_free_run(data, *search)
        if found[1] >= (end - start):
            relocation = found
    return Plan(name=name, start=start, end=end, used=used, addressing=addressing,
                pointer_table=pointer_table, free_after=free_run_after(data, end),
                relocation=relocation)
