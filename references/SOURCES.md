# Sources

The skills in this plugin derive from documents written by the Italian and
international ROM hacking communities. **No third-party text is redistributed**:
this file records where each chapter comes from; the skills are rewritten and
verified. Italian titles are kept in the original, with a short English gloss.

In the skills, sources appear in two places for two purposes. The `SOURCES:`
line at the bottom is **attribution**: where the chapter comes from. The
`### Read more` section, which closes the explanation, is **further reading**:
for each pointer, what you will find there that the skill does not have.

The sources span 1996–2016. Where they prescribe programs, the prescription is
dropped and the concept kept.

---

## Table File Format (TBL)

- **Author:** Nightcrawler (TransCorp), with Tauwasser, Klarth, DaMarsMan, abw,
  KingMike, Gil Galad, snarf
- **Version:** 1.0 Draft, 5 July 2016
- **URL:** <https://transcorp.romhacking.net/scratchpad/Table%20File%20Format.txt>
  (indexed at <https://romhacking.it/doc/view/id/57>)
- **Derived:** `scripts/tbl.py`, skill `tables`

`tbl.py` implements the directives of the specification (one test each in
`tests/test_tbl.py`), with two deliberate departures:

**1. Table switching recognised but not decoded.** The `!` and `@` directives
are parsed and recorded, but `decode` raises an explicit error instead of
silently producing wrong text. Switching matters mostly for Japanese games with
separate kana and kanji tables; a game whose contexts use different charsets can
also be handled with one table file per context.

**2. Parameter rendering.** The specification formats control-code parameters
through the `%D`, `%X`, `%B` placeholders. That output is not unambiguously
reversible — an unpadded `%D` cannot be told apart from the surrounding text —
and a dump that does not reinsert byte-identical fails the only test that
matters. `tbl.py` uses the reversible form `[Label:0A,05]`; interoperating with
a third-party tool means converting on output.

---

## Tables

- **L'HexWorkshop e le table** (building a table by hand) — SadNES cITy — <https://romhacking.it/doc/view/id/44>
- **Derived:** skill `tables`

## Relative search and dumping

- **Dumping, questo sconosciuto** (dumping from first principles) — Dark Schneider — <https://romhacking.it/doc/view/id/6>
- **Come trovare tabelle dei font particolari** (non-contiguous charsets) — Mat — <https://romhacking.it/doc/view/id/26>
- **Guida alle traduzioni parte I: le basi** (translation guide, part I: basics) — SadNES cITy — <https://sadnescity.it/guide/guidasad_base.php>
- **Derived:** `scripts/relsearch.py`, skills `text-search`, `tables`

## Pointers

- **I puntatori** (pointers) — AnusP — <https://romhacking.it/doc/view/id/12>
- **Puntatori (SNES): questi sconosciuti** (SNES pointers) — DrZork4 Translations — <https://romhacking.it/doc/view/id/13>
- **I puntatori lorom** (LoROM pointers) — SadNES cITy — <https://romhacking.it/doc/view/id/36>
- **I puntatori hirom** (HiROM pointers) — SadNES cITy — <https://romhacking.it/doc/view/id/43>
- **Guida ai puntatori del Game Boy** (Game Boy pointers) — Dark Schneider — <https://romhacking.it/doc/view/id/14>
- **Derived:** `scripts/pointers.py`, skill `pointers`

## Expansion

- **Espansione fisica di una rom** (physical ROM expansion) — DrZork4 Translations — <https://romhacking.it/doc/view/id/7>
- **Guida alle traduzioni parte II: l'hacking delle ROM** (translation guide, part II: ROM hacking) — SadNES cITy — <https://sadnescity.it/guide/guidasad_rom.php>
- **Derived:** `scripts/ines.py`, skills `expansion`, `relocation`

## Graphics and fonts

- **Guida all'hacking della grafica nel processo di traduzione di ROM** (graphics hacking for translation) — Dark Schneider — <https://romhacking.it/doc/view/id/10>
- **8x8 proportional font secrets** — Near — <https://romhacking.it/doc/view/id/55>
- **Modificare i Variable Width Font** (editing VWFs) — Gemini — <https://romhacking.it/doc/view/id/27>
- **Variable Width Font disegnati su tile** (tile-based VWFs) — Gemini — <https://romhacking.it/doc/view/id/38>
- **Game Boy Advance: Formati comuni per la grafica** (common GBA graphics formats) — DarkDreAm — <https://romhacking.it/doc/view/id/45>
- **Formati grafici del NeoGeo** (Neo Geo graphics formats) — DarkDreAm — <https://romhacking.it/doc/view/id/56>
- **Guida all'estrazione e all'inserimento di TIM modificate nell'immagine di un gioco** (extracting and reinserting TIM images) — Dull — <https://romhacking.it/doc/view/id/17>
- **Modificare la grafica RAW nei giochi PSX** (raw graphics in PSX games) — Dark Schneider — <https://romhacking.it/doc/view/id/16>
- **Derived:** `scripts/tilepng.py`, skills `accents`, `tiles`, `palettes`, `fonts`, `vwf`, `image-formats`

## Assembly

- **Guida all'Assembly** (assembly guide) — UST — <https://romhacking.it/doc/view/id/30>
- **L'Assembly in un passo** (assembly in one step) — Dark Schneider — <https://romhacking.it/doc/view/id/15>
- **Hacking Mega Man X with ASM modification** — DarkDreAm — <https://romhacking.it/doc/view/id/41>
- **Game Boy Assembly Hacking** — DarkDreAm — <https://romhacking.it/doc/view/id/34>
- **Derived:** skill `asm`

## Control codes

- **Guida alla modifica dei byte a capo** (editing line-break bytes) — Random Stones — <https://romhacking.it/doc/view/id/46>
- **Derived:** skill `control-codes`

## General method

- **Guida al Rom Hacking** (introduction to ROM hacking) — Brisma — <https://romhacking.it/doc/view/id/2>
- **Introduzione al ROM-HACK e alla traduzione** (introduction to ROM hacking and translation) — LoRdCoStE — <https://romhacking.it/doc/view/id/3>
- **Rom Hacking Tutorial vol. 1 e 2** — DarkDreAm — <https://romhacking.it/doc/view/id/31>, <https://romhacking.it/doc/view/id/48>
- **Corso di traduzioni** (translation course) — Auryn — <https://romhacking.it/doc/view/id/5>
- **Derived:** skills `romhacking`, `recon`

## Translation, glossary and QA

- **Guida completa alla traduzione di ROM in lingua straniera** (complete guide to ROM translation) — SadNES cITy — <https://romhacking.it/doc/view/id/1>
- **Mini guida alla traduzione** (short translation guide) — Macchianera — <https://romhacking.it/doc/view/id/54>
- **De-Jap Guide to Translation** — DeJap — <https://romhacking.it/doc/view/id/9>
- **Bugfix delle patch** (fixing released patches) — Psyco — <https://romhacking.it/doc/view/id/32>
- **Derived:** skills `glossary`, `translation`, `qa`, `dump-insert`

## Patching

- **Specifiche del formato patch ips** (IPS format specification) — DarkDreAm (translated by Z.e.r.o / ZeroSoft) — <https://romhacking.it/doc/view/id/39>
- **Note:** the document states that IPS patches files up to "2^24-1 bit
  (2047 MB)" and that a record cannot exceed "2^16-1 bit (7.99 MB)". Both are
  wrong: the offset is 3 **bytes** (16 MB) and the length 2 bytes (64 KB).
- **Patch .ips** and **Patch .ppf** — Dull — <https://romhacking.it/doc/view/id/18>, <https://romhacking.it/doc/view/id/19>
- **Derived:** skill `patching`, `scripts/mkpatch.py`

## Compression

- **Gli algoritmi LZ77 e LZSS** (the LZ77 and LZSS algorithms) — Dark Schneider — <https://romhacking.it/doc/view/id/11>
- **Guida alle compressioni di tipo LZSS** (reversing LZSS) — SadNES cITy — <https://romhacking.it/doc/view/id/42>
- **Game Boy ASM Hacking: Le compressioni** (Game Boy compression) — DarkDreAm — <https://romhacking.it/doc/view/id/33>
- **DMA Transfer e Compressione** (DMA transfer and compression) — DarkDreAm, from the DMA Log by GhideonZhi/AGTP — <https://romhacking.it/doc/view/id/40>
- **Derived:** `scripts/entropy.py`, skill `compressions`

DarkDreAm's documents contribute three techniques used in `compressions` and
absent from theoretical treatments: finding the routine from the destination of
the decompressed data, confirming it by NOPping the call, and bypassing the
compression by inserting data already decompressed.

## Disc images and archives

- **Guida alle traduzioni parte III** (translation guide, part III: consoles with a filesystem) — SadNES cITy — <https://sadnescity.it/guide/guidasad_fs.php>
- **Come modificare la TOC** (editing the TOC) — Sephiroth 1311 — <https://romhacking.it/doc/view/id/29>
- **Guida all'inserimento di files modificati in immagini BIN** (reinserting files into BIN images) — PSX Trans (KaRMa) — <https://romhacking.it/doc/view/id/20>
- **Guida x idioti masterdotati alla compilazione/creazione di CD PSX** (building PSX CDs) — PSX Trans — <https://romhacking.it/doc/view/id/21>
- **Everything You Have Always Wanted to Know about the Playstation** — Joshua Walker — <https://romhacking.it/doc/view/id/49>
- **Derived:** skills `filesystem-iso`, `archives`

Of the second PSX Trans guide only the invariant survives — ISO 9660, Mode 2,
the licence in the first sector — while the instructions for the program of the
time are dropped.

---

## External references

They are not the base the skills were rewritten from — that remains the
documentation above — but they are where to go when a skill ends and the detail
of a specific platform is needed.

### Hardware specifications

Martin Korth's references are the de facto standard: complete, maintained, and
written for people who program the machine rather than use it.

- **fullsnes** — SNES — <https://problemkaputt.de/fullsnes.htm>
- **gbatek** — GBA and NDS — <https://problemkaputt.de/gbatek.htm>
- **everynes** — NES — <https://problemkaputt.de/everynes.htm>
- **psx-spx** — PlayStation — <https://problemkaputt.de/psx-spx.htm> (also as the `psx-spx` plugin)
- **ps2tek** — PlayStation 2 — <https://psi-rockin.github.io/ps2tek/>
- **PS1 consoledev** — <https://ps1.consoledev.net/one/>

### Assembly by platform

- **Assembly for the SNES** (65c816) — Ersanio — <https://ersanio.gitbook.io/assembly-for-the-snes/>
- **SNES Development: Getting Started** — Wesley Aptekar-Cassels — <https://blog.wesleyac.com/posts/snes-dev-1-getting-started>
- **Intro to ASM Modding & Hooking** — MGAMERZ, The Rockman EXE Zone — <http://forums.therockmanexezone.com/intro-to-asm-modding-hooking-t5374.html>
- **NesHacker** — YouTube channel on NES programming and hacking — <https://www.youtube.com/@NesHacker>

### Modern case studies

Worth as much as a guide, because they show the reasoning and not only the
result.

- **Cracking a Compression Algorithm** — Jonko, Chokuretsu project — <https://haroohie.club/blog/2022-10-19-chokuretsu-compression/> — reversing an unknown compression scheme, step by step
- **Tracking down pointers for PlayStation games using debuggers and Ghidra** — <https://suxin.space/notes/tracking-down-playstation-pointers-using-debuggers-ghidra/> — the modern method for pointers, with today's tools
- **Neo Geo ROM Hacking Guide** — Matt Greer — the complete series, covering
  hardware that is poorly documented elsewhere:
  [part 1](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-guide-part-1/) ·
  [part 2](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-guide-part-2/) ·
  [part 3](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-guide-part-3/) ·
  [digging into MAME traces](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-digging-into-mame-traces/) ·
  [fixed point](https://www.mattgreer.dev/blog/neo-geo-dev-fixed-point/) ·
  [finding tiles](https://www.mattgreer.dev/blog/finding-neo-geo-tiles/) ·
  [SMA encrypted PROMs](https://www.mattgreer.dev/blog/neo-geo-rom-hacking-sma-encrypted-proms/)
- **Policenauts — ROMhacking Technicals** — slowbeef — <https://lparchive.org/Policenauts/Update%2050/>

### Video

Watching someone work teaches what a document does not: the rhythm of
debugging, what to look at first, when to stop reading and set a breakpoint.

- **[NesHacker](https://www.youtube.com/@NesHacker)** — NES programming and hacking, from the ground up
- **[Super NES Features](https://www.youtube.com/playlist?list=PLHQOutQyFw5KCcj1IjIhExH_lvGwfn6GV)** — SNES hardware features, one per video
- **[Various](https://www.youtube.com/playlist?list=PLHQOutQyFw5LfOwu3YlZ_lyZC6ghTl4d6)** — NES and related topics, including the loading seam

### Less documented platforms

- **[The PowerPC 750CL Broadway Notebook](https://docs.google.com/document/d/1y2jUmJn7aoXo1FohaU6gx1vJ8cVc1tg1FEjbgNf4tUY/edit)** — grishnung — notes on the GameCube and Wii processor, admittedly incomplete and still the best available

### Collections and portals

- **Awesome Rom Hacking** — <https://github.com/romh-acking/Awesome-Rom-Hacking>
- **ROMhacking.net — Getting Started** — <http://www.romhacking.net/start/>
- **Zophar's Domain — translation docs** — <https://www.zophar.net/documents/transdocs.html>
- **The Ultimate Nintendo DS ROM Hacking Guide** — GBAtemp — <https://gbatemp.net/threads/the-ultimate-nintendo-ds-rom-hacking-guide.291274/>
- **ZTG — Gruppo di Traduzione Zuminator** (Italian) — <http://www.zuminator.altervista.org/guide.htm>
- **Brisma — guides and translations** (Italian) — the original site no longer
  responds; the archived copy of 19 February 2025 remains —
  <http://web.archive.org/web/20250219102818/https://spazioinwind.libero.it/brisma/>
- **Manual de traducción de videojuegos** (Spanish) — Sayans — <https://sayans.romhackhispano.org/old/documentos/manual_de_traduccion_de_videojuegos.pdf>
- **Documentos romhacking** (Spanish) — <https://emulacionsinsecretos.wordpress.com/documentos-romhacking/>
