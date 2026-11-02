# Documentación de análisis del código de Beancount

Guía de estudio en español para entender Beancount **v3.2.3** antes de evaluarlo con la NTP-ISO/IEC 9126 (componentes C1 analizador/cargador, C2 núcleo contable y C3 CLI). Se apoya en el código real: las citas son enlaces a `ruta:línea` dentro de `../beancount-src/`.

No contiene métricas ni resultados de la evaluación, que corresponden al paso siguiente.

## Orden de lectura recomendado

1. [00 Resumen ejecutivo](00_resumen_ejecutivo.md) y [10 Glosario](10_glosario.md), para tener a mano el vocabulario.
2. [01 Visión general](01_vision_general.md).
3. [04 Modelo de datos y sintaxis](04_modelo_de_datos_y_sintaxis.md): conviene conocer el lenguaje antes que el código.
4. [02 Arquitectura](02_arquitectura.md) y [05 Flujo de ejecución](05_flujo_de_ejecucion.md): lo más importante del conjunto.
5. [06 Herramientas CLI](06_herramientas_cli.md) y [07 Plugins](07_plugins_y_extensiones.md).
6. [08 Pruebas](08_pruebas_y_calidad_interna.md) y [09 Comparación de versiones](09_comparacion_2_3_6_vs_3_2_3.md).
7. [11 Notas para la evaluación](11_notas_para_evaluacion_9126.md), al preparar el informe.
8. [03 Mapa de módulos](03_mapa_de_modulos.md) y [12 Referencias](12_referencias.md), como consulta.

## Contenido

| Archivo | Descripción |
|---|---|
| [00_resumen_ejecutivo.md](00_resumen_ejecutivo.md) | Qué es, versión exacta, cifras clave y componentes. |
| [01_vision_general.md](01_vision_general.md) | Problema que resuelve, usuarios, flujo típico y ecosistema. |
| [02_arquitectura.md](02_arquitectura.md) | Capas, módulos que las implementan y puntos de entrada. |
| [03_mapa_de_modulos.md](03_mapa_de_modulos.md) | Propósito y dependencias por paquete; tabla de todos los módulos. |
| [04_modelo_de_datos_y_sintaxis.md](04_modelo_de_datos_y_sintaxis.md) | Directivas, tipos, gramática y ejemplo comentado. |
| [05_flujo_de_ejecucion.md](05_flujo_de_ejecucion.md) | Recorrido de `bean-check` paso a paso y dónde provocar errores. |
| [06_herramientas_cli.md](06_herramientas_cli.md) | Cada herramienta: módulo, opciones, ejemplo y componente. |
| [07_plugins_y_extensiones.md](07_plugins_y_extensiones.md) | Sistema de plugins, catálogo y esqueleto de plugin propio. |
| [08_pruebas_y_calidad_interna.md](08_pruebas_y_calidad_interna.md) | Suite de pruebas, recuentos y pruebas omitidas. |
| [09_comparacion_2_3_6_vs_3_2_3.md](09_comparacion_2_3_6_vs_3_2_3.md) | Diferencias de estructura, API, sintaxis y CLI. |
| [10_glosario.md](10_glosario.md) | Términos de contabilidad, de Beancount y de la evaluación. |
| [11_notas_para_evaluacion_9126.md](11_notas_para_evaluacion_9126.md) | Mapa de componentes, puntos de observación y riesgos. |
| [12_referencias.md](12_referencias.md) | Enlaces oficiales y fuentes. |
| [LEEME_generacion.md](LEEME_generacion.md) | Cómo se generó, entorno y comandos para regenerar. |
| [diagramas/arquitectura.mmd](diagramas/arquitectura.mmd) | Capas y relaciones. |
| [diagramas/flujo_parseo.mmd](diagramas/flujo_parseo.mmd) | Flujo completo de `bean-check`. |
| [diagramas/flujo_booking.mmd](diagramas/flujo_booking.mmd) | Algoritmo de booking. |
| [diagramas/dependencias_modulos.mmd](diagramas/dependencias_modulos.mmd) | Dependencias entre paquetes (generado). |
| [inventario/modulos.csv](inventario/modulos.csv) | Todos los `.py` de [`beancount/`](../beancount-src/v3.2.3/beancount/): ruta, LOC, docstring e imports. |
| [inventario/entry_points.csv](inventario/entry_points.csv) | Comandos declarados en el paquete. |
| [inventario/directivas_soportadas.csv](inventario/directivas_soportadas.csv) | Cruce de léxico, gramática, Builder y clase. |
| [inventario/resumen.json](inventario/resumen.json) | Cifras que se citan en los documentos. |
| [scripts/generar_inventario.py](scripts/generar_inventario.py) | Crea los CSV (solo biblioteca estándar). |
| [scripts/generar_dependencias.py](scripts/generar_dependencias.py) | Crea el grafo de dependencias. |
| [scripts/verificar_documentacion.py](scripts/verificar_documentacion.py) | Enlaza las citas y comprueba enlaces y líneas. |

La carpeta `inventario/` incluye además CSV auxiliares (`comparacion_*.csv`, `pruebas_*.csv`, `modulos_2.3.6.csv`, entre otros) que alimentan los documentos 08 y 09.

## Cómo seguir una cita

Las citas como [`beancount/loader.py:89`](../beancount-src/v3.2.3/beancount/loader.py#L89) abren el archivo en esa línea desde la vista previa de Markdown de VS Code (Ctrl+clic). En otro visor, abre la ruta a mano bajo `beancount-src/v3.2.3/`. Las citas con prefijo `v2.3.6:` apuntan a `beancount-src/v2.3.6/`.

## Cómo regenerar

Los inventarios y el grafo de dependencias se regeneran con los comandos de [LEEME_generacion.md](LEEME_generacion.md). El texto de los documentos es redacción manual asistida y **no** se regenera con esos comandos.
