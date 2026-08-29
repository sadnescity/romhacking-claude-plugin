---
name: relocation
description: Moves data into space that already exists instead of enlarging the file — finding free space, moving a block, and repointing it. Use when translated text does not fit, before considering expansion.
---

# Relocation

## What this is

Your text does not fit where it is. Before making the file bigger, look for
somewhere it already fits.

Almost every cartridge and disc has unused space. Banks were filled to a round
number and the last part left blank; a build tool padded to an alignment; a
feature was cut and its data removed. In a hex editor it shows as long runs of
`$FF` or `$00`, and it is free until something proves otherwise.

Relocation is: copy the block somewhere with room, update whatever points at it,
and leave the original alone until it works. If it does not work you have
changed nothing you cannot undo in two minutes.

The catch is the "whatever points at it". A block reached through a pointer
table moves easily — recompute the pointers. A block reached by an address
compiled into the code does not move at all until you patch the code. And a
block reached by counting from a fixed start moves only as a whole.

The second catch is subtler: **free space inside a bank the game already maps
is usable immediately; free space in a bank nothing ever switches to is not.**
The bytes are there but the processor never sees them, so using them costs the
same code change as an expansion, and at that point you may as well expand.

This is why relocation comes first in the order of work and expansion second:
when relocation is possible it is cheaper, reversible, and touches nothing
outside the block you moved.

### Read more

→ **[Espansione fisica di una rom](https://romhacking.it/doc/view/id/7)** (DrZork4 Translations) — covers finding usable free space, which is the half of this that comes first.

## Recognize

Relocation fits when a block needs more room than it has **and** somewhere else
has room. It does not fit when the data must live at a fixed address because
something other than a pointer reaches it — code with a hardcoded address, or a
table indexed by position.

## Analyze

Look for runs of a single filler byte long enough to hold what you want to move
(`budget.largest_free_run` does this), and check which bank the region belongs
to, for the reason above.

Then check the granularity of the pointers. If they address **groups**, you can
move a whole group but not one message inside it: everything after it in the
same group shifts, and no pointer describes those.

## Implement

1. copy the block to the new position
2. rewrite the pointers that address it
3. leave the old bytes alone until it works — restoring is then free

## Verify

Read that text in the game, from its new home. Then confirm nothing else moved:
only the block and its pointer entries should differ from the original file.

SOURCES: Espansione fisica di una rom — DrZork4 Translations — https://romhacking.it/doc/view/id/7 · I puntatori — AnusP — https://romhacking.it/doc/view/id/12 · Guida alle traduzioni parte II — SadNES cITy — https://sadnescity.it/guide/guidasad_rom.php
