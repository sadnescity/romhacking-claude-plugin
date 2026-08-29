# Contributing

The plugin has rules. They are not style preferences: they are what makes it
useful rather than a pile of notes, and **every one is enforced by a test**.
You would find them by running into them, so here they are first.

```bash
python3 -m pytest -q                      # the suite: must be green
python3 -m pytest -m network -q           # the links: before a release

# optional integration on real data (otherwise these tests are skipped)
ROMHACK_TEST_ROM=/path/to/rom.nes ROMHACK_TEST_PROJECT=/path/to/project python3 -m pytest -q
```

---

## The rules

### 1. A skill teaches, it does not only assist

Every theme skill opens with `## What this is`: 250–350 words that explain the
subject **to someone who does not know it**, before any procedure. What a
pointer is and why a translation breaks it. Why DTE exists. What happens when a
planar tile is read as linear.

Games all differ; concepts do not. They are the part that transfers.

> *Enforced by:* `test_the_explanation_comes_before_the_procedure`

### 2. Name the capability, never the product

The sources are up to thirty years old and prescribe programs that no longer
exist. Keep the concept, drop the tool. Not "expand it with that program" but
"add a whole number of banks, update the header, keep the fixed bank last".

**The only exception:** emulators, debuggers, disassemblers, assemblers. Those
are not rewritten; they are used.

A historical tool may be named in two forms only: a note starting with
`Historically:`, and a bibliographic title in `SOURCES:` or in a `→` pointer.

> *Enforced by:* `test_no_tool_is_prescribed`

### 3. The four movements

After the explanation: `## Recognize`, `## Analyze`, `## Implement`, `## Verify`.

- **Recognize** — the signals that tell you this is your case
- **Analyze** — how to study the concrete case, and with what
- **Implement** — what gets produced
- **Verify** — **how to prove it works, in game**

The fourth is what separates this plugin from a book. "Byte-identical
round-trip", "a screenshot from the emulator", "lit pixels counted on the
accent rows" are verifications. "Done" is not.

> *Enforced by:* `test_theme_skill_has_four_movements`

### 4. Sources in two places, for two purposes

`### Read more` closes the explanation and precedes the procedure. Every
pointer says **what you will find there that the skill does not have**:

```
→ **[Title](url)** (author) — the specific reason to go there.
```

`SOURCES:` at the bottom is attribution: where the chapter comes from.

"For more" (or "per approfondire") is rejected by the test as a non-reason,
together with any reason shorter than five words.

> *Enforced by:* `test_a_theme_points_at_its_sources_where_it_explains`,
> `test_every_read_more_says_what_you_will_find_there`,
> `test_the_reasons_are_specific_rather_than_generic`

### 5. Verify, do not remember

Sources make mistakes. The IPS format document (*Specifiche del formato patch
ips*) gives the offset range as 2047 MB: it is three bytes, 16 MB. Before
writing a number or a structure, check it against the real specification — and
when a source is wrong, say so in the skill: it is the most useful thing you can
leave the reader.

The same goes for code examples: if you write one, a test must extract it from
the skill and run it. A wrong example gets copied.

> *See:* `tests/test_lz77_example.py`

### 6. No dead-end references

A skill may name another only if it exists.

> *Enforced by:* `test_no_skill_points_at_one_that_does_not_exist`

### 7. A method, not a diary

The skills teach a method that holds for any game. A game may appear only as a
short example marked as such, never as part of the procedure. No local paths,
no development history, no references to internal documents the reader does
not have.

> *Enforced by:* `test_no_development_traces_or_local_paths`

---

## Adding a skill

1. `skills/<name>/SKILL.md` with `name` and `description` in the frontmatter.
   The description says **when** to load it, not what it contains: it is the
   only thing Claude reads to decide.
2. Add the name to `THEMES` (or `PHASE_SKILLS`) in `tests/roles.py`.
3. Write the explanation, the pointers, the four movements, `SOURCES:`.
4. `python3 -m pytest -q`.

## Adding a script

It lives in `scripts/`, **Python 3 with the standard library only**, and it is
born with its tests. The admission criterion: it embodies an invariant that
holds across games. What holds for one game only belongs in that translation's
repository — the `tooling` skill explains why.

## Changing the method

When a rule changes, two things change: the skill and the test that enforces
it. A rule without a test is a recommendation, and recommendations decay at the
first hurried commit.

## Sources

They are listed in `references/SOURCES.md` with author, URL and what derives
from each. **No third-party text is redistributed**: it is read, verified,
rewritten and cited.

No binaries in the repository: no ROMs, no disc images, no original documents.
Tests on real data receive the ROM and the project through `ROMHACK_TEST_ROM`
and `ROMHACK_TEST_PROJECT`, and report themselves *skipped* when the variables
are not set.
