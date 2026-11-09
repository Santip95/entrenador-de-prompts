> Guía técnica conservada del desarrollo. Las observaciones sobre el «equipo actual» corresponden al entorno original. Para una instalación nueva, comenzar por [INSTALACION_WINDOWS.md](../INSTALACION_WINDOWS.md). Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

**Disparador diario comprobado el 9/11/2026:** 107→100/200→201/102, misma instancia, resultado 0; XML intacto y próxima 10/11 02:00 Córdoba. Copia de 02:00:08 autenticada/descifrada según reporte existente, sin restauración SQL. No acredita continuidad, B2, custodia externa ni NF-02. Evidencia en [EVIDENCIA_DISPARADOR_DIARIO_20261109.md](../evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md). Las notas anteriores de preparación se conservan como históricas.

**Ensayo sin sesión del 8/11 aprobado:** intervalo confirmado por Santiago 16:08–16:27 Córdoba; tarea 16:17:52 resultado 0 y copia 16:17:53 autenticada/SHA-256/descifrada nuevamente por Codex. No acredita disparador diario, restauración SQL de esa copia ni B2. Retiro temporal confirmado por Santiago y verificado por Codex: ausente, diaria Ready/habilitada e idéntico XML, próxima 9/11 a las 02:00 Córdoba. Ver docs/evidencias/EVIDENCIA_ETAPA06.md.

**Seguimiento 8/11/2026:** ejecución 09:35:22 resultado 0, copia autenticada/SHA-256/descifrado completo verificados. Arranque 09:26:35 y StartWhenAvailable=true compatibles con diferida, sin evento de disparador (historial deshabilitado). Ensayo sin sesión preparado, no realizado. Guía en docs/operacion/ETAPA06_WINDOWS.md; la nota del 7/11 debajo es histórica.

# Operación y contingencias

**Actualización etapa 06:** tarea instalada por Santiago y ejecución iniciada desde Task Scheduler comprobada con resultado 0 a 7/11/2026 19:49:54Z; primer disparo diario 8/11 a 02:00 Cordoba todavía no observado. B2 sin habilitar/contactar. Restore local repetido con reaplicación del diario y revocación; paquete cifrado de recuperación de configuración/diario exportado y verificado, identidad privada separada. Custodia offline/transferencia independiente y operación externa siguen pendientes. Guía vigente docs/operacion/ETAPA06_WINDOWS.md; los datos de etapa 05 son históricos.

Esta guía concreta §13 y las correcciones a R5/R6. Etapa 05 incorpora respaldo y restauración **locales aislados** con datos ficticios; evidencia en docs/evidencias/EVIDENCIA_ETAPA05.md y comandos vigentes en docs/operacion/ETAPA05_OPERACION_WINDOWS.md. No acredita despliegue, proveedor externo, custodia offline ni operación continua.

## Entornos y portabilidad

### Desarrollo local en Windows

El desarrollo se ejecuta directamente desde PowerShell: frontend React/Vite por Node.js/npm, API FastAPI por Python dentro de `.venv`, PostgreSQL instalado en Windows y Mailpit como capturador SMTP. No usar WSL, Ubuntu ni Docker para iniciar, migrar, probar o respaldar el entorno local. Las conexiones de desarrollo son exclusivamente `127.0.0.1`: PostgreSQL en el puerto `5432`, Mailpit SMTP en `1025` e interfaz de Mailpit en `8025`.

Los comandos reales de instalación, migraciones, precarga, pruebas y arranque de la etapa 01 están en `README.md`; sus resultados ejecutados están en `docs/evidencias/EVIDENCIA_ETAPA01.md`. El intérprete se invoca directamente dentro de `.venv`, sin requerir Activate.ps1. Si PowerShell bloquea `npm.ps1`, se invoca `npm.cmd`; no se modifica la política de ejecución. El binario de PostgreSQL se puede invocar sin alterar el `PATH`, por ejemplo:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --version
```

La máquina auditada tiene instalaciones 17 y 18. Se comprobó y eligió PostgreSQL 18.6 en `127.0.0.1:5432`; usar `psql`, `pg_dump` y `pg_restore` del mayor 18. No cambiar puertos, servicios ni datos de la instalación 17. Las bases del proyecto ya están creadas y migradas; no repetir su creación en el equipo actual.

Mailpit es una dependencia local de pruebas de correo, no un destino de producción. Una vez instalado, iniciar una instancia limitada al equipo local desde PowerShell:

```powershell
& .\local-data\mailpit\mailpit.exe --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025 --disable-version-check --smtp-disable-rdns --quiet
```

La aplicación usa `SMTP_HOST=127.0.0.1`, `SMTP_PORT=1025` y no requiere autenticación ni STARTTLS en este entorno de prueba. No enviar correos reales desde esa configuración ni registrar el token de recuperación.

Desde etapa 03 se dispone de Mailpit 1.33.0 oficial verificado por `scripts/install_mailpit.py`; el ejecutable y los correos son locales, fuera de Git. Detener con Ctrl+C; no habilitar relay. Las pruebas reutilizan una instancia ya iniciada sin vaciar correos ajenos o inician/detienen su proceso propio. La API arranca con `--no-access-log --no-proxy-headers`. `entrenador_app` ya no es propietario ni tiene DDL/TEMP; Alembic/seeds usan `entrenador_migracion` con una credencial separada. Conservar ese reparto al restaurar. El procedimiento administrativo sólo para instalación nueva está en `docs/historico/ETAPA03_CONFIGURACION_LOCAL.md` y la evidencia en `docs/evidencias/EVIDENCIA_ETAPA03.md`.

### Futuro despliegue y contingencia

En producción, frontend y API se sirven bajo el mismo origen HTTPS, PostgreSQL y SMTP se configuran como servicios administrados o equivalentes, y Backblaze B2 privado recibe respaldos cifrados. El proveedor aún no está contratado ni configurado. Dockerfiles, imágenes fijadas y una configuración de contenedores pueden incorporarse para ese despliegue o para R6 si se decide entonces; no sustituyen las instrucciones locales de Windows. Git conserva código, migraciones y semillas sin secretos. Las variables de DB/SMTP/B2 se inyectan fuera del repositorio y ninguna API de dominio depende del SDK de un proveedor.

## Respaldo y eliminación

Objetivo operativo: cada día a las 02:00 America/Argentina/Cordoba, generar `pg_dump` personalizado, cifrar/verificar y subir al bucket privado cuando esté habilitado y comprobado. El trabajo Windows actual es Python versionado sin secretos, invocado por tarea S4U con ejecutable explícito; las rutas/credenciales locales están fuera de Git. XML validado, trabajo ejecutado una vez directamente, tarea no registrada y B2 no habilitado. Manifiesto técnico autenticado sin datos personales: fecha UTC, origen, versión app/esquema, tamaño y hash. La clave privada de descifrado debe custodiarse aparte del servidor/bucket en despliegue; aquí sólo se comprobó separación local de directorios y ACL. Nunca incluir contraseñas en argumentos ni scripts.

Retener 7 copias diarias y 4 semanales, todas con antigüedad máxima de 30 días. Eliminar las copias mensuales de tres meses que contradicen el plazo de borrado. Aplicar límite a versiones antiguas y cargas incompletas del objeto, no solo a la vista de archivos actuales. Verificar efectividad de la purga al configurar el proveedor.

Objetivos: RPO ≤24 h y RTO ≤4 h. Ensayo mensual aislado: descifrar, `pg_restore`, revisar integridad/esquema y ejecutar lectura/comparación. Las mediciones locales de etapa 05 se registran en su evidencia; no son una garantía continua ni una restauración externa. El procedimiento vigente cifra antes de escribir una copia y sólo restaura en destinos ficticios explícitos. Comandos desde la raíz:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest tests\operations\test_backups.py -q
Pop-Location
```

El auxiliar usa credenciales de migración locales en el entorno privado de sus subprocesos, nunca argumentos. La guía docs/operacion/ETAPA05_OPERACION_WINDOWS.md detalla copia/restore manual ficticios, tarea, retención, ubicación separada de claves/diario y condiciones para reabrir. No sustituir el destino por una base activa ni usar la copia de desarrollo en una prueba destructiva.

Solicitudes de borrado: escribir primero un registro cifrado independiente de la base principal con UUID de práctica/cuenta y fecha, sin textos/correos. El registro se conserva fuera del respaldo que se restaurará. Al restaurar, reaplicar tanto solicitudes completadas como pendientes posteriores a la copia, antes de habilitar lecturas. Purgar marcas cuando hayan expirado todas las copias afectadas. Si no se puede asegurar ese orden, no reabrir con información que pueda haber sido eliminada.

## R5 Exposición o pérdida de datos

| Paso | Acción y evidencia |
|---|---|
| Detectar | Registrar evento, hora, alcance estimado y quién lo investiga; no copiar datos sensibles al ticket. |
| Contener | Suspender escrituras o acceso del componente afectado; desactivar cuentas comprometidas; revocar sesiones y rotar credenciales relacionadas. |
| Preservar | Conservar logs técnicos y manifiestos permitidos en un área restringida para determinar alcance. |
| Recuperar | Si hubo pérdida/corrupción, restaurar la última copia verificada en entorno limpio; aplicar migraciones compatibles y diario de borrados; invalidar sesiones/tokens recuperados. |
| Corregir | Reparar autorización, configuración o proceso causante y ejecutar pruebas de regresión. |
| Cerrar | Reabrir solo con integridad verificada y defecto corregido. Registrar datos recuperados/perdidos y tiempos reales; comunicar a las personas afectadas cuando corresponda según el alcance y obligaciones aplicables. |

La exposición no se resuelve únicamente restaurando una copia. Si se filtró una clave, restaurar datos sin rotarla conserva el incidente.

## R6 Interrupción o costo inviable del proveedor

Disparador: indisponibilidad que amenaza la demostración/continuidad o nueva tarifa fuera del presupuesto autorizado. Responsable: autor en función técnica.

1. Conservar último commit/etiqueta y copia cifrada comprobada; revisar estado del proveedor y registrar incidente/costo comunicado.
2. Ejecutar la aplicación en otro host compatible o en el equipo local como contingencia de demostración. Puede usarse una configuración de contenedores solo si fue creada y verificada para despliegue; en la máquina local la contingencia se ejecuta directamente desde PowerShell. Restaurar PostgreSQL, aplicar borrados, cambiar configuración y secretos, invalidar sesiones y verificar flujo principal.
3. Si se requiere servicio público, seleccionar y presupuestar un proveedor alternativo antes de contratarlo. El agente no debe crear cargos ni cuentas por iniciativa propia.
4. Verificar autenticación, guardado, comparación y recuperación. Registrar tiempo y limitaciones. Una demo local puede permitir mostrar el prototipo, pero no acredita disponibilidad pública.
5. Actualizar instrucciones/enlaces y costos solo después de comprobar el nuevo entorno. Si no hay una alternativa viable, suspender el servicio de forma controlada, conservar respaldos dentro de la retención y documentar la limitación.

## Separación de costos solicitada

| Grupo | Qué registrar |
|---|---|
| Proyecto académico de cuatro meses | Horas de desarrollo/diseño/QA, infraestructura del período y contingencia; no sumar nuevamente esas horas al costo mensual. |
| Hardware | Indicar si la notebook es compra necesaria o valoración de un equipo disponible. Falta confirmar ese dato; no afirmar que hubo un desembolso. |
| Operación posterior por mes | Hosting, PostgreSQL, almacenamiento/transferencias de respaldos, SMTP y dominio si se contratan, y horas efectivas de mantenimiento. |

Usar dos totales: valoración económica y desembolso previsto, cuando exista equipo propio. Registrar moneda, fecha de cotización, impuestos y tipo de cambio de cada presupuesto. Las tarifas de F1 son históricas: confirmar al contratar, sin convertirlas en requisitos técnicos ni precios actuales. Los valores reales pendientes no bloquean la programación local.

## Historial diario y custodia externa — preparación del 8/11

Historial habilitado por Santiago el 8/11 21:58 Córdoba y comprobado activo por Codex, con XML diario idéntico. Disparador del 9/11 02:00 pendiente: pasos y criterios de correlación en docs/operacion/DISPARADOR_DIARIO_WINDOWS.md. No volver a iniciar/reprogramar la tarea para esta comprobación. Guía detallada de material externo, identidad age cifrada separada y verificación sin extraer secretos en docs/operacion/CUSTODIA_RECUPERACION_WINDOWS.md. Custodia/transferencia/recuperación externas y B2 no se consideran realizados por preparar esas instrucciones.
