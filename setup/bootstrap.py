#!/usr/bin/env python3
"""Monta el entorno de evaluacion de Beancount (3.2.3 y 2.3.6). Solo stdlib.

Uso:  python bootstrap.py [--mode auto|editable|overlay] [--python RUTA]
                          [--no-verify] [--update-locks]

Es idempotente: lo que ya esta correcto se reutiliza y lo que no coincide con
lo esperado se reporta como FALLO sin sobrescribirlo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tomllib
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "beancount-src"
LOGS = ROOT / "logs"
LOCKS = ROOT / "locks"
TOOLS = ROOT / ".tools"
REPO_URL = "https://github.com/beancount/beancount.git"

# Los wheels oficiales de 2.3.6 llegan solo hasta CPython 3.12; por eso es el
# unico rango en el que ambas versiones comparten interprete sin compilar.
SUPPORTED_PYTHONS = [(3, 12), (3, 11)]

PORTABLE_PYTHON_URL = "https://www.nuget.org/api/v2/package/python/3.12.10"
PORTABLE_PYTHON_SHA256 = "0eb85c2dfccccf1b17352de4c397f69194035b7d37149eacc16f1147d93de3b8"
PORTABLE_PYTHON_EXE = TOOLS / "python312" / "tools" / "python.exe"

STATE_FILE = "beancount-setup.json"


@dataclass(frozen=True)
class Version:
    number: str
    tag: str
    extra_packages: tuple[str, ...]

    @property
    def worktree(self) -> Path:
        return SRC / f"v{self.number}"

    @property
    def venv(self) -> Path:
        return ROOT / (".venv-" + self.number.replace(".", ""))

    @property
    def lock(self) -> Path:
        return LOCKS / f"constraints-{self.number}.txt"


VERSIONS = [
    # En 3.x, bean-query vive en el paquete aparte "beanquery".
    Version("3.2.3", "3.2.3", ("pytest", "beanquery")),
    Version("2.3.6", "2.3.6", ("pytest",)),
]


class StepError(Exception):
    """Fallo esperado de un paso, con un mensaje accionable para el usuario."""


def venv_bin(version: Version) -> Path:
    return version.venv / ("Scripts" if os.name == "nt" else "bin")


def venv_python(version: Version) -> Path:
    return venv_bin(version) / ("python.exe" if os.name == "nt" else "python")


def child_env(version: Version | None = None) -> dict[str, str]:
    env = dict(os.environ, PYTHONUTF8="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    if version is not None:
        env["VIRTUAL_ENV"] = str(version.venv)
        env["PATH"] = str(venv_bin(version)) + os.pathsep + env.get("PATH", "")
    return env


def run(cmd, version=None, cwd=None, log=None, check=True):
    """Ejecuta cmd; si falla (o hay log) guarda la salida y da un error util."""
    cmd = [str(c) for c in cmd]
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=child_env(version),
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = proc.stdout + proc.stderr
    if log:
        LOGS.mkdir(exist_ok=True)
        with open(LOGS / log, "a", encoding="utf-8") as handle:
            handle.write(f"\n$ {' '.join(cmd)}\n{output}\n")
    if check and proc.returncode != 0:
        tail = "\n".join(output.strip().splitlines()[-15:])
        where = f" (ver logs/{log})" if log else ""
        raise StepError(f"Fallo: {' '.join(cmd)}{where}\n{tail}")
    return proc


class Report:
    def __init__(self):
        self.rows = []

    def step(self, name, func, *args):
        """Ejecuta un paso, registra PASS/FAIL y devuelve (ok, resultado)."""
        try:
            result = func(*args)
        except StepError as exc:
            self.rows.append((name, "FAIL"))
            print(f"[FAIL] {name}\n       {exc}")
            return False, None
        self.rows.append((name, "PASS"))
        detail = f" -> {result}" if isinstance(result, str) else ""
        print(f"[PASS] {name}{detail}")
        return True, result

    @property
    def failed(self):
        return any(status == "FAIL" for _, status in self.rows)

    def show(self):
        print("\nResumen de bootstrap")
        width = max(len(name) for name, _ in self.rows)
        for name, status in self.rows:
            print(f"  {name:<{width}}  {status}")


def install_hint(tool):
    system = platform.system()
    if tool == "git":
        return {
            "Windows": "winget install -e --id Git.Git --scope user",
            "Darwin": "xcode-select --install   (o: brew install git)",
        }.get(system, "sudo apt install git   (o el equivalente de tu distribucion)")
    return {
        "Windows": "winget install -e --id Python.Python.3.12 --scope user",
        "Darwin": "brew install python@3.12",
    }.get(system, "sudo apt install python3.12 python3.12-venv   (o: uv python install 3.12)")


def check_host_python():
    if sys.version_info < (3, 11):
        raise StepError(
            f"bootstrap.py requiere Python >= 3.11 (este es {platform.python_version()}). "
            f"Instalalo con: {install_hint('python')}"
        )
    return platform.python_version()


def check_git():
    if not shutil.which("git"):
        raise StepError(f"Git no esta instalado. Instalalo con: {install_hint('git')}")
    return run(["git", "--version"]).stdout.strip()


def probe_python(cmd):
    """Devuelve la ruta real del interprete si cmd es un Python soportado."""
    code = "import sys; print(sys.version_info[0], sys.version_info[1], sys.executable)"
    try:
        proc = subprocess.run(
            [*cmd, "-c", code], capture_output=True, text=True, timeout=30,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    major, minor, exe = proc.stdout.strip().split(maxsplit=2)
    return exe if (int(major), int(minor)) in SUPPORTED_PYTHONS else None


def download_portable_python():
    """Python 3.12 oficial (paquete NuGet) en .tools/, sin admin ni registro."""
    target = TOOLS / "python312"
    package = TOOLS / "python-3.12.10.nupkg"
    TOOLS.mkdir(exist_ok=True)
    print(f"       Descargando Python 3.12.10 portable en {target} ...")
    try:
        with urllib.request.urlopen(PORTABLE_PYTHON_URL, timeout=120) as response:
            package.write_bytes(response.read())
    except OSError as exc:
        raise StepError(
            f"No se pudo descargar Python portable ({exc}). "
            f"Alternativa: {install_hint('python')}"
        ) from exc
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    if digest != PORTABLE_PYTHON_SHA256:
        package.unlink()
        raise StepError(f"SHA-256 inesperado en el Python descargado: {digest}")
    shutil.rmtree(target, ignore_errors=True)
    with zipfile.ZipFile(package) as archive:
        archive.extractall(target)
    package.unlink()


def find_python(explicit):
    if explicit:
        exe = probe_python([explicit])
        if not exe:
            wanted = " o ".join(f"{a}.{b}" for a, b in SUPPORTED_PYTHONS)
            raise StepError(f"--python {explicit} no es un Python {wanted} ejecutable.")
        return exe
    candidates = [[str(PORTABLE_PYTHON_EXE)]]
    for major, minor in SUPPORTED_PYTHONS:
        if os.name == "nt":
            candidates.append(["py", f"-{major}.{minor}"])
        candidates.append([f"python{major}.{minor}"])
    candidates += [[sys.executable], ["python3"], ["python"]]
    for cmd in candidates:
        exe = probe_python(cmd)
        if exe:
            return exe
    if os.name == "nt" and platform.machine().lower() in ("amd64", "x86_64"):
        download_portable_python()
        exe = probe_python([str(PORTABLE_PYTHON_EXE)])
        if exe:
            return exe
    raise StepError(
        "Hace falta Python 3.11 o 3.12 (los wheels de Beancount 2.3.6 terminan en "
        f"CPython 3.12). Instalalo con: {install_hint('python')}"
    )


def git_src(*args, check=True):
    return run(["git", "-C", SRC, *args], check=check)


def ensure_clone():
    if SRC.exists():
        inside = git_src("rev-parse", "--git-dir", check=False)
        origin = git_src("remote", "get-url", "origin", check=False).stdout.strip()
        if inside.returncode != 0 or origin.removesuffix(".git") != REPO_URL.removesuffix(".git"):
            raise StepError(
                f"{SRC} existe pero no es un clon de {REPO_URL} (origin={origin!r}). "
                "No se toca; muevelo o renombralo."
            )
        status = f"reutilizado {SRC.name}"
    else:
        # autocrlf=false: conservar LF. El hash de fuentes del parser y varios
        # tests dependen de los bytes exactos del repositorio.
        proc = run(
            ["git", "clone", "--no-checkout", "-c", "core.autocrlf=false",
             "-c", "core.longpaths=true", REPO_URL, SRC],
            log="bootstrap-git.log", check=False,
        )
        if proc.returncode != 0:
            shutil.rmtree(SRC, ignore_errors=True)
            raise StepError(
                f"No se pudo clonar {REPO_URL}.\n{proc.stderr.strip()}\n"
                "Si la red falla con el clon completo, prueba un clon superficial "
                f"y vuelve a ejecutar:\n  git clone --no-checkout --depth 1 --branch 3.2.3 "
                f"-c core.autocrlf=false {REPO_URL} {SRC.name}"
            )
        status = f"clonado en {SRC.name}"
    git_src("config", "core.autocrlf", "false")
    git_src("config", "core.longpaths", "true")
    return status


def tag_commit(tag):
    proc = git_src("rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}", check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def ensure_worktree(version):
    commit = tag_commit(version.tag)
    if not commit:
        git_src("fetch", "origin", f"refs/tags/{version.tag}:refs/tags/{version.tag}", check=False)
        commit = tag_commit(version.tag)
    if not commit:
        tags = git_src("tag", "-l").stdout.split()
        close = [t for t in tags if version.number[:3] in t]
        raise StepError(f"No existe el tag {version.tag}. Tags parecidos: {close}")
    worktree = version.worktree
    if worktree.exists():
        head = run(["git", "-C", worktree, "rev-parse", "HEAD"], check=False).stdout.strip()
        if head != commit:
            raise StepError(
                f"{worktree} no esta en el tag {version.tag} (HEAD={head or '?'}). "
                "No se toca; usa reset.ps1 / reset.sh si quieres recrearlo."
            )
        return f"reutilizado, commit {commit[:10]}"
    git_src("worktree", "prune")
    git_src("worktree", "add", "--detach", worktree, version.tag)
    return f"creado, commit {commit[:10]}"


def ensure_venv(version, base_python):
    python = venv_python(version)
    if python.exists() and probe_python([str(python)]):
        return f"reutilizado {version.venv.name}"
    if version.venv.exists():
        raise StepError(
            f"{version.venv.name} existe pero no es un venv con Python soportado. "
            "Borralo con reset.ps1 / reset.sh."
        )
    proc = run([base_python, "-m", "venv", version.venv], check=False)
    if proc.returncode != 0:
        shutil.rmtree(version.venv, ignore_errors=True)
        raise StepError(
            f"No se pudo crear el venv: {proc.stdout}{proc.stderr}\n"
            "En Debian/Ubuntu suele faltar: sudo apt install python3.12-venv"
        )
    return f"creado {version.venv.name}"


def install_probe(version):
    """True si el beancount importable es el del worktree, con parser C y version."""
    code = (
        "import beancount, beancount.parser._parser; "
        "print(beancount.__version__); print(beancount.__file__)"
    )
    # cwd neutro: desde la raiz del worktree importar siempre encontraria el codigo.
    proc = run([venv_python(version), "-c", code], version, cwd=version.venv, check=False)
    lines = proc.stdout.strip().splitlines()
    if proc.returncode != 0 or len(lines) != 2 or lines[0] != version.number:
        return False
    return Path(lines[1]).resolve().is_relative_to(version.worktree.resolve())


def has_compiler():
    if os.name != "nt":
        return any(shutil.which(c) for c in ("cc", "gcc", "clang"))
    if shutil.which("cl"):
        return True
    program_files = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    vswhere = Path(program_files) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    if not vswhere.exists():
        return False
    proc = run(
        [vswhere, "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        check=False,
    )
    return bool(proc.stdout.strip())


def constraint_args(version):
    return ["-c", version.lock] if version.lock.exists() else []


def pip(version, *args):
    run(
        [venv_python(version), "-m", "pip", "install", *constraint_args(version), *args],
        version, log=f"bootstrap-{version.number}.log",
    )


def install_editable(version):
    """pip install -e . real; compila la extension C desde el worktree."""
    pyproject = version.worktree / "pyproject.toml"
    if pyproject.exists():
        # meson-python recompila al importar: necesita sus dependencias de
        # compilacion dentro del venv y, por tanto, --no-build-isolation.
        requires = tomllib.loads(pyproject.read_text("utf-8"))["build-system"]["requires"]
        pip(version, "ninja", *requires)
        pip(version, *version.extra_packages, "--no-build-isolation", "-e", version.worktree)
    else:
        pip(version, *version.extra_packages, "-e", version.worktree)


def install_overlay(version):
    """Sin compilador: wheel oficial del mismo tag, redirigido al worktree.

    Queda el mismo resultado practico que un editable para el codigo Python:
    los comandos bean-* y los imports usan el worktree. La extension _parser es
    el binario oficial, asi que cambios en .c/.l/.y NO se recompilan.
    """
    wheel = f"beancount=={version.number}"
    pip(version, "--only-binary=beancount", wheel, *version.extra_packages)
    pip(version, "--only-binary=beancount", "--force-reinstall", "--no-deps", wheel)
    code = "import sysconfig; print(sysconfig.get_path('platlib'))"
    site = Path(run([venv_python(version), "-c", code], version).stdout.strip())
    installed = site / "beancount"
    binaries = list((installed / "parser").glob("_parser*"))
    if not binaries:
        raise StepError(f"El wheel de {version.number} no trae la extension _parser.")
    for binary in binaries:
        shutil.copy2(binary, version.worktree / "beancount" / "parser" / binary.name)
    shutil.rmtree(installed)
    pth = site / "beancount_worktree.pth"
    pth.write_text(str(version.worktree) + "\n", "utf-8")
    silence = parser_hash_filter(version)
    if silence:
        with open(pth, "a", encoding="utf-8") as handle:
            handle.write(silence + "\n")


def parser_hash_filter(version):
    """Comprueba que _parser procede de este tag; devuelve la linea .pth necesaria.

    Los wheels de Windows se compilaron con fuentes CRLF, asi que su SOURCE_HASH
    difiere del de las fuentes LF de git aunque el codigo sea el mismo, y
    beancount avisa de "out-of-date" en cada comando. Se silencia solo ese par
    exacto de hashes: si alguien edita el parser, el aviso reaparece.
    """
    code = (
        "import hashlib, pathlib\n"
        "import beancount.parser._parser as p\n"
        "from beancount.parser import hashsrc\n"
        "root = pathlib.Path(hashsrc.__file__).parent\n"
        "lf, crlf = hashlib.md5(), hashlib.md5()\n"
        "for name in hashsrc.PARSER_SOURCE_FILES:\n"
        "    data = (root / name).read_bytes()\n"
        "    lf.update(data)\n"
        "    crlf.update(data.replace(b'\\n', b'\\r\\n'))\n"
        "print(p.SOURCE_HASH, lf.hexdigest(), crlf.hexdigest())\n"
    )
    proc = run([venv_python(version), "-W", "ignore", "-c", code], version, cwd=version.venv)
    binary, lf_hash, crlf_hash = proc.stdout.split()
    if binary == lf_hash:
        return None
    if binary != crlf_hash:
        raise StepError(
            f"El parser binario de {version.number} no corresponde a las fuentes del tag "
            f"(binario {binary}, LF {lf_hash}, CRLF {crlf_hash})."
        )
    pattern = rf"The Beancount parser C extension module is out-of-date \('{binary}' != '{lf_hash}'\)"
    return f'import warnings; warnings.filterwarnings("ignore", message=r"{pattern}")'


def ensure_installed(version, mode):
    state_path = version.venv / STATE_FILE
    if install_probe(version) and state_path.exists():
        return "ya instalado, modo " + json.loads(state_path.read_text("utf-8"))["mode"]

    chosen = mode
    note = ""
    if mode == "auto":
        chosen = "editable" if has_compiler() else "overlay"
    if chosen == "editable":
        try:
            install_editable(version)
        except StepError as exc:
            if mode == "editable":
                raise
            note = " (pip install -e fallo; ver logs)"
            chosen = "overlay"
            print(f"       AVISO: {str(exc).splitlines()[0]}")
    if chosen == "overlay":
        install_overlay(version)
    if not install_probe(version):
        raise StepError(f"Tras instalar, beancount {version.number} no carga desde su worktree.")
    state = {
        "version": version.number,
        "mode": chosen,
        "commit": run(["git", "-C", version.worktree, "rev-parse", "HEAD"]).stdout.strip(),
    }
    state_path.write_text(json.dumps(state, indent=2) + "\n", "utf-8")
    return f"modo {chosen}{note}"


def update_lock(version):
    frozen = run([venv_python(version), "-m", "pip", "freeze"], version).stdout.splitlines()
    pins = [
        line for line in frozen
        if line and not line.startswith(("-e", "#")) and not line.startswith("beancount")
    ]
    LOCKS.mkdir(exist_ok=True)
    version.lock.write_text("\n".join(sorted(pins, key=str.lower)) + "\n", "utf-8", newline="\n")
    return f"{len(pins)} paquetes fijados en {version.lock.relative_to(ROOT)}"


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=["auto", "editable", "overlay"], default="auto",
                        help="auto: -e real si hay compilador; si no, wheel oficial + worktree")
    parser.add_argument("--python", help="interprete 3.11/3.12 base para los venvs")
    parser.add_argument("--no-verify", action="store_true", help="no ejecutar verify.py al final")
    parser.add_argument("--update-locks", action="store_true",
                        help="regenerar locks/constraints-*.txt desde los venvs")
    args = parser.parse_args()

    report = Report()
    ok, _ = report.step("Python anfitrion >= 3.11", check_host_python)
    if not ok:
        report.show()
        return 1
    ok_git, _ = report.step("Git", check_git)
    ok_py, base_python = report.step("Python 3.11/3.12 para venvs", find_python, args.python)
    if not (ok_git and ok_py):
        report.show()
        return 1
    ok, _ = report.step("Clon de beancount", ensure_clone)
    if not ok:
        report.show()
        return 1

    for version in VERSIONS:
        tag = version.number
        ok, _ = report.step(f"{tag}: worktree", ensure_worktree, version)
        ok = ok and report.step(f"{tag}: venv", ensure_venv, version, base_python)[0]
        ok = ok and report.step(f"{tag}: instalacion", ensure_installed, version, args.mode)[0]
        if ok and args.update_locks:
            report.step(f"{tag}: lock", update_lock, version)
    report.show()

    if report.failed:
        return 1
    if args.no_verify:
        return 0
    return subprocess.run([sys.executable, str(ROOT / "verify.py")], env=child_env()).returncode


if __name__ == "__main__":
    sys.exit(main())
