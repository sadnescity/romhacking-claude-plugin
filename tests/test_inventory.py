import pytest

import inventory


@pytest.fixture(params=["synthetic", "real"])
def nes(request, synthetic_rom):
    """A synthetic image always; a real one when ROMHACK_TEST_ROM is iNES."""
    if request.param == "synthetic":
        return synthetic_rom
    return request.getfixturevalue("ines_rom")


def test_every_byte_is_accounted_for(nes):
    regions = inventory.classify(nes, platform="nes")
    covered = sum(r.end - r.start for r in regions)
    assert covered == len(nes), "the inventory must cover the whole file"


def test_regions_do_not_overlap(nes):
    regions = sorted(inventory.classify(nes, platform="nes"), key=lambda r: r.start)
    for a, b in zip(regions, regions[1:]):
        assert a.end <= b.start, f"sovrapposizione fra {a} e {b}"


def test_header_prg_and_chr_are_identified(nes):
    kinds = {r.kind for r in inventory.classify(nes, platform="nes")}
    assert {"header", "code"} <= kinds


def test_coverage_reports_the_unknown_share(nes):
    regions = inventory.classify(nes, platform="nes")
    share = inventory.coverage(regions, len(nes))
    assert abs(sum(share.values()) - 1.0) < 1e-9
    assert share.get("unknown", 0.0) < 1.0


def test_an_unsupported_platform_is_refused_not_guessed(synthetic_rom):
    with pytest.raises(NotImplementedError) as excinfo:
        inventory.classify(synthetic_rom, platform="dreamcast")
    assert "dreamcast" in str(excinfo.value)


def test_marking_a_block_narrows_the_inventory(nes):
    regions = inventory.classify(nes, platform="nes")
    refined = inventory.mark(regions, start=0x8000, end=0x8100, kind="text", note="dialogue")
    covered = sum(r.end - r.start for r in refined)
    assert covered == len(nes), "marking must not lose bytes"
    assert any(r.kind == "text" and r.start == 0x8000 and r.end == 0x8100 for r in refined)


def test_marking_twice_is_stable(nes):
    regions = inventory.classify(nes, platform="nes")
    once = inventory.mark(regions, 0x8000, 0x8100, "text")
    twice = inventory.mark(once, 0x8000, 0x8100, "text")
    assert sum(r.end - r.start for r in twice) == len(nes)
    assert len([r for r in twice if r.kind == "text"]) == 1
