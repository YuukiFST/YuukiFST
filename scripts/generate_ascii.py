#!/usr/bin/env python3
"""Generate ASCII art for profile SVGs from assets/profile.jpg.

Preferred tool (best quality):
  ascii-image-converter  https://github.com/TheZoraiz/ascii-image-converter
  ascii-image-converter assets/profile.jpg -d 38,22 -m ' .:;+=*#%@'

Fallback: pip install ascii-magic pillow
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHOTO = ROOT / "assets" / "profile.jpg"
WIDTH, HEIGHT = 38, 22
CHAR_MAP = " .:;+=*#%@"


def run_converter() -> list[str] | None:
    binary = shutil.which("ascii-image-converter")
    if not binary:
        return None
    result = subprocess.run(
        [binary, str(PHOTO), "-d", f"{WIDTH},{HEIGHT}", "-m", CHAR_MAP],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [line.rstrip() for line in result.stdout.splitlines() if line.strip()]
    return lines[:HEIGHT] if lines else None


def run_ascii_magic() -> list[str]:
    try:
        from ascii_magic import AsciiArt
    except ImportError as exc:
        raise SystemExit(
            "Install ascii-image-converter or: pip install ascii-magic pillow"
        ) from exc

    art = AsciiArt.from_image(str(PHOTO))
    lines = [line.rstrip() for line in art.to_ascii(columns=WIDTH).splitlines() if line.strip()]
    while len(lines) < HEIGHT:
        lines.append("")
    return lines[:HEIGHT]


def ascii_to_svg_tsps(lines: list[str], y_start: int = 30, x: int = 15) -> str:
    rows = []
    for index, line in enumerate(lines):
        y = y_start + index * 20
        safe = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        rows.append(f'<tspan x="{x}" y="{y}">{safe}</tspan>')
    return "\n".join(rows)


def patch_svg(path: Path, ascii_block: str) -> None:
    content = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<text x="15" y="30" fill="[^"]*" class="ascii">\n)(.*?)(\n</text>)',
        re.DOTALL,
    )
    if not pattern.search(content):
        raise SystemExit(f"Could not find ASCII block in {path}")
    updated = pattern.sub(rf"\1{ascii_block}\3", content, count=1)
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    if not PHOTO.exists():
        raise SystemExit(f"Missing photo: {PHOTO}")

    lines = run_converter() or run_ascii_magic()
    block = ascii_to_svg_tsps(lines)
    for name in ("dark_mode.svg", "light_mode.svg"):
        patch_svg(ROOT / name, block)
    print(f"Updated ASCII art in dark_mode.svg and light_mode.svg ({len(lines)} lines)")


if __name__ == "__main__":
    main()
