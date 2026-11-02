# Reproducibilidad de la evaluación de calidad de Beancount

Este documento explica cómo repetir cada medición del informe *Informe_Evaluación_Calidad_Software_EPIS_CS_Beancount_v1_0.docx*.
Las evidencias originales (scripts, libros de prueba, registros crudos y JSON de resultados) están en `Evidencias_Beancount.zip`.

## 1. Producto evaluado

| Elemento | Valor |
|---|---|
| Producto | Beancount 3.2.3 (última versión estable en PyPI y en GitHub al 2026-10-29) |
| Repositorio | https://github.com/beancount/beancount |
| Tag / commit evaluado | `3.2.3` / `eeda2aa2a3204ffb980dab11220b2abde5e80b38` (2026-05-05) |
| Distribución | wheel `beancount-3.2.3-cp313-cp313-manylinux2014_x86_64` (PyPI) + `beanquery==0.2.0` |
| Versión de comparación | Beancount 2.3.6 (sdist de PyPI, Python 3.11) para las métricas 004, 024 y 025 |
| Sistema operativo | Ubuntu 24.04.5 LTS, kernel Linux 6.18, x86_64; máquina virtual de 2 vCPU y 7 GiB de RAM |
| Python | 3.13.18 (principal); 3.11 y 3.12 en la métrica 023 |

## 2. Preparar el entorno

```bash
# Código fuente (para la suite de pruebas y las mutaciones de la métrica 021)
git clone https://github.com/beancount/beancount ext/beancount
git -C ext/beancount worktree add ../../bc-3.2.3 3.2.3

# Beancount 3.2.3 (evaluado)
python3.13 -m venv venv-bc3
venv-bc3/bin/pip install beancount==3.2.3 beanquery==0.2.0 pytest

# Beancount 2.3.6 (comparación)
python3.11 -m venv venv-bc2
venv-bc2/bin/pip install beancount==2.3.6

# Árbol fuente del tag con la extensión C del wheel (suite oficial, métricas 009/010/021/022)
cp -r bc-3.2.3 run-src && rm -f run-src/.git
cp venv-bc3/lib/python3.13/site-packages/beancount/parser/_parser*.so run-src/beancount/parser/
```

Los scripts asumen las rutas `/home/claude/{venv-bc3,venv-bc2,run-src,eval}`; para otra ubicación se cambian las constantes de `eval/scripts/comun.py` y `SRC` en `m_resto.py`.

## 3. Libros de prueba

| Archivo | Cómo se genera | SHA-256 (16 primeros) |
|---|---|---|
| `example.beancount` (1 552 tx, 2022–2026) | `bean-example --seed 42 --date-begin 2022-01-01 --date-end 2026-01-01` | fcd83b562e3b0152 |
| `sint_101/202/303.beancount` + `.oraculo.json` | `python gen_ledger.py SEMILLA 3000 salida.beancount oraculo.json` (semillas 101, 202 y 303) | 0df5bbc9… / e07660a1… / 8b79a192… |
| `grande_100k.beancount` + oráculo | `python gen_ledger.py 999 100000 ...` | 6c815edcc2efef74 |

`gen_ledger.py` no usa Beancount: calcula los saldos esperados con `decimal.Decimal` y un booking FIFO propio (oráculo independiente).

## 4. Protocolo

Los umbrales de las 25 métricas se fijaron antes de medir: ver `logs/00_protocolo_registrado.txt` (sello 2026-10-29T03:09:44-05:00, incluye el SHA-256 del catálogo usado). Después de medir solo se corrigieron descripciones de método (métricas 016, 021 y 023) para reflejar lo ejecutado; ningún umbral cambió.

## 5. Ejecutar las mediciones

```bash
cd eval/scripts
python3 m_func.py m001 m002 m003 m004 m005 m006_007      # Funcionalidad (006/007 tarda ~15 min)
python3 -c "import m_func; m_func.m006_obsoleta_ns()"     # repetición del caso de caché obsoleta (mtime en ns)
# Suite oficial (009/010): desde el árbol del tag
(cd ../../run-src && PYTHONPATH=$PWD ../venv-bc3/bin/python -m pytest beancount -p no:cacheprovider -q -rs \
   --junitxml=../eval/logs/raw/009_010/pytest_fuente.xml)
python3 m_fiab.py m008 m009_010 m011 m012 m013           # Fiabilidad
python3 m_resto.py m014 m015 m016 m019 m020 m022 m023 m024 m025
python3 m_resto.py m017 m021                             # tiempos: ejecutar con la máquina sin otra carga
python3 m_resto.py m018                                  # peor caso: ~20 min
python3 calcular.py                                      # out/resultados.json
python3 textos.py && python3 build_excel.py X.xlsx && python3 build_docx.py X.docx
```

Cada caso deja `logs/raw/<métrica>/<caso>.txt` (comando exacto, código de salida, duración, stdout y stderr) y cada métrica deja `out/<métrica>.json` (esperado, observado, conteo).

## 6. Comando y evidencia por métrica

| Métrica | Función | Qué ejecuta | Evidencia |
|---|---|---|---|
| 001 Precisión esperada | `m_func.m001` | 21 casos con resultado documentado (include, pushtag, expresiones, booking, pad, tolerancias, bean-query, bean-format) | `logs/raw/001/` |
| 002 Exactitud de cálculo | `m_func.m002` | 30 expresiones vs `Decimal`; saldos de 3 libros vs oráculo; bean-query vs oráculo | `logs/raw/002/` |
| 003 Precisión | `m_func.m003` | números de 8–20 dígitos, 0.1+0.2, presentación de bean-query | `logs/raw/003/` |
| 004 Intercambiabilidad | `m_func.m004` | printer, Beancount 2.3.6, CSV, `-f beancount` PRINT, `--json`, bean-format | `logs/raw/004/` |
| 005 Control de operaciones ilegales | `m_func.m005` | 15 tipos × (API + bean-check) | `logs/raw/005/` |
| 006/007 Corrupción de datos | `m_func.m006_007`, `m006_obsoleta_ns` | herramientas de lectura, SIGKILL, caché corrupta/obsoleta, concurrencia, solo lectura, CRLF, plugins | `logs/raw/006_007/` |
| 008 Densidad de fallas | `m_fiab.m008` | 23 libros válidos × 5 operaciones | `logs/raw/008/` |
| 009/010 Cobertura y madurez de prueba | pytest + `m_fiab.m009_010` | suite oficial (JUnit XML) | `logs/raw/009_010/` |
| 011 Prevención de caídas | `m_fiab.m011` | 28 entradas defectuosas | `logs/raw/011/` |
| 012 Prevención de fallas | `m_fiab.m012` | 10 errores insertados + 3 casos de CLI | `logs/raw/012/` |
| 013 Operación incorrecta | `m_fiab.m013` | 21 usos incorrectos | `logs/raw/013/` |
| 014 Consistencia operacional | `m_resto.m014` | lista de verificación de 38 elementos | `logs/raw/014/` |
| 015 Mensajes autoexplicativos | `m_resto.m015` | 36 condiciones de error (criterio del evaluador, validar por el grupo) | `out/015.json` |
| 016 Recuperabilidad de error operacional | `m_resto.m016` | 7 operaciones de riesgo | `logs/raw/016/` |
| 017 Tiempo medio | `m_resto.m017` | 10 × (parse, bean-check -C, bean-query) sobre el ejemplo | `logs/raw/017/` |
| 018 Peor caso | `m_resto.m018` | 5 × lo mismo sobre 100 000 tx, sin caché | `logs/raw/018/` |
| 019 Modificabilidad parametrizada | `m_resto.m019` | 14 opciones, plugins y flags | `logs/raw/019/` |
| 020 Pruebas incorporadas | `m_resto.m020` | 17 oportunidades de prueba | `logs/raw/020/` |
| 021 Eficiencia de pruebas tras corrección | `m_resto.m021` | 6 mutaciones de código + 5 errores del libro | `logs/raw/021/` |
| 022 Reanudar la prueba | `m_resto.m022` | 9 puntos de pausa/reanudación | `logs/raw/022/` |
| 023 Reinstalación | `m_resto.m023` | 7 escenarios pip/uv × prueba de humo por componente | `logs/raw/023/` |
| 024 Uso continuo de los datos | `m_resto.m024` | 8 libros válidos en 2.3.6 leídos por 3.2.3 | `logs/raw/024/` |
| 025 Inclusividad de funciones | `m_resto.m025` | 13 herramientas, 14 API y 30 complementos de 2.3.6 | `logs/raw/025/` |

## 7. Notas de reproducción

* Los tiempos (017, 018, 021) dependen del hardware; se midieron en la VM descrita con la otra vCPU parcialmente ocupada por la generación de documentos durante 018.
* 006/007: el caso de caché obsoleta requiere restaurar la fecha con `os.utime(..., ns=...)`; con precisión de segundos Beancount detecta el cambio (`st_mtime_ns`) y el caso no se reproduce. La primera versión del caso se descartó por ese motivo y queda registrada.
* 009/010: desde el paquete instalado 2 pruebas fallan porque buscan la raíz del repositorio (`test_utils.find_repository_root`); por eso la ejecución oficial es desde el árbol del tag (`logs/raw/009_010/pytest_instalado.log` conserva la otra ejecución).
* 024: los libros generados por `bean-example` 2.3.6 con rangos que cruzan varios fines de año presentan errores en la propia 2.3.6; se usó el rango 2024-01-01 a 2026-10-29, válido en 2.3.6.
* 021/022 modifican temporalmente `run-src` (mutaciones) y lo restauran; se desactiva el bytecode (`PYTHONDONTWRITEBYTECODE=1` y borrado de `__pycache__`) para evitar `.pyc` obsoletos.
