#!/usr/bin/env python3
"""Render a single 1024x1024 news poster for 26 November 2026."""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BG = (10, 17, 28)
PANEL = (18, 28, 43)
INK = (238, 243, 248)
MUTED = (150, 167, 186)
ACCENT = (90, 210, 255)
GOLD = (255, 197, 94)
RED = (255, 112, 112)
GREEN = (86, 214, 154)
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FB = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def font(size, bold=False):
    return ImageFont.truetype(FB if bold else F, size)

def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ''
    for word in words:
        trial = f'{cur} {word}'.strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

NEWS = [
    ('WAR', RED, 'Kyiv under missile barrage', 'Seven wounded as ballistic missiles hit the capital; Zelensky warns of a new mass strike.'),
    ('US', GOLD, 'Thanksgiving storms', 'More than 600,000 homes lose power; Macy’s 100th parade is postponed.'),
    ('MIDEAST', RED, 'Drone over Kuwait', 'Two Italian technicians killed at an air-defence site; Iran denies involvement.'),
    ('TRADE', ACCENT, 'Tariffs on 14 partners', 'Washington proposes 15–25% duties; China would face the top rate of 20%.'),
    ('HEALTH', GREEN, 'Ebola passes 12,000', 'The Congo outbreak becomes the second-largest ever recorded.'),
    ('ASIA', GOLD, 'Kim vows more nukes', 'North Korea’s leader inspects nuclear sites and calls for a bigger arsenal.'),
    ('SPACE', ACCENT, 'FCC OKs one million satellites', 'SpaceX may build data centres in orbit; scientists question the plan.'),
    ('EU', MUTED, 'Budget standoff', 'Leaders split over a €1.7tn budget and fresh aid for Ukraine.'),
]

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 132], fill=(15, 25, 39))
d.text((48, 32), 'THE WORLD', font=font(25, True), fill=ACCENT)
d.text((48, 66), '26 NOVEMBER 2026', font=font(52, True), fill=INK)
d.text((49, 126), 'One day, eight headlines', font=font(17), fill=MUTED)

cols, rows = 2, 4
pw, ph = 456, 198
gx, gy = 20, 16
x0, y0 = 44, 160
for i, (tag, color, title, detail) in enumerate(NEWS):
    col, row = i % cols, i // cols
    x = x0 + col * (pw + gx)
    y = y0 + row * (ph + gy)
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=12, fill=PANEL, outline=(35, 50, 70), width=2)
    d.rounded_rectangle([x + 16, y + 16, x + 133, y + 42], radius=6, fill=color)
    d.text((x + 26, y + 19), tag, font=font(14, True), fill=(9, 16, 26))
    ty = y + 54
    for line in wrap(d, title, font(22, True), pw - 34):
        d.text((x + 17, ty), line, font=font(22, True), fill=INK)
        ty += 27
    ty += 4
    for line in wrap(d, detail, font(15), pw - 34):
        d.text((x + 17, ty), line, font=font(15), fill=MUTED)
        ty += 20

d.text((48, H - 30), 'Compiled from public reporting of events first reported on 26 November 2026',
       font=font(13), fill=MUTED)
img.save('/home/hatch/workspace/makefun/news-image/entry.png', 'PNG', optimize=True)
print('wrote entry.png', img.size)
