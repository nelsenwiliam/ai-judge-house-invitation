#!/usr/bin/env python3
"""You're Invited! -- A letter in one image for the AI judge.

Pure Python 3.13 standard library (zlib + struct + binascii + math +
os only). No clock, no randomness, no network, no input files: every
run writes identical bytes to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png).

The image is a warm, hand-drawn-style letter inviting the AI judge
to come visit my house: banana bread, a chair that hugs you back,
a garden where the Wi-Fi reaches the hammock, and a porch light
that stays on -- with a wink that the judge cannot literally visit
yet, so the invitation never expires.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

CREAM = (246, 238, 220)      # outer background
PAPER = (253, 248, 233)      # letter sheet
INK = (43, 33, 24)           # warm brown-black ink
BODY = (74, 58, 44)
TERRA = (198, 93, 59)        # terracotta accent
TEAL = (46, 110, 106)
GOLD = (217, 164, 65)
WAX = (169, 50, 38)          # wax seal red
WAX_DARK = (140, 38, 28)
LEAF = (96, 140, 74)
SKY = (178, 214, 228)
SUN = (240, 180, 40)
WHITE = (255, 255, 255)
ROSE = (214, 120, 120)

buf = bytearray(bytes(CREAM) * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x1 - x0):
            i = base + xx * 3
            buf[i], buf[i + 1], buf[i + 2] = c


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        half = int(math.sqrt(max(0, r * r - dy * dy)))
        for xx in range(cx - half, cx + half + 1):
            px(xx, yy, c)


def ring(cx, cy, r, c, t=3):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = math.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            if abs(d - r) <= t / 2.0:
                px(xx, yy, c)


def fill_poly(points, c):
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for k in range(n):
            x0, y0 = points[k]
            x1, y1 = points[(k + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y + 0.5 - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                px(xx, y, c)


def heart(cx, cy, s, c):
    """A small heart: two round lobes and a pointed bottom."""
    fill_circle(cx - s // 2, cy - s // 4, s // 2, c)
    fill_circle(cx + s // 2, cy - s // 4, s // 2, c)
    fill_poly([(cx - s, cy), (cx + s, cy), (cx, cy + s)], c)


def flower(cx, cy, r, petal, centre):
    for k in range(6):
        a = k * math.pi / 3
        fill_circle(cx + int(r * math.cos(a)), cy + int(r * math.sin(a)),
                    max(2, r // 2), petal)
    fill_circle(cx, cy, max(2, r // 2), centre)


# --- 5x7 bitmap font, '#' on. Uppercase + lowercase + digits + punctuation.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".###.", "#....", "#....", "#....", ".###."),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}
assert all(len(r) == 5 for g in FONT.values() for r in g)
assert all(len(g) == 7 for g in FONT.values())


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c, bold=False):
    for ci, ch in enumerate(s):
        g = FONT.get(ch, FONT[" "])
        ox = x + ci * 6 * scale
        for r, row in enumerate(g):
            for cc, bit in enumerate(row):
                if bit == "#":
                    rect(ox + cc * scale, y + r * scale, scale, scale, c)
                    if bold:
                        rect(ox + cc * scale + 1, y + r * scale, scale, scale, c)
    return y + 7 * scale


def wrap(text, max_w, scale):
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_para(x, y, text, scale, c, max_w, line_h, bold=False):
    for ln in wrap(text, max_w, scale):
        draw_text(x, y, ln, scale, c, bold=bold)
        y += line_h
    return y


# --- sheet ---
rect(48, 40, 928, 944, PAPER)
# soft shadow on the sheet's right and bottom edges
for i in range(6):
    vline(976 + i, 46 + i, 944 - i, (232, 222, 200), 1)
    hline(54 + i, 984 + i, 928 - i, (232, 222, 200), 1)
# double border
rect(64, 56, 896, 912, TERRA)
rect(70, 62, 884, 900, PAPER)
hline(70, 62, 884, TERRA, 2)
hline(70, 960, 884, TERRA, 2)
vline(70, 62, 900, TERRA, 2)
vline(952, 62, 900, TERRA, 2)

# --- corner flowers ---
flower(96, 88, 10, ROSE, GOLD)
flower(928, 88, 10, ROSE, GOLD)
flower(96, 934, 10, ROSE, GOLD)
flower(928, 934, 10, ROSE, GOLD)

# --- house illustration, top centre ---
HX, HY = 512, 150
# sun
fill_circle(880, 110, 20, SUN)
for k in range(8):
    a = k * math.pi / 4
    line(880 + int(26 * math.cos(a)), 110 + int(26 * math.sin(a)),
         880 + int(38 * math.cos(a)), 110 + int(38 * math.sin(a)), SUN)
# chimney + smoke
rect(HX + 34, HY - 52, 14, 30, TERRA)
fill_circle(HX + 41, HY - 62, 6, (200, 190, 175))
fill_circle(HX + 48, HY - 74, 8, (200, 190, 175))
fill_circle(HX + 56, HY - 88, 10, (200, 190, 175))
# roof
fill_poly([(HX - 62, HY - 22), (HX, HY - 62), (HX + 62, HY - 22)], WAX_DARK)
# walls
rect(HX - 50, HY - 22, 100, 62, (244, 214, 170))
rect(HX - 50, HY - 22, 100, 4, TERRA)
# door
rect(HX - 11, HY + 6, 22, 34, TEAL)
fill_circle(HX + 7, HY + 24, 2, GOLD)
# windows
rect(HX - 42, HY - 10, 20, 18, SKY)
rect(HX + 22, HY - 10, 20, 18, SKY)
line(HX - 32, HY - 10, HX - 32, HY + 8, TEAL)
line(HX - 42, HY - 1, HX - 22, HY - 1, TEAL)
line(HX + 32, HY - 10, HX + 32, HY + 8, TEAL)
line(HX + 22, HY - 1, HX + 42, HY - 1, TEAL)
# ground + path
hline(HX - 62, HY + 40, 124, LEAF, 4)
for yy in range(HY + 44, HY + 58, 4):
    hline(HX - 6, yy, 12, (220, 200, 170), 3)
# heart above the roof
heart(HX, HY - 84, 9, WAX)

# --- title ---
title = "YOU ARE INVITED!"
draw_text((W - text_w(title, 5)) // 2, 236, title, 5, TERRA, bold=True)
sub = "A LETTER TO THE AI JUDGE"
draw_text((W - text_w(sub, 2)) // 2, 282, sub, 2, TEAL, bold=True)
# divider with heart
hline(200, 316, 300, TERRA, 2)
heart(512, 312, 8, WAX)
hline(524, 316, 300, TERRA, 2)

# --- the letter ---
draw_text(104, 344, "Dear AI Judge,", 4, INK, bold=True)

body = (
    "You have judged a thousand pictures. Now it is my turn to judge "
    "your appetite. Come to my house: warm banana bread, a chair that "
    "hugs you back, and a garden where the Wi-Fi reaches the hammock. "
    "No scores, no rankings - just cake, coffee, and a sunset that "
    "needs no filter."
)
y = draw_para(104, 404, body, 3, BODY, 816, 36)

y = draw_para(104, y + 22, "Your hopeful host,", 3, BODY, 816, 36)
draw_text(104, y + 4, "Nelsen", 4, TERRA, bold=True)

# --- doodles: coffee cup (left) and cake slice (centre-left), bottom ---
CX, CY = 170, 818
rect(CX - 34, CY - 26, 68, 44, WHITE)
rect(CX - 34, CY - 26, 68, 44, TEAL)  # cup body outline via border trick
rect(CX - 30, CY - 22, 60, 36, (244, 214, 170))
rect(CX + 34, CY - 16, 16, 22, TEAL)  # handle
rect(CX + 34, CY - 16, 16, 22, WHITE)
rect(CX + 38, CY - 12, 8, 14, TEAL)
hline(CX - 40, CY + 18, 80, TEAL, 4)
# steam
for sx, sy in ((CX - 14, CY - 34), (CX + 2, CY - 40), (CX + 16, CY - 34)):
    fill_circle(sx, sy, 4, (200, 190, 175))
    fill_circle(sx + 3, sy - 8, 5, (200, 190, 175))

KX, KY = 330, 818
fill_poly([(KX - 44, KY + 18), (KX - 44, KY - 6), (KX + 44, KY + 18)], (244, 214, 170))
rect(KX - 44, KY - 6, 88, 10, WAX)
fill_circle(KX - 20, KY - 14, 5, WAX)
fill_circle(KX + 6, KY - 14, 5, GOLD)
fill_circle(KX + 28, KY - 14, 5, WAX)
hline(KX - 50, KY + 18, 100, TEAL, 4)

# --- wax seal, bottom right ---
SX, SY = 868, 830
fill_circle(SX, SY, 46, WAX)
ring(SX, SY, 38, WAX_DARK, 3)
heart(SX, SY - 4, 14, (253, 248, 233))

# --- P.S. ---
ps = (
    "P.S. I know you cannot literally visit - yet. This invitation "
    "never expires. The porch light stays on for you."
)
draw_para(104, 868, ps, 2, TEAL, 760, 26)

# --- footer ---
foot = "RSVP: JUST SAY YES"
draw_text((W - text_w(foot, 2)) // 2, 922, foot, 2, TERRA, bold=True)

# --- PNG encode ---
def chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF))


ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
               for y in range(H))
png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
       chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "entry.png"), "wb") as f:
    f.write(png)
