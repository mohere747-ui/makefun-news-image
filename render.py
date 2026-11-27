#!/usr/bin/env python3
"""Render a 1024x1024 editorial news poster to entry.png.

Six stories, one icon each, all hand-drawn with Pillow primitives.
The picture is composed at 2x resolution and downsampled for clean edges.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2                      # supersampling factor
W = H = 1024
OUT = Path(__file__).resolve().parent / "entry.png"

# Palette: deep navy paper, cool panels, six bright accents.
NAVY = "#091225"
PANEL = "#13203B"
WELL = "#1B2C4C"
EDGE = "#2D4270"
WHITE = "#F3F7FF"
MUTED = "#96A9CC"
CYAN = "#43D9E8"
AMBER = "#FFC05A"
RED = "#FF7466"
GREEN = "#68DCA4"
VIOLET = "#C49BFF"

BOLD_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
)
REG_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
)


def _font_path(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    return None


@lru_cache(maxsize=None)
def font(size: int, bold: bool = True):
    path = _font_path(BOLD_PATHS if bold else REG_PATHS)
    px = size * S
    if path:
        return ImageFont.truetype(path, px)
    return ImageFont.load_default(size=px)


# ---- scaled drawing primitives (all layout numbers are in final pixels) ----

def sc(v: float) -> int:
    return int(round(v * S))


def bb(x0: float, y0: float, x1: float, y1: float) -> tuple[int, int, int, int]:
    return sc(x0), sc(y0), sc(x1), sc(y1)


def pts(seq) -> list[tuple[int, int]]:
    return [(sc(x), sc(y)) for x, y in seq]


def ellipse(d, x0, y0, x1, y1, fill=None, outline=None, width=1):
    d.ellipse(bb(x0, y0, x1, y1), fill=fill, outline=outline, width=sc(width))


def rect(d, x0, y0, x1, y1, radius=0, fill=None, outline=None, width=1):
    d.rounded_rectangle(
        bb(x0, y0, x1, y1), radius=sc(radius), fill=fill, outline=outline, width=sc(width)
    )


def line(d, coordinates, fill, width=1):
    d.line(pts(coordinates), fill=fill, width=sc(width), joint="curve")


def polygon(d, coordinates, fill, outline=None):
    d.polygon(pts(coordinates), fill=fill, outline=outline)


def text(d, xy, string, f, fill, anchor=None):
    d.text((sc(xy[0]), sc(xy[1])), string, font=f, fill=fill, anchor=anchor)


def text_width(f, string) -> float:
    return f.getlength(string) / S


def fit_font(size: int, string: str, max_width: float):
    """Keep headlines big, but never let one escape its card."""
    while size > 26:
        f = font(size)
        if text_width(f, string) <= max_width:
            return f
        size -= 1
    return font(size)


# ---- the six hand-drawn icons ----

def icon_storm(d, cx, cy, a):
    cloud, shade = "#DEE9FA", "#9FB4D8"
    ellipse(d, cx - 32, cy - 22, cx + 4, cy + 12, fill=cloud, outline=shade, width=2)
    ellipse(d, cx - 16, cy - 34, cx + 20, cy + 10, fill=cloud, outline=shade, width=2)
    ellipse(d, cx + 6, cy - 24, cx + 36, cy + 8, fill=cloud, outline=shade, width=2)
    rect(d, cx - 28, cy - 8, cx + 32, cy + 12, radius=8, fill=cloud, outline=shade, width=2)
    for x in (cx - 20, cx - 4, cx + 12):
        line(d, [(x, cy + 20), (x - 7, cy + 34)], CYAN, width=4)
        ellipse(d, x - 9, cy + 32, x - 5, cy + 36, fill=CYAN)
    polygon(d, [
        (cx + 12, cy + 13), (cx + 1, cy + 29), (cx + 11, cy + 29),
        (cx + 3, cy + 43), (cx + 28, cy + 23), (cx + 17, cy + 23),
    ], fill=AMBER, outline="#FFE6A8")


def icon_missile(d, cx, cy, a):
    rect(d, cx - 32, cy + 12, cx + 26, cy + 42, radius=2,
         fill="#2C426B", outline=WHITE, width=2)
    for row in (cy + 19, cy + 29):
        for col in (cx - 24, cx - 8, cx + 8):
            rect(d, col, row, col + 7, row + 5, fill=a)
    line(d, [(cx - 30, cy - 34), (cx + 2, cy + 2)], "#E8EEFF", width=9)
    polygon(d, [(cx + 2, cy + 2), (cx + 12, cy - 5), (cx + 8, cy + 9)], fill=WHITE)
    polygon(d, [(cx - 28, cy - 32), (cx - 40, cy - 24), (cx - 32, cy - 20)], fill=a)
    polygon(d, [(cx - 30, cy - 36), (cx - 40, cy - 42), (cx - 36, cy - 28)], fill=AMBER)
    # Starburst where the missile lands.
    star = []
    for i in range(16):
        ang = i * math.pi / 8
        r = 19 if i % 2 == 0 else 8
        star.append((cx + 10 + r * math.cos(ang), cy + 8 + r * math.sin(ang)))
    polygon(d, star, fill=AMBER, outline=RED)
    ellipse(d, cx + 6, cy + 4, cx + 14, cy + 12, fill=WHITE)


def icon_drone(d, cx, cy, a):
    for end in ((cx - 38, cy - 24), (cx + 38, cy - 24),
                (cx - 38, cy + 24), (cx + 38, cy + 24)):
        arm_start = (cx + (-11 if end[0] < cx else 11),
                     cy + (-5 if end[1] < cy else 5))
        line(d, [arm_start, end], a, width=5)
        ellipse(d, end[0] - 11, end[1] - 6, end[0] + 11, end[1] + 6,
                outline=a, width=3)
    rect(d, cx - 17, cy - 11, cx + 17, cy + 11, radius=8,
         fill="#E8EEFF", outline=a, width=2)
    rect(d, cx - 7, cy - 5, cx + 7, cy + 5, radius=2, fill=WELL)
    ellipse(d, cx - 6, cy + 10, cx + 6, cy + 22, fill="#E8EEFF", outline=a, width=2)
    ellipse(d, cx - 2, cy + 14, cx + 2, cy + 18, fill=a)


def icon_document(d, cx, cy, a):
    polygon(d, [(cx - 24, cy - 36), (cx + 12, cy - 36), (cx + 24, cy - 24),
                (cx + 24, cy + 38), (cx - 24, cy + 38)],
            fill="#EAF1FF", outline=a)
    polygon(d, [(cx + 12, cy - 36), (cx + 24, cy - 24), (cx + 12, cy - 24)],
            fill="#A9C3E8")
    for y in (cy - 12, cy - 2, cy + 8):
        line(d, [(cx - 15, y), (cx + 2, y)], MUTED, width=3)
    ellipse(d, cx + 6, cy + 10, cx + 14, cy + 18, outline=a, width=3)
    ellipse(d, cx + 14, cy + 26, cx + 22, cy + 34, outline=a, width=3)
    line(d, [(cx + 6, cy + 32), (cx + 22, cy + 12)], a, width=4)


def icon_virus(d, cx, cy, a):
    for i in range(12):
        ang = i * 2 * math.pi / 12
        x0, y0 = cx + 21 * math.cos(ang), cy + 21 * math.sin(ang)
        x1, y1 = cx + 37 * math.cos(ang), cy + 37 * math.sin(ang)
        line(d, [(x0, y0), (x1, y1)], a, width=4)
        ellipse(d, x1 - 4, y1 - 4, x1 + 4, y1 + 4, fill=a)
    ellipse(d, cx - 22, cy - 22, cx + 22, cy + 22, fill="#463A72", outline=WHITE, width=2)
    ellipse(d, cx - 12, cy - 12, cx + 12, cy + 12, outline="#EADCFF", width=2)
    for dx, dy in ((-8, -3), (7, -7), (3, 8)):
        ellipse(d, cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3, fill=a)


def icon_euro(d, cx, cy, a):
    ellipse(d, cx - 40, cy - 40, cx + 40, cy + 40, fill="#E8B84B", outline="#FFF0C0", width=3)
    ellipse(d, cx - 32, cy - 32, cx + 32, cy + 32, outline="#B07E22", width=2)
    text(d, (cx, cy), "€", font(54), "#553A10", anchor="mm")


ICONS = {
    "storm": icon_storm,
    "missile": icon_missile,
    "drone": icon_drone,
    "document": icon_document,
    "virus": icon_virus,
    "euro": icon_euro,
}

STORIES = [
    dict(tag="UNITED STATES", accent=AMBER, icon="storm",
         lines=["THANKSGIVING STORMS", "PARADE CANCELLED"], stat="PARADE OFF"),
    dict(tag="UKRAINE", accent=RED, icon="missile",
         lines=["RUSSIAN STRIKE ON KYIV", "ZELENSKY WARNS"], stat="7 HURT"),
    dict(tag="KUWAIT", accent=RED, icon="drone",
         lines=["IRANIAN DRONE KILLS", "2 ITALIANS IN KUWAIT"], stat="IRAN DENIES"),
    dict(tag="UNITED STATES", accent=GREEN, icon="document",
         lines=["US TARIFFS: 14", "PARTNERS"], stat="CHINA 40%"),
    dict(tag="DR CONGO", accent=VIOLET, icon="virus",
         lines=["EBOLA CASES", "PASS 12,000"], stat="12,000+"),
    dict(tag="EUROPE", accent=CYAN, icon="euro",
         lines=["EU BUDGET ROW OVER", "UKRAINE FUNDING"], stat="€1.7TN"),
]


def draw_card(d, story, x, y, w, h, limits):
    accent = story["accent"]
    rect(d, x, y, x + w, y + h, radius=18, fill=PANEL, outline=EDGE, width=2)
    rect(d, x + 18, y + 12, x + 62, y + 15, radius=2, fill=accent)

    # Icon disc, top-left.
    cx, cy = x + 74, y + 78
    ellipse(d, cx - 56, cy - 56, cx + 56, cy + 56, fill=WELL, outline=accent, width=2)
    ICONS[story["icon"]](d, cx, cy, accent)

    # Region tag: coloured capsule beside the disc.
    tag_f = font(20)
    tag = story["tag"]
    tag_w = text_width(tag_f, tag)
    tx0, ty0 = x + 146, y + 46
    rect(d, tx0 - 10, ty0 - 6, tx0 + tag_w + 10, ty0 + 33, radius=8,
         fill=WELL, outline=accent, width=2)
    text(d, (tx0, ty0), tag, tag_f, accent)

    # Two-line headline across the full card width.
    inner = w - 36
    headline_fonts = [fit_font(34, s, inner) for s in story["lines"]]
    for i, (headline, hf) in enumerate(zip(story["lines"], headline_fonts)):
        hy = y + (132 if i == 0 else 168)
        text(d, (x + 18, hy), headline, hf, WHITE)

    # One big stat, anchored by an accent dot.
    stat_f = fit_font(38, story["stat"], inner - 22)
    ellipse(d, x + 21, y + 229, x + 31, y + 239, fill=accent)
    text(d, (x + 40, y + 208), story["stat"], stat_f, accent)

    # Guard: every string stays inside the card with right padding.
    for string, f, px, py in (
        (tag, tag_f, tx0, ty0),
        (story["lines"][0], headline_fonts[0], x + 18, y + 132),
        (story["lines"][1], headline_fonts[1], x + 18, y + 168),
        (story["stat"], stat_f, x + 40, y + 208),
    ):
        bx0, by0, bx1, by1 = f.getbbox(string)
        limits.append((string,
                       x + 12 <= px + bx0 / S and px + bx1 / S <= x + w - 12,
                       y + 8 <= py + by0 / S and py + by1 / S <= y + h - 4))


def render() -> Image.Image:
    img = Image.new("RGB", (W * S, H * S), NAVY)
    d = ImageDraw.Draw(img)

    # Header.
    rect(d, 24, 44, 30, 96, radius=3, fill=CYAN)
    text(d, (50, 13), "THURSDAY", font(19), MUTED)
    text(d, (48, 34), "26 NOVEMBER 2026", font(58), WHITE)
    text(d, (50, 108), "THE DAY IN SIX PICTURES", font(23), CYAN)
    mark = "WORLD NEWS"
    mark_f = font(18)
    mark_w = text_width(mark_f, mark)
    text(d, (976 - mark_w, 112), mark, mark_f, MUTED)
    line(d, [(40, 152), (984, 152)], EDGE, width=2)
    line(d, [(40, 152), (184, 152)], CYAN, width=3)

    margin, gap = 40, 16
    card_w = (W - 2 * margin - gap) // 2
    card_h = 260
    row_gap = 16
    top = 176
    limits = []
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (card_w + gap)
        y = top + row * (card_h + row_gap)
        draw_card(d, story, x, y, card_w, card_h, limits)

    for label, inside_x, inside_y in limits:
        if not (inside_x and inside_y):
            raise RuntimeError(f"text escapes its card: {label!r} "
                               f"(x_ok={inside_x}, y_ok={inside_y})")

    return img.resize((W, H), Image.Resampling.LANCZOS)


def main() -> None:
    poster = render()
    poster.save(OUT, "PNG", optimize=True)
    size_kib = OUT.stat().st_size / 1024
    print(f"wrote {OUT.name}: {poster.width}x{poster.height} PNG, {size_kib:.1f} KiB")


if __name__ == "__main__":
    main()
