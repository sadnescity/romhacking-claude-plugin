---
name: fonts
description: Finds a game's font, understands how characters map to glyph tiles, and extends it with the characters a translation needs. Use when adding letters a game does not have, when text renders as the wrong symbols, or when you need to know how much room a font has left.
---

# Fonts

## What this is

A game's font is a set of tiles, one per character it can draw, plus a rule
linking a byte in the text to one of those tiles. That rule is usually the
simplest one imaginable — **the byte is the tile number** — and when it is, the
font and the table (see `tables`) are two views of the same thing.

Not always, though. Some games add an offset, some use a lookup table because
the glyphs are not in alphabetical order, and some draw text with sprites rather
than background tiles, which changes where the font lives but not what it is.

Two properties decide what a translation can do with it.

**How many slots there are.** A font occupying tiles `$00`–`$7F` has 128
positions, of which the game may use 90. The rest are free — if the print
routine can address them, which is a separate question (see `asm`).

**Whether characters are the same width.** A fixed-width font gives every
character the same number of pixels, so text is easy to measure and looks airy.
A variable-width font stores a width per character and packs them; it fits far
more text in the same window, and it costs a table of widths that you must also
extend. See `vwf`.

For a translation the font is where the accented characters come from, and it is
usually the least contested resource in the whole project: fonts almost always
have unused slots. The scarce thing is byte values, not pictures.

### Read more

→ **[Come trovare tabelle dei font particolari](https://romhacking.it/doc/view/id/26)** (Mat) — fonts that are not laid out in alphabetical order, and how to map them.

→ **[Guida all'hacking della grafica](https://romhacking.it/doc/view/id/10)** (Dark Schneider) — finding the font among the rest of the graphics.

## Recognize

The font is the easiest graphics to find in any game, because you know exactly
what it should look like. Point a tile viewer at the character graphics and
scroll: an alphabet is unmistakable.

Two quick confirmations:

- **the space character's tile is blank.** Find the byte your table says is a
  space, look at that tile index: if it is uniform, the mapping is direct.
- **the letters are in order.** `A B C D` in consecutive slots means byte value
  and tile number differ by a constant, which you can read off immediately.

If the alphabet is there but scrambled, the game has a lookup table between text
byte and tile — find it by picking a letter, noting its tile, and searching for
that value near the font.

## Analyze

**Count the free slots.** Uniform tiles are candidates, but check they are not
used: a blank tile may be a second space the game uses in menus, and drawing on
it puts a letter where the game wanted nothing. Cross-check against the text: a
byte that never appears in any block is genuinely unused.

**Check which plane carries the shape** — rendering the planes separately, as
`tiles` explains. New glyphs go on the same planes.

**Find the width table, if there is one.** A run of small numbers — 3 to 8 —
with as many entries as the font has glyphs, usually near the font itself.

## Implement

Adding a character is: draw the tile in a free slot, add the table entry for its
byte, and — if the font is variable-width — add its width. Miss the third and
the new character renders with whatever width was there before, which for an
unused slot is often zero.

Copy an existing glyph as a starting point rather than drawing from scratch:
matching the stroke weight and baseline of a pixel font by eye is harder than it
sounds, and a letter that is one pixel taller than its neighbours is visible
immediately.

## Verify

Render the whole font as a sheet and read it. Then put the new characters in
actual game text and look at them on screen, at the size the game draws them —
a glyph that is legible at 6× is not necessarily legible at 1×.

Count the lit pixels rather than trusting the eye for anything small — see
`accents` for the measurement.

SOURCES: Come trovare tabelle dei font particolari — Mat — https://romhacking.it/doc/view/id/26 · Guida all'hacking della grafica nel processo di traduzione di ROM — Dark Schneider — https://romhacking.it/doc/view/id/10 · Guida alle traduzioni parte II — SadNES cITy — https://sadnescity.it/guide/guidasad_rom.php
