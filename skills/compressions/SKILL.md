---
name: compressions
description: Recognises compressed data, finds and understands the routine that unpacks it, and decides between bypassing the compression, reimplementing the codec, or working around it. Use when text or graphics are not in the ROM in readable form, when a region's byte distribution differs sharply from its neighbours, or when a decompressor is needed to translate a game.
---

# Compressions

## What this is

A cartridge holds a few megabytes and a game wants more, so it stores some of
its data packed and unpacks it when needed. That is all compression is here: a
routine in the game reads a compact form and writes out the real bytes, usually
into RAM, just before they are used.

Three families cover almost everything you will meet.

**RLE** — run-length encoding. "Twenty of this byte" instead of the byte twenty
times. Trivial to write, works brilliantly on tilemaps and flat colour, does
nothing for text.

**LZ** — the family behind LZ77, LZSS and most of what games use. The idea:
while writing the output, if the next few bytes already appeared earlier, write
a *reference* — "go back 565 bytes and copy 4" — instead of the bytes
themselves. Text and graphics are full of repetition, so this pays well. Every
variant differs in how it encodes the reference and how it tells a reference
apart from a literal.

**Huffman and friends** — entropy coding. Common symbols get short bit patterns,
rare ones get long ones. No byte alignment at all, which makes it unmistakable
in a hex editor and unpleasant to reverse.

And a fourth thing that is *not* compression but gets called it: **dictionary
substitution**, where one byte stands for a syllable. That is DTE, it is much
more common in text than any of the above, and it lives in `dte-mte`.

Why a translator cares: if the script is compressed you cannot read it in the
file, you cannot search for it, and you cannot put your text back without a
compressor. But the useful news is that **you often do not need to reimplement
anything**. A compressed font can frequently be replaced with an uncompressed
one by patching the routine that loads it — the strategies below are ordered by
cost, and writing a codec is not the first of them.

### Read more

→ **[Gli algoritmi LZ77 e LZSS](https://romhacking.it/doc/view/id/11)** (Dark Schneider) — the algorithms themselves, if you want the theory behind the byte shapes above.

→ **[Guida alle compressioni di tipo LZSS](https://romhacking.it/doc/view/id/42)** (SadNES cITy) — a worked reverse of an LZSS variant in a real game.

→ **[Game Boy ASM Hacking: Le compressioni](https://romhacking.it/doc/view/id/33)** (DarkDreAm) — where the breakpoint-on-the-destination method comes from, followed step by step on R-Type 2.

→ **[DMA Transfer e Compressione](https://romhacking.it/doc/view/id/40)** (DarkDreAm, from GhideonZhi's DMA log) — the bypass strategy in full: inserting decompressed data and patching the transfer, on SNES.

→ **[Cracking a Compression Algorithm](https://haroohie.club/blog/2022-10-19-chokuretsu-compression/)** (Jonko) — a modern, unhurried account of reversing an unknown scheme from scratch. The best single thing to read on how this actually feels.

## Recognize

### Entropy points, it does not prove

Compressed data has a flat byte distribution, so its entropy per byte runs high.
So does other data, and this is where hours get lost:

```python
import entropy
for offset, score in entropy.profile(data, window=2048):
    print(f"0x{offset:05X}  {score:.2f}")
```

**Machine code scores as high as compressed data.** *Example:* on a game with no
compression at all, code regions can run 6.3–6.9 bits per byte and the dialogue
4.7. Read as "high entropy means compressed", that profile says the code is
compressed and the text is not — both wrong.

The other reliable false positives: audio samples, graphics with many colours,
anything encrypted, and tables of pointers into a wide range.

Two rules keep entropy useful:

1. **Compare regions with each other**, never against an absolute threshold. The
   interesting thing is a region unlike its neighbours, not a number.
2. **Use windows of at least 512 bytes**, 2048 is better. Entropy is bounded by
   `log2(window)`: on 64 bytes even pure noise cannot exceed 6 bits, so short
   compressed regions read as uncompressed. `entropy.suspects` refuses windows
   below the useful size rather than returning a comforting answer.

### What the schemes actually look like

Recognising a scheme from its bytes is faster than any breakpoint, and there are
only a handful in common use.

**RLE** — a count and a value. The cheapest thing that works, and everywhere.

```
03 41 05 20 02 42        →  AAA·····BB
^^ ^^                       three of $41, five of $20, two of $42
```

Variants: a sign bit distinguishing "repeat this once N times" from "copy the
next N bytes literally"; a terminator like `$00` or `$FFFF`.

**LZ77 / LZSS** — literals and back-references into what you have already
written. The flag byte is the giveaway:

```
10 00 20 00              header: type $10, decompressed size $2000 (24-bit LE)
0F 41 42 43 44 12 34 ..  a block
^^                       flag byte: 8 flags, most significant bit first
                         1 = back-reference (2 bytes), 0 = literal (1 byte)
   ^^ ^^ ^^ ^^           $0F = 0000 1111, so the first four are literals
                         (A B C D) and the last four are back-references
```

A back-reference in the Nintendo BIOS form is two bytes, `LLLLOOOO OOOOOOOO`:

```
12 34   →  length = ($12 >> 4) + 3 = 4
           offset = (($12 & $0F) << 8 | $34) + 1 = $235 = 565
        copy 4 bytes from 565 back in the output you have written so far
```

The `+3` and `+1` exist because a reference shorter than 3 bytes would cost more
than the literals it replaces. **Every LZ variant has offsets like these and
every one chooses them differently** — this is where reimplementations go wrong,
and where comparing against the game's own decompressor pays for itself.

The signature is unmistakable once seen: a byte, then a run of 8 items each
either one or two bytes long, then another byte. In a hex editor the flag bytes
line up in a loose diagonal.

**Huffman** — a tree at the start, then a bit stream with no byte alignment.
Recognisable by a small table of symbols and lengths at the head, and by the
fact that nothing in the payload aligns to anything.

A decompressor for the LZ77 form above is about a dozen lines, which is worth
knowing before deciding the codec is too hard:

```python
def lz77(data: bytes) -> bytes:
    size = int.from_bytes(data[1:4], "little")
    out = bytearray()
    i = 4
    while len(out) < size:
        flags = data[i]; i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                hi, lo = data[i], data[i + 1]; i += 2
                length = (hi >> 4) + 3
                offset = (((hi & 0x0F) << 8) | lo) + 1
                for _ in range(length):          # byte at a time: the source may
                    out.append(out[-offset])     # overlap the destination
            else:
                out.append(data[i]); i += 1
    return bytes(out)
```

The byte-at-a-time copy is not clumsiness. A reference may point at bytes the
same reference is still writing — offset 1, length 20 means "repeat the previous
byte 20 times" — so a block copy produces different output. Getting this wrong
gives a decompressor that works on most data and fails on runs.

### Stronger signals than entropy

**A declared size.** Many schemes put the decompressed length in a header. The
Nintendo BIOS family — used on GB, GBA and DS, and copied widely — is one type
byte then a 24-bit little-endian size:

```python
sig = entropy.signature(block)   # 0x10 LZ77, 0x11 LZ11, 0x20/0x28 Huffman, 0x30 RLE
```

Check the size for **plausibility**. A lone `$10` byte means nothing; treating
every one as a compressed block wastes a day.

**A pointer into a region you cannot read.** If something points at it, the game
reads it, and if you cannot read it either it is encoded somehow.

**Text that exists on screen and nowhere in the file.** The strongest signal of
all. `text-search` covers finding it in RAM instead.

## Analyze

### Find the routine from its destination

You do not need to recognise the algorithm to find the code. You need to know
**where the output lands**.

1. Reach the screen that shows the decompressed data.
2. Capture the emulator's memory and find the data there — a font, a tilemap, a
   block of text.
3. Set a **write breakpoint on that destination**. The routine that fires is the
   decompressor, or its last step.
4. Read the registers at the break: one will hold an address in RAM or video
   memory — the destination — and another an address in ROM: the **source**. You
   now have both ends.

**A timing detail that tells you where to look.** On most consoles video memory
can only be written during the vertical blank, which is a few thousand cycles.
Decompressing a font does not fit in that window, so the game unpacks into
ordinary RAM first and transfers afterwards. Breakpoint on the RAM buffer, not
on video memory, or you will find the transfer and not the decompressor.

### Confirm by breaking it

The cheapest confirmation in this whole craft: **replace the call with NOPs and
see what disappears.** If the font stops appearing, that was the call. No
disassembly required, and it takes a minute.

Then read the routine. You are looking for the shape, not the name: a length
byte followed by a run of literals, a back-reference as offset plus length, a
bit stream where each bit says "literal or reference", an end marker.

## Implement

Three strategies, in increasing order of cost. **Pick the cheapest that fits.**

### 1. Bypass it

Put the data in **already decompressed**, and patch the code to use it directly
instead of calling the decompressor. Where the game copies the unpacked result
into video memory with a block transfer, redirect that transfer at your data and
skip the call entirely.

Costs an assembly patch and some free space; costs no codec at all. For a
compressed font — the single most common case in a translation — this is usually
the right answer.

Its limit, and it is a real one: it does not scale. A game with dozens of
compressed blocks needs a codec, because bypassing each one separately is more
work than writing the decompressor once.

### 2. Reimplement the codec

Write **both** halves. A decompressor alone lets you read; only a compressor
lets you put anything back.

The compressor must produce output the game's decompressor accepts, which is a
stricter requirement than "output that decompresses correctly with my code".
And it should be **no worse than the original** at packing: if your version of
the same data comes out larger, you have spent your headroom on the codec rather
than on the translation.

### 3. Work around it

Sometimes the data need not be compressed at all. If a block has room to hold
its uncompressed form — or can be relocated somewhere that does — store it flat
and patch the routine to copy rather than unpack. Simpler than a codec and
faster at runtime, when the space exists.

## Verify

**The round-trip rule, in its strictest form: recompress the original data and
the game must run identically.**

```python
assert decompress(compress(original)) == original      # your codec agrees with itself
assert game_runs_identically(rebuilt_with_recompressed_original)  # and with the game
```

The first line is necessary and nowhere near sufficient. A codec can be
self-consistent and still produce a stream the game's own decompressor reads
differently. Only the game's decompressor is the authority.

Order matters: **recompress the untouched original first**, before putting new
data in. If that fails you have a codec bug; if you skip it and go straight to
new data, a failure could be either the codec or the data and you have no way to
tell.

Then check the ratio. `entropy.ratio_hint` reads it against what schemes
typically achieve — a result far off the original's ratio means your compressor
is leaving space on the table, and space is the thing this whole phase exists to
buy.

SOURCES: Cracking a Compression Algorithm — Jonko, Chokuretsu project — https://haroohie.club/blog/2022-10-19-chokuretsu-compression/ · Gli algoritmi LZ77 e LZSS — Dark Schneider — https://romhacking.it/doc/view/id/11 · Guida alle compressioni di tipo LZSS — SadNES cITy — https://romhacking.it/doc/view/id/42 · Game Boy ASM Hacking: Le compressioni — DarkDreAm — https://romhacking.it/doc/view/id/33 · DMA Transfer e Compressione — DarkDreAm (from the DMA Log by GhideonZhi/AGTP) — https://romhacking.it/doc/view/id/40
