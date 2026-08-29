---
name: image-formats
description: Console and engine image containers — TIM, TIM2, GIM and their relatives — how to recognise them, extract them, and put a modified picture back. Use when a game stores pictures as files rather than raw tiles, when a title screen or a menu graphic needs translating, or when an extractor produces the right size and the wrong picture.
---

# Image Formats

## What this is

Cartridge games store graphics as raw tiles: bytes at an offset, with nothing
saying how wide the picture is or what colours it uses (see `tiles`). Disc-era
games generally do not. They wrap pictures in small **container formats** with a
header describing the image — dimensions, colour depth, where the palette is —
because a disc holds thousands of pictures and something has to keep track.

The PlayStation family is the clearest example, and its formats set the pattern
that many others follow:

**TIM** — the PlayStation's own. A magic number, a flags word saying the colour
mode, an optional **CLUT block** holding the palette, then the image block
holding pixels. The dimensions are given in units of the console's video memory
rather than in pixels, which is the detail that catches people: a 4-bit image
256 pixels wide reports a width of 64, because four pixels share each 16-bit
video word.

**TIM2, GIM** — the PlayStation 2 and PSP successors. Same idea, more header,
support for several images and palettes in one file.

Beyond Sony the names change and the shape does not: a magic number, a header
with width, height and depth, a palette, and pixel data. Engine-specific formats
from the PC era work the same way.

Why this matters for a translation: title screens, menus and anything with words
painted into the artwork are pictures, not text. Translating them means
extracting the image, editing it in a normal graphics program, and putting it
back — which requires reading the header correctly, and writing it back exactly.

### Read more

→ **[Guida all'estrazione e all'inserimento di TIM modificate](https://romhacking.it/doc/view/id/17)** (Dull) — the TIM format handled end to end.

→ **[Modificare la grafica RAW nei giochi PSX](https://romhacking.it/doc/view/id/16)** (Dark Schneider) — when the picture is not in a container at all.

## Recognize

Look for the magic number at the start of a file, or repeated through a larger
archive. TIM begins with `10 00 00 00`. Others use four printable characters.

If the container is inside an archive, the magic gives you a way to find every
image at once: scan for it and treat each hit as a file start. Where the archive
gives sizes, cross-check — a magic that appears at an offset the index does not
list is a coincidence, or a picture embedded inside another file.

## Analyze

Read the header and check it against the file size:

```
expected = header_size + palette_entries * 2 + width * height * bits_per_pixel / 8
```

If that lands on the file's length, or on it plus a small padding, you have read
the header correctly. If not, one field is being misread — most often the width,
because of the video-memory units.

Watch for palettes stored separately. Several images sharing one CLUT is common,
and an image extracted without its palette is a picture in the wrong colours,
which looks like a decoding error and is not.

## Implement

Convert to PNG for editing and back for insertion. The conversion must preserve
the **palette order**: a graphics program will happily reorder or deduplicate
palette entries, and the resulting file draws correctly on your screen and
wrongly in the game, because the game's tiles index by position.

Where the image must go back at its original size — which is most of the time —
the constraint is the pixels, not the file: the same dimensions and the same
colour depth. Only the pixel values change.

## Verify

Round-trip before editing: extract and reinsert untouched, and the file must be
identical. This is the check that catches misread headers, padding you did not
notice, and palette reordering — all of which produce a plausible picture and a
broken file.

Then look at it in the game.

SOURCES: Guida all'estrazione e all'inserimento di TIM modificate nell'immagine di un gioco — Dull — https://romhacking.it/doc/view/id/17 · Modificare la grafica RAW nei giochi PSX — Dark Schneider — https://romhacking.it/doc/view/id/16 · Everything You Have Always Wanted to Know about the Playstation — Joshua Walker — https://romhacking.it/doc/view/id/49
