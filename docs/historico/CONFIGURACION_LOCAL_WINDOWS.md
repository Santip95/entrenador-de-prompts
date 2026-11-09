> Documento histórico. Conserva decisiones y comprobaciones de su etapa; para instalar esta versión, seguir [la guía vigente](../INSTALACION_WINDOWS.md). Los prompts y el manifiesto del paquete original no se incluyen en esta distribución. Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Preparación de PostgreSQL y Git para la etapa 01

Ejecutar desde la raíz de esta carpeta, en una terminal PowerShell propia. La instancia elegida es `postgresql-x64-18`, en `127.0.0.1:5432`. No se toca la instalación 17.

Estado actual: los recursos ya fueron creados y su conexión quedó comprobada durante el cierre de la etapa 01. No volver a ejecutar su creación en este equipo. Las instrucciones siguientes sirven para preparar otra instalación vacía.

## 1. Crear los recursos exclusivos del proyecto

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --password --set=ON_ERROR_STOP=on --file '.\scripts\crear_bases_locales.sql'
```

Ingresar primero la contraseña del administrador local `postgres`. Después, `\password` solicita dos veces una contraseña nueva para `entrenador_app`. Se ingresan sin mostrarse; no se incluyen en comandos, chat ni archivos SQL. Si el administrador tiene otro nombre, cambiar sólo `--username`. Si no conocés su contraseña, se requiere recuperarla con el administrador del equipo; no cambiar la configuración de autenticación de PostgreSQL.

El script verifica el mayor 18 y comprueba que no existan recursos con los nombres del proyecto. Si encuentra alguno, se detiene sin modificarlo: guardar únicamente el mensaje de error sin contraseñas para revisar el estado. No repetir sentencias de creación manualmente después de un fallo. Los recursos previstos son:

| Recurso | Nombre |
|---|---|
| Rol local de aplicación sin superusuario | `entrenador_app` |
| Base de desarrollo | `entrenador_prompts` |
| Base aislada de pruebas | `entrenador_prompts_test` |

## 2. Completar `.env`

Ya está preparado en la raíz y excluido de Git. Abrirlo en el editor y completar sólo `POSTGRES_PASSWORD=` con la contraseña elegida para `entrenador_app`. Si contiene espacios o caracteres especiales, usar comillas simples alrededor del valor según la sintaxis de python-dotenv. Conservar `POSTGRES_HOST=127.0.0.1`, `POSTGRES_PORT=5432`, `POSTGRES_USER=entrenador_app` y los nombres de las dos bases. Dejar vacíos `DATABASE_URL` y `TEST_DATABASE_URL` para construir las conexiones desde esas variables. No ejecutar comandos que impriman el contenido de `.env`.

## 3. Comprobar la conexión

Este comando solicita la contraseña del rol del proyecto y ejecuta consultas de lectura:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=entrenador_app --dbname=entrenador_prompts --password --set=ON_ERROR_STOP=on --command "SELECT current_database(), current_user, current_setting('server_version'); SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user;"
```

Esperado: `entrenador_prompts`, `entrenador_app`, versión 18 y los tres privilegios en `f`. Después validar la lectura de `.env`:

```powershell
Push-Location backend
try { & ..\.venv\Scripts\python.exe -m app.scripts.validate_config } finally { Pop-Location }
```

La validación de configuración confirma el formato, pero no abre una conexión. Las migraciones y pruebas posteriores deben ejecutarse sólo después de comprobar la conexión anterior. Avisar cuando esté listo sin compartir contraseñas.

## 4. Identidad Git sólo para este repositorio

La identidad local ya quedó configurada y fue comprobada al cerrar la etapa 01. Para configurar otra copia del repositorio sin enviar nombre/correo al chat:

```powershell
$nombreGitTFG = Read-Host 'Nombre que aparecerá como autor'
$correoGitTFG = Read-Host 'Correo que aparecerá como autor'
git config --local user.name $nombreGitTFG
git config --local user.email $correoGitTFG
git config --local --get user.name
git config --local --get user.email
```

No se usa `--global`. Los commits conservarán esa identidad como metadatos locales. Si tu terminal ya tiene una identidad que querés usar, no hace falta cambiarla.
