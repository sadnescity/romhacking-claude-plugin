---
name: recon
description: First phase of a translation. Identifies what a target actually is — cartridge ROM, optical image with a filesystem, or modern container — and builds an inventory where every byte is classified or counted as unknown. Use at the start of any ROM hacking project, or when handed an unfamiliar file.
---

# Recon

## What this is

Someone hands you a file and says "translate this game". Before anything else
you need to know what the file *is*: which machine, how it is laid out, where
the code ends and the data begins, and — most usefully — how much of it you
cannot explain yet.

That last number is the point of this phase, and it is the one people skip. An
inventory that says "81% code, 19% graphics, 0% unknown" is worth less than one
saying "60% code, 19% graphics, **21% unknown**", because the second tells you
where the next three days go. Labelling everything `code` to reach zero unknown
is not knowledge, it is bookkeeping.

Targets come in three shapes and the difference decides everything downstream:

**Cartridge images** are a flat address space with a small header. Everything is
at a fixed offset, the machine maps chunks of it into the processor's view, and
there is no directory of any kind. NES, SNES, Game Boy, Mega Drive.

**Optical images** are sequences of sectors with a filesystem on top. Files have
names, positions are sector numbers, and a byte offset is something you compute.
PlayStation, Saturn, PSP. See `filesystem-iso`.

**Containers** — one enormous file with a private index inside it. Common from
the disc era onward and universal in modern games. See `archives`.

Work out which from the bytes, never from the extension: an `.iso` is often a
raw dump, a `.bin` is often a cartridge, and a `.dat` is anything at all.

### Read more

→ **[Guida al Rom Hacking](https://romhacking.it/doc/view/id/2)** (Brisma) — an introduction covering both cartridges and PSX games, and a good first read for the whole craft.

→ **[Rom Hacking Tutorial vol. 1](https://romhacking.it/doc/view/id/31)** and **[vol. 2](https://romhacking.it/doc/view/id/48)** (DarkDreAm) — the same ground at more length, with worked examples.

→ **[ROMhacking.net — Getting Started](http://www.romhacking.net/start/)** — the English-speaking scene's entry point, and the largest collection of tools and documents.

## Recognize

Three families of substrate, distinguished by what the first bytes and the shape
of the file tell you.

| Family | Signals | Examples |
|---|---|---|
| **Cartridge image** | small magic header, size a power of two, no directory | `NES\x1a`, SNES with a header at a fixed offset, GB, GBA, Mega Drive |
| **Optical image** | sector-sized structure, a volume descriptor, a path table | ISO 9660 at sector 16, BIN/CUE with 2352-byte sectors, PSP UMD |
| **Modern container** | an index at one end, repeated record sizes, names in clear text | engine archives, packed asset bundles |

Useful early questions:

- Does a header describe the sizes? Do those sizes add up to the file length?
  If they do not, either the header is not what you think or there is trailing
  data — both are worth knowing on day one.
- Is there a region whose byte distribution is far from the rest? That is a
  candidate for compressed or packed data. The `compressions` skill picks this
  up.
- Are there runs of printable bytes? Names, paths and messages often sit in
  clear text even when the dialogue does not.

## Analyze

Build the inventory. Every byte belongs to exactly one region, and regions do
not overlap:

```python
import inventory
regions = inventory.classify(data, platform="nes")
print(inventory.report(regions, len(data)))
```

`classify` refuses platforms it does not know rather than guessing. Adding a
platform is a small, well-bounded piece of work — the `tooling` skill covers it.

As the project learns, narrow the inventory instead of rewriting it:

```python
regions = inventory.mark(regions, start=0x8000, end=0x8100, kind="text", note="dialogue")
```

Nothing is lost: `mark` carves the span out of whatever contained it.

## Implement

Initialise the project state:

```python
import romhack_state
state = romhack_state.State.new("game.nes", platform="nes")
state.save("ROMHACK.md")
```

Record platform, hash of the untouched copy, size, and the regions. The hash
matters more than it looks: every later verification compares against it, and a
project that lost track of which copy it started from cannot prove anything.

## Verify

`coverage` sums to 1, and the `unknown` share is a stated number.

```python
share = inventory.coverage(regions, len(data))
```

Pass the gate with that number as the evidence — for example
`inventory: 81% code, 19% graphics, 0% unknown`. Not "inventory done".

**Say what you measured.** "23% of the ROM is empty" is three different numbers
depending on what you counted: zero bytes, empty 32 KB banks, or empty 64 KB
blocks — on the same file they can easily differ by a factor of three. A share
without its unit cannot be checked by anyone, including you next week: write
`23.4% of 32 KB banks are empty` and the number becomes evidence instead of an
impression.

SOURCES: Guida al Rom Hacking — Brisma — https://romhacking.it/doc/view/id/2 · Introduzione al ROM-HACK e alla traduzione — LoRdCoStE — https://romhacking.it/doc/view/id/3 · Rom Hacking Tutorial vol. 1-2 — DarkDreAm — https://romhacking.it/doc/view/id/31 · Corso di traduzioni — Auryn — https://romhacking.it/doc/view/id/5 · Guida alle traduzioni parte I — SadNES cITy — https://sadnescity.it/guide/guidasad_base.php
