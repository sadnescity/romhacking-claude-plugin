---
name: glossary
description: Builds the terminology a translation must hold to — names, items, spells, places and recurring phrases — each with the length limit its context imposes. Use before translating dialogue, when the same term appears in several places, or when a name must fit a menu.
---

# Glossary

## What this is

The same word appears in a game hundreds of times: an item in the shop, in the
inventory, in the message that says you found it, in the one that says you
cannot afford it. If it is translated differently in any of them, the player
notices something is wrong without being able to say what.

A glossary is the decision, made once, written down: this English term is that
Italian term, everywhere. It is the difference between a translation and a pile
of translated sentences.

For games it carries a second job that a literary glossary does not: **each term
has a length limit**, and the limit comes from the narrowest place the term
appears. A sword whose name fits comfortably in the dialogue may not fit the
inventory box, and the inventory decides.

Which is why this phase sits *after* the technical ones. You cannot know the
limits until you know how the text is stored, what the window sizes are, and
whether the font is variable width. Deciding terminology first and discovering
the limits later means deciding twice.

There is a third thing worth capturing here, and it is the one that saves the
most argument later: **what a term actually is**. `Fairy Water` is not water
made of fairies. Names composed from parts are the sharpest case — a game that
builds `Copper` + `Sword` breaks in Italian, where the halves swap order — but
any term whose meaning is not obvious from the word deserves a note.

### Read more

→ **[Corso di traduzioni](https://romhacking.it/doc/view/id/5)** (Auryn) — terminology and consistency treated as a discipline rather than a habit.

→ **[Guida completa alla traduzione di ROM in lingua straniera](https://romhacking.it/doc/view/id/1)** (SadNES cITy) — the translation process end to end, glossary included.

## Recognize

Terms that belong in the glossary: characters, places, items, equipment, spells,
enemies, key phrases the game repeats, and the words that appear in the
interface. Anything the player sees more than once.

Terms that do not: ordinary sentences. A glossary of everything is a glossary
nobody reads.

## Analyze

Take the term lists straight from the dump — item names, spells, monsters are
usually contiguous blocks, and the TSV form (see `dump-insert`) is already the
right shape.

For each, find **the narrowest context it appears in**, and its limit in
characters or pixels. That is a real measurement: count the window, or count the
bytes the entry has. Copying the English length is a good default when the
storage is fixed-size, and no substitute for measuring when it is not.

Watch for terms **built from parts**. A game that composes names from two lists
imposes an order the target language may not accept, and the fix is a decision —
translate the halves so the joined result reads correctly, or patch the code
that joins them. Both are legitimate; picking one after the lists are translated
is not.

## Implement

A table, one row per term, with the English, the Italian, the limit, and a note
saying what it is:

```
english      italian        max   says
Copper Sword Spada di rame   14   starting weapon; name joined from two lists
Fairy Water  Acqua fatata    12   item: repels weak enemies
```

Keep it beside the translation and version it. It is the file a second
translator reads first.

## Verify

Every entry has a limit that came from a measurement. Every term in the
translated text appears in the form the glossary decided — grep for the English
term in the finished script and confirm nothing was left behind, then grep for
variants of the Italian term to catch the same thing translated twice.

SOURCES: Corso di traduzioni — Auryn — https://romhacking.it/doc/view/id/5 · Guida completa alla traduzione di ROM in lingua straniera — SadNES cITy — https://romhacking.it/doc/view/id/1 · De-Jap Guide to Translation — DeJap — https://romhacking.it/doc/view/id/9
