---
name: archives
description: Opens proprietary container files — finding the index, reading its entry format, extracting and rebuilding without breaking alignment. Use when a game keeps its data in one big file, when the filesystem lists a handful of huge files, or when a game reads by sector number and ignores the filesystem.
---

# Archives

## What this is

Open a typical disc-based game and the disc holds a handful of files, most of
them enormous.
The dialogue is not in any file called `SCRIPT.TXT`; it is inside `DATA.BIN`,
along with the graphics, the music and everything else.

Games do this because a disc is slow: one big sequential read beats a hundred
small ones. So the developers wrote their own container — an archive — with
their own index, and no two studios did it the same way.

An archive is almost always two parts: **an index** and **the data**. The index
is a table saying, for each item, where it starts and how big it is; the data is
everything glued together. Sometimes the index is at the front, sometimes at the
back, sometimes in a separate file, and sometimes — this is the awkward case —
inside the game's executable, because the game never uses the disc's filesystem
at all and reads by sector number.

There is nothing mysterious in any of them. The formats are simple because they
were written to be fast, not clever: a count, then a run of fixed-size entries,
then the payload, usually padded so each item starts on a round boundary.

What makes them work is that they are **self-describing if you look**: offsets
ascend, `offset[n] + size[n]` lands on `offset[n+1]`, names sit at a fixed
stride. You confirm the format with arithmetic, not with guesswork — and when
the arithmetic closes, you have understood it completely.

### Read more

→ **[Guida alle traduzioni parte III, §4](https://sadnescity.it/guide/guidasad_fs.php)** (SadNES cITy) — proprietary indexes and how games hide them, including the case where the table lives in the executable.

## Recognize

Signals, in the order they usually appear:

- the filesystem lists few files, several megabytes each
- a file begins with what looks like a **table**: values that ascend, spaced
  regularly, all landing inside the file
- repeated structure at a fixed stride: the same shape every 8, 12 or 16 bytes
- names in clear text, often padded to a fixed width
- a count at the very start, followed by that many entries

And the awkward case described above: no index in any file, because the game
reads by sector number from a table inside its executable.

## Analyze

### Find the index

The index is almost always at one end. Read the first 64 bytes and ask whether
they could be a count and a table; if not, read the last few kilobytes.

Then work out the entry format by looking for internal consistency:

- **offsets**, if consecutive values ascend and stay inside the file
- **offsets plus sizes**, if `offset[n] + size[n]` lands on or just before
  `offset[n+1]`. This is the strongest confirmation available and it costs one
  line of arithmetic
- **sizes only**, if the values do not ascend but summing them reaches the
  file's end: positions are implied by accumulation
- **names**, if there are runs of printable bytes at a fixed stride

Watch for **alignment**. Entries frequently start on 4, 16, 512 or 2048-byte
boundaries, with padding between them. Padding that you read as data produces an
extractor that works and a repacker that does not, because you will write the
padding back in the wrong place.

Ask whether offsets are absolute in the file, relative to the end of the index,
or **sector numbers** rather than bytes. Sector numbers are common in disc games
and look like small values that multiply neatly by 2048.

### When the index is in the executable

Convert a known file's position to the units the table would use — a sector
number for a disc, a byte offset for a flat file — and search the executable for
that value. Finding it once is a coincidence; finding several in sequence,
matching several files, is the table.

Failing that, put a **read breakpoint** on the data and let the game show you
who fetched it. The routine that computes the address reads the table.

## Implement

Write the extractor and the repacker **together**. An extractor alone gives you
things to look at and no way to put them back, and the effort is mostly shared.

Rebuilding has three rules that are easy to state and easy to forget:

1. **Preserve alignment.** If entries began on 2048-byte boundaries, they still
   must.
2. **Update the index.** Every offset and size after a changed file moves.
3. **Keep the container's total size** where anything outside it — a
   filesystem record, a hardcoded sector number, another index — describes it.

When a file must grow and the container cannot, the answers are the ones from
`space`: relocate the container, or expand the image and move it.

## Verify

**The round-trip, before anything else: unpack and repack untouched, and the
container must be identical byte for byte.**

An extractor that produces plausible files is not evidence. Only the rebuild
proves you understood the format — alignment, padding, the index, all of it. A
tool that has not passed this has no business touching real data.

Then the game: it boots, and the content from the container appears.

SOURCES: Guida alle traduzioni parte III §4 — SadNES cITy — https://sadnescity.it/guide/guidasad_fs.php · Come modificare la TOC — Sephiroth 1311 — https://romhacking.it/doc/view/id/29 · Dumping, questo sconosciuto — Dark Schneider — https://romhacking.it/doc/view/id/6
