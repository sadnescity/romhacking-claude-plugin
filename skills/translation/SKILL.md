---
name: translation
description: The constraints translated game text must satisfy — length, line breaks, preserved control codes, terms from the glossary — and how to check them before reinsertion rather than after. Use when translating a dumped script, or when reinserted text overflows or formats wrongly.
---

# Translation

## What this is

The phase everyone thinks the whole project is, and the one that goes quickly
when the previous six were done.

This skill is not about how to translate well: that is a craft of its own and it
belongs to the translator. It is about the **constraints** game text has and
ordinary text does not, because those constraints are invisible in a word
processor and fatal at reinsertion.

There are four:

**Length.** The text goes back into a space that is measured. Sometimes the
space is one entry's worth of bytes, sometimes a whole block's, sometimes a
window's width in pixels — and which one applies is a property of how the game
stores that text (see `dump-insert`).

**Line breaks.** The window is a fixed number of rows, and the game does not
usually reflow. A translated line that runs long does not wrap politely; it
overflows the box or vanishes.

**Control codes.** The markers in the script are instructions: wait for a
button, insert the hero's name, change colour, end. Delete one and the game
stops waiting, or runs two messages together, or reads past the end of the
string.

**Terminology.** The same term, the same way, every time. See `glossary`.

And one thing that is not a constraint but decides whether the constraints can
be met: **Italian runs about 10–20% longer than English** for the same content.
That is not a problem to solve at the last line — it is a budget to plan for at
the first.

### Read more

→ **[Corso di traduzioni](https://romhacking.it/doc/view/id/5)** (Auryn) — the longest Italian treatment of translating games specifically.

→ **[Mini guida alla traduzione](https://romhacking.it/doc/view/id/54)** (Macchianera) — short, practical, good as a checklist.

→ **[De-Jap Guide to Translation](https://romhacking.it/doc/view/id/9)** (DeJap) — the English-language classic, from a group that shipped a great many of these.

## Recognize

You are ready to translate when the script dump exists, the glossary is decided,
and each block's budget is written in the file's header. If any of those is
missing, translating now means translating twice.

## Analyze

Read the header of the file you were given. It should tell you how many bytes
the block has, whether entries can move, and where there is room if they cannot.
If it does not, ask — that information exists and someone chose not to write it
down.

Then look at the shape of the text. In a well-made dump the game's line breaks
are real line breaks, so the lines on your screen are the lines on the player's.
Work against that shape rather than translating into a paragraph and breaking it
afterwards.

## Implement

Translate entry by entry, keeping the markers exactly as they are. Move them
only when the Italian sentence genuinely needs the break somewhere else — and
when you do, count the resulting lines against the window.

Where the Italian will not fit, the options in order: say it shorter (usually
possible, and usually better prose); use a shorter term from the glossary if one
is defensible; ask for more space (see `space`) — which is a real answer, not a
defeat, and the reason the space phase came first.

What not to do: silently drop a control code to save two bytes, or truncate a
line and hope it is a scene nobody replays.

## Verify

Before reinsertion, mechanically:

- every entry still has its terminator, and no marker was lost
- no entry exceeds its budget — `insert.measure` gives the numbers without
  touching the ROM
- glossary terms appear in the decided form

Then reinsert and **look at it in the game**. Text that measures correctly and
reads badly on screen is common: a line that is technically within the window
but leaves one word alone on the last row, a name that collides with a number.
Only the screen shows that.

Then `qa`.

SOURCES: Corso di traduzioni — Auryn — https://romhacking.it/doc/view/id/5 · Guida completa alla traduzione di ROM in lingua straniera — SadNES cITy — https://romhacking.it/doc/view/id/1 · Mini guida alla traduzione — Macchianera — https://romhacking.it/doc/view/id/54 · De-Jap Guide to Translation — DeJap — https://romhacking.it/doc/view/id/9
