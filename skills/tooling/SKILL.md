---
name: tooling
description: Writes the tool that does not exist instead of hunting for one that no longer runs. Use when a source prescribes a program that is gone, when a game's format is proprietary and nothing handles it, or when a seed script needs adapting to a specific target.
---

# Tooling

## What this is

The literature of this craft spans thirty years, and most of it says "open the
file in X" where X is a program that no longer runs. That is not a flaw in the
documents: when they were written, the tool *was* the method, because writing
your own meant a compiler and a weekend.

It does not any more. A dumper that reads a table, follows a pointer table and
handles DTE is a couple of hundred lines. An extractor for a proprietary archive
is less. Written today, for the one game in front of you, it is also *better*
than the general-purpose tool of 1999, because it knows that game's quirks
instead of covering the average of a hundred.

So the useful reflex when a source prescribes a program is to read past the
program and take the **capability**. A guide that says "expand the ROM with
this utility" knows something worth having — *add whole banks, update the
header, keep the fixed bank last* — and the utility's name is not it. Write down
the capability and forget the name.

There is one class of exception, and it is worth being precise about. Emulators,
debuggers, disassemblers and assemblers are not reproducible on demand — an accurate
emulator is decades of hardware reverse engineering by many people, and nothing
you write this afternoon replaces it. Use what exists. Everything else, write.

The other half of this chapter is where the tool should live. Not in a general
toolbox: **in the repository of the translation**, beside the data it
understands, versioned with it. A finished translation ends up with its own
small toolchain, tuned to that game, and that is the right outcome — it is how
anyone can rebuild the patch two years later.

### Read more

→ **[Awesome Rom Hacking](https://github.com/romh-acking/Awesome-Rom-Hacking)** — a maintained list of what already exists, worth checking before writing anything.

## Recognize

Two situations lead here:

- a source says "open it in X" and X is a DOS binary, a 32-bit Windows tool, or
  simply gone
- you need a **capability** nothing covers, because the format belongs to that
  one game

Both have the same answer.

## Analyze

Separate three layers before writing anything:

| Layer | Example | What to do |
|---|---|---|
| **Concept** | pointers, DTE, bitplanes, sector geometry, entropy | keep it — this is what the source is really worth |
| **Format** | TBL, IPS, BPS, PPF, xdelta, ISO 9660, PNG | respect it exactly: other people's tools must read your output |
| **Tool** | whichever program the document names | discard it and write what you need |

For the exception — emulators, debuggers, disassemblers — see `toolchain`.

## Implement

Start from the closest seed in `scripts/`: `tbl.py`, `relsearch.py`,
`dump.py`/`insert.py`, `budget.py`, `pointers.py`, `ines.py`, `inventory.py`,
`dte.py`, `entropy.py`, `tilepng.py`, `mkpatch.py`, `romhack_state.py`. They are **reference implementations, not products** — each one
carries an invariant that holds everywhere, and the specifics of any given game
are yours to add.

The scripts live in `${CLAUDE_PLUGIN_ROOT}/scripts`: copy the ones you need
into the project's repository and adapt them there, next to the data they
understand, rather than editing the plugin. Every tool is born with its test.
Not after.

## Verify

**The round-trip rule: before a tool produces anything new, it must reproduce
the original bit for bit.**

An extractor must rebuild the archive it just unpacked. A decompressor must have
a compressor that regenerates the original bytes. A converter must survive a
there-and-back trip. A tool that has not passed this is not ready to touch real
data, however plausible its output looks.

The reason is not purity. A tool that is subtly wrong produces files that mostly
work, and the damage shows up in a scene nobody replays for a month.

SOURCES: no single third-party document: this is the plugin's own rule separating concepts, formats and tools · Awesome Rom Hacking — https://github.com/romh-acking/Awesome-Rom-Hacking
