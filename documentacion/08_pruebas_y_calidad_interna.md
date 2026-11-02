# 08. Pruebas y calidad interna

> **Aclaración.** Este documento es una **inspección** de las pruebas del proyecto. No contiene métricas externas de la 9126 ni mide la calidad en uso. Que una prueba exista no significa que pase en tu entorno.

## Ubicación y convención

Las pruebas conviven con el código: `modulo.py` y `modulo_test.py` en la misma carpeta (por ejemplo [`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py) y [`beancount/loader_test.py`](../beancount-src/v3.2.3/beancount/loader_test.py)). [`pyproject.toml:83`](../beancount-src/v3.2.3/pyproject.toml#L83) configura pytest sobre `beancount`. También hay pruebas de C en [`beancount/parser/tokens_test.c`](../beancount-src/v3.2.3/beancount/parser/tokens_test.c) y [`beancount/utils/errors_test.cc`](../beancount-src/v3.2.3/beancount/utils/errors_test.cc), no incluidas en estas cifras.

Muchas pruebas escriben el libro de entrada en la docstring del caso y lo cargan con un decorador: [`beancount/loader.py:760`](../beancount-src/v3.2.3/beancount/loader.py#L760), [`beancount/parser/parser.py:258`](../beancount-src/v3.2.3/beancount/parser/parser.py#L258). Eso las hace buena referencia para aprender la sintaxis.

## Cómo se ejecutan

Desde `beancount-src/v3.2.3/`:

```bash
../../.venv-323/Scripts/python -m pytest beancount
```

El proyecto usa [`Makefile:112`](../beancount-src/v3.2.3/Makefile#L112) y la integración continua de [`.github/workflows/tests.yaml`](../beancount-src/v3.2.3/.github/workflows/tests.yaml), que cubre Ubuntu, Windows y macOS con Python de 3.9 a 3.14, y añade `meson test` para las pruebas C. No hay configuración de tox en el repositorio.

## Recuentos

- **1119** pruebas recogidas por `pytest --collect-only` (v3.2.3).
- **1094** según el análisis estático con `ast`. La diferencia de 25 probablemente se debe a clases de prueba heredadas y otras generadas; no la he desglosado.

| Paquete | Módulos | Archivos de prueba | Pruebas (estático) | LOC producto | LOC prueba |
|---|--:|--:|--:|--:|--:|
| `beancount` raíz | 3 | 1 | 32 | 1042 | 740 |
| `beancount.core` | 17 | 16 | 283 | 5616 | 5019 |
| `beancount.ops` | 10 | 9 | 131 | 2371 | 4074 |
| `beancount.parser` | 13 | 12 | 476 | 5295 | 8950 |
| `beancount.plugins` | 19 | 18 | 67 | 1562 | 1906 |
| `beancount.projects` | 2 | 1 | 1 | 429 | 24 |
| `beancount.scripts` | 7 | 7 | 32 | 2982 | 837 |
| `beancount.tools` | 2 | 1 | 20 | 430 | 610 |
| `beancount.utils` | 12 | 11 | 52 | 1717 | 1046 |
| **Total** | **85** | **76** | **1094** | **21 444** | **23 206** |

Por componente, la densidad es desigual: `parser` tiene más líneas de prueba que de código (8950 frente a 5295), mientras que `scripts`, que corresponde a C3, tiene bastante menos (837 frente a 2982).

## Cobertura

**No calculada.** `pytest-cov` no está en los entornos y la restricción era no instalar nada. Como aproximación estática, todos los módulos tienen un `_test.py` con su nombre salvo [`beancount/api.py`](../beancount-src/v3.2.3/beancount/api.py) ([modulos_sin_test.csv](inventario/modulos_sin_test.csv)), sin contar los `__init__.py`. Esto indica que el archivo existe, **no** cuánto código ejercita. El proyecto incluye [`tools/find_missing_tests.py`](../beancount-src/v3.2.3/tools/find_missing_tests.py) para una revisión parecida.

## Pruebas omitidas o de fallo esperado

Lista completa con motivos en [pruebas_omitidas.csv](inventario/pruebas_omitidas.csv) (18 decoradores). Las relevantes para madurez son:

| Prueba | Motivo declarado | Línea |
|---|---|---|
| `TestBookCrossover` (clase) | Cruce de posiciones sin soporte; remite a la reescritura en C++ | [`beancount/parser/booking_full_test.py:2706`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2706) |
| `_TestBookAmbiguousAVERAGE` (clase) | `Booking.AVERAGE is disabled` | [`beancount/parser/booking_full_test.py:2737`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2737) |
| 3 pruebas de autorreducción | `Disabled until self-reduction is supported` | [`beancount/parser/booking_full_test.py:2178`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2178) |
| `test_has_self_reductions__total_replacement` | Sin soporte de autorreducción total | [`beancount/parser/booking_full_test.py:2134`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2134) |
| 2 pruebas de costo explícito | `FIXME enable this when...` | [`beancount/parser/booking_full_test.py:2939`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2939) |
| `test_arithmetic_expressions` | `bean-format` aún no admite expresiones | [`beancount/scripts/format_test.py:244`](../beancount-src/v3.2.3/beancount/scripts/format_test.py#L244) |

Son condicionales y no indican carencias: [`beancount/utils/encryption_test.py:148`](../beancount-src/v3.2.3/beancount/utils/encryption_test.py#L148) (requiere `gpg`) y [`beancount/parser/parser_test.py:191`](../beancount-src/v3.2.3/beancount/parser/parser_test.py#L191) (requiere `sys.getrefcount`).

[`beancount/parser/parser_test.py:53`](../beancount-src/v3.2.3/beancount/parser/parser_test.py#L53) y [`beancount/parser/parser_test.py:63`](../beancount-src/v3.2.3/beancount/parser/parser_test.py#L63) son `expectedFailure` **a propósito**: comprueban que el decorador de pruebas detecta errores. No son defectos.

La mayoría de las omisiones relevantes están en booking, lo que coincide con el código desactivado en [`beancount/parser/booking_full.py:194`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L194) y [`beancount/parser/booking_method.py:295`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L295).

## Qué se ha ejecutado realmente

- `pytest --collect-only` en ambas versiones: 1119 (v3.2.3) y 1742 (v2.3.6). No ejecuta las pruebas.
- El setup previo ejecutó **solo un subconjunto** con `verify.py`. Sus registros dicen:
  - [logs/verify-3.2.3.log](../logs/verify-3.2.3.log): `112 passed, 2 xfailed`.
  - [logs/verify-2.3.6.log](../logs/verify-2.3.6.log): `2 failed, 113 passed, 2 xfailed`. Los fallos son `PermissionError` al reabrir un archivo temporal en `test_parse_file` y `test_parse_filename`. Parece un problema del test en Windows, no de la lógica, pero tenlo en cuenta al comparar.
- **La suite completa no se ha ejecutado en ninguna versión.**

## Otras herramientas de calidad interna

[`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml) configura `ruff` y `mypy`. [`.github/workflows/linting.yaml:16`](../beancount-src/v3.2.3/.github/workflows/linting.yaml#L16) ejecuta `make lint`, [`.github/workflows/linting.yaml:27`](../beancount-src/v3.2.3/.github/workflows/linting.yaml#L27) ejecuta `pre-commit` y [`.github/workflows/linting.yaml:39`](../beancount-src/v3.2.3/.github/workflows/linting.yaml#L39) ejecuta `mypy`. [`beancount/projects/`](../beancount-src/v3.2.3/beancount/projects/) queda excluido de los errores de `mypy` ([`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml)).
