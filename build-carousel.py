# htjworld.svg / htjworld-logo.svg 수정 후 `python3 build-carousel.py` 로 carousel.svg 재생성
# README의 <img>는 외부 파일을 못 불러오므로 두 슬라이드를 한 SVG 안에 인라인한다.
import re

W, H = 680, 706
SLIDES = ["htjworld.svg", "htjworld-logo.svg"]

def inner(path):
    src = open(path, encoding="utf-8").read()
    return re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)

n = len(SLIDES)
slides = "".join(f'<svg x="{i * W}" width="{W}" height="{H}">{inner(p)}</svg>' for i, p in enumerate(SLIDES))

# 슬라이드마다 hold 후 0.6s 동안 넘어가고, 마지막 슬라이드에서 처음으로 돌아간다.
hold, move = 3.4, 0.6
total = n * (hold + move)
pct = lambda t: f"{t / total * 100:.2f}%"
track, dots = [], [[] for _ in range(n)]
for i in range(n):
    start = i * (hold + move)
    track.append(f"{pct(start)},{pct(start + hold)}{{transform:translateX({-i * W}px)}}")
    for d in range(n):
        dots[d].append(f"{pct(start)},{pct(start + hold)}{{opacity:{1 if d == i else .3}}}")
track.append("100%{transform:translateX(0)}")
for d in range(n):
    dots[d].append(f"100%{{opacity:{1 if d == 0 else .3}}}")

ease = f"{total}s cubic-bezier(.4,0,.2,1) infinite"
css = f"@keyframes track{{{''.join(track)}}} .track{{animation:track {ease}}}"
for d in range(n):
    css += f"@keyframes dot{d}{{{''.join(dots[d])}}} .dot{d}{{animation:dot{d} {ease}}}"
css += "@media (prefers-reduced-motion:reduce){.track,[class^=dot]{animation:none}}"

gap = 16
dot_svg = "".join(
    f'<circle class="dot{d}" cx="{W / 2 + (d - (n - 1) / 2) * gap}" cy="{H + 14}" r="4" fill="#8b949e" opacity="{1 if d == 0 else .3}"/>'
    for d in range(n)
)

out = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H + 28}" viewBox="0 0 {W} {H + 28}">
<style>{css}</style>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<g clip-path="url(#frame)"><g class="track">{slides}</g></g>
{dot_svg}
</svg>
'''
open("carousel.svg", "w", encoding="utf-8").write(out)
