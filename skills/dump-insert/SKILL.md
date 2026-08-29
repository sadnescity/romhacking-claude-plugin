---
name: dump-insert
description: Takes text out of a game into a file a translator can actually work in, and puts it back reporting every overflow instead of truncating. Covers the readable script format, when to prefer TSV or PO instead, and the untouched-cycle gate. Use when extracting text for translation, reinserting it, or choosing the working format for a project.
---

# Dump and Insert

## What this is

The two operations at the centre of a translation: get the text out into a file
someone can edit, and put the edited file back into the game.

They sound mechanical and they are, but the shape of the file in the middle
decides how good the translation can be. That file is read by a **human being**,
often not the person who did the hacking, often months later, frequently someone
who has never opened a hex editor. What they can see, they can get right; what
is hidden from them, they will get wrong.

The thing most worth making visible is **length**. Game text lives in a window
of fixed width and fixed rows, and Italian runs longer than English, so a
translator works against a limit at every line — and can only do that if the
file shows where the lines break and how much room there is.

The other half is the return trip. Reinsertion is where the constraints bite: a
line that is two bytes too long has to go somewhere, and the honest answer is
never to cut it silently. A dumper and an inserter that quietly truncate produce
a translation that is missing a line nobody notices until someone replays that
scene, a year later, in a released patch.

So this chapter is really about three things: a readable intermediate format, a
reinsertion that reports rather than truncates, and telling the translator the
budget **before** they write instead of after.

### Read more

→ **[Dumping, questo sconosciuto](https://romhacking.it/doc/view/id/6)** (Dark Schneider) — the dump/reinsert cycle from first principles.

→ **[Guida alle traduzioni parte I, §4](https://sadnescity.it/guide/guidasad_base.php)** (SadNES cITy) — dumping and reinsertion with pointer recalculation.

## Recognize

You are ready to dump when the table round-trips and the control codes are
mapped. Dumping earlier produces a script that looks fine and reinserts wrong.

## Analyze

### A format for the person who reads it

The cost of an unreadable script is not aesthetic: it produces translations
that do not fit, lose control codes, and break the line structure the game
expects. Compare the same two strings.

```
#0000 @0x8A2C
[QUOTE_OPEN]Welcome, traveller![C_FD]The inn is full tonight.[C_FC]
#0001 @0x8A45
[C_60][C_FD]You have no money.[C_FC]
```

and:

```
[#0]
<QUOTE_OPEN>Welcome, traveller!
The inn is full tonight.<C_FC>

[#1]
<C_60>
You have no money.<C_FC>
```

Same bytes. The second is readable because of four choices, and each one earns
its place.

### The four choices

**The game's line break is a real line break.** This is the one that matters
most. A translator writing Italian needs to see how long each line is, because
the window is fixed and Italian runs longer than English. Leaving the break as
`<CODE>` inline hides exactly the thing they have to work against.

**The marker is quiet and on its own line.** `[#0]`, not `#0000 @0x8A2C`. The
offset is your business, not the translator's; it goes in the project state
where it belongs. Use **the game's own string id** when it has one, so a bug
report saying "string 214 is wrong" points at something.

**Codes are `<ANGLED>` while the marker is `[SQUARE]`.** Two different kinds of
thing, two different shapes, no ambiguity about what may be edited.

**A blank line between entries.** Costs nothing, and turns a wall into a list.

### A dump without a space plan is half a dump

**Never hand over a script without telling the translator how much room they
have and what happens when they exceed it.** Otherwise they write the whole
translation and find out at reinsertion, when every line is already written and
every choice already made.

Three questions, answered in the header:

```
# You have 0 bytes of headroom: the translation of this block must fit in 15448 bytes.
# Entries may move and grow: recompute the pointers (table at 0x8012) after any change.
# There is no room left here, but 65536 bytes are free at 0xC010: this block can be relocated there.
```

The second line is not the same for every block, and the difference decides what
a translator may do:

| Addressing | How entries are reached | What may change |
|---|---|---|
| **pointed** | a pointer table | entries may move **and** grow; recompute the pointers |
| **sequential** | the game walks separators or terminators | any entry may resize; **only the block total matters** |
| **fixed** | hardcoded offsets in the code | nothing may move; each entry keeps its size, or the code gets patched |

Work it out per block, not per game: dialogue reached through a pointer table
and item names reached by counting separators can sit in the same ROM, with
different rules for each.

```python
plan = budget.plan(data, "dialogue", start, end, used,
                   addressing=budget.POINTED, pointer_table=table,
                   search=(free_region_start, free_region_end))
dump.write_script(entries, path, budget=plan)
```

`budget.plan` also looks for somewhere to relocate to. When headroom is zero —
which is the normal case, because original scripts fill their space — the answer
is relocation, and when there is nowhere to relocate to the answer is expansion.
Say which, in the header, before anyone writes a line.

### The header is not decoration

Three or four lines that answer what a translator asks on opening the file:

```
# game.nes — dialogue, 298 strings
# [#n] is the string id. Leave the markers alone.
# A line break here is a line break in the game.
# Leave the <CODES> alone: they are the game's own formatting.
```

Add a line for anything peculiar in *this* file — "seven of these carry no
letters, they are glyph indices: leave them as they are" — because peculiarities
discovered by surprise get edited by mistake.

### When another format is better

The marked script is the default because most game text is prose. Two cases
where it is not:

| Format | Use it for | What it buys | What it costs |
|---|---|---|---|
| **marked script** | dialogue, anything read as sentences | the shape on screen is the shape on the page | nothing for prose; awkward for lists |
| **TSV** | item names, spells, places, monsters — things read as a **set** | one row each, a length column, and a `says` column for notes: this is where a glossary starts | line breaks become escapes; unreadable for long text |
| **PO (gettext)** | projects using a CAT tool | translation memory, fuzzy matching, glossary checks, and translators who already own the workflow | the game's line breaks become `\n` inside quoted strings — the readability you just bought is spent |

Offer the choice rather than imposing one. A team with a CAT tool and a
terminology database wants PO; a lone translator wants the script; both want TSV
for the item list. Nothing stops a project from using all three for different
parts, and most large ones do.

## Implement

```python
entries = dump.dump_block(data, table, start, end,
                          end_token="[C_FC]", newline_token="[C_FD]")
dump.write_script(entries, "dialogue.txt",
                  source="game.nes", title="dialogue",
                  notes=("block 0x08038-0x0BC90",))

entries = dump.read_script("dialogue.txt")
rebuilt, overflow = insert.insert_block(data, table, entries, start, end,
                                        newline_token="[C_FD]")
```

**Naming the newline token is what turns the dump readable.** Until you know
which code it is, dump anyway and read the result: the code that appears where
sentences break is the one.

**The terminator is a property of the block, not of the game.** Dialogue may end
entries with one byte while item names are separated by another. Record it per
block; a single global terminator silently produces one enormous entry for the
block that does not use it.

**Bytes after the last terminator are kept** as a final entry. Dropping them
makes the pipeline lossy, and lossy fails the gate.

`insert_block` **never truncates**. What does not fit comes back as a list
naming the entry, the bytes needed and the bytes available. `measure()` gives
the same numbers before you touch the ROM at all — useful for telling a
translator which lines are already too long.

## Verify

The gate of phase 2, on the real thing:

```python
rebuilt, overflow = ...   # dump and reinsert every block, unmodified
assert not overflow
assert hashlib.sha1(rebuilt).hexdigest() == hashlib.sha1(original).hexdigest()
```

That single comparison exercises the charset, every control code's parameter
count, the block boundaries and the terminators at once.

**Changing the format is a change to the pipeline**: rerun the gate after it.
Turning a control code into a real newline and back is exactly the kind of edit
that looks harmless and is not.

SOURCES: Dumping, questo sconosciuto — Dark Schneider — https://romhacking.it/doc/view/id/6 · Guida alle traduzioni parte I §4 — SadNES cITy — https://sadnescity.it/guide/guidasad_base.php · Table File Format (TBL) — Nightcrawler — https://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt
