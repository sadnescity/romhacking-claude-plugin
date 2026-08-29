import dump
import insert
import tbl

TABLE = tbl.Table.parse("41=A\n42=B\n43=C\n20= \n/00=[END]\n$01=[LINE]\n")
RAW = bytes([0x41, 0x42, 0x00, 0x43, 0x01, 0x41, 0x00])


def test_dump_splits_on_the_end_token():
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW))
    assert [e.text for e in entries] == ["AB<END>", "C<LINE>A<END>"]
    assert [e.offset for e in entries] == [0, 3]


def test_the_game_line_break_becomes_a_real_line_break():
    """The line that makes a script readable: it shows the shape the text has on screen."""
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    assert entries[1].text == "C\nA<END>"


def test_the_script_file_carries_a_header_that_explains_itself():
    import pathlib
    import tempfile
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "script.txt"
        dump.write_script(entries, path, source="GAME.BIN", title="dialogue")
        head = path.read_text(encoding="utf-8").splitlines()[:4]
    assert head[0] == "# GAME.BIN — dialogue, 2 strings"
    assert "markers alone" in head[1]
    assert "line break" in head[2]
    assert "<CODES>" in head[3]


def test_the_script_survives_a_roundtrip(tmp_path):
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    path = tmp_path / "script.txt"
    dump.write_script(entries, path)
    assert [e.text for e in dump.read_script(path)] == [e.text for e in entries]


def test_reinserting_an_untouched_dump_reproduces_the_original():
    """The phase 2 gate, in miniature."""
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    rebuilt, overflow = insert.insert_block(RAW, TABLE, entries, 0, len(RAW),
                                            newline_token="[LINE]")
    assert rebuilt == RAW
    assert overflow == []


def test_overflow_is_reported_not_truncated():
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW))
    entries[0] = dump.Entry(index=0, offset=0, text="ABABABABABAB<END>")
    rebuilt, overflow = insert.insert_block(RAW, TABLE, entries, 0, len(RAW))
    assert overflow, "text that is too long must be reported"
    assert "0" in overflow[0]
    assert len(rebuilt) == len(RAW), "the file does not change size here: the overflow is reported"


def test_trailing_bytes_after_the_last_terminator_are_kept():
    raw = RAW + b"\x42"
    entries = dump.dump_block(raw, TABLE, 0, len(raw))
    rebuilt, overflow = insert.insert_block(raw, TABLE, entries, 0, len(raw))
    assert rebuilt == raw


def test_measure_tells_you_the_cost_before_you_touch_the_rom():
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    sizes = insert.measure(TABLE, entries, newline_token="[LINE]")
    assert sizes == {0: 3, 1: 4}


def test_tsv_form_for_short_lists(tmp_path):
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW))
    path = tmp_path / "items.tsv"
    dump.write_tsv(entries, path, says={0: "opening greeting"})
    rows = path.read_text(encoding="utf-8").splitlines()
    assert rows[0] == "id\tbytes\ttext\tsays"
    assert rows[1].endswith("opening greeting")


def test_po_form_for_cat_tools(tmp_path):
    entries = dump.dump_block(RAW, TABLE, 0, len(RAW), newline_token="[LINE]")
    path = tmp_path / "script.po"
    dump.write_po(entries, path, source="GAME.BIN")
    body = path.read_text(encoding="utf-8")
    assert 'msgid "AB<END>"' in body
    assert "\\n" in body, "the PO file must escape line breaks"
