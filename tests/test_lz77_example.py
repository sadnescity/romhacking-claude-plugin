"""The example decompressor in the compressions skill must actually work.

A wrong example in a skill is worse than none: it gets copied.
"""
import re

from roles import ROOT


def _extract_example() -> str:
    text = (ROOT / "skills" / "compressions" / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"```python\n(def lz77.*?)```", text, re.S)
    assert match, "the lz77 example is no longer in the skill"
    return match.group(1)


def _lz77():
    namespace: dict = {}
    exec(_extract_example(), namespace)
    return namespace["lz77"]


def _compress_literal_only(payload: bytes) -> bytes:
    """The simplest valid stream: literals only."""
    out = bytearray([0x10]) + len(payload).to_bytes(3, "little")
    for i in range(0, len(payload), 8):
        chunk = payload[i:i + 8]
        out.append(0x00)
        out += chunk
    return bytes(out)


def test_the_example_decodes_a_literal_only_stream():
    lz77 = _lz77()
    payload = b"Welcome, traveller!"
    assert lz77(_compress_literal_only(payload)) == payload


def test_the_example_resolves_a_back_reference():
    """The flag byte describes the eight items that follow, MSB first.

    0x08 = 0000 1000: four literals, then a reference. Miscounting this is the
    first mistake anyone makes writing a stream by hand.
    """
    lz77 = _lz77()
    stream = bytes([0x10, 0x08, 0x00, 0x00])          # header, size 8
    stream += bytes([0x08]) + b"ABCD"                 # flag + four literals
    stream += bytes([0x10, 0x03])                     # length 4, offset 4
    assert lz77(stream) == b"ABCDABCD"


def test_an_overlapping_reference_repeats_a_run():
    """Offset 1 means 'repeat the last byte': a block copy would get it wrong."""
    lz77 = _lz77()
    stream = bytes([0x10, 0x06, 0x00, 0x00])          # header, size 6
    stream += bytes([0x40]) + b"A"                    # 0100 0000: literal, then reference
    stream += bytes([0x20, 0x00])                     # length 5, offset 1
    assert lz77(stream) == b"AAAAAA"


def test_the_declared_size_stops_the_loop():
    lz77 = _lz77()
    payload = b"12345"
    stream = _compress_literal_only(payload) + b"\xFF" * 32   # trailing bytes ignored
    assert lz77(stream) == payload
