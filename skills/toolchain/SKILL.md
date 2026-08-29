---
name: toolchain
description: Maps a target platform to the emulator or debugger plugin that can inspect it, and explains how to reach MesenCE over MCP. Use when a ROM hacking task needs runtime inspection, breakpoints, memory or VRAM reads, or an in-game screenshot.
user-invocable: false
---

# Toolchain

## What this covers, and what it does not

This table covers the **irreproducible** category only: emulators, debuggers,
disassemblers, assemblers. Those embed decades of hardware reverse engineering
and cannot be rewritten on demand, so we use what exists.

For everything else — dumpers, inserters, converters, archive extractors, patch
builders — there is **no table of recommended tools here**, because the tool
gets written. See the `tooling` skill.

## Target to plugin

| Target | Plugin | What it gives you |
|---|---|---|
| NES, SNES, Game Boy, GBA, PC Engine, SMS/Game Gear, WonderSwan | `mesence` | breakpoints, memory read/write, disassembly, tracing, tile and palette inspection, Lua, TBL text search |
| PlayStation | `duckstation` + `psx-spx` | MIPS breakpoints, memory, GPU/SPU state, VRAM watches, controller automation; plus the hardware reference |
| PSP | `ppsspp` | CPU debugging, GE display lists, framebuffer dumps, texture and CLUT inspection |
| Mega Drive / Genesis | `exodus` | M68000 and Z80 debugging, VDP state, sprites, palette, nametables, VRAM |
| Static code: executables, overlays, ELF | `ghidra` | decompilation, cross-references, annotation |
| Assembly patches | `armips` | MIPS and ARM assembly, reassembly into the target |

All are on the `sadnescity-plugins` marketplace.

For the hardware itself, Martin Korth's references are the standard — fullsnes,
gbatek, everynes and psx-spx, at <https://problemkaputt.de/>. When guidance here
stops at "this depends on the machine", that is where the answer is.

## When the plugin is not installed

Say so plainly, name the plugin, and point at `/plugin`. **Do not substitute
it** — do not try to reimplement an emulator's inspection with static analysis
and call it equivalent. Static analysis answers different questions; when the
question is "what does the game actually do at this moment", only the emulator
answers it.

Work that does not need runtime inspection continues normally: most of
`recon`, `tables`, `pointers` and `dump-insert` is static.

## Reaching MesenCE without the plugin

If the `mesence` plugin is loaded, use its MCP tools directly — they are typed
and documented. This section is only for sessions where it is not.

MesenCE embeds its own MCP server. Launch it with the server enabled:

```bash
open -a MesenCE --args --mcp          # default port 9100
```

Transport is Streamable HTTP, JSON-RPC 2.0, at `POST http://localhost:9100/mcp`.
`initialize` returns an `MCP-Session-Id` header that every later request must
carry. `scripts/mesen_rpc.py` wraps this.

Before assuming a tool name, ask the server:

```python
import mesen_rpc
client = mesen_rpc.MesenRPC()
client.initialize()
[t["name"] for t in client.list_tools()]
```

## Choosing between static and runtime

| Question | Where it is answered |
|---|---|
| Where is this text stored? | static: search the file |
| Which code reads this text? | runtime: read breakpoint on the block |
| What does this byte mean? | runtime: watch what the game does with it |
| How many pointers are there? | static: read the table |
| Does the patched ROM still boot? | runtime, always |

The last row has no static substitute. A structurally valid ROM that does not
boot is a common outcome, and only the emulator tells you.

