# 06. Herramientas de línea de comandos

Las opciones proceden de la salida real de `--help` en `.venv-323` y de las declaraciones `click` citadas. El origen de los comandos es [`pyproject.toml:54`](../beancount-src/v3.2.3/pyproject.toml#L54).

## Comandos del paquete beancount

### `bean-check`
- **Módulo:** [`beancount/scripts/check.py:36`](../beancount-src/v3.2.3/beancount/scripts/check.py#L36)
- **Propósito:** cargar y validar un libro. No imprime nada si no hay errores; el resultado se expresa en el código de salida.
- **Ejemplo:** `bean-check libro.beancount`

| Opción | Efecto |
|---|---|
| `-v`, `--verbose` | Muestra tiempos por etapa |
| `-C`, `--no-cache` | Desactiva la caché |
| `--cache-filename RUTA` | Cambia el archivo de caché |
| `-a`, `--auto` | Añade plugins automáticos ([`beancount/plugins/auto.py`](../beancount-src/v3.2.3/beancount/plugins/auto.py)) |
| `--json` | Errores en JSON por stdout ([`beancount/scripts/check.py:88`](../beancount-src/v3.2.3/beancount/scripts/check.py#L88)) |
| `--version`, `--help` | Versión y ayuda |

Salida JSON observada:

```json
{"errors": [{"message": "Transaction does not balance: (1 USD)", "filename": "...", "lineno": 3}]}
```

### `bean-doctor`
- **Módulo:** [`beancount/scripts/doctor.py:92`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L92)
- **Propósito:** diagnóstico para quien investiga problemas en un libro o en el analizador.
- **Ejemplo:** `bean-doctor context libro.beancount 120`

| Subcomando | Efecto | Línea |
|---|---|---|
| `lex` | Vuelca los tokens | [`beancount/scripts/doctor.py:98`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L98) |
| `parse` | Analiza en modo depuración | [`beancount/scripts/doctor.py:111`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L111) |
| `roundtrip` | Comprueba imprimir y volver a cargar | [`beancount/scripts/doctor.py:122`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L122) |
| `directories` | Valida carpetas de documentos | [`beancount/scripts/doctor.py:196`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L196) |
| `list-options` | Lista las opciones disponibles | [`beancount/scripts/doctor.py:213`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L213) |
| `print-options` | Muestra las opciones de un libro | [`beancount/scripts/doctor.py:220`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L220) |
| `context` | Saldos antes y después de una transacción | [`beancount/scripts/doctor.py:230`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L230) |
| `linked` | Transacciones relacionadas | [`beancount/scripts/doctor.py:256`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L256) |
| `region` | Transacciones y saldos de una región | [`beancount/scripts/doctor.py:391`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L391) |
| `missing-open` | Genera los `open` que faltan | [`beancount/scripts/doctor.py:516`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L516) |
| `display-context` | Precisión inferida de los números | [`beancount/scripts/doctor.py:544`](../beancount-src/v3.2.3/beancount/scripts/doctor.py#L544) |

### `bean-example`
- **Módulo:** [`beancount/scripts/example.py:1851`](../beancount-src/v3.2.3/beancount/scripts/example.py#L1851)
- **Propósito:** generar un libro ficticio realista. Su ayuda indica que también sirve para pruebas de rendimiento.
- **Ejemplo:** `bean-example --date-begin 2023-01-01 --date-end 2025-01-01 -s 42 -o ejemplo.beancount`
- **Opciones:** `--date-begin`, `--date-end`, `--date-birth`, `-s/--seed`, `--no-reformat`, `-o/--output`, `-v/--verbose`.

Peculiaridad: `-v/--verbose` está declarada con `type=bool` ([`beancount/scripts/example.py:1849`](../beancount-src/v3.2.3/beancount/scripts/example.py#L1849)), así que exige un valor, a diferencia de `bean-check -v`.

### `bean-format`
- **Módulo:** [`beancount/scripts/format.py:176`](../beancount-src/v3.2.3/beancount/scripts/format.py#L176)
- **Propósito:** alinear importes. Según su ayuda, **no analiza el libro**: usa expresiones regulares, así que no detecta errores.
- **Ejemplo:** `bean-format -i libro.beancount`
- **Opciones:** `-o/--output`, `-w/--prefix-width`, `-W/--num-width`, `-c/--currency-column`, `-i/--in-place`.

### `treeify`
- **Módulo:** [`beancount/tools/treeify.py:409`](../beancount-src/v3.2.3/beancount/tools/treeify.py#L409)
- **Propósito:** convertir una columna de cuentas jerárquicas en un árbol ASCII. Es un filtro de texto genérico que usa `argparse`, a diferencia de los demás, que usan `click`.
- **Ejemplo:** `bean-query libro.beancount "SELECT account, sum(position) GROUP BY 1" | treeify`
- **Opciones:** `-o`, `-r/--pattern`, `-d/--delimiter`, `-s/--split`, `-F/--filenames`, `-A/--loose-accounts`, `--filler`.

## Comandos que pediste revisar y ya no son del paquete

| Comando | v2.3.6 | Situación en v3.2.3 |
|---|---|---|
| `bean-query` | [`v2.3.6:beancount/query/shell.py`](../beancount-src/v2.3.6/beancount/query/shell.py) | Fuera del paquete. **Disponible en `.venv-323`** gracias a `beanquery` 0.2.0 (`beanquery.shell:main`). Opciones: `-o`, `-f`, `-m`, `-q`. |
| `bean-report` | [`v2.3.6:beancount/reports/report.py`](../beancount-src/v2.3.6/beancount/reports/report.py) | Eliminado ([`CHANGES:203`](../beancount-src/v3.2.3/CHANGES#L203)). |
| `bean-extract` | [`v2.3.6:beancount/ingest/scripts_utils.py`](../beancount-src/v2.3.6/beancount/ingest/scripts_utils.py) | No está en el paquete ni en `.venv-323`. Su función pasó a beangulp. |
| `bean-identify` | [`v2.3.6:beancount/ingest/scripts_utils.py`](../beancount-src/v2.3.6/beancount/ingest/scripts_utils.py) | Igual que `bean-extract`. |
| `bean-file` | [`v2.3.6:beancount/ingest/scripts_utils.py`](../beancount-src/v2.3.6/beancount/ingest/scripts_utils.py) | Igual que `bean-extract`. |

Siguen disponibles en `.venv-236` para comparar.

## Tabla resumen

| Comando | Paquete | Framework | Lee el libro con | Comp. |
|---|---|---|---|---|
| `bean-check` | beancount | click | `loader.load_file` | C3, ejercita C1 y C2 |
| `bean-doctor` | beancount | click | `loader` o lexer, según el subcomando | C3, ejercita C1 y C2 |
| `bean-example` | beancount | click | No lee; genera | C3, genera datos para C1 y C2 |
| `bean-format` | beancount | click | Expresiones regulares | C3 |
| `treeify` | beancount | argparse | Texto genérico | C3 |
| `bean-query` | beanquery (externo) | click | `beanquery` | **Fuera de C3**, salvo que decidas incluirlo |

## Mapeo para la evaluación

Toda prueba por CLI atraviesa las tres capas. `bean-check` es el mejor punto de observación porque ejecuta toda la tubería y expone errores y código de salida. Para probar C1 de forma aislada, `bean-doctor parse` y `bean-doctor lex` llegan solo hasta el analizador. Para C2 sin CLI, usa `loader.load_string` ([`beancount/loader.py:341`](../beancount-src/v3.2.3/beancount/loader.py#L341)).

**Decisión que debes tomar:** si las funciones declaradas de C3 incluyen `bean-query`, estarías evaluando otro producto (beanquery 0.2.0), con otra versión y otras dependencias. Lo recomendable es dejarlo fuera y usarlo solo como apoyo.
