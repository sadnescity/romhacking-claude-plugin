---
name: filesystem-iso
description: Works with optical disc images — ISO 9660 and raw BIN, sector geometry, LBA arithmetic, the volume descriptor and path table, EDC/ECC, and reinserting a modified file without breaking the image. Use when the target is a CD or DVD based game, when a file must be extracted from or put back into a disc image, or when a rebuilt image no longer boots.
---

# Disc Images

## What this is

A cartridge is a flat block of bytes: offset 4096 is offset 4096. A CD is not.
It is a spiral of **sectors**, each 2352 bytes on the disc, of which only part
is your data — the rest is synchronisation marks, a header saying which sector
this is, and error correction so that a scratch does not lose the data.

On top of the sectors sits a filesystem, ISO 9660, which is a directory
structure much like any other: a root, folders, files, each with a name, a
starting sector and a length.

Two units, then, and confusing them is the classic mistake. A file's position is
a **sector number** (the LBA — logical block address). To reach it in your image
you multiply by the sector size and add the offset where data starts inside a
sector — and both depend on how the image was dumped:

- a **cooked** image keeps only the 2048 data bytes per sector: offset = LBA × 2048
- a **raw** image keeps all 2352: offset = LBA × 2352 + 16 or 24, depending on
  the sector mode

Eight bytes of error there gives you a file that looks right and is subtly
corrupt.

Two consequences a translator meets immediately.

**Files occupy whole sectors.** A 3000-byte file takes two sectors and wastes
1096 bytes. That waste is free space: the file can grow into it without anything
moving.

**Many games ignore the filesystem.** They keep their own table of sector
numbers and read directly, which means editing the directory entry achieves
nothing at all. See `archives`.

### Read more

→ **[Guida alle traduzioni parte III](https://sadnescity.it/guide/guidasad_fs.php)** (SadNES cITy) — TOC, LBA, sector sizes and error correction, written for translators rather than for CD engineers.

→ **[Come modificare la TOC](https://romhacking.it/doc/view/id/29)** (Sephiroth 1311) — changing the allocation table to make room, in detail.

→ **[Everything You Have Always Wanted to Know about the Playstation](https://romhacking.it/doc/view/id/49)** (Joshua Walker) — the hardware and disc format reference behind all of it.

## Recognize

| Signal | What it is |
|---|---|
| `CD001` at offset 0x8001 (32 KB in) | ISO 9660 primary volume descriptor: a 2048-byte-per-sector image |
| `CD001` at 0x9319, and the file size divides by 2352 | a raw image: 2352 bytes per sector, data plus sync, header and error correction |
| a `.cue` beside the image | track layout, and where the data track ends and audio begins |
| size divides by 2048 but there is no `CD001` | a filesystem that is not ISO 9660, or a proprietary layout |

## Analyze

### Sector geometry, which is where the arithmetic lives

A physical sector is always 2352 bytes. What changes is how much of it is your
data and where that data starts:

| Mode | Layout | Data | Data starts at |
|---|---|---|---|
| **Mode 1** | 12 sync + 4 header + **2048** + 4 EDC + 8 blank + 276 ECC | 2048 | offset 16 |
| **Mode 2 Form 1** | 12 sync + 4 header + 8 subheader + **2048** + 4 EDC + 276 ECC | 2048 | offset 24 |
| **Mode 2 Form 2** | 12 sync + 4 header + 8 subheader + **2324** + 4 EDC | 2324 | offset 24 |
| **cooked (2048)** | data only, everything else stripped | 2048 | offset 0 |

Form 2 carries streamed audio and video: more payload, no error correction,
because a glitch in a video frame matters less than the space.

### From LBA to a byte offset

The LBA is a sector number, and it is the pointer of the disc world. Converting
it is the single most error-prone step:

```
cooked image:  offset = LBA * 2048
raw image:     offset = LBA * 2352 + data_start     # 16 or 24, per the mode
```

Read the byte at `LBA * 2352 + 15` to know which: mode 1 or mode 2 is written
there, in the sector header.

### The filesystem

The primary volume descriptor at sector 16 gives the root directory's LBA and
size. Directory records give each file its **LBA and its length in bytes**, and
the length is what matters when reinserting: a file occupies whole sectors, so
there are usually spare bytes at the end of the last one.

**That slack is free space.** A file can grow into the tail of its own last
sector without touching anything else. Beyond that, the file must move, and then
its directory record — its LBA and length — has to be updated.

## Implement

Three operations, in rising order of risk.

**Edit in place, same length.** Nothing else changes. Locate the file's LBA,
convert to an offset, write the bytes. On a raw image the error correction of
every touched sector must be recomputed.

**Grow within the last sector.** Update the length in the directory record. The
LBA stays. Still nothing moves.

**Move the file.** Write it to free space — the end of the image is usually
available — update LBA and length in the directory record, and leave the
original bytes alone until it works. This is the risky one: anything that
hardcodes the old LBA breaks, and games that bypass the filesystem (see above
and `archives`) never read the directory record at all.

### Error correction

On raw images, EDC and ECC are computed over the sector's contents. Change a
byte without recomputing them and a real console may refuse the sector, while an
emulator happily reads it — so it works on your desk and fails on hardware.
Recompute for every sector you touch. Cooked 2048-byte images have none of this,
which is why they are easier to work with when the format allows.

## Verify

1. **The image mounts** and the file list matches the original, with your file
   at its expected size.
2. **The game boots** in the emulator and reaches the content you changed.
3. **The sector count is unchanged**, unless you deliberately grew the image —
   a changed total usually means a rebuild that moved everything.
4. For a raw image, **error correction is valid** on every sector you touched.

For distribution, xdelta handles moved data; PPF is the traditional choice for
this platform but describes byte replacements at fixed offsets, so it does not
survive a layout change. See `patching`.

SOURCES: Guida alle traduzioni parte III: l'hacking delle console con file system — SadNES cITy — https://sadnescity.it/guide/guidasad_fs.php · Come modificare la TOC — Sephiroth 1311 — https://romhacking.it/doc/view/id/29 · Guida all'inserimento di files modificati in immagini BIN — PSX Trans (KaRMa) — https://romhacking.it/doc/view/id/20 · Everything You Have Always Wanted to Know about the Playstation — Joshua Walker — https://romhacking.it/doc/view/id/49
