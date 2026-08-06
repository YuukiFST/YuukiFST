#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — SSH session profile layout."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# NixOS snowflake (neofetch/fastfetch distro art). Block Elements only — no Nerd
# Font glyphs, because GitHub proxies the SVG through camo and only resolves
# whatever monospace font the reader's OS ships.
ASCII_LOGO = [
    "          ▗▄▄▄       ▗▄▄▄▄    ▄▄▄▖",
    "          ▜███▙       ▜███▙  ▟███▛",
    "           ▜███▙       ▜███▙▟███▛",
    "            ▜███▙       ▜██████▛",
    "     ▟█████████████████▙ ▜████▛     ▟▙",
    "    ▟███████████████████▙ ▜███▙    ▟██▙",
    "           ▄▄▄▄▖           ▜███▙  ▟███▛",
    "          ▟███▛             ▜██▛ ▟███▛",
    "         ▟███▛               ▜▛ ▟███▛",
    "▟███████████▛                  ▟██████████▙",
    "▜██████████▛                  ▟███████████▛",
    "      ▟███▛ ▟▙               ▟███▛",
    "     ▟███▛ ▟██▙             ▟███▛",
    "    ▟███▛  ▜███▙           ▝▀▀▀▀",
    "    ▜██▛    ▜███▙ ▜██████████████████▛",
    "     ▜▛     ▟████▙ ▜████████████████▛",
    "           ▟██████▙       ▜███▙",
    "          ▟███▛▜███▙       ▜███▙",
    "         ▟███▛  ▜███▙       ▜███▙",
    "         ▝▀▀▀    ▀▀▀▀▘       ▀▀▀▘",
]

THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        # Omarchy Vantablack (ghostty.conf / colors.toml) + NixOS blue accents
        "bg": "#000000",
        "fg": "#ffffff",
        "border": "#2b3a52",
        "prompt_host": "#7ebae4",
        "prompt_path": "#5277c3",
        "command": "#ffffff",
        "key": "#b6b6b6",
        "value": "#cecece",
        "dim": "#5c5c5c",
        "add": "#7ebae4",
        "delete": "#a4a4a4",
        "cursor": "#7ebae4",
        "ascii": "#7ebae4",
        "ascii_gradient": ("#8fc6ee", "#4a6cb8"),
        "titlebar": "#0d1117",
        "titlebar_text": "#8b949e",
        "statusbar": "#5277c3",
        "statusbar_text": "#e8eefc",
        "statusbar_alt": "#1b2740",
        "statusbar_alt_text": "#9db4dd",
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
        "ascii": "#5277c3",
        "ascii_gradient": ("#5277c3", "#2f4f96"),
        "titlebar": "#eee8d5",
        "titlebar_text": "#657b83",
        "statusbar": "#268bd2",
        "statusbar_text": "#fdf6e3",
        "statusbar_alt": "#eee8d5",
        "statusbar_alt_text": "#657b83",
        "font": "ConsolasFallback,Consolas,monospace",
    },
}

SVG_WIDTH = 985
SVG_HEIGHT = 600
TITLEBAR_H = 36
STATUSBAR_H = 30
STATUSBAR_Y = SVG_HEIGHT - STATUSBAR_H
SCAN_DURATION_S = 39
SCANLINE_HEIGHT = 28
SCAN_MARGIN = 10
FADE_WINDOW_PCT = 3.0
FADED_OPACITY = 0.1

ASCII_X = 20
ASCII_FONT_SIZE = 9
ASCII_LINE_H = 12
ASCII_Y_START = 170
TTY_X = 300

TTY_ROW_Y = [66, 106, 126, 146, 166, 186, 206, 226, 256, 276, 296, 316, 346, 366, 386, 416, 436, 466, 486, 516]
ASCII_ROW_Y = [ASCII_Y_START + index * ASCII_LINE_H for index in range(len(ASCII_LOGO))]
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
@keyframes logo-pulse {{
  0%, 100% {{ opacity: 0.92; }}
  50% {{ opacity: 1; }}
}}
.terminal-row {{
  opacity: 1;
}}
{row_rules}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
.ascii {{ animation: logo-pulse 6s ease-in-out infinite; }}
#terminal-scanline {{
  fill: url(#scanline-gradient);
  animation: scanline {SCAN_DURATION_S}s linear infinite;
}}
"""


def row_class(y: int) -> str:
    return f"terminal-row row-y-{y}"


def ascii_block(theme: dict, x: int = ASCII_X, y_start: int = ASCII_Y_START) -> str:
    rows = []
    for index, line in enumerate(ASCII_LOGO):
        y = y_start + index * ASCII_LINE_H
        rows.append(
            f'<tspan x="{x}" y="{y}" class="{row_class(y)}" fill="url(#logo-gradient)">'
            f"{esc(line)}</tspan>"
        )
    return "\n".join(rows)


def prompt(theme: dict, command: str) -> str:
    return (
        f'<tspan class="prompt-host">yuuki@nixos</tspan>'
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


def loc_line(indent: str = "   ") -> str:
    """Lines of code written, with the add/delete split — replaces the repo count.

    Three ids so today.py can justify each number independently.
    """
    return (
        f'<tspan class="dim">{esc(indent)}</tspan>'
        f'<tspan class="value" id="loc_data">0</tspan>'
        f'<tspan class="dim" id="loc_data_dots"></tspan>'
        f'<tspan class="dim"> lines of code   </tspan>'
        f'<tspan class="addColor" id="loc_add">0</tspan>'
        f'<tspan class="dim" id="loc_add_dots"></tspan>'
        f'<tspan class="dim">++ / </tspan>'
        f'<tspan class="delColor" id="loc_del">0</tspan>'
        f'<tspan class="dim" id="loc_del_dots"></tspan>'
        f'<tspan class="dim">--</tspan>'
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
            66,
            f'<tspan class="dim">Last login: Sat Jul 11 2026 — </tspan>'
            f'<tspan class="value" id="age_data">3 years, 9 months, 0 days</tspan>'
            f'<tspan class="dim" id="age_data_dots"></tspan>'
            f'<tspan class="dim"> on GitHub</tspan>',
        ),
        (106, prompt(theme, "fastfetch --logo nixos")),
        (126, f'<tspan class="key">yuuki@nixos</tspan><tspan class="dim"> ─────────────────────────────</tspan>'),
        (146, info_row("OS", "NixOS unstable · x86_64")),
        (166, info_row("Host", "São Benedito / IFMT")),
        (186, info_row("Shell", "bash")),
        (206, info_row("Terminal", "Ghostty")),
        (226, info_row("Role", "Fullstack")),
        (256, stack_row("Backend", "Python, Django, Go, tRPC, Prisma")),
        (276, stack_row("Frontend", "React, Next.js, TypeScript, Tailwind, shadcn/ui")),
        (296, stack_row("Databases", "PostgreSQL, Neon, Supabase")),
        (316, stack_row("DevOps", "Docker, Git, Linux, Cloudinary")),
        (346, prompt(theme, "cat ~/links")),
        (366, f'<tspan class="dim"> </tspan><tspan class="key">portfolio</tspan><tspan class="dim">  → </tspan><tspan class="value">fausto-yuuki.vercel.app</tspan>'),
        (386, f'<tspan class="dim"> </tspan><tspan class="key">linkedin</tspan><tspan class="dim">   → </tspan><tspan class="value">fausto-yuuki</tspan>'),
        (416, prompt(theme, "git shortlog -sn --all | head -1")),
        (436, stat_line("commit_data", "  commits authored by YuukiFST", "   ")),
        (466, prompt(theme, "cloc --vcs=git ~/github/*")),
        (486, loc_line()),
        (
            516,
            f'{prompt(theme, "")}'
            f'<tspan class="cursor">█</tspan>',
        ),
    ]

    rows = []
    for y, content in lines:
        rows.append(f'<tspan x="{TTY_X}" y="{y}" class="{row_class(y)}">{content}</tspan>')
    return "\n".join(rows)


def titlebar(theme: dict) -> str:
    """macOS-style window chrome so the SVG reads as a terminal at a glance."""
    dots = "".join(
        f'<circle cx="{cx}" cy="{TITLEBAR_H // 2}" r="6" fill="{color}"/>'
        for cx, color in ((26, "#ff5f57"), (48, "#febc2e"), (70, "#28c840"))
    )
    return f'''<path d="M1 13 A12 12 0 0 1 13 1 L972 1 A12 12 0 0 1 984 13 L984 {TITLEBAR_H} L1 {TITLEBAR_H} Z" fill="{theme["titlebar"]}"/>
{dots}
<text x="{SVG_WIDTH // 2}" y="{TITLEBAR_H // 2 + 5}" text-anchor="middle" font-size="13" fill="{theme["titlebar_text"]}">yuuki@nixos: ~ — ghostty</text>
<line x1="1" y1="{TITLEBAR_H}" x2="984" y2="{TITLEBAR_H}" stroke="{theme["border"]}" stroke-width="1"/>'''


def statusbar(theme: dict) -> str:
    """tmux-ish status line pinned to the bottom of the window."""
    left_w = 130
    right_w = 250
    text_y = STATUSBAR_Y + STATUSBAR_H // 2 + 5
    return f'''<path d="M1 {STATUSBAR_Y} L984 {STATUSBAR_Y} L984 {SVG_HEIGHT - 13} A12 12 0 0 1 972 {SVG_HEIGHT - 1} L13 {SVG_HEIGHT - 1} A12 12 0 0 1 1 {SVG_HEIGHT - 13} Z" fill="{theme["statusbar_alt"]}"/>
<rect x="1" y="{STATUSBAR_Y}" width="{left_w}" height="{STATUSBAR_H}" fill="{theme["statusbar"]}"/>
<text x="20" y="{text_y}" font-size="13" fill="{theme["statusbar_text"]}">[0] NIXOS</text>
<text x="{left_w + 20}" y="{text_y}" font-size="13" fill="{theme["statusbar_alt_text"]}">~/github/YuukiFST   │   main ✓   │   flake.nix</text>
<text x="{SVG_WIDTH - 20}" y="{text_y}" text-anchor="end" font-size="13" fill="{theme["statusbar_alt_text"]}">utf-8   │   nixos-unstable   │   ★ reproducible</text>'''


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    scanline = theme["prompt_host"]
    font = theme.get("font", "ConsolasFallback,Consolas,monospace")
    logo_from, logo_to = theme["ascii_gradient"]
    ascii_y_end = ASCII_Y_START + len(ASCII_LOGO) * ASCII_LINE_H
    return f'''<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="{font}" width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" font-size="16px">
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
<linearGradient id="logo-gradient" gradientUnits="userSpaceOnUse" x1="{ASCII_X}" y1="{ASCII_Y_START}" x2="285" y2="{ascii_y_end}">
<stop offset="0%" stop-color="{logo_from}"/>
<stop offset="100%" stop-color="{logo_to}"/>
</linearGradient>
</defs>
<rect width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="12"/>
{titlebar(theme)}
{statusbar(theme)}
<rect x="1" y="1" width="983px" height="{SVG_HEIGHT - 2}px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<rect id="terminal-scanline" x="12" y="0" width="961" height="{SCANLINE_HEIGHT}" opacity="0"/>
<text x="15" y="30" fill="{theme["ascii"]}" class="ascii" font-size="{ASCII_FONT_SIZE}px">
{ascii_block(theme)}
</text>
<text x="{TTY_X}" y="30" fill="{theme["fg"]}">
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
