# 09. Comparación entre v2.3.6 y v3.2.3

Ambos worktrees están disponibles. Los datos proceden del análisis estático de los dos árboles (`scripts/generar_inventario.py`) y de `git diff 2.3.6 3.2.3`.

Commits: `d77540c4` (v2.3.6) y `eeda2aa2` (v3.2.3).

## Resumen

| Aspecto | v2.3.6 | v3.2.3 | Cambio |
|---|--:|--:|---|
| Archivos `.py` | 315 | 161 | -154 |
| Módulos de producto | 168 | 85 | 84 eliminados, 1 nuevo |
| LOC de producto | 40 159 | 21 444 | -47 % |
| LOC de prueba | 33 416 | 23 206 | -31 % |
| Pruebas (pytest, recogidas) | 1742 | 1119 | -623 |
| Comandos | 15 | 5 | 10 retirados, 0 nuevos |
| Plugins (módulos, sin contar `__init__`) | 30 | 18 | 12 retirados |
| Símbolos públicos | 1094 | 481 | 652 retirados, 39 nuevos |
| Directivas | 19 | 19 | Ninguna añadida ni retirada |
| Opciones | 32 | 36 | 4 nuevas, 0 retiradas |
| Dependencias obligatorias | 10 y 1 condicional | 3 | Ver abajo |

La reducción **no** es pérdida de funciones equivalente en todos los casos: en gran parte son funciones movidas a otros proyectos o sustituidas por ellos. Para la inclusividad de funciones importa distinguir si la evaluación considera el paquete o el ecosistema.

## Estructura

Lista completa: [comparacion_modulos.csv](inventario/comparacion_modulos.csv).

| Área | Módulos retirados | Destino |
|---|--:|---|
| [`v2.3.6:beancount/ingest`](../beancount-src/v2.3.6/beancount/ingest) | 19 | beangulp |
| [`v2.3.6:beancount/reports`](../beancount-src/v2.3.6/beancount/reports) | 16 | Retirado ([`CHANGES:203`](../beancount-src/v3.2.3/CHANGES#L203)) |
| [`v2.3.6:beancount/plugins`](../beancount-src/v2.3.6/beancount/plugins) | 12 | Retirados; destino no verificado |
| [`v2.3.6:beancount/prices`](../beancount-src/v2.3.6/beancount/prices) | 10 | beanprice ([`CHANGES:186`](../beancount-src/v3.2.3/CHANGES#L186)) |
| [`v2.3.6:beancount/query`](../beancount-src/v2.3.6/beancount/query) | 9 | beanquery |
| [`v2.3.6:beancount/utils`](../beancount-src/v2.3.6/beancount/utils) | 9 | Retirados |
| [`v2.3.6:beancount/web`](../beancount-src/v2.3.6/beancount/web) | 4 | Fava ([`CHANGES:205`](../beancount-src/v3.2.3/CHANGES#L205)) |
| Otros (`ops.holdings`, `projects.will`, `scripts.bake`, `scripts.sql`, `tools.sheets_upload`) | 5 | Retirados |

El único módulo nuevo es [`beancount/api.py`](../beancount-src/v3.2.3/beancount/api.py). Los paquetes `core`, `ops`, `parser`, `plugins`, `scripts`, `tools`, `utils` y `projects` se conservan.

**Plugins retirados:** `book_conversions`, `divert_expenses`, `exclude_tag`, `fill_account`, `fix_payees`, `forecast`, `ira_contribs`, `mark_unverified`, `merge_meta`, `split_expenses`, `tag_pending`, `unrealized`.

## Herramientas CLI

Fuente: [comparacion_cli.csv](inventario/comparacion_cli.csv).

| Comando | v2.3.6 | v3.2.3 | Nota |
|---|---|---|---|
| `bean-check` | Sí | Sí | `--json` es nueva ([`beancount/scripts/check.py:34`](../beancount-src/v3.2.3/beancount/scripts/check.py#L34)); `--cache-filename` ya existía ([`v2.3.6:beancount/scripts/check.py:32`](../beancount-src/v2.3.6/beancount/scripts/check.py#L32)) |
| `bean-doctor` | Sí | Sí | |
| `bean-example` | Sí | Sí | |
| `bean-format` | Sí | Sí | |
| `treeify` | Sí | Sí | |
| `bean-query` | Sí | No | En beanquery |
| `bean-extract`, `bean-identify`, `bean-file` | Sí | No | Función de beangulp |
| `bean-price` | Sí | No | En beanprice |
| `bean-report` | Sí | No | Retirado; [`CHANGES:203`](../beancount-src/v3.2.3/CHANGES#L203) recomienda `bean-query` |
| `bean-web`, `bean-bake` | Sí | No | [`CHANGES:205`](../beancount-src/v3.2.3/CHANGES#L205) recomienda Fava |
| `bean-sql` | Sí | No | Retirado |
| `upload-to-sheets` | Sí | No | Retirado |

También cambió el empaquetado: de `setuptools` ([`v2.3.6:setup.py`](../beancount-src/v2.3.6/setup.py)) a [`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml) con `mesonpy` ([`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml)).

## Sintaxis

Las 19 palabras de directiva y control existen en ambas ([comparacion_directivas.csv](inventario/comparacion_directivas.csv)). Las reglas de `grammar.y` y `lexer.l` sí cambian:

| Cambio | v2.3.6 | v3.2.3 |
|---|---|---|
| `note` con etiquetas y enlaces | [`v2.3.6:beancount/parser/grammar.y:725`](../beancount-src/v2.3.6/beancount/parser/grammar.y#L725) sin ellos | Admite `tags_links` ([`beancount/parser/grammar.y:742`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L742)) |
| Monedas de una letra | `Invalid token: 'V'` (probado) | Aceptadas (probado): token `CAPITAL` y regla `currency` ([`beancount/parser/grammar.y:352`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L352)) |
| Reconocimiento de banderas de letra | En `FLAGS` ([`v2.3.6:beancount/parser/lexer.l:140`](../beancount-src/v2.3.6/beancount/parser/lexer.l#L140)) | Fuera de `FLAGS` ([`beancount/parser/lexer.l:134`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L134)); se reconocen con `CAPITAL` ([`beancount/parser/lexer.l:240`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L240)) |
| Número de conflictos de la gramática esperados | `%expect 7` | `%expect 8` |

**Banderas de letra:** el cambio interno no rompe la sintaxis habitual. Comprobé en v3.2.3 que `P` en una transacción y `R` en un posting se aceptan sin comilla. El comentario de [`beancount/parser/lexer.l:134`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L134) dice que una letra debe llevar comilla, pero `'P` da `Invalid token` en ambas versiones, así que ese comentario induce a error.

**Opciones nuevas** ([`beancount/parser/options.py`](../beancount-src/v3.2.3/beancount/parser/options.py)): `account_unrealized_gains`, `display_precision`, `tolerance_multiplier`, `use_precise_interpolation`. Recuento hecho con una expresión regular sobre las declaraciones `Opt(`.

## API pública

Fuente: [comparacion_api.csv](inventario/comparacion_api.csv). Se cuentan clases, funciones y tipos de nivel superior sin guion bajo, fuera de pruebas. La mayor parte de lo retirado corresponde a módulos eliminados.

**Dentro de los módulos conservados del núcleo:**

| Símbolo | Cambio | Comentario |
|---|---|---|
| `beancount.core.data.new_directive` | Retirado | Las directivas pasaron de [`v2.3.6:beancount/core/data.py:101`](../beancount-src/v2.3.6/beancount/core/data.py#L101) a clases ([`beancount/core/data.py:93`](../beancount-src/v3.2.3/beancount/core/data.py#L93)) |
| `beancount.core.inventory.Booking` | Retirado | Sigue en [`beancount/core/data.py:55`](../beancount-src/v3.2.3/beancount/core/data.py#L55) |
| `beancount.ops.holdings.*` | Retirado | Módulo completo |
| `beancount.ops.balance.BalanceError` | Retirado | No verificado qué lo sustituye |
| `beancount.parser.cmptest.assertEqualEntries` y similares | Cambian de sitio | De función de módulo a método de `TestCase` ([`beancount/parser/cmptest.py:138`](../beancount-src/v3.2.3/beancount/parser/cmptest.py#L138)) |
| `beancount.parser.version.ArgumentParser` | Retirado | Los comandos usan `click` |
| `beancount.core.data.dtypes`, `BeancountError` | Nuevos | [`beancount/core/data.py:484`](../beancount-src/v3.2.3/beancount/core/data.py#L484), [`beancount/core/data.py:35`](../beancount-src/v3.2.3/beancount/core/data.py#L35) |
| `beancount.parser.booking_method.booking_method_STRICT_WITH_SIZE` | Nuevo | [`beancount/parser/booking_method.py:124`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L124) |
| `beancount` raíz como API | Nuevo | [`beancount/api.py:1`](../beancount-src/v3.2.3/beancount/api.py#L1), permite `import beancount as bn` |

Limitaciones: es una comparación por nombre. No detecta cambios de parámetros o de comportamiento, y un símbolo movido aparece como retirado y nuevo a la vez.

## Dependencias

- **v2.3.6** ([`v2.3.6:setup.py`](../beancount-src/v2.3.6/setup.py)): `pytest`, `python-dateutil`, `ply`, `bottle`, `lxml`, `beautifulsoup4`, `chardet`, `requests`, `google-api-python-client`, `pdfminer2`, y `python-magic` fuera de Windows.
- **v3.2.3** ([`pyproject.toml:30`](../beancount-src/v3.2.3/pyproject.toml#L30)): `click`, `python-dateutil`, `regex`.
- **Python:** de `>=3.7` a `>=3.9` ([`pyproject.toml:29`](../beancount-src/v3.2.3/pyproject.toml#L29)).

## Advertencias para la comparación

- `git status` de v2.3.6 muestra [`beancount/parser/_parser.cp312-win_amd64.pyd`](../beancount-src/v3.2.3/beancount/parser/_parser.cp312-win_amd64.pyd) sin seguimiento: lo instaló el setup previo. Es un binario compilado, no un cambio de código.
- Las pruebas de ambas versiones no se han ejecutado por completo ([doc. 08](08_pruebas_y_calidad_interna.md)).
- La columna «Destino» se basa en [`CHANGES`](../beancount-src/v3.2.3/CHANGES) y en el conocimiento general del proyecto. Solo se ha comprobado en el código lo que lleva cita.
