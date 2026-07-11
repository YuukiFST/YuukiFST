#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — SSH session profile layout."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ASCII_LOGO = [
    "#   # #   # #   # #   # ### ",
    " # #  #   # #   # #  #   #  ",
    "  #   #   # #   # ###    #  ",
    "  #   #   # #   # #  #   #  ",
    "  #    ###   ###  #   # ### ",
    "                            ",
    "                            ",
    "                            ",
]

THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        # Omarchy Vantablack (ghostty.conf / colors.toml)
        "bg": "#000000",
        "fg": "#ffffff",
        "border": "#404040",
        "prompt_host": "#8d8d8d",
        "prompt_path": "#ececec",
        "command": "#ffffff",
        "key": "#b6b6b6",
        "value": "#cecece",
        "dim": "#5c5c5c",
        "add": "#ffffff",
        "delete": "#a4a4a4",
        "cursor": "#ffffff",
        "ascii": "#8d8d8d",
        "font": "FantasqueSansM Nerd Font,ConsolasFallback,Consolas,monospace",
    },
    "light": {
        "file": "light_mode.svg",
        "bg": "#fdf6e3",
        "fg": "#657b83",
        "border": "#93a1a1",
        "prompt_host": "#268bd2",
        "prompt_path": "#859900",
        "command": "#657b83",
        "key": "#cb4b16",
        "value": "#073642",
        "dim": "#93a1a1",
        "add": "#859900",
        "delete": "#dc322f",
        "cursor": "#6c71c4",
        "ascii": "#268bd2",
        "font": "ConsolasFallback,Consolas,monospace",
    },
}

SVG_HEIGHT = 540
SCAN_DURATION_S = 26
SCANLINE_HEIGHT = 28
SCAN_MARGIN = 10
FADE_WINDOW_PCT = 3.0
FADED_OPACITY = 0.1

TTY_ROW_Y = [30, 70, 90, 110, 130, 150, 170, 190, 220, 240, 260, 280, 320, 340, 360, 400, 420, 460, 480, 520]
ASCII_ROW_Y = [40 + index * 20 for index in range(len(ASCII_LOGO))]
ALL_ROW_Y = sorted(set(TTY_ROW_Y + ASCII_ROW_Y))
FIRST_ROW_Y = min(ALL_ROW_Y)
LAST_ROW_Y = max(ALL_ROW_Y)
SCAN_START = FIRST_ROW_Y - SCANLINE_HEIGHT - SCAN_MARGIN
SCAN_END = LAST_ROW_Y + SCAN_MARGIN
SCAN_SPAN = SCAN_END - SCAN_START


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def scan_arrival_percent(y: int) -> float:
    """Timeline % when scanline bottom edge reaches row baseline."""
    arrival_translate = y - SCANLINE_HEIGHT
    return max(0.0, min(98.0, ((arrival_translate - SCAN_START) / SCAN_SPAN) * 100))


def row_fade_keyframe(y: int) -> str:
    hit = scan_arrival_percent(y)
    lead = max(0.0, hit - 0.3)
    fade_end = min(hit + FADE_WINDOW_PCT, 99.5)
    return f"""@keyframes row-fade-{y} {{
  0%, {lead:.1f}% {{ opacity: 1; }}
  {fade_end:.1f}% {{ opacity: {FADED_OPACITY}; }}
  {fade_end:.1f}%, 99.9% {{ opacity: {FADED_OPACITY}; }}
  100% {{ opacity: 1; }}
}}"""


def animation_styles(theme: dict) -> str:
    row_keyframes = "\n".join(row_fade_keyframe(y) for y in ALL_ROW_Y)
    row_rules = "\n".join(
        f".row-y-{y} {{ animation: row-fade-{y} {SCAN_DURATION_S}s linear infinite; }}"
        for y in ALL_ROW_Y
    )
    visible_at = max(0.6, scan_arrival_percent(FIRST_ROW_Y) - 0.2)
    return f"""
{row_keyframes}
@keyframes cursor-blink {{
  0%, 45% {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}
@keyframes scanline {{
  0% {{ transform: translateY({SCAN_START}px); opacity: 0; }}
  {visible_at:.1f}% {{ opacity: 0.22; }}
  99.5% {{ opacity: 0.22; }}
  100% {{ transform: translateY({SCAN_END}px); opacity: 0; }}
}}
.terminal-row {{
  opacity: 1;
}}
{row_rules}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
#terminal-scanline {{
  fill: url(#scanline-gradient);
  animation: scanline {SCAN_DURATION_S}s linear infinite;
}}
"""


def row_class(y: int) -> str:
    return f"terminal-row row-y-{y}"


def ascii_block(theme: dict, x: int = 15, y_start: int = 40) -> str:
    rows = []
    for index, line in enumerate(ASCII_LOGO):
        y = y_start + index * 20
        rows.append(
            f'<tspan x="{x}" y="{y}" class="{row_class(y)}" fill="{theme["ascii"]}">'
            f"{esc(line)}</tspan>"
        )
    return "\n".join(rows)


def prompt(theme: dict, command: str) -> str:
    return (
        f'<tspan class="prompt-host">yuuki@github</tspan>'
        f'<tspan class="prompt-path">:~$</tspan> '
        f'<tspan class="command">{esc(command)}</tspan>'
    )


def info_row(label: str, value: str) -> str:
    return (
        f'<tspan class="dim"> </tspan>'
        f'<tspan class="key">{esc(f"{label:<8}")}</tspan>'
        f'<tspan class="dim">· </tspan>'
        f'<tspan class="value">{esc(value)}</tspan>'
    )


def stat_line(value_id: str, suffix: str, indent: str = "    ") -> str:
    return (
        f'<tspan class="dim">{esc(indent)}</tspan>'
        f'<tspan class="value" id="{value_id}">0</tspan>'
        f'<tspan class="dim" id="{value_id}_dots"></tspan>'
        f'<tspan class="dim">{esc(suffix)}</tspan>'
    )


def stack_row(label: str, value: str) -> str:
    return (
        f'<tspan class="dim"> » </tspan>'
        f'<tspan class="key">{esc(f"{label + ':':<12}")}</tspan>'
        f'<tspan class="value">{esc(value)}</tspan>'
    )


def tty_block(theme: dict) -> str:
    lines: list[tuple[int, str]] = [
        (
            30,
            f'<tspan class="dim">Last login: Sat Jul 11 2026 from 127.0.0.1 — </tspan>'
            f'<tspan class="value" id="age_data">3 years, 9 months, 0 days</tspan>'
            f'<tspan class="dim" id="age_data_dots"></tspan>'
            f'<tspan class="dim"> on GitHub</tspan>',
        ),
        (70, prompt(theme, "fastfetch --logo custom")),
        (90, f'<tspan class="key">yuuki@github</tspan><tspan class="dim"> ─────────────────────────────</tspan>'),
        (110, info_row("OS", "Omarchy")),
        (130, info_row("Host", "São Benedito / IFMT")),
        (150, info_row("Shell", "bash")),
        (170, info_row("Terminal", "Ghostty")),
        (190, info_row("Role", "Fullstack")),
        (220, stack_row("Backend", "Python, Django, Go, tRPC, Prisma")),
        (240, stack_row("Frontend", "React, Next.js, TypeScript, Tailwind, shadcn/ui")),
        (260, stack_row("Databases", "PostgreSQL, Neon, Supabase")),
        (280, stack_row("DevOps", "Docker, Git, Linux, Cloudinary")),
        (320, prompt(theme, "cat ~/links")),
        (340, f'<tspan class="dim"> </tspan><tspan class="key">portfolio</tspan><tspan class="dim">  → </tspan><tspan class="value">fausto-yuuki.vercel.app</tspan>'),
        (360, f'<tspan class="dim"> </tspan><tspan class="key">linkedin</tspan><tspan class="dim">   → </tspan><tspan class="value">fausto-yuuki</tspan>'),
        (400, prompt(theme, "git shortlog -sn --all | head -1")),
        (420, stat_line("commit_data", "  YuukiFST", "   ")),
        (460, prompt(theme, "gh api graphql --field query=contributions")),
        (480, stat_line("contrib_data", " contributions", "  ")),
        (
            520,
            f'{prompt(theme, "")}'
            f'<tspan class="cursor">█</tspan>',
        ),
    ]

    rows = []
    for y, content in lines:
        rows.append(f'<tspan x="300" y="{y}" class="{row_class(y)}">{content}</tspan>')
    return "\n".join(rows)


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    scanline = theme["prompt_host"]
    font = theme.get("font", "ConsolasFallback,Consolas,monospace")
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="{font}" width="985px" height="{SVG_HEIGHT}px" font-size="16px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.prompt-host {{fill: {theme["prompt_host"]};}}
.prompt-path {{fill: {theme["prompt_path"]};}}
.command {{fill: {theme["command"]};}}
.key {{fill: {theme["key"]};}}
.value {{fill: {theme["value"]};}}
.dim {{fill: {theme["dim"]};}}
.addColor {{fill: {theme["add"]};}}
.delColor {{fill: {theme["delete"]};}}
.cursor {{fill: {theme["cursor"]};}}
text, tspan {{white-space: pre;}}
{animation_styles(theme)}
</style>
<defs>
<linearGradient id="scanline-gradient" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="{theme["bg"]}" stop-opacity="0"/>
<stop offset="47%" stop-color="{scanline}" stop-opacity="0.4"/>
<stop offset="53%" stop-color="{scanline}" stop-opacity="0.4"/>
<stop offset="100%" stop-color="{theme["bg"]}" stop-opacity="0"/>
</linearGradient>
</defs>
<rect width="985px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="12"/>
<rect x="1" y="1" width="983px" height="{SVG_HEIGHT - 2}px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<rect id="terminal-scanline" x="12" y="0" width="961" height="{SCANLINE_HEIGHT}" opacity="0"/>
<text x="15" y="30" fill="{theme["fg"]}" class="ascii">
{ascii_block(theme)}
</text>
<text x="300" y="30" fill="{theme["fg"]}">
{tty_block(theme)}
</text>
</svg>'''


def main() -> None:
    for theme_name in THEMES:
        path = ROOT / THEMES[theme_name]["file"]
        path.write_text(build_svg(theme_name), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
