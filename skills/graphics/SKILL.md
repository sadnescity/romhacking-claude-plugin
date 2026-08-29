---
name: graphics
description: Phase five of a translation. Extracts, edits and reinserts the pictures that contain words — title screens, menus, signs — and extends the font with the characters the target language needs. Use when the text is done and words remain painted into the artwork.
---

# Phase 5 — Graphics

**Precondition:** `encoding` passed. The text pipeline works.

**Artifact:** every graphic containing words extracted and reinsertable, and the
font carrying the characters the translation needs.

**Gate:** round-trip on one asset — extracted, reinserted untouched, byte
identical — and the game shows it unchanged. Then the edited version appears
correctly in game.

## What belongs to this phase

Words that are pictures rather than text: the title screen, menu labels drawn as
artwork, signs, the "GAME OVER" that turns out to be a bitmap. They are invisible
to every text search and they are the last thing anyone notices is untranslated.

And the font, because a translation needs characters the original never had.
That work is `accents` and `fonts`; this phase is where it lands if it was not
done earlier.

## Order of work

1. **`tiles`** — how graphics are stored on this machine, and getting a viewer
   to show pictures instead of noise.
2. **`palettes`** — which colours, and which index is which. Do this before
   editing anything: it is where an invisible glyph comes from.
3. **`fonts`** — find the font, count its free slots, extend it.
4. **`vwf`** — only if the game has variable width, or you need one to fit.
5. **`image-formats`** — for disc-era games where pictures are files rather than
   raw tiles.

## What makes this phase different

Everything else in a translation is verifiable by arithmetic. Graphics are
verifiable only by looking, and the eye is easily satisfied: a picture that is
almost right looks right. Two habits compensate.

**Round-trip everything before editing anything.** Extract and reinsert
untouched: identical or you have misread the format, and any edit made on top of
a misreading is wasted.

**Measure what you cannot trust yourself to see.** Small details — an accent, a
one-pixel misalignment, a colour that renders as background — are exactly the
size at which you see what you expect. Count pixels.

## Verify

Round-trip on every asset, not a sample. Then the game, on the screen where each
one appears — including the ones that need a save state to reach.
