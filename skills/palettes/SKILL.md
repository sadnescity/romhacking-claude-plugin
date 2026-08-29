---
name: palettes
description: Finds and edits colour palettes — the packed 15/16-bit formats consoles use, fixed hardware palettes, and how to tell which entry a tile is actually drawn with. Use when graphics come out with the right shapes and the wrong colours, or when a new glyph is invisible.
---

# Palettes

## What this is

A tile does not contain colours. It contains small numbers — 0, 1, 2, 3 — and a
separate table says what each number looks like. That table is the palette.

The arrangement exists because it is cheap and flexible. Cheap: a 4-colour tile
needs 2 bits per pixel instead of 24. Flexible: the same tile drawn with a
different palette becomes a different-coloured object, which is how one sprite
becomes an enemy and its stronger variant.

Consoles store a colour in about two bytes, splitting them between red, green
and blue — typically five bits each, which is 32 levels per channel and 32768
colours in total. Some machines, like the NES, have no colour values at all,
only indices into a set fixed in the hardware.

For a translator this chapter usually matters in one specific way: **a new
glyph drawn in the wrong colour index can be invisible**, while everything
about it looks correct. The trap is described under Analyze.

### Read more

→ **[Guida all'hacking della grafica](https://romhacking.it/doc/view/id/10)** (Dark Schneider) — palettes alongside the tile formats they serve.

→ **[fullsnes](https://problemkaputt.de/fullsnes.htm)** / **[gbatek](https://problemkaputt.de/gbatek.htm)** (Martin Korth) — the exact colour format and palette memory layout per machine, when you need the bits rather than the idea.

## Recognize

**Packed 15-bit BGR**, the most common by far — SNES, Game Boy Color, GBA. Two
bytes per colour, little-endian:

```
        bit  15 14        10 9         5 4         0
             0  b b b b b   g g g g g   r r r r r

7C 1F  →  $1F7C  →  b=%00111 g=%11011 r=%11100  →  a warm yellow
```

Note the order: **blue is the high bits, red the low ones**. Reading it as RGB
gives you a picture with red and blue swapped, which looks deliberate and is not.

Each channel is 5 bits, so to get 8-bit values for a PNG multiply by 8 — or
better, replicate the top bits (`v << 3 | v >> 2`) so that 31 maps to 255 and
not 248.

**Fixed hardware palettes** — the NES has no palette data in the usual sense:
memory holds indices into a fixed set of about 54 colours built into the
hardware. "Editing the palette" means choosing different entries from that set;
you cannot invent a colour that the console cannot make.

**Indexed with a CLUT** — the PlayStation and friends keep the colour table
inside the image file. See `image-formats`.

## Analyze

**Find the palette by changing it.** Write conspicuous values into a candidate
region while the game runs and see what changes colour on screen. Faster and
more certain than any static search, and it also tells you *which* palette a
given tile uses — usually the thing you actually need to know.

```python
palette = client.call("mesen_get_palette", cpuType="Nes")   # or the equivalent
```

**Index 0 is normally transparent** for sprites and the backdrop for
backgrounds. A pixel of colour 0 is not "black", it is "nothing".

### The invisible glyph

**A pixel drawn in a colour the palette renders as the background is invisible,
and everything about it looks correct.** The tile is right, the position is
right, the data in video memory is right, and nothing appears.

*Example:* in a 2bpp tile, plane 0 alone gives colour 1 and both planes give
colour 3. An accent drawn on both planes, in a font that uses only plane 0,
comes out as colour 3; with an active palette of `0F 30 0E 0E` colour 1 is
white and colour 3 is black — the accent is there, black on black.

So before drawing anything into an existing tile, **read the palette and check
which indices the surrounding glyph uses**. Draw in those. Then count the lit
pixels on screen rather than looking: two pixels on an 8×8 grid are exactly the
size at which the eye sees what it expects.

## Implement

Read the packed value, unpack, edit, repack. The only real decision is what to
do about the missing bits when converting to 8-bit and back: if you multiply by
8 on the way out you must divide by 8 on the way in, and if you replicate bits
you must shift right. Mixing the two loses a step of colour every round-trip.

## Verify

Round-trip the whole palette, then look at the game. Colours are the one area
where the eye is a better instrument than a test — but only after the numbers
agree.

SOURCES: Guida all'hacking della grafica nel processo di traduzione di ROM — Dark Schneider — https://romhacking.it/doc/view/id/10 · Game Boy Advance: Formati comuni per la grafica — DarkDreAm — https://romhacking.it/doc/view/id/45 · Modificare la grafica RAW nei giochi PSX — Dark Schneider — https://romhacking.it/doc/view/id/16
