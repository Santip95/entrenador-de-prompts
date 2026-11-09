> Documento histórico. Conserva decisiones y comprobaciones de su etapa; para instalar esta versión, seguir [la guía vigente](../INSTALACION_WINDOWS.md). Los prompts y el manifiesto del paquete original no se incluyen en esta distribución. Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Registro de implementación

## Disparo diario del 9/11/2026 — comprobado

Lectura de registros existentes: evento 107 de horario a **02:00:01.8375713 Córdoba**, seguido de 100/200/201/102 para la misma instancia {bcaabcf6-f442-4948-bcd6-2851a1bf8690}; acción completada con resultado **0** a 02:00:09.4643375. XML completo idéntico a la referencia del 8/11; tarea Ready/habilitada, intervalo diario y próxima **10/11 a las 02:00 Córdoba**. Sin inicio manual ni cambios de tarea/configuración/antivirus.

Copia de **02:00:08.436255**, 54555 bytes, esquema 0004: reporte existente del verificador de Santiago acredita autenticidad/SHA-256/descifrado completo. Codex leyó ese reporte, el estado del trabajo y volvió a autenticar el manifiesto/comprobar tamaño y hash, sin descifrar de nuevo, generar respaldo o restaurar SQL. Tres retenidas/cero purgadas y B2=false. Se aprueba este disparo automático concreto; no continuidad/RPO/RTO, sesión cerrada de hoy ni restauración SQL de esa copia. B2, custodia externa y NF-02 conservan sus pendientes separados. Detalle y RecordIds en docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md.

## Incremento D36 — secuencias numéricas, 8/11/2026

Motor **1.1.0**, nuevo detector fijo secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, sin normalizar separadores ni subcoincidencias de tramos mayores. Patrones/filtros/mensajes previos y fórmulas intactos; se omite sólo la genérica contenida en una alerta previa aceptada. Panel y presentación en español incorporados; mismas rutas de objetivo, guiado/libre, revisión/confirmación y guardado. **C6 v2 publicada realmente en desarrollo**, idempotente y con los cuatro detectores activos. Huella agregada antes/después de prácticas/versiones/evaluaciones/resultados/alertas idéntica; sin recalcular historia.

**358 pytest aprobadas, 0 fallidas, 0 omitidas, 98,63 s** (317 previas +41 nuevas); corpus histórico 33/33 sin cambiar esperados; TypeScript/build aprobados. Chrome real: publicar desde panel, objetivo no persistido antes de confirmar, guardado con dos genéricas en campos distintos y una DNI sin genérica superpuesta, avisos conservados. API/PostgreSQL cubren guiado/libre, tokens viejos, falta de confirmación, historia inmutable y no comparabilidad tras publicación. Incidencias iniciales y repeticiones conservadas en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md; no se presentan como ejecuciones aprobadas iniciales.

Reiniciar la API que estuviera abierta antes del cambio para cargar 1.1.0 y recargar frontend. No se reiniciaron procesos ajenos ni se cambiaron claves, roles, dependencias, esquema, antivirus, tarea diaria o documento académico. **NF-02 continúa pendiente/no aprobado**; disparador diario y custodia conservan su estado. No se declara revisión manual de Santiago del detector ni validación externa. Guía de pantalla y activación de instalaciones nuevas en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. Sin publicación/despliegue externo.

## Preparación del disparador diario y custodia — 8/11/2026

Santiago habilitó Microsoft-Windows-TaskScheduler/Operational mediante el auxiliar en PowerShell elevada a **8/11 21:58:10 Córdoba =9/11 00:58:10Z**. Se conserva la denegación inicial de Windows desde Codex como incidencia resuelta con intervención local, no como rechazo de aprobación automática. Comprobación independiente de Codex a 00:59:59Z: historial activo, tarea Ready/habilitada y XML completo idéntico a la referencia. Próxima 9/11 02:00 −03, intervalo de un día, StartWhenAvailable=true y WakeToRun=false. No se modificaron programación, acciones, principal, políticas, tamaño/retención del canal ni se ejecutó la diaria.

Consulta del auxiliar a **9/11 01:00:25Z =8/11 22:00:25 Córdoba**: cero eventos del día 9/11 local, esperado antes del horario. **Disparador diario pendiente**: correlacionar tarea e instancia en 107/100/200/201/102, diferenciar 110, resultado del trabajo y copia nueva. No habilitación retroactiva ni aprobación por LastTaskResult anterior. El canal incluye todas las tareas del equipo; el informe guarda sólo la diaria y campos permitidos sin mensajes completos/usuarios. Evidencia ignorada en local-data/etapa06/disparador-diario-preparacion.json, disparador-diario-preparacion-comprobada.json y disparador-diario-consulta-*.json. Instrucciones exactas en docs/operacion/DISPARADOR_DIARIO_WINDOWS.md.

Custodia externa revisada en código de exportación/verificación/extracción, diario bajo bloqueo y verificación/restauración de respaldos. Guía docs/operacion/CUSTODIA_RECUPERACION_WINDOWS.md: conservar conjuntos backup.age/manifest.json/manifest.auth completos, paquete cifrado actualizado con local.env/diario/clave/ancla, identidad privada age protegida y separada, código/locks/guías e inventario sin secretos. Diario vigente después de borrados, no sólo snapshot antiguo. Clave original sin frase requiere protección adicional antes de transportarla; age admite identidad cifrada por frase para verificar copias externas a NUL sin mostrar contenido. Comandos revisados en documentación oficial; **transferencia, custodia efectiva, uso de clave externa y recuperación de otro equipo no ejecutados ni aprobados**. No se copiaron claves/paquetes a un destino externo ni se tocó desarrollo/B2.

Comprobaciones de este incremento: parser PowerShell aprobado; preparación ejecutada por Santiago y contrastada por Codex; consulta real del intervalo futuro sin eventos ejecutada correctamente. Procesamiento de una instancia diaria nueva aún no ejercitado, sin inventar eventos. No se repiten las 317 pruebas ni el build porque no cambió la aplicación. Matriz y MANIFEST actualizados; secretos e índice revisados antes del commit. Fuentes de comandos: [Microsoft wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil), manifiesto local Microsoft-Windows-TaskScheduler y [age oficial](https://github.com/FiloSottile/age#usage).

## Contraste de NF-02 — 8/11/2026, posterior a los ensayos de respaldo

Observación manual de Santiago con PRUEBA_NF02_ABC123: tres coincidencias locales en 5173; petición inspeccionada Ping/TimerCallback. Archivo histórico flujo-auditoria.json, solicitud externa índice 14: POST XHR a gc.kis.v2.scr.kaspersky-labs.com, 3517 bytes, AsyncCall/Call y dos coincidencias de campo fuente texto 45/34. **No se registraron ruta, requestId, hora, acción ni campo del cuerpo remoto.** Longitudes compatibles con Tarea/Contexto de CP-31/CP-01, sin identificación inequívoca sólo por longitud. No se atribuye ese POST a Ping ni a un clic específico.

Repetición acotada CP-31 por pantallas en Chrome/Edge, revisar y repetir con marcador ficticio, sólo PostgreSQL de pruebas: 23 solicitudes externas por navegador, **cero cuerpos externos visibles con coincidencias** y dos revisiones locales con textos/marcador. No guardó versiones ni modificó antivirus/bloqueó solicitudes. GET periódicos Ping/TimerCallback y otros POST observados; no reproducido el POST histórico de 3517 bytes. Reportes previos conservados. **NF-02 sigue pendiente/no aprobado**: no es evidencia nueva de filtración ni una prueba de ausencia global; atribución física/tratamiento e identificación exacta histórica siguen sin confirmar. Detalle, campos conocidos y límites en docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md.

## Ensayo local sin sesión Windows — aprobado, 8/11/2026

Santiago confirmó sesión cerrada de 16:08 a 16:27, hora Córdoba. Consulta automática: tarea temporal 16:17:52, resultado 0; copia 19:17:53Z =16:17:53 local autenticada/SHA-256/descifrado completo aprobados nuevamente por Codex (53890 bytes, esquema 0004). Se aprueba ese ensayo local; no el disparador diario, una restauración SQL de esta copia ni B2. Primer intento de retiro denegado por Windows; Santiago ejecutó el comando elevado y confirmó. Consulta posterior 19:34:35Z: temporal ausente; diaria Ready/habilitada, XML completo idéntico al previo, intervalo de un día y próxima 9/11 a 02:00 Córdoba. Ver docs/evidencias/EVIDENCIA_ETAPA06.md. Los apartados anteriores del mismo día conservan los estados históricos de preparación.

## Continuación de etapa 06 — 8/11/2026

**NF-01 básico aprobado por revisión manual de Santiago:** teclado, foco, confirmaciones, etiquetas, errores, 360 px y zoom en Chrome/Edge. Narrador falló inicialmente en Edge; al repetir en una ventana nueva funcionó sin cambios de código/configuración. Se conserva la incidencia; no equivale a certificación WCAG ni validación educativa. NF-02 sigue sin aprobar y continúa impidiendo el cierre integral.

Respaldo: tarea diaria registra 8/11 09:35:22 -03 y resultado 0; arranque Windows 09:26:35, StartWhenAvailable=true, WakeToRun=false, S4U y privilegios mínimos. Compatible con ejecución diferida, no demostrada: historial de tareas deshabilitado, sin evento de disparador. Copia de 09:35:36 autenticada/SHA-256/descifrado completo y pg_restore al dispositivo nulo aprobados: 52338 bytes, esquema 0004, dos retenidas/ninguna purgada, B2=false. Sin restauración SQL de esta copia y sin tocar datos.

Ensayo con sesión cerrada preparado en tarea temporal separada; XML validado por el servicio sin registrarlo/ejecutarlo. Falta ejecución e intervalo sin sesión confirmado por Santiago. No se cerró su sesión ni se cambió tarea diaria, energía, historial o políticas. Evidencia y comandos en docs/evidencias/EVIDENCIA_ETAPA06.md y docs/operacion/ETAPA06_WINDOWS.md. Las secciones del 7/11 se conservan como estado histórico.

## Etapa 06 — verificación integral, 7/11/2026

**Estado vigente: incremento comprobado y documentado; cierre integral local NO declarado.** Base efectiva `f109b21`, limpia al comenzar, preservando trabajo y datos. Matriz de 89 requisitos/casos en docs/evidencias/INFORME_FINAL_ETAPA06.md y evidencia en docs/evidencias/EVIDENCIA_ETAPA06.md. Santiago confirmó revisión general manual de etapa 05 y rotación local de contraseña PostgreSQL/CSRF; sin inventar resultados detallados ni valores anteriores.

**317 pruebas aprobadas, 0 fallidas, 0 omitidas, 94,99 s**; 294 previas +23 nuevas. Corpus 33/33/motor 1.0.0, cinco integraciones (INT-05 completo sobre la misma práctica), tipos/build y pip check aprobados. Dieciséis grupos funcionales en Chrome/Edge reales, seis comprobaciones adicionales y 49 instantáneas AX/DOM sin hallazgos automáticos. Corregidos ARIA/errores, foco/cancelación/editores, contraste de foco de cabecera y rechazo de claves de ejemplo de revisión/huellas. Sin rediseño ni cambios semánticos/motor/fixtures/dependencias.

NF-03 medido por HTTP real: 100 revisar +100 guardar, cinco usuarios, diez calentamientos por endpoint, texto de 10000 caracteres; p95 final 37,938/75,819 ms y cero errores. Primera medición y un intento rechazado por puerto ocupado se conservan; no se atribuye optimización ni garantía continua. Restore/diario/contingencia repetidos: 3,918 s hasta historial/comparación, copia de 2,751 s al restore; dato histórico 5,679 s conservado con su alcance.

Demo separada en entrenador_prompts_demo, preparada repetidamente sin duplicar, contraseñas privadas aleatorias y recorrido Chrome aprobado. Desarrollo conserva 6/6/5/30 de catálogo en dos inicios con entorno limpio; no se forzaron seeds. Esquema vacío y permisos de instalación nueva probados sólo en restore_test. Configuración/diario/clave/ancla exportados y verificados como paquete cifrado separado, sin identidad age; extracción ficticia probada sin sobrescribir estado activo.

Tarea inicialmente denegada por Windows 0x80070005; Santiago la instaló con su misma cuenta elevada. Codex comprobó ejecutable/script y ejecución vía Start-ScheduledTask a 19:49:54Z, resultado 0, copia/purga aprobadas y B2=false. Primer disparo diario 8/11 a 02:00 Cordoba, todavía no observado; prueba sin sesión Windows/custodia offline/B2 pendientes. Ninguna protección del equipo fue desactivada.

**Bloqueos del cierre:** NF-01 humano completo pendiente; NF-02 no aprobado. CDP identificó scripts/XHR ajenos y un POST cuyo cuerpo visible coincidió con dos textos ficticios de componentes (45/34 caracteres, sin guardar fragmentos). HTML directo/código sin ese origen; Kaspersky 21.26.4.406 instalado, rutas de avp protegidas. Firma/atribución y ruta física/tratamiento aún sin resolver. No se interpreta el dominio como inocuo ni se presenta ausencia de IA en el código como aprobación global de privacidad. Validación externa/educativa, B2 y otras dependencias académicas/operativas conservadas. Guía y comprobaciones manuales concretas en docs/operacion/ETAPA06_WINDOWS.md. Commit local sin push/despliegue.

**Estado histórico de etapa 05:** etapa 05 implementada y comprobada localmente; evidencia, límites y guía en docs/evidencias/EVIDENCIA_ETAPA05.md y docs/operacion/ETAPA05_OPERACION_WINDOWS.md. Confirmación manual de Santiago limitada a pantallas generales/recuperación/historial tras logout/login de etapa 04. Las secciones previas conservan sus estados históricos, no representan pendientes ya resueltos en incrementos posteriores.

## Etapa 05 — cierre técnico local, 7/11/2026

Referencia efectiva `6a66e5b`, limpio al comenzar. Panel HU-09 conectado a API/PostgreSQL, catálogo versionado/publicaciones atómicas/revisiones, cuentas y protección concurrente del último administrador, comando local de creación con contraseña oculta. Borrado propio de práctica/cuenta desde pantallas con CSRF y diario Fernet independiente; reintentos, fallo de diario y SQL/pendientes comprobados. Claves separadas fuera de Git/destino, ACL privadas y valores existentes conservados.

Santiago creó tres bases ficticias exclusivas; propiedad verificada. Migración `20261107_0004` primero en pruebas, luego copia cifrada de desarrollo verificada y aplicación sin modificar datos. Ejecución sigue sin DDL/TEMP/propiedad/membresías ni edición directa de historia. age 1.3.2 oficial/SHA-256 y cryptography 50.0.2 fijados; ninguna dependencia anterior cambiada, frontend sin dependencias nuevas.

**294 pytest aprobadas, 0 fallidas, 0 omitidas (114,39 s)**; 263 anteriores +31 nuevas. Motor 1.0.0/corpus 33/33 y límites CP-25/27/28 conservados. Tipos/build aprobados. Diez grupos previos y seis nuevos desde Chrome/Edge reales; estos últimos incluyen bloqueo desde panel y borrados con confirmación. Automatización distinta de revisión manual. Captura de panel a 360 px inspeccionada; accesibilidad humana completa pendiente. NF-02 sigue sin aprobar por los mismos orígenes ajenos, sin alterar antivirus ni atribuir payload/procedencia.

Restore real de dos bases aisladas: pendientes/completados reaplicados sin resurrección, todas las sesiones/recuperaciones invalidadas e historia/comparación conservadas. Diario corrupto deja CONNECT cerrado. Contingencia Uvicorn/Vite/Chrome sobre la copia restaurada, **5,679 s hasta lectura/comparación**, edad de copia al restore **3,408 s**. Cumple las metas sólo en ese ensayo local con entorno ya instalado; sin garantía continua ni proveedor público. Retención real local probada; adaptador B2/versiones/multipart sólo simulados.

Tarea Windows XML validada con TASK_VALIDATE_ONLY, no registrada. Trabajo ejecutado directamente una vez: copia y purga local aprobadas; B2=false y credenciales incompletas, sin contacto externo. **Pendientes:** 05.1–05.6 manuales de Santiago, 05.9 parcial (registro/ejecución diaria sin sesión interactiva, B2 real, custodia offline/redundancia/transferencia de diario y claves), NF-01 completo/NF-02/NF-03, validación externa/educativa y otros pendientes de despliegue previos. No se purga el diario activo sin comprobar todas las copias afectadas. Guía con terminales/URLs/comandos en docs/operacion/ETAPA05_OPERACION_WINDOWS.md; resultados y fallos intermedios resueltos en docs/evidencias/EVIDENCIA_ETAPA05.md. Sin etapa 06, publicación ni despliegue.

## Etapa 01 — estructura, base de datos y arranque

**Estado histórico al cerrar etapa 02: etapa 01 comprobada técnicamente y revisión visual confirmada manualmente por Santiago; etapa 02 implementada y comprobada automáticamente.** La separación de roles PostgreSQL y Mailpit siguen pendientes. El registro de intentos anteriores se conserva debajo como antecedente; resultados actuales en `docs/evidencias/EVIDENCIA_ETAPA01.md` y `docs/evidencias/EVIDENCIA_ETAPA02.md`.

Fecha de inicio: 6 de noviembre de 2026. Entorno: Windows con PowerShell, Python 3.11.4, Node.js 26.13.0 y npm 11.20.0 mediante `npm.cmd`.

Elección de PostgreSQL: el listener `127.0.0.1:5432` (PID 8132) tiene como padre el PID 5644, correspondiente al servicio `postgresql-x64-18`; se adopta PostgreSQL 18.6. No se modificó PostgreSQL 17 ni ninguna base existente.

Bloqueos conocidos al inicio: falta crear el rol y las bases exclusivas del proyecto con una credencial administrativa local; Mailpit queda diferido a la etapa 03. La descarga de paquetes Python está bloqueada por una cadena TLS no confiable en el entorno de Python y debe resolverse configurando la CA institucional, sin desactivar la validación TLS.

El detalle de comprobaciones ejecutadas, bloqueadas y pendientes se completa al cerrar esta etapa. No considerar las tablas, seeds o servicios de arranque como historias funcionales terminadas.

### Comprobaciones ejecutadas con éxito

- Selección de PostgreSQL: `netstat` identificó el listener 5432; una consulta CIM con privilegios vinculó el PID 8132 con el servicio `postgresql-x64-18` (PID padre 5644). No se modificaron servicios ni bases.
- Git: `git init` creó el repositorio local. `.gitignore` excluye `.env`, `.venv`, `node_modules`, builds, logs, respaldos y datos locales, y conserva `.env.example`.
- Frontend: `npm.cmd install --no-audit --no-fund` creó `frontend/package-lock.json`; `npm.cmd run build`, desde `frontend`, compiló TypeScript y Vite correctamente. Una ejecución temporal de Vite devolvió HTTP 200 en `http://127.0.0.1:5173`; se detuvo al finalizar.
- Backend estático: `python -m compileall -q backend\app backend\alembic backend\tests` finalizó con código 0. No equivale a ejecutar FastAPI, Alembic ni pytest.
- Secretos: la inspección de `.env.example` confirmó vacías las variables de contraseña, URLs de base y claves de firma. `git check-ignore` confirmó la exclusión de `.env`, `.venv`, `node_modules` y respaldos.

### Comprobaciones pendientes, bloqueadas o fallidas

- **01.1 y 01.2 — Bloqueadas:** el frontend arranca, pero la API no puede instalarse/arrancar todavía. La descarga con `pip` falló con `SSLCertVerificationError: self signed certificate in certificate chain` al acceder a PyPI. Se requiere configurar la CA institucional para Python sin desactivar TLS.
- **01.3 a 01.7 — Bloqueadas:** no existen aún `entrenador_app`, `entrenador_prompts` ni `entrenador_prompts_test`; deben crearse localmente con una credencial administrativa que no se compartirá en chat. No se ejecutaron migraciones, seeds, restricciones/FK, reinicio ni persistencia para evitar tocar bases ajenas.
- **01.8 — Parcial, no aprobada:** la exclusión de secretos se comprobó, pero la validación de configuración no pudo ejecutarse al faltar `pydantic-settings`; queda pendiente la comprobación real de error seguro ante configuración incompleta.
- **Mailpit — Diferida:** no es requisito de esta etapa y se instalará/verificará en la etapa 03.
- **Commit local — Pendiente:** el sandbox no tiene `user.name` ni `user.email` configurados para Git. No se inventó una identidad. El repositorio fue inicializado y está listo para que el propietario configure su identidad local y confirme el incremento.

### Reanudación — resultados vigentes

- Se conservaron los archivos existentes y el repositorio, sin regenerar el proyecto.
- Se actualizó únicamente pip dentro de `.venv` a 26.3 usando HTTPS con certificados de Windows y verificación SHA-256 del wheel. La instalación Python finalizó; `pip check` no detectó dependencias incompatibles.
- Se generó `backend/requirements.lock`, resuelto desde las dependencias directas. Se retiraron de `.venv` los extras de CLI y exportación de telemetría instalados por el extra `standard`; se fijaron Uvicorn y HTTPX explícitamente. La aplicación desactiva telemetría.
- Se corrigieron `%(here)s` en Alembic, el CHECK del objetivo nulo, la relación regla/aplicabilidad y los estados permitidos por criterio. La compilación de la migración a SQL pasó; su ejecución real permanece pendiente.
- Se corrigió la resolución de FK de seeds por código para admitir UUID previos. La repetición preserva registros existentes. Esta propiedad tiene una prueba PostgreSQL preparada y todavía no ejecutada.
- `pytest -q`: **8 aprobadas, 5 omitidas** por falta de credenciales; XML local en `local-data/etapa01-pytest.xml`. Las aprobadas cubren configuración, contraseñas con caracteres especiales, rechazo de bases inseguras y compilación offline de migración. No acreditan integridad en PostgreSQL.
- `npm.cmd ci --offline --no-audit --no-fund` y `npm.cmd run build`: aprobados, instalando desde el lockfile existente.
- A pedido del propietario se preparó `.env`, conservando valores no sensibles y contraseña vacía. Se añadieron `docs/historico/CONFIGURACION_LOCAL_WINDOWS.md` y `scripts/crear_bases_locales.sql` para preparación interactiva local sin compartir secretos.
- `validate_config` muestra únicamente el nombre de la variable faltante. Este fallo es esperado hasta completar `.env`.
- No se ejecutaron sentencias de creación de roles/bases ni migraciones sobre ningún servidor en esta reanudación. No se conoce aún la existencia de esos recursos: el script local la comprobará antes de crear.
- Git sigue sin identidad efectiva; no hay commit. Configurar la identidad sólo en este repositorio según la guía local.
- Mailpit sigue diferido a etapa 03. No se inició la etapa 02.

### Cierre de comprobaciones de etapa 01

- El propietario completó `.env`, creó los recursos locales y configuró identidad Git. Se comprobó la conexión a ambas bases vacías con `entrenador_app`, PostgreSQL 18.6 y `rolsuper/rolcreatedb/rolcreaterole=false`.
- Alembic creó desde cero las 13 tablas del contrato y `alembic_version` en desarrollo y pruebas; revisión `20261106_0001 (head)`. No se restauraron copias ni se corrigieron tablas manualmente.
- Dos ejecuciones de seed en desarrollo mantuvieron 6 criterios, 6 reglas, 4 desafíos y 24 relaciones. La prueba de no sobrescritura conserva modificaciones ficticias en nombres, títulos y mensajes de reglas y luego las revierte.
- `pytest`: **20 aprobadas, ninguna fallida ni omitida**; 8 comprobaciones sin base y 12 con PostgreSQL. Incluye FK inválidas, duplicados, estados incompatibles, objetivo nulo, número de versión repetido y cascada sin huérfanos. Los datos ficticios de cada comprobación se revierten con savepoints.
- `scripts/verify_startup.py`: dos ciclos independientes de inicio/parada de API y Vite con HTTP 200; HTML y módulo React entregados. Conteos conservados después de reiniciar. No se reinició el servicio PostgreSQL compartido con otras bases.
- Se añadieron comandos reproducibles de diagnóstico, arranque/reinicio y revisión de secretos; evidencia local detallada en `local-data/`, excluida de Git.
- Las comprobaciones HTTP no equivalen a una revisión visual en navegador. Las historias de usuario, autenticación, motor, validación externa, respaldo/restauración y Mailpit permanecen en sus etapas correspondientes.
- Limitación explícita: en este entorno inicial el rol del proyecto es propietario para ejecutar migraciones. La separación entre rol de migración y rol de ejecución sin DDL debe resolverse antes del uso funcional; no se presenta el entorno local como configuración de producción.

### Revisión visual de etapa 01 — confirmación manual de Santiago

El 6/11/2026 se contrastaron los comandos con `backend/app/main.py`, `frontend/package.json`, `frontend/vite.config.ts` y `frontend/src/App.tsx`. En este paso no se iniciaron servidores ni se ejecutó una revisión visual. La evidencia HTTP anterior sigue siendo una comprobación automática.

Abrir dos terminales PowerShell, ambas inicialmente en la raíz del proyecto. En la primera:

```powershell
Set-Location .\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En la segunda:

```powershell
Set-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run dev
```

No se requiere activar `.venv`, reinstalar dependencias ni repetir migraciones o seeds. Mantener ambas terminales abiertas mientras se revisa. Abrir `http://127.0.0.1:5173`: debe aparecer el título «Entrenador de Prompts» y el texto «La estructura técnica está disponible. Los recorridos funcionales se incorporarán por etapas.». Abrir `http://127.0.0.1:8000/health`: debe aparecer el JSON `{"status":"ok","service":"api"}`. El navegador puede mostrarlo con formato. La raíz `http://127.0.0.1:8000/` no tiene una pantalla implementada; usar `/health`.

Para detener los servidores, presionar Ctrl+C en cada terminal; si Windows solicita confirmar el cierre del proceso por lotes de npm, confirmarlo. Esperar a que vuelva el prompt. Esto no detiene PostgreSQL ni borra datos.

- [x] Santiago comunicó que completó la revisión visual y que el frontend funciona correctamente. Comprobación manual realizada por él; no se atribuye a Codex ni se inventan capturas.
- [x] Santiago comunicó que el backend funciona correctamente durante esa revisión manual. Se registra su confirmación de funcionamiento; el JSON exacto también tiene evidencia HTTP automática previa.
- [ ] Santiago confirmó que pudo detener ambos procesos.

Confirmación recibida en el mensaje que solicita la etapa 02, con fecha de referencia 6/11/2026. No se recibió una confirmación explícita de la detención manual de ambos procesos; esa casilla permanece pendiente. La inspección visual no acredita funcionalidades que todavía no están implementadas. Referencia del cierre técnico de etapa 01: `2c2069e`; preparación documental visual: `4c2ae19`.

### Separación de rol de migraciones y rol de ejecución — planificación histórica

**Actualización 7/11/2026:** resuelta y comprobada en etapa 03, tras intervención administrativa local de Santiago. Se conserva a continuación el hito original y su desvío; los resultados actuales están al final de este documento y en `docs/evidencias/EVIDENCIA_ETAPA03.md`.

Contraste de contratos: `AGENTS.md` exige respetar los contratos técnicos, autorizar en servidor y mantener secretos fuera de Git/frontend/logs, pero no define por sí mismo dos roles de PostgreSQL. `docs/tecnica/SECURITY.md` exige protección de credenciales, autorización y configuración segura de producción; tampoco fija nombres de roles ni una etapa concreta para separarlos. El requisito específico está en `docs/tecnica/DATABASE.md`, «Infraestructura añadida»: las credenciales del motor no deben permitir DDL y las migraciones usan una credencial separada al desplegar. No se atribuye esta decisión técnica a la docente.

La configuración inicial usa `entrenador_app` como propietario para aplicar Alembic. La ausencia de superusuario no elimina sus permisos DDL sobre los objetos propios, por lo que ese punto del contrato sigue pendiente; no queda aprobado por las 20 pruebas actuales.

**Momento previsto: resolver como siguiente ajuste de infraestructura de la etapa 01, después de recibir el resultado de esta revisión visual y antes de iniciar la etapa 02.** Este orden adelanta la separación respecto del despliegue para no arrastrar la limitación al desarrollo funcional. En este turno sólo se registra la planificación: no se crean roles ni se cambian propietarios o permisos.

Para darlo por resuelto se deberá separar la credencial que ejecuta Alembic de la que usa FastAPI, conservar únicamente los permisos de datos necesarios en ejecución y comprobar en las dos bases exclusivas del proyecto que el rol de ejecución no puede crear, alterar ni eliminar estructuras ni adquirir esos permisos mediante propiedad o membresía. Se repetirán migraciones con su credencial correspondiente, seeds, pruebas y arranque con la credencial de ejecución. Las credenciales permanecerán locales y fuera de Git y `VITE_*`. No se tocarán roles o bases ajenos al proyecto.

**Situación al ejecutar el pedido actual:** el hito anterior decía resolver antes de etapa 02 y continúa sin cumplirse. Santiago solicita explícitamente implementar sólo el motor aislado y conservar este pendiente. Por precedencia de su instrucción se realiza la etapa 02 sin cambiar roles, propietarios, credenciales ni permisos, dejando visible el desvío del hito; no se reprograma silenciosamente ni se considera resuelto. Debe tratarse como ajuste de infraestructura pendiente antes de integrar el motor a la API funcional y antes de cualquier despliegue. Mailpit mantiene su etapa 03.

## Etapa 02 — motor puro y detectores

- Versión del motor: `1.0.0`, coherente con `seeds/rules.json`. No se cambiaron dependencias, migraciones, fixtures esperadas, endpoints ni pantallas.
- `app/domain/evaluation.py` implementa validación estricta, normalización NFC/LF, ensamblado guiado, modo libre con confirmación, C1–C6, estados y evidencias sin fragmentos sensibles, revisión preventiva del objetivo, coincidencias opacas, snapshots y comparaciones/indicadores puros. Sólo utiliza biblioteca estándar; recibe configuración y claves en memoria.
- `app/application/fixture_evaluation.py` carga los archivos ficticios fuera del motor. `confirmar_todas` se interpreta sólo en el adaptador del corpus; el motor recibe una selección de coincidencias ligada a su contenido/configuración y contexto. No se implementaron tokens HTTP, autenticación ni persistencia de versiones o alertas.
- Corpus: 33/33 casos aprobados, CP-01–CP-34 excluyendo CP-12. CP-25 conserva presencia sin juicio de calidad; CP-27 y CP-28 conservan falsos negativos conocidos. CP-12 sigue reservado a etapa 04.
- Pruebas del motor: 120 aprobadas. Incluyen repetibilidad, ausencia de mutaciones, entradas límite, tipos y configuración inválida, privacidad, objetivo, criterios no aplicables, confirmaciones, firmas, indicadores y comparación de huellas. Pruebas de aislamiento bloquean archivos, sockets y creación de motores SQLAlchemy; también se importa el dominio con Python `-I -S` sin paquetes de terceros.
- Regresión completa ejecutada: 140 aprobadas, ninguna fallida ni omitida (120 motor y 20 de etapa 01). El motor se prueba sin leer `.env`; la regresión PostgreSQL conserva la base exclusiva de pruebas existente.
- Evidencia reproducible y resultados esperado/obtenido por caso: `docs/evidencias/EVIDENCIA_ETAPA02.md`. No se declara terminada ninguna historia funcional por estas pruebas puras.
- Al cierre técnico de esta etapa quedaban pendientes: interpretación manual de mensajes (02.9), separación de roles y Mailpit/acceso. La confirmación posterior de 02.9 se registra a continuación. Integración, tokens firmados, guardado, comparación con persistencia y CP-12 corresponden a etapa 04; validación externa antes de usuarios.

### Comprobación manual parcial de 02.9 — CP-25, CP-27 y CP-28

El 6/11/2026 Santiago comunicó que verificó las salidas de CP-25, CP-27 y CP-28: esperado y obtenido coinciden y los tres muestran `aprobado=true`. En ese momento su comprobación manual estaba limitada a esa coincidencia, sin confirmar interpretación; el cierre posterior de 02.9 se registra abajo, con fecha 7/11/2026.

En respuesta se ejecutó el motor 1.0.0 para extraer sus mensajes reales, sin cambiar código ni expectativas. Los tres casos producen los mismos seis mensajes de cumplimiento, cero coincidencias y 6/6 = 100 %. La transcripción está en `docs/evidencias/EVIDENCIA_ETAPA02.md`. Mostrar estos textos no significa que Santiago ya los haya revisado.

Distinción de presentación: el resultado público del motor incluye el aviso genérico «Estos patrones no detectan toda la información sensible». La consola `check_motor` agrega «El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.». Este último texto no forma parte del resultado público individual ni del informe resumido `--json`. Las explicaciones específicas de CP-25/27/28 están en fixtures/documentación, no se emiten como advertencias particulares de cada evaluación. El frontend sigue sin pantalla de resultados; la presentación al usuario de esos límites queda pendiente de la interfaz de etapa 04. No se implementó nueva UI ni se alteraron reglas en esta comprobación.

### Cierre manual de 02.9 — 7/11/2026

Santiago confirmó que revisó los mensajes y las limitaciones mostrados para CP-25, CP-27 y CP-28. **02.9 completada por comprobación manual del usuario**, conservando la evidencia previa de esperado/obtenido y la transcripción literal en `docs/evidencias/EVIDENCIA_ETAPA02.md`. No se atribuye esta revisión a una ejecución automática ni a una pantalla.

**Requisito pendiente de etapa 04:** mostrar junto a cada resultado que «El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad» y «Estos patrones no detectan toda la información sensible». Su presentación en la interfaz no está implementada ni aprobada. Se conservan los límites conocidos de CP-25/27/28.

## Etapa 03 — cierre técnico, 7/11/2026

Referencia inicial: `6b4dc38`. Se conservó el proyecto existente. Santiago ejecutó el procedimiento administrativo local y guardó `MIGRATION_PASSWORD` fuera de Git. Se verificaron ambas credenciales en ambas bases: `entrenador_app` sin DDL, TEMP, propiedad ni membresías; `entrenador_migracion` propietario de 15 tablas (14 de aplicación y Alembic). Se probaron CREATE/ALTER/DROP/TEMP/CREATE SCHEMA/SET ROLE denegados. No se cambiaron datos ni configuración de PostgreSQL 17.

- Mailpit oficial Windows amd64 1.33.0 instalado en `local-data/`, con SHA-256 publicado verificado. SMTP real `127.0.0.1:1025` e interfaz/API `127.0.0.1:8025`, sin Docker/WSL. Se inicia con versión automática y resolución DNS inversa desactivadas y sólo en loopback; instrucciones y parada Ctrl+C en README.
- Migración `20261107_0002` aplicada con `entrenador_migracion` a desarrollo y pruebas; añade `limite_solicitud` y su DML de ejecución. Seeds conservan 6/6/4/24. Se mantienen datos y migración inicial; no se regeneró ni vació ninguna base.
- API de registro/login/logout/me/csrf/recuperación/restablecimiento/cambio de clave; listado mínimo y estado administrativo sólo para comprobar permisos/revocación. Argon2id 65536/3/1, claves con espacios/Unicode y lista local limitada/versionada; sesiones opacas de 32 bytes, hash en PostgreSQL, cookie HttpOnly/Lax, estado/epoch consultados en servidor, CSRF ligado a sesión y origen único. No hay pantallas nuevas, cambio de rol público, acceso administrativo a textos ajenos ni endpoints funcionales de prácticas.
- Revocación transaccional, límites compartidos PostgreSQL por IP/cuenta, expiraciones servidor, tokens de recuperación con hash/15 minutos/uso único, consumo concurrente y revocación global comprobados. El guard de escritura bloquea usuario hasta confirmar y se serializa con bloqueo/desactivación. Errores uniformes sin reflejar cuerpos, cookies o claves; límite 64 KiB. Desactivar logs de acceso/cabeceras proxy en arranque local.
- **Regresión final: 223 aprobadas, 0 fallidas, 0 omitidas, 35,08 s**: 140 previas + 83 nuevas de acceso/configuración/SMTP. Incluye purga concurrente sin interbloqueos, errores de JSON/UTF-8 con 400 y validación de un único destinatario de correo. Advertencia de deprecación de Starlette al usar el httpx ya fijado; no se sustituyeron dependencias previas. Corpus motor 1.0.0: 33/33; sin cambios en dominio/fixtures. Dos ciclos de inicio/parada API y Vite con HTTP 200 y conteos conservados.
- Argon2id medido: mínimo 19456/2/1, mediana 25,2 ms; elegido 65536/3/1, mediana 116,9 ms y máximo 118,1 ms, 10 hashes por configuración. Se elevaron los valores iniciales de `.env` sin imprimir ni sustituir secretos. Parámetros inferiores al contrato impiden el arranque; los hashes antiguos se actualizan tras autenticar correctamente.
- Evidencia, comandos, correcciones durante la ejecución y alcance por SEC: `docs/evidencias/EVIDENCIA_ETAPA03.md`. Informe JUnit detallado en `local-data/etapa03-regresion.xml` ignorado por Git. La revisión manual 02.9 está completada por Santiago.

### Confirmación manual de acceso y Mailpit — 7/11/2026

Santiago confirmó que completó `scripts/check_access_manual.py` sobre el cierre técnico `6910957` y recibió el correo de recuperación en Mailpit. Resultados comunicados: restablecimiento 204; reutilización del token 400; sesión B revocada 401; contraseña anterior 401; ingreso con la nueva contraseña 200; cierre final 204. **03.M1 completada por comprobación manual del usuario.**

En el primer intento ingresó una nueva contraseña demasiado corta; repitió el recorrido respetando el mínimo de 15 caracteres y todas las comprobaciones del auxiliar finalizaron correctamente. No informó el código HTTP del primer intento y no se inventa. Evidencia detallada en `docs/evidencias/EVIDENCIA_ETAPA03.md`, sin secretos ni datos de cuenta. Esta actualización es documental: no se repitieron las 223 pruebas automáticas ni se modificó código/configuración.

**Pendientes conservados:** dos navegadores reales; las sesiones A/B del auxiliar son clientes HTTP con cookies independientes. En etapa 04: pantallas, avisos estructural/calidad/seguridad junto a resultados, revisión del objetivo/prompt, integración del motor, tokens de revisión, CP-12 y SEC-07/08/17 completos sobre endpoints/pantallas de prácticas, comparación y borrado. En etapa 05: borrado durable de cuenta/práctica, diario y ensayo completo de respaldo/restauración (SEC-09 sólo tiene el hook de invalidación probado). El panel administrativo y una vía de recuperación del último administrador siguen pendientes de su etapa: la API actual rechaza restringir administradores en lugar de dejar al sistema sin una vía comprobada. Lista de contraseñas comunes inicial limitada y SMTP real de producción pendientes de preparación de despliegue. Validación externa y con personas no realizadas. No se inicia etapa 04.

## Etapa 04 — incremento funcional, 7/11/2026

**Confirmación manual posterior de Santiago:** comprobó pantallas generales, recuperación e historial tras salir y volver a ingresar. Se registra sólo ese alcance; no se marcan por extensión CP-12 exacto, todas las casillas manuales, reinicios ni accesibilidad completa. NF-02 sigue pendiente y no se modifica el antivirus. El resto del apartado conserva la evidencia histórica del cierre técnico.

Punto de partida efectivo `c331728`, limpio; sin reset ni avances posteriores que sobrescribir. El estado pendiente del apartado anterior es histórico: los siguientes controles ya se realizaron en esta etapa. Se conserva la confirmación manual de Santiago 03.M1; no se inventa una revisión manual de pantallas de etapa 04.

- Formularios reales de registro/login/logout/recuperación/restablecimiento/perfil; inicio por desafío u objetivo propio; constructor guiado/libre declarado; revisión preventiva y de prompt; confirmación específica; V1/V2/resultados/comparación; historial con filtros/paginación y progreso separado por práctica/configuración. React/TypeScript → API → PostgreSQL real. Copia sólo por botón, borrador en memoria ante error de red, retirada de contenido al invalidarse/cambiar sesión; sin almacenamiento persistente de prompts/tokens.
- Ambos avisos estructural/calidad/seguridad junto a resultados, incluso 100 % y sin coincidencias, implementados y comprobados en navegador. Limitación de libre y avisos confirmados visibles. Se consultaron prototipos y figuras originales 4–7; no se reescribió documentación académica.
- Motor **1.0.0** y fixtures conservados. Aplicación/carga de catálogos separadas del dominio, consultas parametrizadas en persistencia. Tokens firmados sin texto, ligados a operación/usuario/práctica/contenido/configuración/versión de huellas/expiración de 10 min/nonce. Claves ausentes generadas independientemente sólo en `.env`; claves y versión existentes conservadas, sin mostrar valores.
- Migración **20261107_0003** aplicada a desarrollo y pruebas con `entrenador_migracion`: INSERT de prácticas/versiones/evaluaciones/resultados/alertas y UPDATE sólo de fecha de práctica. Ejecución sigue sin DDL/TEMP/propiedad/membresías ni edición/borrado de versiones. Datos conservados; no se vació ni reconstruyó desarrollo, ni se modificó PostgreSQL 17.
- Guardado atómico con sesión/usuario bloqueado, catálogo compartido 90404 y práctica bloqueada. Idempotencia y reintento tras respuesta perdida, numeración concurrente, rollback, token vencido/ajeno/alterado/desactualizado, autorización al commit, propiedad derivada, snapshots y comparación de huellas probados. Publicador exclusivo ensayado sólo mediante fixture SQL de pruebas; el panel real sigue en etapa 05.
- **Regresión final: 263 aprobadas, 0 fallidas, 0 omitidas, 61,18 s**: 223 anteriores + 40 nuevas. Corpus **33/33**. Tipos/build Vite aprobados. Dos arranques/paradas API/Vite HTTP 200 con conteos 6/6/4/24 conservados; también reinicio real de los servidores temporales durante el recorrido de navegador. Revisión repetida tras respuesta perdida conserva ID de contenido y recupera V2 sin duplicarla, incluso con un nuevo token; nuevas versiones con alertas siguen requiriendo confirmación.
- **Dos navegadores reales**: Chrome 156.0.8078.80 y Edge 157.0.4341.42, procesos/perfiles independientes headless. Diez grupos funcionales aprobados: formularios, CP-12 3/6→6/6/V1 intacta/+50 pp/100 % resolución, reintento sin duplicar, copia, persistencia tras reinicio, objetivo/libre/confirmación, recuperación Mailpit/clave usada, perfil y revocación/bloqueo/desbloqueo. Esto acredita navegadores, no clientes HTTP; tampoco es una confirmación manual de Santiago.
- Capturas ficticias de 360 px/resultados/comparación de escritorio inspeccionadas por Codex. Etiquetas explícitas, foco de teclado y ausencia de desborde probados; falta revisión humana completa de teclado/lector/contraste. Sondeo de sesión sin renovar inactividad, datos en UTC y filtros de fecha Cordoba verificados.
- Dependencia nueva sólo de prueba: Playwright 1.64.1 y pyee 13.0.1 fijados, usando navegadores instalados; dependencias anteriores conservadas. Sin WSL/Docker ni cambio de política PowerShell. Evidencia detallada: `docs/evidencias/EVIDENCIA_ETAPA04.md`; reportes/capturas locales ignorados.

**NF-02 pendiente real del entorno:** el navegador observó orígenes `gc.kis.v2.scr.kaspersky-labs.com` y `me.kis.v2.scr.kaspersky-labs.com`, ausentes de la app. Se registran sólo orígenes, no contenido/identificadores. Compatible con inserción de protección local según documentación oficial, sin auditar su configuración ni demostrar que el tráfico salga físicamente del equipo. No se desactivó el antivirus ni se maquilló la comprobación. El informe distingue recorrido funcional aprobado de NF-02 no aprobado (código nativo 2 del auxiliar).

**Pendientes:** confirmación manual de Santiago de las pantallas y accesibilidad completa (NF-01), aislamiento de la observación NF-02 y NF-03 sin medición. Etapa 05: panel, borrado durable/diario/restauración completa y tramos SEC-09/SEC-11/INT-05/borrado SEC-07. El cierre de sesión, recuperación y cambio de clave sí están probados desde formularios. No se implementa etapa 05 ni se publica/despliega. Guía manual con comandos/URLs en README y docs/evidencias/EVIDENCIA_ETAPA04.md; el auxiliar administrativo manual sigue pendiente de ejecución humana.
