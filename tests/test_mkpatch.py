import pytest

import mkpatch


def test_an_ips_patch_starts_with_PATCH_and_ends_with_EOF():
    patch = mkpatch.make_ips(b"AAAA", b"ABAA")
    assert patch.startswith(b"PATCH")
    assert patch.endswith(b"EOF")


def test_applying_a_patch_reproduces_the_target():
    original = bytes(range(256)) * 4
    modified = bytearray(original)
    modified[100:110] = b"translated"
    modified[900] = 0xFF
    patch = mkpatch.make_ips(original, bytes(modified))
    assert mkpatch.apply_ips(original, patch) == bytes(modified)


def test_an_unchanged_file_produces_an_empty_patch():
    data = b"unchanged" * 100
    patch = mkpatch.make_ips(data, data)
    assert patch == b"PATCHEOF"
    assert mkpatch.apply_ips(data, patch) == data


def test_a_run_is_encoded_as_rle():
    original = b"\x00" * 4096
    modified = b"\x00" * 100 + b"\xFF" * 3000 + b"\x00" * 996
    patch = mkpatch.make_ips(original, modified)
    assert len(patch) < 200, "a long run must use RLE, not 3000 literal bytes"
    assert mkpatch.apply_ips(original, patch) == modified


def test_a_file_too_large_for_the_format_is_refused():
    """IPS offsets are 3 bytes: 16 MB, not 2 GB as some sources claim."""
    with pytest.raises(ValueError) as excinfo:
        mkpatch.make_ips(b"\x00" * 8, b"\x01" * 8, target_size=0x1000000 + 1)
    assert "16" in str(excinfo.value) or "0xFFFFFF" in str(excinfo.value)


def test_growing_the_file_is_recorded():
    original = b"A" * 64
    modified = original + b"B" * 32
    patch = mkpatch.make_ips(original, modified)
    assert mkpatch.apply_ips(original, patch) == modified


def test_the_EOF_offset_quirk_is_handled():
    """A change at offset 0x454F46 collides with the EOF marker.

    It is the format's known defect: the record must start elsewhere, or the
    patcher stops reading there.
    """
    size = 0x454F46 + 16
    original = bytearray(b"\x00" * size)
    modified = bytearray(original)
    modified[0x454F46] = 0x42
    patch = mkpatch.make_ips(bytes(original), bytes(modified))
    assert mkpatch.apply_ips(bytes(original), patch) == bytes(modified)


def test_verify_compares_against_the_expected_hash():
    original = b"before" * 50
    modified = b"after!" * 50
    patch = mkpatch.make_ips(original, modified)
    assert mkpatch.verify(original, patch, modified)
    assert not mkpatch.verify(original, patch, modified + b"x")
