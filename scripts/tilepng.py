"""Tiles to PNG and back, with no dependencies.

PNG is written by hand because the alternative is a dependency, and a seed that
needs `pip install` is a seed nobody plants.
"""
from __future__ import annotations

import struct
import zlib


def png_write(path, pixels: list[list[tuple[int, int, int]]]) -> None:
    height, width = len(pixels), len(pixels[0])
    raw = b"".join(
        b"\x00" + b"".join(bytes(px) for px in row) for row in pixels
    )

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        handle.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        handle.write(chunk(b"IEND", b""))


def decode_tile_2bpp(data: bytes, offset: int) -> list[list[int]]:
    """NES-style planar 2bpp: eight bytes of plane 0, then eight of plane 1."""
    rows = []
    for y in range(8):
        low, high = data[offset + y], data[offset + 8 + y]
        rows.append([
            ((low >> (7 - x)) & 1) | (((high >> (7 - x)) & 1) << 1)
            for x in range(8)
        ])
    return rows


def encode_tile_2bpp(rows: list[list[int]]) -> bytes:
    low = bytearray(8)
    high = bytearray(8)
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            low[y] |= (value & 1) << (7 - x)
            high[y] |= ((value >> 1) & 1) << (7 - x)
    return bytes(low) + bytes(high)


def sheet(data: bytes, base: int, indices, palette, scale: int = 4, gap: int = 1):
    """Render tiles side by side into a pixel grid ready for `png_write`."""
    cell = 8 * scale + gap
    width = cell * len(indices) + gap
    height = 8 * scale + 2 * gap
    canvas = [[palette[0] for _ in range(width)] for _ in range(height)]
    for slot, index in enumerate(indices):
        tile = decode_tile_2bpp(data, base + index * 16)
        for y in range(8):
            for x in range(8):
                colour = palette[tile[y][x]]
                for dy in range(scale):
                    for dx in range(scale):
                        canvas[gap + y * scale + dy][gap + slot * cell + x * scale + dx] = colour
    return canvas


def png_read(path) -> list[list[tuple[int, int, int]]]:
    """Read back a truecolour 8-bit PNG. Enough to crop and zoom a screenshot."""
    import struct
    import zlib

    raw = open(path, "rb").read()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, width, height = 8, b"", 0, 0
    while pos < len(raw):
        length, tag = struct.unpack(">I", raw[pos:pos + 4])[0], raw[pos + 4:pos + 8]
        payload = raw[pos + 8:pos + 8 + length]
        if tag == b"IHDR":
            width, height, depth, colour = struct.unpack(">IIBB", payload[:10])
            assert depth == 8 and colour in (2, 6), f"unsupported PNG: depth {depth}, colour {colour}"
            channels = 3 if colour == 2 else 4
        elif tag == b"IDAT":
            idat += payload
        elif tag == b"IEND":
            break
        pos += 12 + length
    data = zlib.decompress(idat)
    stride = width * channels
    out, previous = [], bytearray(stride)
    at = 0
    for _ in range(height):
        filter_type, line = data[at], bytearray(data[at + 1:at + 1 + stride])
        at += 1 + stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = previous[i]
            c = previous[i - channels] if i >= channels else 0
            if filter_type == 1:
                line[i] = (line[i] + a) & 0xFF
            elif filter_type == 2:
                line[i] = (line[i] + b) & 0xFF
            elif filter_type == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif filter_type == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        out.append([tuple(line[x * channels:x * channels + 3]) for x in range(width)])
        previous = line
    return out


def crop_zoom(pixels, x: int, y: int, width: int, height: int, scale: int = 4):
    return [
        [pixels[y + row // scale][x + col // scale] for col in range(width * scale)]
        for row in range(height * scale)
    ]


def lit_pixels(pixels, x: int, y: int, width: int, height: int, threshold: int = 200) -> int:
    """Count bright pixels in a screen region.

    Use it to check that something is actually rendered rather than trusting a
    zoomed screenshot. Two pixels of accent on an 8x8 grid are exactly the size
    at which the eye sees what it expects.
    """
    return sum(
        1
        for row in range(y, y + height)
        for col in range(x, x + width)
        if sum(pixels[row][col]) > threshold
    )
