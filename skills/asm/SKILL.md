---
name: asm
description: "Patches the game's code when the data alone cannot solve the problem — finding the routine, hooking it without disturbing what works, and verifying that nothing else broke. Use when a limit is enforced by code rather than by data: a print routine that rejects byte values, a hardcoded length, a bank never switched."
---

# Assembly

## What this is

Sooner or later a limit turns out to be written in the game's code rather than
in its data. The print routine refuses byte values above a threshold; a name
field is copied with a hardcoded length of eight; the font is decompressed by a
routine you would rather bypass. No amount of editing data changes any of these.
You have to change the instructions.

That sounds like it requires being a machine-code programmer, and mostly it does
not. The technique that carries you a long way is the **hook**: leave the game's
code alone except for a handful of bytes, replace those with a jump to empty
space, do your work there, and jump back into the original flow. You are not
rewriting the routine, you are inserting yourself into it.

A hook has three properties worth stating plainly, because they are what makes
it safe:

- it fits **exactly** the bytes it replaces, so nothing after it shifts
- it changes behaviour **only** for the cases you name, and every other path
  reaches the original code unchanged
- it returns to where the replaced instructions would have gone

Finding *where* to hook is the real work, and it is not done by reading a
disassembly from the top. You know something about the data — where the text is
stored, where the graphics land in video memory, which byte misbehaves — and you
let the emulator tell you which code touches it. A breakpoint does in seconds
what reading could not do in an afternoon.

### Read more

→ **[Guida all'Assembly](https://romhacking.it/doc/view/id/30)** (UST) and **[L'Assembly in un passo](https://romhacking.it/doc/view/id/15)** (Dark Schneider) — the language itself, if you are starting from nothing.

→ **[Assembly for the SNES](https://ersanio.gitbook.io/assembly-for-the-snes/)** (Ersanio) — a full modern course on 65c816, written for ROM hackers rather than for programmers.

→ **[Intro to ASM Modding & Hooking](http://forums.therockmanexezone.com/intro-to-asm-modding-hooking-t5374.html)** (MGAMERZ) — hooking specifically, at length, on GBA.

→ **[Hacking Mega Man X with ASM modification](https://romhacking.it/doc/view/id/41)** (DarkDreAm) — a worked patch from finding the routine to testing it.

→ **[Neo Geo ROM hacking: digging into MAME traces](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-digging-into-mame-traces/)** (Matt Greer) — reading an execution trace to find the routine you want, on a machine with no debugger worth the name.

## Recognize

You need code when the limit is **enforced by the code**, not by the data. The
signature is a change that is correct in the file and has no effect, or an
effect the data cannot explain.

Typical cases:

- glyph indices above a threshold never reach the screen — a comparison in the
  print routine sends them to the control-code handler
- text longer than N characters is cut, and no pointer says N
- a bank holds what you need and nothing ever switches to it

Before reaching for code: is there data room left? The `space` and `accents`
skills cover that. Code is the answer when the answer is not room.

## Analyze

**Find the routine from the data it touches**, not by reading the disassembly
top to bottom.

| You know | Set a breakpoint on |
|---|---|
| where the text lives | **read** on that ROM range |
| what appears on screen | **write** on the video memory it lands in |
| the byte value that misbehaves | **trace with a condition** on that value |

The conditional trace is the sharpest of the three: it answers "who touches this
byte" without knowing anything else first.

Two traps worth knowing before they cost you an hour:

**The data is often copied to RAM first.** A breakpoint on the ROM then fires
once, early, far from the routine that consumes it. If a read breakpoint on the
text never fires while the text is on screen, the game is reading a copy.

**One game has as many barriers as it has routines touching text**, and this is
the single most expensive lesson in this kind of work.

Menus, dialogue windows, status lines, shop lists, battle messages and name
entry are often separate code paths written at different times by different
people. Patching one and declaring the problem solved is how a translation ships
with a screen nobody tested showing garbage.

Worse: **the second routine rarely looks like the first**. *Example*, two
routines of one small 6502 game enforcing the same limit:

```asm
; dialogue: an explicit comparison
CMP #$80
BCS ControlCodeHandler

; the menu, elsewhere in the same bank, doing the same job
LDA ($9F),Y
BPL Character          ; tests bit 7 directly — no comparison at all
```

Searching the ROM for `C9 80` finds the first and is blind to the second. They
enforce the same rule through different instructions, so **pattern-matching on
what you already found is exactly the wrong instinct**. Search for the *effect* —
who reads this text, who writes that tile — not for the shape of the code.

The discipline that catches them all:

1. **List the contexts** where the thing you changed can appear. Write the list
   down before touching anything: dialogue, menus, shops, battle, status, name
   entry, ending, credits.
2. **Verify each one on screen.** Not by reasoning about shared code — by
   opening that screen and looking.
3. When a context misbehaves, **find its routine from scratch**. Do not assume
   it is the one you already know.
4. **Record which contexts you have checked**, in the project state. Three
   verified out of seven is a number; "seems fine" is not.

Two symptoms tell you that you are standing in front of a second routine: your
patch is provably correct and has no effect, and a breakpoint on your patched
code never fires while the misbehaving screen draws. Both mean the same thing —
this screen never runs your code.

Static search complements this. Looking for the comparison itself is cheap:

```python
re.finditer(rb"\xC9\x80", prg)      # CMP #$80
```

Then confirm the candidate with an execute breakpoint. A match found statically
and never executed is not the routine.

## Implement

**Hook, do not rewrite.** Replace as few bytes as possible with a jump to free
space, do the new work there, and return into the original flow.

*Example* (6502), letting two extra byte values through as characters:

```asm
.org $80F8              ; was: CMP #$80 / BCS $809E   — four bytes
    jmp Dispatch
    nop

.org $BEA0              ; free space found in the same bank
Dispatch:
    cmp #$B2
    beq AsCharacter
    cmp #$BB
    beq AsCharacter
    cmp #$80            ; everything else behaves exactly as before
    bcs AsControlCode
AsCharacter:
    jmp $80FC
AsControlCode:
    jmp $809E
```

**The free space must be in the same bank** the routine runs from, or the jump
lands in whatever happens to be mapped. Look for long runs of a single filler
byte and check the bank, not just the offset.

Write the patch as an `.asm` file and assemble it with `armips` — the plugin
covers the syntax. Hand-assembling a dozen bytes works and is unreadable six
months later.

## Verify

**That the patch runs.** An execute breakpoint on the hook: if it never fires
on the screen you care about, you have patched a routine that is not the one in
play, and everything downstream is guesswork.

**That the intended behaviour changed**, observed on screen.

**That nothing else did.** A hook that widens a comparison changes every value
in the widened range, not only yours. Walk the screens that used those values.

SOURCES: Assembly for the SNES — Ersanio — https://ersanio.gitbook.io/assembly-for-the-snes/ · Intro to ASM Modding & Hooking — MGAMERZ — http://forums.therockmanexezone.com/intro-to-asm-modding-hooking-t5374.html · Guida all'Assembly — UST — https://romhacking.it/doc/view/id/30 · L'Assembly in un passo — Dark Schneider — https://romhacking.it/doc/view/id/15 · Hacking Mega Man X with ASM modification — DarkDreAm — https://romhacking.it/doc/view/id/41 · Game Boy Assembly Hacking — DarkDreAm — https://romhacking.it/doc/view/id/34
