# Entorno reproducible de Beancount 3.2.3 y 2.3.6

Entorno local para evaluar Beancount (NTP-ISO/IEC 9126): las dos versiones en
paralelo, cada una en su worktree y su venv. No requiere administrador y no
instala nada fuera de esta carpeta.

## Requisitos

| Requisito | Windows 11 | Linux / macOS |
|---|---|---|
| Git | `winget install -e --id Git.Git --scope user` | `sudo apt install git` / `xcode-select --install` |
| Python >= 3.11 para lanzar el script | `winget install -e --id Python.Python.3.12 --scope user` | `sudo apt install python3.12 python3.12-venv` / `brew install python@3.12` |
| Python 3.11 o 3.12 para los venvs | Si no hay, se descarga 3.12.10 portable en `.tools/` | Debe estar instalado |
| Compilador (opcional) | No necesario | Opcional: `gcc`, `m4` y cabeceras de Python para `-e` real |

Los venvs usan 3.11 o 3.12 porque los wheels oficiales de 2.3.6 terminan en
CPython 3.12. Beancount 3.2.3 admite >= 3.9, de modo que 3.12 es el punto común.

## Instalación

**Windows 11** (PowerShell 5.1 o 7+; también vale doble clic en `setup.bat`):

```powershell
git clone <URL-de-este-proyecto> trabajo   # o copia la carpeta
cd trabajo
.\setup.ps1
```

**Linux / macOS:**

```bash
git clone <URL-de-este-proyecto> trabajo   # o copia la carpeta
cd trabajo
./setup.sh
```

El script clona, crea worktrees y venvs, instala y ejecuta `verify.py`. En Windows
tardó 70-92 s con buena conexión; repetirlo con todo listo tarda unos 6 s.

## Uso

```powershell
.\run.ps1 -Version 3.2.3 -Command "bean-check archivo.beancount"
.\run.ps1 -Version 2.3.6 -Command "bean-query archivo.beancount 'SELECT account, sum(position) GROUP BY account'"
```

```bat
run.bat 3.2.3 bean-check archivo.beancount
```

```bash
./run.sh 3.2.3 bean-check archivo.beancount
```

El comando se ejecuta en la carpeta actual y `run.*` devuelve su código de salida.

Para verificar: `python verify.py` (con cualquier Python >= 3.11). La salida
completa queda en `logs/verify-<version>.log`.

### Activar un venv a mano

```powershell
.\.venv-323\Scripts\Activate.ps1    # PowerShell
.venv-323\Scripts\activate.bat      # cmd
```

```bash
source .venv-323/bin/activate
```

## Versiones y rutas

| Versión | Tag en git | Commit | Worktree | Venv |
|---|---|---|---|---|
| 3.2.3 | `3.2.3` | `eeda2aa2a3` | `beancount-src/v3.2.3` | `.venv-323` |
| 2.3.6 | `2.3.6` | `d77540c4b8` | `beancount-src/v2.3.6` | `.venv-236` |

Los tags oficiales no llevan prefijo `v`; solo las carpetas lo usan.

Comandos: 3.2.3 trae `bean-check`, `bean-doctor`, `bean-example`, `bean-format` y
`treeify`; `bean-query` procede del paquete aparte `beanquery` 0.2.0. Esto cambia
la superficie funcional comparada: `bean-report`, `bean-web`, `bean-price`,
`bean-extract`, `bean-file`, `bean-identify`, `bean-sql` y `bean-bake` solo están en 2.3.6.

## Modos de instalación

`verify.py` muestra el modo de cada versión. `bootstrap.py --mode` permite forzarlo.

| Modo | Cuándo | Código Python | Parser C |
|---|---|---|---|
| `editable` | Hay compilador: `pip install -e .` real | Worktree | Compilado desde el worktree |
| `overlay` | No hay compilador, o `-e` falló | Worktree (vía `.pth`) | Binario del wheel oficial del mismo tag |

**Limitación de `overlay`:** las ediciones en `.py` se aplican al momento, pero
las de `lexer.l`, `grammar.y` o `*.c` no se recompilan. Beancount avisará con
"out-of-date" y `verify.py` lo marcará FALLO. Para compilar en Windows hacen falta
MSVC y el SDK (Visual Studio Build Tools con "Desarrollo para el escritorio con
C++", requiere administrador); después ejecuta `reset.ps1` y `setup.ps1`.

**Hash del parser en Windows:** los wheels de Windows se compilaron con fuentes
CRLF, y por eso su hash difiere del de las fuentes LF de git aunque el código sea
el mismo. `bootstrap.py` comprueba esa equivalencia (si no se cumple, falla) y
silencia únicamente ese par exacto de hashes; cualquier edición reactiva el aviso.

**Worktree:** `overlay` deja `_parser*.pyd` o `_parser*.so` como archivo sin
seguimiento en el worktree. Los archivos versionados siguen idénticos al tag.

## Línea base de la suite completa

```powershell
cd beancount-src\v2.3.6
..\..\run.ps1 -Version 2.3.6 -Command "python -m pytest -q beancount -p no:cacheprovider"
```

Resultados medidos el 2026-11-01 con Python 3.12:

| Plataforma | Modo | 3.2.3 | 2.3.6 |
|---|---|---|---|
| Windows 11 | overlay | 1094 pasan, 0 fallan, 23 omitidos | 1550-1552 pasan, 161-163 fallan, 3 errores, 28 omitidos |
| Linux (Docker `python:3.12`) | editable | 1096 pasan, 0 fallan, 21 omitidos | 1707 pasan, 10 fallan, 24 omitidos |
| Linux (WSL Ubuntu 26.04, sin compilador) | overlay | 1096 pasan, 0 fallan, 21 omitidos | 1706 pasan, 11 fallan, 24 omitidos |

Los fallos de 2.3.6 fueron distintos entre dos ejecuciones en Windows (163 y 161),
así que conviene repetir antes de citar una cifra exacta. De 164 casos con fallo o
error en la ejecución clasificada, 154 no fallan en Linux y 10 sí. El tipo más
frecuente es `PermissionError` (90).

`verify.py` no ejecuta la suite completa. En Windows excluye, de forma explícita y
anunciada, dos tests de `parser_test.py` en 2.3.6 (`KNOWN_WINDOWS_FAILURES`).

## Reset

```powershell
.\reset.ps1         # venvs, worktrees, examples, logs
.\reset.ps1 -Full   # además beancount-src y .tools
```

```bash
./reset.sh          # igual
./reset.sh --full
```

## Reproducibilidad

- Tags fijos; clon con `core.autocrlf=false` para conservar los bytes del repositorio.
- Dependencias fijadas en `locks/constraints-*.txt`, generados en Windows. Los
  paquetes exclusivos de otra plataforma (p. ej. `python-magic`) quedan sin fijar.
  Se regeneran con `python bootstrap.py --update-locks`.
- `bean-example` usa semilla y fechas fijas.
- `PYTHONUTF8=1` en `run.*` y `verify.py`, pero no en un venv activado a mano.
- Python portable verificado con SHA-256.

## Problemas frecuentes

**Política de ejecución.** Si PowerShell bloquea los scripts:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Si los scripts llegaron en un ZIP descargado, además: `Get-ChildItem *.ps1 | Unblock-File`.
`setup.bat` no cambia la política: usa `-ExecutionPolicy Bypass` solo para esa ejecución.

**Rutas largas en Windows.** El repositorio ya usa `core.longpaths` localmente. Si
trabajas con rutas muy profundas, conviene activarlo también de forma global:

```powershell
git config --global core.longpaths true
```

**El clon falla por la red.** Clon superficial, y vuelve a ejecutar el setup (traerá
el otro tag por su cuenta):

```bash
git clone --no-checkout --depth 1 --branch 3.2.3 -c core.autocrlf=false https://github.com/beancount/beancount.git beancount-src
```

**Se movió la carpeta del proyecto.** Los venvs guardan rutas absolutas: ejecuta
`reset` y `setup` de nuevo.

**`pip install -e` falla en Linux.** Suele faltar `m4` o las cabeceras de Python
(`sudo apt install build-essential m4 python3.12-dev`). El setup continúa en
`overlay` y lo indica con un aviso; `--mode editable` hace que falle en su lugar.
