# htjworld.svg / htjworld-logo.svg 수정 후 `python3 build-terminal.py` 로 terminal.svg 재생성
# 시작 화면 = htjworld.svg. 프롬프트에 명령을 차례로 타이핑하고, 출력이 나오면 오래된 줄은 위로 밀려난다.
import re

PROMPT = "htjworld@github:~$ "
X0, CHAR_W = 24, 7.8          # Courier New 13px 한 글자 폭 (원본 커서 x=172 와 동일한 계산)
BOTTOM = 683                  # 프롬프트 줄이 머무는 화면 baseline
CLIP_TOP, CLIP_BOTTOM = 48, 700
IDLE_FIRST, IDLE, CHAR_T, ENTER_T = 4.0, 2.4, 0.09, 0.35

def texts(src, section):
    """<!-- section --> 주석 뒤부터 다음 주석 전까지의 (y, <text> 마크업) 목록"""
    body = open(src, encoding="utf-8").read()
    part = re.search(rf"<!-- {re.escape(section)} -->(.*?)(?=<!--|</svg>)", body, re.S).group(1)
    return [(float(re.search(r'\by="([\d.]+)"', t).group(1)), t) for t in re.findall(r"<text\b.*?</text>", part, re.S)]

def at(markup, y):
    return re.sub(r'\by="[\d.]+"', f'y="{y:g}"', markup, count=1)

# --- 명령 블록: (명령, [(프롬프트 기준 dy, 마크업)], 다음 프롬프트까지 dy) ---
def prompt_block(section, next_y):
    (py, first), *rest = texts("htjworld.svg", section)
    cmd = re.findall(r"<tspan[^>]*>(.*?)</tspan>", first)[1]
    return cmd, [(y - py, t) for y, t in rest], next_y - py

logo = texts("htjworld-logo.svg", "Block logo")
art = texts("htjworld.svg", "ASCII art") + texts("htjworld.svg", "Contact")
sections = ["whoami", "cat skills.json", "ls ./projects", "cat status.txt"]
starts = [texts("htjworld.svg", s)[0][0] for s in sections] + [texts("htjworld.svg", "Final prompt")[0][0]]

blocks = [
    ("logo", [(23 + y - logo[0][0], t) for y, t in logo], 23 + logo[-1][0] - logo[0][0] + 40),
    ("htjworld", [(23 + y - art[0][0], t) for y, t in art], 23 + starts[0] - art[0][0]),
] + [prompt_block(s, starts[i + 1]) for i, s in enumerate(sections)]

# --- 테이프: 같은 내용을 두 번(A, B) 이어 붙인다. A는 이미 출력된 과거, B는 이번 루프에서 출력된다. ---
period = sum(b[2] for b in blocks)
prompt_y = []                       # B 의 각 프롬프트 y
y = period
for b in blocks:
    prompt_y.append(y)
    y += b[2]

def prompt_line(y, cmd=""):
    tail = f'<tspan fill="#fafaf8">{cmd}</tspan>' if cmd else ""
    return f'<text x="{X0}" y="{y:g}" font-family="Courier New, monospace" font-size="13" xml:space="preserve"><tspan fill="#58a6ff">{PROMPT}</tspan>{tail}</text>'

# --- 타임라인 ---
t, events = 0.0, []                 # events: (시각, 이벤트)
enter_t = []
for k, (cmd, _, _) in enumerate(blocks):
    t += IDLE_FIRST if k == 0 else IDLE
    for i in range(len(cmd)):
        events.append((t + i * CHAR_T, ("char", k, i)))
    t += len(cmd) * CHAR_T + ENTER_T
    enter_t.append(t)
T = enter_t[-1]                     # 마지막 명령의 엔터 = 시작 화면과 동일 → 여기서 루프
pct = lambda s: f"{s / T * 100:.3f}%"

css, groups = [], {}                # groups: 등장 시각 → 요소들

def appear(time, markup):
    groups.setdefault(round(time, 4), []).append(markup)

a_parts = []
y = 0
for cmd, out, adv in blocks:        # A: 전부 보이는 과거 출력
    a_parts.append(prompt_line(y, cmd))
    a_parts += [at(m, y + dy) for dy, m in out]
    y += adv

b_parts = [prompt_line(prompt_y[0])]   # B 첫 프롬프트는 처음부터 보인다
for k, (cmd, out, adv) in enumerate(blocks[:-1]):
    py = prompt_y[k]
    for i, ch in enumerate(cmd):
        appear(events[sum(len(b[0]) for b in blocks[:k]) + i][0],
               f'<text x="{X0 + (len(PROMPT) + i) * CHAR_W:g}" y="{py:g}" font-family="Courier New, monospace" font-size="13" fill="#fafaf8" xml:space="preserve">{ch}</text>')
    for dy, m in out:
        appear(enter_t[k], at(m, py + dy))
    appear(enter_t[k], prompt_line(prompt_y[k + 1]))
# 마지막 블록(status)의 글자 타이핑만 보인다. 출력은 루프가 돌아 A 가 대신 보여준다.
k = len(blocks) - 1
for i, ch in enumerate(blocks[k][0]):
    appear(events[sum(len(b[0]) for b in blocks[:k]) + i][0],
           f'<text x="{X0 + (len(PROMPT) + i) * CHAR_W:g}" y="{prompt_y[k]:g}" font-family="Courier New, monospace" font-size="13" fill="#fafaf8" xml:space="preserve">{ch}</text>')

for n, (time, items) in enumerate(sorted(groups.items())):
    css.append(f"@keyframes a{n}{{0%{{opacity:0}}{pct(time)}{{opacity:1}}}}.a{n}{{opacity:0;animation:a{n} {T:.2f}s step-end infinite}}")
    b_parts += [m.replace("<text ", f'<text class="a{n}" ', 1) for m in items]

# 스크롤: 엔터마다 새 프롬프트가 BOTTOM 에 오도록 테이프를 올린다.
off0 = prompt_y[0] - BOTTOM
scroll = [f"0%{{transform:translateY({-off0:g}px)}}"] + [
    f"{pct(enter_t[k])}{{transform:translateY({-(prompt_y[k + 1] - BOTTOM):g}px)}}" for k in range(len(blocks) - 1)]
css.append(f"@keyframes scroll{{{''.join(scroll)}}}.tape{{animation:scroll {T:.2f}s step-end infinite}}")

# 가림막: 스크롤 상태마다 제목줄 아래에 반쯤 잘린 줄이 보이지 않도록 그 줄까지 배경색으로 덮는다.
lines = [(float(re.search(r'\by="([\d.]+)"', m).group(1)), float(re.search(r'font-size="([\d.]+)"', m).group(1)))
         for m in a_parts + b_parts]
def cover(off):
    cut = [y - off + 4 for y, fs in lines if y - off - fs < CLIP_TOP < y - off + 4]
    return max([CLIP_TOP] + cut)
offs = [off0] + [prompt_y[k + 1] - BOTTOM for k in range(len(blocks) - 1)]
cov = [f"0%{{transform:translateY({cover(offs[0]):g}px)}}"] + [
    f"{pct(enter_t[k])}{{transform:translateY({cover(offs[k + 1]):g}px)}}" for k in range(len(blocks) - 1)]
css.append(f"@keyframes cover{{{''.join(cov)}}}.cover{{animation:cover {T:.2f}s step-end infinite}}")

# 커서: 프롬프트마다 하나. 등장 → 글자마다 오른쪽으로 → 엔터에 사라짐.
cursors = []
for k, (cmd, _, _) in enumerate(blocks):
    shown = 0 if k == 0 else enter_t[k - 1]
    first = sum(len(b[0]) for b in blocks[:k])
    op = [f"0%{{opacity:{1 if k == 0 else 0}}}"] + ([f"{pct(shown)}{{opacity:1}}"] if k else []) + [f"{pct(enter_t[k])}{{opacity:0}}"]
    mv = ["0%{transform:translateX(0)}"] + [f"{pct(events[first + i][0])}{{transform:translateX({(i + 1) * CHAR_W:g}px)}}" for i in range(len(cmd))]
    css.append(f"@keyframes co{k}{{{''.join(op)}}}@keyframes cm{k}{{{''.join(mv)}}}"
               f".c{k}{{opacity:{1 if k == 0 else 0};animation:co{k} {T:.2f}s step-end infinite,cm{k} {T:.2f}s step-end infinite}}")
    cursors.append(f'<g class="c{k}"><rect class="blink" x="{X0 + len(PROMPT) * CHAR_W:g}" y="{prompt_y[k] - 10:g}" width="8" height="13" fill="#58a6ff"/></g>')

css.append("@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}.blink{animation:blink 1s step-end infinite}")
css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}.c0{opacity:1!important}}")

frame = re.search(r"(<!-- Terminal background -->.*?)<!-- ASCII art -->", open("htjworld.svg", encoding="utf-8").read(), re.S).group(1)
title = frame.split("<!-- Title bar -->", 1)[1]
nl = "\n"
out = f'''<svg xmlns="http://www.w3.org/2000/svg" width="680" height="706">
<style>{"".join(css)}</style>
<clipPath id="screen"><rect x="0" y="{CLIP_TOP}" width="680" height="{CLIP_BOTTOM - CLIP_TOP}"/></clipPath>
{frame.strip()}
<g clip-path="url(#screen)"><g class="tape" transform="translate(0 {-off0:g})">
{nl.join(a_parts)}
{nl.join(b_parts)}
{nl.join(cursors)}
</g></g>
<rect class="cover" y="-24" width="680" height="24" fill="#0d1117" transform="translate(0 {cover(off0):g})"/>
{title.strip()}
</svg>
'''
open("terminal.svg", "w", encoding="utf-8").write(out)
print(f"loop {T:.2f}s, period {period:g}px")
