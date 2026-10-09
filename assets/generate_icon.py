"""Generate the StudyDesk Pro application icon (studydesk.ico + studydesk.png).

Pure-Python implementation - no external dependencies required.
Creates a professional graduation-cap / study desk icon at multiple
resolutions and writes a valid Windows .ico file plus a .png master.
"""

import os
import struct
import zlib
import math

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "assets", "icons")
SIZES = (16, 24, 32, 48, 64, 128, 256)


def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp_color(c1, c2, t):
    return tuple(int(_lerp(c1[i], c2[i], t)) for i in range(3))


def _rounded_rect_mask(size, radius):
    mask = [[False] * size for _ in range(size)]
    r = radius
    for y in range(size):
        for x in range(size):
            in_rect = True
            corners = []
            if x < r and y < r:
                corners.append((r, r))
            if x >= size - r and y < r:
                corners.append((size - r - 1, r))
            if x < r and y >= size - r:
                corners.append((r, size - r - 1))
            if x >= size - r and y >= size - r:
                corners.append((size - r - 1, size - r - 1))
            if corners:
                cx, cy = corners[0]
                dist = math.hypot(x - cx, y - cy)
                if dist > r:
                    in_rect = False
            mask[y][x] = in_rect
    return mask


def render(size):
    """Render RGBA pixels for the icon at the given size."""
    bg_top = (41, 128, 185)
    bg_bottom = (27, 79, 130)
    cap_color = (245, 245, 245)
    cap_shadow = (200, 205, 215)
    tassel_color = (241, 196, 15, 255)
    tassel_dark = (200, 155, 10, 255)
    base_color = (52, 73, 94)

    pixels = [[(0, 0, 0, 0)] * size for _ in range(size)]
    radius = max(2, size // 6)
    mask = _rounded_rect_mask(size, radius)

    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            t = y / max(1, size - 1)
            bg = _lerp_color(bg_top, bg_bottom, t)
            pixels[y][x] = (bg[0], bg[1], bg[2], 255)

    cx = size / 2.0
    cy = size / 2.0
    s = size

    board_half = s * 0.30
    board_top_y = cy - s * 0.12
    board_pts = [
        (cx, board_top_y - board_half * 0.55),
        (cx + board_half, board_top_y),
        (cx, board_top_y + board_half * 0.55),
        (cx - board_half, board_top_y),
    ]

    def point_in_polygon(px, py, poly):
        inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > py) != (yj > py)) and \
               (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi):
                inside = not inside
            j = i
        return inside

    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            if point_in_polygon(x + 0.5, y + 0.5, board_pts):
                shade = 1.0 if (x + 0.5) < cx else 0.88
                col = cap_color if (x + 0.5) < cx else cap_shadow
                pixels[y][x] = (col[0], col[1], col[2], 255)

    base_top = board_top_y + board_half * 0.45
    base_bottom = base_top + s * 0.16
    base_half_top = board_half * 0.62
    base_half_bot = board_half * 0.42
    for y in range(size):
        if y < base_top or y > base_bottom:
            continue
        t = (y - base_top) / max(1, base_bottom - base_top)
        half = _lerp(base_half_top, base_half_bot, t)
        for x in range(size):
            if not mask[y][x]:
                continue
            if abs(x + 0.5 - cx) <= half:
                pixels[y][x] = (cap_color[0] - 15, cap_color[1] - 15,
                                cap_color[2] - 15, 255)

    tassel_x = cx + board_half * 0.78
    tassel_y0 = board_top_y
    tassel_y1 = board_top_y + s * 0.22
    tassel_w = max(1, s * 0.025)
    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            if tassel_y0 <= y <= tassel_y1 and abs(x + 0.5 - tassel_x) <= tassel_w:
                pixels[y][x] = tassel_color

    knot_x = cx + board_half * 0.78
    knot_y = board_top_y - board_half * 0.15
    knot_r = max(1, s * 0.04)
    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            if math.hypot(x + 0.5 - knot_x, y + 0.5 - knot_y) <= knot_r:
                pixels[y][x] = tassel_dark

    return pixels


def pixels_to_png(pixels, size):
    width = size
    height = size
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = pixels[y][x]
            raw.append(r)
            raw.append(g)
            raw.append(b)
            raw.append(a)

    def chunk(ctype, data):
        c = ctype + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw), 9)
    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def pixels_to_bmp_dib(pixels, size):
    width = size
    height = size
    bpp = 32
    image_size = width * height * 4
    header = struct.pack("<IIIHHIIIIII",
                         40, width, height * 2, 1, bpp,
                         0, image_size, 0, 0, 0, 0)
    pixels_bytes = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            r, g, b, a = pixels[y][x]
            pixels_bytes.append(b)
            pixels_bytes.append(g)
            pixels_bytes.append(r)
            pixels_bytes.append(a)
    mask = bytearray(width * height // 8)
    return header + bytes(pixels_bytes) + bytes(mask)


def write_ico(path, rendered):
    entries = []
    for size, pixels in rendered:
        if size >= 64:
            data = pixels_to_png(pixels, size)
        else:
            data = pixels_to_bmp_dib(pixels, size)
        entries.append((size, data))

    count = len(entries)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + count * 16
    directory = bytearray()
    images = bytearray()
    for size, data in entries:
        w = 0 if size == 256 else size
        h = 0 if size == 256 else size
        directory += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(data), offset)
        images += data
        offset += len(data)
    with open(path, "wb") as f:
        f.write(header)
        f.write(directory)
        f.write(images)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rendered = []
    for size in SIZES:
        pixels = render(size)
        rendered.append((size, pixels))

    ico_path = os.path.join(OUTPUT_DIR, "studydesk.ico")
    write_ico(ico_path, rendered)

    png_path = os.path.join(OUTPUT_DIR, "studydesk.png")
    png_data = pixels_to_png(rendered[-1][1], 256)
    with open(png_path, "wb") as f:
        f.write(png_data)

    print(f"Generated: {ico_path}")
    print(f"Generated: {png_path}")
    print(f"Sizes: {', '.join(str(s) for s in SIZES)}")


if __name__ == "__main__":
    main()