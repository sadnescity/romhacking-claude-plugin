---
name: vwf
description: Variable width fonts — reading and extending a width table, and hacking one into a game that draws fixed-width text. Use when a translation does not fit the window, when new glyphs render with the wrong spacing, or when deciding whether a VWF is worth the work.
---

# Variable Width Fonts

## What this is

In a fixed-width font every character occupies the same number of pixels, so
`i` gets as much room as `W`. It is simple to draw — advance eight pixels, stamp
the next tile — and it wastes a great deal of space, because most letters are
narrower than the widest one.

A variable-width font gives each character its own width. `i` takes three
pixels, `W` takes eight, and a line of text fits perhaps a third more
characters in the same window.

For a translation into Italian, that third is often the difference between the
text fitting and not. It is the single most effective thing you can do about
space that does not involve moving any data — and it is worth considering before
relocating or expanding anything, because it makes every line shorter rather
than finding somewhere to put the overflow.

The cost is that the game must **draw differently**. Fixed-width text can be
stamped tile by tile onto the background grid, which is nearly free. Variable
width means characters no longer align to tile boundaries: a glyph starts three
pixels into one tile and finishes in the next, so the renderer has to compose
each row of text pixel by pixel into a buffer and then transfer it.

This is why the chapter splits in two, and they are very different jobs:

- **the game already has a VWF** — then there is a width table, you extend it,
  and the work is an afternoon
- **the game draws fixed width** — then adding a VWF means writing a text
  renderer in assembly, which is one of the larger jobs in this craft

### Read more

→ **[Modificare i Variable Width Font](https://romhacking.it/doc/view/id/27)** (Gemini) — editing an existing VWF, width tables included.

→ **[Variable Width Font disegnati su tile](https://romhacking.it/doc/view/id/38)** (Gemini) — the harder case: composing proportional text onto a tile grid.

→ **[8x8 proportional font secrets](https://romhacking.it/doc/view/id/55)** (Near) — the classic on fitting a proportional renderer into an 8-bit budget.

## Recognize

Look at the game's own text on screen. If the gap between `i` and the next
letter is visibly smaller than between `W` and the next, it is variable width.
If everything sits on a strict grid, it is fixed.

A width table looks like a run of small numbers — typically 2 to 8 — with as
many entries as the font has glyphs, and it usually sits next to the font. The
entry for the space character is a good anchor: it is usually the narrowest
value in the table.

## Analyze

**With an existing VWF**, find the table and confirm it by changing one value to
something absurd and watching that letter's spacing change. The table's order
matches the font's, so once you have the correspondence for one glyph you have
it for all of them.

**Without one**, you are looking at the routine that draws text. Find it the way
`asm` describes — breakpoint where the characters land — and understand how it
composes a line. Adding variable width means: keep a running pixel position
instead of a tile position, shift each glyph's bits into place, and merge into a
buffer. The shifting is the expensive part on an 8-bit machine and the reason
some games have a VWF only in dialogue and fixed width in menus.

Before starting that job, measure what it buys. Add up the widths of your
translated text under fixed and variable width; if the difference does not solve
your space problem, it is a large piece of work for a partial result, and
relocation may be the better answer.

## Implement

Extending a table: one entry per new glyph, matching the drawn width. Measure the
glyph rather than guessing — the width is the number of pixels from the left
edge to the last lit column, plus the gap you want after it, and consistency
here is what makes text look composed rather than ragged.

Writing one: budget it as an assembly project with its own free space, and keep
the original routine intact behind your hook so that anything you have not
handled still renders the old way.

## Verify

The screen, always. Then a line of the widest characters in the language,
followed by a line of the narrowest, both at the window's limit — a VWF that
handles average text and breaks on `WWWWW` is a VWF that will break in the one
scene where a character shouts.

SOURCES: Modificare i Variable Width Font — Gemini — https://romhacking.it/doc/view/id/27 · Variable Width Font disegnati su tile — Gemini — https://romhacking.it/doc/view/id/38 · 8X8 PROPORTIONAL FONT SECRETS — Near — https://romhacking.it/doc/view/id/55
