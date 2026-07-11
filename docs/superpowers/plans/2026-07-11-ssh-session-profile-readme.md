# SSH Session Profile README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace neofetch-clone SVG profile with SSH terminal session layout + Arch ASCII logo, keeping dynamic stats via `today.py`.

**Architecture:** `scripts/build_svg_template.py` generates `dark_mode.svg` and `light_mode.svg` with static TTY shell + dynamic element ids. `today.py` patches ids via existing `svg_overwrite()`. README.md unchanged.

**Tech Stack:** Python 3.11, lxml, requests, SVG, GitHub GraphQL

## Global Constraints

- No photo ASCII art (v1)
- No stars/followers in stats section
- Editor field: Doom Emacs only
- Palettes: doom-one dark (`#1a1a2e` bg), Solarized light (`#fdf6e3` bg)
- Dynamic ids: `age_data`, `repo_data`, `contrib_data`, `commit_data`, `loc_data`, `loc_add`, `loc_del` (+ `*_dots` siblings)
- Reuse `today.py` cache LOC pipeline unchanged

---

### Task 1: SVG template generator

**Files:**
- Create: `scripts/build_svg_template.py`
- Modify: `dark_mode.svg`, `light_mode.svg` (generated output)

**Interfaces:**
- Produces: valid SVG files with Arch ASCII left column + SSH session right column
- Consumes: none

- [ ] Create generator with Arch logo constant (~22 lines × 38 cols)
- [ ] Emit doom-one dark + Solarized light palettes per spec
- [ ] Wire all dynamic `id` attributes for `today.py`
- [ ] Run: `python scripts/build_svg_template.py`

### Task 2: Verify today.py compatibility

**Files:**
- Modify: `today.py` (only if justify lengths need tuning)

- [ ] Run: `ACCESS_TOKEN=$(gh auth token) USER_NAME=YuukiFST python today.py`
- [ ] Confirm commits, repos, LOC non-zero in both SVGs

### Task 3: Ship

**Files:**
- Commit: SVGs, cache, generator script

- [ ] `git push origin main`
- [ ] Visual check on github.com/YuukiFST
