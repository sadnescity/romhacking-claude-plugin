---
name: project-state
description: Reads and updates ROMHACK.md, the state file of a translation project. Use whenever you need to know which phase a project is in, which gates have passed, what the table covers, or when recording that a gate passed. Never mark a gate passed without evidence.
user-invocable: false
---

# Project State

A translation takes months and dozens of sessions. `ROMHACK.md` is what makes
session forty start from where session thirty-nine ended instead of from
questions the user has already answered.

## Where it lives

In the project directory, next to the data, **committed to version control**.
It is Markdown with a YAML frontmatter block: a person reads it, a diff shows
what changed, and `scripts/romhack_state.py` parses it.

Read and write it through `romhack_state.py`, never by hand-editing the
frontmatter:

```python
import sys; sys.path.insert(0, "${CLAUDE_PLUGIN_ROOT}/scripts")   # the plugin's scripts
import romhack_state
state = romhack_state.State.load("ROMHACK.md")
state.phase                       # 'encoding'
state.gate_passed("recon")        # True
state.pass_gate("encoding", evidence="round-trip identical on 0x8A2C-0x8B40")
state.save("ROMHACK.md")
```

## The schema

```yaml
---
target:
  file: game.nes
  platform: nes
  sha1: <hash of the untouched copy>
  size: 81936
phase: encoding
toolchain: [mesence]
gates:
  recon:    { passed: "2026-08-30", evidence: "inventory: 100% classified" }
  encoding: { passed: null, blocking: "round-trip not yet identical" }
table:
  file: game.tbl
  entries: 218
  roundtrip: { status: pass, sample: "0x8A2C-0x8B40", last_run: "2026-08-30" }
control_codes: { mapped: 11, unknown: 3 }
pointers:
  tables:
    - { offset: 107520, count: 512, width: 2, endian: little, base: 32768 }
blocks:
  - { name: dialogue, offset: 35372, end: 35648, dumped: true, reinserted: false }
---

## Working notes
Free text: hypotheses, dead ends, decisions and why they were taken.
```

The seven phases, in order: `recon`, `encoding`, `accents`, `space`,
`graphics`, `glossary`, `translation`.

## The gate rule

**A gate passes with a date and evidence, or it does not pass.**

Evidence is a command that was run or an observation that was made — never an
assertion. `pass_gate` refuses an empty one, and that refusal is deliberate:
the whole method rests on the difference between *declaring* a phase finished
and *proving* it.

Examples of real evidence:

- `encoding`: `sha1 of the untouched dump/insert cycle matches the original`
- `accents`: `work/proof/accents-shop.png shows à è é ì ò ù È on screen`
- `space`: `expanded ROM boots and reaches the extended block`

Examples of what is **not** evidence: "done", "should work", "the code looks
right", "I added the tile".

## When the file and reality disagree

Reality wins. Re-run the verification, then update the file. A state file that
claims a gate passed when it does not is worse than no state file at all,
because it moves the project forward on a false floor.

## Unknowns are counted, never hidden

`control_codes.unknown`, the `unknown` share of the inventory, blocks not yet
reinserted: these numbers stay visible. A project that knows the size of its
own ignorance can plan; one that rounds it to zero cannot.
