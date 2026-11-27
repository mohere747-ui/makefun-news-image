"""Render the 26 November 2026 world-news poster as entry.png.

Self-contained: uses only Pillow and the DejaVu fonts shipped with the system.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

WIDTH = HEIGHT = 1024
MARGIN = 46
GAP = 16
GRID_TOP = 172
CARD_W = (WIDTH - 2 * MARGIN - GAP) // 2
CARD_H = (HEIGHT - GRID_TOP - 46 - 3 * GAP) // 4

CANVAS = "#080d18"
CARD_BG = "#111a2b"
CARD_EDGE = "#2a3952"
INK = "#f2f6ff"
MUTED = "#a9b8cf"
ACCENT = "#5ad1ff"

TITLE = "THE WORLD / 26 NOVEMBER 2026"

# tag, headline, one-sentence detail, accent colour
STORIES = [
    ("WAR", "Kyiv under missile barrage",
     "Seven were wounded and Zelensky warned of a new mass strike.", "#ff6b81"),
    ("US", "Storms sweep the US",
     "Over 600,000 lost power and Macy's 100th parade was postponed.", "#ffc857"),
    ("MIDEAST", "Drone over Kuwait",
     "Two Italian technicians were killed; Iran denies involvement.", "#ff8f5a"),
    ("TRADE", "Tariffs on 14 partners",
     "Washington proposes 15-25% and China faces 20%.", "#7ee787"),
    ("HEALTH", "Ebola passes 12,000",
     "The Congo outbreak is now the second-largest ever.", "#5ad1ff"),
    ("ASIA", "Kim vows more nukes",
     "He pledged more nuclear weapons after inspecting nuclear sites.", "#c9a7ff"),
    ("SPACE", "One million satellites OK'd",
     "The FCC cleared SpaceX's data-center plan; scientists are skeptical.", "#8fb8ff"),
    ("EU", "Budget standoff",
     "A 1.7 trillion euro plan and Ukraine aid remain deadlocked.", "#f7a8d8"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [FONT_DIR / name, Path("/usr/share/fonts/dejavu") / name, Path(name)]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.truetype(name, size)


def wrap(text: str, face: ImageFont.FreeTypeFont, max_width: float,
         draw: ImageDraw.ImageDraw) -> list[str]:
    """Greedy word wrap, with a character-level fallback for overlong words."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=face) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        if draw.textlength(word, font=face) <= max_width:
            current = word
            continue
        chunk = ""
        for char in word:
            if chunk and draw.textlength(chunk + char, font=face) > max_width:
                lines.append(chunk)
                chunk = ""
            chunk += char
        current = chunk
    if current:
        lines.append(current)
    return lines


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), CANVAS)
    draw = ImageDraw.Draw(image)

    # Masthead.
    draw.text((MARGIN, 36), "DAILY GLOBAL BRIEF", font=font(14, True), fill=ACCENT)
    title_size = 48
    while title_size > 24 and draw.textlength(TITLE, font=font(title_size, True)) > WIDTH - 2 * MARGIN:
        title_size -= 1
    draw.text((MARGIN, 64), TITLE, font=font(title_size, True), fill=INK)
    draw.line([(MARGIN, 136), (WIDTH - MARGIN, 136)], fill=CARD_EDGE, width=2)
    draw.line([(MARGIN, 136), (MARGIN + 150, 136)], fill=ACCENT, width=4)

    # Eight cards, two columns by four rows.
    for index, (tag, headline, detail, colour) in enumerate(STORIES):
        col, row = index % 2, index // 2
        x = MARGIN + col * (CARD_W + GAP)
        y = GRID_TOP + row * (CARD_H + GAP)

        draw.rounded_rectangle(
            [x, y, x + CARD_W - 1, y + CARD_H - 1],
            radius=14, fill=CARD_BG, outline=CARD_EDGE, width=2,
        )
        draw.rounded_rectangle(
            [x + 1, y + 18, x + 5, y + CARD_H - 18],
            radius=2, fill=colour,
        )

        tx = x + 22
        tw = CARD_W - 44

        draw.text((tx, y + 16), tag, font=font(13, True), fill=colour)

        head_face = font(25, True)
        cursor = y + 42
        for line in wrap(headline, head_face, tw, draw)[:2]:
            draw.text((tx, cursor), line, font=head_face, fill=INK)
            cursor += 30
        cursor += 8

        detail_face = font(16)
        for line in wrap(detail, detail_face, tw, draw)[:3]:
            draw.text((tx, cursor), line, font=detail_face, fill=MUTED)
            cursor += 21

    target = ROOT / "entry.png"
    image.save(target)
    print(f"wrote {target} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
