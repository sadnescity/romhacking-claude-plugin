---
name: dte-mte
description: Recognises, reconstructs and recomputes DTE/MTE dictionaries — one byte standing for two or more characters. Use when text decodes with syllables missing, when unmapped bytes recur inside words, or when translated text needs to fit in the original space.
---

# DTE and MTE

## What this is

Cartridges were small and text is repetitive. DTE — dual tile encoding — buys
space with the cheapest trick available: **let one byte stand for two
characters**.

Normally `$41` means `A` and `$42` means `B`. In a game with DTE, a value like
`$80` means `th`, `$81` means `the `, `$82` means `ou`. The word `thou` then
costs two bytes instead of four. MTE is the same idea with longer sequences.

The dictionary — which byte means which pair — is a table somewhere in the ROM,
usually a plain list read by index. Nothing about it is clever; its value is
entirely in the arithmetic. English text under a good DTE dictionary shrinks by
a quarter to a third, and on a cartridge that was the difference between the
script fitting and not.

Two consequences for a translation, and both are easy to miss:

**Reading.** Until you know the dictionary, the text decodes with syllables
missing: `Th u art` instead of `Thou art`. It looks like a broken table rather
than compression, and people spend a day on the charset before realising.

**Writing.** The dictionary was computed for *English*. The frequent pairs of
Italian are not `th`, `he`, `ou` but `ch`, `gli`, `zio`, `che`. Translating
while keeping the original dictionary keeps the format and throws away most of
the saving — and the saving is precisely the space your longer Italian sentences
need. The dictionary is a table: recompute it for the language you are writing.

DTE is not the same thing as LZ77 or Huffman, which pack arbitrary data. It is a
substitution applied to text, it is far more common in games than real
compression, and it is the reason a script that looks uncompressed may still not
be readable byte by byte. For actual compression see `compressions`.

### Read more

→ **[Guida alle traduzioni parte I, §2](https://sadnescity.it/guide/guidasad_base.php)** (SadNES cITy) — DTE, MTE and the 16-bit encodings side by side, with the cases where a game mixes them.

→ **[Dumping, questo sconosciuto](https://romhacking.it/doc/view/id/6)** (Dark Schneider) — locating the dictionary in the ROM and reading it back.

## Recognize

- decoded text reads *almost* right, with syllables missing: `Th u art` instead
  of `Thou art`
- bytes outside the alphabet recur **inside** words, not at their edges
- somewhere in the ROM there is a region that looks like a list of short letter
  groups — that is the dictionary
- the same text takes visibly fewer bytes than its character count

The negative result is worth as much. A table that reaches near-total coverage
with **no multi-byte entry at all** means the game does not use DTE, and saying
so early stops you looking for a dictionary that is not there.

## Analyze

Find the dictionary, then confirm it. It is usually a contiguous table indexed
by the byte value: entry *n* is what byte `first + n` expands to. Decode a
sentence with it and read it — if the syllables land, it is right.

To look for candidates in what you cannot yet explain:

```python
import dte
dte.find_candidates(decoded_text, top=32, length=2)
```

## Implement

In the table, a DTE entry is just a multi-byte-to-text mapping:

```
80=th
81=the
82=ou
```

Encoding then prefers the longest match on its own, which is where the saving
comes from.

**For new text, recompute the dictionary** from the translated script, as
explained above:

```python
pairs = dte.best_pairs(translated_blocks, slots=len(original_dictionary))
```

Same number of slots, different contents. If the dictionary lives in ROM as a
table, you are rewriting a table, not restructuring anything.

## Verify

1. Round-trip holds with the multi-byte entries in place. If it breaks, the
   dictionary is being read wrongly — most often the base index is off by one.
2. The translated text **fits**. That is what the dictionary was for. Measure
   the bytes before and after: a recomputed dictionary that saves less than the
   original is a recomputation that went wrong.

SOURCES: Guida alle traduzioni parte I §2 — SadNES cITy — https://sadnescity.it/guide/guidasad_base.php · Dumping, questo sconosciuto — Dark Schneider — https://romhacking.it/doc/view/id/6
