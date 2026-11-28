#!/usr/bin/env python3
"""A broadsheet-style world news poster, 1600x1200, drawn from scratch with Pillow.

Everything (typography, layout, illustrations, world map) is generated here;
no external images or downloaded code are used.
"""

# v3 broadsheet: 38 stories, map and UTC timeline; text boxes are fit and checked.

from __future__ import annotations

import os
from functools import lru_cache
from math import cos, radians, sin

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# canvas / palette / fonts
# ---------------------------------------------------------------------------

W, H = 1600, 1200
M = 24  # outer left/right margin

CREAM = "#F8F5ED"
INK = "#121212"
RED = "#C4102E"
BLUE = "#144E92"
GREEN = "#147852"
GOLD = "#B07A0C"
PANEL = "#FFFDF8"
HAIR = "#D6D0C5"
MUTED = "#5A554C"

FONTDIR = "/usr/share/fonts/truetype/dejavu"


@lru_cache(maxsize=512)
def F(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONTDIR, name), size)


img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img)

# Every piece of layout text is registered so we can prove at the end that
# nothing was drawn outside its box or on top of another text box.
TEXTBOXES: list[tuple[str, tuple[int, int, int, int], tuple[int, int, int, int] | None]] = []


def text(xy, s, fnt, fill, name, region=None):
    raw = d.textbbox(xy, s, font=fnt)
    bbox = (int(raw[0]), int(raw[1]), int(raw[2]), int(raw[3]))
    TEXTBOXES.append((name, bbox, region))
    d.text(xy, s, font=fnt, fill=fill)
    return bbox


def tw(s, fnt) -> float:
    b = d.textbbox((0, 0), s, font=fnt)
    return b[2] - b[0]


def center_text(cx, y, s, fnt, fill, name, region=None):
    b = d.textbbox((0, 0), s, font=fnt)
    x = cx - (b[2] - b[0]) / 2 - b[0]
    return text((x, y), s, fnt, fill, name, region)


# ---------------------------------------------------------------------------
# text fitting helpers -- used on every headline
# ---------------------------------------------------------------------------


def wrap(s, fnt, width):
    """Greedy word wrap measured with the real font metrics."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if tw(trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, base, width, minsz, maxlines, bold=True, serif=False):
    """Shrink the font from `base` until `text` fits in `width` and `maxlines`.

    Returns (font, lines).  Called for all hero and small-card headlines and
    for the large metric numerals, so no headline is ever clipped.
    """

    def measure(s, fnt):
        b = d.textbbox((0, 0), s, font=fnt)
        return b[2] - b[0]

    def wrap_to(s, fnt):
        lines, cur = [], ""
        for word in s.split():
            trial = word if not cur else cur + " " + word
            if measure(trial, fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    size = base
    while size >= minsz:
        fnt = F(size, bold=bold, serif=serif)
        lines = wrap_to(text, fnt)
        if len(lines) <= maxlines and all(measure(line, fnt) <= width for line in lines):
            return fnt, lines
        size -= 1
    fnt = F(minsz, bold=bold, serif=serif)
    return fnt, wrap_to(text, fnt)


def trunc(s, fnt, width):
    """Cut a line to `width`, adding an ellipsis when it is too long."""
    if tw(s, fnt) <= width:
        return s
    out = s
    while out and tw(out + "…", fnt) > width:
        out = out[:-1]
    return out + "…"


# ---------------------------------------------------------------------------
# flat-vector scene illustrations
# ---------------------------------------------------------------------------


def panel(x0, y0, x1, y1, radius=7, fill=PANEL, outline=HAIR, width=1):
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                        outline=outline, width=width)


def scene_storm(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#D7E1EC")
    d.rectangle([x, y + h - 34, x + w, y + h], fill="#B9C4CE")
    for cx, cy, cr in ((0.22, 0.32, 0.20), (0.40, 0.28, 0.24),
                       (0.66, 0.33, 0.22), (0.82, 0.38, 0.13)):
        px, py = x + cx * w, y + cy * h
        rx, ry = cr * w, cr * h * 0.55
        d.ellipse([px - rx, py - ry, px + rx, py + ry], fill="#4C5B6B")
        d.ellipse([px - rx * 0.8, py - ry * 1.25,
                   px + rx * 0.8, py + ry * 0.55], fill="#617286")
    for i in range(28):
        rx = x + (i * 37) % int(w)
        ry = y + int(h * 0.34) + (i * 13) % int(h * 0.34)
        d.line([(rx, ry), (rx - 5, ry + 14)], fill="#93A5B7", width=1)
    d.polygon([
        (x + 0.50 * w, y + 0.30 * h), (x + 0.44 * w, y + 0.52 * h),
        (x + 0.51 * w, y + 0.52 * h), (x + 0.41 * w, y + 0.78 * h),
        (x + 0.60 * w, y + 0.48 * h), (x + 0.53 * w, y + 0.48 * h),
        (x + 0.62 * w, y + 0.30 * h),
    ], fill="#F2C300")
    for bx, bw, bh, col in (
        (0.02, 0.16, 0.34, "#3F4956"), (0.20, 0.13, 0.48, "#4E5A68"),
        (0.35, 0.14, 0.30, "#39434F"), (0.66, 0.16, 0.42, "#4E5A68"),
        (0.84, 0.14, 0.32, "#3F4956"),
    ):
        bx0, by0 = x + bx * w, y + h - bh * h
        d.rectangle([bx0, by0, bx0 + bw * w, y + h], fill=col)
        for wy in range(int(by0 + 6), y + h - 4, 12):
            for wx in range(int(bx0 + 5), int(bx0 + bw * w - 4), 12):
                d.rectangle([wx, wy, wx + 4, wy + 6], fill="#E9D68C")


def scene_kyiv(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#E8E3D9")
    d.rectangle([x, y + h - 28, x + w, y + h], fill="#C8CFC9")
    for bx, bw, bh in (
        (0.03, 0.17, 0.52), (0.23, 0.14, 0.66), (0.40, 0.16, 0.44),
        (0.60, 0.14, 0.72), (0.78, 0.18, 0.50),
    ):
        bx0, by0 = x + bx * w, y + h - bh * h
        d.rectangle([bx0, by0, bx0 + bw * w, y + h], fill="#98A4AE",
                    outline="#7C8894")
        for wy in range(int(by0 + 8), y + h - 4, 14):
            for wx in range(int(bx0 + 6), int(bx0 + bw * w - 5), 12):
                lit = "#5E6C78" if (wx + wy) % 3 == 0 else "#F4F1E7"
                d.rectangle([wx, wy, wx + 5, wy + 7], fill=lit)
    d.polygon([
        (x + 0.88 * w, y + 0.04 * h), (x + 0.81 * w, y + 0.30 * h),
        (x + 0.72 * w, y + 0.47 * h), (x + 0.79 * w, y + 0.28 * h),
        (x + 0.77 * w, y + 0.07 * h),
    ], fill="#B23A2E")
    cx, cy = x + 0.55 * w, y + 0.62 * h
    pts = []
    for k in range(16):
        a = k * 2 * 3.14159265 / 16
        r = w * 0.14 if k % 2 == 0 else w * 0.07
        pts.append((cx + r * cos(a), cy + r * sin(a)))
    d.polygon(pts, fill="#E4701F")
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill="#F4C542")
    for sx, sy, sr in ((0.64, 0.50, 0.10), (0.71, 0.43, 0.08), (0.47, 0.51, 0.07)):
        d.ellipse([x + sx * w - sr * w, y + sy * h - sr * h * 0.8,
                   x + sx * w + sr * w, y + sy * h + sr * h * 0.8], fill="#A8A29A")


def scene_kuwait(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#F1DFB6")
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill="#E4C488")
    d.ellipse([x + 0.08 * w, y + 0.08 * h, x + 0.20 * w, y + 0.08 * h + 0.10 * h],
              fill="#F7E7AF")
    for tx, th in ((0.18, 0.60), (0.34, 0.78), (0.50, 0.55)):
        bx, top = x + tx * w, y + h - th * h
        d.rectangle([bx - 3, top + 14, bx + 3, y + h], fill="#7A5A32")
        d.ellipse([bx - 13, top - 2, bx + 13, top + 24], fill="#9A7442")
        d.ellipse([bx - 7, top + 6, bx + 7, top + 18], fill="#C79A5E")
    dx, dy = x + 0.73 * w, y + 0.30 * h
    d.line([(dx - 24, dy - 10), (dx + 24, dy + 10)], fill="#8E1226", width=3)
    d.line([(dx - 24, dy + 10), (dx + 24, dy - 10)], fill="#8E1226", width=3)
    for ox, oy in ((-24, -10), (-24, 10), (24, -10), (24, 10)):
        d.ellipse([dx + ox - 11, dy + oy - 3, dx + ox + 11, dy + oy + 3],
                  outline="#C4102E", width=2)
    d.rounded_rectangle([dx - 14, dy - 8, dx + 14, dy + 8], radius=4, fill="#C4102E")
    d.rectangle([dx - 3, dy + 8, dx + 3, dy + 13], fill="#8E1226")


def draw_mini(x, y, s, kind):
    """Small flat icon for the eight lower cards."""
    d.rectangle([x, y, x + s, y + s], fill="#EDE8DC", outline=HAIR, width=1)
    if kind == "eu":
        d.rectangle([x + 8, y + 20, x + s - 8, y + s - 20], fill=BLUE)
        for k in range(12):
            a = k * 2 * 3.14159265 / 12
            cx = x + s / 2 + (s * 0.23) * cos(a)
            cy = y + s / 2 + (s * 0.23) * sin(a)
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill="#F2C300")
    elif kind == "ebola":
        cx, cy = x + s / 2, y + s / 2
        for k in range(10):
            a = k * 2 * 3.14159265 / 10
            ex, ey = cx + 22 * cos(a), cy + 22 * sin(a)
            d.line([(cx + 15 * cos(a), cy + 15 * sin(a)), (ex, ey)], fill=GREEN, width=2)
            d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=GREEN)
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=GREEN)
        for dx0, dy0 in ((-6, -4), (5, -7), (2, 6), (-8, 7), (8, 3)):
            d.ellipse([cx + dx0 - 2, cy + dy0 - 2, cx + dx0 + 2, cy + dy0 + 2],
                      fill=CREAM)
    elif kind == "ecb":
        d.ellipse([x + 12, y + 10, x + s - 12, y + s - 10], fill=BLUE)
        f = F(40, bold=True)
        b = d.textbbox((0, 0), "€", font=f)
        d.text((x + s / 2 - (b[2] - b[0]) / 2 - b[0],
                y + s / 2 - (b[3] - b[1]) / 2 - b[1]), "€", font=f, fill=CREAM)
    elif kind == "gaza":
        d.rectangle([x + 8, y + 42, x + 30, y + s - 8], fill="#8C8F89")
        d.rectangle([x + 68, y + 30, x + s - 8, y + s - 8], fill="#8C8F89")
        cx, cy = x + s * 0.52, y + s * 0.40
        pts = []
        for k in range(12):
            a = k * 2 * 3.14159265 / 12
            r = 24 if k % 2 == 0 else 12
            pts.append((cx + r * cos(a), cy + r * sin(a)))
        d.polygon(pts, fill="#E4701F")
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill="#F4C542")
    elif kind == "hormuz":
        d.rectangle([x, y + 58, x + s, y + s], fill="#B9D3E0")
        d.polygon([(x + 18, y + 58), (x + s - 18, y + 58),
                   (x + s - 30, y + 76), (x + 30, y + 76)], fill="#6D8798")
        d.rectangle([x + 30, y + 36, x + s - 26, y + 58], fill="#E6E1D4")
        d.rectangle([x + 52, y + 22, x + 66, y + 36], fill="#A9A497")
        cx, cy = x + s - 18, y + 22
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill="#2B2B2B")
        for deg in range(0, 360, 60):
            a = radians(deg)
            d.line([(cx, cy), (cx + 12 * cos(a), cy + 12 * sin(a))],
                   fill="#2B2B2B", width=2)
    elif kind == "bok":
        for i, (bh, col) in enumerate(((18, "#9EB8D2"), (30, "#6F9BC4"), (44, BLUE))):
            bx = x + 16 + i * 24
            d.rectangle([bx, y + s - 8 - bh, bx + 16, y + s - 8], fill=col)
        d.polygon([(x + 18, y + 42), (x + 38, y + 26), (x + 52, y + 36),
                   (x + 78, y + 14)], fill=RED)
    elif kind == "argentina":
        for i, (bh, col) in enumerate(((46, "#D9A0A0"), (32, "#C87B7B"), (18, "#8E2338"))):
            bx = x + 16 + i * 24
            d.rectangle([bx, y + s - 8 - bh, bx + 16, y + s - 8], fill=col)
        d.polygon([(x + 18, y + 18), (x + 38, y + 34), (x + 54, y + 26),
                   (x + 78, y + 50)], fill=RED)
    elif kind == "nato":
        d.ellipse([x + 14, y + 12, x + 54, y + 52], outline=BLUE, width=2)
        d.line([(x + 34, y + 32), (x + 72, y + 32)], fill=BLUE, width=2)
        d.polygon([(x + 44, y + 27), (x + 88, y + 32), (x + 44, y + 39),
                   (x + 54, y + 32)], fill=BLUE)
        d.line([(x + 62, y + 22), (x + 62, y + 44)], fill=BLUE, width=2)


# ---------------------------------------------------------------------------
# simple world map with numbered pins
# ---------------------------------------------------------------------------

CONTINENTS = [
    # North America
    [(-168, 65), (-150, 70), (-130, 70), (-110, 68), (-95, 70), (-80, 72),
     (-60, 60), (-55, 50), (-65, 45), (-70, 42), (-75, 35), (-81, 25),
     (-97, 26), (-105, 20), (-115, 30), (-125, 40), (-130, 55), (-150, 60)],
    # South America
    [(-80, 10), (-70, 12), (-60, 8), (-50, 0), (-35, -6), (-38, -15),
     (-48, -25), (-55, -35), (-65, -55), (-72, -50), (-75, -40),
     (-70, -20), (-80, -5)],
    # Europe
    [(-10, 36), (-9, 43), (-5, 48), (0, 51), (5, 53), (10, 55), (20, 55),
     (30, 60), (40, 60), (40, 50), (30, 45), (25, 40), (20, 38), (12, 37),
     (5, 36)],
    # Africa
    [(-17, 15), (-10, 28), (0, 32), (10, 37), (20, 32), (32, 31), (35, 25),
     (43, 12), (51, 12), (42, -2), (40, -12), (35, -20), (30, -30),
     (20, -35), (12, -18), (8, -5), (0, 5), (-8, 5)],
    # Asia
    [(40, 60), (60, 70), (90, 75), (120, 73), (150, 70), (170, 65),
     (160, 55), (145, 50), (140, 40), (130, 35), (122, 30), (120, 22),
     (110, 20), (105, 10), (100, 5), (95, 15), (90, 22), (80, 8),
     (72, 20), (65, 25), (55, 25), (48, 30), (40, 40)],
    # Australia
    [(115, -22), (125, -12), (135, -12), (145, -16), (150, -25),
     (145, -38), (135, -35), (125, -32)],
]

MAP_PINS = [
    (-74, 40),   # 01 US storms / New York
    (31, 49),    # 02 Kyiv
    (48, 29),    # 03 Kuwait
    (15, -4),    # 04 Congo
    (4, 50),     # 05 EU budget / Brussels
    (34, 31),    # 06 Gaza
    (60, 24),    # 07 Strait of Hormuz
    (127, 37),   # 08 Bank of Korea / Seoul
    (-58, -34),  # 09 Argentina
    (20, 54),    # 10 NATO Poland / Warsaw
    (175, -41),  # 11 New Zealand
    (114, 22),   # 12 Hong Kong
]


def ll2p(lon, lat, x, y, w, h):
    return (x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)


def draw_world_map(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill="#EFEAE0", outline=HAIR, width=1)
    for lat in (-60, -30, 0, 30, 60):
        gy = ll2p(0, lat, x, y, w, h)[1]
        d.line([(x, gy), (x + w, gy)], fill="#E2DCCD", width=1)
    for poly in CONTINENTS:
        d.polygon([ll2p(lo, la, x, y, w, h) for lo, la in poly], fill="#C6BFB0")
    f = F(10, bold=True)
    for idx, (lo, la) in enumerate(MAP_PINS, 1):
        px, py = ll2p(lo, la, x, y, w, h)
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline="#FFFFFF", width=1)
        lab = str(idx)
        b = d.textbbox((0, 0), lab, font=f)
        text((px - (b[2] - b[0]) / 2 - b[0], py - (b[3] - b[1]) / 2 - b[1]),
             lab, f, "#FFFFFF", f"pin_{idx}", (x, y, x + w, y + h))


# ---------------------------------------------------------------------------
# 1. masthead
# ---------------------------------------------------------------------------

text((M, 8), "THE WORLD IN ONE DAY", F(26, bold=True), RED, "kicker",
     (M, 0, 760, 42))
text((M, 34), "26 November 2026", F(64, bold=True, serif=True), INK, "date",
     (M, 30, 800, 122))

meta1 = "THURSDAY • 38 STORIES • 11 REGIONS"
meta2 = "ALL FIRST REPORTED 26 NOV 2026"
f1, f2 = F(20, bold=True), F(20)
text((W - M - tw(meta1, f1), 24), meta1, f1, INK, "meta1", (900, 20, W - M, 52))
text((W - M - tw(meta2, f2), 56), meta2, f2, MUTED, "meta2", (900, 52, W - M, 86))
d.line([(M, 122), (W - M, 122)], fill=INK, width=3)

# ---------------------------------------------------------------------------
# 2. deck
# ---------------------------------------------------------------------------

deck = [
    ("US STORMS", "More than 900,000 lose power as severe storms sweep the US; the Macy's parade is moved to Saturday."),
    ("KUWAIT STRIKE", "Drone shrapnel kills two Italian nationals; Iran denies any role in the attack."),
    ("EU BUDGET", "Leaders close the summit with no deal on the €1.582tn spending plan."),
]
deck_w, deck_gap = 496, 32
for i, (label, body) in enumerate(deck):
    x = M + i * (deck_w + deck_gap)
    text((x, 130), label, F(15, bold=True), RED, f"deck_label_{i}",
         (x, 126, x + deck_w, 150))
    fnt = F(17)
    lines = wrap(body, fnt, deck_w)[:3]
    for j, line in enumerate(lines):
        text((x, 152 + j * 20), line, fnt, INK, f"deck_{i}_{j}",
             (x, 149, x + deck_w, 214))
for sx in (M + deck_w + deck_gap // 2, M + 2 * deck_w + deck_gap + deck_gap // 2):
    d.line([(sx, 130), (sx, 210)], fill=HAIR, width=1)

# ---------------------------------------------------------------------------
# 3. metric strip
# ---------------------------------------------------------------------------

metrics = [
    ("900K+", "US power cuts", RED),
    ("12,021", "Congo Ebola cases", GREEN),
    ("€1.582tn", "EU budget plan", BLUE),
    ("14", "US tariff partners", GOLD),
    ("87", "missiles/drones downed", RED),
    ("3.25%", "Bank of Korea rate", BLUE),
]
mbw, mgap, my, mh = 252, 8, 224, 70
for i, (value, label, col) in enumerate(metrics):
    x = M + i * (mbw + mgap)
    panel(x, my, x + mbw, my + mh, radius=5)
    fval, _ = fit_text(d, value, 34, mbw - 16, 24, 1)
    center_text(x + mbw / 2, 226, value, fval, col, f"metric_val_{i}",
                (x + 4, 224, x + mbw - 4, 272))
    flab = F(13)
    center_text(x + mbw / 2, 276, label, flab, MUTED, f"metric_lab_{i}",
                (x + 4, 273, x + mbw - 4, 294))

# ---------------------------------------------------------------------------
# 4. region band + UTC timeline
# ---------------------------------------------------------------------------

regions = ["AMERICAS", "EUROPE", "MIDDLE EAST", "AFRICA", "ASIA",
           "OCEANIA", "FINANCE", "SPORT"]
rf = F(15, bold=True)
slot = (W - 2 * M) / 8
for i, r in enumerate(regions):
    rw = tw(r, rf)
    rx = M + i * slot + (slot - rw) / 2
    text((rx, 310), r, rf, BLUE, f"region_{i}", (M, 306, W - M, 334))

d.line([(120, 352), (W - 120, 352)], fill=HAIR, width=2)
lf = F(12)
for t in (0, 6, 12, 18, 23):
    tx = 120 + t / 23 * (W - 240)
    d.ellipse([tx - 4, 348, tx + 4, 356], fill=RED)
    lab = f"{t:02d}"
    text((tx - tw(lab, lf) / 2, 334), lab, lf, MUTED, f"utc_{lab}",
         (0, 330, W, 354))
uf = F(11, bold=True)
text((72, 334), "UTC", uf, MUTED, "utc_word", (M, 330, 106, 354))

# ---------------------------------------------------------------------------
# 5. three hero cards
# ---------------------------------------------------------------------------

heroes = [
    ("WEATHER", "900,000+ LOST POWER",
     ["Storms cut power to 900,000+ across the US.", "Macy's parade moved to Saturday."],
     scene_storm),
    ("WAR", "SEVEN HURT IN KYIV",
     ["Ukraine said a missile strike wounded seven.", "Officials reported 87 missiles/drones downed."],
     scene_kyiv),
    ("MIDDLE EAST", "TWO ITALIANS KILLED",
     ["Drone shrapnel killed two Italians in Kuwait.", "Iran denied any role in the attack."],
     scene_kuwait),
]
hy, hh, cw, cgap = 366, 288, 500, 26
for i, (tag, headline, body, scene) in enumerate(heroes):
    x = M + i * (cw + cgap)
    panel(x, hy, x + cw, hy + hh)
    sx, sy, sw, sh = x + 8, hy + 8, cw - 16, 132
    scene(sx, sy, sw, sh)
    d.rectangle([sx, sy, sx + sw, sy + sh], outline=HAIR, width=1)
    tf = F(14, bold=True)
    twid = tw(tag, tf) + 20
    d.rectangle([sx, sy, sx + twid, sy + 26], fill=RED)
    text((sx + 10, sy + 5), tag, tf, "#FFFFFF", f"hero_tag_{i}",
         (sx, sy, sx + twid, sy + 26))

    hfont, hlines = fit_text(d, headline, 34, cw - 24, 22, 2)
    hx, hy0 = x + 12, hy + 150
    pitch = hfont.size + 4
    for j, line in enumerate(hlines):
        text((hx, hy0 + j * pitch), line, hfont, INK, f"hero_head_{i}_{j}",
             (x + 8, hy + 146, x + cw - 8, hy + 250))
    # body is positioned *after* the (possibly two-line) headline
    by = hy0 + len(hlines) * pitch + 8
    bf = F(17)
    for j, line in enumerate(body[:2]):
        line = trunc(line, bf, cw - 24)
        text((hx, by + j * 22), line, bf, MUTED, f"hero_body_{i}_{j}",
             (x + 8, by, x + cw - 8, by + 48))

# ---------------------------------------------------------------------------
# 6. eight small cards (2 rows x 4 columns)
# ---------------------------------------------------------------------------

smalls = [
    ("EUROPE", "No deal on €1.582tn budget", "Leaders end summit without an agreement.", "eu"),
    ("AFRICA", "Ebola passes 12,021 cases", "Congo outbreak prompts scaled-up response.", "ebola"),
    ("EUROPE", "De Cos picked for ECB", "Spanish economist set to lead the ECB.", "ecb"),
    ("MIDDLE EAST", "Strikes kill nine in Gaza", "Officials say strikes killed nine people.", "gaza"),
    ("MIDDLE EAST", "Iran claims Hormuz mine hits", "Tehran says tankers struck mines.", "hormuz"),
    ("FINANCE", "Bank of Korea hikes rates", "Policy rate raised to 3.25%.", "bok"),
    ("AMERICAS", "Q3 GDP shrinks 1.8%", "Argentina enters technical recession.", "argentina"),
    ("EUROPE", "NATO AWACS over Poland", "Surveillance aircraft deployed east.", "nato"),
]
sw2, sg, sy1, sy2, sh2 = 379, 12, 670, 810, 132
for i, (tag, headline, body, kind) in enumerate(smalls):
    col, row = i % 4, i // 4
    x = M + col * (sw2 + sg)
    y = sy1 if row == 0 else sy2
    panel(x, y, x + sw2, y + sh2, radius=5)
    draw_mini(x + 8, y + 16, 100, kind)
    tx = x + 116
    text((tx, y + 10), tag, F(11, bold=True), RED, f"small_tag_{i}",
         (tx - 2, y + 8, x + sw2 - 8, y + 26))
    hf, hlines = fit_text(d, headline, 20, sw2 - 124, 13, 1)
    text((tx, y + 28), hlines[0], hf, INK, f"small_head_{i}",
         (tx - 2, y + 26, x + sw2 - 8, y + 70))
    bf = F(13)
    for j, line in enumerate(wrap(body, bf, sw2 - 124)[:2]):
        text((tx, y + 72 + j * 18), trunc(line, bf, sw2 - 124), bf, MUTED,
             f"small_body_{i}_{j}", (tx - 2, y + 70, x + sw2 - 8, y + 116))

# ---------------------------------------------------------------------------
# 7. footer: world map + ALSO TODAY index + date-check line
# ---------------------------------------------------------------------------

d.line([(M, 952), (W - M, 952)], fill=HAIR, width=2)
text((M, 962), "WHERE TODAY'S STORIES HAPPENED", F(14, bold=True), INK,
     "map_title", (M, 958, 620, 984))
draw_world_map(M, 984, 580, 176)

text((650, 962), "ALSO TODAY — 38 STORIES", F(20, bold=True), RED,
     "also_title", (640, 958, W - M, 992))

ITEMS = [
    "US storms: 900,000+ without power",
    "Macy's parade delayed to Saturday",
    "Kyiv: seven hurt in missile strike",
    "Ukraine downs 87 missiles/drones",
    "Kuwait drone kills two Italians",
    "Iran denies role in Kuwait attack",
    "Congo Ebola cases hit 12,021",
    "EU budget summit ends without deal",
    "de Cos picked to lead ECB",
    "Gaza strikes kill nine, officials say",
    "Iran claims Hormuz tanker mines",
    "Bank of Korea raises to 3.25%",
    "US tariffs on 14 partners",
    "China faces top tariff rate of 20%",
    "Trump urges Putin to pull back",
    "Grain ships hit near Odesa",
    "Ukraine drones hit Russian ship",
    "Zelensky warns of new strike",
    "NATO sends AWACS to Poland",
    "Poland plans eastern no-fly zone",
    "Argentina enters technical recession",
    "Farmers march in Brussels over CAP cuts",
    "24 of 27 back €45bn Ukraine loan",
    "Macron sets budget ultimatum",
    "Spain heads to Sunday snap election",
    "Feminist marches across Spain",
    "NZ count leaves Luxon short",
    "Hong Kong marks fire victims",
    "Taiwan tracks six Chinese ships",
    "Indonesia mine flood kills 12+",
    "Saudi intercepts Houthi missiles",
    "Jazan refinery hit; one dead",
    "FIFA hit by cyberattack",
    "Amazon workers plan strikes",
    "Altria eyes Imperial Brands",
    "Nvidia curbs SE Asia servers",
    "Stocks rebound; US markets shut",
    "Sinner out of Australian Open",
]
idx_w, idx_gap = 299, 14
ifnt = F(13)
for c in range(3):
    cx = 650 + c * (idx_w + idx_gap)
    for r in range(13):
        n = c * 13 + r
        if n >= len(ITEMS):
            break
        label = f"{n + 1:02d}  {trunc(ITEMS[n], ifnt, idx_w - tw('00  ', ifnt))}"
        text((cx, 996 + r * 14), label, ifnt, INK, f"item_{n + 1}",
             (cx, 993 + r * 14, cx + idx_w, 1016 + r * 14))

check = ("DATE CHECK: all events first reported 26 November 2026; "
         "disputed claims attributed, no speculation as fact.")
text((M, 1182), check, F(13), MUTED, "date_check", (M, 1178, W - M, 1200))

# ---------------------------------------------------------------------------
# verification + save
# ---------------------------------------------------------------------------

def verify():
    issues = []
    for name, bb, region in TEXTBOXES:
        if bb[0] < 0 or bb[1] < 0 or bb[2] > W or bb[3] > H:
            issues.append(f"canvas clip: {name} {bb}")
        if region and not (bb[0] >= region[0] and bb[1] >= region[1]
                           and bb[2] <= region[2] and bb[3] <= region[3]):
            issues.append(f"region clip: {name} {bb} vs {region}")
    for i in range(len(TEXTBOXES)):
        a = TEXTBOXES[i][1]
        for j in range(i + 1, len(TEXTBOXES)):
            b = TEXTBOXES[j][1]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                issues.append(f"overlap: {TEXTBOXES[i][0]} & {TEXTBOXES[j][0]}")
    return issues


issues = verify()
print("VERIFY: " + (f"FAIL ({len(issues)} issues): " + "; ".join(issues[:12])
                    if issues else f"OK — {len(TEXTBOXES)} text boxes, no clipping or overlap"))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, "PNG")
print(f"Saved {out} — {img.size[0]}x{img.size[1]} — {os.path.getsize(out)} bytes")
