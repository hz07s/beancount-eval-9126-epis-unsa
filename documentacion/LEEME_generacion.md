# Cómo se generó esta carpeta

## Datos de la generación

| Dato | Valor |
|---|---|
| Fecha | 2026-11-01 |
| Beancount analizado | 3.2.3, commit `eeda2aa2a3204ffb980dab11220b2abde5e80b38` |
| Beancount comparado | 2.3.6, commit `d77540c4b815221f882648b105ac06cdcb4699f3` |
| Python de los scripts | 3.14.5 (biblioteca estándar) |
| Python de `.venv-323` y `.venv-236` | 3.12 (3.12.10 comprobado en `.venv-323`) |
| Git | 2.53.0.windows.3 |
| Graphviz | No instalado: solo se generan `.mmd` |
| Redacción | Claude Code (Opus 5.5), a partir de la lectura del código y de pruebas puntuales |

Los worktrees y los entornos virtuales son los del setup previo, en esta misma carpeta de trabajo. No se modificaron ni se instaló nada en ellos.

## Qué se regenera y qué no

| Elemento | ¿Se regenera con los comandos? |
|---|---|
| `inventario/*` | Sí |
| `diagramas/dependencias_modulos.mmd` | Sí |
| Tabla de módulos de `03_mapa_de_modulos.md` | Sí |
| Enlaces de las citas en los `.md` | Sí |
| Texto de los documentos | **No**: es redacción manual |
| Otros diagramas (`arquitectura`, `flujo_parseo`, `flujo_booking`) | **No**: hechos a mano |

Si cambias de versión de Beancount, los comandos fallarán en las citas cuya línea ya no exista, pero **no detectarán** citas que sigan existiendo y hayan quedado desplazadas. Habría que revisar el texto a mano.

## Comandos

Desde `D:\2026B\CS\teo\trabajo` (carpeta que contiene `beancount-src/` y `documentacion/`):

```bash
git -C beancount-src/v3.2.3 rev-parse HEAD
git -C beancount-src/v2.3.6 rev-parse HEAD
python documentacion/scripts/generar_inventario.py
python documentacion/scripts/generar_dependencias.py
python documentacion/scripts/verificar_documentacion.py
```

Si no tienes los worktrees, antes de esto: `git clone --depth 1 --branch 3.2.3 https://github.com/beancount/beancount.git beancount-src/v3.2.3`. La etiqueta real del repositorio es `3.2.3`, sin la `v`. Haz lo mismo con `2.3.6` para el doc. 09.

Para el recuento de pruebas del doc. 08 (no ejecuta las pruebas):

```bash
cd beancount-src/v3.2.3
PYTHONDONTWRITEBYTECODE=1 ../../.venv-323/Scripts/python -m pytest --collect-only -q -p no:cacheprovider beancount
```

## Qué comprueba `verificar_documentacion.py`

- Que existan todos los archivos esperados y funcionen los enlaces relativos.
- Que cada cita apunte a un archivo existente y a una línea dentro de su rango.
- Que `modulos.csv` coincida con todos los `.py` de [`beancount/`](../beancount-src/v3.2.3/beancount/) en disco.
- Que cada documento técnico cite código.
- Una comprobación básica de los `.mmd`.

**No** comprueba que la línea citada diga lo que afirma el texto. En esta generación se listaron las 254 citas con línea junto al texto de esa línea y se revisaron una vez, sin automatizar esa comparación. Las citas solo a archivo no tienen esa revisión.

## Comprobaciones adicionales de esta generación

No forman parte de los scripts y se hicieron una vez:

- Los 4 `.mmd` y los 2 bloques Mermaid de los `.md` se analizaron con el paquete `mermaid` real para Node, instalado en una carpeta temporal.
- El ejemplo del doc. 04 y los casos de error del doc. 05 se pasaron por `bean-check` con `BEANCOUNT_DISABLE_LOAD_CACHE=1`.
- El esqueleto de plugin del doc. 07 se ejecutó.
- El efecto sobre `VALIDATIONS` del doc. 11 se reprodujo.

## Herramientas opcionales

No usadas ni necesarias: `pydeps` (grafo por módulo), `pdoc` o `sphinx` (referencia de API), `pytest-cov` (cobertura) y `graphviz` (exportar PNG; `generar_dependencias.py` lo usa si está en el PATH).
