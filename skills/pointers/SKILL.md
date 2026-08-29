---
name: pointers
description: Finds, classifies and rewrites pointer tables — width, endianness, base, banking, and whether they address messages or groups. Use before moving any block of text or data, or when reinserted text appears in the wrong place.
---

# Pointers

## What this is

A game does not store its text as one long stream it reads from the top. It
needs to jump straight to line 214 when the shopkeeper speaks, so somewhere
there is a list saying *where each line begins*. That list is the pointer table,
and each value in it is a pointer.

Why this matters more than anything else in a translation: **the moment your
text changes length, every line after it moves**, and the pointers still describe
where things used to be. The game happily jumps to the middle of a word.

A pointer is just a number — an address — stored in two, three or four bytes.
Three details decide whether you read it correctly:

**Width.** Two bytes reach 64 KB, three reach 16 MB. Older consoles use two,
which is why their text lives in banks.

**Byte order.** Most consoles are little-endian: the value `$8A2C` is stored as
`2C 8A`, low byte first. Reading it the other way gives `$2C8A`, which is a
plausible-looking address pointing at nothing.

**Base.** This is the one that catches people. The number a pointer holds is the
address *the CPU sees*, not the offset in your file. A cartridge maps its data
into the processor's address space at some fixed point, and a disc game's file
starts at some sector; either way there is a constant difference between "byte
17 of the file" and "the address the game asks for". Get it wrong by a constant
and every pointer is wrong by the same constant — which at least is easy to
spot, because the whole table lands in the wrong place together.

One more thing, and it is not obvious: **a pointer table need not point at every
string**. Many games point at *groups* — the ten lines of one conversation — and
then walk forward counting terminators to reach the fourth line. You can move a
whole group; you cannot move one line inside it without shifting its neighbours.

### Read more

→ **[I puntatori lorom](https://romhacking.it/doc/view/id/36)** and **[I puntatori hirom](https://romhacking.it/doc/view/id/43)** (SadNES cITy) — the SNES memory maps worked through in full. The two layouts compute the base differently, and adding a single byte to a HiROM shifts every pointer at once.

→ **[Guida ai puntatori del Game Boy](https://romhacking.it/doc/view/id/14)** (Dark Schneider) — the same reasoning on a banked 8-bit machine, with the bank arithmetic spelled out.

→ **[Tracking down pointers for PlayStation games using debuggers and Ghidra](https://suxin.space/notes/tracking-down-playstation-pointers-using-debuggers-ghidra/)** — when static search fails: finding the table by watching the code read it.

## Recognize

A run of fixed-width values that all land inside a plausible region, usually
ascending, usually sitting **immediately before or after** the data they
address — often just a few bytes before the first string.

One value matching is noise: with two bytes it happens by chance every few
kilobytes. A **run** of consecutive slots all pointing into the set is a table.

Ascending and distinct is the cheap sanity check. Collisions or a value going
backwards mean the width, the endianness or the base is wrong — not that the
game is strange.

## Analyze

**Work out the base from the mapping, not by trial.** On a banked cartridge:
which bank holds the data, where that bank appears in the CPU's address space,
and what the file offset of the bank start is. For a block sitting in a bank
mapped at `$8000`, with a 16-byte file header, the base is simply `-0x10`.

```python
import pointers
found = pointers.find_pointer_tables(data, targets, width=2, endian="little", base=-0x10, min_run=8)
```

**Ask what granularity they address.** Compare the number of pointers with the
number of terminators in the block: far fewer pointers than messages (say, 19
for nearly 300) means **group** pointers, and the game counts terminators to
reach the n-th message inside a group. You may then move a whole group freely,
but not one message inside it.

When the static search finds nothing, put a **read breakpoint** on the block and
let the game tell you who fetched it. The routine that reads the address shows
the width and the base at once. See `toolchain` for the emulator.

## Implement

```python
values = pointers.read_pointers(data, table)
patched = pointers.write_pointers(data, table, new_values)
```

Rewrite only what moved. A repointing that changes bytes outside the table is
a repointing that has already gone wrong.

## Verify

Move **one** block, recompute **its** pointer, and read that text in the game.
If the right line appears in the right place, the model of width, endianness,
base and granularity is correct, and it will hold for the rest.

Cheap checks first, in this order: the rewritten table still reads back as
expected; only the intended bytes changed; the values are still ascending and
distinct. Then run it.

SOURCES: Tracking down pointers for PlayStation games using debuggers and Ghidra — https://suxin.space/notes/tracking-down-playstation-pointers-using-debuggers-ghidra/ · I puntatori — AnusP — https://romhacking.it/doc/view/id/12 · Puntatori (SNES): questi sconosciuti — DrZork4 Translations — https://romhacking.it/doc/view/id/13 · I puntatori lorom — SadNES cITy — https://romhacking.it/doc/view/id/36 · I puntatori hirom — SadNES cITy — https://romhacking.it/doc/view/id/43 · Guida ai puntatori del Game Boy — Dark Schneider — https://romhacking.it/doc/view/id/14
