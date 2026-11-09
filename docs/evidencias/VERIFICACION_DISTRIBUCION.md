# Verificación de la distribución limpia

Fecha: **9 de noviembre de 2026**. Distribución: `entrenador-de-prompts`. Esta comprobación corresponde a la preparación del código para compartirlo, no a un despliegue ni a una nueva certificación integral del producto.

## Cambios

- Carpeta raíz renombrada; nombres de bases, roles y directorios privados conservados.
- Dependencias instaladas, ejecutables descargados, configuración privada, reportes locales, cachés e historial Git excluidos.
- Documentación organizada en `docs/`; nuevo README, índice, guía de instalación y guía de pruebas. Evidencias históricas conservadas con sus fechas, resultados y límites.
- Plantilla `.env.example` conservada sin credenciales; `.gitignore` ampliado.
- Prompts antiguos de implementación, contexto de reanudación y manifiesto del paquete original excluidos de esta copia.

El código de la aplicación, frontend, migraciones, seeds, fixtures y archivos de dependencias conserva sus bytes originales. Dos archivos Python auxiliares tienen ajustes acotados:

1. `scripts/report_stage06.py`: referencias documentales y ruta de salida adaptadas a `docs/evidencias/`. No se ejecutó para reescribir resultados históricos.
2. `backend/tests/motor/test_contract.py`: SQLAlchemy se importa antes de bloquear E/S en `test_evaluate_works_when_io_is_forbidden`. Evita que la importación de `ssl/asyncio` ocurra cuando `socket.socket` ya está sustituido por la función que rechaza E/S. Conserva el bloqueo y la expectativa del motor. No se cambiaron casos esperados ni lógica de la aplicación.

## Comprobaciones de esta copia

| Control | Resultado |
|---|---|
| Corpus del motor 1.1.0 | **33/33** aprobados con la configuración histórica de fixtures. |
| Suite `tests/motor` | **158 aprobadas**, 0 fallidas, 0 omitidas; incluye el detector numérico. |
| Sintaxis Python | 89 archivos analizados. |
| JSON y dependencias del frontend | JSON válidos; dependencias directas y versiones coherentes con el lock. |
| Rutas documentales | Enlaces locales y rutas explícitas revisados después de reorganizar. |
| Exclusiones Git | 11 rutas de ejemplo privadas/regenerables ignoradas; archivos de la distribución admitidos. |
| Secretos conocidos | 5 valores privados del `.env` original contrastados en memoria con la copia; ninguna coincidencia. No se guardaron sus valores en este informe. |
| Rutas personales y claves privadas | Sin rutas personales de Windows ni firmas de claves privadas en los archivos de la copia. |

Las pruebas se ejecutaron en Linux con Python **3.12.14**, utilizando para esta verificación las dependencias Python necesarias del ZIP original en una carpeta temporal separada. Esas dependencias no forman parte de la distribución. Los comandos de comprobación equivalen a `python -m pytest tests/motor -q --tb=short` y `python -m app.scripts.check_motor`, desde `backend/`.

Antes de completar la preparación de dependencias de verificación, pytest no pudo iniciar por faltar el módulo auxiliar `py`. Luego hubo 157 pruebas aprobadas y una fallida: primero por ausencia de SQLAlchemy en esa carpeta temporal y después por su importación tardía bajo el bloqueo de `socket`. Se completaron las dependencias y se corrigió el orden de preparación descrito arriba; la ejecución final aprobó las 158 pruebas. No se eliminaron pruebas ni se cambiaron expectativas para obtener ese resultado.

No se repitieron aquí la regresión completa de 358 pruebas, el build del frontend, los navegadores reales, PostgreSQL, la instalación de Windows ni los respaldos programados. Sus resultados anteriores se conservan como evidencia del entorno original. El control de secretos sólo cubre los valores disponibles y los patrones revisados; no es una auditoría exhaustiva.

## Pendientes conservados

NF-02 sigue sin aprobar. La operación real de B2, la custodia externa de claves, la revisión externa de reglas y la validación educativa siguen pendientes. La limpieza no cambia estos estados.

No se modificaron bases, claves, tareas ni archivos de la instalación original. Tampoco se publicó o desplegó esta distribución.
