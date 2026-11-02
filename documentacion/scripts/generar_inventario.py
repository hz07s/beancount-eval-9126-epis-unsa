#!/usr/bin/env python3
"""Genera el inventario de Beancount a partir del código real (solo biblioteca estándar).

No importa ni ejecuta Beancount: analiza los fuentes con `ast` y expresiones regulares.

Uso (desde cualquier carpeta):
    python documentacion/scripts/generar_inventario.py

Salidas en documentacion/inventario/:
    modulos.csv, modulos_2.3.6.csv, entry_points.csv, directivas_soportadas.csv,
    pruebas_por_paquete.csv, pruebas_omitidas.csv, modulos_sin_test.csv,
    comparacion_modulos.csv, comparacion_cli.csv, comparacion_directivas.csv,
    comparacion_api.csv, resumen.json
Además rellena en 03_mapa_de_modulos.md la tabla situada entre sus marcadores.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import re
import warnings
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

warnings.simplefilter("ignore", SyntaxWarning)

DOCS = Path(__file__).resolve().parent.parent
RAIZ = DOCS.parent
MARCA_INI = "<!-- INICIO_TABLA_MODULOS -->"
MARCA_FIN = "<!-- FIN_TABLA_MODULOS -->"

# Una directiva del lenguaje -> (palabra clave, token, regla de grammar.y, método del
# Builder, clase de core/data.py). Se verifica contra los fuentes más abajo.
DIRECTIVAS = [
    ("transaction", "txn o una bandera (*, !, ...)", "TXN", "transaction", "transaction", "Transaction"),
    ("open", "open", "OPEN", "open", "open", "Open"),
    ("close", "close", "CLOSE", "close", "close", "Close"),
    ("commodity", "commodity", "COMMODITY", "commodity", "commodity", "Commodity"),
    ("pad", "pad", "PAD", "pad", "pad", "Pad"),
    ("balance", "balance", "BALANCE", "balance", "balance", "Balance"),
    ("note", "note", "NOTE", "note", "note", "Note"),
    ("event", "event", "EVENT", "event", "event", "Event"),
    ("query", "query", "QUERY", "query", "query", "Query"),
    ("price", "price", "PRICE", "price", "price", "Price"),
    ("document", "document", "DOCUMENT", "document", "document", "Document"),
    ("custom", "custom", "CUSTOM", "custom", "custom", "Custom"),
    ("option", "option", "OPTION", "option", "option", ""),
    ("include", "include", "INCLUDE", "include", "include", ""),
    ("plugin", "plugin", "PLUGIN", "plugin", "plugin", ""),
    ("pushtag", "pushtag", "PUSHTAG", "pushtag", "pushtag", ""),
    ("poptag", "poptag", "POPTAG", "poptag", "poptag", ""),
    ("pushmeta", "pushmeta", "PUSHMETA", "pushmeta", "pushmeta", ""),
    ("popmeta", "popmeta", "POPMETA", "popmeta", "popmeta", ""),
]


def leer(ruta: Path) -> str:
    return ruta.read_text(encoding="utf-8", errors="replace")


def nombre_modulo(rel: Path) -> str:
    partes = list(rel.with_suffix("").parts)
    if partes[-1] == "__init__":
        partes.pop()
    return ".".join(partes)


def resolver_import(nodo: ast.ImportFrom, modulo: str, es_paquete: bool) -> str:
    """Devuelve el nombre absoluto base de un `from ... import`."""
    if not nodo.level:
        return nodo.module or ""
    base = modulo.split(".")
    corte = nodo.level - 1 if es_paquete else nodo.level
    base = base[: len(base) - corte]
    return ".".join(base + ([nodo.module] if nodo.module else []))


def imports_internos(arbol: ast.AST, modulo: str, es_paquete: bool, modulos: set[str]) -> list[str]:
    """Módulos beancount.* importados, incluidos los imports dentro de funciones."""
    salida = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            salida.update(a.name for a in nodo.names if a.name.split(".")[0] == "beancount")
        elif isinstance(nodo, ast.ImportFrom):
            base = resolver_import(nodo, modulo, es_paquete)
            if base.split(".")[0] != "beancount":
                continue
            for alias in nodo.names:
                candidato = f"{base}.{alias.name}"
                salida.add(candidato if candidato in modulos else base)
    salida.discard(modulo)
    return sorted(salida)


def decoradores_omision(arbol: ast.AST):
    """Devuelve (línea, objeto, tipo) de cada prueba omitida o marcada como fallo esperado."""
    claves = ("skip", "skipIf", "skipUnless", "expectedFailure", "xfail")
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for deco in nodo.decorator_list:
                objetivo = deco.func if isinstance(deco, ast.Call) else deco
                nombre = objetivo.attr if isinstance(objetivo, ast.Attribute) else getattr(objetivo, "id", "")
                if nombre in claves or nombre == "skipIfRaises":
                    motivo = ""
                    if isinstance(deco, ast.Call):
                        for arg in deco.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                motivo = arg.value
                    yield deco.lineno, nodo.name, nombre, " ".join(motivo.split())


def contar_tests(arbol: ast.Module) -> int:
    """Cuenta funciones test_* y métodos test_* de clases (análisis estático)."""
    total = 0
    for nodo in arbol.body:
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and nodo.name.startswith("test"):
            total += 1
        elif isinstance(nodo, ast.ClassDef):
            total += sum(
                isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test")
                for m in nodo.body
            )
    return total


def inventariar(repo: Path) -> list[dict]:
    fuentes = sorted((repo / "beancount").rglob("*.py"))
    fuentes = [f for f in fuentes if "__pycache__" not in f.parts]
    modulos = {nombre_modulo(f.relative_to(repo)) for f in fuentes}
    filas = []
    for archivo in fuentes:
        rel = archivo.relative_to(repo)
        texto = leer(archivo)
        modulo = nombre_modulo(rel)
        lineas = texto.splitlines()
        codigo = sum(1 for l in lineas if l.strip() and not l.strip().startswith("#"))
        fila = {
            "modulo": modulo,
            "ruta": rel.as_posix(),
            "paquete": ".".join(rel.parts[:2]) if len(rel.parts) > 2 else "beancount",
            "es_test": "si" if archivo.name.endswith("_test.py") else "no",
            "loc_total": len(lineas),
            "loc_no_vacias": codigo,
            "num_tests": 0,
            "docstring": "",
            "imports_internos": "",
            "error_ast": "",
        }
        try:
            arbol = ast.parse(texto, filename=str(archivo))
        except SyntaxError as exc:
            fila["error_ast"] = str(exc)
            filas.append(fila)
            continue
        doc = ast.get_docstring(arbol) or ""
        fila["docstring"] = doc.strip().split("\n")[0].strip() if doc.strip() else ""
        fila["imports_internos"] = ";".join(
            imports_internos(arbol, modulo, archivo.name == "__init__.py", modulos)
        )
        if fila["es_test"] == "si":
            fila["num_tests"] = contar_tests(arbol)
        filas.append(fila)
    return filas


def escribir_csv(ruta: Path, filas: list[dict], campos: list[str] | None = None) -> None:
    campos = campos or (list(filas[0]) if filas else [])
    with ruta.open("w", newline="", encoding="utf-8-sig") as salida:
        escritor = csv.DictWriter(salida, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def puntos_entrada(repo: Path) -> list[dict]:
    pyproject, setup = repo / "pyproject.toml", repo / "setup.py"
    pares: list[str] = []
    origen = ""
    if pyproject.exists() and tomllib and "project" in tomllib.loads(leer(pyproject)):
        origen = "pyproject.toml"
        scripts = tomllib.loads(leer(pyproject))["project"].get("scripts", {})
        pares = [f"{k} = {v}" for k, v in scripts.items()]
    elif setup.exists():
        origen = "setup.py"
        for nodo in ast.walk(ast.parse(leer(setup))):
            if isinstance(nodo, ast.Dict):
                for clave, valor in zip(nodo.keys, nodo.values):
                    if isinstance(clave, ast.Constant) and clave.value == "console_scripts":
                        pares = [e.value for e in valor.elts]
    filas = []
    for par in pares:
        nombre, destino = (x.strip() for x in par.split("="))
        modulo, funcion = destino.split(":")
        ruta = modulo.replace(".", "/") + ".py"
        filas.append({
            "cli": nombre, "modulo": modulo, "funcion": funcion,
            "ruta": ruta, "existe_modulo": "si" if (repo / ruta).exists() else "no",
            "origen": origen,
        })
    return sorted(filas, key=lambda f: f["cli"])


def linea_de(texto: str, patron: str) -> int:
    coincidencia = re.search(patron, texto, re.M)
    return texto.count("\n", 0, coincidencia.start()) + 1 if coincidencia else 0


def directivas(repo: Path) -> list[dict]:
    p = repo / "beancount"
    gramatica = leer(p / "parser/grammar.y")
    lexico = leer(p / "parser/lexer.l")
    builder = leer(p / "parser/grammar.py")
    datos = leer(p / "core/data.py")
    filas = []
    for nombre, palabra, token, regla, metodo, clase in DIRECTIVAS:
        def ref(archivo, n):
            return f"beancount/{archivo}:{n}" if n else "NO ENCONTRADO"
        # En v2.3.6 las directivas se definen como `Open = new_directive(...)`, no con `class`.
        l_clase = linea_de(datos, rf"^(?:class {clase}\(|{clase} = )") if clase else 0
        filas.append({
            "directiva": nombre,
            "palabra_clave": palabra,
            "token": token,
            "lexer_l": ref("parser/lexer.l", linea_de(lexico, rf"^\S+\s+\{{ return {token}; \}}")),
            "regla_grammar_y": ref("parser/grammar.y", linea_de(gramatica, rf"^{regla}:")),
            "metodo_builder": ref("parser/grammar.py", linea_de(builder, rf"^    def {metodo}\(")),
            "clase": clase or "(sin clase: afecta al analizador, no genera entrada)",
            "archivo_clase": ref("core/data.py", l_clase) if clase else "",
        })
    return filas


def api_publica(repo: Path) -> set[str]:
    """Clases y funciones públicas de nivel superior, módulos que no son test."""
    simbolos = set()
    for archivo in (repo / "beancount").rglob("*.py"):
        if archivo.name.endswith("_test.py") or "__pycache__" in archivo.parts:
            continue
        modulo = nombre_modulo(archivo.relative_to(repo))
        if any(p.startswith("_") for p in modulo.split(".")):
            continue
        try:
            arbol = ast.parse(leer(archivo))
        except SyntaxError:
            continue
        for nodo in arbol.body:
            if isinstance(nodo, (ast.FunctionDef, ast.ClassDef)) and not nodo.name.startswith("_"):
                simbolos.add(f"{modulo}.{nodo.name}")
            # Tipos creados por llamada: `Open = new_directive(...)`, `Cost = NamedTuple(...)`.
            elif isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Call):
                for destino in nodo.targets:
                    if isinstance(destino, ast.Name) and destino.id[:1].isupper() and not destino.id.isupper():
                        simbolos.add(f"{modulo}.{destino.id}")
    return simbolos


def comparar(actual, anterior, repo_a, repo_b, ent_a, ent_b, salida: Path) -> dict:
    map_a = {f["modulo"]: f for f in actual if f["es_test"] == "no"}
    map_b = {f["modulo"]: f for f in anterior if f["es_test"] == "no"}
    filas = []
    for mod in sorted(set(map_a) | set(map_b)):
        a, b = map_a.get(mod), map_b.get(mod)
        estado = "conservado" if a and b else ("nuevo_en_3.2.3" if a else "eliminado_en_3.2.3")
        filas.append({
            "modulo": mod, "estado": estado,
            "loc_2_3_6": b["loc_total"] if b else "", "loc_3_2_3": a["loc_total"] if a else "",
        })
    escribir_csv(salida / "comparacion_modulos.csv", filas)

    cli_a, cli_b = {e["cli"]: e for e in ent_a}, {e["cli"]: e for e in ent_b}
    filas_cli = [{
        "cli": c, "en_2_3_6": cli_b[c]["modulo"] if c in cli_b else "",
        "en_3_2_3": cli_a[c]["modulo"] if c in cli_a else "",
        "estado": "conservado" if c in cli_a and c in cli_b else ("nuevo" if c in cli_a else "eliminado"),
    } for c in sorted(set(cli_a) | set(cli_b))]
    escribir_csv(salida / "comparacion_cli.csv", filas_cli)

    dir_a, dir_b = directivas(repo_a), directivas(repo_b)
    filas_dir = [{
        "directiva": a["directiva"],
        "regla_2_3_6": b["regla_grammar_y"], "regla_3_2_3": a["regla_grammar_y"],
        "clase_2_3_6": b["archivo_clase"], "clase_3_2_3": a["archivo_clase"],
    } for a, b in zip(dir_a, dir_b)]
    escribir_csv(salida / "comparacion_directivas.csv", filas_dir)

    api_a, api_b = api_publica(repo_a), api_publica(repo_b)
    filas_api = [
        {"simbolo": s, "estado": "eliminado_en_3.2.3"} for s in sorted(api_b - api_a)
    ] + [{"simbolo": s, "estado": "nuevo_en_3.2.3"} for s in sorted(api_a - api_b)]
    escribir_csv(salida / "comparacion_api.csv", filas_api, ["simbolo", "estado"])
    return {
        "modulos_conservados": sum(f["estado"] == "conservado" for f in filas),
        "modulos_nuevos": sum(f["estado"] == "nuevo_en_3.2.3" for f in filas),
        "modulos_eliminados": sum(f["estado"] == "eliminado_en_3.2.3" for f in filas),
        "cli_conservados": sum(f["estado"] == "conservado" for f in filas_cli),
        "cli_nuevos": sum(f["estado"] == "nuevo" for f in filas_cli),
        "cli_eliminados": sum(f["estado"] == "eliminado" for f in filas_cli),
        "api_conservada": len(api_a & api_b),
        "api_nueva": len(api_a - api_b),
        "api_eliminada": len(api_b - api_a),
        "api_total_2_3_6": len(api_b),
        "api_total_3_2_3": len(api_a),
    }


def pruebas(repo: Path, filas: list[dict], salida: Path) -> dict:
    por_paquete: dict[str, dict] = {}
    for f in filas:
        d = por_paquete.setdefault(f["paquete"], {
            "paquete": f["paquete"], "modulos": 0, "archivos_test": 0, "tests_estaticos": 0,
            "loc_producto": 0, "loc_test": 0,
        })
        if f["es_test"] == "si":
            d["archivos_test"] += 1
            d["tests_estaticos"] += f["num_tests"]
            d["loc_test"] += f["loc_total"]
        else:
            d["modulos"] += 1
            d["loc_producto"] += f["loc_total"]
    escribir_csv(salida / "pruebas_por_paquete.csv", sorted(por_paquete.values(), key=lambda d: d["paquete"]))

    omitidas = []
    for f in filas:
        if f["es_test"] != "si":
            continue
        for linea, objeto, tipo, motivo in decoradores_omision(ast.parse(leer(repo / f["ruta"]))):
            omitidas.append({"archivo": f"{f['ruta']}:{linea}", "objeto": objeto, "tipo": tipo, "motivo": motivo})
    escribir_csv(salida / "pruebas_omitidas.csv", omitidas, ["archivo", "objeto", "tipo", "motivo"])

    rutas = {f["ruta"] for f in filas}
    sin_test = [
        {"modulo": f["modulo"], "ruta": f["ruta"], "loc_total": f["loc_total"]}
        for f in filas
        if f["es_test"] == "no" and not f["ruta"].endswith("__init__.py")
        and f["ruta"][:-3] + "_test.py" not in rutas
    ]
    escribir_csv(salida / "modulos_sin_test.csv", sin_test, ["modulo", "ruta", "loc_total"])
    return {"omisiones": len(omitidas), "modulos_sin_test": len(sin_test)}


def actualizar_mapa(filas: list[dict]) -> None:
    mapa = DOCS / "03_mapa_de_modulos.md"
    if not mapa.exists():
        return
    texto = leer(mapa)
    if MARCA_INI not in texto:
        return
    tabla = ["| Módulo | Ruta | LOC | Tests (estático) | Docstring (1.ª línea, original) |", "|---|---|--:|--:|---|"]
    for f in filas:
        if f["es_test"] == "si":
            continue
        pareja = next((p for p in filas if p["ruta"] == f["ruta"][:-3] + "_test.py"), None)
        doc = f["docstring"].replace("|", "\\|") or "(sin docstring)"
        tabla.append(f"| {f['modulo']} | `{f['ruta']}` | {f['loc_total']} | {pareja['num_tests'] if pareja else '—'} | {doc} |")
    ini, fin = texto.index(MARCA_INI) + len(MARCA_INI), texto.index(MARCA_FIN)
    mapa.write_text(texto[:ini] + "\n" + "\n".join(tabla) + "\n" + texto[fin:], encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=RAIZ / "beancount-src/v3.2.3")
    ap.add_argument("--repo-anterior", type=Path, default=RAIZ / "beancount-src/v2.3.6")
    args = ap.parse_args()
    salida = DOCS / "inventario"
    salida.mkdir(parents=True, exist_ok=True)

    filas = inventariar(args.repo)
    escribir_csv(salida / "modulos.csv", filas)
    entradas = puntos_entrada(args.repo)
    escribir_csv(salida / "entry_points.csv", entradas)
    escribir_csv(salida / "directivas_soportadas.csv", directivas(args.repo))
    extra = pruebas(args.repo, filas, salida)
    actualizar_mapa(filas)

    producto = [f for f in filas if f["es_test"] == "no"]
    test = [f for f in filas if f["es_test"] == "si"]
    resumen = {
        "archivos_py": len(filas), "modulos_producto": len(producto), "archivos_test": len(test),
        "loc_producto": sum(f["loc_total"] for f in producto),
        "loc_test": sum(f["loc_total"] for f in test),
        "tests_estaticos": sum(f["num_tests"] for f in test),
        "cli": len(entradas),
        "plugins": sum(f["paquete"] == "beancount.plugins" and not f["ruta"].endswith("__init__.py") for f in producto),
        "errores_ast": sum(bool(f["error_ast"]) for f in filas),
        **extra,
    }
    if (args.repo_anterior / "beancount").exists():
        previas = inventariar(args.repo_anterior)
        escribir_csv(salida / "modulos_2.3.6.csv", previas)
        ent_prev = puntos_entrada(args.repo_anterior)
        escribir_csv(salida / "entry_points_2.3.6.csv", ent_prev)
        resumen["comparacion"] = comparar(filas, previas, args.repo, args.repo_anterior, entradas, ent_prev, salida)
        prod_prev = [f for f in previas if f["es_test"] == "no"]
        resumen["v2_3_6"] = {
            "archivos_py": len(previas), "modulos_producto": len(prod_prev),
            "archivos_test": len(previas) - len(prod_prev),
            "loc_producto": sum(f["loc_total"] for f in prod_prev),
            "loc_test": sum(f["loc_total"] for f in previas if f["es_test"] == "si"),
            "tests_estaticos": sum(f["num_tests"] for f in previas),
            "cli": len(ent_prev),
        }
    else:
        resumen["comparacion"] = "v2.3.6 no disponible en este entorno"
    (salida / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
