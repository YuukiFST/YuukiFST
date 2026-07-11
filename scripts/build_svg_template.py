#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — SSH session profile layout."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ARCH_LOGO = [
    "            .---.            ",
    "        .--:+*****+:--.        ",
    "     .-+***++++++++***+-.     ",
    "   .:=**++++++++++++++++=:    ",
    "  :=+*++++++++++++++++++*+=:  ",
    " .=*++++++++++++++++++++++*=. ",
    " -++++++++++++++++++++++++++++- ",
    " -++++++++++++++++++++++++++++- ",
    " .=*++++++++++++++++++++++*=. ",
    "  :=+*++++++++++++++++++*+=:  ",
    "   .:=**++++++++++++++++=:    ",
    "     .-+***++++++++***+-.     ",
    "        `--:+*****+:--`        ",
    "            `---`            ",
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


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ascii_block(theme: dict, x: int = 15, y_start: int = 30) -> str:
    rows = []
    for index, line in enumerate(ARCH_LOGO):
        y = y_start + index * 20
        rows.append(f'<tspan x="{x}" y="{y}" fill="{theme["ascii"]}">{esc(line)}</tspan>')
    return "\n".join(rows)


def prompt(theme: dict, command: str) -> str:
    return (
        f'<tspan class="prompt-host">yuuki@github</tspan>'
        f'<tspan class="prompt-path">:~$</tspan> '
        f'<tspan class="command">{esc(command)}</tspan>'
    )


def tty_block(theme: dict) -> str:
    lines: list[tuple[int, str]] = [
        (
            30,
            f'<tspan class="dim">Last login: Sat Jul 11 2026 from 127.0.0.1 — </tspan>'
            f'<tspan class="value" id="age_data">3 years, 9 months, 0 days</tspan>'
            f'<tspan class="dim" id="age_data_dots"> </tspan>'
            f'<tspan class="dim">on GitHub</tspan>',
        ),
        (70, prompt(theme, "fastfetch --logo arch")),
        (90, f'<tspan class="key">yuuki@github</tspan><tspan class="dim"> ─────────────────────────────</tspan>'),
        (110, f'<tspan class="dim"> </tspan><tspan class="key">OS</tspan><tspan class="dim"> ····· </tspan><tspan class="value">Arch Linux, WSL 2</tspan>'),
        (130, f'<tspan class="dim"> </tspan><tspan class="key">Host</tspan><tspan class="dim"> ·· </tspan><tspan class="value">São Benedito / IFMT</tspan>'),
        (150, f'<tspan class="dim"> </tspan><tspan class="key">Shell</tspan><tspan class="dim"> · </tspan><tspan class="value">zsh</tspan>'),
        (170, f'<tspan class="dim"> </tspan><tspan class="key">Editor</tspan><tspan class="dim">  </tspan><tspan class="value">Doom Emacs</tspan>'),
        (190, f'<tspan class="dim"> </tspan><tspan class="key">Stack</tspan><tspan class="dim"> · </tspan><tspan class="value">Python, Go, PostgreSQL, TypeScript</tspan>'),
        (210, f'<tspan class="dim"> </tspan><tspan class="key">Focus</tspan><tspan class="dim"> · </tspan><tspan class="value">Backend, Data, AI Agents</tspan>'),
        (250, prompt(theme, "cat ~/links")),
        (270, f'<tspan class="dim"> </tspan><tspan class="key">portfolio</tspan><tspan class="dim">  → </tspan><tspan class="value">fausto-yuuki.vercel.app</tspan>'),
        (290, f'<tspan class="dim"> </tspan><tspan class="key">linkedin</tspan><tspan class="dim">   → </tspan><tspan class="value">fausto-yuuki</tspan>'),
        (330, prompt(theme, "git shortlog -sn --all | head -1")),
        (
            350,
            f'<tspan class="dim">   </tspan>'
            f'<tspan class="value" id="commit_data">0</tspan>'
            f'<tspan class="dim" id="commit_data_dots"> </tspan>'
            f'<tspan class="dim"> YuukiFST</tspan>',
        ),
        (390, prompt(theme, "cloc --sum-reports .")),
        (
            410,
            f'<tspan class="dim">  </tspan>'
            f'<tspan class="value" id="loc_data">0</tspan>'
            f'<tspan class="dim" id="loc_data_dots"> </tspan>'
            f'<tspan class="dim">lines | +</tspan>'
            f'<tspan class="addColor" id="loc_add">0</tspan>'
            f'<tspan class="dim"> / -</tspan>'
            f'<tspan class="delColor" id="loc_del">0</tspan>'
            f'<tspan class="dim" id="loc_del_dots"></tspan>',
        ),
        (450, prompt(theme, "ls ~/repos | wc -l")),
        (
            470,
            f'<tspan class="dim"> </tspan>'
            f'<tspan class="value" id="repo_data">0</tspan>'
            f'<tspan class="dim" id="repo_data_dots"> </tspan>'
            f'<tspan class="dim">repos (</tspan>'
            f'<tspan class="value" id="contrib_data">0</tspan>'
            f'<tspan class="dim"> contributed)</tspan>',
        ),
        (
            510,
            f'{prompt(theme, "")}'
            f'<tspan class="cursor">█</tspan>',
        ),
    ]

    rows = []
    for y, content in lines:
        rows.append(f'<tspan x="300" y="{y}">{content}</tspan>')
    return "\n".join(rows)


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="540px" font-size="16px">
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
</style>
<rect width="985px" height="540px" fill="{theme["bg"]}" rx="12"/>
<rect x="1" y="1" width="983px" height="538px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<text x="15" y="30" fill="{theme["fg"]}" class="ascii">
{ascii_block(theme)}
</text>
<text x="300" y="30" fill="{theme["fg"]}">
{tty_block(theme)}
</text>
</svg>'''


def main() -> None:
    for theme_name, theme in THEMES.items():
        path = ROOT / theme["file"]
        path.write_text(build_svg(theme_name), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
