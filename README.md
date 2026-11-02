# Evaluación de calidad de Beancount 3.2.3 (NTP-ISO/IEC 9126)

Este repositorio contiene la infraestructura reproducible y la documentación del código de Beancount para la evaluación 9126 del curso Calidad de Software (EPIS-UNSA). **La ENTREGA_FINAL (informe, Excel, evidencias y LEEMEs) aún no está incorporada.**

## Estado actual

| Parte | Estado |
|---|---|
| `setup/` | Operativo: `verify.py` da OK en 3.2.3 y 2.3.6 |
| `documentacion/` | Completo: 13 documentos, diagramas, inventario y scripts |
| ENTREGA_FINAL | Pendiente: ver [PENDIENTE_ENTREGA_FINAL.md](PENDIENTE_ENTREGA_FINAL.md) |

El informe se generó en una sesión y máquina separadas, y no se localizó al hacer el push. Se subirá en un commit posterior.

## Qué se puede hacer ya

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

## Veredicto del análisis (referencia)

**88,41 % → ACEPTABLE.** Pasan 5 subcaracterísticas principales; Operabilidad no pasa (0,7947). Estas cifras proceden del informe, que todavía no está en este repositorio.

## Advertencia

No re-medir sin reauditar. Cuando se añada ENTREGA_FINAL, el commit debe ser `Add ENTREGA_FINAL v1.0`.
