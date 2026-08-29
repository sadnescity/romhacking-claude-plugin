---
name: expansion
description: Adds physical space to a ROM without breaking it — bank granularity, header update, mapper limits, and the fixed bank that carries the reset vectors. Use when a translation needs more room than the original layout provides and relocation is not enough.
---

# Expansion

## What this is

The cartridge is full and your translation is longer than the original. One
answer is to make the cartridge bigger — add empty space to the file and tell
the machine it is there.

This works because a cartridge is not just a block of bytes: it is a block of
bytes plus a **mapper**, a small chip that decides which part of the cartridge
the processor sees at any moment. The processor's address space is small — a
6502 sees 64 KB total — so the mapper swaps chunks called **banks** in and out.
A 512 KB game is 32 banks of 16 KB, and the mapper shows two at a time.

Expansion means adding banks. Three constraints, all hard:

**The mapper has a ceiling.** A bank register of four bits selects sixteen
banks and no more. Adding a seventeenth produces a file the machine cannot
address. Find the ceiling before you plan anything.

**Space comes in whole banks.** Half a bank is not a thing.

**Something must switch to the new banks.** Empty space the game never maps is
empty space on your disk and nothing else. Usually this means a small code
change — see `asm`.

And one trap that silently kills a ROM: on many mappers **the last bank is
fixed** at the top of the address space, because that is where the processor
looks for the reset vector when it powers on. Append your new banks at the end
and that bank is no longer last. The machine jumps into empty space and the
screen stays black, with a file that looks perfectly well-formed. New banks go
*before* the last one.

### Read more

→ **[Espansione fisica di una rom](https://romhacking.it/doc/view/id/7)** (DrZork4 Translations) — expansion worked through, with the mapper constraints.

→ **[Guida alle traduzioni parte II, §2](https://sadnescity.it/guide/guidasad_rom.php)** (SadNES cITy) — the SNES case, where bank granularity and the LoROM/HiROM distinction decide what is possible.

→ **[fullsnes](https://problemkaputt.de/fullsnes.htm)**, **[gbatek](https://problemkaputt.de/gbatek.htm)**, **[everynes](https://problemkaputt.de/everynes.htm)** (Martin Korth) — the authority on what each mapper can actually address. Check the ceiling here before planning an expansion.

## Recognize

Expansion is possible when the mapper can address more space than the cartridge
contains, and pointless when it cannot — no amount of header editing raises the
mapper's ceiling.

It is the second answer, not the first: look for free space that already exists first — see `relocation`. Expanding is
more invasive and can be undone only by starting over.

## Analyze

Beyond the constraints above, **the header must keep describing the file**:
after adding banks, the declared sizes and the actual length have to agree, or
the emulator loads garbage. For an iNES image the seed script handles both the
header and the fixed bank:

```python
import ines
expanded = ines.expand_prg(data, add_banks=4)   # inserts before the last bank
```

## Implement

Expand, then verify the structure before spending time on anything else:

```python
assert ines.is_consistent(expanded)
start, end = ines.prg_slice(expanded)
assert expanded[end - 16384:end] == original_last_bank
```

Then decide what goes in the new space and how the code switches to it — see
`asm`.

## Verify

**Boot it.** A structurally valid ROM that does not boot is an ordinary
outcome, and static checks cannot see it. Load it, watch it reach the title
screen, then reach the text.

Then the phase gate: the game runs with a block deliberately longer than the
original.

SOURCES: Espansione fisica di una rom — DrZork4 Translations — https://romhacking.it/doc/view/id/7 · Guida alle traduzioni parte II §2 — SadNES cITy — https://sadnescity.it/guide/guidasad_rom.php
