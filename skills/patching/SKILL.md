---
name: patching
description: Distributing a translation as a patch — choosing between IPS, BPS, PPF and xdelta, building one, and verifying that applying it reproduces exactly the build you tested. Use when a translation is ready to release, or when deciding which patch format a project should target.
---

# Patching

## What this is

You cannot distribute the game. It belongs to whoever made it, and shipping a
translated copy is shipping their work. What you can distribute is the
**difference** between their file and yours: a patch. Players apply it to the
copy they already own.

This is not a technicality. It is the arrangement that has allowed fan
translation to exist for thirty years, and it shapes the tooling: every format
below describes changes, never content.

Formats differ in one important way — **what they record**.

**IPS** records "at offset X, write these bytes". Simple, universal, and it
cannot describe a file whose layout changed: shift everything by one byte and
the patch becomes a list of thousands of records. Its offsets are three bytes,
which caps it at 16 MB. (Some Italian documentation states 2047 MB; that is an
error — three bytes reach 0xFFFFFF.)

**BPS** records a delta with checksums of both source and target. It handles
insertions properly, refuses to apply to the wrong file, and has no practical
size limit. The modern default for cartridge games.

**PPF** was made for PlayStation disc images and records byte replacements at
fixed offsets, like IPS but larger. It shares IPS's blindness to layout changes,
which matters more on a disc, where rebuilding an image moves everything.

**xdelta** is a general-purpose binary delta. It handles moved and inserted data
efficiently, which makes it the practical choice for disc images and anything
where the whole file was rebuilt.

Choose by what your project does to the file: replacements in place → IPS or
PPF; a rebuilt image → xdelta; a cartridge with expansion → BPS.

### Read more

→ **[Specifiche del formato patch ips](https://romhacking.it/doc/view/id/39)** (DarkDreAm) — the IPS format written out. Note the size limits given there are wrong: offsets are three **bytes**, not bits.

→ **[Patch .ips](https://romhacking.it/doc/view/id/18)** and **[Patch .ppf](https://romhacking.it/doc/view/id/19)** (Dull) — using both formats in practice.

→ **[Guida alle traduzioni parte III, §7](https://sadnescity.it/guide/guidasad_fs.php)** (SadNES cITy) — PPF and xdelta for disc images, and when each one fails.

## Recognize

You are ready to build a patch when the build you intend to release exists, has
been played, and you can name its hash. Not before: a patch is generated *from*
a finished build, and rebuilding after generating one invalidates it silently.

## Analyze

Two properties decide whether a patch is safe to release.

**Which original it applies to.** Games exist in revisions, regions and dumps
with different headers. A patch built against one and applied to another
produces a broken game and a confused player. BPS records a checksum of the
source and refuses; IPS and PPF do not, so the release notes must state exactly
which dump is expected — name, size and hash.

**Whether it reproduces your build exactly.** This is the only thing that
matters at release time and the one most often assumed.

## Implement

```python
patch = mkpatch.make_ips(original, translated)
assert mkpatch.verify(original, patch, translated)
```

`make_ips` handles the format's two sharp edges. Records are capped at 65535
bytes, so long changes split. And a record whose offset happens to be `0x454F46`
is byte-identical to the `EOF` marker, so every patcher stops reading there — the
builder starts such a record one byte earlier, including an unchanged byte to
move the offset. It is the format's one real defect and it is silent when
mishandled.

Ship the patch with: the exact name and hash of the expected original, the hash
of the result, the version, and what changed since the last one.

## Verify

**Apply your own patch to a clean copy and compare hashes with the build you
tested.** Not "it looks right" — the same hash.

```python
assert hashlib.sha1(mkpatch.apply_ips(clean, patch)).hexdigest() == tested_hash
```

Then play the patched build for a few minutes. Verifying the hash proves the
bytes; only running it proves you patched the file you meant to.

For a release, have someone else apply it on their own machine, to their own
copy, following your instructions. Half the problems in distribution are
instructions that assume something the author had and the reader does not.

SOURCES: Specifiche del formato patch ips — DarkDreAm, translated by Z.e.r.o/ZeroSoft — https://romhacking.it/doc/view/id/39 · Patch .ips — Dull — https://romhacking.it/doc/view/id/18 · Patch .ppf — Dull — https://romhacking.it/doc/view/id/19 · Bugfix delle patch — Psyco — https://romhacking.it/doc/view/id/32 · Guida alle traduzioni parte III §7 — SadNES cITy — https://sadnescity.it/guide/guidasad_fs.php
