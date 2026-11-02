#!/usr/bin/env python3
"""Enlaza las citas de código de los .md y comprueba la integridad de la carpeta.

Convierte citas entre comillas invertidas en enlaces relativos (es idempotente):
    `beancount/loader.py:89`         -> worktree v3.2.3
    `v2.3.6:beancount/loader.py:89`  -> worktree v2.3.6

Comprueba: archivos esperados, enlaces relativos, citas (archivo y línea existentes),
que cada .md numerado cite código, cobertura de modulos.csv y sintaxis básica de Mermaid.
Devuelve código 1 si encuentra algún problema.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote

DOCS = Path(__file__).resolve().parent.parent
RAIZ = DOCS.parent
WT = {"v3.2.3": RAIZ / "beancount-src/v3.2.3", "v2.3.6": RAIZ / "beancount-src/v2.3.6"}
BASES = ("beancount/", "bin/", "tools/", "examples/", "experiments/", "docs/", ".github/")
RAICES = ("pyproject.toml", "setup.py", "meson.build", "Makefile", "CHANGES", "README.rst")

CITA = re.compile(
    r"(?<!\[)`(?:(v2\.3\.6|v3\.2\.3):)?((?:(?:" + "|".join(map(re.escape, BASES)) + r")[\w./\-]*\.?[\w\-]*|"
    + "|".join(map(re.escape, RAICES)) + r"))(?::(\d+)(?:-(\d+))?)?`(?!\])"
)
ENLACE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")

ESPERADOS = """README.md 00_resumen_ejecutivo.md 01_vision_general.md 02_arquitectura.md
03_mapa_de_modulos.md 04_modelo_de_datos_y_sintaxis.md 05_flujo_de_ejecucion.md 06_herramientas_cli.md
07_plugins_y_extensiones.md 08_pruebas_y_calidad_interna.md 09_comparacion_2_3_6_vs_3_2_3.md 10_glosario.md
11_notas_para_evaluacion_9126.md 12_referencias.md LEEME_generacion.md
diagramas/arquitectura.mmd diagramas/flujo_parseo.mmd diagramas/flujo_booking.mmd diagramas/dependencias_modulos.mmd
inventario/modulos.csv inventario/entry_points.csv inventario/directivas_soportadas.csv
scripts/generar_inventario.py scripts/generar_dependencias.py""".split()
SIN_CITA_OBLIGATORIA = {"12_referencias.md", "LEEME_generacion.md", "README.md"}


def enlazar(texto: str, problemas: list[str], nombre: str) -> str:
    def sustituir(m: re.Match) -> str:
        version = m.group(1) or "v3.2.3"
        ruta, linea = m.group(2), m.group(3)
        destino = WT[version] / ruta
        etiqueta = m.group(0)
        if not destino.exists():
            problemas.append(f"{nombre}: cita a archivo inexistente {etiqueta}")
            return etiqueta
        if linea:
            total = len(destino.read_text(encoding="utf-8", errors="replace").splitlines())
            ultima = int(m.group(4) or linea)
            if ultima > total:
                problemas.append(f"{nombre}: {etiqueta} supera las {total} líneas del archivo")
        relativo = f"../beancount-src/{version}/{ruta}"
        ancla = f"#L{linea}" if linea else ""
        return f"[{etiqueta}]({relativo}{ancla})"

    # No tocar bloques de código.
    trozos = re.split(r"(```.*?```)", texto, flags=re.S)
    return "".join(t if t.startswith("```") else CITA.sub(sustituir, t) for t in trozos)


def verificar_mermaid(ruta: Path, problemas: list[str]) -> None:
    texto = ruta.read_text(encoding="utf-8")
    cuerpo = [l for l in texto.splitlines() if l.strip() and not l.strip().startswith("%%")]
    if not cuerpo or not re.match(r"(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram)", cuerpo[0]):
        problemas.append(f"{ruta.name}: cabecera Mermaid no reconocida")
    for pareja in ("[]", "()", "{}"):
        if texto.count(pareja[0]) != texto.count(pareja[1]):
            problemas.append(f"{ruta.name}: {pareja} desbalanceados")
    if texto.count('"') % 2:
        problemas.append(f"{ruta.name}: comillas desbalanceadas")


def main() -> int:
    problemas: list[str] = []
    for esperado in ESPERADOS:
        if not (DOCS / esperado).exists():
            problemas.append(f"Falta {esperado}")

    citas = enlaces = 0
    for md in sorted(DOCS.glob("*.md")):
        original = md.read_text(encoding="utf-8")
        texto = enlazar(original, problemas, md.name)
        if texto != original:
            md.write_text(texto, encoding="utf-8")
        for destino in ENLACE.findall(texto):
            if destino.startswith(("http://", "https://", "mailto:", "#")):
                continue
            enlaces += 1
            ruta = (DOCS / unquote(destino.split("#")[0])).resolve()
            if not ruta.exists():
                problemas.append(f"{md.name}: enlace roto {destino}")
        propias = len(re.findall(r"\.\./beancount-src/", texto))
        citas += propias
        if propias == 0 and md.name not in SIN_CITA_OBLIGATORIA:
            problemas.append(f"{md.name}: no cita ninguna ruta de código")

    # Cobertura del inventario frente al disco.
    repo = WT["v3.2.3"]
    disco = {
        p.relative_to(repo).as_posix()
        for p in (repo / "beancount").rglob("*.py") if "__pycache__" not in p.parts
    }
    with (DOCS / "inventario/modulos.csv").open(encoding="utf-8-sig", newline="") as entrada:
        inventario = {f["ruta"] for f in csv.DictReader(entrada)}
    if disco != inventario:
        problemas.append(f"modulos.csv no cubre el disco: faltan {sorted(disco - inventario)[:5]}, sobran {sorted(inventario - disco)[:5]}")

    for mmd in sorted((DOCS / "diagramas").glob("*.mmd")):
        verificar_mermaid(mmd, problemas)

    print(f"Enlaces relativos comprobados: {enlaces}; enlaces a código: {citas}; módulos en inventario: {len(inventario)}/{len(disco)}")
    for problema in problemas:
        print("PROBLEMA:", problema)
    print("RESULTADO:", "con problemas" if problemas else "correcto")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
