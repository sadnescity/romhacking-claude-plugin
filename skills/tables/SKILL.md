---
name: tables
description: Builds and validates a .tbl table file, the contract between raw bytes and readable text. Covers the TBL format directives, multi-byte entries, control-code labels, and the round-trip that is the only proof a table is correct. Use when creating, extending, debugging or validating a table.
---

# Tables

## What this is

Inside a game there is no text, only numbers. The byte `$0A` might be `a`, or
`A`, or a space, or the tenth tile of a font — nothing in the file says which.
A **table** is the document that decides: a plain text file listing, one per
line, what each byte value means.

```
0A=a
0B=b
5F= 
```

That is the entire idea. Its importance is out of proportion to its complexity,
because every later step rests on it: the dump you hand a translator, the
reinsertion, the length calculations, the search for a phrase you saw on screen.
A wrong table produces text that reads perfectly and reinserts wrong.

Tables do three things beyond the obvious byte-to-letter mapping:

**Multi-byte entries.** `8000=the` says two bytes produce three characters. This
is how DTE lives in a table — see `dte-mte`.

**Control codes.** Some bytes are not characters at all: they end the string,
break the line, wait for a button. A table gives them names so a translator sees
`[END]` instead of a mystery. Some take parameters — a colour, a delay — and the
table records how many bytes each one eats, because miscounting shifts
everything after it.

**Several tables.** A game often encodes its menus differently from its
dialogue, and the same character sits at different values in each. One table per
context is normal, not a workaround.

The format is specified — the TBL format, written down by Nightcrawler with the
help of a good part of the English-speaking scene — and worth following even if
you write your own tools, because everyone else's tools read it.

### Read more

→ **[Table File Format (TBL)](https://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt)** (Nightcrawler, TransCorp) — the specification itself. Short, precise, and the authority on every directive: read it before writing a parser.

→ **[L'HexWorkshop e le table](https://romhacking.it/doc/view/id/44)** (SadNES cITy) — building a table by hand, which is still how you understand what a table is.

## Recognize

You need a table the moment you can locate text but not read it, and you need
to **extend** one every time a decode raises on a byte it has never seen. That
error is not a failure: it is the table telling you exactly what it is missing.

## Analyze

Directives, one line each:

| Syntax | Meaning |
|---|---|
| `HH=text` | normal entry; hex is even-length, big-endian; text cannot contain `[` or `]` |
| `HHHH=text` | multi-byte entry — this is how DTE and MTE live in a table |
| `$HH=[Label],p1,p2` | control code; **one raw byte consumed per parameter** |
| `/HH=[Label]` | end token; no parameters |
| `!HH=[ID],fallback` | table switching |
| `@ID` | table identifier |
| `[$HH]` | a byte with no entry, in dump output |
| `#` | comment |

Resolution rules that matter in practice: on the byte side the **longest match**
wins; on the text side the **shortest hex** wins, and on a tie the **last**
entry declared. Files are UTF-8, BOM optional.

```python
import tbl
table = tbl.Table.load("game.tbl")
table.decode(data[0x8050:0x8100], strict=False)   # [$HH] for unmapped bytes
table.encode(text)
```

`strict=True` while building — you want to be told about every unknown byte.
`strict=False` for a real dump, where unknown bytes become `[$HH]` and survive
the trip.

## Implement

Build it as a loop, not in one pass:

1. seed the alphabet from the base you found (`relsearch.table_from_base`)
2. decode a sample and read it
3. the first unmapped byte is your next question — decide what it is from
   context, add the entry
4. repeat until the round-trip passes

Give control codes **neutral labels** (`[C_FC]`) until you have seen them act —
see `control-codes`.

### One game, several tables

A charset is not necessarily global. Menus, dialogue and name lists are often
encoded by different code written at different times, and the same character can
sit at different values in each.

The symptom is a round-trip that fails on **one block only**, with a consistent
`0xNN → 0xMM` substitution. *Example:* an apostrophe stored as `0x53` in the
dialogue and `0x40` in the item names — one glyph, two byte values; with a
single table mapping both to `'`, encoding picks one and the other block comes
back wrong.

The fix is one table per context, which is what the format's `@ID` directive is
for. Keep them as separate files and record which block uses which — the state
file is the right place. Both tables can still render `'` as `'`, so the
translator sees an apostrophe either way and never learns this happened.

Expect this whenever a game has visibly separate text systems. It travels
together with several print routines and several terminators: they are all the
same underlying fact, that the game was not written as one uniform whole.

## Verify

**The round-trip is the only proof.**

```python
assert table.encode(table.decode(raw, strict=False)) == raw
```

A table that decodes into perfectly readable text and fails this is a wrong
table that looks right. *Example:* two bytes both mapped to `.` — the text reads
identically, and every occurrence of one comes back as the other. Only the
round-trip sees it.

When two bytes want the same character, one of them becomes a labelled token
until you know which glyph it really draws.

Track **coverage** alongside the round-trip: the share of bytes explained by
real entries rather than `[$HH]`. The round-trip passes trivially when
everything is raw hex — coverage is what says how much you actually understand.
99% coverage with a passing round-trip is a working table; 40% coverage with a
passing round-trip is a file you can copy but not read.

SOURCES: Table File Format (TBL) — Nightcrawler, TransCorp — https://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt · indexed at https://romhacking.it/doc/view/id/57 · L'HexWorkshop e le table — SadNES cITy — https://romhacking.it/doc/view/id/44
