import pytest

import romhack_state as st


def _state(tmp_path):
    rom = tmp_path / "game.nes"
    rom.write_bytes(b"NES\x1a" + bytes(12))
    return st.State.new(rom, platform="nes")


def test_new_state_starts_at_recon(tmp_path):
    rom = tmp_path / "game.nes"
    rom.write_bytes(b"NES\x1a" + bytes(12))
    state = st.State.new(rom, platform="nes")
    assert state.phase == "recon"
    assert state.data["target"]["sha1"]
    assert state.data["gates"] == {}


def test_a_gate_needs_evidence(tmp_path):
    state = _state(tmp_path)
    with pytest.raises(st.GateError):
        state.pass_gate("recon", evidence="")
    assert not state.gate_passed("recon")


def test_a_passed_gate_records_when_and_why(tmp_path):
    state = _state(tmp_path)
    state.pass_gate("recon", evidence="inventory: 100% classified", when="2026-08-30")
    assert state.gate_passed("recon")
    assert state.data["gates"]["recon"]["evidence"].startswith("inventory")
    assert state.data["gates"]["recon"]["passed"] == "2026-08-30"


def test_survives_a_save_and_load_cycle(tmp_path):
    path = tmp_path / "ROMHACK.md"
    state = _state(tmp_path)
    state.pass_gate("recon", evidence="ok", when="2026-08-30")
    state.notes = "The block at 0x8000 looks compressed.\n"
    state.save(path)

    reloaded = st.State.load(path)
    assert reloaded.gate_passed("recon")
    assert "0x8000" in reloaded.notes
    assert reloaded.data["target"]["platform"] == "nes"


def test_the_file_is_readable_markdown(tmp_path):
    path = tmp_path / "ROMHACK.md"
    _state(tmp_path).save(path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "## Working notes" in text


def test_the_full_schema_roundtrips(tmp_path):
    """The full ROMHACK.md schema, saved and loaded back unchanged."""
    path = tmp_path / "ROMHACK.md"
    state = _state(tmp_path)
    state.data["table"] = {
        "file": "game.tbl",
        "entries": 218,
        "roundtrip": {"status": "fail", "sample": "0x8A2C-0x8B40", "last_run": "2026-08-30"},
    }
    state.data["control_codes"] = {"mapped": 11, "unknown": 3}
    state.data["pointers"] = {
        "tables": [{"offset": 107520, "count": 512, "width": 2, "endian": "little", "base": 32768}]
    }
    state.data["blocks"] = [
        {"name": "dialogue", "offset": 35372, "end": 35648, "dumped": True, "reinserted": False}
    ]
    before = state.data
    state.save(path)

    assert st.State.load(path).data == before


def test_notes_under_any_heading_are_read_back(tmp_path):
    path = tmp_path / "ROMHACK.md"
    _state(tmp_path).save(path)
    text = path.read_text(encoding="utf-8").replace(st.NOTES_HEADING, "## Notes")
    path.write_text(text + "Pointer table at 0x8012.\n", encoding="utf-8")
    assert st.State.load(path).notes == "Pointer table at 0x8012.\n"


def test_an_unknown_phase_is_refused(tmp_path):
    state = _state(tmp_path)
    with pytest.raises(ValueError):
        state.phase = "free-translation"
