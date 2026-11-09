# Evidencia de etapa 06 — verificación integral y correcciones

Actualización vigente: **8/11/2026**, sección de continuación al final. Los pendientes del 7/11 son históricos cuando se resuelven expresamente debajo.

Fecha inicial: **7/11/2026**, America/Buenos_Aires. Repositorio inicial limpio en **f109b21**; se conservaron sus datos/código e historial, sin reset, push ni despliegue. La versión final corresponde al commit que incorpora este informe. Matriz reproducible: **docs/evidencias/INFORME_FINAL_ETAPA06.md**, 89 filas (AT-01–25, SEC-01–17, NF-01–04, OPS-01–03, cinco integraciones, 33 casos puros y VAL-01/02), derivadas del JUnit realmente ejecutado y auditorías indicadas.

**No se declara cierre técnico integral:** NF-02 no está aprobado y NF-01 humano completo sigue pendiente. Las pruebas funcionales aprobadas no sustituyen esos controles. B2, custodia externa, periodicidad operativa y validación educativa se informan aparte.

## Confirmaciones y estado conservado

- Santiago confirmó la revisión **general** de los recorridos de etapa 05 que probó. Se registra como manual sin inventar entradas, capturas, tiempos ni resultados por caso. No se marcan por extensión todas las casillas individuales ni accesibilidad completa.
- Confirmó haber rotado **ambos secretos** mencionados (contraseña PostgreSQL y CSRF). Se comprobaron conexiones actuales de ejecución/migración y arranque con configuración válida. No se solicitaron ni compararon valores antiguos; no se imprimen secretos. Se considera rotación confirmada por el usuario, no una prueba automática de diferencia con el secreto anterior.
- Se conserva el ensayo histórico de etapa 05: **5,679 s** hasta lectura/comparación con copia de **3,408 s** al restore, entorno ya instalado. El ensayo nuevo de abajo es independiente; ninguno es una garantía continua.
- PostgreSQL 18.6 y la separación de roles permanecen; instalación 17 y bases ajenas sin cambios. Desarrollo tenía **6 criterios/6 reglas/5 desafíos/30 relaciones** al comprobar arranque, conservados en ambos ciclos. No se forzó el catálogo de desarrollo a los cuatro seeds iniciales.

## Fallos corregidos y preparación técnica

1. Referencias `aria-describedby` a errores inexistentes: ahora se agregan sólo cuando existen, y un campo compartido asocia el aviso general con los controles de formularios y administración. Se conserva validación de contraseña y borrador en memoria.
2. Confirmaciones de borrado sin gestión explícita de foco/cancelación: controles con expanded/controls, foco inicial, Escape y botón Cancelar, retorno al activador; no se convierten en modales falsos. Editores administrativos enfocan su primer campo editable. Se permitió partir encabezados/etiquetas largos sin recortar contenido.
3. Foco de cabecera con contraste bajo: color previo `#ad4c00` frente a `#005148`, **1,678:1**; ahora `#ffcf66`, **6,328:1**. Foco del cuerpo conserva **5,154:1** sobre su fondo. Cambio acotado de accesibilidad, sin rediseño. Referencia: [W3C, contraste no textual](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast). No certifica todos los contrastes/estados.
4. Claves de ejemplo: el rechazo de prefijos example/ejemplo se aplicaba a CSRF y no a revisión/huellas. Se extendió a las tres, sin rotar claves legítimas ni modificar motor/reglas. Producción ficticia válida, 17 variantes inseguras y caso de independencia probados (19 pruebas) sin conexión/despliegue.
5. Arranque podía consultar puertos de servidores ajenos mientras lanzaba procesos propios: ahora se rechaza ocupación previa y se limpian variables de proyecto heredadas en los hijos; dos ciclos reales con `.env` y conteos conservados. Sólo se detienen procesos propios.
6. La secuencia antigua de instalación de roles suponía tablas/funciones existentes. Se preparó un SQL exclusivo para instalación **nueva** y un bloque atómico de permisos de acceso posterior a Alembic, probado después de migrar un esquema ficticio vacío. No se reescribieron migraciones existentes ni se ejecutó creación de roles sobre el equipo actual.
7. Recuperación operativa: archivo age cifrado de `.env`, diario, clave Fernet y ancla, con manifiesto interno. Directorio separado y ACL privadas; identidad privada age permanece fuera del paquete. Exportación/verificación real del estado local; roundtrip/extracción y rechazo de sobrescritura con configuración ficticia. No se sobrescribe configuración activa ni se habilita servicio al extraer. Límite 16 MiB sin truncar y validación de miembros de archivo, sin extractall.
8. Demo en base exclusiva `entrenador_prompts_demo`, creada por Santiago y verificada propietaria de migración. Preparación inicial y repeticiones: IDs estables, mismas cuentas/práctica/V1/V2, sin duplicar ni modificar historia. Credenciales aleatorias privadas fuera de Git/seeds/documentos; usuario y administrador ficticios comprobados en Chrome contra API/Vite, con cierre y retirada de estado privado. Desarrollo/pruebas no reciben esos historiales. La promoción local de demo reutiliza el lock y la revocación de sesiones del comando técnico existente.

No se añadieron dependencias ni actualizaron locks; stack y política 15–128 intactos. Motor **1.0.0**, C1–C6, parámetros, modo libre declarado, normalización y límites CP-25/27/28 conservados; ninguna fixture esperada modificada. No se agregó IA, inferencia semántica, ponderación ni funciones educativas nuevas.

## Resultados ejecutados

| Grupo | Resultado real | Evidencia |
|---|---|---|
| Regresión integral final | **317 aprobadas, 0 fallidas, 0 omitidas, 94,99 s** | local-data/etapa06-regresion.xml; 294 previas +23 nuevas (19 producción, 2 migración/INT-05, 2 archivo de configuración). |
| Regresión anterior de este incremento | 315 aprobadas, sin fallos/omisiones, 97,71 s; luego se añadieron dos casos de claves de ejemplo | No se presenta como ejecución del código posterior. |
| Procedimiento de permisos de instalación nueva | 1 prueba dirigida adicional aprobada, 1,39 s; mismo caso de la suite ampliado, no se suma como prueba distinta | Esquema restore_test comprobado vacío, 15 tablas/head 0004, seeds 6/6/4/24 idénticos al repetir; INSERT de acceso permitido, CREATE de esquema denegado. |
| Corpus puro | **33/33**, motor 1.0.0 | test_fixture parametrizado en JUnit; check_motor y reporte corpus. |
| Cinco integraciones | CP-12, INT-02/03/04/05 aprobados técnicamente | Matriz/JUnit y navegadores. INT-05 ahora ejecuta objetivo con correo, rechazo sin persistir, confirmación, copia, borrado y restauración de esa misma práctica. |
| Tipos/build final | Aprobados: tsc -b y Vite; 19 módulos, 124 ms | npm.cmd run build; sin dependencias frontend nuevas. |
| Dependencias | pip check sin incompatibilidades | Locks conservados y entorno existente. |
| Inicio/parada | Dos ciclos HTTP 200 API/Vite/módulo, conteos 6/6/5/30 iguales | verify_startup.py, logs técnicos locales sin cuerpos. |
| Propiedad/rol/CSRF/estado/sesiones/errores | Regresión aprobada; no bypass del administrador sobre prompts ajenos | SEC-01–17 con pruebas específicas enumeradas en matriz. |
| Datos extremos/concurrencia/rollback/idempotencia | Aprobados: tokens alterados/ajenos/desactualizados, numeración, reintento perdido, configuración, todo o nada | Suite previa repetida, casos nuevos e instrumentación de navegador. |

Advertencia conservada de Starlette sobre TestClient/httpx: funciona la combinación fijada; no se ocultó cambiando dependencias.

### Navegadores e interfaz

Chrome **156.0.8078.80** y Edge **157.0.4341.42**, procesos/perfiles independientes headless, PostgreSQL real. Diez grupos de flujo y seis de administración aprobados nuevamente: acceso/Mailpit/restablecimiento/cambio de clave, desafío y objetivo propio, guiado/libre, alertas, copia, V1/V2 y CP-12 (3/6→6/6, +50 pp, resolución 100 %, V1 intacta), historial/progreso, publicación/no comparabilidad, bloqueo, desactivación y borrados.

Auditoría CDP AX/DOM de **49 instantáneas**: cero controles sin nombre, referencias ARIA faltantes, IDs duplicados o desbordes en las vistas examinadas. Seis comprobaciones adicionales: foco/contraste de cabecera; objetivo 1001; componente 2001 y corte de red antes del servidor/reintento; libre 10001 sin truncar; confirmaciones por teclado/Escape/retorno; desactivación desde panel con ambas sesiones reales revocadas. Las entradas inválidas se mantienen, no hay éxito ficticio ni versión nueva por esos errores. El reintento después de commit ya consumado sigue sin duplicar. Resultados mantienen ambos avisos, incluidos 100 %/cero coincidencias, y la limitación del modo libre.

No se ejecutó lector humano completo ni se certifica WCAG. La revisión general manual de Santiago no reemplaza esa comprobación. Capturas de móvil del flujo/panel y comparación fueron inspeccionadas por Codex; los reportes no contienen contraseñas, tokens, fragmentos sensibles ni HAR. Código del auxiliar: 2 = funcional aprobado con NF-02 pendiente; no es éxito integral.

### NF-02: investigación y hallazgo no resuelto

Código frontend: fetch relativo a `/api/v1`, proxy localhost; sin IA, analítica, sendBeacon, storage persistente de prompts ni SDK externo. API/PostgreSQL/Mailpit y respaldo privado configurados tienen finalidad explícita. B2 sigue deshabilitado y no se contactó.

CDP observó solicitudes a `gc.kis.v2.scr.kaspersky-labs.com` y `me.kis.v2.scr.kaspersky-labs.com`. La primera carga es de tipo Script/iniciador parser; peticiones XHR posteriores tienen iniciadores de ese mismo origen (por ejemplo AsyncCall/Call). En un POST a gc, el cuerpo visible **coincidió con dos valores ficticios de campos texto, longitudes 45 y 34**. Se guardaron únicamente campo/longitud/booleano, no cuerpos/fragmentos, cookies ni cabeceras. No se afirma que se hayan observado datos reales ni que otros cuerpos no contengan datos codificados.

HTML consultado directamente por httpx, también con user-agent de navegador, e index.html del proyecto **no contienen** esos dominios. Los scripts recuperados son opacos y no mostraron los identificadores textuales Kaspersky/KasperskyLab buscados; no se atribuye su firma por esa ausencia/presencia. Registro Windows confirma Kaspersky **21.26.4.406** y procesos avp.exe; sus rutas ejecutables no fueron accesibles, por lo que no se acreditó firma/correlación de ese componente. Producto instalado y nombre del dominio no prueban inocuidad ni ruta física.

**NF-02 pendiente/no aprobado.** Falta atribución comprobada del script a componente/configuración firmados y correlación con la ruta efectiva de red y tratamiento del contenido, con el responsable del entorno y datos ficticios. No se desactivó/reconfiguró antivirus ni se bloquearon/excluyeron solicitudes externas para aprobar. El aborto de red funcional sólo afectó la ruta localhost de revisión. Esto impide declarar cierre integral aunque las pruebas funcionales pasen.

### NF-03: medición real conservada

Equipo: AMD Ryzen 7 5800H, **8 núcleos/16 lógicos**, **15,86 GiB RAM**, Windows build 26200 AMD64, Python 3.11.4, Uvicorn 0.54.0/FastAPI 0.162.0/SQLAlchemy 2.0.57/psycopg 3.3.8/PostgreSQL 18.6. Node 26.13.0/npm 11.20.0 para frontend. Máquina habitual, sin aislamiento de otros procesos Windows; entorno/dependencias ya instalados.

Cinco usuarios/sesiones independientes en ops_test, un proceso API real y cinco clientes HTTP concurrentes. Por endpoint: 10 calentamientos (2/usuario), luego **100 solicitudes** (20/usuario), texto libre normalizado de **10000 caracteres**, componentes declarados válidos y configuración D01. Login/preparación de práctica fuera del tiempo. Medición hasta recepción completa del cuerpo: revisar incluye motor; guardar incluye reevaluación, PostgreSQL y commit (la adquisición previa de token no está en el tiempo de guardar). Se verificaron **110 versiones persistidas**: 10 warmup +100 medidas. Todas las muestras, también errores/lentas si los hubiera, se conservan. P95 = elemento ceil(0,95×N) de la muestra ordenada, posición 95 de 100; no promedio del motor puro.

| Corrida | Endpoint | Muestras/errores | Mediana ms | p95 ms | Máximo ms |
|---|---|---|---|---|---|
| Inicial, 19:20:19Z | revisar | 100/0 | 35,399 | 66,789 | 126,168 |
| Inicial | guardar | 100/0 | 58,120 | 85,149 | 105,069 |
| Final, 19:55:43Z | revisar | 100/0 | 27,663 | **37,938** | 107,228 |
| Final | guardar | 100/0 | 56,685 | **75,819** | 88,565 |

NF-03 aprobado para estos endpoints/volumen/entorno: ambos p95 <2000 ms, cero errores. No se atribuye una optimización entre corridas ni garantía general a la variación. Un intento a las 19:53:46Z fue rechazado **antes de medir**, por puerto 18000 ocupado por el navegador; informe conservado y ejecución repetida secuencialmente, sin descartar muestras. No es un fallo de latencia de una solicitud ni se oculta como corrida aprobada.

### Operación, recuperación y programación

Regresión final repitió restore/diario/purga/contingencia sobre bases ficticias, sin restaurar desarrollo. Último ensayo: restore_test **0,631 s**, edad **1,725 s**; contingencia_test restore **0,628 s**, edad **2,751 s**, arranque/Chrome hasta historial/comparación **3,290 s**, total **3,918 s**. Conserva el dato histórico **5,679 s** con su alcance. Copias recién creadas y entorno instalado, sin medir transferencia externa/instalación de otra máquina ni garantizar continuidad RPO≤24 h/RTO≤4 h.

Tarea: primer intento desde Codex denegado por Windows **0x80070005 PermissionDenied**; no fue rechazo de revisión automática de Codex ni se alteraron permisos globales. Santiago la registró desde PowerShell elevada, misma cuenta, estado Ready. Su 267011/0x41303 significaba todavía no ejecutada, no un respaldo aprobado ([Microsoft](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-error-and-success-constants)). Se comprobó ejecutable/script y se inició con Start-ScheduledTask. **7/11/2026 19:49:54Z**, resultado final **0**; estado del trabajo aprobado, B2=false, una copia retenida y una diaria anterior purgada. No se confunde con la ejecución directa de etapa 05. Próximo disparo: **8/11/2026 05:00Z =02:00 Cordoba**, todavía sin observar. Tampoco se probó cierre de sesión Windows/apagado/reanudación. La tarea instalada queda activa por el pedido operativo; no es un proceso temporal que se deba retirar al cerrar las pruebas.

Paquete de configuración exportado/verificado a las **19:41:53Z** en EntrenadorPromptsRecovery, fuera de repo/DB-backups/diario/keys, ACL privadas; sin identidad age dentro. La extracción se prueba sólo con datos ficticios, no se reemplaza `.env` activo. Custodia offline y copia independiente de identidad/journal/anchor más recientes siguen pendientes; un paquete antiguo no permite ignorar borrados posteriores. B2 sin operaciones reales, no contratación/publicación. Guía de recuperación y comandos en ETAPA06_WINDOWS.md/ETAPA05_OPERACION_WINDOWS.md.

## Comandos y evidencia reproducible

Desde raíz con `.venv\Scripts\python.exe`: `scripts/verify_stage06_browsers.py`, `scripts/verify_stage06_performance.py`, `scripts/verify_stage06_demo.py`, `scripts/verify_startup.py`, `scripts/demo.py preparar` (inicial y repeticiones idempotentes), `scripts/recover_configuration.py exportar --destination ...`, `scripts/manage_backup_task.py instalar/consultar`, `scripts/report_stage06.py`, `-m pip check`, `scripts/check_secrets.py` y `--staged` antes del commit. Desde backend con `..\.venv\Scripts\python.exe`: pytest final con JUnit, pruebas dirigidas de producción/operación/configuración, `-m app.scripts.check_motor`, `-m app.scripts.check_access_roles`. Frontend: npm.cmd run build. Comandos completos en docs/operacion/ETAPA06_WINDOWS.md. No se volcaron secretos ni URLs privadas.

Los auxiliares de navegador usan 18000/15173; la carga sólo 18000; arranque normal 8000/5173. Se ejecutan secuencialmente cuando comparten puertos. Detienen sólo sus propios procesos; PostgreSQL/antivirus y Mailpit preexistente no se detienen. Nuevas bases/roles de otro equipo no se simulan como instalados: SQL nuevo preparado y validación local de esquema/permisos, sin acreditar reinstalación de Windows.

Informes privados/ignorados: `local-data/etapa06-regresion.xml`, `local-data/etapa06/matriz.json`, `flujo-auditoria.json`, `administracion-auditoria.json` y anteriores, `navegadores-resumen.json`, tres archivos rendimiento por fecha, `restauracion-final.json`, `demo.json`; capturas ficticias en las carpetas de etapas 04/05. Archivo de demo y configuración cifrada fuera del repo. Inventario MANIFEST, revisión de índice y ausencia de secretos comprobados antes del commit.

Pruebas adicionales de teclado inicialmente fallaron porque el auxiliar intentaba enfocar un botón todavía deshabilitado durante carga. Se corrigió la sincronización del **auxiliar** esperando habilitación; no se debilitó el comportamiento/expectativa del foco ni se ocultó una falla de la aplicación. Los informes anteriores se conservaron. Ninguna fixture esperada modificada. Errores controlados de rollback/diario son verificaciones aprobadas de rechazo, no omisiones.

## Qué impide el cierre y qué queda fuera

**Bloqueos del cierre integral local:** NF-02 no aprobado por el hallazgo y atribución/ruta sin resolver; NF-01 parcial, faltando lector/revisión humana completa. La revisión general de Santiago se conserva pero no se presenta como certificación. Manual concreto en docs/operacion/ETAPA06_WINDOWS.md.

**Operación pendiente:** observar disparo diario real y ejecución sin sesión interactiva, custodia/transferencia/recuperación independiente de claves y diario vigente, B2 real y su purga de todas las versiones/cargas incompletas. No se garantiza eliminación externa ≤30 días por pruebas locales ni se purga el diario activo sin verificar todas las copias afectadas.

**Académico:** VAL-01/02, revisor externo y participantes educativos no realizados; necesarios antes de pruebas con usuarios. No se inventan dictámenes, participantes ni resultados. SMTP productivo, revisión de la lista común limitada, costos/notebook y documento académico mantienen su alcance previo; no se modificó el DOCX ni sus conclusiones.

## Continuación manual y operativa — 8/11/2026

**Fuente manual: confirmación explícita de Santiago en este chat.** Teclado, foco, confirmaciones, etiquetas, errores, 360 px y zoom correctos en Chrome y Edge. Narrador inicialmente no funcionó en Edge; al abrir una ventana nueva funcionó sin cambiar configuraciones ni código. Se registra el intento inicial y la repetición correcta, sin inventar causa, versión nueva, capturas o dictamen. 06.3/NF-01 básico completado; no certificación WCAG ni validación con participantes. NF-02 sigue pendiente/no aprobado.

**Consulta efectiva de tarea y equipo:** LastRunTime 8/11/2026 09:35:22 -03, resultado 0, próxima ejecución 9/11 02:00 -03; Windows LastBootUpTime 09:26:35. Santiago informa apagado nocturno y encendido aproximadamente 09:30. Tarea con único CalendarTrigger diario 02:00, StartWhenAvailable=true, WakeToRun=false, S4U, nivel mínimo y acción Python/script conocidos. Historial Microsoft-Windows-TaskScheduler/Operational deshabilitado: no hay evento que acredite el disparador. Compatible con ejecución diferida tras encender, **no atribución concluyente** ni prueba de ejecución sin sesión. Microsoft documenta cola y demora predeterminada de diez minutos, que no es una garantía de intervalo exacto: [StartWhenAvailable](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-startwhenavailable). No se activó historial ni se cambió energía, tarea, políticas o antivirus.

**Copia efectivamente verificada** con `scripts/check_scheduled_backup.py`: estado aprobado de 12:35:31.631282Z; copia de 12:35:36.119629Z (09:35:36 local), 52338 bytes, esquema 20261107_0004, manifiesto `tfg-20261108T123536-8ee17afdb1e04ceead58654db37addbe.manifest.json`. Autenticación Fernet del manifiesto, SHA-256/tamaño y descifrado age completo hacia pg_restore --file=dispositivo nulo aprobados; estado sin cambio al terminar. No se imprimió SQL ni se restauró desarrollo/otra base. Retención informada por el trabajo: dos copias, ninguna purga; B2=false. No se presenta como una restauración SQL nueva ni como RPO continuo. Reporte ignorado en local-data/etapa06/respaldo-verificado-*.json, generado el 8/11 a las 15:01:28Z.

**Preparación del ensayo sin sesión:** scripts/ensayar_respaldo_sin_sesion.ps1 copia sólo acción/principal/settings conocidos a una tarea temporal de un disparo futuro, sin modificar la diaria ni pedir contraseña Windows. No se registró ni ejecutó todavía. Sintaxis PowerShell/Python comprobadas; XML final validado por Task Scheduler con TASK_VALIDATE_ONLY. Primer intento de validación en scriptblock no tenía PSScriptRoot; se admitió ejecución explícita desde raíz con verificación de archivo. Segundo intento detectó RunLevel omitido por exportación de Windows; se admitió el valor predeterminado LeastPrivilege, conservando rechazo de valores elevados. Tercer intento aprobó; no se relajó identidad ni acción. Ninguno instaló tareas ni se presenta como prueba sin sesión.

Comandos ejecutados: consulta Get-ScheduledTask/Get-ScheduledTaskInfo, CIM LastBootUpTime y estado del historial; `python scripts/check_scheduled_backup.py`; parser PowerShell, `python -m py_compile scripts/check_scheduled_backup.py`; validación COM RegisterTask con flag 1; regeneración de matriz, inventario y revisión de secretos. Consultas privadas inicialmente denegadas en sandbox, repetidas con autorización sin cambiar ACL. Guía exacta del ensayo en docs/operacion/ETAPA06_WINDOWS.md. Pendientes: realizar ensayo, confirmar intervalo sin sesión y correlacionarlo con tarea/copia; historial disparador, custodia externa/B2 y validación educativa siguen con sus límites.

## Ensayo local sin sesión aprobado — 8/11/2026

**Confirmación manual de Santiago:** cerró sesión Windows a las 16:08 y volvió a ingresar a las 16:27, hora de Córdoba (UTC−03). Es el respaldo del intervalo sin sesión; no se atribuye esa constatación a una auditoría automática de inicios/cierres.

**Verificaciones automáticas consultadas por Codex:** tarea temporal EntrenadorPrompts-Respaldo-EnsayoSinSesion ejecutada a las 16:17:52, resultado 0; copia del 8/11 a las 19:17:53.288423Z =16:17:53 local, 53890 bytes, esquema 20261107_0004. Manifiesto tfg-20261108T191753-10ca80c8e49b4594b02371267ae789d8.manifest.json autenticado; tamaño/SHA-256 y descifrado age completo hacia pg_restore al dispositivo nulo aprobados nuevamente a las 19:31:53Z. Estado de trabajo aprobado y sin cambio durante la verificación; B2=false. El trabajo informa una copia purgada y dos retenidas. No se imprimieron datos ni se restauró SQL.

**Conclusión acotada:** ensayo local con sesión Windows cerrada aprobado por correlación de la confirmación manual del intervalo con tarea y copia verificadas. No acredita disparador diario, restauración SQL de esta copia, continuidad RPO/RTO, B2 ni custodia externa. NF-02 y los demás pendientes conservan su estado.

**Retiro de tarea temporal:** intento mediante el procedimiento documentado rechazado por Windows con Acceso denegado, incluso fuera del sandbox. No fue rechazo de aprobación automática. Se solicitó únicamente el mismo comando desde PowerShell elevada con la cuenta del proyecto; retiro todavía pendiente de confirmación/verificación. La diaria fue consultada antes: Ready/habilitada, intervalo de un día, próximo 9/11/2026 02:00 −03, S4U y StartWhenAvailable=true. Se guardó SHA-256 del XML completo para comparar después; no se modificó su configuración.

Evidencia técnica ignorada: local-data/etapa06/ensayo-sin-sesion-antes-retiro.json y respaldo-verificado-*.json de las 19:31:53Z. El archivo de preparación ensayo-sin-sesion.json se conserva como antecedente, sin convertir su booleano inicial en auditoría de sesiones. No se eliminan respaldos ni evidencia al retirar la tarea.

### Retiro exclusivamente temporal — comprobación completada

Tras el Acceso denegado inicial, Santiago confirmó haber ejecutado el comando documentado desde su terminal elevada. Consulta posterior de Codex a las **19:34:35Z (16:34:35 Córdoba)**: EntrenadorPrompts-Respaldo-EnsayoSinSesion **ausente**; EntrenadorPrompts-Respaldo **instalada, Ready y habilitada**. SHA-256 del XML exportado idéntico al tomado antes del intento: no cambió acción, principal, settings ni trigger. Intervalo **un día**, próxima ejecución **9/11/2026 02:00 −03**. No se ejecutó ni reconfiguró la diaria para comprobarlo, ni se borraron copias/evidencia. La primera denegación se conserva como incidencia resuelta mediante intervención local de Santiago; no como retiro exitoso desde Codex.

Comandos efectivos: procedimiento ensayar_respaldo_sin_sesion.ps1 -Accion eliminar (intento Codex denegado, ejecución local confirmada por Santiago); Get-ScheduledTask/Get-ScheduledTaskInfo y Export-ScheduledTask antes/después, comparación SHA-256 completa. Reportes ignorados: ensayo-sin-sesion-antes-retiro.json y ensayo-sin-sesion-comprobacion-posterior.json. El ensayo y retiro quedan aprobados en su alcance local. Disparador diario, restauración SQL de esta copia, B2 y custodia externa no se dan por probados. Matriz regenerada, inventario verificado y revisión de secretos sobre índice antes del commit; no se repite regresión funcional por este cambio documental.

## Contraste de NF-02 — 8/11/2026, posterior a los ensayos de respaldo

Observación manual de Santiago con PRUEBA_NF02_ABC123: tres coincidencias locales en 5173; petición inspeccionada Ping/TimerCallback. Archivo histórico flujo-auditoria.json, solicitud externa índice 14: POST XHR a gc.kis.v2.scr.kaspersky-labs.com, 3517 bytes, AsyncCall/Call y dos coincidencias de campo fuente texto 45/34. **No se registraron ruta, requestId, hora, acción ni campo del cuerpo remoto.** Longitudes compatibles con Tarea/Contexto de CP-31/CP-01, sin identificación inequívoca sólo por longitud. No se atribuye ese POST a Ping ni a un clic específico.

Repetición acotada CP-31 por pantallas en Chrome/Edge, revisar y repetir con marcador ficticio, sólo PostgreSQL de pruebas: 23 solicitudes externas por navegador, **cero cuerpos externos visibles con coincidencias** y dos revisiones locales con textos/marcador. No guardó versiones ni modificó antivirus/bloqueó solicitudes. GET periódicos Ping/TimerCallback y otros POST observados; no reproducido el POST histórico de 3517 bytes. Reportes previos conservados. **NF-02 sigue pendiente/no aprobado**: no es evidencia nueva de filtración ni una prueba de ausencia global; atribución física/tratamiento e identificación exacta histórica siguen sin confirmar. Detalle, campos conocidos y límites en docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md.

Comando ejecutado: `& .\.venv\Scripts\python.exe scripts\check_nf02_focused.py`, salida 0 (caso ejecutado, no aprobación NF-02). Reporte ignorado nf02-focalizado-20261108T201654116172Z.json. Cinco comprobaciones puras del auxiliar aprobadas después de corregir sanitización de rutas para futuras ejecuciones; no se altera el reporte original ni se declara ejecutado el navegador con esa corrección posterior. Regresión funcional/build no repetidos: no cambió código de aplicación. Matriz/inventario y secretos revisados para el commit local.

## Preparación del disparador diario y custodia — 8/11/2026

Santiago habilitó Microsoft-Windows-TaskScheduler/Operational mediante el auxiliar en PowerShell elevada a **8/11 21:58:10 Córdoba =9/11 00:58:10Z**. Se conserva la denegación inicial de Windows desde Codex como incidencia resuelta con intervención local, no como rechazo de aprobación automática. Comprobación independiente de Codex a 00:59:59Z: historial activo, tarea Ready/habilitada y XML completo idéntico a la referencia. Próxima 9/11 02:00 −03, intervalo de un día, StartWhenAvailable=true y WakeToRun=false. No se modificaron programación, acciones, principal, políticas, tamaño/retención del canal ni se ejecutó la diaria.

Consulta del auxiliar a **9/11 01:00:25Z =8/11 22:00:25 Córdoba**: cero eventos del día 9/11 local, esperado antes del horario. **Disparador diario pendiente**: correlacionar tarea e instancia en 107/100/200/201/102, diferenciar 110, resultado del trabajo y copia nueva. No habilitación retroactiva ni aprobación por LastTaskResult anterior. El canal incluye todas las tareas del equipo; el informe guarda sólo la diaria y campos permitidos sin mensajes completos/usuarios. Evidencia ignorada en local-data/etapa06/disparador-diario-preparacion.json, disparador-diario-preparacion-comprobada.json y disparador-diario-consulta-*.json. Instrucciones exactas en docs/operacion/DISPARADOR_DIARIO_WINDOWS.md.

Custodia externa revisada en código de exportación/verificación/extracción, diario bajo bloqueo y verificación/restauración de respaldos. Guía docs/operacion/CUSTODIA_RECUPERACION_WINDOWS.md: conservar conjuntos backup.age/manifest.json/manifest.auth completos, paquete cifrado actualizado con local.env/diario/clave/ancla, identidad privada age protegida y separada, código/locks/guías e inventario sin secretos. Diario vigente después de borrados, no sólo snapshot antiguo. Clave original sin frase requiere protección adicional antes de transportarla; age admite identidad cifrada por frase para verificar copias externas a NUL sin mostrar contenido. Comandos revisados en documentación oficial; **transferencia, custodia efectiva, uso de clave externa y recuperación de otro equipo no ejecutados ni aprobados**. No se copiaron claves/paquetes a un destino externo ni se tocó desarrollo/B2.

Comprobaciones de este incremento: parser PowerShell aprobado; preparación ejecutada por Santiago y contrastada por Codex; consulta real del intervalo futuro sin eventos ejecutada correctamente. Procesamiento de una instancia diaria nueva aún no ejercitado, sin inventar eventos. No se repiten las 317 pruebas ni el build porque no cambió la aplicación. Matriz y MANIFEST actualizados; secretos e índice revisados antes del commit. Fuentes de comandos: [Microsoft wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil), manifiesto local Microsoft-Windows-TaskScheduler y [age oficial](https://github.com/FiloSottile/age#usage).

## Disparo diario del 9/11/2026 — comprobado

Lectura de registros existentes: evento 107 de horario a **02:00:01.8375713 Córdoba**, seguido de 100/200/201/102 para la misma instancia {bcaabcf6-f442-4948-bcd6-2851a1bf8690}; acción completada con resultado **0** a 02:00:09.4643375. XML completo idéntico a la referencia del 8/11; tarea Ready/habilitada, intervalo diario y próxima **10/11 a las 02:00 Córdoba**. Sin inicio manual ni cambios de tarea/configuración/antivirus.

Copia de **02:00:08.436255**, 54555 bytes, esquema 0004: reporte existente del verificador de Santiago acredita autenticidad/SHA-256/descifrado completo. Codex leyó ese reporte, el estado del trabajo y volvió a autenticar el manifiesto/comprobar tamaño y hash, sin descifrar de nuevo, generar respaldo o restaurar SQL. Tres retenidas/cero purgadas y B2=false. Se aprueba este disparo automático concreto; no continuidad/RPO/RTO, sesión cerrada de hoy ni restauración SQL de esa copia. B2, custodia externa y NF-02 conservan sus pendientes separados. Detalle y RecordIds en docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md.
