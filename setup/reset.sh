#!/usr/bin/env bash
# Borra lo generado por setup. Uso: ./reset.sh [--full]
#   sin --full: venvs, worktrees, examples y logs (conserva el clon)
#   con --full: ademas beancount-src y .tools
# Solo actua sobre estas rutas fijas junto al script. No toca locks ni scripts.
set -eu
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

targets=(.venv-323 .venv-236 beancount-src/v3.2.3 beancount-src/v2.3.6 examples logs)
if [ "${1:-}" = "--full" ]; then
    targets+=(beancount-src .tools)
fi

for name in "${targets[@]}"; do
    if [ -e "$here/$name" ]; then
        rm -rf "${here:?}/$name"
        echo "Borrado: $name"
    fi
done

if [ -d "$here/beancount-src/.git" ] && command -v git >/dev/null 2>&1; then
    git -C "$here/beancount-src" worktree prune
fi
echo "Reset terminado."
