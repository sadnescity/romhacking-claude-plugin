"""Optional integration: a real project's gates, checked against the data.

Needs ROMHACK_TEST_ROM (the untouched copy) and ROMHACK_TEST_PROJECT (the
directory holding ROMHACK.md and the tables). Without them every test is skipped.

The state file declares; these tests check again. A gate marked as passed that
does not hold here is a gate that did not pass.
"""
import hashlib

import pytest

import dump
import insert
import pointers
import romhack_state
import tbl


@pytest.fixture(scope="module")
def state(project_dir):
    return romhack_state.State.load(project_dir / "ROMHACK.md")


@pytest.fixture(scope="module")
def blocks(state):
    found = state.data.get("blocks", [])
    if not found:
        pytest.skip("no blocks recorded in ROMHACK.md")
    return found


def _table(project_dir, block):
    """Each block declares its own table: a game may have more than one."""
    return tbl.Table.load(project_dir / block["table"])


def test_the_rom_is_the_untouched_copy_the_project_declares(state, rom_bytes):
    declared = state.data.get("target", {}).get("sha1")
    if not declared:
        pytest.skip("ROMHACK.md does not declare the sha1 of the untouched copy")
    assert hashlib.sha1(rom_bytes).hexdigest() == declared, \
        "ROMHACK_TEST_ROM is not the copy the project was built on"


def test_every_passed_gate_carries_evidence(state):
    for name, gate in state.data.get("gates", {}).items():
        if gate.get("passed"):
            assert str(gate.get("evidence", "")).strip(), f"gate {name} passed without evidence"


def test_every_block_declares_how_it_is_addressed(project_dir, blocks):
    """Without this, the translator cannot know what may grow and what may not."""
    for block in blocks:
        assert block.get("addressing") in ("pointed", "sequential", "fixed"), \
            f"block {block['name']} does not declare how it is addressed"
        assert block.get("end_token"), f"block {block['name']} does not declare its terminator"
        assert block.get("table"), f"block {block['name']} does not declare its table"
        assert (project_dir / block["table"]).exists(), f"{block['table']} declared but missing"


def test_every_block_roundtrips(project_dir, blocks, rom_bytes):
    for block in blocks:
        table = _table(project_dir, block)
        raw = rom_bytes[block["offset"]:block["end"]]
        assert table.encode(table.decode(raw, strict=False)) == raw, \
            f"round-trip broken on block {block['name']}"


def test_coverage_is_high_enough_to_translate_against(project_dir, blocks, rom_bytes):
    """The round-trip passes trivially if everything is raw hex: coverage does not."""
    total = explained = 0
    for block in blocks:
        table = _table(project_dir, block)
        raw = rom_bytes[block["offset"]:block["end"]]
        text = table.decode(raw, strict=False)
        total += len(raw)
        explained += len(raw) - text.count("[$")
    assert explained / total > 0.95, f"coverage only {explained / total:.1%}"


def test_control_codes_are_mapped_or_counted(state):
    codes = state.data.get("control_codes")
    if codes is None:
        pytest.skip("control codes not recorded yet")
    assert codes.get("mapped", 0) > 0, "no control code mapped"
    assert "unknown" in codes, "unknown codes must be counted, not hidden"


def test_pointer_tables_read_back_and_rewrite_cleanly(state, rom_bytes):
    tables = state.data.get("pointers", {}).get("tables", [])
    if not tables:
        pytest.skip("no pointer table recorded")
    for spec in tables:
        table = pointers.PointerTable(**spec)
        values = pointers.read_pointers(rom_bytes, table)
        assert len(set(values)) == len(values), "colliding pointers: wrong width or base"
        moved = pointers.write_pointers(rom_bytes, table, [values[0] + 2] + values[1:])
        assert pointers.read_pointers(moved, table)[1:] == values[1:], "repointing touched other pointers"


def test_an_untouched_cycle_reproduces_the_rom(project_dir, blocks, rom_bytes):
    """The encoding gate: untouched dump and reinsertion, identical file."""
    rebuilt = bytes(rom_bytes)
    for block in blocks:
        table = _table(project_dir, block)
        newline = block.get("newline_token")
        entries = dump.dump_block(rom_bytes, table, block["offset"], block["end"],
                                  end_token=block["end_token"], newline_token=newline)
        rebuilt, overflow = insert.insert_block(rebuilt, table, entries,
                                                block["offset"], block["end"],
                                                newline_token=newline)
        assert not overflow, f"unexpected overflow on {block['name']}: {overflow[:2]}"
    assert rebuilt == rom_bytes


def test_no_original_glyph_was_sacrificed(state):
    """Accents are added: the project must not have removed glyphs."""
    accents = state.data.get("accents")
    if not accents:
        pytest.skip("accents phase not started yet")
    assert not accents.get("sacrificed"), f"sacrificed glyphs: {accents['sacrificed']}"


def test_the_accented_glyphs_are_reachable_from_the_tables(project_dir, state, blocks):
    glyphs = state.data.get("accents", {}).get("glyphs", {})
    if not glyphs:
        pytest.skip("no accented glyph recorded")
    rendered = set()
    for name in {b["table"] for b in blocks}:
        rendered |= set("".join(tbl.Table.load(project_dir / name).entries.values()))
    missing = [c for c in glyphs if c not in rendered]
    assert not missing, f"accented glyphs with no entry in any table: {missing}"
