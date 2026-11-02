# 00. Resumen ejecutivo

## Qué es Beancount

Beancount es un sistema de contabilidad de partida doble que usa archivos de texto como entrada. El usuario escribe sus movimientos en un lenguaje propio y el programa los carga en memoria, los verifica y permite generar informes ([`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml)). Toda transacción debe cuadrar y el libro admite aserciones de saldo, de modo que muchos errores de registro salen a la luz al cargar el archivo ([`beancount/ops/validation.py:365`](../beancount-src/v3.2.3/beancount/ops/validation.py#L365), [`beancount/ops/balance.py:48`](../beancount-src/v3.2.3/beancount/ops/balance.py#L48)).

Técnicamente es una biblioteca Python con un analizador en C generado con Flex y Bison ([`meson.build:215`](../beancount-src/v3.2.3/meson.build#L215)). Las herramientas de línea de comandos son una capa fina sobre esa biblioteca. El autor principal es Martin Blais y la licencia es GPL-2.0 ([`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml)).

La versión 3 es mucho más pequeña que la 2 porque separó funciones en otros paquetes: consultas, importación y precios ya no están en este repositorio (ver [doc. 09](09_comparacion_2_3_6_vs_3_2_3.md)).

## Versión analizada

| Versión | Etiqueta | Commit | Fecha del commit |
|---|---|---|---|
| 3.2.3 (principal) | `3.2.3` | `eeda2aa2a3204ffb980dab11220b2abde5e80b38` | 2026-05-05 |
| 2.3.6 (comparación) | `2.3.6` | `d77540c4b815221f882648b105ac06cdcb4699f3` | 2023-10-05 |

## Cifras clave (v3.2.3)

| Dato | Valor | Fuente |
|---|---|---|
| Archivos `.py` en [`beancount/`](../beancount-src/v3.2.3/beancount/) | 161 | [modulos.csv](inventario/modulos.csv) |
| Módulos de producto / archivos de prueba | 85 / 76 | [resumen.json](inventario/resumen.json) |
| Líneas Python de producto / de prueba | 21 444 / 23 206 | [resumen.json](inventario/resumen.json) |
| Comandos propios | 5 | [`pyproject.toml:54`](../beancount-src/v3.2.3/pyproject.toml#L54) |
| Plugins incluidos | 18 | [`beancount/plugins/__init__.py`](../beancount-src/v3.2.3/beancount/plugins/__init__.py) |
| Pruebas recogidas por pytest | 1119 | `pytest --collect-only`; **no se ejecutaron** |
| Directivas con clase de datos | 12 | [`beancount/core/data.py:452`](../beancount-src/v3.2.3/beancount/core/data.py#L452) |

Las líneas son físicas e incluyen comentarios y líneas en blanco. No cuentan el código C, Flex y Bison de [`beancount/parser/`](../beancount-src/v3.2.3/beancount/parser/).

## Componentes de la evaluación

| Componente | Cubre | Rutas principales |
|---|---|---|
| **C1** Analizador y cargador | Del texto a directivas, `include`, opciones y orquestación | [`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py), [`beancount/parser/parser.py`](../beancount-src/v3.2.3/beancount/parser/parser.py), [`beancount/parser/grammar.py`](../beancount-src/v3.2.3/beancount/parser/grammar.py), [`beancount/parser/grammar.y`](../beancount-src/v3.2.3/beancount/parser/grammar.y), [`beancount/parser/lexer.l`](../beancount-src/v3.2.3/beancount/parser/lexer.l), [`beancount/parser/options.py`](../beancount-src/v3.2.3/beancount/parser/options.py) |
| **C2** Núcleo contable | Tipos, inventarios, booking, validación y plugins | [`beancount/core/`](../beancount-src/v3.2.3/beancount/core/), [`beancount/ops/`](../beancount-src/v3.2.3/beancount/ops/), [`beancount/plugins/`](../beancount-src/v3.2.3/beancount/plugins/), [`beancount/parser/booking.py`](../beancount-src/v3.2.3/beancount/parser/booking.py), [`beancount/parser/booking_full.py`](../beancount-src/v3.2.3/beancount/parser/booking_full.py), [`beancount/parser/booking_method.py`](../beancount-src/v3.2.3/beancount/parser/booking_method.py) |
| **C3** CLI | Comandos y sus opciones | [`beancount/scripts/`](../beancount-src/v3.2.3/beancount/scripts/), [`beancount/tools/`](../beancount-src/v3.2.3/beancount/tools/), [`bin/`](../beancount-src/v3.2.3/bin/) |

Decisión de este análisis: el booking vive físicamente en [`beancount/parser/`](../beancount-src/v3.2.3/beancount/parser/), pero se asigna a C2 porque su función es contable. Si tu definición de componentes es otra, ajusta esta tabla antes del informe. El detalle está en el [doc. 11](11_notas_para_evaluacion_9126.md).

## Tres hechos que condicionan la evaluación

1. `bean-query`, `bean-extract`, `bean-identify`, `bean-file`, `bean-report`, `bean-web`, `bean-bake`, `bean-price`, `bean-sql` y `upload-to-sheets` **ya no pertenecen a este paquete** ([`pyproject.toml:54`](../beancount-src/v3.2.3/pyproject.toml#L54)). En el entorno, `bean-query` existe porque se instaló `beanquery` por separado.
2. `Booking.AVERAGE` figura como método en [`beancount/core/data.py:55`](../beancount-src/v3.2.3/beancount/core/data.py#L55), pero la implementación devuelve siempre un error ([`beancount/parser/booking_method.py:290`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L290)).
3. `validate()` modifica sin querer una lista global al recibir validaciones extra ([`beancount/ops/validation.py:423`](../beancount-src/v3.2.3/beancount/ops/validation.py#L423)). Lo comprobé ejecutándolo; afecta a cargas repetidas dentro de un mismo proceso (ver [doc. 11](11_notas_para_evaluacion_9126.md)).
