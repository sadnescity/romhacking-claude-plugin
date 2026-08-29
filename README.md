# romhacking

A Claude Code plugin that teaches and applies **the method** of ROM hacking for
game translation, whatever the game or platform.

## The problem

Ask a model to translate a game and it starts editing strings. What comes out
is truncated work: missing accents, lines cut short by the space available,
broken formatting — because the groundwork was never done.

Technical knowledge is not the bottleneck. **Sequence discipline** and
**measurable verification** are. This plugin provides both.

## The flow

```
recon → text encoding (table + control codes) → accented glyphs → space
→ graphics → glossary → translation → QA → patch
```

Translation comes near the end, never first. Every phase has a gate that is not
declared but proved: a table counts when its round-trip is byte-identical;
accents count when they are readable on screen in the emulator. Project state
lives in `ROMHACK.md`, next to the data, and survives across sessions.

## What it contains

- **Phase skills** — `romhacking` (the director), `recon`, `encoding`,
  `accents`, `space`, `graphics`, `glossary`, `translation`: what each phase
  needs, what it produces, how its gate is closed.
- **Theme skills** — text search, tables, control codes, DTE/MTE, pointers,
  expansion, relocation, compression, archives, disc images, tiles, palettes,
  fonts, VWF, image formats, assembly, dump and insert, QA, patching. Each one
  explains the subject before the procedure, then follows four movements:
  recognize, analyze, implement, verify.
- **Reference scripts** in `scripts/` — Python 3, standard library only: TBL
  tables, relative search, pointers, dump/insert, iNES, entropy, tiles and PNG,
  IPS patches, project state. They are seeds to adapt in the translation's own
  repository, not finished products.

## Installation

The plugin is distributed through the `sadnescity-plugins` marketplace:

```
/plugin marketplace add sadnescity/claude-plugins
/plugin install romhacking@sadnescity-plugins
```

## Usage

```
/romhacking                    figures out where you are and guides you
/romhacking:tables             one chapter, from recognition to verification
/romhacking:pointers
/romhacking:accents
```

Skills also load on their own when a request calls for them: asking to
translate a game reaches the director, which reads `ROMHACK.md` and refuses to
produce translated text while earlier gates are open.

## Relationship to the other plugins

This plugin does not drive emulators, it **orchestrates** them. Runtime
debugging stays with `mesence` (NES/SNES/GB/GBA/PCE/SMS/WS), `duckstation`
(PS1), `ppsspp` (PSP) and `exodus` (Mega Drive); static analysis with `ghidra`;
assembly patches with `armips`; PS1 hardware reference with `psx-spx`. They are
all on the same marketplace, and none of their tools are duplicated here.

## Concepts, formats, tools

The sources behind this plugin span 1996–2016 and prescribe programs that
mostly no longer run. The plugin separates three layers:

- **concepts** — pointers, DTE/MTE, bitplanes, LBA, entropy: invariant, they
  are the content of the skills;
- **formats** — TBL, IPS, BPS, PPF, xdelta, ISO 9660: durable, respected to the
  letter;
- **tools** — **written when needed**, not prescribed. The exception is
  emulators, debuggers, disassemblers and assemblers, which embed decades of
  hardware reverse engineering and are not rewritten.

The sources are listed in [`references/SOURCES.md`](references/SOURCES.md). No
third-party text is redistributed.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
