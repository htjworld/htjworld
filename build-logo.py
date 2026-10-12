#!/usr/bin/env python3
"""Render htjworld_logo.png: "HTJ" over "WORLD" in Rubik Bubbles, transparent, wide crop.

Both lines share one font size, so WORLD sticks out past HTJ on both sides.
Lines are drawn on an oversized canvas, then cropped to the ink: flush left/right
(README stretches it to full width), small top/bottom padding.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONT = HERE / "RubikBubbles-Regular.ttf"
WIDTH = 2400                     # output width
FILL_RATIO = 0.92                # sizes the font; sides are trimmed to the ink afterwards
PAD_Y = 80                       # top/bottom transparent margin in px
LINE_GAP = 0.08                  # gap between lines, as a fraction of font size
LINES = [
    [("H", (20, 193, 241)), ("T", (30, 225, 160)), ("J", (235, 45, 125))],
    # Coolors "ffbe0b-fb5607-ff006e-8338ec-3a86ff" with the pink swapped for red
    # (pink is J's), ordered warm/cool so neighbours never blur together.
    [("W", (230, 57, 70)), ("O", (255, 190, 11)), ("R", (131, 56, 236)),
     ("L", (251, 86, 7)), ("D", (58, 134, 255))],
]

widest = max(LINES, key=len)
probe = ImageFont.truetype(str(FONT), 1000)
l, _, r, _ = probe.getbbox("".join(c for c, _ in widest))
fs = round(1000 * WIDTH * FILL_RATIO / (r - l))
font = ImageFont.truetype(str(FONT), fs)

img = Image.new("RGBA", (WIDTH, fs * 4), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
y = fs  # ink top of the current line
for line in LINES:
    text = "".join(c for c, _ in line)
    l, t, r, b = font.getbbox(text)
    x = (WIDTH - (r - l)) / 2 - l
    for ch, col in line:
        d.text((x, y - t), ch, font=font, fill=col + (255,))
        x += font.getlength(ch)
    y += (b - t) + fs * LINE_GAP

left, top, right, bottom = img.getbbox()
img = img.crop((left, top - PAD_Y, right, bottom + PAD_Y))
img.save(HERE / "htjworld_logo.png", optimize=True)
print("wrote htjworld_logo.png", img.size, "font", fs)
