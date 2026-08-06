#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — tmux/NixOS session profile.

Layout is a two-pane tmux window:
  left pane  — NixOS snowflake logo + flake.nix
  right pane — fastfetch output, links, git stats, contribution heatmap

Animation is a session replay: every row prints in on its own cue and then
stays lit for the rest of the loop. Nothing ever dims. Both the reveal and the
command-typing masks are fail-safe — a renderer that ignores CSS animation
shows the finished session, never a blank window.

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

# (text, css class) per line — the profile as a derivation.
# Lines must fit the left pane; FLAKE_MAX_COLS is enforced in main().
FLAKE_LINES: list[list[tuple[str, str]]] = [
    [("{", "nix-punct")],
    [("  description", "nix-key"), (" = ", "nix-punct"), ('"nixos + fullstack"', "nix-str"), (";", "nix-punct")],
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
FLAKE_MAX_COLS = 40

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
FLAKE_HEADER_Y = FLAKE_Y_START - FLAKE_LINE_H - 8
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

# Session replay timing (seconds). The loop opens on the finished session, holds
# it, clears, replays it, then holds again — so frame 0 is always the full
# window and nothing ever dims.
HOLD_BEFORE_S = 10.0
HOLD_AFTER_S = 6.0
LOOP_S = 22.0  # recomputed from the session span in build_svg()
TYPE_CHAR_S = 0.035
PRINT_ROW_S = 0.08
PRINT_LOGO_S = 0.03
PRINT_FLAKE_S = 0.05
BEAT_S = 0.25


class Reveal:
    """Assigns a CSS class per print-in cue, deduplicating identical timings."""

    def __init__(self) -> None:
        self.classes: dict[float, str] = {}

    def at(self, seconds: float) -> str:
        key = round(seconds, 2)
        if key not in self.classes:
            self.classes[key] = f"rv{len(self.classes)}"
        return self.classes[key]

    def css(self) -> str:
        blocks = [".reveal {opacity: 1;}"]
        for seconds, name in self.classes.items():
            clear_at = HOLD_BEFORE_S / LOOP_S * 100
            print_at = (HOLD_BEFORE_S + seconds) / LOOP_S * 100
            lit_at = min(print_at + 0.3, 99.8)
            blocks.append(
                f"@keyframes {name} {{\n"
                f"  0%, {clear_at:.2f}% {{ opacity: 1; }}\n"
                f"  {clear_at + 0.01:.2f}%, {print_at:.2f}% {{ opacity: 0; }}\n"
                f"  {lit_at:.2f}%, 100% {{ opacity: 1; }}\n"
                f"}}\n"
                f".{name} {{ animation: {name} {LOOP_S}s linear infinite; }}"
            )
        return "\n".join(blocks)


REVEAL = Reveal()
# (mask index, row y, command, seconds the command starts typing)
TYPED: list[tuple[int, int, str, float]] = []


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def flake_line_width(segments: list[tuple[str, str]]) -> int:
    return sum(len(text) for text, _ in segments)


def typing_css() -> str:
    """Mask that uncovers a command one character at a time.

    Defaults to scaleX(0) so a renderer without CSS animation shows the command
    in full instead of a blank bar.
    """
    blocks = [".type-mask {transform: scaleX(0); transform-origin: right center; transform-box: fill-box;}"]
    for index, (_, _, command, cue) in enumerate(TYPED):
        duration = len(command) * TYPE_CHAR_S
        clear_pct = HOLD_BEFORE_S / LOOP_S * 100
        start_pct = (HOLD_BEFORE_S + cue) / LOOP_S * 100
        end_pct = min((HOLD_BEFORE_S + cue + duration) / LOOP_S * 100, 99.8)
        blocks.append(
            f"@keyframes type-{index} {{\n"
            f"  0%, {clear_pct:.2f}% {{ transform: scaleX(0); }}\n"
            f"  {clear_pct + 0.01:.2f}%, {start_pct:.2f}% {{ transform: scaleX(1); animation-timing-function: steps({max(1, len(command))}, end); }}\n"
            f"  {end_pct:.2f}%, 100% {{ transform: scaleX(0); }}\n"
            f"}}\n"
            f".type-{index} {{ animation: type-{index} {LOOP_S}s linear infinite; }}"
        )
    return "\n".join(blocks)


def animation_styles() -> str:
    return f"""
{REVEAL.css()}
{typing_css()}
@keyframes cursor-blink {{
  0%, 45% {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}
@keyframes logo-pulse {{
  0%, 100% {{ opacity: 0.9; }}
  50% {{ opacity: 1; }}
}}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
.ascii {{ animation: logo-pulse 6s ease-in-out infinite; }}
"""


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


class Session:
    """Builds the replay: rows are emitted in the order the session prints them."""

    def __init__(self) -> None:
        self.clock = 0.3
        self.tty: list[str] = []
        self.logo: list[str] = []
        self.flake: list[str] = []
        self.cues: dict[str, float] = {}

    def _tspan(self, x: int, y: int, content: str, seconds: float) -> str:
        return f'<tspan x="{x}" y="{y}" class="reveal {REVEAL.at(seconds)}">{content}</tspan>'

    def beat(self, seconds: float = BEAT_S) -> None:
        self.clock += seconds

    def output(self, y: int, content: str, step: float = PRINT_ROW_S) -> None:
        self.tty.append(self._tspan(TTY_X, y, content, self.clock))
        self.clock += step

    def command(self, y: int, text: str) -> None:
        """Prompt appears, then the command types itself in."""
        self.tty.append(self._tspan(TTY_X, y, prompt(text), self.clock))
        TYPED.append((len(TYPED), y, text, self.clock))
        self.clock += len(text) * TYPE_CHAR_S + 0.15

    def logo_pane(self) -> None:
        for index, segments in enumerate(ASCII_LOGO):
            y = ASCII_Y_START + index * ASCII_LINE_H
            parts = "".join(
                f'<tspan class="logo-{tone}">{esc(text)}</tspan>' for text, tone in segments
            )
            self.logo.append(self._tspan(ASCII_X, y, parts, self.clock))
            self.clock += PRINT_LOGO_S

    def flake_pane(self) -> None:
        header = (
            f'<tspan class="prompt-host">yuuki@nixos</tspan>'
            f'<tspan class="prompt-path">:~$</tspan> '
            f'<tspan class="command">bat flake.nix</tspan>'
        )
        self.flake.append(self._tspan(FLAKE_X, FLAKE_HEADER_Y, header, self.clock))
        TYPED.append((len(TYPED), FLAKE_HEADER_Y, "bat flake.nix", self.clock))
        self.clock += len("bat flake.nix") * TYPE_CHAR_S + 0.15
        for index, segments in enumerate(FLAKE_LINES):
            y = FLAKE_Y_START + index * FLAKE_LINE_H
            parts = "".join(
                f'<tspan class="{cls}">{esc(text)}</tspan>' for text, cls in segments
            )
            self.flake.append(self._tspan(FLAKE_X, y, parts, self.clock))
            self.clock += PRINT_FLAKE_S

    def mark(self, name: str) -> None:
        self.cues[name] = self.clock


def build_session() -> Session:
    session = Session()

    session.output(66, boot_row("Started yuuki.service — GitHub profile daemon"), 0.18)
    session.output(86, boot_row("Reached target Multi-User System"), 0.18)
    session.output(
        106,
        f'<tspan class="dim">Last login: Sat Jul 11 2026 — </tspan>'
        f'<tspan class="value" id="age_data">3 years, 9 months, 0 days</tspan>'
        f'<tspan class="dim" id="age_data_dots"></tspan>'
        f'<tspan class="dim"> on GitHub</tspan>',
    )
    session.beat()

    session.command(136, "fastfetch --logo nixos")
    # fastfetch prints the logo and the info block side by side
    info_start = session.clock
    session.logo_pane()
    session.clock = info_start
    session.output(156, '<tspan class="key">yuuki@nixos</tspan><tspan class="dim"> ─────────────────────────────</tspan>')
    session.output(176, info_row("OS", "NixOS unstable · x86_64"))
    session.output(196, info_row("Host", "São Benedito / IFMT"))
    session.output(216, info_row("Shell", "bash"))
    session.output(236, info_row("Terminal", "Ghostty"))
    session.output(256, info_row("Role", "Fullstack"))
    session.output(286, stack_row("Backend", "Python, Django, Go, tRPC, Prisma"))
    session.output(306, stack_row("Frontend", "React, Next.js, TypeScript, Tailwind, shadcn/ui"))
    session.output(326, stack_row("Databases", "PostgreSQL, Neon, Supabase"))
    session.output(346, stack_row("DevOps", "Docker, Git, Linux, Cloudinary"))
    session.mark("palette_1")
    session.clock += PRINT_ROW_S
    session.mark("palette_2")
    session.clock += PRINT_ROW_S
    session.beat()

    session.command(426, "cat ~/links")
    session.output(446, f'<tspan class="dim"> </tspan><tspan class="key">portfolio</tspan><tspan class="dim">  → </tspan><tspan class="value">fausto-yuuki.vercel.app</tspan>')
    session.output(466, f'<tspan class="dim"> </tspan><tspan class="key">linkedin</tspan><tspan class="dim">   → </tspan><tspan class="value">fausto-yuuki</tspan>')
    session.beat()

    # left pane catches up while the right pane pauses
    flake_start = session.clock
    session.flake_pane()
    session.clock = max(flake_start + 0.4, session.clock - 0.6)

    session.command(496, "git shortlog -sn --all | head -1")
    session.output(516, stat_line("commit_data", "  commits authored by YuukiFST", "   "))
    session.beat()

    session.command(546, "cloc --vcs=git ~/github/*")
    session.output(566, loc_line())
    session.beat()

    session.command(596, "gh api graphql -f query=contributionCalendar")
    session.mark("heatmap")
    session.clock += 0.5
    session.beat()

    session.output(746, f'{prompt("")}<tspan class="cursor">█</tspan>')
    return session


def palette_block(theme: dict, session: Session) -> str:
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
        cue = session.cues[f"palette_{row_index + 1}"]
        groups.append(f'<g class="reveal {REVEAL.at(cue)}">{cells}</g>')
    return "\n".join(groups)


def heatmap_placeholder(theme: dict, session: Session) -> str:
    """Empty calendar grid + month labels; today.py replaces both with real data."""
    cue = REVEAL.at(session.cues["heatmap"])
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
    return f'''<text id="heatmap_months" class="dim reveal {cue}" font-size="11px" fill="{theme["dim"]}">
{"".join(months)}
</text>
<g id="heatmap" class="reveal {cue}" transform="translate({HEAT_X},{HEAT_Y})">{cells}</g>
<g class="reveal {cue}">
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X}" y="{HEAT_LEGEND_Y}">Less</text>
{legend_cells}
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X + 44 + 5 * HEAT_PITCH + 6}" y="{HEAT_LEGEND_Y}">More</text>
</g>'''


def typing_masks(theme: dict) -> str:
    """Bg-colored rects that uncover each command left-to-right.

    Painted after the text, so they must stay last in document order.
    """
    rects = []
    for index, (_, y, command, _) in enumerate(TYPED):
        left_pane = y == FLAKE_HEADER_Y
        char_w = FLAKE_FONT_SIZE * 0.60 if left_pane else CHAR_W
        x = (FLAKE_X if left_pane else TTY_X) + PROMPT_LEN * char_w
        width = len(command) * char_w + 2
        height = 14 if left_pane else 19
        rects.append(
            f'<rect class="type-mask type-{index}" x="{x:.1f}" y="{y - height + 3}" '
            f'width="{width:.1f}" height="{height}" fill="{theme["bg"]}"/>'
        )
    return "\n".join(rects)


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
    global REVEAL, TYPED, LOOP_S
    REVEAL = Reveal()
    TYPED = []

    theme = THEMES[theme_name]
    session = build_session()
    LOOP_S = HOLD_BEFORE_S + session.clock + HOLD_AFTER_S
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
{animation_styles()}
</style>
<defs>
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
<text x="15" y="30" fill="{theme["logo_1"]}" class="ascii" font-size="{ASCII_FONT_SIZE}px" filter="url(#phosphor)">
{"".join(chr(10) + row for row in session.logo)}
</text>
<text x="{FLAKE_X}" y="30" fill="{theme["fg"]}" font-size="{FLAKE_FONT_SIZE}px">
{"".join(chr(10) + row for row in session.flake)}
</text>
<text x="{TTY_X}" y="30" fill="{theme["fg"]}">
{"".join(chr(10) + row for row in session.tty)}
</text>
{palette_block(theme, session)}
{heatmap_placeholder(theme, session)}
{typing_masks(theme)}
</svg>'''


def main() -> None:
    too_wide = [
        "".join(text for text, _ in line)
        for line in FLAKE_LINES
        if flake_line_width(line) > FLAKE_MAX_COLS
    ]
    if too_wide:
        raise SystemExit(
            f"flake.nix lines exceed {FLAKE_MAX_COLS} cols and would spill into the "
            f"right pane: {too_wide}"
        )
    for theme_name in THEMES:
        path = ROOT / THEMES[theme_name]["file"]
        path.write_text(build_svg(theme_name), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
