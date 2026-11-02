# Evaluación de calidad de Beancount 3.2.3 (NTP-ISO/IEC 9126)

Este repositorio contiene la entrega final, la infraestructura reproducible y la documentación del código de Beancount para la evaluación 9126 del curso Calidad de Software (EPIS-UNSA).

**Veredicto: 88,41 % → ACEPTABLE.** Pasan 5 de las 6 subcaracterísticas principales; Operabilidad no pasa (0,7947). 7 de 25 métricas no alcanzan su umbral: 003, 007, 011, 013, 016, 018 y 025.

## Estado actual

| Parte | Estado |
|---|---|
| `setup/` | Operativo: `verify.py` da OK en 3.2.3 y 2.3.6 |
| `documentacion/` | Completo: 13 documentos, diagramas, inventario y scripts |
| [`ENTREGA_FINAL/`](ENTREGA_FINAL/) | Informe (.docx), Excel (.xlsx y .xls), `LEEME_reproducibilidad.md` y `Evidencias_Beancount.zip` |

## Cómo usar el repositorio

**Ejecutar el entorno:**

```powershell
cd setup
.\setup.ps1          # Windows
python verify.py
```

```bash
cd setup
./setup.sh           # Linux/macOS
python3 verify.py
```

Detalles y limitaciones en [setup/README_SETUP.md](setup/README_SETUP.md). En Windows sin compilador, `verify.py` indica el modo `overlay` y excluye dos tests de 2.3.6, que son fallos conocidos de Beancount en esa plataforma.

**Estudiar el código:** abrir [documentacion/README.md](documentacion/README.md).

Las citas de `documentacion/` apuntan a `../beancount-src/`, mientras que el setup lo crea en `setup/beancount-src/`. Para que funcionen, tras el setup, crea un enlace en la raíz del repositorio:

```powershell
New-Item -ItemType Junction -Path beancount-src -Target (Resolve-Path setup\beancount-src)   # Windows
```

```bash
ln -s setup/beancount-src beancount-src                                       # Linux/macOS
```

## Advertencia

No re-medir sin reauditar. Las mediciones se hicieron en Ubuntu 24.04 con Python 3.13, en el entorno que describe `ENTREGA_FINAL/LEEME_reproducibilidad.md`.
