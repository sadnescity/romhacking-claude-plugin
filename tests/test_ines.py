import pytest

import ines


def test_rejects_non_ines():
    with pytest.raises(ValueError):
        ines.parse_header(b"NOPE" + bytes(12))


def test_expansion_keeps_the_last_bank_last_on_a_synthetic_rom(synthetic_rom):
    rom = synthetic_rom
    last = rom[ines.prg_slice(rom)[1] - ines.PRG_BANK:ines.prg_slice(rom)[1]]
    expanded = ines.expand_prg(rom, add_banks=2)
    assert ines.is_consistent(expanded)
    assert ines.parse_header(expanded).prg_size == 4 * ines.PRG_BANK
    end = ines.prg_slice(expanded)[1]
    assert expanded[end - ines.PRG_BANK:end] == last


# Optional integration: a real iNES ROM through ROMHACK_TEST_ROM.

def test_a_real_header_is_consistent(ines_rom):
    h = ines.parse_header(ines_rom)
    assert h.prg_size > 0 and h.prg_size % ines.PRG_BANK == 0
    assert ines.is_consistent(ines_rom)


def test_expansion_keeps_the_last_bank_last(ines_rom):
    """On many mappers the last bank carries the vectors: it must stay last."""
    end0 = ines.prg_slice(ines_rom)[1]
    original_last_bank = ines_rom[end0 - ines.PRG_BANK:end0]
    before = ines.parse_header(ines_rom).prg_size

    expanded = ines.expand_prg(ines_rom, add_banks=4)

    assert ines.parse_header(expanded).prg_size == before + 4 * ines.PRG_BANK
    assert ines.is_consistent(expanded)
    end = ines.prg_slice(expanded)[1]
    assert expanded[end - ines.PRG_BANK:end] == original_last_bank


def test_expansion_preserves_chr(ines_rom):
    h0 = ines.parse_header(ines_rom)
    end0 = ines.prg_slice(ines_rom)[1]
    chr0 = ines_rom[end0:end0 + h0.chr_size]

    expanded = ines.expand_prg(ines_rom, add_banks=4)

    end1 = ines.prg_slice(expanded)[1]
    assert expanded[end1:end1 + h0.chr_size] == chr0


def test_expansion_adds_only_free_space(ines_rom):
    expanded = ines.expand_prg(ines_rom, add_banks=2, fill=0xFF)
    end = ines.prg_slice(expanded)[1]
    added = expanded[end - ines.PRG_BANK - 2 * ines.PRG_BANK:end - ines.PRG_BANK]
    assert added == b"\xFF" * (2 * ines.PRG_BANK)
