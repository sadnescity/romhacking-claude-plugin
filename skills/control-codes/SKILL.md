---
name: control-codes
description: Identifies and maps the control codes that format in-game text — line break, wait for input, pause, new window, colour, name insertion, end of string — including how many parameter bytes each consumes. Use when a text block contains bytes that are not characters, or when reinserted text formats wrongly.
---

# Control Codes

## What this is

Open a game's script and among the letters you find bytes that are not letters.
They tell the text engine what to *do*: break the line here, wait for the player
to press a button, clear the window, switch colour, insert the hero's name,
pause for half a second, stop.

These are **control codes** — you will also see them called text opcodes, though
the term invites confusion with a processor's instructions, so this skill says
control code throughout. They are why a game's text is not a list of strings but
a small program: `"Welcome, traveller!<LINE>The inn is full tonight.<WAIT><END>"`
is two sentences and three instructions.

The families you meet everywhere, whatever the machine:

| Kind | What it does |
|---|---|
| end of string | this line is over |
| line break | continue on the next row of the window |
| wait for input | hold until the player presses a button |
| new window / clear | start a fresh box |
| insert name / number | splice in something the game knows at runtime |
| colour, speed, pause | presentation |
| branch | pick a continuation from a flag |

Two things make them matter for a translation more than they look.

**Length.** Some codes take parameters — a colour index, a delay, a name slot —
and those bytes follow the code. If you record a code as taking no parameters
when it takes one, the leftover byte decodes as a letter and everything after it
shifts by one. The text becomes almost-right, which is much harder to debug than
completely wrong.

**Line breaks are not cosmetic.** The window is a fixed number of characters
wide and a fixed number of rows tall. Italian runs longer than English for the
same sentence, so a translation that keeps the original breaks overflows the box
— and a translation that removes them gets whatever the engine does when a line
is too long, which is sometimes wrapping and sometimes garbage.

### Read more

→ **[Guida alla modifica dei byte a capo](https://romhacking.it/doc/view/id/46)** (Random Stones) — line-break codes specifically, and what changing them does to a window.

→ **[Guida alle traduzioni parte I](https://sadnescity.it/guide/guidasad_base.php)** (SadNES cITy) — control codes in the context of the whole text system.

## Recognize

A byte is a control code, not a character, when it behaves structurally rather than
lexically:

- it appears at ends of lines or strings, never inside words
- it never sits between two letters in a way that would form a word
- its frequency matches a structural role, not a letter distribution
- decoding it as a letter produces text that is *almost* right

Counting is a strong tool. *Example:* one byte appears 228 times at the start
of sentences, and two others 48 and 179 times at their ends — 227 in total.
Opening and closing quotation marks, established by arithmetic before running
anything.

## Analyze

Two ways, in this order.

**Watch it act.** Put the text on screen, and compare what the game does with
where the byte sits. This settles most of them and costs minutes.

**Break on the reader.** When observation is ambiguous, set a read breakpoint on
the text block and look at the routine that consumes the byte: how it dispatches
tells you both the meaning and, crucially, **how many bytes it reads after** the
control code. Use the emulator for the platform — see `toolchain`.

## Implement

In the table, a control code is `$HH=[Label],p1,p2` — one raw byte per parameter.

**Use neutral labels until you have seen the control code act.** `[C_FC]` says "byte
FC, meaning unknown". `[END]` says you know. If it later turns out to be "wait
for input", every decision that leaned on the name was built on a guess. Rename
when you have the evidence, and the diff will show you exactly what changed.

## Verify

Two checks, both required:

1. **Every mapped control code has been observed acting.** Not inferred from position.
2. **The unmapped ones are counted**, in `ROMHACK.md` under
   `control_codes: {mapped: N, unknown: M}`. Three unknown ones is a number
   you can work with; "mostly mapped" is not.

Then the phase gate: a dump reinserted unchanged produces a byte-identical
file. If a control code's parameter count is wrong, this fails — which is the point.

SOURCES: Guida alla modifica dei byte a capo — Random Stones — https://romhacking.it/doc/view/id/46 · Guida alle traduzioni parte I — SadNES cITy — https://sadnescity.it/guide/guidasad_base.php · Table File Format (TBL) — Nightcrawler — https://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt
