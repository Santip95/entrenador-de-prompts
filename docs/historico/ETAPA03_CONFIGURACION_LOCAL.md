> Documento histórico. Conserva decisiones y comprobaciones de su etapa; para instalar esta versión, seguir [la guía vigente](../INSTALACION_WINDOWS.md). Los prompts y el manifiesto del paquete original no se incluyen en esta distribución. Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Preparación administrativa de etapa 03

Desde la raíz, con API y pruebas detenidas, ejecutar en PowerShell:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --set=ON_ERROR_STOP=on --file=scripts/separar_roles_locales.sql
```

Ingresar la clave administrativa y luego la nueva clave de `entrenador_migracion` cuando psql las solicite sin eco. No escribirlas como sentencias SQL ni enviarlas al chat. El script sólo transfiere propiedad y permisos de los objetos existentes en `entrenador_prompts` y `entrenador_prompts_test`; conserva tablas y datos. No usar `REASSIGN OWNED` global. Si se interrumpe, informar el error sin contraseñas antes de repetir: verifica que el nuevo rol no exista para evitar reutilizar un rol desconocido.

Conservar `POSTGRES_USER=entrenador_app` y su contraseña existente en `.env`. Añadir localmente:

```dotenv
MIGRATION_USER=entrenador_migracion
MIGRATION_PASSWORD=
```

Completar la nueva contraseña sólo en el editor. No cambiar `DATABASE_URL`/`TEST_DATABASE_URL` para dar privilegios de migración a la API. La herramienta de migraciones usa una conexión distinta; los tests que preparan fixtures usan esa conexión exclusivamente en la base de pruebas.

Avisar cuando esté aplicado para comprobar DDL denegado, migraciones y API con el rol mínimo. No se da por resuelto por ejecutar este procedimiento sin verificarlo.
