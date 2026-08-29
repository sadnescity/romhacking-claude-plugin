---
name: accents
description: Adds accented glyphs to a game that never had them — finding glyph space and byte values without sacrificing existing characters, drawing the glyphs, and proving they render on screen. Use when a translation needs à è é ì ò ù È or any character outside the original charset.
---

# Accented Glyphs

## What this is

Italian needs à è é ì ò ù, and È at the start of a sentence. A game written for
English has none of them — neither the shapes to draw them nor the byte values
to select them — so a translation has to add both.

It is a space problem on **two independent axes** that people routinely
conflate:

**The glyph.** Somewhere in the character graphics there must be a picture of
`à`. Fonts are tiles like any other graphics (see `tiles`), and a font has a
slot for each character it can draw. Adding a glyph means finding an unused
slot and drawing in it.

**The code.** The text must be able to *say* `à`: a byte value that the print
routine accepts and that maps to the new tile. This axis is usually the binding
one, and that surprises people: character graphics almost always have unused
tiles somewhere, while the byte values a routine accepts are often completely
spoken for.

Solving one without the other gets you a glyph nothing can reach, or a table
entry that draws garbage.

### The rule

**Accented glyphs are characters you ADD. You never take an existing one away.**

The temptation is obvious: Italian does not use `j`, `w`, `x`, `y`, so their
slots look free. They are not. Sacrificing them means:

- every line of **original** text that used them renders as garbage for the
  entire months the translation is in progress (*example:* `listen now to my
  words` becomes `listen noì to mù ìords`);
- **proper names lose letters** — names keep their spelling in any language;
- any screen you have not tested that still uses that glyph is broken, and you
  will not find out until someone plays it;
- whoever inherits the project inherits a mutilated font and no way to know
  which glyphs are gone.

Usage counts do not make it acceptable — they only tell you which damage is
smallest. The answer is to find room, not to make room.

**The one legitimate exception** is an entire alphabet the target language does
not use: hiragana, katakana and kanji in a Japanese game being translated. That
space is genuinely dead — nothing in the translated game will reference those
glyphs — and usually generous enough for a full accented set.

This phase comes where it does because an accent on screen needs the font, the
table, the space and the pointers to be right *at the same time*: it is the
cheapest end-to-end proof that the earlier phases worked.

### Read more

→ **[Guida all'hacking della grafica](https://romhacking.it/doc/view/id/10)** (Dark Schneider) — drawing glyphs, which is the first of the two axes.

→ **[Guida alle traduzioni parte II, §3-4](https://sadnescity.it/guide/guidasad_rom.php)** (SadNES cITy) — font editing in the context of a translation.

## Recognize

Italian needs seven at minimum — **à è é ì ò ù È** — and twelve to be done
properly, adding **À É Ì Ò Ù**. A translation without them is the mark of a job
that stopped early; an apostrophe in place of the accent (`perche'`) is not an
alternative, it is the defect this phase exists to prevent.

## Analyze

### Where to find room, in order of cost

1. **Unused tiles that the text encoding can already reach.** Look for uniform
   tiles and check they are not used anywhere, including as an alternate blank
   (see `fonts`). Then check the print routine actually accepts their index: a
   free tile at `0xB2` is worthless if the routine stops at `0x80`.
2. **An unused alphabet**, per the exception above.
3. **A code patch, and possibly a new bank.** When free tiles exist but the
   encoding cannot reach them, the barrier is the print routine: patch it to let
   the values through. When tiles are what is missing, put the extended font in
   a fresh character bank and patch the routine to switch to it while drawing.
   Either way nothing is taken away — see `asm` and `expansion`.

   **Expect more than one routine.** Menus, dialogue, shops and battle text are
   frequently separate code, enforcing the same limit through different
   instructions. Patching the dialogue routine and finding the menu still
   truncating is the normal experience, not a mistake — `asm` covers the
   discipline.
4. **An escape control code**: one byte meaning "the next character comes from
   the extended set". Costs a byte per accented character, so it fits games
   with room in the script and none in the charset.

Recovering byte values by shrinking a DTE dictionary belongs here too, when the
dictionary is bigger than the translation needs (see `dte-mte`).

### Which bank is on screen

Character graphics are often banked, and the banks need not hold the same font.
Writing glyphs into the first bank of the file and seeing no change on screen
is the classic symptom. Compare what the file holds with what the video
hardware is actually showing — on NES, for instance:

```lua
emu.read(addr, emu.memType.nesChrRom)      -- what is in the file
emu.read(addr, emu.memType.nesPpuMemory)   -- what the PPU is showing
```

If they differ, find the bank whose contents match what is on screen, and write
there.

### Drawing the mark

**Where the accent goes.** Lowercase glyphs usually leave the top row **and**
the bottom row empty: shift the glyph down one row and you have two rows for
the accent instead of one — the difference between an accent you can read at
8×8 and a stray pixel. Uppercase frees only one row, so it gets a single-row
mark.

**The dotted letter.** `i` already uses the top row for its dot; for `ì` the
accent **replaces** the dot, which is also what the typography wants.

**The colour.** Draw the accent on the **same bitplanes the base glyph uses**.
A mark drawn on other planes selects another palette entry, which may render as
the background: correct in the file, correct in video memory, and invisible.
`palettes` covers this trap.

## Implement

Copy the base vowel, add the mark, write it to the free slot, and add the table
entry for its byte value — plus its width, if the font is variable-width (see
`vwf`). Record in `ROMHACK.md` the glyph indices, the bank, and an empty list of
sacrificed glyphs.

## Verify

**A screenshot from the emulator, showing the glyphs in game — and then measure
it.**

Not "I added the tile". Not a render of the character graphics — that proves
the glyph exists in the file, a useful intermediate check and *not* the same
claim. And not "I looked at the screenshot and they seem to be there": an
accent is two pixels on an 8×8 grid, and at that size you see what you expect
to see. Count them:

```python
import tilepng
pixels = tilepng.png_read("proof/accents-in-game.png")
on_accent = tilepng.lit_pixels(pixels, x=x0, y=accent_row, width=w, height=2)
on_body = tilepng.lit_pixels(pixels, x=x0, y=accent_row + 2, width=w, height=6)
assert on_body > 0 and on_accent > 0
```

`on_body` is the sensitivity check: if the letters themselves are not lit, the
coordinates are wrong and a zero on the accent rows proves nothing.

Insert a line containing all seven, reach it in the game, capture it, measure,
and put the path in the `accents` gate evidence in `ROMHACK.md`. Then reach the
other contexts — menus, shops, names — and check each one.

SOURCES: Guida all'hacking della grafica nel processo di traduzione di ROM — Dark Schneider — https://romhacking.it/doc/view/id/10 · Guida alle traduzioni parte II §3-4 — SadNES cITy — https://sadnescity.it/guide/guidasad_rom.php · 8x8 proportional font secrets — Near — https://romhacking.it/doc/view/id/55
