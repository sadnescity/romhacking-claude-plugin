import budget


def test_headroom_counts_the_free_space_after_the_block():
    data = b"A" * 100 + b"\xFF" * 50
    p = budget.plan(data, "blk", 0, 100, used=90, addressing=budget.SEQUENTIAL)
    assert p.capacity == 100
    assert p.free_after == 50
    assert p.headroom == 60


def test_a_block_with_no_room_says_relocation_is_needed():
    data = b"A" * 100 + b"B" * 50
    p = budget.plan(data, "blk", 0, 100, used=99, addressing=budget.SEQUENTIAL)
    assert p.free_after == 0
    assert "relocation NEEDED" in p.report()


def test_fixed_addressing_forbids_moving_anything():
    data = b"A" * 100
    p = budget.plan(data, "blk", 0, 100, used=50, addressing=budget.FIXED)
    assert "nothing may move" in p.strategy()


def test_sequential_addressing_only_cares_about_the_total():
    data = b"A" * 100
    p = budget.plan(data, "blk", 0, 100, used=50, addressing=budget.SEQUENTIAL)
    assert "only the total matters" in p.strategy()


def test_pointed_addressing_asks_for_a_recompute():
    import pointers
    data = b"A" * 100
    table = pointers.PointerTable(offset=0x10, count=4)
    p = budget.plan(data, "blk", 0, 100, used=50, addressing=budget.POINTED,
                    pointer_table=table)
    assert "recompute the pointers" in p.strategy()
    assert "0x10" in p.strategy()


def test_relocation_is_offered_only_when_the_run_is_big_enough():
    data = b"A" * 100 + b"\x00" * 20 + b"B" * 10 + b"\xFF" * 300
    small = budget.plan(data, "blk", 0, 100, used=90, addressing=budget.SEQUENTIAL,
                        search=(100, 125))
    assert small.relocation is None
    big = budget.plan(data, "blk", 0, 100, used=90, addressing=budget.SEQUENTIAL,
                      search=(100, len(data)))
    assert big.relocation is not None and big.relocation[1] >= 100


def test_an_overfull_block_is_flagged():
    data = b"A" * 100
    p = budget.plan(data, "blk", 0, 100, used=120, addressing=budget.SEQUENTIAL)
    assert p.headroom < 0
    assert "ALREADY OVER" in p.report()
