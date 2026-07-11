#!/usr/bin/env bash
# Delega para my-harness-config (fonte canonica dos hooks).
set -euo pipefail

for candidate in \
  "${MY_HARNESS_CONFIG:-}" \
  "$HOME/Projects/my-harness-config" \
  "$HOME/Developer/my-harness-config" \
  "$HOME/repos/my-harness-config" \
  "$HOME/my-harness-config"; do
  if [[ -n "$candidate" && -x "$candidate/scripts/install-git-hooks.sh" ]]; then
    exec "$candidate/scripts/install-git-hooks.sh" "$@"
  fi
done

echo "ERRO: clone my-harness-config e defina MY_HARNESS_CONFIG ou use um caminho padrao." >&2
exit 1
