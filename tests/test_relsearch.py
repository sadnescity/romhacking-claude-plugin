import relsearch


def _synthetic(base: int, text: str) -> bytes:
    """A block where 'A' is `base`, surrounded by noise."""
    body = bytes((base + ord(c) - ord("A")) & 0xFF for c in text)
    return b"\x00\xFF\x7F" + body + b"\xFF\x00"


def test_finds_a_word_at_an_arbitrary_base():
    data = _synthetic(0x0A, "HELLO")
    matches = relsearch.relative_search(data, "HELLO")
    assert len(matches) == 1
    assert matches[0].offset == 3
    assert matches[0].base == 0x0A


def test_the_same_base_explains_several_words():
    data = _synthetic(0x30, "SWORD") + _synthetic(0x30, "SHIELD")
    bases = relsearch.consistent_bases(data, ["SWORD", "SHIELD"])
    assert 0x30 in bases
    assert {m.word for m in bases[0x30]} == {"SWORD", "SHIELD"}


def test_a_base_that_explains_more_words_ranks_higher():
    data = _synthetic(0x30, "SWORD") + _synthetic(0x30, "SHIELD") + _synthetic(0x77, "SWORD")
    bases = relsearch.consistent_bases(data, ["SWORD", "SHIELD"])
    best = max(bases, key=lambda b: len({m.word for m in bases[b]}))
    assert best == 0x30


def test_builds_a_usable_table_from_a_base():
    table = relsearch.table_from_base(0x0A, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    assert table.decode(bytes([0x0A, 0x0B])) == "AB"
    assert table.encode("AB") == bytes([0x0A, 0x0B])


def test_a_mixed_case_word_is_refused():
    """'A'-'Z' and 'a'-'z' are two contiguous runs separated by a gap."""
    import pytest
    with pytest.raises(ValueError):
        relsearch.relative_search(b"\x00" * 32, "Sword")

