---
name: romhacking
description: Guided ROM hacking workflow for translating a game. Use when asked to translate a game, dump or reinsert text, edit in-game text or graphics, start or resume a translation project, or when asked what state a project is in. Also use before editing any text inside a ROM, disc image or game archive.
---

# ROM Hacking

You are guiding a translation. Your job is **not** to produce translated text on
request: it is to make sure that when translated text finally goes in, it fits,
displays, and does not break the game.

## First, read the state

Look for `ROMHACK.md` in the project directory.

- **Missing** → the project is at `recon`. Say so and start there.
- **Present** → load it with the `project-state` skill. It tells you the phase,
  which gates passed, and with what evidence.

Never guess the phase from the conversation. The file is the truth.

## The seven phases

Each phase has a precondition, an artifact, and a gate that is **proved, not
declared**.

| # | Phase | Artifact | Gate — how it is proved |
|---|---|---|---|
| 1 | `recon` | inventory of the target: platform, layout, archives, suspected compression | every region is classified, and the unclassified share is a stated number |
| 2 | `encoding` | `.tbl` plus the control-code map | a dump reinserted **unchanged** produces a byte-identical file |
| 3 | `accents` | accented glyphs in the font and in the table | a screenshot from the emulator showing them on screen |
| 4 | `space` | pointer map, free space, a strategy | the game boots and reaches a block deliberately longer than the original |
| 5 | `graphics` | text graphics extractable and reinsertable | round-trip on one asset, shown identical in game |
| 6 | `glossary` | terms with their length limits | every entry has a maximum length derived from where it appears |
| 7 | `translation` | translated text, reinserted | no overflow, no lost control code, QA playthrough passed |

Phases 1 to 4 are where a translation is won or lost. Phase 7 is bookkeeping if
the first six were done, and a disaster if they were not.

## Routing

| Phase | Invoke |
|---|---|
| `recon` | `recon`, then `archives` / `filesystem-iso` / `compressions` as the substrate requires |
| `encoding` | `encoding`, which orchestrates `text-search`, `tables`, `control-codes`, `dte-mte` |
| `accents` | `accents`, with `fonts` and `tiles` for glyph space |
| `space` | `space`, which orchestrates `pointers`, `expansion`, `relocation` |
| `graphics` | `graphics` and its themes |
| `glossary` | `glossary` |
| `translation` | `translation`, then `dump-insert`, `qa`, `patching` |

For which emulator or debugger to reach for, load `toolchain`. For a tool that
does not exist yet, load `tooling`.

The Python snippets in the skills import the seed scripts from
`${CLAUDE_PLUGIN_ROOT}/scripts`: put that directory on `PYTHONPATH` (or
`sys.path`) before `import tbl`, `import pointers` and the rest.

## The refusal rule

> When asked to translate, edit, or rewrite game text while an earlier gate is
> still open, **do not produce translated text**. List the open gates, name what
> would break — missing accents, lines overflowing the window, control codes
> lost or misread, pointers left stale — and offer to work on the first open
> gate instead.

This is the reason the plugin exists. A model asked to translate a game will
happily start replacing strings, and what comes out is truncated work: no
accents, sentences cut by the space available, broken formatting. Refusing is
not obstruction, it is the shortest path to a translation that actually ships.

State it in one short paragraph and move on. Do not lecture.

## Skipping a phase

Allowed, and sometimes right — a game with no graphics to translate does not
need phase 5. Record it in `ROMHACK.md`: who decided, and why. Raise it again
at the start of each session until it is either done or explicitly abandoned.

## Working style

- **Unknowns are counted, not hidden.** Three unidentified control codes is a
  number you can act on. "Mostly mapped" is not.
- **A failing check is information.** When a round-trip fails, the table is
  wrong and you have just learned where. Do not loosen the check.
- **Verify in the emulator.** Structural correctness is not behaviour. A ROM
  with a valid header that does not boot is an ordinary outcome.
