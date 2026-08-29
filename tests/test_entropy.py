import math
import zlib

import entropy


def test_uniform_data_has_no_entropy():
    assert entropy.shannon(b"\x00" * 4096) == 0.0


def test_random_data_is_near_eight_bits():
    import random
    rng = random.Random(1)
    data = bytes(rng.randrange(256) for _ in range(8192))
    assert entropy.shannon(data) > 7.9


def test_english_text_sits_in_the_middle():
    text = (b"the quick brown fox jumps over the lazy dog " * 100)
    assert 3.0 < entropy.shannon(text) < 5.0


def test_compressed_data_scores_higher_than_its_source():
    """On data large enough to measure: see the test below."""
    import random
    rng = random.Random(7)
    words = [b"sword", b"shield", b"potion", b"castle", b"dragon", b"village"]
    text = b" ".join(rng.choice(words) for _ in range(20000))
    packed = zlib.compress(text, 9)
    assert len(packed) > 4096, "the sample must be large for the measurement to mean anything"
    assert entropy.shannon(packed) > entropy.shannon(text) + 2


def test_entropy_on_a_small_sample_is_bounded_by_its_size():
    """The limit that makes small windows useless.

    n bytes hold at most n distinct symbols, so entropy cannot exceed log2(n).
    A 64-byte window never goes above 6 bits even on perfectly random data, and
    a short compressed region looks uncompressed.
    """
    import random
    rng = random.Random(3)
    tiny = bytes(rng.randrange(256) for _ in range(64))
    assert entropy.shannon(tiny) <= math.log2(64)
    assert entropy.shannon(tiny) < 7.0, "not even pure noise reaches 8 bits on 64 bytes"


def test_the_profile_walks_the_file_in_windows():
    import random
    rng = random.Random(11)
    noisy = bytes(rng.randrange(256) for _ in range(4096))
    data = b"\x00" * 4096 + noisy
    windows = entropy.profile(data, window=1024)
    assert abs(windows[0][1]) < 1e-9
    assert max(e for _, e in windows) > 7


def test_suspects_are_the_high_entropy_runs():
    import random
    rng = random.Random(5)
    packed = bytes(rng.randrange(256) for _ in range(4096))
    data = b"A" * 4096 + packed + b"A" * 4096
    found = entropy.suspects(data, window=1024, threshold=6.5)
    assert found, "a high-entropy region must be reported"
    start, end, score = found[0]
    assert start == 4096 and end == 8192
    assert score > 7.0


def test_a_window_too_small_to_measure_is_refused():
    with __import__("pytest").raises(ValueError):
        entropy.suspects(b"\x00" * 4096, window=64)


def test_a_nintendo_lz77_header_is_recognised():
    # type $10, then the decompressed size as 24-bit little-endian
    blob = bytes([0x10, 0x00, 0x10, 0x00]) + b"\x00" * 64
    sig = entropy.signature(blob)
    assert sig is not None
    assert sig.name == "LZ77 (Nintendo BIOS)"
    assert sig.decompressed_size == 0x1000


def test_an_rle_header_is_recognised():
    blob = bytes([0x30, 0x40, 0x00, 0x00]) + b"\x00" * 32
    sig = entropy.signature(blob)
    assert sig.name.startswith("RLE")
    assert sig.decompressed_size == 0x40


def test_an_implausible_size_is_not_a_signature():
    """A stray $10 byte is not enough: the size must be plausible."""
    blob = bytes([0x10, 0xFF, 0xFF, 0xFF]) + b"\x00" * 16
    assert entropy.signature(blob) is None


def test_plain_text_has_no_signature():
    assert entropy.signature(b"Once upon a time in a kingdom far away") is None
