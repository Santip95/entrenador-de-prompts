> Guía técnica conservada del desarrollo. Las observaciones sobre el «equipo actual» corresponden al entorno original. Para una instalación nueva, comenzar por [INSTALACION_WINDOWS.md](../INSTALACION_WINDOWS.md). Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Administración y operación local — etapa 05

Todo se ejecuta desde la raíz en PowerShell, con la `.venv` existente. No requiere Docker, WSL ni cambiar la política de ejecución. El panel funcional administra catálogo/cuentas; las copias y las claves quedan fuera del panel.

## Abrir la aplicación y crear el primer administrador

Tres terminales independientes, abiertas mientras se usa la aplicación:

```powershell
# Terminal 1: correo local
& .\local-data\mailpit\mailpit.exe --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025 --disable-version-check --smtp-disable-rdns --quiet
```

```powershell
# Terminal 2: API
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers
```

```powershell
# Terminal 3: frontend y proxy
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run dev
```

Abrir `http://127.0.0.1:5173`; Mailpit: `http://127.0.0.1:8025`; salud: `http://127.0.0.1:8000/health`. Ctrl+C en cada terminal detiene su proceso. No detener PostgreSQL ni procesos ajenos.

Desde una cuarta terminal, crear **una cuenta administradora nueva**, sin credenciales públicas ni seeds de usuarios:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.manage_access crear-admin
Pop-Location
```

Solicita correo y dos entradas ocultas de la contraseña (15–128 caracteres). No se escribe la clave en argumentos ni Git. Si el correo ya existe, se rechaza sin reemplazarlo. El comando anterior `promover-admin --correo ...` conserva su uso para una cuenta activa ya registrada y revoca sus sesiones. Estas acciones usan la credencial de migración local; no hay cambio público de rol. El comando de creación también permite recuperar la administración mediante otra cuenta nueva si el operador técnico conserva sus credenciales. No probar esta recuperación con una identidad real ni borrar un administrador de desarrollo para demostrarla.

## Recorridos manuales pendientes del usuario

Usar datos ficticios. En etapa 06 Santiago confirmó revisión general de los recorridos que probó; no comunicó detalle por caso y no se inventa. La lista siguiente queda como guía reproducible, sin equiparar automatización o esa confirmación general con accesibilidad humana completa:

1. Ingresar como administrador y abrir **Administración**. Crear un desafío con código nuevo, título, consigna y seis configuraciones válidas. Guardar borrador. En otra cuenta, recargar inicio: no aparece. Publicarlo desde el panel; al recargar aparece. Editar un borrador lo conserva borrador; editar uno publicado valida y publica una revisión completa.
2. Guardar V1 en una práctica ficticia. En **Reglas**, crear una versión desde C2; ajustar un mensaje permitido y guardarla inactiva. Publicarla. Guardar V2: V1 conserva sus textos/evaluación; la comparación informa configuración distinta y no calcula delta ni resolución. Las condiciones del ejercicio se cambian en **Desafíos**; el tipo de cada regla y AND son fijos. C6 admite sólo los tres detectores conocidos, sin regex propias.
3. Desactivar un desafío usado. El historial conserva lectura y copia; el servidor rechaza revisión/guardado nuevos. No hay botón ni ruta para borrar reglas/desafíos históricos. Desactivar una regla requerida produce error de configuración, no un criterio omitido.
4. Ingresar con una misma cuenta ficticia en Chrome y Edge, o perfiles realmente independientes. Desde otra sesión administradora, **Cuentas → Bloquear**. Pedir historial en ambos: exige ingresar y retira lo privado. Desbloquear no revive cookies antiguas. El último administrador habilitado no se puede restringir ni eliminar; la comprobación es transaccional y se serializa con otras operaciones administrativas.
5. Desde historial o resultados de una práctica ficticia, **Eliminar esta práctica**, leer el aviso y confirmar su casilla. Desaparecen todas sus versiones, evaluaciones y alertas. Otra práctica debe conservarse. No existe borrado de versiones individuales.
6. En **Perfil → Eliminar mi cuenta**, ingresar la clave actual y confirmar la casilla. Se retira la cuenta y sus dependencias; la otra sesión deja de acceder. El aviso distingue activo, diario de borrados y copias rotativas, con máximo previsto de 30 días y verificación externa pendiente.
7. Revisar teclado, etiquetas, errores, foco y lectura a 360 px y escritorio. Las comprobaciones automáticas no sustituyen accesibilidad humana completa. NF-02 sigue pendiente por los orígenes ajenos observados; no desactivar el antivirus para obtener una aprobación.

## Configuración protegida ya preparada en este equipo

`scripts/prepare_operation_local.py` creó directorios privados con ACL del usuario y SYSTEM. Sólo completa valores ausentes, nunca reemplaza claves, credenciales ni un diario existente. Si falta la clave de un diario existente, falla en vez de regenerarla.

- Copias: `%LOCALAPPDATA%\EntrenadorPrompts\backups`.
- Diario cifrado: `%LOCALAPPDATA%\EntrenadorPrompts\diario\borrados.fernet`.
- Identidad privada age, clave Fernet y ancla: `%LOCALAPPDATA%\EntrenadorPromptsKeys`, separados del repositorio y de las copias.
- `.env` contiene las rutas `BACKUP_DIRECTORY`, `BACKUP_IDENTITY_FILE`, `DELETION_JOURNAL_LOCATION`, `DELETION_JOURNAL_KEY_FILE`, `DELETION_JOURNAL_ANCHOR_FILE` y el destinatario público `BACKUP_ENCRYPTION_RECIPIENT`. No publicar `.env` ni esos archivos.

Para una instalación nueva, después de configurar PostgreSQL y `.env`:

```powershell
& .\.venv\Scripts\python.exe scripts\install_age.py
& .\.venv\Scripts\python.exe scripts\prepare_operation_local.py
```

age 1.3.2 oficial, SHA-256 fijado, cifra el formato personalizado de pg_dump; PyCA cryptography 50.0.2 usa la receta Fernet para el diario y autenticar manifiestos. La clave privada de respaldo sólo se necesita en operación/verificación local; un despliegue deberá separarla del servidor y disponer de una copia offline protegida. Aquí se comprobó separación de directorios/ACL, no custodia offline ni redundancia de otro equipo. No retirar ni rotar estas claves sin un procedimiento de conservación de las copias existentes.

El diario independiente contiene únicamente UUID técnicos (solicitud, recurso y titular), tipo y fechas de solicitud/completado; no correos ni textos. Primero se confirma durablemente el diario, después se elimina en PostgreSQL y, tras el commit, se completa el registro. Un fallo SQL deja una solicitud pendiente; se puede reintentar. Un fallo al completar no anuncia éxito aunque el activo ya se haya borrado. Un reintento de práctica propia ya registrada devuelve 204; tras borrar cuenta la sesión ya no sirve y obtiene 401. Ambas situaciones mantienen el borrado idempotente. **No borrar el diario ni su ancla para arreglar un error.** Corrupción, pérdida o desacuerdo impiden borrar/restaurar con éxito. Un corte entre escrituras puede exigir conciliación técnica; no se reconstruye automáticamente un diario vacío.

## Copia y restauración ficticia aislada

Santiago creó las bases `entrenador_prompts_ops_test`, `entrenador_prompts_restore_test` y `entrenador_prompts_contingencia_test`, propietarias de `entrenador_migracion`. Las credenciales existentes se conservan. El script administrativo está en `scripts/crear_bases_operacion.sql`; no toca desarrollo ni roles ajenos. La restauración rechaza desarrollo, la base habitual de pruebas y cualquier nombre arbitrario.

Para reproducir todo el ensayo, incluidos datos ficticios, copia, borrados completados/pendientes, restauraciones, sesiones inválidas y comparación histórica:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest tests\operations\test_backups.py -q
Pop-Location
```

Este ensayo utiliza sus propias claves de diario y destino temporal, preserva el diario activo y limpia sólo los usuarios ficticios que creó en las tres bases identificadas. Deja un informe técnico sin datos personales en `local-data/etapa05/restauracion.json`. La prueba negativa final deja CONNECT de aplicación revocado en `entrenador_prompts_restore_test` deliberadamente; el operador propietario puede inspeccionarla. La siguiente restauración válida vuelve a habilitarlo después de verificar todo.

También se puede generar una copia local **sólo del origen ficticio** para comprobar los comandos:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.operate preparar-pruebas --database entrenador_prompts_ops_test
& ..\.venv\Scripts\python.exe -m app.scripts.operate backup --database entrenador_prompts_ops_test
$manifiesto = Read-Host 'Ruta del manifiesto recién impreso para la copia ficticia'
& ..\.venv\Scripts\python.exe -m app.scripts.operate restore --database entrenador_prompts_restore_test --manifest $manifiesto
Pop-Location
```

No seleccionar una copia de desarrollo para este ensayo: puede contener información real. La salida del respaldo indica el manifiesto, nunca secretos. Se verifica el archivo cifrado completo reconstruyendo SQL hacia el dispositivo nulo, no sólo su índice. No se escribe un dump en claro. El manifiesto autenticado contiene fecha UTC, origen técnico, versión de aplicación/esquema, bytes y SHA-256 del cifrado. Las contraseñas se transmiten sólo mediante el entorno privado del subproceso, no en argumentos o logs.

Antes de restaurar, cerrar procesos/conexiones de aplicación al destino aislado. Se revoca CONNECT de aplicación y PUBLIC en un commit independiente; si hay conexiones existentes se aborta antes de restaurar. Se verifica copia y diario, se restaura, se reaplican **todos** los borrados pendientes/completados, se invalidan sesiones y recuperaciones y se comprueba integridad. Sólo después se habilita CONNECT. Una excepción lo deja cerrado. No copiar un diario viejo desde el mismo respaldo: se necesita el diario independiente más reciente, su clave y ancla. Para otro equipo deben transferirse protegidos y por una vía separada; esa transferencia externa no fue ensayada.

## Tarea diaria y retención

```powershell
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py preparar
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py validar
# Sólo cuando decidas habilitar la ejecución persistente:
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py instalar
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py consultar
# Para retirarla:
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py eliminar
```

**Estado histórico de etapa 05:** XML validado con TASK_VALIDATE_ONLY, trabajo directo una vez y tarea no registrada entonces. **Actualización etapa 06:** Santiago instaló la tarea, y ejecución mediante Start-ScheduledTask comprobada con resultado 0 a 7/11/2026 19:49:54Z. Falta observar disparo diario y ejecución sin sesión Windows. No repetir instalación; consultar su estado según docs/operacion/ETAPA06_WINDOWS.md. `instalar` usa S4U y privilegios mínimos, sin pedir/guardar contraseña de Windows; puede necesitar permisos locales del Programador de tareas. No se modifican esos permisos ni la política global como atajo. La tarea invoca directamente `.venv\Scripts\python.exe`, no depende de una terminal abierta, y guarda estado técnico en el destino de copias. No se ha probado ejecución sin sesión interactiva ni despertar/reanudación.

El inicio se calcula con zoneinfo/tzdata para las 02:00 `America/Argentina/Cordoba` y se escribe UTC explícito: con las reglas actuales, 05:00Z. No cambia la zona del sistema. Repreparar/reinstalar al actualizar reglas horarias si cambian. `StartWhenAvailable` permite reintentar al volver a estar disponible; un equipo apagado no garantiza RPO diario.

`scheduled_backup.py` crea/verifica la copia y aplica retención local. Para purga local explícita:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.operate purge
Pop-Location
```

Se conservan las últimas copias de 7 días distintos y de 4 semanas ISO, admitiendo solapamientos, todas con antigüedad máxima de 30 días; no significa conservar siempre 11 archivos. Se separan orígenes para que una copia ficticia no sustituya una diaria de desarrollo. Sólo se purgan conjuntos propios autenticados en el destino configurado; archivos desconocidos y otros directorios se conservan. Parciales propios de más de 24 horas se retiran. Un manifiesto no verificable impide declarar una purga exitosa y requiere intervención. No se purgan marcas del diario hasta comprobar que expiraron **todas** las copias afectadas, incluidas externas; la operación `prune` existe, pero no se ejecutó sobre el diario activo porque B2 no fue verificado.

## B2 pendiente, sin contratación ni cargas realizadas

El adaptador optativo usa B2 Native API v4 mediante httpx ya existente. `B2_ENABLED=false` por defecto. No contacta B2 al iniciar la API ni al ejecutar pruebas; no se creó cuenta, bucket ni cargo. Para una futura habilitación autorizada, configurar localmente `B2_BUCKET`, `B2_BUCKET_ID`, `B2_KEY_ID`, `B2_APPLICATION_KEY`; clave limitada al bucket privado y prefijo `entrenador-prompts/`, con `listBuckets`, `listFiles`, `writeFiles`, `deleteFiles`. `B2_ENDPOINT_URL` anterior era reserva S3: este adaptador usa los endpoints HTTPS oficiales de Native v4 y no esa variable. No mezclar entornos en el mismo bucket/prefijo. Se cargan exclusivamente cifrado y manifiestos técnicos, nunca identidad privada ni diario obsoleto del respaldo.

Los comandos preparados `operate b2-upload --manifest ...` y `operate b2-purge` requieren esa habilitación externa explícita; no se ejecutaron aquí. El trabajo programado los incorpora sólo con `B2_ENABLED=true`. La purga enumera todas las versiones, también antiguas/ocultas, y cancela cargas inconclusas de más de 24 horas del prefijo propio; vuelve a enumerar para comprobar el resultado. Su lógica y el adaptador se probaron con transporte simulado, no en el proveedor. Antes de considerar operación real: verificar bucket privado, carga/descarga, restauración, versiones antiguas, multipart, política de 30 días y custodia redundante del diario/clave/ancla más recientes. Quedan pendientes acceso externo, programación real, alertas operativas y comprobación periódica.
