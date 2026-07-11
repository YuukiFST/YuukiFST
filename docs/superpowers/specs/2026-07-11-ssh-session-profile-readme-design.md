# Design: SSH Session Profile README

**Date:** 2026-07-11  
**Repo:** YuukiFST/YuukiFST  
**Status:** Approved (brainstorming)  
**Author:** Agent + Fausto Yuuki

## Summary

Replace the current neofetch-clone profile README with a single SVG that renders a **recorded SSH terminal session** on host `yuuki@github`. The left column shows a hand-crafted **Arch Linux ASCII logo** (no photo). The right column shows a **command history** where each shell command reveals a section of the profile. Dynamic GitHub stats appear as realistic command output (`git shortlog`, `cloc`, `ls ~/repos | wc -l`).

## Goals

- Feel like a Linux developer who lives in the terminal
- Match Andrew6rant-level creativity (SVG engineering, not generic markdown badges)
- Reuse existing `today.py` + cache + GitHub Actions infrastructure
- No photo ASCII art (v1)
- No stars/followers (per prior user request)
- Doom Emacs as editor identity (field, not full Emacs UI)

## Non-Goals

- Animated SVG or typing effects
- Photo-to-ASCII pipeline (deferred; `scripts/generate_ascii.py` stays but unused in v1)
- skillicons.dev or badge rows
- Bilingual PT/EN toggle
- Emacs org-mode buffer layout (rejected in favor of shell narrative)

## User Context

| Field | Value |
|---|---|
| GitHub | YuukiFST |
| Role | Back-End Developer |
| OS | Arch Linux, Windows (WSL 2) |
| Editor | Doom Emacs |
| Host | São Benedito, IFMT |
| Stack | Python, Go, TypeScript, Java, PostgreSQL |
| Focus | Data, Backend, AI Agents |
| Portfolio | fausto-yuuki.vercel.app |
| LinkedIn | fausto-yuuki |

## Visual Concept

```
┌─ yuuki@github ─────────────────────────────────────────────────┐
│ Last login: <dynamic date> from 127.0.0.1                      │
│                                                                │
│  [Arch ASCII logo]     (left column, ~22 lines)                │
│                                                                │
│ yuuki@github:~$ fastfetch --logo arch                          │
│ yuuki@github  ─────────────────────────────                    │
│  OS ····· Arch Linux, WSL 2                                    │
│  Host ·· São Benedito / IFMT                                   │
│  Shell · zsh                                                   │
│  Editor  Doom Emacs                                              │
│  Stack · Python, Go, PostgreSQL, TypeScript                    │
│  Focus · Backend, Data, AI Agents                              │
│                                                                │
│ yuuki@github:~$ cat ~/links                                    │
│  portfolio  → fausto-yuuki.vercel.app                          │
│  linkedin   → fausto-yuuki                                     │
│                                                                │
│ yuuki@github:~$ git shortlog -sn --all | head -1               │
│   <commits>  YuukiFST                          [DYNAMIC]       │
│                                                                │
│ yuuki@github:~$ cloc --sum-reports .                           │
│  <loc_total> lines | +<loc_add> / -<loc_del>   [DYNAMIC]       │
│                                                                │
│ yuuki@github:~$ ls ~/repos | wc -l                             │
│  <repos> repos (<contrib> contributed)         [DYNAMIC]       │
│                                                                │
│ yuuki@github:~$ █                                              │
└────────────────────────────────────────────────────────────────┘
```

## Color Palette

### Dark mode (`dark_mode.svg`) — doom-one inspired

| Role | Hex | Usage |
|---|---|---|
| Background | `#1a1a2e` | Terminal window fill |
| Window border | `#3d3d5c` | Rounded rect stroke (optional) |
| Prompt user@host | `#51afef` | `yuuki@github` |
| Prompt path | `#98be65` | `~$` |
| Command text | `#bbc2cf` | Typed commands |
| Output keys | `#ff6c6b` | Field labels in fastfetch block |
| Output values | `#a9a1e1` | Field values |
| MOTD / dim | `#5b6268` | `Last login` line |
| LOC additions | `#98be65` | `++` count |
| LOC deletions | `#ff6c6b` | `--` count |
| Cursor | `#a9a1e1` | Block cursor `█` |

### Light mode (`light_mode.svg`) — Solarized light TTY

| Role | Hex |
|---|---|
| Background | `#fdf6e3` |
| Prompt | `#268bd2` |
| Command | `#657b83` |
| Keys | `#cb4b16` |
| Values | `#073642` |
| Cursor | `#6c71c4` |

## ASCII Art (Left Column)

- **v1:** Hand-crafted Arch Linux logo ASCII (~38 cols × 22 rows)
- Source: classic Arch ASCII templates, tuned for monospace 16px in SVG
- **Not** generated from photo
- Future: swap art block without changing layout (same bounding box)

## Static vs Dynamic Content

### Static (baked into SVG template)

- Arch ASCII art block
- All prompt lines and command strings
- fastfetch field labels and static values (OS, Host, Shell, Editor, Stack, Focus)
- `cat ~/links` output (portfolio, linkedin)
- Section structure and dot-padding for alignment

### Dynamic (updated by `today.py`)

| SVG element `id` | Fake command context | Data source |
|---|---|---|
| `age_data` | `Last login` / uptime line | GitHub account `createdAt` via `daily_readme()` |
| `repo_data` | `ls ~/repos \| wc -l` count | GraphQL repos OWNER |
| `contrib_data` | contributed count in parens | GraphQL repos OWNER+COLLABORATOR+ORG |
| `commit_data` | `git shortlog -sn` number | `commit_counter()` from cache |
| `loc_data` | `cloc` total lines | cache_builder net LOC |
| `loc_add` | `cloc` additions | cache_builder |
| `loc_del` | `cloc` deletions | cache_builder |
| `*_dots` siblings | dot-padding for alignment | `justify_format()` |

### Removed from v1

- `star_data`, `follower_data` (already removed from `today.py`)

## Architecture

```
README.md
  └── <picture> embeds dark_mode.svg / light_mode.svg

dark_mode.svg / light_mode.svg
  └── Single <svg> with two <text> blocks:
        - left:  ASCII art (static)
        - right: TTY session (static shell + dynamic ids)

today.py
  └── GitHub GraphQL → svg_overwrite() patches ids in both SVGs

cache/<sha256>.txt
  └── Per-repo LOC/commit cache (unchanged format)

.github/workflows/build.yaml
  └── Daily cron + push; needs ACCESS_TOKEN + USER_NAME secrets
```

## File Changes

| File | Action |
|---|---|
| `dark_mode.svg` | Rewrite layout: SSH session + Arch logo |
| `light_mode.svg` | Same structure, light palette |
| `today.py` | Update `svg_overwrite()` ids if renamed; no star/follower calls |
| `README.md` | Unchanged (`<picture>` embed) |
| `cache/` | Keep; commit cache after first local run |
| `scripts/generate_ascii.py` | Keep; out of scope v1 |
| `assets/profile.jpg` | Keep; out of scope v1 |
| `.github/workflows/build.yaml` | User adds via GitHub UI (OAuth workflow scope) |

## `today.py` Interface

`svg_overwrite(filename, age_data, commit_data, repo_data, contrib_data, loc_data)` — already matches v1 needs.

Optional addition: format `age_data` as `X years, Y months on GitHub` for MOTD line instead of neofetch "Uptime" label.

## Error Handling

| Failure | Behavior |
|---|---|
| Missing `ACCESS_TOKEN` | Workflow fails; SVG keeps last committed values |
| GraphQL rate limit | `today.py` raises; partial cache saved via `force_close_file()` |
| Cache/repo count mismatch | `flush_cache()` rebuilds |
| SVG id missing | `find_and_replace` no-ops; log in CI |

## Testing

1. **Local:** `ACCESS_TOKEN=$(gh auth token) USER_NAME=YuukiFST python today.py` — verify all ids update, no XML errors
2. **Visual:** Open SVG in browser; check dark + light `prefers-color-scheme`
3. **GitHub:** Push; confirm README renders image on profile page
4. **Regression:** Confirm commits > 0, LOC > 0 after cache warm (not zeros)

## Implementation Phases

1. Draft Arch ASCII art + SVG shell layout (static)
2. Wire dynamic ids into new layout
3. Run `today.py` locally; commit SVG + cache
4. Push; verify GitHub profile render
5. Document secrets setup for daily cron (README or `docs/setup.md`)

## Open Decisions (Resolved)

| Question | Decision |
|---|---|
| Photo ASCII? | No (v1) |
| Visual identity? | SSH session on `yuuki@github` |
| Left art? | Arch Linux logo ASCII |
| Editor? | Doom Emacs (fastfetch field) |
| Stats? | repos, contributed, commits, LOC +/- |
| Stars/followers? | Excluded |

## Success Criteria

- [ ] Profile README reads as a terminal session, not a neofetch form
- [ ] Arch ASCII visible without photo
- [ ] Dynamic stats show real non-zero values after `today.py` run
- [ ] Dark/light modes both polished
- [ ] `today.py` + cache still work without rewrite
