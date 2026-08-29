"""iNES container: parsing, consistency, and expansion that keeps the ROM bootable."""
from __future__ import annotations

import dataclasses

MAGIC = b"NES\x1a"
HEADER_SIZE = 16
TRAINER_SIZE = 512
PRG_BANK = 16 * 1024
CHR_BANK = 8 * 1024


@dataclasses.dataclass(frozen=True)
class INesHeader:
    prg_banks: int
    chr_banks: int
    flags6: int
    flags7: int

    @property
    def prg_size(self) -> int:
        return self.prg_banks * PRG_BANK

    @property
    def chr_size(self) -> int:
        return self.chr_banks * CHR_BANK

    @property
    def mapper(self) -> int:
        return (self.flags6 >> 4) | (self.flags7 & 0xF0)

    @property
    def has_trainer(self) -> bool:
        return bool(self.flags6 & 0x04)


def parse_header(data: bytes) -> INesHeader:
    if len(data) < HEADER_SIZE or data[:4] != MAGIC:
        raise ValueError("not an iNES image: magic 'NES\\x1a' missing")
    return INesHeader(prg_banks=data[4], chr_banks=data[5], flags6=data[6], flags7=data[7])


def prg_slice(data: bytes) -> tuple[int, int]:
    h = parse_header(data)
    start = HEADER_SIZE + (TRAINER_SIZE if h.has_trainer else 0)
    return start, start + h.prg_size


def is_consistent(data: bytes) -> bool:
    h = parse_header(data)
    start, end = prg_slice(data)
    return len(data) == end + h.chr_size


def expand_prg(data: bytes, add_banks: int, fill: int = 0xFF) -> bytes:
    """Insert `add_banks` empty 16KB banks *before* the last one.

    The last PRG bank carries the reset and interrupt vectors and, on common
    mappers, is the one hardwired at $C000. Appending at the end would move it
    and the ROM would stop booting.
    """
    if add_banks < 1:
        raise ValueError("add_banks must be >= 1")
    h = parse_header(data)
    if h.prg_banks + add_banks > 255:
        raise ValueError("iNES header cannot describe more than 255 PRG banks")
    start, end = prg_slice(data)
    prg, tail = data[start:end], data[end:]
    body, last = prg[:-PRG_BANK], prg[-PRG_BANK:]
    header = bytearray(data[:start])
    header[4] = h.prg_banks + add_banks
    return bytes(header) + body + bytes([fill]) * PRG_BANK * add_banks + last + tail
