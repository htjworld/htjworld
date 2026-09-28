#!/usr/bin/env python3
"""Generate circular link-badge SVGs for the README (left: contacts, right: projects).

GitHub blocks external image loads inside an SVG rendered as <img>, so logos are
inlined as base64 data URIs. Each badge is one self-contained circular SVG; the
click target is added in the README via a markdown/HTML <a> wrapper (SVG-internal
links don't work through GitHub's camo proxy).
"""
import base64
from pathlib import Path

HERE = Path(__file__).parent
LOGO_DIR = HERE.parent / "htjworld.github.io" / "public"
OUT = HERE / "badges"
OUT.mkdir(exist_ok=True)

SIZE = 160  # viewBox; rendered smaller via <img width> in README

# Rubik Mono One embedded as base64 so the label renders identically for every
# viewer — GitHub's <img>-mode SVG can't fetch web fonts, but a data-URI
# @font-face is inline (no request) and works. Falls back to monospace if the
# renderer ignores it.
_FONT_B64 = base64.b64encode((HERE / "RubikMonoOne.woff2").read_bytes()).decode()
FONT_FACE = (
    "@font-face{font-family:'Rubik Mono One';font-style:normal;font-weight:400;"
    f"src:url(data:font/woff2;base64,{_FONT_B64}) format('woff2');}}"
)
FONT_FAMILY = "'Rubik Mono One', 'Courier New', monospace"


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
    """Dark gradient circle with a per-project accent ring and a bright label.

    Hover CSS is included as progressive enhancement: it lights up the ring and
    tints the label where the SVG is interactive (Pages site / direct view).
    GitHub renders README SVGs as <img> in secure-animated mode, which blocks
    pointer events, so hover is silently ignored there — costs nothing to keep.
    """
    n = len(lines)
    step = font + 6
    start = SIZE / 2 - (n - 1) * step / 2 + font / 3  # baseline of first line
    tspans = "".join(
        f'<text x="{SIZE/2}" y="{start + i*step:.1f}" text-anchor="middle" '
        f'font-family="{FONT_FAMILY}" font-size="{font}">{ln}</text>'
        for i, ln in enumerate(lines)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">
  <defs>
    <style>
      {FONT_FACE}
      .badge {{ cursor: pointer; }}
      .badge .ring {{ transition: stroke-width .2s ease, fill .2s ease; }}
      .badge text {{ fill: #111111; transition: fill .2s ease; }}
      .badge:hover .ring {{ stroke-width: 5; fill: {accent}22; }}
      .badge:hover text {{ fill: {accent}; }}
    </style>
  </defs>
  <g class="badge">
    <circle class="ring" cx="{SIZE/2}" cy="{SIZE/2}" r="{SIZE/2-3}" fill="#ffffff" stroke="{accent}" stroke-width="2.5"/>
    {tspans}
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
