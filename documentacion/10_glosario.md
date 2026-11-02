# 10. Glosario

Las citas señalan dónde se implementa el concepto. Las definiciones contables son generales.

## Contabilidad

| Término | Significado |
|---|---|
| **Partida doble** | Todo movimiento afecta al menos a dos cuentas y suma cero. Se comprueba en [`beancount/ops/validation.py:350`](../beancount-src/v3.2.3/beancount/ops/validation.py#L350). |
| **Asiento** | Registro de un movimiento. En Beancount, una transacción ([`beancount/core/data.py:239`](../beancount-src/v3.2.3/beancount/core/data.py#L239)). |
| **Libro mayor** | Conjunto de movimientos por cuenta. El libro es el archivo; [`beancount/core/realization.py:211`](../beancount-src/v3.2.3/beancount/core/realization.py#L211) agrupa por cuenta. |
| **Balance o saldo** | Lo acumulado en una cuenta en una fecha. |
| **Activo, pasivo, patrimonio, ingreso, gasto** | Los cinco tipos de cuenta: `Assets`, `Liabilities`, `Equity`, `Income` y `Expenses` ([`beancount/core/account_types.py:26`](../beancount-src/v3.2.3/beancount/core/account_types.py#L26)). |
| **Costo base** | Lo que costó adquirir un activo. Base para calcular ganancias ([`beancount/core/position.py:28`](../beancount-src/v3.2.3/beancount/core/position.py#L28)). |
| **Lote** | Unidades adquiridas juntas, con su costo y fecha. |
| **FIFO, LIFO, HIFO** | Primero en entrar, último en entrar y costo más alto primero. Implementados en [`beancount/parser/booking_method.py:161`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L161), [`beancount/parser/booking_method.py:175`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L175) y [`beancount/parser/booking_method.py:189`](../beancount-src/v3.2.3/beancount/parser/booking_method.py#L189). |

## Beancount

| Término | Significado |
|---|---|
| **Directiva o entrada** | Elemento fechado del libro ([`beancount/core/data.py:452`](../beancount-src/v3.2.3/beancount/core/data.py#L452)). En el código, `entries` y `directives` son lo mismo. |
| **Posting** | Una línea de una transacción: cuenta e importe ([`beancount/core/data.py:206`](../beancount-src/v3.2.3/beancount/core/data.py#L206)). |
| **Bandera (flag)** | Estado de una transacción: `*` confirmada, `!` pendiente, y otras internas como `P` de padding ([`beancount/core/flags.py`](../beancount-src/v3.2.3/beancount/core/flags.py)). |
| **Metadatos** | Pares clave-valor en un objeto ([`beancount/core/data.py:508`](../beancount-src/v3.2.3/beancount/core/data.py#L508)). |
| **Tag** | Etiqueta `#nombre`. |
| **Link** | Enlace `^nombre` que relaciona transacciones. |
| **Moneda (commodity, currency)** | Cualquier unidad contable, también acciones o puntos. Formato en [`beancount/parser/lexer.l:203`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L203). |
| **Inventario** | Posiciones de una cuenta ([`beancount/core/inventory.py:81`](../beancount-src/v3.2.3/beancount/core/inventory.py#L81)). |
| **Booking** | Emparejar una reducción con los lotes existentes y completar importes ([`beancount/parser/booking_full.py:564`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L564)). |
| **Interpolación** | Calcular el número que falta para que la transacción cuadre ([`beancount/parser/booking_full.py:798`](../beancount-src/v3.2.3/beancount/parser/booking_full.py#L798)). |
| **Tolerancia** | Margen de redondeo admitido al cuadrar ([`beancount/core/interpolate.py:97`](../beancount-src/v3.2.3/beancount/core/interpolate.py#L97)). |
| **Reducción y aumento** | Posting que disminuye o incrementa una posición. |
| **Pad** | Genera un movimiento para que el siguiente `balance` se cumpla ([`beancount/ops/pad.py:29`](../beancount-src/v3.2.3/beancount/ops/pad.py#L29)). |
| **Balance (directiva)** | Aserción de saldo ([`beancount/ops/balance.py:48`](../beancount-src/v3.2.3/beancount/ops/balance.py#L48)). |
| **Realización** | Conversión de la lista de entradas en un árbol de cuentas con saldos ([`beancount/core/realization.py:45`](../beancount-src/v3.2.3/beancount/core/realization.py#L45)). |
| **Plugin** | Función que transforma o valida entradas al cargar ([`beancount/loader.py:639`](../beancount-src/v3.2.3/beancount/loader.py#L639)). |
| **Builder** | Objeto Python que crea las directivas durante el análisis ([`beancount/parser/grammar.py:145`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L145)). |
| **Query** | Consulta con nombre guardada en el libro ([`beancount/core/data.py:350`](../beancount-src/v3.2.3/beancount/core/data.py#L350)). La ejecuta beanquery, no este paquete. |
| **`options_map`** | Diccionario con las opciones del libro ([`beancount/parser/options.py:735`](../beancount-src/v3.2.3/beancount/parser/options.py#L735)). |

## Evaluación

Definiciones de trabajo: **compruébalas con el texto de la norma y con los materiales de tu curso**. No se han extraído de un documento oficial.

| Término | Significado |
|---|---|
| **NTP-ISO/IEC 9126** | Adopción peruana de la norma ISO/IEC 9126 sobre calidad del producto de software. La familia ISO/IEC 25000 (SQuaRE) es su sucesora. |
| **Métrica externa** | Mide el software en ejecución mediante su comportamiento, en lugar de inspeccionar su código. |
| **Métrica interna** | Mide el producto sin ejecutarlo, por ejemplo mediante el análisis del código. |
| **RNF** | Requisito no funcional: una exigencia sobre cómo debe comportarse el sistema, no sobre qué hace. |
| **Clarrus** | Aparece en tu encargo, pero **no** tengo una fuente que permita definirlo con seguridad. Completa esta entrada con tu material. |
| **C1, C2, C3** | Componentes definidos en tu encargo: analizador/cargador, núcleo contable y CLI. |
