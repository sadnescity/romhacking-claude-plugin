---
name: space
description: Phase four of a translation. Establishes how much room the translated text can have — pointer map, free space, and the choice between relocating and expanding. Use when translated text will not fit, or before deciding to enlarge a ROM.
---

# Phase 4 — Space

**Precondition:** `encoding` passed. Text goes out and comes back byte-identical.

**Artifact:** the pointer map, an inventory of free space, and a chosen strategy,
in `ROMHACK.md`.

**Gate:** the game boots and reaches the text with a block deliberately longer
than the original.

## The order that saves work

1. **`pointers`** — what addresses what, at which granularity. Everything else
   depends on this: you cannot move what you cannot repoint.
2. **`relocation`** — is there space already? Usually yes.
3. **`expansion`** — only if relocation is not enough.

Reversing steps 2 and 3 is the common mistake. Expanding is more invasive, needs
the mapper's cooperation and a way for the code to reach the new banks;
relocation needs neither.

## Deciding

| Situation | Answer |
|---|---|
| A few blocks need a little more room | relocate into existing free space |
| Text grows by a third across the whole game | expand, then relocate into the new banks |
| Pointers address groups, and one message in the middle grows | move the whole group, or make room by shortening a neighbour |
| Data is reached by hardcoded addresses, not pointers | neither: change the code, see `asm` |

Italian runs longer than English — commonly 10 to 20 percent for the same
sentence — so plan for growth rather than discovering it at the last block.

## Verify

Not "the ROM is structurally valid". Load it, boot it, reach the text. A valid
header with a broken layout produces a ROM that loads and does nothing, and only
the emulator tells you.

Record in `ROMHACK.md` how much room the strategy actually bought, in bytes.
"Enough" is not a number.
