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
        "bg": "#1a1a2e",
        "fg": "#bbc2cf",
        "border": "#3d3d5c",
        "prompt_host": "#51afef",
        "prompt_path": "#98be65",
        "command": "#bbc2cf",
        "key": "#ff6c6b",
        "value": "#a9a1e1",
        "dim": "#5b6268",
        "add": "#98be65",
        "delete": "#ff6c6b",
        "cursor": "#a9a1e1",
        "ascii": "#7aa2f7",
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
    },
}

SVG_HEIGHT = 540


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def animation_styles(theme: dict) -> str:
    return f"""
@keyframes terminal-pulse {{
  0%, 100% {{ opacity: 0.55; }}
  50% {{ opacity: 1; }}
}}
@keyframes cursor-blink {{
  0%, 45% {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}
@keyframes scanline {{
  0% {{ transform: translateY(12px); opacity: 0; }}
  8% {{ opacity: 0.1; }}
  92% {{ opacity: 0.1; }}
  100% {{ transform: translateY({SVG_HEIGHT - 12}px); opacity: 0; }}
}}
.terminal-row {{
  animation: terminal-pulse 2.8s ease-in-out infinite;
}}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
#terminal-scanline {{
  fill: url(#scanline-gradient);
  animation: scanline 5s linear infinite;
}}
"""


def row_delay(y: int) -> str:
    return f"{max(0, y - 30) * 0.035:.2f}s"


def ascii_block(theme: dict, x: int = 15, y_start: int = 40) -> str:
    rows = []
    for index, line in enumerate(ASCII_LOGO):
        y = y_start + index * 20
        rows.append(
            f'<tspan x="{x}" y="{y}" class="terminal-row" '
            f'style="animation-delay:{row_delay(y)}" fill="{theme["ascii"]}">'
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
        (150, info_row("Shell", "zsh")),
        (170, info_row("Editor", "Doom Emacs")),
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
        rows.append(
            f'<tspan x="300" y="{y}" class="terminal-row" '
            f'style="animation-delay:{row_delay(y)}">{content}</tspan>'
        )
    return "\n".join(rows)


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    scanline = theme["prompt_host"]
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="{SVG_HEIGHT}px" font-size="16px">
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
<stop offset="45%" stop-color="{scanline}" stop-opacity="0.35"/>
<stop offset="55%" stop-color="{scanline}" stop-opacity="0.35"/>
<stop offset="100%" stop-color="{theme["bg"]}" stop-opacity="0"/>
</linearGradient>
</defs>
<rect width="985px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="12"/>
<rect x="1" y="1" width="983px" height="{SVG_HEIGHT - 2}px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<rect id="terminal-scanline" x="12" y="0" width="961" height="24" opacity="0"/>
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
