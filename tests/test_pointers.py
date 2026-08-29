import pointers


def test_finds_a_table_of_little_endian_pointers():
    targets = [0x1234, 0x1240, 0x1250]
    blob = b"\x00" * 8 + b"".join(t.to_bytes(2, "little") for t in targets) + b"\xFF" * 8
    found = pointers.find_pointer_tables(blob, targets, width=2)
    assert found and found[0].offset == 8 and found[0].count == 3


def test_reads_back_what_it_found():
    targets = [0x1234, 0x1240, 0x1250]
    blob = b"\x00" * 4 + b"".join(t.to_bytes(2, "little") for t in targets)
    table = pointers.find_pointer_tables(blob, targets, width=2)[0]
    assert pointers.read_pointers(blob, table) == targets


def test_rewriting_a_pointer_moves_only_its_bytes():
    targets = [0x1234, 0x1240, 0x1250]
    blob = b"\x00" * 4 + b"".join(t.to_bytes(2, "little") for t in targets)
    table = pointers.find_pointer_tables(blob, targets, width=2)[0]
    updated = pointers.write_pointers(blob, table, [0x1234, 0x9999, 0x1250])
    assert len(updated) == len(blob)
    assert updated[:4] == blob[:4]
    assert pointers.read_pointers(updated, table) == [0x1234, 0x9999, 0x1250]


def test_a_base_offset_is_applied_in_both_directions():
    """A pointer holds the CPU address, not the file offset."""
    table = pointers.PointerTable(offset=0, count=1, width=2, endian="little", base=0x8000)
    blob = (0x8010).to_bytes(2, "little")
    assert pointers.read_pointers(blob, table) == [0x10]
    assert pointers.write_pointers(blob, table, [0x20]) == (0x8020).to_bytes(2, "little")


def test_a_lone_match_is_not_a_table():
    targets = [0x1234]
    blob = b"\x00" * 16 + (0x1234).to_bytes(2, "little") + b"\x00" * 16
    assert pointers.find_pointer_tables(blob, targets, width=2) == []
