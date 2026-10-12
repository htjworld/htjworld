#!/usr/bin/env python3
"""Render htj_logo.png: "HTJ" in Rubik Bubbles, transparent, wide crop.

Letters are drawn on an oversized canvas, then cropped to the ink bbox with a
little side padding and almost none top/bottom, so the README shows no gap.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONT = HERE / "RubikBubbles-Regular.ttf"
WIDTH = 2400                     # output width
FILL_RATIO = 0.90                # letters' width / output width (rest = side padding)
PAD_Y = 12                       # top/bottom transparent margin in px
LETTERS = [("H", (20, 193, 241)), ("T", (30, 225, 160)), ("J", (235, 45, 125))]
text = "".join(c for c, _ in LETTERS)

# Font size so the letters span WIDTH * FILL_RATIO.
probe = ImageFont.truetype(str(FONT), 1000)
l, t, r, b = probe.getbbox(text)
font = ImageFont.truetype(str(FONT), round(1000 * WIDTH * FILL_RATIO / (r - l)))

l, t, r, b = font.getbbox(text)
img = Image.new("RGBA", (WIDTH, b - t + 200), (255, 255, 255, 0))
d = ImageDraw.Draw(img)
x, y = (WIDTH - (r - l)) / 2 - l, 100 - t
for ch, col in LETTERS:
    d.text((x, y), ch, font=font, fill=col + (255,))
    x += font.getlength(ch)

_, top, _, bottom = img.getbbox()
img = img.crop((0, top - PAD_Y, WIDTH, bottom + PAD_Y))
img.save(HERE / "htj_logo.png", optimize=True)
print("wrote htj_logo.png", img.size)
