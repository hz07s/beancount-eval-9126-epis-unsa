#!/usr/bin/env bash
# Monta el entorno completo. Uso: ./setup.sh [argumentos de bootstrap.py]
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
    echo "Falta Git. macOS: xcode-select --install | Debian/Ubuntu: sudo apt install git" >&2
    exit 1
fi

for candidate in python3.12 python3.11 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
        exec "$candidate" "$here/bootstrap.py" "$@"
    fi
done

echo "Falta Python >= 3.11. macOS: brew install python@3.12 | Debian/Ubuntu: sudo apt install python3.12 python3.12-venv" >&2
exit 1
