---
name: text-search
description: Finds where a game stores its text when the encoding is unknown. Relative search, consensus across candidate bases, block boundaries by density, and searching RAM when the ROM holds nothing readable. Use when you need to locate dialogue, item names or menus inside a ROM, disc image or archive.
---

# Text Search

## What this is

You can see the text on screen. Now find it in the file — and you cannot search
for the words, because the game does not store letters as ASCII. `A` might be
`$0A`, or `$24`, or anything.

**Relative search** solves this with one observation: whatever value `A` has,
`B` is one more and `C` is two more. The *distances* between letters survive any
encoding. So instead of searching for `SWORD`, search for a place where five
consecutive bytes differ by the same amounts that S, W, O, R and D differ by:
`+4, -8, +3, -14`. Wherever that pattern appears, read the first byte, subtract,
and you know what value `A` has.

One word matching is luck — five bytes with the right differences turn up by
chance. Several *different* words agreeing on the same base is a finding, and
that agreement is the whole method.

Expect **two** answers, not one. Upper and lower case are usually two separate
runs of values, so two bases each explaining several words means two alphabets,
not a contradiction.

When relative search finds nothing, the possibilities are ordered:

1. the alphabet is not contiguous — letters scattered, or reordered to put
   frequent ones first
2. the text is compressed — see `compressions`
3. the text is not in the file at all: it is built at runtime, or comes from
   somewhere you have not looked

For 2 and 3 the answer is the same and it is a good one: **the text must exist
in memory while it is on screen**. Reach that screen, dump the console's RAM,
and search there — the encoding is the same, and RAM is small enough to search
by hand.

### Read more

→ **[Dumping, questo sconosciuto](https://romhacking.it/doc/view/id/6)** (Dark Schneider) — relative search explained from first principles, with the arithmetic written out.

→ **[Come trovare tabelle dei font particolari](https://romhacking.it/doc/view/id/26)** (Mat) — what to do when the alphabet is not contiguous and relative search finds nothing.

## Recognize

Three cases, and you find out which one you are in by trying the cheapest first.

| Case | What you see | Where to go |
|---|---|---|
| **Plain, linear encoding** | relative search finds several words agreeing on one base | continue here |
| **Non-contiguous alphabet** | words match individually but no base explains more than one | the alphabet is reordered or split; look for a font table instead |
| **Not in the ROM at all** | nothing matches anywhere | compressed or generated: search RAM while the text is on screen |

## Analyze

**Relative search**, with words you have seen on screen:

```python
import relsearch
bases = relsearch.consistent_bases(data, ["SWORD", "SHIELD", "ARMOR", "CASTLE"])
ranked = sorted(bases, key=lambda b: len({m.word for m in bases[b]}), reverse=True)
```

The base is anchored to the letter `A`, not to each word's own first letter, so
bases from different words can be compared. A base explaining three or more
words is a finding; two such bases are usually the two cases of one alphabet.

Search words must be single-case. In ASCII `A`–`Z` and `a`–`z` are each
contiguous but the gap between them is not, so a mixed word has no single base.

**Block boundaries** come from density, not from the matches. Slide a window
over the file and keep the runs where mapped bytes dominate:

```python
def density(window, is_mapped):
    return sum(is_mapped(b) for b in window) / len(window)
```

Treat the result as candidates, never as findings. Data that happens to use the
same byte range scores high and is not text: read the first eighty bytes of
every candidate before believing it. One block of repeating bytes decoding to
`eeeeeeMghg` is graphics, whatever the density says.

**When the ROM holds nothing**, the text exists at runtime. Reach the screen
that shows it, capture the emulator's memory, and search there; then take a
distinctive byte sequence from RAM and look for it in the file to find where it
was loaded from. The `toolchain` skill maps the platform to the emulator.

## Implement

Record every block in `ROMHACK.md` with name, start and end. Ranges, not
offsets alone: the end is what tells the next phase how much room there is.

## Verify

Decode at the offset and **read a sentence you have seen on screen**. That is
the proof. A statistical match is a lead, not a result.

If what comes out is almost words — right rhythm, wrong letters — the base is
off by a constant, which is a one-line fix, not a dead end.

SOURCES: Dumping, questo sconosciuto — Dark Schneider — https://romhacking.it/doc/view/id/6 · Come trovare tabelle dei font particolari — Mat — https://romhacking.it/doc/view/id/26 · Guida alle traduzioni parte I — SadNES cITy — https://sadnescity.it/guide/guidasad_base.php
