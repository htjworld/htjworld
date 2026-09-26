# htjworld.svg / htjworld-logo.svg 수정 후 `python3 build-slides.py` 로 slide-*.svg 재생성
# 원본 위에 인스타그램식 화살표와 점 표시만 덧그린다.
SLIDES = ["htjworld.svg", "htjworld-logo.svg"]
W, H = 680, 706

def arrow(i):
    last = i == len(SLIDES) - 1
    cx = 28 if last else W - 28
    d = "M31 346 L24 353 L31 360" if last else f"M{W - 31} 346 L{W - 24} 353 L{W - 31} 360"
    return (f'<circle cx="{cx}" cy="353" r="14" fill="#fafaf8" fill-opacity="0.9"/>'
            f'<path d="{d}" fill="none" stroke="#0d1117" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')

def dots(i):
    n, gap = len(SLIDES), 12
    return "".join(
        f'<circle cx="{W / 2 + (d - (n - 1) / 2) * gap:g}" cy="{H - 12}" r="3.5" fill="#fafaf8" fill-opacity="{1 if d == i else 0.35}"/>'
        for d in range(n)
    )

for i, src in enumerate(SLIDES):
    svg = open(src, encoding="utf-8").read().rstrip()
    assert svg.endswith("</svg>"), src
    out = svg[: -len("</svg>")] + f"\n  <!-- carousel nav -->\n  {arrow(i)}\n  {dots(i)}\n</svg>\n"
    open(f"slide-{i + 1}.svg", "w", encoding="utf-8").write(out)
