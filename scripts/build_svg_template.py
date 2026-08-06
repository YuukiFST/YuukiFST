#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — tmux/NixOS session profile.

Layout is a two-pane tmux window:
  left pane  — NixOS snowflake logo + flake.nix
  right pane — fastfetch output, links, git stats, contribution heatmap

The heatmap grid and its month labels are emitted here as an empty placeholder;
today.py fills them with the real contribution calendar (and the stat numbers)
on every run.
"""

from __future__ import annotations

import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# NixOS snowflake, split into the two lambda triads the official logo alternates
# (tone 1 = light blue, tone 2 = dark blue). Block Elements only — no Nerd Font
# glyphs, because GitHub proxies the SVG through camo and only resolves whatever
# monospace font the reader's OS ships.
ASCII_LOGO: list[list[tuple[str, int]]] = [
    [("          ▗▄▄▄       ", 1), ("▗▄▄▄▄    ▄▄▄▖", 2)],
    [("          ▜███▙       ", 1), ("▜███▙  ▟███▛", 2)],
    [("           ▜███▙       ", 1), ("▜███▙▟███▛", 2)],
    [("            ▜███▙       ", 1), ("▜██████▛", 2)],
    [("     ▟█████████████████▙ ", 1), ("▜████▛     ▟▙", 2)],
    [("    ▟███████████████████▙ ", 1), ("▜███▙    ▟██▙", 2)],
    [("           ▄▄▄▄▖           ", 1), ("▜███▙  ▟███▛", 2)],
    [("          ▟███▛             ", 1), ("▜██▛ ▟███▛", 2)],
    [("         ▟███▛               ", 1), ("▜▛ ▟███▛", 2)],
    [("▟███████████▛                  ", 1), ("▟██████████▙", 2)],
    [("▜██████████▛                  ", 2), ("▟███████████▛", 1)],
    [("      ▟███▛ ▟▙               ", 2), ("▟███▛", 1)],
    [("     ▟███▛ ▟██▙             ", 2), ("▟███▛", 1)],
    [("    ▟███▛  ▜███▙           ", 2), ("▝▀▀▀▀", 1)],
    [("    ▜██▛    ▜███▙ ", 2), ("▜██████████████████▛", 1)],
    [("     ▜▛     ▟████▙ ", 2), ("▜████████████████▛", 1)],
    [("           ▟██████▙       ", 2), ("▜███▙", 1)],
    [("          ▟███▛▜███▙       ", 2), ("▜███▙", 1)],
    [("         ▟███▛  ▜███▙       ", 2), ("▜███▙", 1)],
    [("         ▝▀▀▀    ▀▀▀▀▘       ", 2), ("▀▀▀▘", 1)],
]

# (text, css class) per line — the profile as a derivation
FLAKE_LINES: list[list[tuple[str, str]]] = [
    [("{", "nix-punct")],
    [("  description", "nix-key"), (" = ", "nix-punct"), ('"fullstack dev, NixOS user"', "nix-str"), (";", "nix-punct")],
    [("", "nix-punct")],
    [("  inputs = {", "nix-key")],
    [("    backend.url", "nix-attr"), ("  = ", "nix-punct"), ('"python+django+go"', "nix-str"), (";", "nix-punct")],
    [("    frontend.url", "nix-attr"), (" = ", "nix-punct"), ('"react+next+ts"', "nix-str"), (";", "nix-punct")],
    [("    data.url", "nix-attr"), ("     = ", "nix-punct"), ('"postgres+prisma"', "nix-str"), (";", "nix-punct")],
    [("  };", "nix-key")],
    [("", "nix-punct")],
    [("  outputs = { self, ... }: {", "nix-key")],
    [("    devShells.default", "nix-attr"), (" =", "nix-punct")],
    [("      pkgs.mkShell { buildInputs = [", "nix-punct")],
    [("        docker git neovim ghostty", "nix-val")],
    [("      ]; };", "nix-punct")],
    [("  };", "nix-key")],
    [("}", "nix-punct")],
]

THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        # Omarchy Vantablack (ghostty.conf / colors.toml) + NixOS blue accents
        "bg": "#000000",
        "fg": "#ffffff",
        "border": "#2b3a52",
        "pane_border": "#1d2942",
        "prompt_host": "#7ebae4",
        "prompt_path": "#5277c3",
        "command": "#ffffff",
        "key": "#b6b6b6",
        "value": "#cecece",
        "dim": "#5c5c5c",
        "ok": "#28c840",
        "add": "#7ebae4",
        "delete": "#a4a4a4",
        "cursor": "#7ebae4",
        "logo_1": "#7ebae4",
        "logo_2": "#5277c3",
        "nix_key": "#7ebae4",
        "nix_attr": "#b6b6b6",
        "nix_str": "#28c840",
        "nix_val": "#cecece",
        "nix_punct": "#5c5c5c",
        "heat": ["#10161f", "#1b3a5c", "#2b5d8f", "#4a8ec2", "#7ebae4"],
        "palette": ["#000000", "#ff5f57", "#28c840", "#febc2e", "#5277c3", "#c678dd", "#56b6c2", "#cecece"],
        "palette_bright": ["#5c5c5c", "#ff8b85", "#5ce06f", "#ffd479", "#7ebae4", "#dda0ee", "#8ad9e3", "#ffffff"],
        "titlebar": "#0d1117",
        "titlebar_text": "#8b949e",
        "statusbar": "#5277c3",
        "statusbar_text": "#e8eefc",
        "statusbar_alt": "#101828",
        "statusbar_alt_text": "#9db4dd",
        "font": "FantasqueSansM Nerd Font,ConsolasFallback,Consolas,monospace",
    },
    "light": {
        "file": "light_mode.svg",
        "bg": "#fdf6e3",
        "fg": "#657b83",
        "border": "#93a1a1",
        "pane_border": "#c8c0aa",
        "prompt_host": "#268bd2",
        "prompt_path": "#859900",
        "command": "#657b83",
        "key": "#cb4b16",
        "value": "#073642",
        "dim": "#93a1a1",
        "ok": "#859900",
        "add": "#859900",
        "delete": "#dc322f",
        "cursor": "#6c71c4",
        "logo_1": "#5277c3",
        "logo_2": "#2f4f96",
        "nix_key": "#268bd2",
        "nix_attr": "#cb4b16",
        "nix_str": "#859900",
        "nix_val": "#073642",
        "nix_punct": "#93a1a1",
        "heat": ["#eee8d5", "#b8d2ea", "#7aa9d6", "#4380bd", "#1f5a94"],
        "palette": ["#073642", "#dc322f", "#859900", "#b58900", "#268bd2", "#d33682", "#2aa198", "#eee8d5"],
        "palette_bright": ["#586e75", "#cb4b16", "#9fb300", "#d4a017", "#5294cf", "#e05a9c", "#3fc4b8", "#fdf6e3"],
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
SVG_HEIGHT = 810
TITLEBAR_H = 36
STATUSBAR_H = 30
STATUSBAR_Y = SVG_HEIGHT - STATUSBAR_H
SCAN_DURATION_S = 39
SCANLINE_HEIGHT = 28
SCAN_MARGIN = 10
FADE_WINDOW_PCT = 3.0
FADED_OPACITY = 0.1

# Advance width of the 16px monospace face, measured against the rendered SVG.
# Used to place the typing masks over each command.
CHAR_W = 9.6
PROMPT_LEN = len("yuuki@nixos:~$ ")

PANE_X = 292
ASCII_X = 15
ASCII_FONT_SIZE = 10
ASCII_LINE_H = 12
ASCII_Y_START = 80
FLAKE_X = 15
FLAKE_FONT_SIZE = 11
FLAKE_LINE_H = 16
FLAKE_Y_START = 420
TTY_X = 300

PALETTE_ROW_Y = (376, 396)
PALETTE_CELL_W = 22
PALETTE_CELL_H = 12

HEAT_CELL = 9
HEAT_GAP = 2
HEAT_PITCH = HEAT_CELL + HEAT_GAP
HEAT_WEEKS = 53
HEAT_X = TTY_X
HEAT_Y = 626
HEAT_MONTHS_Y = 616
HEAT_LEGEND_Y = 716

TTY_ROW_Y = [66, 86, 106, 136, 156, 176, 196, 216, 236, 256, 286, 306, 326, 346, 426, 446, 466, 496, 516, 546, 566, 596, 746]
ASCII_ROW_Y = [ASCII_Y_START + index * ASCII_LINE_H for index in range(len(ASCII_LOGO))]
FLAKE_HEADER_Y = FLAKE_Y_START - FLAKE_LINE_H - 8
FLAKE_ROW_Y = [FLAKE_HEADER_Y] + [
    FLAKE_Y_START + index * FLAKE_LINE_H for index in range(len(FLAKE_LINES))
]
ALL_ROW_Y = sorted(set(TTY_ROW_Y + ASCII_ROW_Y + FLAKE_ROW_Y + list(PALETTE_ROW_Y)))
FIRST_ROW_Y = min(ALL_ROW_Y)
LAST_ROW_Y = max(ALL_ROW_Y)
SCAN_START = FIRST_ROW_Y - SCANLINE_HEIGHT - SCAN_MARGIN
SCAN_END = LAST_ROW_Y + SCAN_MARGIN
SCAN_SPAN = SCAN_END - SCAN_START

# Command typing. The session starts fully typed and re-types near the end of
# the loop, so any renderer that freezes on frame 0 (social cards, PDF exports)
# still shows every command.
TYPE_COVER_PCT = 58.0
TYPE_FIRST_PCT = 62.0
TYPE_STAGGER_PCT = 6.0
TYPE_WINDOW_PCT = 3.2


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


def typing_keyframes(commands: list[tuple[int, str]]) -> str:
    """One reveal animation per command.

    The mask defaults to scaleX(0) — a renderer that ignores CSS animation shows
    every command in full rather than a row of blank bars.
    """
    blocks = []
    for index, (_, command) in enumerate(commands):
        start = TYPE_FIRST_PCT + index * TYPE_STAGGER_PCT
        end = min(start + TYPE_WINDOW_PCT, 99.5)
        steps = max(1, len(command))
        blocks.append(
            f"""@keyframes type-{index} {{
  0%, {TYPE_COVER_PCT:.1f}% {{ transform: scaleX(0); }}
  {TYPE_COVER_PCT + 0.1:.1f}%, {start:.1f}% {{ transform: scaleX(1); animation-timing-function: steps({steps}, end); }}
  {end:.1f}%, 100% {{ transform: scaleX(0); }}
}}
.type-{index} {{ animation: type-{index} {SCAN_DURATION_S}s linear infinite; }}"""
        )
    return "\n".join(blocks)


def animation_styles(theme: dict, commands: list[tuple[int, str]]) -> str:
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
  0%, 100% {{ opacity: 0.9; }}
  50% {{ opacity: 1; }}
}}
.terminal-row {{
  opacity: 1;
}}
{row_rules}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
.ascii {{ animation: logo-pulse 6s ease-in-out infinite; }}
.type-mask {{ transform: scaleX(0); transform-origin: right center; transform-box: fill-box; }}
{typing_keyframes(commands)}
#terminal-scanline {{
  fill: url(#scanline-gradient);
  animation: scanline {SCAN_DURATION_S}s linear infinite;
}}
"""


def row_class(y: int) -> str:
    return f"terminal-row row-y-{y}"


def ascii_block(theme: dict) -> str:
    rows = []
    for index, segments in enumerate(ASCII_LOGO):
        y = ASCII_Y_START + index * ASCII_LINE_H
        parts = [
            f'<tspan class="logo-{tone}">{esc(text)}</tspan>'
            for text, tone in segments
        ]
        rows.append(
            f'<tspan x="{ASCII_X}" y="{y}" class="{row_class(y)}">{"".join(parts)}</tspan>'
        )
    return "\n".join(rows)


def flake_block(theme: dict) -> str:
    header_y = FLAKE_Y_START - FLAKE_LINE_H - 8
    rows = [
        f'<tspan x="{FLAKE_X}" y="{header_y}" class="terminal-row row-y-{header_y}">'
        f'<tspan class="prompt-host">yuuki@nixos</tspan>'
        f'<tspan class="prompt-path">:~$</tspan> '
        f'<tspan class="command">bat flake.nix</tspan></tspan>'
    ]
    for index, segments in enumerate(FLAKE_LINES):
        y = FLAKE_Y_START + index * FLAKE_LINE_H
        parts = [f'<tspan class="{cls}">{esc(text)}</tspan>' for text, cls in segments]
        rows.append(
            f'<tspan x="{FLAKE_X}" y="{y}" class="{row_class(y)}">{"".join(parts)}</tspan>'
        )
    return "\n".join(rows)


def prompt(command: str) -> str:
    return (
        f'<tspan class="prompt-host">yuuki@nixos</tspan>'
        f'<tspan class="prompt-path">:~$</tspan> '
        f'<tspan class="command">{esc(command)}</tspan>'
    )


def boot_row(unit: str) -> str:
    return (
        f'<tspan class="dim">[</tspan>'
        f'<tspan class="ok">  OK  </tspan>'
        f'<tspan class="dim">] </tspan>'
        f'<tspan class="value">{esc(unit)}</tspan>'
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
    """Lines of code written, with the add/delete split.

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


def tty_rows() -> list[tuple[int, str]]:
    return [
        (66, boot_row("Started yuuki.service — GitHub profile daemon")),
        (86, boot_row("Reached target Multi-User System")),
        (
            106,
            f'<tspan class="dim">Last login: Sat Jul 11 2026 — </tspan>'
            f'<tspan class="value" id="age_data">3 years, 9 months, 0 days</tspan>'
            f'<tspan class="dim" id="age_data_dots"></tspan>'
            f'<tspan class="dim"> on GitHub</tspan>',
        ),
        (136, prompt("fastfetch --logo nixos")),
        (156, f'<tspan class="key">yuuki@nixos</tspan><tspan class="dim"> ─────────────────────────────</tspan>'),
        (176, info_row("OS", "NixOS unstable · x86_64")),
        (196, info_row("Host", "São Benedito / IFMT")),
        (216, info_row("Shell", "bash")),
        (236, info_row("Terminal", "Ghostty")),
        (256, info_row("Role", "Fullstack")),
        (286, stack_row("Backend", "Python, Django, Go, tRPC, Prisma")),
        (306, stack_row("Frontend", "React, Next.js, TypeScript, Tailwind, shadcn/ui")),
        (326, stack_row("Databases", "PostgreSQL, Neon, Supabase")),
        (346, stack_row("DevOps", "Docker, Git, Linux, Cloudinary")),
        (426, prompt("cat ~/links")),
        (446, f'<tspan class="dim"> </tspan><tspan class="key">portfolio</tspan><tspan class="dim">  → </tspan><tspan class="value">fausto-yuuki.vercel.app</tspan>'),
        (466, f'<tspan class="dim"> </tspan><tspan class="key">linkedin</tspan><tspan class="dim">   → </tspan><tspan class="value">fausto-yuuki</tspan>'),
        (496, prompt("git shortlog -sn --all | head -1")),
        (516, stat_line("commit_data", "  commits authored by YuukiFST", "   ")),
        (546, prompt("cloc --vcs=git ~/github/*")),
        (566, loc_line()),
        (596, prompt("gh api graphql -f query=contributionCalendar")),
        (746, f'{prompt("")}<tspan class="cursor">█</tspan>'),
    ]


def typed_commands() -> list[tuple[int, str]]:
    """(row y, command) for every non-empty prompt — drives the typing masks."""
    return [
        (136, "fastfetch --logo nixos"),
        (426, "cat ~/links"),
        (496, "git shortlog -sn --all | head -1"),
        (546, "cloc --vcs=git ~/github/*"),
        (596, "gh api graphql -f query=contributionCalendar"),
    ]


def typing_masks(theme: dict) -> str:
    """Bg-colored rects that uncover each command left-to-right.

    Painted after the text, so they must stay last in document order.
    """
    rects = []
    for index, (y, command) in enumerate(typed_commands()):
        x = TTY_X + PROMPT_LEN * CHAR_W
        width = len(command) * CHAR_W + 2
        rects.append(
            f'<rect class="type-mask type-{index}" x="{x:.1f}" y="{y - 14}" '
            f'width="{width:.1f}" height="19" fill="{theme["bg"]}"/>'
        )
    return "\n".join(rects)


def tty_block() -> str:
    rows = []
    for y, content in tty_rows():
        rows.append(f'<tspan x="{TTY_X}" y="{y}" class="{row_class(y)}">{content}</tspan>')
    return "\n".join(rows)


def palette_block(theme: dict) -> str:
    """The two swatch rows fastfetch prints under the info block."""
    groups = []
    for row_index, (y, colors) in enumerate(
        zip(PALETTE_ROW_Y, (theme["palette"], theme["palette_bright"]))
    ):
        cells = "".join(
            f'<rect x="{TTY_X + 4 + index * PALETTE_CELL_W}" y="{y - PALETTE_CELL_H}" '
            f'width="{PALETTE_CELL_W - 4}" height="{PALETTE_CELL_H}" rx="2" fill="{color}" '
            f'stroke="{theme["pane_border"]}" stroke-width="1"/>'
            for index, color in enumerate(colors)
        )
        groups.append(f'<g class="{row_class(y)}">{cells}</g>')
    return "\n".join(groups)


def heatmap_placeholder(theme: dict) -> str:
    """Empty calendar grid + month labels; today.py replaces both with real data."""
    cells = "".join(
        f'<rect class="lvl0" x="{week * HEAT_PITCH}" y="{day * HEAT_PITCH}" '
        f'width="{HEAT_CELL}" height="{HEAT_CELL}" rx="2"/>'
        for week in range(HEAT_WEEKS)
        for day in range(7)
    )
    today = datetime.date.today()
    months = []
    for index in range(12):
        month = (today.month - 11 + index - 1) % 12 + 1
        label = datetime.date(2000, month, 1).strftime("%b")
        months.append(
            f'<tspan x="{HEAT_X + index * (HEAT_WEEKS * HEAT_PITCH) // 12}" '
            f'y="{HEAT_MONTHS_Y}">{label}</tspan>'
        )
    legend_cells = "".join(
        f'<rect class="lvl{level}" x="{HEAT_X + 44 + level * HEAT_PITCH}" '
        f'y="{HEAT_LEGEND_Y - 9}" width="{HEAT_CELL}" height="{HEAT_CELL}" rx="2"/>'
        for level in range(5)
    )
    return f'''<text id="heatmap_months" class="dim" font-size="11px" fill="{theme["dim"]}">
{"".join(months)}
</text>
<g id="heatmap" transform="translate({HEAT_X},{HEAT_Y})">{cells}</g>
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X}" y="{HEAT_LEGEND_Y}">Less</text>
{legend_cells}
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X + 44 + 5 * HEAT_PITCH + 6}" y="{HEAT_LEGEND_Y}">More</text>'''


def titlebar(theme: dict) -> str:
    """macOS-style window chrome so the SVG reads as a terminal at a glance."""
    dots = "".join(
        f'<circle cx="{cx}" cy="{TITLEBAR_H // 2}" r="6" fill="{color}"/>'
        for cx, color in ((26, "#ff5f57"), (48, "#febc2e"), (70, "#28c840"))
    )
    return f'''<path d="M1 13 A12 12 0 0 1 13 1 L972 1 A12 12 0 0 1 984 13 L984 {TITLEBAR_H} L1 {TITLEBAR_H} Z" fill="{theme["titlebar"]}"/>
{dots}
<text x="{SVG_WIDTH // 2}" y="{TITLEBAR_H // 2 + 5}" text-anchor="middle" font-size="13" fill="{theme["titlebar_text"]}">yuuki@nixos: ~ — tmux — ghostty</text>
<line x1="1" y1="{TITLEBAR_H}" x2="984" y2="{TITLEBAR_H}" stroke="{theme["border"]}" stroke-width="1"/>'''


def statusbar(theme: dict) -> str:
    """tmux status line pinned to the bottom of the window."""
    left_w = 130
    text_y = STATUSBAR_Y + STATUSBAR_H // 2 + 5
    return f'''<path d="M1 {STATUSBAR_Y} L984 {STATUSBAR_Y} L984 {SVG_HEIGHT - 13} A12 12 0 0 1 972 {SVG_HEIGHT - 1} L13 {SVG_HEIGHT - 1} A12 12 0 0 1 1 {SVG_HEIGHT - 13} Z" fill="{theme["statusbar_alt"]}"/>
<rect x="1" y="{STATUSBAR_Y}" width="{left_w}" height="{STATUSBAR_H}" fill="{theme["statusbar"]}"/>
<text x="20" y="{text_y}" font-size="13" fill="{theme["statusbar_text"]}">[0] NIXOS</text>
<text x="{left_w + 20}" y="{text_y}" font-size="13" fill="{theme["statusbar_alt_text"]}">0:flake*   1:session-   │   ~/github/YuukiFST</text>
<text x="{SVG_WIDTH - 20}" y="{text_y}" text-anchor="end" font-size="13" fill="{theme["statusbar_alt_text"]}">main ✓   │   nixos-unstable   │   ★ reproducible</text>'''


def pane_divider(theme: dict) -> str:
    return (
        f'<line x1="{PANE_X}" y1="{TITLEBAR_H}" x2="{PANE_X}" y2="{STATUSBAR_Y}" '
        f'stroke="{theme["pane_border"]}" stroke-width="1"/>'
    )


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    scanline = theme["prompt_host"]
    font = theme.get("font", "ConsolasFallback,Consolas,monospace")
    heat_rules = "\n".join(
        f".lvl{level} {{fill: {color};}}" for level, color in enumerate(theme["heat"])
    )
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
.ok {{fill: {theme["ok"]};}}
.addColor {{fill: {theme["add"]};}}
.delColor {{fill: {theme["delete"]};}}
.cursor {{fill: {theme["cursor"]};}}
.logo-1 {{fill: {theme["logo_1"]};}}
.logo-2 {{fill: {theme["logo_2"]};}}
.nix-key {{fill: {theme["nix_key"]};}}
.nix-attr {{fill: {theme["nix_attr"]};}}
.nix-str {{fill: {theme["nix_str"]};}}
.nix-val {{fill: {theme["nix_val"]};}}
.nix-punct {{fill: {theme["nix_punct"]};}}
{heat_rules}
text, tspan {{white-space: pre;}}
{animation_styles(theme, typed_commands())}
</style>
<defs>
<linearGradient id="scanline-gradient" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="{theme["bg"]}" stop-opacity="0"/>
<stop offset="47%" stop-color="{scanline}" stop-opacity="0.4"/>
<stop offset="53%" stop-color="{scanline}" stop-opacity="0.4"/>
<stop offset="100%" stop-color="{theme["bg"]}" stop-opacity="0"/>
</linearGradient>
<filter id="phosphor" x="-25%" y="-25%" width="150%" height="150%">
<feGaussianBlur stdDeviation="2.4" result="blurred"/>
<feMerge>
<feMergeNode in="blurred"/>
<feMergeNode in="SourceGraphic"/>
</feMerge>
</filter>
</defs>
<rect width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="12"/>
{titlebar(theme)}
{statusbar(theme)}
{pane_divider(theme)}
<rect x="1" y="1" width="983px" height="{SVG_HEIGHT - 2}px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<rect id="terminal-scanline" x="12" y="0" width="961" height="{SCANLINE_HEIGHT}" opacity="0"/>
<text x="15" y="30" fill="{theme["logo_1"]}" class="ascii" font-size="{ASCII_FONT_SIZE}px" filter="url(#phosphor)">
{ascii_block(theme)}
</text>
<text x="{FLAKE_X}" y="30" fill="{theme["fg"]}" font-size="{FLAKE_FONT_SIZE}px">
{flake_block(theme)}
</text>
<text x="{TTY_X}" y="30" fill="{theme["fg"]}">
{tty_block()}
</text>
{palette_block(theme)}
{heatmap_placeholder(theme)}
{typing_masks(theme)}
</svg>'''


def main() -> None:
    for theme_name in THEMES:
        path = ROOT / THEMES[theme_name]["file"]
        path.write_text(build_svg(theme_name), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
