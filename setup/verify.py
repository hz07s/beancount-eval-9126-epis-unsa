#!/usr/bin/env python3
"""Verifica ambos entornos de Beancount y muestra una tabla OK/FALLO. Solo stdlib.

Sale con codigo 0 solo si todas las comprobaciones de todas las versiones pasan.
La salida completa de cada comando queda en logs/verify-<version>.log.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from bootstrap import LOGS, ROOT, STATE_FILE, VERSIONS, child_env, venv_bin, venv_python

EXAMPLES = ROOT / "examples"
TIMEOUT_SECONDS = 300
PYTEST_SUBSET = [
    "beancount/core/amount_test.py",
    "beancount/core/inventory_test.py",
    "beancount/parser/lexer_test.py",  # ejercitan la extension C
    "beancount/parser/parser_test.py",
]
QUERY = "SELECT account, sum(position) GROUP BY account ORDER BY account"
# Defectos de portabilidad de Beancount en Windows, ajenos al entorno: se excluyen
# para que este chequeo mida el entorno, y se anuncian en cada ejecucion.
KNOWN_WINDOWS_FAILURES = {
    "2.3.6": [
        "beancount/parser/parser_test.py::TestParserInputs::test_parse_file",
        "beancount/parser/parser_test.py::TestParserInputs::test_parse_filename",
    ],
}
# Si reaparece, el parser C no corresponde a las fuentes y la medicion no es valida.
STALE_PARSER = "out-of-date"


def execute(version, cmd, log, cwd=None):
    """Devuelve (returncode, salida combinada); un timeout cuenta como fallo."""
    if cmd[0] == "python":
        cmd = [str(venv_python(version)), *cmd[1:]]
    else:
        cmd = [str(venv_bin(version) / cmd[0]), *cmd[1:]]
    try:
        proc = subprocess.run(
            cmd, cwd=cwd or version.venv, env=child_env(version), stdin=subprocess.DEVNULL,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS,
        )
        code, output = proc.returncode, proc.stdout + proc.stderr
    except FileNotFoundError:
        code, output = 127, f"no existe: {cmd[0]}"
    except subprocess.TimeoutExpired:
        code, output = 124, f"timeout tras {TIMEOUT_SECONDS}s"
    log.write(f"\n$ {' '.join(cmd)}\n(rc={code})\n{output}\n")
    if STALE_PARSER in output:
        return 1, output
    return code, output


def known_failures(version):
    return KNOWN_WINDOWS_FAILURES.get(version.number, []) if os.name == "nt" else []


def verify_version(version):
    """Devuelve la lista ordenada de (comprobacion, ok) de una version."""
    LOGS.mkdir(exist_ok=True)
    EXAMPLES.mkdir(exist_ok=True)
    ledger = EXAMPLES / f"ejemplo-{version.number}.beancount"
    results = []

    with open(LOGS / f"verify-{version.number}.log", "w", encoding="utf-8") as log:
        def simple(label, cmd, must_contain=None, cwd=None):
            code, output = execute(version, cmd, log, cwd)
            ok = code == 0 and (must_contain is None or must_contain in output)
            results.append((label, ok))
            return ok

        where = (
            "import beancount, beancount.parser._parser; "
            "print(beancount.__version__, beancount.__file__)"
        )
        code, output = execute(version, ["python", "-c", where], log)
        parts = output.split(maxsplit=1)
        in_worktree = (
            code == 0 and len(parts) == 2 and parts[0] == version.number
            and Path(parts[1].strip()).resolve().is_relative_to(version.worktree.resolve())
        )
        results.append(("import desde su worktree", in_worktree))

        simple("bean-check --version", ["bean-check", "--version"], must_contain=version.number)
        simple("bean-check --help", ["bean-check", "--help"])
        simple("bean-doctor --help", ["bean-doctor", "--help"])

        # Fechas y semilla fijas: el mismo libro hoy y dentro de un ano.
        ledger.unlink(missing_ok=True)
        generated = simple(
            "bean-example (genera libro)",
            ["bean-example", "--date-begin", "2023-01-01", "--date-end", "2025-01-01",
             "--seed", "42", "-o", str(ledger)],
        ) and ledger.exists() and ledger.stat().st_size > 0
        if generated:
            simple("bean-check libro", ["bean-check", str(ledger)])
            simple("bean-query SELECT", ["bean-query", str(ledger), QUERY], must_contain="Assets:")
        else:
            results.append(("bean-check libro", False))
            results.append(("bean-query SELECT", False))

        deselect = [arg for test in known_failures(version) for arg in ("--deselect", test)]
        simple("pytest -q (subconjunto)",
               ["python", "-m", "pytest", "-q", *PYTEST_SUBSET, *deselect],
               cwd=version.worktree)
    return results


def installed_mode(version):
    try:
        return json.loads((version.venv / STATE_FILE).read_text("utf-8"))["mode"]
    except (OSError, ValueError, KeyError):
        return "?"


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    all_results = {version.number: dict(verify_version(version)) for version in VERSIONS}
    labels = list(next(iter(all_results.values())))
    numbers = [version.number for version in VERSIONS]

    width = max(len(label) for label in labels)
    print(f"\n{'Comprobacion':<{width}}  " + "  ".join(f"{n:<8}" for n in numbers))
    print("-" * width + "  " + "  ".join("-" * 8 for _ in numbers))
    for label in labels:
        cells = ("OK" if all_results[n][label] else "FALLO" for n in numbers)
        print(f"{label:<{width}}  " + "  ".join(f"{cell:<8}" for cell in cells))
    print(f"{'modo de instalacion':<{width}}  "
          + "  ".join(f"{installed_mode(v):<8}" for v in VERSIONS))

    for version in VERSIONS:
        for test in known_failures(version):
            print(f"NOTA: {version.number} excluye fallo conocido de Windows: {test}")

    passed = all(all(row.values()) for row in all_results.values())
    print("\nRESULTADO: " + ("TODO OK" if passed else "HAY FALLOS (ver logs/verify-*.log)"))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
