"""DTE and MTE: buying space by spending table slots.

One byte that stands for several characters is the cheapest compression there
is. The dictionary that suits English is not the one that suits Italian, so a
translation that keeps the original dictionary throws away most of the saving.
"""
from __future__ import annotations

import collections


def savings(text: str, pairs: list[str]) -> int:
    """Bytes saved by encoding `pairs` as single bytes.

    Pairs are consumed in order and the text already spent is not counted
    twice, so overlapping candidates do not inflate the total.
    """
    total = 0
    remaining = text
    for pair in pairs:
        if len(pair) < 2:
            continue
        count = remaining.count(pair)
        if count:
            total += count * (len(pair) - 1)
            remaining = remaining.replace(pair, "\x00")
    return total


def find_candidates(text: str, top: int = 32, length: int = 2) -> list[tuple[str, int]]:
    """The most frequent substrings of a given length, most frequent first."""
    counter = collections.Counter(
        text[i:i + length] for i in range(len(text) - length + 1)
    )
    return counter.most_common(top)


def best_pairs(texts: list[str], slots: int, max_length: int = 6) -> list[str]:
    """Greedily fill `slots` with the substrings that save the most.

    Greedy rather than optimal on purpose: the optimal dictionary is a hard
    problem, the greedy one is within a few percent, and the difference is
    smaller than the uncertainty about how much text the translation will add.
    """
    if slots < 1:
        return []
    corpus = "\n".join(texts)
    chosen: list[str] = []
    for _ in range(slots):
        best, best_gain = None, 0
        for length in range(2, max_length + 1):
            for candidate, count in find_candidates(corpus, top=64, length=length):
                if candidate in chosen or "\n" in candidate:
                    continue
                gain = count * (len(candidate) - 1)
                if gain > best_gain:
                    best, best_gain = candidate, gain
        if best is None or best_gain <= 0:
            break
        chosen.append(best)
        corpus = corpus.replace(best, "\x00")
    return chosen
