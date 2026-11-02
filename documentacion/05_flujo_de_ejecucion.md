# 05. Flujo de ejecución de `bean-check`

Diagramas: [flujo_parseo.mmd](diagramas/flujo_parseo.mmd) y [flujo_booking.mmd](diagramas/flujo_booking.mmd).

## Resumen

```text
Texto ─► tokens ─► directivas incompletas ─► ordenadas ─► booking ─► plugins ─► validación ─► salida
```

## Paso a paso

### 1. Arranque del comando
`main` ([`beancount/scripts/check.py:36`](../beancount-src/v3.2.3/beancount/scripts/check.py#L36)) lee las opciones con `click`. Con `--auto` añade plugins ([`beancount/scripts/check.py:60`](../beancount-src/v3.2.3/beancount/scripts/check.py#L60)) y con `--no-cache` o `--cache-filename` reconfigura la caché ([`beancount/scripts/check.py:67`](../beancount-src/v3.2.3/beancount/scripts/check.py#L67)). Llama a `load_file` pidiendo además las validaciones lentas ([`beancount/scripts/check.py:72-78`](../beancount-src/v3.2.3/beancount/scripts/check.py#L72)).

### 2. Normalización y caché
`load_file` ([`beancount/loader.py:89`](../beancount-src/v3.2.3/beancount/loader.py#L89)) expande la ruta y detecta si está cifrada ([`beancount/loader.py:118`](../beancount-src/v3.2.3/beancount/loader.py#L118)). `_load_file` está envuelta por la caché ([`beancount/loader.py:834`](../beancount-src/v3.2.3/beancount/loader.py#L834)). Si el pickle es válido y sus archivos no cambiaron, se devuelve el resultado y **no se repite ningún paso** ([`beancount/loader.py:246`](../beancount-src/v3.2.3/beancount/loader.py#L246)).

> Para medir tiempos o reproducir errores, usa `--no-cache` o `BEANCOUNT_DISABLE_LOAD_CACHE`. Una caché vigente cambia por completo lo que se ejecuta.

### 3. Análisis recursivo
`_parse_recursive` ([`beancount/loader.py:376`](../beancount-src/v3.2.3/beancount/loader.py#L376)) mantiene una pila de archivos.
- Archivo repetido: `Duplicate filename parsed` ([`beancount/loader.py:440`](../beancount-src/v3.2.3/beancount/loader.py#L440)).
- Archivo inexistente: `File "..." does not exist` ([`beancount/loader.py:450`](../beancount-src/v3.2.3/beancount/loader.py#L450)).
- `include` sin coincidencias: `File glob ... does not match` ([`beancount/loader.py:507`](../beancount-src/v3.2.3/beancount/loader.py#L507)).
- Las opciones que cuentan son solo las del archivo principal ([`beancount/loader.py:487`](../beancount-src/v3.2.3/beancount/loader.py#L487)).

### 4. Análisis de un archivo
`parse_file` ([`beancount/parser/parser.py:188`](../beancount-src/v3.2.3/beancount/parser/parser.py#L188)) crea el `Builder` ([`beancount/parser/parser.py:224`](../beancount-src/v3.2.3/beancount/parser/parser.py#L224)) y el analizador C ([`beancount/parser/parser.py:225`](../beancount-src/v3.2.3/beancount/parser/parser.py#L225)), lo ejecuta ([`beancount/parser/parser.py:226`](../beancount-src/v3.2.3/beancount/parser/parser.py#L226)) y recoge el resultado con `finalize` ([`beancount/parser/grammar.py:180`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L180)).

**Entra:** bytes. **Sale:** directivas incompletas, errores y opciones.

### 5. Ordenación
Por fecha, tipo y línea ([`beancount/loader.py:602`](../beancount-src/v3.2.3/beancount/loader.py#L602), [`beancount/core/data.py:708`](../beancount-src/v3.2.3/beancount/core/data.py#L708)). Por eso el orden del archivo no importa para las fechas.

### 6. Booking e interpolación
`booking.book` ([`beancount/parser/booking.py:26`](../beancount-src/v3.2.3/beancount/parser/booking.py#L26)) determina el método de cada cuenta ([`beancount/parser/booking.py:41`](../beancount-src/v3.2.3/beancount/parser/booking.py#L41)) y llama a `_book` ([`beancount/parser/booking_full.py:130`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L130)). Por cada transacción:

1. Agrupa los postings por moneda ([`beancount/parser/booking_full.py:164`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L164), función en [`beancount/parser/booking_full.py:296`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L296)). Con error, se **descarta la transacción**.
2. Calcula tolerancias ([`beancount/parser/booking_full.py:171`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L171)).
3. Empareja las reducciones con lotes existentes ([`beancount/parser/booking_full.py:215`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L215), función en [`beancount/parser/booking_full.py:564`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L564)). Si varios lotes coinciden, decide el método ([`beancount/parser/booking_method.py:31`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L31)). Con error, se omite ese grupo.
4. Calcula los números que faltan ([`beancount/parser/booking_full.py:229`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L229), función en [`beancount/parser/booking_full.py:798`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L798)).
5. Actualiza los inventarios ([`beancount/parser/booking_full.py:248`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L248)).

Al final comprueba que no queden `MISSING` ([`beancount/parser/booking.py:57`](../beancount-src/v3.2.3/beancount/parser/booking.py#L57)).

**Entra:** directivas incompletas. **Sale:** directivas completas.

### 7. Transformaciones
`run_transformations` ([`beancount/loader.py:639`](../beancount-src/v3.2.3/beancount/loader.py#L639)) ejecuta en este orden ([`beancount/loader.py:664`](../beancount-src/v3.2.3/beancount/loader.py#L664)):

1. `PLUGINS_PRE`: `beancount.ops.documents` ([`beancount/loader.py:54`](../beancount-src/v3.2.3/beancount/loader.py#L54)).
2. Plugins declarados por el usuario.
3. `PLUGINS_AUTO`: solo con `--auto` ([`beancount/loader.py:60`](../beancount-src/v3.2.3/beancount/loader.py#L60)).
4. `PLUGINS_POST`: `pad` y luego `balance` ([`beancount/loader.py:65`](../beancount-src/v3.2.3/beancount/loader.py#L65)).

Con `option "plugin_processing_mode" "raw"` solo se ejecutan los del usuario ([`beancount/loader.py:662`](../beancount-src/v3.2.3/beancount/loader.py#L662)): **tampoco corren `pad` ni `balance`**, con lo que se omiten las aserciones de saldo.

Un plugin que falla no detiene la carga: su excepción se convierte en error ([`beancount/loader.py:721`](../beancount-src/v3.2.3/beancount/loader.py#L721)).

### 8. Validación
`validate` ([`beancount/ops/validation.py:410`](../beancount-src/v3.2.3/beancount/ops/validation.py#L410)) ejecuta `BASIC_VALIDATIONS` ([`beancount/ops/validation.py:390`](../beancount-src/v3.2.3/beancount/ops/validation.py#L390)) y `bean-check` añade `HARDCORE_VALIDATIONS` ([`beancount/ops/validation.py:404`](../beancount-src/v3.2.3/beancount/ops/validation.py#L404)):

| Función | Comprueba | Línea |
|---|---|---|
| `validate_open_close` | Duplicados y orden de apertura y cierre | [`beancount/ops/validation.py:50`](../beancount-src/v3.2.3/beancount/ops/validation.py#L50) |
| `validate_active_accounts` | Que la cuenta exista y esté abierta | [`beancount/ops/validation.py:194`](../beancount-src/v3.2.3/beancount/ops/validation.py#L194) |
| `validate_currency_constraints` | Monedas permitidas por `open` | [`beancount/ops/validation.py:250`](../beancount-src/v3.2.3/beancount/ops/validation.py#L250) |
| `validate_duplicate_balances` | `balance` contradictorios | [`beancount/ops/validation.py:121`](../beancount-src/v3.2.3/beancount/ops/validation.py#L121) |
| `validate_duplicate_commodities` | `commodity` repetidos | [`beancount/ops/validation.py:160`](../beancount-src/v3.2.3/beancount/ops/validation.py#L160) |
| `validate_documents_paths` | Rutas absolutas de documentos | [`beancount/ops/validation.py:303`](../beancount-src/v3.2.3/beancount/ops/validation.py#L303) |
| `validate_check_transaction_balances` | Que la transacción cuadre | [`beancount/ops/validation.py:350`](../beancount-src/v3.2.3/beancount/ops/validation.py#L350) |
| `validate_data_types` | Tipos correctos (solo `bean-check`) | [`beancount/ops/validation.py:323`](../beancount-src/v3.2.3/beancount/ops/validation.py#L323) |

El cuadre se comprueba **después** de los plugins a propósito, para que un plugin pueda arreglar una transacción ([`beancount/ops/validation.py:365`](../beancount-src/v3.2.3/beancount/ops/validation.py#L365)).

### 9. Salida
`_log_errors` imprime en stderr ([`beancount/loader.py:164`](../beancount-src/v3.2.3/beancount/loader.py#L164)) con el formato `archivo:línea: mensaje` seguido de la entrada ([`beancount/parser/printer.py:556`](../beancount-src/v3.2.3/beancount/parser/printer.py#L556)). Con `--json` se escribe JSON en stdout ([`beancount/scripts/check.py:88`](../beancount-src/v3.2.3/beancount/scripts/check.py#L88)). El código de salida es 1 si hay algún error y 0 si no ([`beancount/scripts/check.py:92`](../beancount-src/v3.2.3/beancount/scripts/check.py#L92)).

## Dónde se pueden provocar errores

Entradas probadas con `bean-check` de la v3.2.3 (salidas reales, con la ruta acortada). Sirven de base para diseñar casos de prueba; **no** son resultados de una evaluación.

| Tipo | Entrada | Salida observada | Origen | Código |
|---|---|---|---|---|
| Sintaxis | Dos monedas en un posting | `syntax error, unexpected CURRENCY, expecting end of file or EOL or ATAT or AT` | [`beancount/parser/grammar.y:121`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L121) | 1 |
| Fecha imposible | `2026-13-40` | `ValueError: month must be in 1..12` | [`beancount/parser/grammar.y:87`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L87) | 1 |
| No cuadra | 10 USD y -9 USD | `Transaction does not balance: (1 USD)` | [`beancount/ops/validation.py:381`](../beancount-src/v3.2.3/beancount/ops/validation.py#L381) | 1 |
| Cuenta sin abrir | `Expenses:Nada` | `Invalid reference to unknown account 'Expenses:Nada'` | [`beancount/ops/validation.py:244`](../beancount-src/v3.2.3/beancount/ops/validation.py#L244) | 1 |
| Saldo incorrecto | `balance` de 5 con 0 | `Balance failed for 'Assets:A': expected 5 USD != accumulated 0 USD (5 too little)` | [`beancount/ops/balance.py:164`](../beancount-src/v3.2.3/beancount/ops/balance.py#L164) | 1 |
| Opción inválida | `option "no_existe" "1"` | `Invalid option: 'no_existe'` | [`beancount/parser/grammar.py:378`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L378) | 1 |
| Plugin inexistente | `plugin "no.existe"` | `Error importing "no.existe": Traceback (most recent call last): ...` | [`beancount/loader.py:697`](../beancount-src/v3.2.3/beancount/loader.py#L697) | 1 |
| `include` roto | Archivo inexistente | `File glob "no-existe.beancount" does not match any files` | [`beancount/loader.py:507`](../beancount-src/v3.2.3/beancount/loader.py#L507) | 1 |
| Archivo ausente | Ruta inexistente | `File "nada.beancount" does not exist` | [`beancount/loader.py:450`](../beancount-src/v3.2.3/beancount/loader.py#L450) | 1 |
| Venta sin lote | `-1 HOOL {1 USD}` con inventario vacío | **Ningún error** | No analizado a fondo | 0 |

Otros mensajes localizados en el código y **no provocados**: `No position matches` ([`beancount/parser/booking_full.py:664`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L664)), `Ambiguous matches` ([`beancount/parser/booking_method.py:102`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L102)), `Not enough lots` ([`beancount/parser/booking_method.py:60`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L60)), `Unused Pad entry` ([`beancount/ops/pad.py:201`](../beancount-src/v3.2.3/beancount/ops/pad.py#L201)).

Observaciones:

- Los errores de archivo, plugin e `include` aparecen como `<load>:0`, sin línea útil del libro ([`beancount/loader.py:439`](../beancount-src/v3.2.3/beancount/loader.py#L439)).
- El mensaje de fecha expone el texto de una excepción de Python, y el de plugin un traceback completo.
- Revisa el último caso de la tabla: reducir una cuenta vacía no dio error en esta prueba. Puede ser el comportamiento previsto (posición corta), pero no lo he verificado en el código.
