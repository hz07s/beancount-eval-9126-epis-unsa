# 11. Notas para la evaluación NTP-ISO/IEC 9126

Este documento prepara la evaluación, pero **no define ni calcula métricas**. Tampoco dispongo del catálogo de métricas de tu curso. De los códigos que menciona tu encargo, solo conozco lo que dice ahí: 025 es «Inclusividad de funciones», y 015 y 011 se relacionan con mensajes de error. Comprueba estas referencias con tu catálogo.

## Mapa de carpetas a componentes

| Ruta | Comp. | Nota |
|---|---|---|
| [`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py) | C1 | Orquesta también a C2 |
| [`beancount/parser/parser.py`](../beancount-src/v3.2.3/beancount/parser/parser.py), [`beancount/parser/lexer.py`](../beancount-src/v3.2.3/beancount/parser/lexer.py) | C1 | |
| [`beancount/parser/grammar.y`](../beancount-src/v3.2.3/beancount/parser/grammar.y), [`beancount/parser/lexer.l`](../beancount-src/v3.2.3/beancount/parser/lexer.l), [`beancount/parser/grammar.py`](../beancount-src/v3.2.3/beancount/parser/grammar.py) | C1 | |
| [`beancount/parser/options.py`](../beancount-src/v3.2.3/beancount/parser/options.py) | C1 | |
| [`beancount/parser/printer.py`](../beancount-src/v3.2.3/beancount/parser/printer.py) | C1 y C3 | Convierte a texto; lo usan los errores de C3 |
| [`beancount/parser/booking.py`](../beancount-src/v3.2.3/beancount/parser/booking.py), [`beancount/parser/booking_full.py`](../beancount-src/v3.2.3/beancount/parser/booking_full.py), [`beancount/parser/booking_method.py`](../beancount-src/v3.2.3/beancount/parser/booking_method.py) | C2 | **Decisión mía**, por su función |
| [`beancount/core/`](../beancount-src/v3.2.3/beancount/core/) | C2 | |
| [`beancount/ops/`](../beancount-src/v3.2.3/beancount/ops/) | C2 | |
| [`beancount/plugins/`](../beancount-src/v3.2.3/beancount/plugins/) | C2 | **Decisión mía**; también podría tratarse aparte |
| [`beancount/scripts/`](../beancount-src/v3.2.3/beancount/scripts/), [`beancount/tools/`](../beancount-src/v3.2.3/beancount/tools/), [`bin/`](../beancount-src/v3.2.3/bin/) | C3 | |
| [`beancount/utils/`](../beancount-src/v3.2.3/beancount/utils/) | Soporte | No se evalúa por separado |
| [`beancount/projects/`](../beancount-src/v3.2.3/beancount/projects/), [`experiments/`](../beancount-src/v3.2.3/experiments/), [`tools/`](../beancount-src/v3.2.3/tools/) | Fuera | Herramientas de desarrollo o ejemplos |

## Dónde observar cada aspecto

| Aspecto a observar | Dónde | Cómo |
|---|---|---|
| Mensajes de error (según tu encargo, 015 y 011) | Sintaxis: [`beancount/parser/grammar.y:121`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L121). Carga: [`beancount/loader.py:437`](../beancount-src/v3.2.3/beancount/loader.py#L437). Booking: [`beancount/parser/booking_full.py:664`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L664). Validación: [`beancount/ops/validation.py:242`](../beancount-src/v3.2.3/beancount/ops/validation.py#L242). Saldo: [`beancount/ops/balance.py:164`](../beancount-src/v3.2.3/beancount/ops/balance.py#L164). Formato: [`beancount/parser/printer.py:556`](../beancount-src/v3.2.3/beancount/parser/printer.py#L556). | Provocar los errores de la [tabla del doc. 05](05_flujo_de_ejecucion.md) y valorar cada mensaje |
| Detección de errores | `bean-check`, código de salida en [`beancount/scripts/check.py:92`](../beancount-src/v3.2.3/beancount/scripts/check.py#L92); `--json` en [`beancount/scripts/check.py:34`](../beancount-src/v3.2.3/beancount/scripts/check.py#L34) | Casos con error conocido; contar los detectados |
| Recuperación tras un error | [`beancount/parser/grammar.y:870`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L870) | Libro con varios errores: ver si los informa todos y qué pasa con las líneas siguientes |
| Transacciones que se omiten tras un error | [`beancount/parser/booking_full.py:165`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L165), [`beancount/parser/booking_full.py:220`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L220) | Comprobar si ocultan errores posteriores |
| Inclusividad de funciones (según tu encargo, 025) | [Doc. 09](09_comparacion_2_3_6_vs_3_2_3.md); [comparacion_cli.csv](inventario/comparacion_cli.csv) | Definir antes si se compara el paquete o el ecosistema |
| Exactitud contable | [`beancount/core/interpolate.py:72`](../beancount-src/v3.2.3/beancount/core/interpolate.py#L72), [`beancount/core/inventory.py:459`](../beancount-src/v3.2.3/beancount/core/inventory.py#L459), [`beancount/parser/booking_method.py:161`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L161) | Casos con resultado calculado a mano |
| Tiempo de respuesta | `bean-check -v`, con tiempos por etapa desde [`beancount/loader.py:598`](../beancount-src/v3.2.3/beancount/loader.py#L598) | Con `--no-cache`, y libros de `bean-example` de varios tamaños |
| Tolerancia a entradas anómalas | [`beancount/parser/parser.py:212`](../beancount-src/v3.2.3/beancount/parser/parser.py#L212), [`beancount/loader.py:446`](../beancount-src/v3.2.3/beancount/loader.py#L446) | Archivos vacíos, binarios, muy grandes y con otra codificación |
| Instalabilidad | [`pyproject.toml`](../beancount-src/v3.2.3/pyproject.toml), [`meson.build:3`](../beancount-src/v3.2.3/meson.build#L3) | Windows requiere Flex y Bison si se compila; el setup usó ruedas binarias |
| Operabilidad y ayuda | `--help` de cada comando ([doc. 06](06_herramientas_cli.md)) | Consistencia entre comandos |
| Extensibilidad | [`beancount/loader.py:673`](../beancount-src/v3.2.3/beancount/loader.py#L673) | [Doc. 07](07_plugins_y_extensiones.md) |
| Datos de prueba reproducibles | [`beancount/scripts/example.py:1840`](../beancount-src/v3.2.3/beancount/scripts/example.py#L1840) | Usar `--seed` |

## Riesgos detectados en el análisis

Están verificados en el código salvo que se indique otra cosa. Son observaciones para investigar, y no una valoración de calidad.

### Confirmados por ejecución

1. **`validate()` altera una lista global.** `validation_tests = VALIDATIONS` seguido de `+=` ([`beancount/ops/validation.py:423`](../beancount-src/v3.2.3/beancount/ops/validation.py#L423), [`beancount/ops/validation.py:425`](../beancount-src/v3.2.3/beancount/ops/validation.py#L425)) modifica la lista original en lugar de una copia. Comprobado: tras 3 cargas con `extra_validations`, `VALIDATIONS` pasa de 7 a 10 elementos y `BASIC_VALIDATIONS` también. **Impacto:** nulo en una ejecución normal de `bean-check`, que carga una vez. En un proceso de larga duración, las validaciones se repiten y acumulan: se duplican errores y aumenta el tiempo. **Afecta a medidas** si automatizas varias cargas en un mismo proceso.
2. **Mensajes con detalle interno.** Una fecha inválida muestra `ValueError: month must be in 1..12`, y un plugin inexistente, un traceback de Python ([doc. 05](05_flujo_de_ejecucion.md)).
3. **Errores sin ubicación útil.** Los problemas de archivo e `include` aparecen como `<load>:0`, aunque el `include` tenga una línea concreta ([`beancount/loader.py:506`](../beancount-src/v3.2.3/beancount/loader.py#L506)).
4. **Reducción sobre inventario vacío sin error.** Mi caso `-1 HOOL {1 USD}` terminó con código 0. Sin confirmar si es lo previsto; investígalo antes de considerarlo un defecto.

### Confirmados por lectura

5. **Método `AVERAGE` no operativo.** Aceptado por la enumeración, siempre devuelve error ([`beancount/parser/booking_method.py:290`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L290)). Con pruebas omitidas ([`beancount/parser/booking_full_test.py:2737`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2737)).
6. **Código desactivado.** `if False:` en [`beancount/parser/booking_full.py:194`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L194) y [`beancount/parser/booking_method.py:295`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L295).
7. **Código aparentemente sin uso.** `validate_inventory_booking` lleva un `FIXME: This goes away` ([`beancount/parser/booking.py:86`](../beancount-src/v3.2.3/beancount/parser/booking.py#L86)). Ni esta función ni `convert_lot_specs_to_lots` ([`beancount/parser/booking.py:139`](../beancount-src/v3.2.3/beancount/parser/booking.py#L139)) tienen llamadas fuera de las pruebas según mi búsqueda.
8. **Assert sin efecto.** `assert "Invalid value..."` en [`beancount/loader.py:669`](../beancount-src/v3.2.3/beancount/loader.py#L669) evalúa una cadena no vacía y nunca falla. El impacto práctico es bajo porque el valor se valida antes ([`beancount/parser/options.py:24`](../beancount-src/v3.2.3/beancount/parser/options.py#L24)).
9. **Plugin sin `__plugins__` ignorado en silencio** ([`beancount/loader.py:689`](../beancount-src/v3.2.3/beancount/loader.py#L689)).
10. **Caché con pickle.** `pickle.load` lee un archivo junto al libro ([`beancount/loader.py:231`](../beancount-src/v3.2.3/beancount/loader.py#L231)). Un archivo de caché malicioso podría ejecutar código. La invalidación usa fecha y tamaño, no contenido ([`beancount/loader.py:337`](../beancount-src/v3.2.3/beancount/loader.py#L337)).
11. **Plugins como código arbitrario.** Cargar un libro ajeno puede ejecutar lo que declare ([`beancount/loader.py:688`](../beancount-src/v3.2.3/beancount/loader.py#L688)).
12. **Modo `raw` sin aserciones.** Omite `pad` y `balance` ([`beancount/loader.py:662`](../beancount-src/v3.2.3/beancount/loader.py#L662)).
13. **Menos cobertura en C3.** 837 líneas de prueba para 2982 de `scripts` ([doc. 08](08_pruebas_y_calidad_interna.md)).
14. **Autorreducción y cruce de posiciones sin soporte** ([`beancount/parser/booking_full_test.py:2178`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2178), [`beancount/parser/booking_full_test.py:2706`](../beancount-src/v3.2.3/beancount/parser/booking_full_test.py#L2706)).
15. **Inconsistencias menores.** `bean-example -v` exige valor ([`beancount/scripts/example.py:1849`](../beancount-src/v3.2.3/beancount/scripts/example.py#L1849)). Docstring copiada en [`beancount/ops/balance.py:1`](../beancount-src/v3.2.3/beancount/ops/balance.py#L1).

### Riesgos del propio entorno de medición

- **Caché:** una caché vigente evita todo el procesamiento. Desactívala al medir.
- **Mezcla de versiones:** `verify-3.2.3.log` muestra que `beancount` se importa desde el worktree, no desde `site-packages`. Confirma qué código ejecutas al medir.
- **Windows:** los dos fallos de v2.3.6 son de permisos con archivos temporales. Pueden distorsionar la comparación de resultados entre versiones.
- **Python:** los entornos usan Python 3.12 (`.tools/python312`). El sistema tiene 3.14. Anótalo en el informe.

## Referencias cruzadas

Arquitectura en el [doc. 02](02_arquitectura.md), flujo y errores en el [doc. 05](05_flujo_de_ejecucion.md), CLI en el [doc. 06](06_herramientas_cli.md), pruebas en el [doc. 08](08_pruebas_y_calidad_interna.md) y versiones en el [doc. 09](09_comparacion_2_3_6_vs_3_2_3.md).
