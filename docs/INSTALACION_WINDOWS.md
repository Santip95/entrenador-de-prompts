# Instalación nueva en Windows

Esta guía prepara una instalación local desde el código de `entrenador-de-prompts`. No usar el aprovisionamiento de bases para reemplazar una instalación existente. Una copia nueva de la carpeta no crea por sí sola un entorno independiente: los nombres de bases y los directorios privados son los mismos salvo configuración explícita.

El procedimiento proviene de los auxiliares e instrucciones del proyecto. El esquema vacío y sus permisos se ensayaron en una base aislada del equipo original; no se acredita con ello una instalación completa en otro Windows.

## 1. Herramientas y dependencias

La combinación registrada fue Windows x64, PowerShell 5.1/7, Python 3.11.4, Node.js 26.13.0 con npm 11.20.0 y PostgreSQL 18.6. Mailpit 1.33.0 y age 1.3.2 se descargan con los auxiliares incluidos. Se conservan las versiones originales de `backend/requirements.lock` y `frontend/package-lock.json`.

Instalar Python, Node.js/npm y PostgreSQL antes de continuar. El servicio PostgreSQL debe escuchar en `127.0.0.1:5432`. Si hay otras instalaciones, identificar la instancia del proyecto; no cambiar ni borrar bases ajenas.

Extraer o clonar el repositorio en su ubicación definitiva. Abrir PowerShell **desde `entrenador-de-prompts`**. Los comandos asumen las ubicaciones estándar de Node.js y PostgreSQL; ajustar la ruta del ejecutable si se instalaron en otra ubicación.

Ejecutar cada comando y continuar sólo si termina correctamente. No hace falta activar `.venv` ni modificar la política de ejecución de PowerShell.

```powershell
python --version
python -m venv .venv
& .\.venv\Scripts\python.exe scripts\bootstrap_pip_windows.py
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" ci
Pop-Location
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
```

El auxiliar de pip descarga la versión fijada, comprueba su SHA-256 y mantiene la validación HTTPS. Si una descarga falla, resolver el error; no desactivar la validación de certificados.

## 2. Bases y roles

**Sólo para un entorno sin los recursos del proyecto.** El SQL se detiene si ya existen los roles o las bases; no quitar esa protección.

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --password --set=ON_ERROR_STOP=on --file=scripts/crear_entorno_nuevo.sql
```

Ingresar la contraseña de PostgreSQL únicamente cuando la solicite la terminal. El script pide además, sin eco, contraseñas nuevas para `entrenador_app` y `entrenador_migracion`; utilizar valores diferentes. Crea `entrenador_prompts` y `entrenador_prompts_test` y separa los permisos de ejecución y migración.

Editar `.env` localmente: `POSTGRES_PASSWORD` corresponde a `entrenador_app`; `MIGRATION_PASSWORD`, a `entrenador_migracion`. Mantener el host/puerto de esa instancia. Dejar `DATABASE_URL` y `TEST_DATABASE_URL` vacíos si se usan las variables anteriores, y `B2_ENABLED=false` para operación local.

No copiar contraseñas a comandos, capturas, documentos, incidencias ni archivos versionados. `.env.example` debe seguir sin secretos.

## 3. Correo, claves y diario

Desde la raíz, ejecutar secuencialmente:

```powershell
& .\.venv\Scripts\python.exe scripts\prepare_access_secret.py
& .\.venv\Scripts\python.exe scripts\prepare_review_secrets.py
& .\.venv\Scripts\python.exe scripts\install_mailpit.py
& .\.venv\Scripts\python.exe scripts\install_age.py
& .\.venv\Scripts\python.exe scripts\prepare_operation_local.py
```

Los preparadores completan claves ausentes y conservan las existentes. Las herramientas se descargan a `local-data/`; las claves y el diario se preparan fuera del repositorio, en directorios de la cuenta de Windows con permisos privados. El diario es necesario para borrar prácticas y cuentas. Si falta la clave de un diario existente, recuperar la original; no inicializar otro para eludir el error.

## 4. Migraciones, catálogo y permisos

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m alembic upgrade head
& ..\.venv\Scripts\python.exe -m app.scripts.seed
& ..\.venv\Scripts\python.exe -m app.scripts.prepare_test_db
Pop-Location
```

Completar los permisos iniciales de acceso **después de las migraciones**, con el propietario de los objetos:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=entrenador_migracion --dbname=entrenador_prompts --password --set=ON_ERROR_STOP=on --file=scripts/permisos_ejecucion_acceso.sql
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=entrenador_migracion --dbname=entrenador_prompts_test --password --set=ON_ERROR_STOP=on --file=scripts/permisos_ejecucion_acceso.sql
```

Los seeds conservan las reglas iniciales v1 para reproducir los casos históricos. Activar la ampliación de números de 7, 8 y 10 dígitos mediante su publicación versionada:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
& ..\.venv\Scripts\python.exe -m app.scripts.enable_numeric_detector --entorno desarrollo
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
Pop-Location
```

El comando del detector es idempotente; no recalcula el historial. El corpus usa su configuración histórica. Si un catálogo modificado impide la publicación, revisar el motivo antes de cambiar reglas.

## 5. Cuenta administradora

Si se necesita usar el panel, crear una cuenta nueva con el comando local:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.manage_access crear-admin
Pop-Location
```

Solicita los datos y la contraseña en la terminal, sin mostrar la contraseña. No hay una cuenta administradora ni una clave pública precargadas. Las cuentas de usuario se registran desde la aplicación.

## 6. Inicio y comprobación

Usar las tres terminales del [README](../README.md#instalación-y-ejecución). Comprobar registro, ingreso, una práctica nueva, revisión y guardado, historial y recuperación mediante Mailpit, con datos ficticios.

La [guía de etapa 06](operacion/ETAPA06_WINDOWS.md) describe una demostración separada. Requiere la base adicional `entrenador_prompts_demo` y genera credenciales privadas; no se publica ninguna contraseña de demostración.

## 7. Respaldos programados

La API y la interfaz no necesitan una tarea programada para iniciar. El respaldo necesita PostgreSQL disponible, herramientas instaladas, claves y rutas privadas correctas.

La distribución no registra tareas automáticamente. Antes de instalar una, comprobar que no haya otra instalación usando `EntrenadorPrompts-Respaldo`. No registrar dos instalaciones sobre la misma tarea ni eliminar la de la instalación habitual. El procedimiento está en [la guía de operación](operacion/ETAPA05_OPERACION_WINDOWS.md).

Si se traslada una instalación existente, conservar datos y claves, recrear `.venv` y revisar `.env`, rutas de herramientas y acciones de la tarea. La tarea contiene rutas absolutas. Su reinstalación debe coordinarse desde la nueva ubicación y verificarse con una copia nueva; el comando `instalar` no se presenta como reemplazo automático de una tarea existente.

La custodia externa de claves y la operación real en B2 siguen pendientes. Publicar el código no completa esos controles.
