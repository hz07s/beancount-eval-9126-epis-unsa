# 03. Mapa de módulos

Las cifras salen de [inventario/modulos.csv](inventario/modulos.csv) y [pruebas_por_paquete.csv](inventario/pruebas_por_paquete.csv). Las dependencias son los imports hacia otros paquetes en código de producto ([dependencias_paquetes.csv](inventario/dependencias_paquetes.csv)).

## Por paquete

| Paquete | Propósito | Depende de | Módulos | LOC | Comp. |
|---|---|---|--:|--:|---|
| [`beancount/`](../beancount-src/v3.2.3/beancount/) raíz | Cargador ([`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py)) y API pública ([`beancount/api.py`](../beancount-src/v3.2.3/beancount/api.py)) | core, ops, parser, utils | 3 | 1042 | C1 |
| [`beancount/parser/`](../beancount-src/v3.2.3/beancount/parser/) | Analizador, opciones, impresión y booking | core, utils, raíz | 13 | 5295 | C1 y C2 |
| [`beancount/core/`](../beancount-src/v3.2.3/beancount/core/) | Tipos y algoritmos contables básicos | utils | 17 | 5616 | C2 |
| [`beancount/ops/`](../beancount-src/v3.2.3/beancount/ops/) | Operaciones sobre listas de directivas y validación | core, parser, utils, raíz | 10 | 2371 | C2 |
| [`beancount/plugins/`](../beancount-src/v3.2.3/beancount/plugins/) | Transformaciones y comprobaciones opcionales | core, parser, raíz | 19 | 1562 | C2 |
| [`beancount/scripts/`](../beancount-src/v3.2.3/beancount/scripts/) | Comandos | core, ops, parser, utils, raíz | 7 | 2982 | C3 |
| [`beancount/tools/`](../beancount-src/v3.2.3/beancount/tools/) | `treeify` | ninguna interna | 2 | 430 | C3 |
| [`beancount/utils/`](../beancount-src/v3.2.3/beancount/utils/) | Soporte general | ninguna interna | 12 | 1717 | Soporte |
| [`beancount/projects/`](../beancount-src/v3.2.3/beancount/projects/) | Script de exportación | core, ops, parser, raíz | 2 | 429 | Fuera de C1-C3 |

## Módulos que conviene leer

**C1**
- [`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py): la orquestación completa.
- [`beancount/parser/parser.py`](../beancount-src/v3.2.3/beancount/parser/parser.py): fachada; su docstring explica las entradas «incompletas».
- [`beancount/parser/grammar.py`](../beancount-src/v3.2.3/beancount/parser/grammar.py): el `Builder` que crea cada directiva.
- [`beancount/parser/grammar.y`](../beancount-src/v3.2.3/beancount/parser/grammar.y), [`beancount/parser/lexer.l`](../beancount-src/v3.2.3/beancount/parser/lexer.l): definición formal del lenguaje.
- [`beancount/parser/options.py`](../beancount-src/v3.2.3/beancount/parser/options.py): las opciones admitidas.

**C2**
- [`beancount/core/data.py`](../beancount-src/v3.2.3/beancount/core/data.py): las 12 directivas.
- [`beancount/core/inventory.py`](../beancount-src/v3.2.3/beancount/core/inventory.py), [`beancount/core/position.py`](../beancount-src/v3.2.3/beancount/core/position.py), [`beancount/core/amount.py`](../beancount-src/v3.2.3/beancount/core/amount.py): el modelo de saldos.
- [`beancount/core/interpolate.py`](../beancount-src/v3.2.3/beancount/core/interpolate.py): tolerancias y residuos.
- [`beancount/parser/booking_full.py`](../beancount-src/v3.2.3/beancount/parser/booking_full.py): el algoritmo más complejo; su docstring inicial explica el problema.
- [`beancount/ops/validation.py`](../beancount-src/v3.2.3/beancount/ops/validation.py), [`beancount/ops/balance.py`](../beancount-src/v3.2.3/beancount/ops/balance.py), [`beancount/ops/pad.py`](../beancount-src/v3.2.3/beancount/ops/pad.py).

**C3**
- [`beancount/scripts/check.py`](../beancount-src/v3.2.3/beancount/scripts/check.py): 96 líneas, lectura rápida y completa.
- [`beancount/scripts/doctor.py`](../beancount-src/v3.2.3/beancount/scripts/doctor.py): subcomandos de diagnóstico.

**Peculiaridades**
- [`beancount/scripts/example.py`](../beancount-src/v3.2.3/beancount/scripts/example.py) es el módulo más largo (1874 líneas), pero solo genera datos ficticios: no refleja complejidad del núcleo.
- La docstring de [`beancount/ops/balance.py:1`](../beancount-src/v3.2.3/beancount/ops/balance.py#L1) dice «Automatic padding», copia de la de [`beancount/ops/pad.py:1`](../beancount-src/v3.2.3/beancount/ops/pad.py#L1); el módulo en realidad comprueba saldos.
- [`beancount/scripts/deps.py`](../beancount-src/v3.2.3/beancount/scripts/deps.py) y [`beancount/scripts/directories.py`](../beancount-src/v3.2.3/beancount/scripts/directories.py) son módulos de apoyo, no comandos independientes.

## Todos los módulos de producto

Tabla generada por `scripts/generar_inventario.py`; no la edites a mano. Las docstrings se conservan en su idioma original. «Tests» indica las pruebas del archivo `*_test.py` emparejado por nombre, sin contar las heredadas.

<!-- INICIO_TABLA_MODULOS -->
| Módulo | Ruta | LOC | Tests (estático) | Docstring (1.ª línea, original) |
|---|---|--:|--:|---|
| beancount | [`beancount/__init__.py`](../beancount-src/v3.2.3/beancount/__init__.py) | 23 | — | Beancount, a double-entry bookkeeping software. |
| beancount.api | [`beancount/api.py`](../beancount-src/v3.2.3/beancount/api.py) | 172 | — | V3 public API. |
| beancount.core | [`beancount/core/__init__.py`](../beancount-src/v3.2.3/beancount/core/__init__.py) | 4 | — | Core basic objects and data structures to represent a list of entries. |
| beancount.core.account | [`beancount/core/account.py`](../beancount-src/v3.2.3/beancount/core/account.py) | 273 | 15 | Functions that operate on account strings. |
| beancount.core.account_types | [`beancount/core/account_types.py`](../beancount-src/v3.2.3/beancount/core/account_types.py) | 195 | 8 | Definition for global account types. |
| beancount.core.amount | [`beancount/core/amount.py`](../beancount-src/v3.2.3/beancount/core/amount.py) | 267 | 14 | Amount class. |
| beancount.core.compare | [`beancount/core/compare.py`](../beancount-src/v3.2.3/beancount/core/compare.py) | 225 | 7 | Comparison helpers for data objects. |
| beancount.core.convert | [`beancount/core/convert.py`](../beancount-src/v3.2.3/beancount/core/convert.py) | 232 | 31 | Conversions from Position (or Posting) to units, cost, weight, market value. |
| beancount.core.data | [`beancount/core/data.py`](../beancount-src/v3.2.3/beancount/core/data.py) | 848 | 16 | Basic data structures used to represent the Ledger entries. |
| beancount.core.display_context | [`beancount/core/display_context.py`](../beancount-src/v3.2.3/beancount/core/display_context.py) | 500 | 28 | A settings class to offer control over the number of digits rendered. |
| beancount.core.distribution | [`beancount/core/distribution.py`](../beancount-src/v3.2.3/beancount/core/distribution.py) | 78 | 2 | A simple accumulator for data about a mathematical distribution. |
| beancount.core.flags | [`beancount/core/flags.py`](../beancount-src/v3.2.3/beancount/core/flags.py) | 14 | 1 | Flag constants. |
| beancount.core.getters | [`beancount/core/getters.py`](../beancount-src/v3.2.3/beancount/core/getters.py) | 382 | 17 | Getter functions that operate on lists of entries to return various lists of |
| beancount.core.interpolate | [`beancount/core/interpolate.py`](../beancount-src/v3.2.3/beancount/core/interpolate.py) | 394 | 27 | Code used to automatically complete postings without positions. |
| beancount.core.inventory | [`beancount/core/inventory.py`](../beancount-src/v3.2.3/beancount/core/inventory.py) | 554 | 36 | A container for an inventory of positions. |
| beancount.core.number | [`beancount/core/number.py`](../beancount-src/v3.2.3/beancount/core/number.py) | 184 | 11 | The module contains the basic Decimal type import. |
| beancount.core.position | [`beancount/core/position.py`](../beancount-src/v3.2.3/beancount/core/position.py) | 401 | 29 | A position object, which consists of units Amount and cost Cost. |
| beancount.core.prices | [`beancount/core/prices.py`](../beancount-src/v3.2.3/beancount/core/prices.py) | 382 | 12 | This module has code that can build a database of historical prices at |
| beancount.core.realization | [`beancount/core/realization.py`](../beancount-src/v3.2.3/beancount/core/realization.py) | 683 | 29 | Realization of specific lists of account postings into reports. |
| beancount.loader | [`beancount/loader.py`](../beancount-src/v3.2.3/beancount/loader.py) | 847 | 32 | Loader code. This is the main entry point to load up a file. |
| beancount.ops | [`beancount/ops/__init__.py`](../beancount-src/v3.2.3/beancount/ops/__init__.py) | 7 | — | Operations on the entries defined in the core modules. |
| beancount.ops.balance | [`beancount/ops/balance.py`](../beancount-src/v3.2.3/beancount/ops/balance.py) | 185 | 19 | Automatic padding of gaps between entries. |
| beancount.ops.basicops | [`beancount/ops/basicops.py`](../beancount-src/v3.2.3/beancount/ops/basicops.py) | 86 | 4 | Basic filtering and aggregation operations on lists of entries. |
| beancount.ops.compress | [`beancount/ops/compress.py`](../beancount-src/v3.2.3/beancount/ops/compress.py) | 130 | 4 | Compress multiple entries into a single one. |
| beancount.ops.documents | [`beancount/ops/documents.py`](../beancount-src/v3.2.3/beancount/ops/documents.py) | 185 | 8 | Everything that relates to creating the Document directives. |
| beancount.ops.find_prices | [`beancount/ops/find_prices.py`](../beancount-src/v3.2.3/beancount/ops/find_prices.py) | 152 | 5 | A library of codes create price fetching jobs from strings and files. |
| beancount.ops.lifetimes | [`beancount/ops/lifetimes.py`](../beancount-src/v3.2.3/beancount/ops/lifetimes.py) | 224 | 13 | Given a Beancount ledger, compute time intervals where we hold each commodity. |
| beancount.ops.pad | [`beancount/ops/pad.py`](../beancount-src/v3.2.3/beancount/ops/pad.py) | 203 | 18 | Automatic padding of gaps between entries. |
| beancount.ops.summarize | [`beancount/ops/summarize.py`](../beancount-src/v3.2.3/beancount/ops/summarize.py) | 763 | 42 | Summarization of entries. |
| beancount.ops.validation | [`beancount/ops/validation.py`](../beancount-src/v3.2.3/beancount/ops/validation.py) | 436 | 18 | Validation checks. |
| beancount.parser | [`beancount/parser/__init__.py`](../beancount-src/v3.2.3/beancount/parser/__init__.py) | 6 | — | Parser module for beancount input files. |
| beancount.parser.booking | [`beancount/parser/booking.py`](../beancount-src/v3.2.3/beancount/parser/booking.py) | 224 | 10 | Algorithms for 'booking' inventory, that is, the process of finding a |
| beancount.parser.booking_full | [`beancount/parser/booking_full.py`](../beancount-src/v3.2.3/beancount/parser/booking_full.py) | 1049 | 138 | Full (new) booking implementation. |
| beancount.parser.booking_method | [`beancount/parser/booking_method.py`](../beancount-src/v3.2.3/beancount/parser/booking_method.py) | 384 | 0 | Implementations of all the particular booking methods. |
| beancount.parser.cmptest | [`beancount/parser/cmptest.py`](../beancount-src/v3.2.3/beancount/parser/cmptest.py) | 244 | 5 | Support utilities for testing scripts. |
| beancount.parser.context | [`beancount/parser/context.py`](../beancount-src/v3.2.3/beancount/parser/context.py) | 209 | 1 | Produce a rendering of the account balances just before and after a |
| beancount.parser.grammar | [`beancount/parser/grammar.py`](../beancount-src/v3.2.3/beancount/parser/grammar.py) | 1142 | 204 | Builder for Beancount grammar. |
| beancount.parser.hashsrc | [`beancount/parser/hashsrc.py`](../beancount-src/v3.2.3/beancount/parser/hashsrc.py) | 94 | 2 | Compute a hash of the source files in order to warn when the source goes out of date. |
| beancount.parser.lexer | [`beancount/parser/lexer.py`](../beancount-src/v3.2.3/beancount/parser/lexer.py) | 86 | 40 | Beancount syntax lexer. |
| beancount.parser.options | [`beancount/parser/options.py`](../beancount-src/v3.2.3/beancount/parser/options.py) | 849 | 22 | Declaration of options and their default values. |
| beancount.parser.parser | [`beancount/parser/parser.py`](../beancount-src/v3.2.3/beancount/parser/parser.py) | 359 | 24 | Beancount syntax parser. |
| beancount.parser.printer | [`beancount/parser/printer.py`](../beancount-src/v3.2.3/beancount/parser/printer.py) | 601 | 28 | Conversion from internal data structures to text. |
| beancount.parser.version | [`beancount/parser/version.py`](../beancount-src/v3.2.3/beancount/parser/version.py) | 48 | 2 | Implement common options across all programs. |
| beancount.plugins | [`beancount/plugins/__init__.py`](../beancount-src/v3.2.3/beancount/plugins/__init__.py) | 12 | — | Example plugins for filtering transactions. |
| beancount.plugins.auto | [`beancount/plugins/auto.py`](../beancount-src/v3.2.3/beancount/plugins/auto.py) | 17 | 1 | A plugin of plugins which triggers are all the automatic and lax plugins. |
| beancount.plugins.auto_accounts | [`beancount/plugins/auto_accounts.py`](../beancount-src/v3.2.3/beancount/plugins/auto_accounts.py) | 44 | 1 | This module automatically inserts Open directives for accounts not opened (at |
| beancount.plugins.check_average_cost | [`beancount/plugins/check_average_cost.py`](../beancount-src/v3.2.3/beancount/plugins/check_average_cost.py) | 97 | 1 | A plugin that ensures cost basis is preserved in unbooked transactions. |
| beancount.plugins.check_closing | [`beancount/plugins/check_closing.py`](../beancount-src/v3.2.3/beancount/plugins/check_closing.py) | 79 | 1 | A plugin that automatically inserts a balance check on a tagged closing posting. |
| beancount.plugins.check_commodity | [`beancount/plugins/check_commodity.py`](../beancount-src/v3.2.3/beancount/plugins/check_commodity.py) | 212 | 5 | A plugin that verifies that all seen commodities have a Commodity directive. |
| beancount.plugins.check_drained | [`beancount/plugins/check_drained.py`](../beancount-src/v3.2.3/beancount/plugins/check_drained.py) | 98 | 8 | Insert a balance check for zero before balance sheet accounts are closed. |
| beancount.plugins.close_tree | [`beancount/plugins/close_tree.py`](../beancount-src/v3.2.3/beancount/plugins/close_tree.py) | 71 | 8 | This plugin inserts close directives for all of an account's descendants when |
| beancount.plugins.coherent_cost | [`beancount/plugins/coherent_cost.py`](../beancount-src/v3.2.3/beancount/plugins/coherent_cost.py) | 49 | 1 | This plugin validates that currencies held at cost aren't ever converted at |
| beancount.plugins.commodity_attr | [`beancount/plugins/commodity_attr.py`](../beancount-src/v3.2.3/beancount/plugins/commodity_attr.py) | 87 | 2 | A plugin that asserts that all Commodity directives have a particular |
| beancount.plugins.currency_accounts | [`beancount/plugins/currency_accounts.py`](../beancount-src/v3.2.3/beancount/plugins/currency_accounts.py) | 155 | 7 | An implementation of currency accounts. |
| beancount.plugins.implicit_prices | [`beancount/plugins/implicit_prices.py`](../beancount-src/v3.2.3/beancount/plugins/implicit_prices.py) | 124 | 5 | This plugin synthesizes Price directives for all Postings with a price |
| beancount.plugins.leafonly | [`beancount/plugins/leafonly.py`](../beancount-src/v3.2.3/beancount/plugins/leafonly.py) | 60 | 3 | A plugin that issues errors when amounts are posted to non-leaf accounts, |
| beancount.plugins.noduplicates | [`beancount/plugins/noduplicates.py`](../beancount-src/v3.2.3/beancount/plugins/noduplicates.py) | 21 | 9 | This plugin validates that there are no duplicate transactions. |
| beancount.plugins.nounused | [`beancount/plugins/nounused.py`](../beancount-src/v3.2.3/beancount/plugins/nounused.py) | 56 | 1 | This plugin validates that there are no unused accounts. |
| beancount.plugins.onecommodity | [`beancount/plugins/onecommodity.py`](../beancount-src/v3.2.3/beancount/plugins/onecommodity.py) | 133 | 5 | A plugin that issues errors when more than one commodity is used in an account. |
| beancount.plugins.pedantic | [`beancount/plugins/pedantic.py`](../beancount-src/v3.2.3/beancount/plugins/pedantic.py) | 27 | 1 | A plugin of plugins which triggers all the pedantic plugins. |
| beancount.plugins.sellgains | [`beancount/plugins/sellgains.py`](../beancount-src/v3.2.3/beancount/plugins/sellgains.py) | 158 | 5 | A plugin that cross-checks declared gains against prices on lot sales. |
| beancount.plugins.unique_prices | [`beancount/plugins/unique_prices.py`](../beancount-src/v3.2.3/beancount/plugins/unique_prices.py) | 62 | 3 | This module adds validation that there is a single price defined per |
| beancount.projects | [`beancount/projects/__init__.py`](../beancount-src/v3.2.3/beancount/projects/__init__.py) | 10 | — | A directory to hold various one-off special project scripts. |
| beancount.projects.export | [`beancount/projects/export.py`](../beancount-src/v3.2.3/beancount/projects/export.py) | 419 | 1 | List assets and attributes of account and commodities. |
| beancount.scripts | [`beancount/scripts/__init__.py`](../beancount-src/v3.2.3/beancount/scripts/__init__.py) | 8 | — | Implementation of the various scripts available from bin. |
| beancount.scripts.check | [`beancount/scripts/check.py`](../beancount-src/v3.2.3/beancount/scripts/check.py) | 96 | 3 | (sin docstring) |
| beancount.scripts.deps | [`beancount/scripts/deps.py`](../beancount-src/v3.2.3/beancount/scripts/deps.py) | 131 | 1 | Check the installation dependencies and report the version numbers of each. |
| beancount.scripts.directories | [`beancount/scripts/directories.py`](../beancount-src/v3.2.3/beancount/scripts/directories.py) | 71 | 2 | Check that document directories mirror a list of accounts correctly. |
| beancount.scripts.doctor | [`beancount/scripts/doctor.py`](../beancount-src/v3.2.3/beancount/scripts/doctor.py) | 554 | 13 | Debugging tool for those finding bugs in Beancount. |
| beancount.scripts.example | [`beancount/scripts/example.py`](../beancount-src/v3.2.3/beancount/scripts/example.py) | 1874 | 2 | (sin docstring) |
| beancount.scripts.format | [`beancount/scripts/format.py`](../beancount-src/v3.2.3/beancount/scripts/format.py) | 248 | 10 | (sin docstring) |
| beancount.tools | [`beancount/tools/__init__.py`](../beancount-src/v3.2.3/beancount/tools/__init__.py) | 13 | — | Standalone tools that aren't linked to Beancount but that are useful with it. |
| beancount.tools.treeify | [`beancount/tools/treeify.py`](../beancount-src/v3.2.3/beancount/tools/treeify.py) | 417 | 20 | Identify a column of text that contains hierarchical id and treeify that column. |
| beancount.utils | [`beancount/utils/__init__.py`](../beancount-src/v3.2.3/beancount/utils/__init__.py) | 6 | — | Generic utility packages and functions. |
| beancount.utils.bisect_key | [`beancount/utils/bisect_key.py`](../beancount-src/v3.2.3/beancount/utils/bisect_key.py) | 78 | 2 | A version of bisect that accepts a custom key function, like the sorting ones do. |
| beancount.utils.defdict | [`beancount/utils/defdict.py`](../beancount-src/v3.2.3/beancount/utils/defdict.py) | 51 | 2 | An instance of collections.defaultdict whose factory accepts a key. |
| beancount.utils.encryption | [`beancount/utils/encryption.py`](../beancount-src/v3.2.3/beancount/utils/encryption.py) | 80 | 3 | Support for encrypted tests. |
| beancount.utils.file_utils | [`beancount/utils/file_utils.py`](../beancount-src/v3.2.3/beancount/utils/file_utils.py) | 102 | 3 | File utilities. |
| beancount.utils.import_utils | [`beancount/utils/import_utils.py`](../beancount-src/v3.2.3/beancount/utils/import_utils.py) | 24 | 1 | Utilities for importing symbols programmatically. |
| beancount.utils.invariants | [`beancount/utils/invariants.py`](../beancount-src/v3.2.3/beancount/utils/invariants.py) | 82 | 1 | Functions to register auxiliary functions on a class' methods to check for invariants. |
| beancount.utils.memo | [`beancount/utils/memo.py`](../beancount-src/v3.2.3/beancount/utils/memo.py) | 61 | 2 | Memoization utilities. |
| beancount.utils.misc_utils | [`beancount/utils/misc_utils.py`](../beancount-src/v3.2.3/beancount/utils/misc_utils.py) | 306 | 14 | Generic utility packages and functions. |
| beancount.utils.pager | [`beancount/utils/pager.py`](../beancount-src/v3.2.3/beancount/utils/pager.py) | 199 | 3 | Code to write output to a pager. |
| beancount.utils.table | [`beancount/utils/table.py`](../beancount-src/v3.2.3/beancount/utils/table.py) | 292 | 8 | Table rendering. |
| beancount.utils.test_utils | [`beancount/utils/test_utils.py`](../beancount-src/v3.2.3/beancount/utils/test_utils.py) | 436 | 13 | Support utilities for testing scripts. |
<!-- FIN_TABLA_MODULOS -->
