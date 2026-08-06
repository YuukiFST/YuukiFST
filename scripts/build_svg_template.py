#!/usr/bin/env python3
"""Generate dark_mode.svg and light_mode.svg — tmux/NixOS session profile.

Layout is a two-pane tmux window:
  left pane  — NixOS snowflake logo, git log --graph, a cava equalizer
  right pane — fastfetch output, links, git stats, contribution heatmap

Animation is a session replay: the loop opens on the finished session, holds
it, clears, and reprints every row on its own cue. Nothing ever dims. The
reveal, the typing masks and the carets are all fail-safe — a renderer that
ignores CSS animation shows the finished session, never a blank window.

today.py fills in the placeholders on every run: the stat numbers, the
contribution calendar, and the commit log rows.
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
        "sheen_opacity": "0.75",
        "git_node": "#febc2e",
        "git_hash": "#c678dd",
        "git_msg": "#cecece",
        "cava_top": "#7ebae4",
        "cava_bottom": "#2b5d8f",
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
        "sheen_opacity": "0.6",
        "git_node": "#b58900",
        "git_hash": "#d33682",
        "git_msg": "#073642",
        "cava_top": "#268bd2",
        "cava_bottom": "#7aa9d6",
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

# Advance widths of the monospace face, measured against the rendered SVG.
CHAR_W = 9.6
PANE_CHAR_W = 6.6
PROMPT_LEN = len("yuuki@nixos:~$ ")

PANE_X = 292
ASCII_X = 15
ASCII_FONT_SIZE = 10
ASCII_LINE_H = 12
ASCII_Y_START = 80
PANE_TEXT_X = 15
PANE_FONT_SIZE = 11
TTY_X = 300

GITLOG_HEADER_Y = 348
GITLOG_Y_START = 374
GITLOG_LINE_H = 18
GITLOG_ROWS = 9
GITLOG_MSG_COLS = 30  # fits "* <hash> " + message inside the left pane

CAVA_HEADER_Y = 582
CAVA_BARS = 24
CAVA_BAR_W = 7
CAVA_BAR_GAP = 4
CAVA_X = 18
CAVA_BASELINE = 706
CAVA_HEIGHT = 88
CAVA_WAVES = 6

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
HEAT_WAVE_STEP_S = 0.025  # per-column delay of the calendar wipe

# Session replay timing (seconds). The loop opens on the finished session, holds
# it, clears, replays it, then holds again — so frame 0 is always the full
# window and nothing ever dims.
HOLD_BEFORE_S = 10.0
HOLD_AFTER_S = 6.0
LOOP_S = 22.0  # recomputed from the session span in build_svg()
TYPE_CHAR_S = 0.035
PRINT_ROW_S = 0.08
PRINT_LOGO_S = 0.03
PRINT_GITLOG_S = 0.07
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

    def keyframes(self, name: str, seconds: float) -> str:
        clear_at = HOLD_BEFORE_S / LOOP_S * 100
        print_at = (HOLD_BEFORE_S + seconds) / LOOP_S * 100
        lit_at = min(print_at + 0.3, 99.8)
        return (
            f"@keyframes {name} {{\n"
            f"  0%, {clear_at:.2f}% {{ opacity: 1; }}\n"
            f"  {clear_at + 0.01:.2f}%, {print_at:.2f}% {{ opacity: 0; }}\n"
            f"  {lit_at:.2f}%, 100% {{ opacity: 1; }}\n"
            f"}}\n"
            f".{name} {{ animation: {name} {LOOP_S}s linear infinite; }}"
        )

    def css(self) -> str:
        blocks = [".reveal {opacity: 1;}"]
        blocks += [self.keyframes(name, seconds) for seconds, name in self.classes.items()]
        return "\n".join(blocks)


REVEAL = Reveal()
# (mask index, row y, command, seconds the command starts typing, in left pane)
TYPED: list[tuple[int, int, str, float, bool]] = []


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def typing_css() -> str:
    """Masks that uncover each command one character at a time, plus the caret
    that travels with it.

    Both default to hidden/uncovered so a renderer without CSS animation shows
    the command in full instead of a blank bar.
    """
    blocks = [
        ".type-mask {transform: scaleX(0); transform-origin: right center; transform-box: fill-box;}",
        ".caret {opacity: 0;}",
    ]
    for index, (_, _, command, cue, left_pane) in enumerate(TYPED):
        duration = len(command) * TYPE_CHAR_S
        steps = max(1, len(command))
        travel = steps * (PANE_CHAR_W if left_pane else CHAR_W)
        clear_pct = HOLD_BEFORE_S / LOOP_S * 100
        start_pct = (HOLD_BEFORE_S + cue) / LOOP_S * 100
        end_pct = min((HOLD_BEFORE_S + cue + duration) / LOOP_S * 100, 99.7)
        blocks.append(
            f"@keyframes type-{index} {{\n"
            f"  0%, {clear_pct:.2f}% {{ transform: scaleX(0); }}\n"
            f"  {clear_pct + 0.01:.2f}%, {start_pct:.2f}% {{ transform: scaleX(1); animation-timing-function: steps({steps}, end); }}\n"
            f"  {end_pct:.2f}%, 100% {{ transform: scaleX(0); }}\n"
            f"}}\n"
            f".type-{index} {{ animation: type-{index} {LOOP_S}s linear infinite; }}"
        )
        blocks.append(
            f"@keyframes caret-{index} {{\n"
            f"  0%, {start_pct:.2f}% {{ opacity: 0; transform: translateX(0); animation-timing-function: steps({steps}, end); }}\n"
            f"  {start_pct + 0.01:.2f}% {{ opacity: 1; transform: translateX(0); animation-timing-function: steps({steps}, end); }}\n"
            f"  {end_pct:.2f}% {{ opacity: 1; transform: translateX({travel:.1f}px); }}\n"
            f"  {min(end_pct + 0.01, 99.8):.2f}%, 100% {{ opacity: 0; transform: translateX({travel:.1f}px); }}\n"
            f"}}\n"
            f".caret-{index} {{ animation: caret-{index} {LOOP_S}s linear infinite; }}"
        )
    return "\n".join(blocks)


def cava_css() -> str:
    """Equalizer bars: a handful of wave shapes, each bar on its own clock."""
    waves = [
        ("0.18", "0.95", "0.35", "1.00", "0.42"),
        ("0.60", "0.25", "0.90", "0.30", "0.75"),
        ("0.35", "0.70", "0.20", "0.85", "0.30"),
        ("0.90", "0.40", "0.65", "0.22", "0.95"),
        ("0.25", "0.55", "1.00", "0.45", "0.20"),
        ("0.72", "0.30", "0.48", "0.92", "0.38"),
    ]
    blocks = [".cava-bar {transform-origin: bottom; transform-box: fill-box;}"]
    for index, steps in enumerate(waves):
        stops = "\n".join(
            f"  {pct}% {{ transform: scaleY({value}); }}"
            for pct, value in zip((0, 25, 50, 75, 100), steps)
        )
        blocks.append(f"@keyframes cava-{index} {{\n{stops}\n}}")
    for bar in range(CAVA_BARS):
        wave = bar % CAVA_WAVES
        duration = 0.9 + (bar * 7 % 9) / 10
        delay = -((bar * 13 % 17) / 10)
        blocks.append(
            f".cava-{bar} {{ animation: cava-{wave} {duration:.1f}s ease-in-out {delay:.1f}s infinite; }}"
        )
    return "\n".join(blocks)


def heatwave_css() -> str:
    """Per-column cues so the calendar wipes in left to right."""
    base = HEAT_CUE[0]
    return "\n".join(
        REVEAL.keyframes(f"hw{week}", base + week * HEAT_WAVE_STEP_S)
        for week in range(HEAT_WEEKS)
    )


def animation_styles() -> str:
    return f"""
{REVEAL.css()}
{typing_css()}
{cava_css()}
{heatwave_css()}
@keyframes cursor-blink {{
  0%, 45% {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}
.cursor {{ animation: cursor-blink 1.05s step-end infinite; }}
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
        self.pane: list[str] = []
        self.cues: dict[str, float] = {}

    def _tspan(self, x: int, y: int, content: str, seconds: float, element_id: str = "") -> str:
        ident = f' id="{element_id}"' if element_id else ""
        return f'<tspan{ident} x="{x}" y="{y}" class="reveal {REVEAL.at(seconds)}">{content}</tspan>'

    def beat(self, seconds: float = BEAT_S) -> None:
        self.clock += seconds

    def mark(self, name: str) -> None:
        self.cues[name] = self.clock

    def output(self, y: int, content: str, step: float = PRINT_ROW_S) -> None:
        self.tty.append(self._tspan(TTY_X, y, content, self.clock))
        self.clock += step

    def command(self, y: int, text: str, left_pane: bool = False) -> None:
        """Prompt appears, then the command types itself in."""
        target = self.pane if left_pane else self.tty
        x = PANE_TEXT_X if left_pane else TTY_X
        target.append(self._tspan(x, y, prompt(text), self.clock))
        TYPED.append((len(TYPED), y, text, self.clock, left_pane))
        self.clock += len(text) * TYPE_CHAR_S + 0.15

    def logo_pane(self) -> None:
        for index, segments in enumerate(ASCII_LOGO):
            y = ASCII_Y_START + index * ASCII_LINE_H
            parts = "".join(
                f'<tspan class="logo-{tone}">{esc(text)}</tspan>' for text, tone in segments
            )
            self.logo.append(self._tspan(ASCII_X, y, parts, self.clock))
            self.clock += PRINT_LOGO_S
        self.mark("logo_done")

    def gitlog_pane(self) -> None:
        """Placeholder commit rows — today.py rewrites their contents."""
        self.command(GITLOG_HEADER_Y, "git log --graph", left_pane=True)
        for index in range(GITLOG_ROWS):
            y = GITLOG_Y_START + index * GITLOG_LINE_H
            body = (
                f'<tspan class="git-node">*</tspan>'
                f'<tspan class="dim"> </tspan>'
                f'<tspan class="git-hash">0000000</tspan>'
                f'<tspan class="dim"> </tspan>'
                f'<tspan class="git-msg">waiting for today.py</tspan>'
            )
            self.pane.append(
                self._tspan(PANE_TEXT_X, y, body, self.clock, element_id=f"gitlog_{index}")
            )
            self.clock += PRINT_GITLOG_S


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
    pane_start = session.clock
    session.gitlog_pane()
    session.command(CAVA_HEADER_Y, "cava", left_pane=True)
    session.mark("cava")
    session.clock = max(pane_start + 0.4, session.clock - 1.2)

    session.command(496, "git shortlog -sn --all | head -1")
    session.output(516, stat_line("commit_data", "  commits authored by YuukiFST", "   "))
    session.beat()

    session.command(546, "cloc --vcs=git ~/github/*")
    session.output(566, loc_line())
    session.beat()

    session.command(596, "gh api graphql -f query=contributionCalendar")
    session.mark("heatmap")
    session.clock += HEAT_WEEKS * HEAT_WAVE_STEP_S
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


def cava_block(theme: dict, session: Session) -> str:
    """Equalizer bars — the one element that keeps moving between replays."""
    bars = "".join(
        f'<rect class="cava-bar cava-{bar}" '
        f'x="{CAVA_X + bar * (CAVA_BAR_W + CAVA_BAR_GAP)}" y="{CAVA_BASELINE - CAVA_HEIGHT}" '
        f'width="{CAVA_BAR_W}" height="{CAVA_HEIGHT}" rx="2" fill="url(#cava-gradient)"/>'
        for bar in range(CAVA_BARS)
    )
    return f'<g class="reveal {REVEAL.at(session.cues["cava"])}">{bars}</g>'


def heatmap_placeholder(theme: dict) -> str:
    """Empty calendar grid + month labels; today.py replaces both with real data.

    Each week is its own group so the calendar wipes in column by column.
    """
    cue = REVEAL.at(HEAT_CUE[0])
    columns = "".join(
        f'<g class="reveal hw{week}">'
        + "".join(
            f'<rect class="lvl0" x="{week * HEAT_PITCH}" y="{day * HEAT_PITCH}" '
            f'width="{HEAT_CELL}" height="{HEAT_CELL}" rx="2"/>'
            for day in range(7)
        )
        + "</g>"
        for week in range(HEAT_WEEKS)
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
<g id="heatmap" transform="translate({HEAT_X},{HEAT_Y})">{columns}</g>
<g class="reveal {cue}">
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X}" y="{HEAT_LEGEND_Y}">Less</text>
{legend_cells}
<text class="dim" font-size="11px" fill="{theme["dim"]}" x="{HEAT_X + 44 + 5 * HEAT_PITCH + 6}" y="{HEAT_LEGEND_Y}">More</text>
</g>'''


def typing_overlays(theme: dict) -> str:
    """Masks + carets, painted after the text so they sit on top of it."""
    parts = []
    for index, (_, y, command, _, left_pane) in enumerate(TYPED):
        char_w = PANE_CHAR_W if left_pane else CHAR_W
        x = (PANE_TEXT_X if left_pane else TTY_X) + PROMPT_LEN * char_w
        height = 14 if left_pane else 19
        parts.append(
            f'<rect class="type-mask type-{index}" x="{x:.1f}" y="{y - height + 3}" '
            f'width="{len(command) * char_w + 2:.1f}" height="{height}" fill="{theme["bg"]}"/>'
        )
        parts.append(
            f'<rect class="caret caret-{index}" x="{x:.1f}" y="{y - height + 3}" '
            f'width="{char_w:.1f}" height="{height}" fill="{theme["cursor"]}"/>'
        )
    return "\n".join(parts)


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
<text x="{left_w + 20}" y="{text_y}" font-size="13" fill="{theme["statusbar_alt_text"]}">0:cava*   1:session-   │   ~/github/YuukiFST</text>
<text x="{SVG_WIDTH - 20}" y="{text_y}" text-anchor="end" font-size="13" fill="{theme["statusbar_alt_text"]}">main ✓   │   nixos-unstable   │   ★ reproducible</text>'''


def pane_divider(theme: dict) -> str:
    return (
        f'<line x1="{PANE_X}" y1="{TITLEBAR_H}" x2="{PANE_X}" y2="{STATUSBAR_Y}" '
        f'stroke="{theme["pane_border"]}" stroke-width="1"/>'
    )


def logo_sheen(theme: dict, session: Session) -> str:
    """A highlight sweeping across the finished snowflake every few seconds.

    Same glyphs as the logo, filled with a moving gradient, so the sheen only
    paints where the block characters already are.
    """
    rows = []
    for index, segments in enumerate(ASCII_LOGO):
        y = ASCII_Y_START + index * ASCII_LINE_H
        line = "".join(esc(text) for text, _ in segments)
        rows.append(f'<tspan x="{ASCII_X}" y="{y}">{line}</tspan>')
    return f'''<text class="reveal {REVEAL.at(session.cues["logo_done"])}" font-size="{ASCII_FONT_SIZE}px" fill="url(#sheen)">
{"".join(rows)}
</text>'''


def build_svg(theme_name: str) -> str:
    global REVEAL, TYPED, LOOP_S, HEAT_CUE
    REVEAL = Reveal()
    TYPED = []
    HEAT_CUE = [0.0]

    theme = THEMES[theme_name]
    session = build_session()
    LOOP_S = HOLD_BEFORE_S + session.clock + HOLD_AFTER_S
    HEAT_CUE[0] = session.cues["heatmap"]
    sheen_end = ASCII_X + 46 * PANE_CHAR_W
    heat_span = HEAT_WEEKS * HEAT_PITCH
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
.git-node {{fill: {theme["git_node"]};}}
.git-hash {{fill: {theme["git_hash"]};}}
.git-msg {{fill: {theme["git_msg"]};}}
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
<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="{ASCII_X - 220}" y1="{ASCII_Y_START}" x2="{ASCII_X - 60}" y2="{ASCII_Y_START + 120}">
<stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
<stop offset="50%" stop-color="#ffffff" stop-opacity="{theme["sheen_opacity"]}"/>
<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
<animate attributeName="x1" values="{ASCII_X - 220};{sheen_end:.0f}" dur="7s" repeatCount="indefinite"/>
<animate attributeName="x2" values="{ASCII_X - 60};{sheen_end + 160:.0f}" dur="7s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="cava-gradient" gradientUnits="userSpaceOnUse" x1="0" y1="{CAVA_BASELINE}" x2="0" y2="{CAVA_BASELINE - CAVA_HEIGHT}">
<stop offset="0%" stop-color="{theme["cava_bottom"]}"/>
<stop offset="100%" stop-color="{theme["cava_top"]}"/>
</linearGradient>
</defs>
<rect width="{SVG_WIDTH}px" height="{SVG_HEIGHT}px" fill="{theme["bg"]}" rx="12"/>
{titlebar(theme)}
{statusbar(theme)}
{pane_divider(theme)}
<rect x="1" y="1" width="983px" height="{SVG_HEIGHT - 2}px" fill="none" stroke="{theme["border"]}" stroke-width="2" rx="12"/>
<text x="15" y="30" fill="{theme["logo_1"]}" class="ascii" font-size="{ASCII_FONT_SIZE}px" filter="url(#phosphor)">
{"".join(chr(10) + row for row in session.logo)}
</text>
{logo_sheen(theme, session)}
<text x="{PANE_TEXT_X}" y="30" fill="{theme["fg"]}" font-size="{PANE_FONT_SIZE}px">
{"".join(chr(10) + row for row in session.pane)}
</text>
<text x="{TTY_X}" y="30" fill="{theme["fg"]}">
{"".join(chr(10) + row for row in session.tty)}
</text>
{palette_block(theme, session)}
{cava_block(theme, session)}
{heatmap_placeholder(theme)}
{typing_overlays(theme)}
</svg>'''


HEAT_CUE = [0.0]


def main() -> None:
    for theme_name in THEMES:
        path = ROOT / THEMES[theme_name]["file"]
        path.write_text(build_svg(theme_name), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
