# 04. Modelo de datos y sintaxis

## Dos familias de elementos

La gramática distingue dos reglas ([`beancount/parser/grammar.y:813`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L813), [`beancount/parser/grammar.y:853`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L853)):

- **Entradas (`entry`):** llevan fecha y producen un objeto en la lista de directivas.
- **Directivas de control (`directive`):** afectan al análisis, pero no producen una entrada.

Cada elemento está cruzado con el léxico, la gramática, el Builder y su clase en [directivas_soportadas.csv](inventario/directivas_soportadas.csv).

### Entradas con fecha

| Directiva | Para qué sirve | Clase |
|---|---|---|
| `open` | Abre una cuenta, con monedas permitidas y método de booking opcionales | [`beancount/core/data.py:93`](../beancount-src/v3.2.3/beancount/core/data.py#L93) |
| `close` | Cierra una cuenta | [`beancount/core/data.py:118`](../beancount-src/v3.2.3/beancount/core/data.py#L118) |
| `commodity` | Declara una moneda o activo y sus metadatos | [`beancount/core/data.py:133`](../beancount-src/v3.2.3/beancount/core/data.py#L133) |
| `pad` | Rellena automáticamente hasta el siguiente `balance` | [`beancount/core/data.py:155`](../beancount-src/v3.2.3/beancount/core/data.py#L155) |
| `balance` | Afirma el saldo de una cuenta al inicio de un día | [`beancount/core/data.py:177`](../beancount-src/v3.2.3/beancount/core/data.py#L177) |
| transacción (`txn` o bandera) | Movimiento compuesto por postings | [`beancount/core/data.py:239`](../beancount-src/v3.2.3/beancount/core/data.py#L239) |
| `note` | Comentario fechado sobre una cuenta | [`beancount/core/data.py:287`](../beancount-src/v3.2.3/beancount/core/data.py#L287) |
| `event` | Valor de una variable en el tiempo | [`beancount/core/data.py:313`](../beancount-src/v3.2.3/beancount/core/data.py#L313) |
| `query` | Consulta con nombre | [`beancount/core/data.py:350`](../beancount-src/v3.2.3/beancount/core/data.py#L350) |
| `price` | Precio de un activo en una fecha | [`beancount/core/data.py:372`](../beancount-src/v3.2.3/beancount/core/data.py#L372) |
| `document` | Vincula un archivo a una cuenta | [`beancount/core/data.py:397`](../beancount-src/v3.2.3/beancount/core/data.py#L397) |
| `custom` | Directiva genérica para extensiones | [`beancount/core/data.py:427`](../beancount-src/v3.2.3/beancount/core/data.py#L427) |

La lista oficial es `ALL_DIRECTIVES` ([`beancount/core/data.py:452`](../beancount-src/v3.2.3/beancount/core/data.py#L452)). Dentro del mismo día, `open` y `balance` se ordenan primero, y `document` y `close` al final ([`beancount/core/data.py:705`](../beancount-src/v3.2.3/beancount/core/data.py#L705)).

### Directivas de control

`option` ([`beancount/parser/grammar.py:367`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L367)), `include` ([`beancount/parser/grammar.py:439`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L439)), `plugin` ([`beancount/parser/grammar.py:449`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L449)), `pushtag`/`poptag` ([`beancount/parser/grammar.py:307`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L307), [`beancount/parser/grammar.py:319`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L319)), `pushmeta`/`popmeta` ([`beancount/parser/grammar.py:335`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L335), [`beancount/parser/grammar.py:346`](../beancount-src/v3.2.3/beancount/parser/grammar.py#L346)).

## Tipos centrales

```text
Transaction
 ├─ meta, date, flag, payee, narration, tags, links
 └─ postings: lista de Posting
      ├─ account   (str, p. ej. "Assets:Banco")
      ├─ units     Amount(number: Decimal, currency: str)
      ├─ cost      Cost(number, currency, date, label)  tras el booking
      │            CostSpec                             antes del booking
      ├─ price     Amount
      ├─ flag
      └─ meta
```

| Tipo | Qué es | Dónde |
|---|---|---|
| `Amount` | Número y moneda | [`beancount/core/amount.py:40`](../beancount-src/v3.2.3/beancount/core/amount.py#L40) |
| `Cost` | Costo definitivo de un lote | [`beancount/core/position.py:28`](../beancount-src/v3.2.3/beancount/core/position.py#L28) |
| `CostSpec` | Costo parcial escrito por el usuario | [`beancount/core/position.py:45`](../beancount-src/v3.2.3/beancount/core/position.py#L45) |
| `Position` | Unidades y costo | [`beancount/core/position.py:161`](../beancount-src/v3.2.3/beancount/core/position.py#L161) |
| `Posting` | Una línea de la transacción | [`beancount/core/data.py:206`](../beancount-src/v3.2.3/beancount/core/data.py#L206) |
| `Inventory` | Posiciones por `(moneda, costo)` | [`beancount/core/inventory.py:81`](../beancount-src/v3.2.3/beancount/core/inventory.py#L81) |
| `Booking` | Enumeración de métodos | [`beancount/core/data.py:55`](../beancount-src/v3.2.3/beancount/core/data.py#L55) |
| `RealAccount` | Árbol de cuentas con sus saldos | [`beancount/core/realization.py:45`](../beancount-src/v3.2.3/beancount/core/realization.py#L45) |

**La distinción clave es incompleto y completo.** El analizador produce postings a los que les pueden faltar datos, marcados con `MISSING` ([`beancount/core/number.py:31`](../beancount-src/v3.2.3/beancount/core/number.py#L31)), y costos `CostSpec`. El booking los convierte en definitivos ([`beancount/parser/parser.py:1`](../beancount-src/v3.2.3/beancount/parser/parser.py#L1)).

**Cuentas.** Son cadenas con componentes separados por `:`. Su formato lo define [`beancount/core/account.py:41`](../beancount-src/v3.2.3/beancount/core/account.py#L41) y las funciones para manejarlas están en el mismo módulo. Los cinco tipos raíz son configurables mediante opciones ([`beancount/core/account_types.py:26`](../beancount-src/v3.2.3/beancount/core/account_types.py#L26)).

**Metadatos.** Todo objeto lleva `meta`, con `filename` y `lineno` como mínimo ([`beancount/core/data.py:508`](../beancount-src/v3.2.3/beancount/core/data.py#L508)). De ahí sale la ubicación que muestran los errores.

## Gramática y generación del analizador

El lenguaje se define en dos archivos fuente:

- [`beancount/parser/lexer.l`](../beancount-src/v3.2.3/beancount/parser/lexer.l) (Flex): por ejemplo, las palabras clave están en [`beancount/parser/lexer.l:246`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L246) y las monedas en [`beancount/parser/lexer.l:203`](../beancount-src/v3.2.3/beancount/parser/lexer.l#L203).
- [`beancount/parser/grammar.y`](../beancount-src/v3.2.3/beancount/parser/grammar.y) (Bison): la regla inicial es [`beancount/parser/grammar.y:895`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L895).

El analizador C no construye objetos por sí mismo: cada regla llama a un método del `Builder` de Python mediante la macro `BUILDY` ([`beancount/parser/grammar.y:72`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L72)). Tras un error de sintaxis, la regla `declarations error` lo absorbe y el análisis continúa ([`beancount/parser/grammar.y:870`](../beancount-src/v3.2.3/beancount/parser/grammar.y#L870)).

## Ejemplo comentado

Este bloque, tal como aparece aquí, se extrajo del documento y se comprobó con `bean-check` de la v3.2.3: código de salida 0 y sin errores. Beancount usa `;` para comentarios.

```beancount
; Opciones del libro.
option "title" "Ejemplo comentado"                   ; Título del libro
option "operating_currency" "PEN"                    ; Moneda principal

2026-01-01 commodity PEN                             ; Declara la moneda
2026-01-01 open Assets:Banco:Corriente  PEN          ; Cuenta restringida a PEN
2026-01-01 open Assets:Inversiones      HOOL "FIFO"  ; Solo HOOL; ventas por FIFO
2026-01-01 open Income:Salario          PEN          ; Los ingresos van en negativo
2026-01-01 open Income:Ganancias        PEN
2026-01-01 open Expenses:Comida         PEN
2026-01-01 open Equity:Apertura         PEN          ; Contrapartida del saldo inicial

; pad genera el movimiento necesario para que el balance siguiente se cumpla.
2026-01-01 pad Assets:Banco:Corriente Equity:Apertura
2026-01-02 balance Assets:Banco:Corriente  1000.00 PEN

; * = confirmada. Beneficiario y descripción, etiqueta (#) y enlace (^).
2026-01-15 * "Empresa SAC" "Sueldo de enero" #sueldo ^boleta-01
  Assets:Banco:Corriente   3000.00 PEN
  Income:Salario                                     ; Sin importe: se calcula (-3000)

; ! = pendiente de revisar. Con un metadato en la línea siguiente.
2026-01-20 ! "Mercado" "Compra semanal"
  ref: "ticket-123"
  Expenses:Comida           150.00 PEN
  Assets:Banco:Corriente                             ; Se calcula (-150)

; Las llaves indican el costo por unidad: crea un lote de 10 acciones.
2026-02-01 * "Compra de acciones"
  Assets:Inversiones        10 HOOL {100.00 PEN}
  Assets:Banco:Corriente  -1000.00 PEN

2026-03-01 price HOOL  120.00 PEN                    ; Precio de mercado

; {} = busca el lote; @ = precio de venta. La ganancia se calcula (-80).
2026-03-02 * "Venta parcial"
  Assets:Inversiones        -4 HOOL {} @ 120.00 PEN
  Assets:Banco:Corriente   480.00 PEN
  Income:Ganancias

2026-03-03 note Assets:Banco:Corriente "Llamé al banco"
2026-03-04 event "ciudad" "Lima"
; 1000 + 3000 - 150 - 1000 + 480 = 3330
2026-03-31 balance Assets:Banco:Corriente  3330.00 PEN
```

Resultado observado al cargarlo: 18 entradas y 0 errores. El `pad` generó una transacción de 1000.00 PEN con bandera `P`; el posting `Income:Ganancias` quedó en -80.00 PEN; y la venta resolvió el lote `{}` al costo de 100.00 PEN con fecha 2026-02-01.
