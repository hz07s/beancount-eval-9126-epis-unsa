#!/usr/bin/env python3
"""Genera el grafo de dependencias entre paquetes desde inventario/modulos.csv.

Requiere haber ejecutado antes generar_inventario.py. Excluye los módulos de prueba.
Escribe diagramas/dependencias_modulos.mmd e inventario/dependencias_paquetes.csv.
Opcional: si Graphviz (`dot`) está en el PATH, exporta además un PNG.
"""

import csv
import shutil
import subprocess
from collections import Counter
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent


def paquete(modulo: str) -> str:
    partes = modulo.split(".")
    return partes[1] if len(partes) > 1 and partes[1] in PAQUETES else "raiz"


PAQUETES = {"core", "ops", "parser", "plugins", "projects", "scripts", "tools", "utils"}


def main() -> None:
    with (DOCS / "inventario/modulos.csv").open(encoding="utf-8-sig", newline="") as entrada:
        filas = [f for f in csv.DictReader(entrada) if f["es_test"] == "no"]
    aristas: Counter = Counter()
    for fila in filas:
        origen = paquete(fila["modulo"])
        for destino in filter(None, fila["imports_internos"].split(";")):
            final = paquete(destino)
            if final != origen:
                aristas[(origen, final)] += 1

    etiquetas = {p: p for p in sorted(PAQUETES)} | {"raiz": "beancount (loader, api)"}
    lineas = [
        "%% Generado por scripts/generar_dependencias.py. No editar a mano.",
        "%% Etiqueta de cada flecha: número de imports entre módulos que no son de prueba.",
        "graph LR",
    ]
    lineas += [f'    {p}["{e}"]' for p, e in etiquetas.items()]
    lineas += [f"    {a} -->|{n}| {b}" for (a, b), n in sorted(aristas.items())]
    (DOCS / "diagramas/dependencias_modulos.mmd").write_text("\n".join(lineas) + "\n", encoding="utf-8")

    with (DOCS / "inventario/dependencias_paquetes.csv").open("w", newline="", encoding="utf-8-sig") as salida:
        escritor = csv.writer(salida)
        escritor.writerow(["origen", "destino", "imports"])
        for (a, b), n in sorted(aristas.items()):
            escritor.writerow([a, b, n])

    if shutil.which("dot"):
        fuente = "digraph G {\n" + "\n".join(f'"{a}" -> "{b}" [label={n}];' for (a, b), n in aristas.items()) + "\n}"
        subprocess.run(
            ["dot", "-Tpng", "-o", str(DOCS / "diagramas/dependencias_modulos.png")],
            input=fuente.encode(), check=True,
        )
    else:
        print("Graphviz no está instalado: solo se genera el .mmd")
    for (a, b), n in sorted(aristas.items()):
        print(f"{a} -> {b}: {n}")


if __name__ == "__main__":
    main()
