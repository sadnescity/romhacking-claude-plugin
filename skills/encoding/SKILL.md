---
name: encoding
description: Phase two of a translation. Establishes how the game stores text — charset, control codes, and any dictionary compression — and does not close until a dump reinserted unchanged reproduces the original byte for byte. Use when the target has been surveyed and the text needs to become readable and writable.
---

# Phase 2 — Encoding

**Precondition:** `recon` passed. You know what the target is and where its
regions are.

**Artifact:** a `.tbl` table plus the control-code map, recorded in
`ROMHACK.md`.

**Gate:** a dump reinserted **without modifications** produces a file identical
to the original. Hash it and compare.

## Why the gate is this one

It is the only check that exercises every assumption at once. If the charset is
wrong the bytes differ; if a control code's parameter count is wrong everything after
it shifts; if two characters collide in the table one silently replaces the
other. All of it fails one hash comparison, and none of it is visible by reading
the decoded text.

## Order of work

1. **`text-search`** — where the text lives, and the boundaries of each block.
2. **`tables`** — the charset, built as a loop: decode, hit an unknown byte, add
   the entry, repeat.
3. **`control-codes`** — the bytes that are not characters, with their parameter
   counts. Neutral labels until each one has been seen acting.
4. **`dte-mte`** — only if the evidence says so. Establishing that a game has no
   dictionary is a valid outcome of this step.

Then the gate.

## Two numbers go in the state file

- `roundtrip: pass|fail` — the gate itself
- `coverage` — the share of bytes explained by real entries rather than `[$HH]`

Both matter. The round-trip passes trivially if every byte is raw hex; coverage
without a round-trip means you can read the text but not write it back. The
phase closes when the round-trip passes **and** coverage is high enough to
translate against — in practice above 95%, with the remainder identified as
control codes rather than mysteries.

## When the gate will not close

The failure names the cause. Diff the original against the reinserted bytes and
look at what changed into what: a systematic `0xNN → 0xMM` across many positions
is a table collision; a one-byte shift from some point onward is a wrong
parameter count; scattered differences in one region only mean that region is
not what you think it is.

Do not weaken the check to move on. The phases after this one all assume it
held.
