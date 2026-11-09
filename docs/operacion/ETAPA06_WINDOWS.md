> Guía técnica conservada del desarrollo. Las observaciones sobre el «equipo actual» corresponden al entorno original. Para una instalación nueva, comenzar por [INSTALACION_WINDOWS.md](../INSTALACION_WINDOWS.md). Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Instalación, verificación y demostración en Windows

**Actualización 9/11:** disparo por horario comprobado por instancia común en 107/100/200/201/102, resultado 0 y copia nueva. XML intacto, próxima 10/11 02:00 Córdoba. Ver docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md. Las indicaciones de preparación y su estado pendiente del 8/11 que siguen son antecedentes; no es necesario volver a habilitar o iniciar la tarea. B2/custodia externa/NF-02 y restauración SQL de esta copia conservan sus límites.

Estado de etapa 06 en docs/evidencias/EVIDENCIA_ETAPA06.md e docs/evidencias/INFORME_FINAL_ETAPA06.md. No hay cierre integral: NF-02 no aprobado. Accesibilidad básica confirmada manualmente por Santiago el 8/11, incluida repetición correcta de Narrador en Edge. Los recorridos funcionales, pruebas y ensayos locales tienen evidencia separada. No se publica ni despliega.

## Equipo actual: arranque y parada

Conservar `.env`, claves, roles y datos existentes. Reiniciar API/frontend para cargar los cambios. Tres terminales PowerShell desde la raíz (reutilizar Mailpit si ya está iniciado):

```powershell
# Terminal 1
& .\local-data\mailpit\mailpit.exe --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025 --disable-version-check --smtp-disable-rdns --quiet
```

```powershell
# Terminal 2: desarrollo
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers
```

```powershell
# Terminal 3
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run dev
```

Aplicación `http://127.0.0.1:5173`; API `http://127.0.0.1:8000/health`; Mailpit `http://127.0.0.1:8025`. Detener cada proceso con Ctrl+C. No detener PostgreSQL compartido. `verify_startup.py` exige 8000/5173 libres, elimina variables de proyecto heredadas de sus subprocesos y prueba dos inicios con `.env` y conteos conservados; no usa servidores ajenos como prueba propia.

## Instalación nueva: procedimiento separado

No ejecutar el aprovisionamiento siguiente sobre este equipo: sus roles/bases ya existen. Combinación comprobada: Windows/PowerShell 5.1 o 7, Git 2.56.0.windows.4, Python 3.11.4, Node 26.13.0/npm 11.20.0, PostgreSQL 18.6/clientes 18, Mailpit 1.33.0 y age 1.3.2. Dependencias fijadas en los locks actuales. No se requiere Docker, WSL ni cambio de política PowerShell.

En una copia nueva del código, desde su raíz:

```powershell
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { python -m venv .venv }
& .\.venv\Scripts\python.exe scripts\bootstrap_pip_windows.py
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" ci
Pop-Location
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
```

Con PostgreSQL 18 instalado en Windows y escuchando en 127.0.0.1:5432, crear sólo los recursos NUEVOS del proyecto:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --set=ON_ERROR_STOP=on --file=scripts/crear_entorno_nuevo.sql
```

Pide las contraseñas sin eco con `\password`. Crea `entrenador_app` y `entrenador_migracion`, sin superusuario/CREATEDB/CREATEROLE; ambas bases propias de migración, ejecución sin CREATE/TEMP. Rechaza recursos existentes y no reemplaza credenciales. No usar el antiguo traslado de roles de etapa 03 en una base vacía: requería tablas/funciones ya existentes.

Completar localmente `.env`: POSTGRES_PASSWORD de entrenador_app y MIGRATION_PASSWORD diferente de entrenador_migracion; hosts 127.0.0.1 y puerto 5432. Dejar DATABASE_URL/TEST_DATABASE_URL vacíos si se usan esas variables. No enviar contraseñas al chat. Después:

```powershell
& .\.venv\Scripts\python.exe scripts\prepare_access_secret.py
& .\.venv\Scripts\python.exe scripts\prepare_review_secrets.py
& .\.venv\Scripts\python.exe scripts\install_mailpit.py
& .\.venv\Scripts\python.exe scripts\install_age.py
& .\.venv\Scripts\python.exe scripts\prepare_operation_local.py
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m alembic upgrade head
& ..\.venv\Scripts\python.exe -m app.scripts.seed
& ..\.venv\Scripts\python.exe -m app.scripts.prepare_test_db
Pop-Location
```

Las migraciones conservan el esquema histórico; los permisos iniciales de acceso antes se provisionaban fuera de Alembic. En la instalación nueva completar ese paso **después** de migrar, como propietario:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=entrenador_migracion --dbname=entrenador_prompts --password --set=ON_ERROR_STOP=on --file=scripts/permisos_ejecucion_acceso.sql
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=entrenador_migracion --dbname=entrenador_prompts_test --password --set=ON_ERROR_STOP=on --file=scripts/permisos_ejecucion_acceso.sql
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
& ..\.venv\Scripts\python.exe -m app.scripts.manage_access crear-admin
Pop-Location
```

El bloque de permisos fue ejecutado y probado tras migrar un esquema ficticio realmente vacío; no se ejecutó el creador de roles/bases sobre la instalación existente. No hay una instalación independiente de Windows nueva acreditada. Crear administrador solicita clave oculta; no hay contraseña pública ni usuarios seed. Bases adicionales de pruebas/contingencia: procedimiento docs/operacion/ETAPA05_OPERACION_WINDOWS.md y `scripts/crear_bases_operacion.sql`, sólo con recursos propios y sin alterar otra instancia.

## Verificación reproducible

Ejecutar **secuencialmente** los auxiliares que usan 18000/15173: rechazan puertos ocupados y no detienen a sus dueños.

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\etapa06-regresion.xml
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
Pop-Location
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run build
Pop-Location
& .\.venv\Scripts\python.exe scripts\verify_stage06_browsers.py
& .\.venv\Scripts\python.exe scripts\verify_stage06_performance.py
& .\.venv\Scripts\python.exe scripts\verify_startup.py
& .\.venv\Scripts\python.exe -m pip check
& .\.venv\Scripts\python.exe scripts\check_secrets.py
& .\.venv\Scripts\python.exe scripts\report_stage06.py
```

El navegador devuelve 2 con flujo funcional aprobado y NF-02 pendiente; 1 si hay fallo funcional/accesibilidad detectado. No interpretar 2 como aprobación integral. Las mediciones se conservan por fecha, incluidos intentos rechazados, con 100 revisar/100 guardar, cinco usuarios y diez calentamientos por endpoint. No ejecutar cambios de catálogo/carga/restauración contra desarrollo. `pytest` verifica destino y utiliza únicamente bases ficticias; la prueba de esquema vacío exige cero usuarios/prácticas y tablas conocidas antes de reconstruir public en restore_test.

## Demostración separada y reproducible

Base dedicada `entrenador_prompts_demo`, ya creada por Santiago y verificada; queda fuera de las restauraciones destructivas. Se repitió la preparación sin duplicar cuentas/práctica/V1/V2; se comprobó desde Chrome contra API/Vite. No se insertaron esos datos en desarrollo ni en los historiales de pruebas automáticas.

Para otra instalación, crear primero sólo la base demo con `psql` y `scripts/crear_base_demo.sql`. En el equipo actual:

```powershell
& .\.venv\Scripts\python.exe scripts\demo.py preparar
```

Genera contraseñas aleatorias únicamente en `%LOCALAPPDATA%\EntrenadorPromptsDemo\credenciales.json`, con ACL privadas; no las imprime ni las incorpora a seeds/documentos/Git. Abrir ese archivo sólo en tu editor local, sin compartir su contenido. Si existe lo conserva. Si la cuenta ya existe y falta el archivo, se detiene; no restablece claves o estados silenciosamente. Las cuentas son `demo.usuario@example.invalid` y `demo.admin@example.invalid`; no corresponden a personas reales.

Usar Mailpit y frontend con los comandos de las terminales 1/3. En la **terminal 2 sustituir el backend de desarrollo**, sin editar `.env`, por:

```powershell
& .\.venv\Scripts\python.exe scripts\demo.py api
```

No iniciar ambos backends en 8000. Entrar en 5173 con la cuenta ficticia; abrir Historial → V2 → Comparar: V1 3/6, V2 6/6, +50 pp, resolución 100 %, avisos de límites. Copiar únicamente por botón. Crear otro objetivo propio y probar libre declarando componentes; usar sólo texto ficticio y confirmar cada coincidencia actual. Ingresar con el administrador ficticio para demostrar borrador/publicación y bloqueo de una cuenta ficticia en Chrome/Edge independientes. Desactivar/eliminar sólo datos de demo. Repetir preparación recupera los IDs de los ejemplos, no reescribe historia; si se alteraron reglas/estados/claves, conservar esos cambios y resolverlos expresamente. Recuperación por correo se consulta en Mailpit local. Ctrl+C detiene cada servidor; el script no modifica la base/URL de desarrollo en `.env`.

## Recuperación de configuración, diario y claves

El dump no incluye `.env` ni el diario independiente. Ubicaciones actuales: `%LOCALAPPDATA%\EntrenadorPrompts\diario`, `%LOCALAPPDATA%\EntrenadorPromptsKeys` y copias en `%LOCALAPPDATA%\EntrenadorPrompts\backups`. No imprimir contenidos. Santiago confirmó rotación de contraseña PostgreSQL y CSRF; conexiones y configuración actuales verificadas. No se solicitaron valores anteriores ni se puede acreditar una comparación con ellos.

Paquete de recuperación cifrado ya exportado y verificado en `%LOCALAPPDATA%\EntrenadorPromptsRecovery`, separado del repo/copias/diario/claves:

```powershell
& .\.venv\Scripts\python.exe scripts\recover_configuration.py exportar --destination "$env:LOCALAPPDATA\EntrenadorPromptsRecovery"
$paquete = Read-Host 'Ruta del paquete cifrado de configuración'
& .\.venv\Scripts\python.exe scripts\recover_configuration.py verificar --file $paquete
$destino = Read-Host 'Carpeta privada nueva o vacía, fuera del repo y directorios activos'
& .\.venv\Scripts\python.exe scripts\recover_configuration.py extraer --file $paquete --destination $destino
```

El paquete contiene `.env` como local.env, diario, clave Fernet y ancla, con manifiesto interno; **no contiene la identidad privada age**. La verificación real del paquete activo fue en memoria; extracción/roundtrip se probaron con configuración ficticia. Extraer no sobrescribe nada activo, rechaza destinos con archivos y comprueba el diario recuperado. No se vuelve a habilitar acceso automáticamente.

Guardar una copia protegida de `backup.agekey` **por separado**, en un medio independiente/cifrado bajo custodia del responsable; esa custodia/transferencia física sigue sin probarse. Sin ella no se puede descifrar el paquete si se pierde el disco. Las credenciales de demo son ficticias y se resguardan aparte si se quieren conservar; no son credenciales públicas.

Un paquete refleja el diario a su fecha de exportación: no sustituye al diario independiente más reciente. Antes de recuperar una base, obtener también todas las solicitudes posteriores, clave y ancla vigentes. Si no se puede demostrar su integridad/vigencia, mantener CONNECT cerrado. No restaurar un diario antiguo para hacer coincidir el ancla. Volver a configurar rutas absolutas en una nueva máquina sin cambiar secretos inadvertidamente; coordinar credenciales con PostgreSQL y revocar sesiones/recuperaciones antes de abrir, según docs/operacion/ETAPA05_OPERACION_WINDOWS.md. No se ensayó pérdida de disco/otro host ni se acredita redundancia externa.

## Tarea instalada y pendientes manuales

Santiago registró la tarea con su misma cuenta desde PowerShell elevada. Se verificó que invoca el Python/script conocidos. `Start-ScheduledTask` produjo una ejecución con resultado 0 y estado de copia/purga aprobado; no equivale a observar el disparo diario. Consultar a partir del **8/11/2026 a las 02:00 Cordoba**:

```powershell
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py consultar
```

Se espera fecha reciente y LastTaskResult=0, además de manifiesto nuevo y estado-tarea.json aprobado. No compartir contenidos de `.env`, claves, cuerpos ni cookies. 267011/0x41303 significa todavía no ejecutada, no un respaldo realizado; [referencia Microsoft](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-error-and-success-constants). No cambiar la zona global. B2 permanece deshabilitado y sin contacto; carga/descarga, todas sus versiones/multipart/purga y custodia externa quedan pendientes.

Revisión básica completada el 8/11; para futuras regresiones repetir teclado/lector de pantalla en registro, constructor, resultados, panel y confirmaciones a 360 px/escritorio; comprobar lectura de errores, foco, orden y acciones sin color. NF-02: con el responsable del entorno, atribuir el script a su componente firmado/configuración y correlacionar solicitudes/cuerpos ficticios con la ruta de red efectiva, sin desactivar la protección. La auditoría sólo registra origen/iniciadores/metadatos; dos valores ficticios coincidieron en un POST externo. No aprobar por bloquear solicitudes ni por ausencia de coincidencias en otra muestra. Validación externa de reglas sigue requerida antes de participantes educativos.

## Ensayo de respaldo con sesión de Windows cerrada

**Resultado vigente 8/11:** ensayo local aprobado: Santiago confirmó 16:08–16:27 sin sesión; tarea 16:17:52 resultado 0 y copia 16:17:53 autenticada/SHA-256/descifrada, repetido por Codex. No prueba disparador diario, restauración SQL de esta copia ni B2. Retiro realizado por Santiago desde PowerShell elevada tras Acceso denegado inicial; Codex verificó temporal ausente y diaria instalada con XML idéntico, intervalo diario y próxima 9/11 a las 02:00 Córdoba. Los pasos de abajo son la guía reproducible, no una solicitud de repetir un ensayo ya aprobado.

Estado 8/11: ejecución 09:35:22 resultado 0 y copia autenticada/descifrada. StartWhenAvailable=true y arranque 09:26:35 son compatibles con ejecución diferida; historial deshabilitado impide acreditar el disparador. No es prueba sin sesión. No hace falta iniciar API, frontend ni Mailpit: PostgreSQL debe seguir disponible como servicio.

1. Guardá tu trabajo. Abrí PowerShell **como administrador con tu misma cuenta**, ubicándote en la raíz. Este comando ejecuta el auxiliar local sin modificar la política de ejecución (su XML ya fue validado, no instalado):

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\ensayar_respaldo_sin_sesion.ps1))) -Accion preparar -Minutos 15
```

2. Anotá la hora que muestra. Crea únicamente `EntrenadorPrompts-Respaldo-EnsayoSinSesion`, copia S4U/acción/nivel mínimo y fija un único disparo en 15 minutos. No cambia la diaria. Dejá el equipo conectado a corriente y encendido, sin suspensión durante el intervalo. Si no podés garantizarlo, el ensayo queda pendiente; no cambies políticas globales.
3. **Cerrá sesión de Windows** desde Inicio — tu cuenta — Cerrar sesión antes de esa hora. No basta Win+L, cambiar usuario o desconectar una sesión remota. No apagues el equipo. Permanecé sin sesión hasta cinco minutos después del horario mostrado. El auxiliar no cierra sesión por vos.
4. Volvé a ingresar y, desde la raíz, consultá y verificá (elevá sílo si Windows deniega lectura):

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\ensayar_respaldo_sin_sesion.ps1))) -Accion consultar
& .\.venv\Scripts\python.exe scripts\check_scheduled_backup.py
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py consultar
```

Esperado: tarea temporal con fecha/hora dentro del intervalo realmente sin sesión y resultado 0; copia NUEVA correspondiente, autenticidad/SHA-256/descifrado completo aprobados. La diaria conserva programación. Si hay demora y se ejecuta después de volver a ingresar, fallo o copia anterior, no aprobar este ensayo. Compartí sílo horas de cierre/reingreso, LastRunTime/LastTaskResult y resultado seguro del verificador, sin claves ni archivos de copia. Tu confirmación del intervalo es necesaria: el auxiliar no audita inicios/cierres de sesión y no marca aprobado automáticamente. Un cero no prueba por sí solo ausencia de sesión. Verificador no restaura SQL ni garantiza RPO continuo.

5. Una vez conservada la evidencia, retirar **sílo** la tarea temporal (mismo contexto de permisos):

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\ensayar_respaldo_sin_sesion.ps1))) -Accion eliminar
```

No elimina la diaria ni copias/evidencia. Si ya existe el ensayo, consultar antes de retirar/preparar otro; no lo sobrescribe. Su acción usa el respaldo/purga normales del proyecto y sílo el destino configurado. B2 permanece deshabilitado. No se registra este procedimiento como realizado hasta contar con ejecución y confirmación del intervalo.

## Contraste acotado de NF-02

Resultado y limitaciones vigentes en docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md. Se ejecutó únicamente el constructor guiado CP-31 (revisión sin guardar y repetición con marcador ficticio) contra la base de pruebas, con Chrome y Edge. No se reprodujo la coincidencia externa histórica; no se aprueba NF-02 ni se atribuyen sus campos/acción faltantes. Para repetir ese mismo ensayo con 18000/15173 libres:

```powershell
& .\.venv\Scripts\python.exe scripts\check_nf02_focused.py
```

Salida 0 significa caso ejecutado, no garantía de privacidad. El auxiliar no cambia antivirus, no bloquea solicitudes y conserva sólo metadatos; una coincidencia negativa no descarta contenido codificado o eventos fuera de la ventana observada. Crea/limpia sólo su cuenta ficticia y prácticas dependientes en entrenador_prompts_test, no datos de desarrollo. No genera HAR ni guarda cuerpos, credenciales o tokens. No hace falta repetirlo para dar por ejecutada la comprobación ya documentada.

## Historial diario y custodia externa — preparación del 8/11

Historial habilitado por Santiago el 8/11 21:58 Córdoba y comprobado activo por Codex, con XML diario idéntico. Disparador del 9/11 02:00 pendiente: pasos y criterios de correlación en docs/operacion/DISPARADOR_DIARIO_WINDOWS.md. No volver a iniciar/reprogramar la tarea para esta comprobación. Guía detallada de material externo, identidad age cifrada separada y verificación sin extraer secretos en docs/operacion/CUSTODIA_RECUPERACION_WINDOWS.md. Custodia/transferencia/recuperación externas y B2 no se consideran realizados por preparar esas instrucciones.

## Activación versionada del detector numérico D36

En el equipo actual ya está publicada C6 v2 con cuatro detectores; reiniciar la API para cargar motor 1.1.0. En instalación nueva, después de Alembic/seeds/permisos de acceso, desde backend ejecutar `& ..\.venv\Scripts\python.exe -m app.scripts.enable_numeric_detector --entorno desarrollo`. La segunda ejecución es idempotente. No sustituye reglas/históricos ni cambia aplicabilidad/indicadores. Ejemplos, pruebas y recorrido de pantalla en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md.
