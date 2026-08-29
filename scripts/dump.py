"""Text out of the game, into a file a translator can actually work in.

The reader is a human being, often not the person who did the hacking, and
often months later. Everything here follows from that: the shape of the text on
the page matches the shape it will have on screen, the markers are quiet, and
the file says what it is before it says anything else.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re

MARKER_RE = re.compile(r"^\[#(?P<id>\d+)\]\s*$")
TBL_TOKEN_RE = re.compile(r"\[([^\[\]]+)\]")
SCRIPT_TOKEN_RE = re.compile(r"<([^<>]+)>")


@dataclasses.dataclass
class Entry:
    index: int
    offset: int
    text: str            # script form: <CODES>, real newlines
    raw_len: int = 0     # bytes it occupied in the original


def dump_block(data: bytes, table, start: int, end: int,
               end_token: str = "[END]", newline_token: str | None = None) -> list[Entry]:
    """Split a block into entries.

    `newline_token` is the control code the game uses for a line break. Naming
    it turns it into a real newline in the output, which is the single change
    that makes a script readable: what the translator sees is the shape the text
    will have on screen.
    """
    decoded = table.decode(data[start:end], strict=False)
    entries: list[Entry] = []
    cursor = index = 0
    while cursor < len(decoded):
        cut = decoded.find(end_token, cursor)
        if cut == -1:
            chunk, cursor = decoded[cursor:], len(decoded)
        else:
            chunk, cursor = decoded[cursor:cut + len(end_token)], cut + len(end_token)
        entries.append(Entry(index=index, offset=0, text=chunk))
        index += 1
    running = start
    for entry in entries:
        entry.offset = running
        entry.raw_len = len(table.encode(entry.text))
        running += entry.raw_len
        entry.text = to_script(entry.text, newline_token)
    return entries


def to_script(text: str, newline_token: str | None = None) -> str:
    """Table form to script form: `[CODE]` becomes `<CODE>`, the newline breaks."""
    if newline_token:
        placeholder = "\x00"
        text = text.replace(newline_token, placeholder)
    text = TBL_TOKEN_RE.sub(lambda m: f"<{m.group(1)}>", text)
    if newline_token:
        text = text.replace("\x00", "\n")
    return text


def to_table(text: str, newline_token: str | None = None) -> str:
    """Script form back to table form. Exactly the inverse of `to_script`."""
    if newline_token:
        text = text.replace("\n", "\x00")
    text = SCRIPT_TOKEN_RE.sub(lambda m: f"[{m.group(1)}]", text)
    if newline_token:
        text = text.replace("\x00", newline_token)
    return text


def write_script(entries: list[Entry], path, *, source: str = "", title: str = "",
                 notes: tuple[str, ...] = (), budget=None) -> None:
    """Write the marked-script form.

    The header is not decoration. A translator opening this file six months from
    now needs to know where it came from, how much of it there is, and which
    parts must survive untouched.
    """
    lines: list[str] = []
    where = f"{source} — " if source else ""
    lines.append(f"# {where}{title or 'script'}, {len(entries)} strings")
    lines.append("# [#n] is the string id. Leave the markers alone.")
    lines.append("# A line break here is a line break in the game.")
    lines.append("# Leave the <CODES> alone: they are the game's own formatting.")
    if budget is not None:
        lines.append("#")
        lines.extend(f"# {line}" for line in budget.for_translator())
    lines.extend(f"# {note}" for note in notes)
    lines.append("")
    for entry in entries:
        lines.append(f"[#{entry.index}]")
        lines.append(entry.text)
        lines.append("")
    pathlib.Path(path).write_text("\n".join(lines), encoding="utf-8")


def read_script(path) -> list[Entry]:
    entries: list[Entry] = []
    current: Entry | None = None
    body: list[str] = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        marker = MARKER_RE.match(line)
        if marker:
            if current is not None:
                current.text = "\n".join(body).strip("\n")
                entries.append(current)
            current = Entry(index=int(marker["id"]), offset=0, text="")
            body = []
        elif current is not None:
            body.append(line)
        # lines before the first marker are the header: skipped
    if current is not None:
        current.text = "\n".join(body).strip("\n")
        entries.append(current)
    return entries


def write_tsv(entries: list[Entry], path, *, says: dict[int, str] | None = None,
              terminator: str = "", header: tuple[str, ...] = (), budget=None) -> None:
    """One row per string, for short lists where a table beats prose.

    Item names, spells, places, monsters: things read as a set rather than as
    sentences. `says` adds a column of human notes, which is where a glossary
    starts.

    `terminator` is stripped from the text column. A separator is punctuation
    between entries, not part of any of them, and leaving it in every cell is
    noise a translator has to read past on every single row.
    """
    says = says or {}
    terminator = to_script(terminator) if terminator else ""
    rows = [f"# {line}" for line in header]
    if budget is not None:
        rows.extend(f"# {line}" for line in budget.for_translator())
    if terminator:
        rows.append(f"# every entry ends with {terminator} in the ROM; it is not shown here")
    rows.append("id\tbytes\ttext\tsays")
    for entry in entries:
        text = entry.text
        if terminator and text.endswith(terminator):
            text = text[: -len(terminator)]
        text = text.replace("\t", " ").replace("\n", "\\n")
        rows.append(f"{entry.index}\t{entry.raw_len}\t{text}\t{says.get(entry.index, '')}")
    pathlib.Path(path).write_text("\n".join(rows) + "\n", encoding="utf-8")


def read_tsv(path, *, terminator: str = "") -> list[Entry]:
    """Read back a TSV, restoring the terminator that was hidden from the reader."""
    entries: list[Entry] = []
    terminator = to_script(terminator) if terminator else ""
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("id\t"):
            continue
        cells = line.split("\t")
        text = cells[2].replace("\\n", "\n") if len(cells) > 2 else ""
        entries.append(Entry(index=int(cells[0]), offset=0,
                             text=text + terminator, raw_len=int(cells[1])))
    return entries


def write_po(entries: list[Entry], path, *, source: str = "") -> None:
    """gettext .po, for translators who work in a CAT tool.

    Buys translation memory, fuzzy matching and glossary checking for free. Costs
    readability: the game's line breaks become \\n escapes inside quoted strings.
    """
    out = ['msgid ""', 'msgstr ""', '"Content-Type: text/plain; charset=UTF-8\\n"', ""]
    for entry in entries:
        body = entry.text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        out.append(f"#: {source}:{entry.index}")
        out.append(f'msgid "{body}"')
        out.append('msgstr ""')
        out.append("")
    pathlib.Path(path).write_text("\n".join(out), encoding="utf-8")
