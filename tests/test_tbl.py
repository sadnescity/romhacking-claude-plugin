"""One test per directive defined by Nightcrawler's TBL specification."""
import pytest

import tbl

SIMPLE = """\
41=A
42=B
43=C
20= 
/00=[END]
$01=[LINE]
"""

WITH_DTE = SIMPLE + """\
80=th
81=the 
82=ou
"""


# --- normal entries ------------------------------------------------
def test_parses_simple_entries():
    t = tbl.Table.parse(SIMPLE)
    assert t.decode(bytes([0x41, 0x42, 0x43])) == "ABC"


def test_encode_is_the_inverse_of_decode():
    t = tbl.Table.parse(SIMPLE)
    assert t.encode("ABC") == bytes([0x41, 0x42, 0x43])


def test_a_normal_entry_cannot_contain_brackets():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("41=[A]\n")


def test_hex_sequences_must_have_an_even_length():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("4=A\n")


def test_duplicate_hex_sequences_are_an_error():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("41=A\n41=B\n")


# --- end tokens and control codes ---------------------------------
def test_end_and_control_entries_become_labels():
    t = tbl.Table.parse(SIMPLE)
    assert t.decode(bytes([0x41, 0x01, 0x42, 0x00])) == "A[LINE]B[END]"
    assert t.encode("A[LINE]B[END]") == bytes([0x41, 0x01, 0x42, 0x00])


def test_an_end_token_takes_no_parameters():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("/00=[END],p1\n")


def test_a_non_normal_entry_needs_a_label():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("$01=LINE\n")


def test_a_control_code_consumes_one_byte_per_parameter():
    t = tbl.Table.parse("41=A\n$E0=[Color],palette=$%X,index=%D\n")
    assert t.decode(bytes([0xE0, 0x0A, 0x05, 0x41])) == "[Color:0A,05]A"


def test_control_code_parameters_survive_the_roundtrip():
    t = tbl.Table.parse("41=A\n$E0=[Color],palette=$%X,index=%D\n")
    raw = bytes([0xE0, 0x0A, 0x05, 0x41])
    assert t.encode(t.decode(raw)) == raw


def test_wrong_parameter_count_is_an_error():
    t = tbl.Table.parse("41=A\n$E0=[Color],palette=$%X,index=%D\n")
    with pytest.raises(tbl.TableError):
        t.encode("[Color:0A]")


def test_truncated_parameters_are_an_error():
    t = tbl.Table.parse("41=A\n$E0=[Color],palette=$%X,index=%D\n")
    with pytest.raises(tbl.TableError):
        t.decode(bytes([0xE0, 0x0A]))


def test_a_newline_in_a_label_is_dump_formatting_only():
    t = tbl.Table.parse("41=A\n/00=[END]\\n\\n\n")
    assert t.decode(bytes([0x41, 0x00])) == "A[END]"
    assert t.encode("A[END]") == bytes([0x41, 0x00])


# --- DTE / MTE ------------------------------------------------------
def test_dte_decodes_multi_character_entries():
    t = tbl.Table.parse(WITH_DTE)
    assert t.decode(bytes([0x80, 0x41])) == "thA"


def test_encode_prefers_the_longest_match():
    """Without this, DTE does not save a single byte."""
    t = tbl.Table.parse(WITH_DTE)
    assert t.encode("the A") == bytes([0x81, 0x41])


def test_roundtrip_holds_for_every_mapped_byte():
    t = tbl.Table.parse(WITH_DTE)
    for raw, text in t.entries.items():
        assert t.decode(raw) == text
        assert t.encode(text) == raw


# --- collisions -----------------------------------------------------
def test_a_text_collision_resolves_to_the_shortest_hex():
    t = tbl.Table.parse("41=A\n8000=A\n")
    assert t.encode("A") == bytes([0x41])


def test_on_equal_length_the_last_occurrence_wins():
    t = tbl.Table.parse("41=A\n42=A\n")
    assert t.encode("A") == bytes([0x42])


# --- raw hex --------------------------------------------------------
def test_an_unmapped_byte_is_an_error_in_strict_mode():
    t = tbl.Table.parse(SIMPLE)
    with pytest.raises(tbl.TableError) as excinfo:
        t.decode(bytes([0x41, 0xFE]))
    assert "FE" in str(excinfo.value)


def test_an_unmapped_byte_becomes_raw_hex_when_not_strict():
    t = tbl.Table.parse(SIMPLE)
    assert t.decode(bytes([0x41, 0xFE]), strict=False) == "A[$FE]"


def test_raw_hex_roundtrips():
    t = tbl.Table.parse(SIMPLE)
    raw = bytes([0x41, 0xFE, 0x42])
    assert t.encode(t.decode(raw, strict=False)) == raw


def test_unknown_token_is_an_error():
    t = tbl.Table.parse(SIMPLE)
    with pytest.raises(tbl.TableError):
        t.encode("A[nope]")


# --- table id and switching ---------------------------------------
def test_a_table_declares_its_id():
    t = tbl.Table.parse("@KATA\n41=A\n")
    assert t.table_id == "KATA"


def test_switch_entries_parse_but_decoding_them_is_refused():
    t = tbl.Table.parse("@MAIN\n41=A\n!F8=[KATA],0\n")
    assert t.decode(b"\x41") == "A"
    with pytest.raises(tbl.TableError) as excinfo:
        t.decode(bytes([0xF8]))
    assert "switching" in str(excinfo.value)


# --- file format ---------------------------------------------------
def test_comments_and_blank_lines_are_ignored():
    t = tbl.Table.parse("# comment\n\n41=A\n")
    assert t.decode(b"\x41") == "A"


def test_a_bom_is_accepted():
    t = tbl.Table.parse("﻿41=A\n")
    assert t.decode(b"\x41") == "A"


def test_an_empty_table_is_an_error():
    with pytest.raises(tbl.TableError):
        tbl.Table.parse("# comments only\n")
