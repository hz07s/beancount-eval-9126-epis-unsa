# 07. Plugins y extensiones

## Cómo funciona

**Corrección a la hipótesis inicial del encargo:** `loader.load_file` **no** tiene un parámetro `plugins=[]` ([`beancount/loader.py:89`](../beancount-src/v3.2.3/beancount/loader.py#L89)). Los plugins se declaran en el propio libro:

```beancount
plugin "beancount.plugins.auto_accounts"
plugin "mi_paquete.mi_plugin" "configuración opcional"
```

Mecanismo:

1. `Builder.plugin` guarda el nombre y la configuración en las opciones ([`beancount/parser/grammar.py:449`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L449)).
2. `run_transformations` importa cada módulo ([`beancount/loader.py:688`](../beancount-src/v3.2.3/beancount/loader.py#L688)). Sin atributo `__plugins__`, el módulo **se ignora sin avisar** ([`beancount/loader.py:689`](../beancount-src/v3.2.3/beancount/loader.py#L689)).
3. Llama a cada función de `__plugins__`, indicada por nombre o directamente ([`beancount/loader.py:705`](../beancount-src/v3.2.3/beancount/loader.py#L705)).
4. Si hay configuración, la pasa como tercer argumento ([`beancount/loader.py:715`](../beancount-src/v3.2.3/beancount/loader.py#L715)).
5. Tras cada plugin, reordena las entradas, sin confiar en el plugin ([`beancount/loader.py:740`](../beancount-src/v3.2.3/beancount/loader.py#L740)).

**Contrato:** `f(entries, options_map[, config]) -> (entries, errors)`.

**Orden:** `documents`, plugins del usuario, automáticos, `pad`, `balance` ([`beancount/loader.py:665`](../beancount-src/v3.2.3/beancount/loader.py#L665)). Un plugin del usuario, por tanto, ve las transacciones ya completas por el booking, pero no las que generará `pad`.

**Fallos:** un error de importación o una excepción se convierten en errores de la lista ([`beancount/loader.py:691`](../beancount-src/v3.2.3/beancount/loader.py#L691), [`beancount/loader.py:721`](../beancount-src/v3.2.3/beancount/loader.py#L721)). Excepción: `SystemExit` sí se propaga ([`beancount/loader.py:723`](../beancount-src/v3.2.3/beancount/loader.py#L723)). Una excepción distinta de `ImportError` **durante la importación** también detiene la ejecución, por decisión documentada ([`beancount/loader.py:685`](../beancount-src/v3.2.3/beancount/loader.py#L685)).

**Plugins fuera del entorno:** con `option "insert_pythonpath" "TRUE"` se añade la carpeta del libro a `sys.path` ([`beancount/loader.py:556`](../beancount-src/v3.2.3/beancount/loader.py#L556)).

> Declarar un plugin equivale a ejecutar código Python arbitrario al cargar el libro. Tenlo presente al abrir archivos de terceros.

Otras vías de extensión: `extra_validations` en la carga ([`beancount/loader.py:93`](../beancount-src/v3.2.3/beancount/loader.py#L93)), `combine_plugins` para agruparlos ([`beancount/loader.py:745`](../beancount-src/v3.2.3/beancount/loader.py#L745)), y la directiva `custom` para datos propios ([`beancount/core/data.py:427`](../beancount-src/v3.2.3/beancount/core/data.py#L427)).

## Plugins incluidos

La descripción se resume de la docstring de cada módulo. «Tipo» es mi clasificación según esa docstring y su nombre, no una categoría del proyecto.

| Plugin | Función | Tipo |
|---|---|---|
| [`beancount/plugins/auto.py:17`](../beancount-src/v3.2.3/beancount/plugins/auto.py#L17) | Grupo: `auto_accounts` e `implicit_prices` | Grupo |
| [`beancount/plugins/pedantic.py:17`](../beancount-src/v3.2.3/beancount/plugins/pedantic.py#L17) | Grupo de comprobaciones estrictas | Grupo |
| [`beancount/plugins/auto_accounts.py:13`](../beancount-src/v3.2.3/beancount/plugins/auto_accounts.py#L13) | Inserta los `open` que falten | Transforma |
| [`beancount/plugins/implicit_prices.py:15`](../beancount-src/v3.2.3/beancount/plugins/implicit_prices.py#L15) | Crea `price` a partir de postings con precio | Transforma |
| [`beancount/plugins/close_tree.py:34`](../beancount-src/v3.2.3/beancount/plugins/close_tree.py#L34) | Cierra también las subcuentas | Transforma |
| [`beancount/plugins/check_closing.py:44`](../beancount-src/v3.2.3/beancount/plugins/check_closing.py#L44) | Añade un `balance` en postings de cierre | Transforma |
| [`beancount/plugins/check_drained.py:34`](../beancount-src/v3.2.3/beancount/plugins/check_drained.py#L34) | Añade un `balance` en cero antes del cierre | Transforma |
| [`beancount/plugins/currency_accounts.py:44`](../beancount-src/v3.2.3/beancount/plugins/currency_accounts.py#L44) | Implementa cuentas de cambio de moneda | Transforma |
| [`beancount/plugins/check_average_cost.py:25`](../beancount-src/v3.2.3/beancount/plugins/check_average_cost.py#L25) | Conserva la base de costo | Valida |
| [`beancount/plugins/check_commodity.py:28`](../beancount-src/v3.2.3/beancount/plugins/check_commodity.py#L28) | Toda moneda necesita `commodity` | Valida |
| [`beancount/plugins/coherent_cost.py:14`](../beancount-src/v3.2.3/beancount/plugins/coherent_cost.py#L14) | Monedas a costo no se convierten a precio | Valida |
| [`beancount/plugins/commodity_attr.py:26`](../beancount-src/v3.2.3/beancount/plugins/commodity_attr.py#L26) | Atributos exigidos en `commodity` | Valida |
| [`beancount/plugins/leafonly.py:19`](../beancount-src/v3.2.3/beancount/plugins/leafonly.py#L19) | Sin importes en cuentas que no son hoja | Valida |
| [`beancount/plugins/noduplicates.py:8`](../beancount-src/v3.2.3/beancount/plugins/noduplicates.py#L8) | Sin transacciones duplicadas | Valida |
| [`beancount/plugins/nounused.py:11`](../beancount-src/v3.2.3/beancount/plugins/nounused.py#L11) | Sin cuentas sin usar | Valida |
| [`beancount/plugins/onecommodity.py:28`](../beancount-src/v3.2.3/beancount/plugins/onecommodity.py#L28) | Una sola moneda por cuenta | Valida |
| [`beancount/plugins/sellgains.py:74`](../beancount-src/v3.2.3/beancount/plugins/sellgains.py#L74) | Coteja ganancias declaradas con precios | Valida |
| [`beancount/plugins/unique_prices.py:22`](../beancount-src/v3.2.3/beancount/plugins/unique_prices.py#L22) | Un único precio por día y par | Valida |

Plugins internos que siempre corren en modo normal: [`beancount/ops/documents.py:35`](../beancount-src/v3.2.3/beancount/ops/documents.py#L35), [`beancount/ops/pad.py:29`](../beancount-src/v3.2.3/beancount/ops/pad.py#L29), [`beancount/ops/balance.py:48`](../beancount-src/v3.2.3/beancount/ops/balance.py#L48).

En v3.2.3 se eliminaron 12 plugins respecto a la v2.3.6, como `forecast`, `unrealized` o `split_expenses`. Lista en [doc. 09](09_comparacion_2_3_6_vs_3_2_3.md).

## Esqueleto mínimo

Sigue la misma estructura de [`beancount/plugins/auto_accounts.py:13`](../beancount-src/v3.2.3/beancount/plugins/auto_accounts.py#L13) y se apoya en [`beancount/core/data.py:93`](../beancount-src/v3.2.3/beancount/core/data.py#L93). Probado con `bean-check` en un libro con `option "insert_pythonpath" "TRUE"`: informó `Transacción sin descripción` en la línea correcta y terminó con código 1.

```python
"""Exige que toda transacción tenga descripción."""
from typing import NamedTuple

from beancount.core import data

__plugins__ = ("exigir_descripcion",)


class ErrorDescripcion(NamedTuple):
    source: dict       # Metadatos: filename y lineno
    message: str
    entry: object


def exigir_descripcion(entries, options_map, config=None):
    errores = [
        ErrorDescripcion(e.meta, "Transacción sin descripción", e)
        for e in entries
        if isinstance(e, data.Transaction) and not e.narration
    ]
    return entries, errores
```

Se activa con `plugin "mi_modulo"`, siempre que el módulo sea importable.

## Relación con la extensibilidad

El sistema es sencillo y potente: una interfaz de una función, acceso a todas las entradas y el mismo mecanismo que los plugins internos. Sus límites, visibles en el código:

- Sin versionado de la interfaz ni registro de plugins.
- Un módulo sin `__plugins__` se ignora en silencio ([`beancount/loader.py:689`](../beancount-src/v3.2.3/beancount/loader.py#L689)), de modo que un plugin mal escrito pasa desapercibido.
- La configuración es una cadena sin estructura.
- Un plugin puede devolver cualquier lista. La validación posterior actúa de red ([`beancount/ops/validation.py:365`](../beancount-src/v3.2.3/beancount/ops/validation.py#L365)), pero `validate_data_types` solo corre en `bean-check` ([`beancount/ops/validation.py:404`](../beancount-src/v3.2.3/beancount/ops/validation.py#L404)).
