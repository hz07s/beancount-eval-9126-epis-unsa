#!/usr/bin/env bash
# Ejecuta un comando dentro del venv de una version.
# Ejemplo: ./run.sh 3.2.3 bean-check archivo.beancount
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ "$#" -lt 2 ]; then
    echo "Uso: $0 {3.2.3|2.3.6} comando [argumentos...]" >&2
    exit 2
fi
case "$1" in
    3.2.3) venv="$here/.venv-323" ;;
    2.3.6) venv="$here/.venv-236" ;;
    *) echo "Version no valida: $1 (usa 3.2.3 o 2.3.6)" >&2; exit 2 ;;
esac
shift

# bin/ en Linux y macOS; Scripts/ si se usa desde Git Bash en Windows.
if [ -d "$venv/bin" ]; then bindir="$venv/bin"; else bindir="$venv/Scripts"; fi
if [ ! -d "$bindir" ]; then
    echo "No existe $venv. Ejecuta primero ./setup.sh" >&2
    exit 1
fi

export VIRTUAL_ENV="$venv" PATH="$bindir:$PATH" PYTHONUTF8=1
exec "$@"
