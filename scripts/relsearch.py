"""Relative search: find an alphabet without knowing its encoding.

Whatever value 'A' has in a given game, the distance between consecutive
letters is preserved. Search for the distances, then read the base off the
match.

The *base* is always the byte that stands for the anchor letter 'A', never the
byte under the word's own first letter. Anchoring it makes bases from different
words comparable, which is the whole point of `consistent_bases`.

Search words must be single-case: in ASCII the run from 'A' to 'Z' is
contiguous and so is 'a' to 'z', but the gap between them is not, so a mixed
word has no single base.
"""
from __future__ import annotations

import collections
import dataclasses

import tbl

ASCII_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ANCHOR = "A"


@dataclasses.dataclass(frozen=True)
class Match:
    offset: int
    base: int
    word: str


def _deltas(word: str) -> list[int]:
    return [(ord(word[i + 1]) - ord(word[i])) & 0xFF for i in range(len(word) - 1)]


def relative_search(data: bytes, word: str, limit: int = 200) -> list[Match]:
    if len(word) < 3:
        raise ValueError("a word shorter than 3 letters matches almost anything")
    if not (word.isupper() or word.islower()):
        raise ValueError(
            f"{word!r} mixes cases: 'A'-'Z' and 'a'-'z' are contiguous runs but "
            "the gap between them is not, so the word has no single base"
        )
    anchor = ANCHOR if word.isupper() else ANCHOR.lower()
    deltas = _deltas(word)
    span = len(word)
    found: list[Match] = []
    for i in range(len(data) - span + 1):
        for j, delta in enumerate(deltas):
            if (data[i + j + 1] - data[i + j]) & 0xFF != delta:
                break
        else:
            base = (data[i] - ord(word[0]) + ord(anchor)) & 0xFF
            found.append(Match(offset=i, base=base, word=word))
            if len(found) >= limit:
                break
    return found


def consistent_bases(data: bytes, words: list[str], limit: int = 200) -> dict[int, list[Match]]:
    by_base: dict[int, list[Match]] = collections.defaultdict(list)
    for word in words:
        for match in relative_search(data, word, limit=limit):
            by_base[match.base].append(match)
    return dict(by_base)


def table_from_base(base: int, letters: str = ASCII_UPPER) -> "tbl.Table":
    entries = {bytes([(base + i) & 0xFF]): letter for i, letter in enumerate(letters)}
    return tbl.Table(entries)
