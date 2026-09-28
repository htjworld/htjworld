#!/usr/bin/env python3
"""Generate circular link-badge SVGs for the README (left: contacts, right: projects).

GitHub blocks external image loads inside an SVG rendered as <img>, so logos are
inlined as base64 data URIs. Each badge is one self-contained circular SVG; the
click target is added in the README via a markdown/HTML <a> wrapper (SVG-internal
links don't work through GitHub's camo proxy).
"""
import base64
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
LOGO_DIR = HERE.parent / "htjworld.github.io" / "public"
OUT = HERE / "badges"
OUT.mkdir(exist_ok=True)

SIZE = 160  # viewBox; rendered smaller via <img width> in README
TEXT_BUDGET = 122  # max label width in px; longer lines auto-shrink to fit the circle

# GitHub's <img>-mode SVG ignores @font-face (even data-URI fonts), so the label
# would fall back to thin monospace. Instead we convert each label to Rubik Mono
# One vector outlines with fontTools — no font loading needed, renders identically
# everywhere as the real (heavy, boxy) glyphs.
_FONT = TTFont(HERE / "RubikMonoOne.ttf")
_UPM = _FONT["head"].unitsPerEm
_CMAP = _FONT.getBestCmap()
_GLYPHS = _FONT.getGlyphSet()
_HMTX = _FONT["hmtx"]


def _line_svg(text: str, font: int, cx: float, baseline: float) -> tuple[str, float]:
    """A <g> of glyph <path>s for `text`, centered at `cx`, sitting on `baseline`.

    Returns (markup, width_px). Font units are y-up; scale(s,-s) flips to SVG.
    """
    scale = font / _UPM
    pen_x, glyphs = 0, []
    for ch in text:
        name = _CMAP[ord(ch)]
        pen = SVGPathPen(_GLYPHS)
        _GLYPHS[name].draw(pen)
        d = pen.getCommands()
        if d:
            glyphs.append(f'<path transform="translate({pen_x} 0)" d="{d}"/>')
        pen_x += _HMTX[name][0]
    width = pen_x * scale
    g = (f'<g class="lbl" transform="translate({cx - width/2:.1f} {baseline:.1f}) '
         f'scale({scale:.4f} {-scale:.4f})">{"".join(glyphs)}</g>')
    return g, width


def data_uri(path: Path) -> str:
    mime = "image/svg+xml" if path.suffix == ".svg" else f"image/{path.suffix.lstrip('.')}"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def logo_badge(name: str, logo: Path, logo_frac: float = 0.52) -> None:
    """White circle with a centered embedded logo."""
    d = SIZE * logo_frac
    off = (SIZE - d) / 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <circle cx="{SIZE/2}" cy="{SIZE/2}" r="{SIZE/2-3}" fill="#ffffff" stroke="#30363d" stroke-width="2"/>
  <image x="{off:.1f}" y="{off:.1f}" width="{d:.1f}" height="{d:.1f}" preserveAspectRatio="xMidYMid meet" href="{data_uri(logo)}" xlink:href="{data_uri(logo)}"/>
</svg>
'''
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def text_badge(name: str, lines: list[str], font: int, accent: str) -> None:
    """White circle, per-project accent ring, black Rubik Mono One label as vectors.

    Hover CSS (ring lights up, label tints to the accent) is progressive
    enhancement — it works where the SVG is interactive (Pages / direct view).
    GitHub renders README SVGs as <img> in secure mode, which blocks pointer
    events, so hover is silently ignored there; costs nothing to keep.
    """
    # Fit: shrink font so the widest line stays inside the circle.
    widest = max(_line_svg(ln, font, 0, 0)[1] for ln in lines)
    if widest > TEXT_BUDGET:
        font = int(font * TEXT_BUDGET / widest)
    n = len(lines)
    step = font + 6
    start = SIZE / 2 - (n - 1) * step / 2 + font / 3  # baseline of first line
    labels = "".join(_line_svg(ln, font, SIZE / 2, start + i * step)[0] for i, ln in enumerate(lines))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <defs>
    <style>
      .badge {{ cursor: pointer; }}
      .badge .ring {{ transition: stroke-width .2s ease, fill .2s ease; }}
      .badge .lbl {{ fill: #111111; transition: fill .2s ease; }}
      .badge:hover .ring {{ stroke-width: 5; fill: {accent}22; }}
      .badge:hover .lbl {{ fill: {accent}; }}
    </style>
  </defs>
  <g class="badge">
    <circle class="ring" cx="{SIZE/2}" cy="{SIZE/2}" r="{SIZE/2-3}" fill="#ffffff" stroke="{accent}" stroke-width="2.5"/>
    {labels}
  </g>
</svg>
'''
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


# Left column — contacts (embedded logos)
logo_badge("gmail", LOGO_DIR / "gmail-logo.svg", logo_frac=0.50)
logo_badge("velog", LOGO_DIR / "velog-logo.png", logo_frac=0.60)

# Right column — vibe-coding projects (Rubik Mono One label, per-project accent).
# Rubik Mono One is wide, so long words use a smaller size; tune here if needed.
text_badge("finfeeds", ["finfeeds"], font=19, accent="#3fb950")       # green
text_badge("art-run", ["art", "run"], font=30, accent="#2dd4bf")      # turquoise
text_badge("krachwerk", ["krach", "werk"], font=25, accent="#75fb4c")  # official neon
text_badge("photo-booth", ["photo", "booth"], font=25, accent="#ff6fb5")  # pink
text_badge("drift-lanterns", ["drift", "lanterns"], font=20, accent="#4c6ef5")  # navy (brightened)

print("wrote:", *(p.name for p in sorted(OUT.glob("*.svg"))))
