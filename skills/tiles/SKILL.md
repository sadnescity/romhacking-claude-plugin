---
name: tiles
description: Reads and writes tile graphics in the formats consoles actually use — planar, interleaved-planar and linear, at 1 to 8 bits per pixel — and converts them to PNG and back. Use when editing game graphics, extracting a font, or when a tile viewer shows noise instead of pictures.
---

# Tiles

## What this is

Consoles do not draw pictures pixel by pixel — there was never enough memory for
that. They draw with **tiles**: small squares, almost always 8×8 pixels, stored
once and stamped onto the screen wherever needed. A background is a grid saying
"tile 12 here, tile 12 again, tile 40 there", and because the same tile repeats,
a whole screen costs very little.

A font is tiles. A character portrait is tiles. This is why editing game
graphics means editing tiles, and why a text window is a grid of them.

What a tile stores is not colours but **colour indices** — small numbers looked
up in a palette (see `palettes`). How many colours a tile can use is its **bit
depth**: 2 bits per pixel gives four colours, 4 bits gives sixteen. More depth
means more bytes per tile, so machines used the least they could get away with,
and text is very often the cheapest depth available.

The part that trips everyone is how those bits are arranged in memory. There are
two philosophies:

**Planar** — store all the low bits of a row together, then all the high bits.
Hardware liked this because each plane could be fetched separately. It means the
bits of a single pixel are in *different bytes*, which is why a planar tile read
as linear looks like stripes.

**Linear** — store the pixels in reading order, packed several per byte. Later
machines use this, and it is what you would invent yourself.

Neither is complicated once you know which one you are looking at. Choosing
wrong is the entire reason a tile viewer shows noise, and the fastest way to
settle it is to look for the font: letters are unmistakable, so a wrong setting
is obviously wrong rather than plausibly right.

### Read more

→ **[Guida all'hacking della grafica nel processo di traduzione di ROM](https://romhacking.it/doc/view/id/10)** (Dark Schneider) — tile formats and bitplanes explained for translators.

→ **[Guida alle traduzioni parte II, §3](https://sadnescity.it/guide/guidasad_rom.php)** (SadNES cITy) — how bitplanes build colour, with the SNES depths.

→ **[Game Boy Advance: Formati comuni per la grafica](https://romhacking.it/doc/view/id/45)** (DarkDreAm) — the linear formats, and the nibble order that catches everyone.

→ **[Finding Neo Geo tiles](https://www.mattgreer.dev/blog/finding-neo-geo-tiles/)** (Matt Greer) — a modern worked example of locating graphics in an unfamiliar machine, part of a [series](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-guide-part-1/) that is the best documentation the Neo Geo has.

→ **[Formati grafici del NeoGeo](https://romhacking.it/doc/view/id/56)** (DarkDreAm) — the same hardware in Italian, shorter and to the point.

## Recognize

Three families. You can tell them apart by editing one pixel and seeing which
bytes change.

**Planar** — one byte per row per bitplane, planes stored one after another.
The NES, at 2 bits per pixel, 16 bytes per tile:

```
plane 0 (8 bytes)   plane 1 (8 bytes)
18 3C 66 66 7E 66 66 00   00 00 00 00 00 00 00 00
```

Pixel (x, y) is `bit(plane0[y], 7-x) | bit(plane1[y], 7-x) << 1`. Row 0 is
`0x18` = `00011000`, so pixels 3 and 4 are colour 1 and the rest colour 0 —
the top of a capital A.

**Interleaved planar** — the same idea, but planes alternate row by row, in
pairs. The SNES at 4bpp, 32 bytes per tile:

```
row0p0 row0p1 row1p0 row1p1 ... then planes 2 and 3 for all eight rows
```

**Linear** — pixels in reading order, packed. The GBA at 4bpp, 32 bytes:

```
21 43 65 87 ...
^^ low nibble is the LEFT pixel, high nibble the right
```

The nibble order catches everyone once: in a linear 4bpp format the **low**
nibble comes first on screen.

### Reading the symptom

| What you see | What it means |
|---|---|
| recognisable shapes, wrong colours | right layout, wrong palette or bit depth |
| vertical stripes, shapes half-formed | planar read as linear, or the wrong plane count |
| shapes shifted diagonally by a pixel per row | wrong tile width, or a stride that is not 8 |
| noise with no structure at all | not graphics, or compressed — see `compressions` |

Half-formed shapes are the useful case: it means you are one parameter away.

## Analyze

Establish four things, in this order, because each narrows the next:

1. **Bit depth** — how many colours. Look at the palette the game loads.
2. **Layout** — planar, interleaved or linear.
3. **Tile size** — 8×8 is the default; 8×16 and 16×16 exist.
4. **Where the tile actually starts** — being off by 8 bytes gives you half of
   one glyph and half of the next, which reads as garbage but is one number
   away from correct.

**A font that looks like noise combined may be perfectly legible one plane at a
time.** Many fonts draw the shape in plane 0 and use the others for an outline
or shadow. Render the planes separately before concluding anything.

## Implement

```python
import tilepng
rows = tilepng.decode_tile_2bpp(data, offset)     # 8x8 grid of colour indices
raw = tilepng.encode_tile_2bpp(rows)              # back to bytes
tilepng.png_write(path, tilepng.sheet(data, base, range(16), palette, scale=6))
```

For a format the seed does not cover, write it: the whole of a tile codec is a
pair of nested loops, and `tooling` explains where it should live.

## Verify

**Round-trip every tile in the region, not a sample.**

```python
for i in range(count):
    off = base + i * 16
    assert tilepng.encode_tile_2bpp(tilepng.decode_tile_2bpp(data, off)) == data[off:off + 16]
```

A codec that handles 500 tiles and mangles the 501st is a codec that will
corrupt one glyph in a font, and nobody notices until that letter appears.

Then look at it: render a sheet and read the alphabet. Correct bytes that
produce unreadable letters mean the parameters are wrong, and the round-trip
cannot see that — it is happy to reproduce nonsense faithfully.

SOURCES: Neo Geo ROM Hacking Guide — Matt Greer — https://www.mattgreer.dev/blog/neo-geo-rom-hacking-guide-part-1/ · fullsnes / gbatek / everynes — Martin Korth — https://problemkaputt.de/ · Guida all'hacking della grafica nel processo di traduzione di ROM — Dark Schneider — https://romhacking.it/doc/view/id/10 · Guida alle traduzioni parte II §3 — SadNES cITy — https://sadnescity.it/guide/guidasad_rom.php · Game Boy Advance: Formati comuni per la grafica — DarkDreAm — https://romhacking.it/doc/view/id/45 · Formati grafici del NeoGeo — DarkDreAm — https://romhacking.it/doc/view/id/56
