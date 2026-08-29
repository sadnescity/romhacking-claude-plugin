import dte


def test_savings_counts_bytes_not_occurrences():
    assert dte.savings("the the the", ["the"]) == 6  # 3 occorrenze x 2 byte risparmiati


def test_best_pairs_fills_the_slots_with_the_most_profitable():
    texts = ["the sword", "the shield", "the sword of the king"]
    pairs = dte.best_pairs(texts, slots=2)
    assert len(pairs) == 2
    assert "the" in "".join(pairs)


def test_best_pairs_never_exceeds_the_slots():
    assert len(dte.best_pairs(["abcabcabc"], slots=1)) == 1


def test_a_dictionary_only_helps_if_it_saves():
    assert dte.savings("abc", ["zz"]) == 0


def test_candidates_come_back_ordered_by_frequency():
    found = dte.find_candidates("the cat and the hat and the bat", top=3, length=4)
    assert found[0][0] == "the "
    assert found[0][1] >= found[-1][1]

