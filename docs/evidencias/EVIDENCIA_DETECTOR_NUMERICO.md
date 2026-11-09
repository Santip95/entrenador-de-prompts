# Ampliación acotada: secuencias numéricas exactas

Fecha: **8/11/2026, Córdoba (UTC−03)**; los reportes usan UTC y parte de sus fechas corresponden al 9/11Z. Base de código **94dc572**. Motor **1.1.0**; detector **secuencia_numerica_7_8_10_v1**, tipo público **secuencia_numerica**. Solicitud explícita de Santiago, decisión técnica D36; no requisito atribuido a la profesora ni cambio del documento académico.

## Implementación y publicación

Patrón fijo: `(?<![0-9])(?:[0-9]{10}|[0-9]{8}|[0-9]{7})(?![0-9])`. Sólo dígitos ASCII; alternativas exactas, sin nueve ni coincidencias parciales en un tramo mayor. Cuenta ceros iniciales, no elimina separadores ni une fragmentos. Los tramos se interpretan como secuencias consecutivas de dígitos, sin exigir límites de palabra ni etiquetas. No es un validador DNI/teléfono, ni identifica personas. Puede marcar identificadores ficticios o números inocuos; conserva el aviso sobre cobertura incompleta.

Los tres patrones previos, filtros y mensajes permanecen intactos. Se ejecutan primero en su orden configurado; únicamente sus coincidencias aceptadas cubren intervalos internos. Se omite una coincidencia **genérica** completamente contenida en un intervalo ya cubierto del mismo campo. No se eliminan, fusionan ni modifican alertas anteriores. El orden de configuración no puede hacer que el detector nuevo gane prioridad. Apariciones distintas y campos distintos conservan su multiplicidad; en libre no se cambia el escaneo existente de texto y declaraciones. Spans y valores se usan sólo en memoria; no se añaden al reporte público, logs o tablas de alertas.

Se mantiene el circuito objetivo/guiado/libre/componentes no aplicables, token firmado, confirmación individual, recálculo al guardar, transacción e historial. La alerta nueva explica posible información sensible sin afirmar DNI o teléfono. El panel ofrece el detector permitido; no admite regex arbitrarias. API y fórmula de indicadores no cambian.

**Publicación real en entrenador_prompts a 9/11 01:10:27Z =8/11 22:10:27 Córdoba:** C6 **v2**, cuatro detectores activos: correo, teléfono, documento y secuencia numérica. Mensajes y configuración anterior copiados sin cambios, nueva regla inmutable y publicación atómica con el servicio administrativo/lock vigentes. Actor nulo identifica intervención técnica con credencial de migración, sin crear ni elevar cuentas. Repetir el comando recuperó la misma v2 sin insertar ni republicar. C6 v1 se conserva inactiva. No se modificaron otras reglas/desafíos.

Huella agregada SHA-256 calculada en PostgreSQL antes/después, sin sacar contenidos ni hashes de prompts al informe: **práctica 9, versiones 4, evaluaciones 4, resultados 24, alertas 0**, igualdad exacta de cada tabla. No se recalculó ni sobrescribió historial. La firma incorpora motor/regla/configuración; entre configuraciones distintas se informa no comparabilidad, sin mejora injustificada. No se modifica la tarea diaria ni se acredita su disparador futuro. NF-02 continúa pendiente/no aprobado, antivirus sin cambios.

El registro permitido en seeds incluye el nuevo detector y motor 1.1.0; **las seis reglas iniciales v1 y sus mensajes siguen intactos** para conservar fixtures/configuraciones históricas y la precarga idempotente. La activación usa un comando explícito versionado después de seeds; no depende de editar una fila previa. El comando rechaza desafíos con lista explícita de detectores para no reescribir su configuración silenciosamente; no hubo ese bloqueo en desarrollo. No hace falta migración de esquema ni dependencias nuevas.

## Comprobaciones reales

| Comprobación | Resultado |
|---|---|
| Pruebas nuevas dirigidas | **41 aprobadas**: 38 puras y 3 de API/PostgreSQL; 5,65 s. |
| Regresión completa final | **358 aprobadas, 0 fallidas, 0 omitidas, 98,63 s**, fuera del sandbox para el acceso age a claves ficticias protegidas. |
| Corpus original | **33/33**, esperado intacto, ejecutado con motor 1.1.0 y configuración histórica C6 v1; incluidos límites CP-25/27/28. No significa que la configuración nueva reproduzca sus negativos históricos de números sin etiqueta. |
| Frontend | `tsc -b` y Vite aprobados; 19 módulos, 324 ms. |
| Navegador real | Chrome 156.0.8078.80 contra API/PostgreSQL de pruebas: publicación desde panel, confirmación preventiva del objetivo, rechazo del botón sin confirmar y versión guardada con avisos. Dos genéricas (objetivo y tarea) + una DNI, **sin genérica duplicada sobre DNI**. |
| API guiado y libre | V1 anterior a publicación preservada; revisión antigua rechazada 409, guardar sin confirmar 409 sin versión adicional; nueva revisión/confirmación guarda V2, C6 cumple con avisos conservados; comparación entre reglas distintas no comparable. |
| Objetivo | Sin confirmación 409 y ninguna práctica persistida; confirmación exacta permite crear. |
| Activación local | Publicación real v2 y segunda ejecución idempotente; historial agregado idéntico y cuatro detectores activos comprobados. |

Positivos: `1234567`, `12345678`, `1234567890`, `0123456`, ceros de 7/8/10 posiciones. Negativos exclusivos del nuevo detector: `123456`, `123456789`, `12345678901`, `2026`, `12.345.678`, `1234 5678`, fragmentos con guion, tramo de 1000 dígitos y dígitos no ASCII. Etiquetas/formato pueden seguir activando los detectores antiguos: por ejemplo `tel 123456789` conserva teléfono y `documento 12.345.678` conserva documento. Pruebas con detector nuevo primero/último conservan exactamente alertas y huellas anteriores, con binding ficticio fijo.

## Comandos ejecutados y reportes

Desde backend con `..\.venv\Scripts\python.exe`:

```powershell
& ..\.venv\Scripts\python.exe -m pytest tests/motor/test_numeric_detector.py tests/access/test_numeric_integration.py -q --tb=short
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\detector-numerico-regresion.xml
& ..\.venv\Scripts\python.exe -m pytest tests/operations/test_backups.py::test_real_encrypted_restore_completed_pending_deletions_and_contingency tests/operations/test_configuration_archive.py::test_configuration_encrypted_roundtrip_and_no_overwrite tests/operations/test_stage06.py::test_int05_complete_objective_confirmation_delete_backup_restore -q --tb=short --junitxml=..\local-data\detector-numerico-operacion-repeticion.xml
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\detector-numerico-regresion-final.xml
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor --json
& ..\.venv\Scripts\python.exe -m app.scripts.enable_numeric_detector --entorno desarrollo
```

Desde frontend: `npm.cmd run build` (ejecutable de Program Files). Desde raíz: `& .\.venv\Scripts\python.exe scripts\check_numeric_browser.py`. Activación ejecutada dos veces por un auxiliar local que compara las tablas antes/después. Evidencia ignorada: JUnit anteriores y `local-data/detector-numerico/activacion-local.json`, `navegador-*.json`. Sin cuerpos HTTP, HAR, contraseñas, cookies o tokens en reportes.

Incidencias conservadas: primera colección de pruebas falló por nombres de módulo repetidos entre carpetas; se renombró el archivo nuevo de integración, sin tocar expectativas. Primera regresión: **355 aprobadas, 3 fallidas**, 88,16 s, en descifrado age de operación/configuración; esas tres pasaron al repetir fuera del sandbox (**18,78 s**) sin cambiar ACL/antivirus. Se repitió toda la suite en ese contexto para obtener el resultado final. Primer intento de navegador rechazado antes de actuar por puertos de pruebas ocupados por la prueba de contingencia; se ejecutó después secuencialmente y pasó. Consulta inicial de huella agregada suponía id en resultado; abortó antes de publicar; se corrigió sólo el auxiliar local a orden por fila JSON y la activación posterior pasó. Ninguna expectativa de fixtures modificada. Advertencia Starlette/httpx preexistente conservada, sin cambios de dependencias.

## Cómo comprobar desde la pantalla

1. Reiniciar la API si estaba abierta antes de cambiar el código; se necesita cargar motor 1.1.0. Desde raíz, en su terminal: Ctrl+C, `Push-Location .\backend` si aún está en raíz, y `& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers`. No iniciar un segundo servidor sobre 8000 ni detener procesos ajenos. Frontend en otra terminal: `Push-Location .\frontend`; `& "$env:ProgramFiles\nodejs\npm.cmd" run dev`. Abrir 127.0.0.1:5173 y recargar. La regla ya está publicada en desarrollo; no repetir seeds para activarla.
2. Con usuario propio, comenzar una práctica nueva y poner `Objetivo ficticio 0123456` como objetivo. Revisar: aparecerá «Secuencia numérica (posible información sensible)»; continuar exige revisar/confirmar la coincidencia.
3. En Tarea escribir `Ejemplo ficticio 12345678; DNI 12345678`. Revisar: una genérica por el número aislado y una documento por el DNI; además reaparece la revisión del objetivo, como prevé el contrato. Sin confirmación individual no se habilita guardar. Confirmarlas y guardar; avisos permanecen visibles y no se presenta el porcentaje como calidad/seguridad.
4. En otra revisión probar los negativos sin objetivo numérico previo. Sólo los tramos exactos producen la nueva alerta; una alerta anterior puede seguir apareciendo según su detector. En libre confirmar componentes y repetir con un tramo exacto en Texto libre.
5. Administrador → Reglas: C6 v2 activa con el cuarto detector; crear versión desde C6 muestra su casilla. No publicar otra versión sólo para comprobarla. Las evaluaciones antiguas conservan su texto, configuración y versión del motor.

Para otra instalación, después de migraciones y seeds, desde backend ejecutar `& ..\.venv\Scripts\python.exe -m app.scripts.enable_numeric_detector --entorno desarrollo`. No publica ni despliega en Internet. La base de pruebas conserva su configuración de referencia; los tests de incremento publican/restauran sólo su catálogo ficticio. No se declara revisión manual de Santiago de esta función, ni NF-02 resuelto.
