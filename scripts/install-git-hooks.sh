#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
HOOKS_SRC="$ROOT/.githooks"
HOOKS_DST="$ROOT/.git/hooks"

for hook in commit-msg prepare-commit-msg forbidden-patterns.sh; do
  install -m 755 "$HOOKS_SRC/$hook" "$HOOKS_DST/$hook" 2>/dev/null || {
    cp "$HOOKS_SRC/$hook" "$HOOKS_DST/$hook"
    chmod 755 "$HOOKS_DST/$hook"
  }
  echo "ok $hook"
done
