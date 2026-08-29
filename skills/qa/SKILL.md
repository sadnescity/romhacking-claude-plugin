---
name: qa
description: Testing a translated game systematically — the failure classes specific to this work, how to cover them without playing everything twice, and what to record. Use before releasing a patch, or when deciding what still needs testing.
---

# QA

## What this is

A translated game fails in ways an ordinary build does not, and most of them are
invisible until someone reaches one particular screen.

The failures have a shape worth knowing in advance, because it tells you what to
look for rather than hoping to stumble on it:

**Overflow.** Text longer than its window. Shows as a box drawn over the
scenery, text running off the edge, or a line that vanishes.

**Lost or wrong control codes.** A message that does not wait for the button and
flashes past; two messages running together; text in the wrong colour; a name
slot showing garbage.

**Pointer damage.** The wrong line for the situation — the shopkeeper saying
what the king should. Means something moved and its pointer did not.

**Missing glyphs.** A blank or wrong character where an accent should be,
usually in the one context whose font you did not extend.

**Regressions from an expansion.** The game boots and reaches the first town,
then crashes in the place that uses the bank you moved.

**Untranslated remnants.** A block nobody dumped: a menu, a game-over screen,
the credits.

Notice that all of these are consequences of the earlier phases. QA does not
find translation mistakes — it finds *hacking* mistakes, in the places the
hacking did not think about.

### Read more

→ **[Bugfix delle patch](https://romhacking.it/doc/view/id/32)** (Psyco) — what goes wrong after release, which is the best guide to what to test before it.

## Recognize

You are ready for QA when the patch applies and the game boots. You are *done*
with QA when the contexts list is covered, not when you feel confident.

## Analyze

**Write the context list before testing.** Every place text appears, listed on
paper: dialogue, menus, shops, battle messages, item descriptions, name entry,
save and load screens, the game-over, the ending, the credits. Then test against
the list.

This matters because the untested context is never the one you were worried
about. A game has perhaps a dozen text systems and you will naturally exercise
three of them by playing.

**Use save states to reach the hard parts.** Playing to the ending to check the
credits is a day; a save state in front of the final boss is a minute. Keep a
set of them, one per context, and reuse them for every build.

**Force the extremes.** The longest name the game allows, the widest item in the
inventory, a message with every accented character. Average text passes; the
edges are where the box overflows.

## Implement

Test in passes, cheapest first:

1. **Mechanical**, before running anything: no entry over budget, no missing
   terminator, no lost control code, every glossary term in its decided form.
   Scripted, so it runs on every build.
2. **Context sweep** with save states: one visit to each item on the list.
3. **Playthrough**, once, near release, for what the sweep cannot reach —
   pacing, sense, and the scenes nobody thought to list.

Record what you tested and on which build. "It worked last month" refers to a
build that no longer exists.

## Verify

The context list is covered, each with the build it was checked against. Bugs
found are fixed *and* their context re-tested — a fix to a pointer table is
exactly the kind of change that breaks the block next to the one you fixed.

And the last check, which costs nothing and catches an embarrassing class of
error: apply the patch to a clean copy, on another machine, following your own
instructions, and play the first ten minutes.

SOURCES: Bugfix delle patch — Psyco — https://romhacking.it/doc/view/id/32 · Corso di traduzioni — Auryn — https://romhacking.it/doc/view/id/5 · Guida completa alla traduzione di ROM in lingua straniera — SadNES cITy — https://romhacking.it/doc/view/id/1
