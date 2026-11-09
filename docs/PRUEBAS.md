# Pruebas

Se separan motor, API/PostgreSQL, operación y navegadores, con datos ficticios. Las condiciones están en [ACCEPTANCE_TESTS.md](tecnica/ACCEPTANCE_TESTS.md); los resultados históricos, en [evidencias](README.md#evidencias-y-diseño).

## Motor, sin base de datos

Después de instalar las dependencias, desde la raíz:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest tests/motor -q --tb=short
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
Pop-Location
```

Incluye el detector numérico y la preservación de las alertas anteriores. El corpus de 33 casos conserva la configuración inicial; su aprobación no sustituye las pruebas específicas de la ampliación.

## Tipos y build

```powershell
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run build
Pop-Location
```

El resultado se genera en `frontend/dist/`, excluido de Git. Usar `npm ci` para reproducir las dependencias del lock antes de comprobar.

## API, persistencia y operación

Completar la [instalación](INSTALACION_WINDOWS.md), incluyendo migración y permisos de `entrenador_prompts_test`. Iniciar Mailpit con el comando del README.

Las pruebas de respaldo/restauración requieren otras tres bases aisladas. Si todavía no existen, crearlas como administrador de PostgreSQL:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --password --set=ON_ERROR_STOP=on --file=scripts/crear_bases_operacion.sql
& .\.venv\Scripts\python.exe scripts\check_operation_databases.py
```

El SQL está limitado a `entrenador_prompts_ops_test`, `entrenador_prompts_restore_test` y `entrenador_prompts_contingencia_test`. No utilizarlas para trabajo real. Los ensayos reconstruyen datos en los destinos de pruebas; algunas comprobaciones exigen un destino vacío y sin otras conexiones.

Revisar primero [ETAPA05_OPERACION_WINDOWS.md](operacion/ETAPA05_OPERACION_WINDOWS.md). Deben estar disponibles `age`, `pg_dump` y `pg_restore`, claves y diario local. No cambiar los destinos permitidos para sortear una protección.

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\regresion.xml
Pop-Location
```

Revisar fallos y omisiones: un resultado parcial no acredita toda la suite. No agregar a Git credenciales, datos reales ni volcados.

## Navegadores y rendimiento

Los auxiliares usan Chrome y Edge instalados en Windows, perfiles de prueba y puertos temporales `18000/15173`. Ejecutarlos secuencialmente y comprobar que los puertos estén libres. No hace falta descargar navegadores adicionales mediante Playwright.

```powershell
& .\.venv\Scripts\python.exe scripts\verify_stage06_browsers.py
& .\.venv\Scripts\python.exe scripts\check_numeric_browser.py
& .\.venv\Scripts\python.exe scripts\verify_stage06_performance.py
```

El verificador de etapa 06 distingue resultado funcional de NF-02: una salida 2 no significa aprobación integral. No alterar el antivirus para ocultar solicitudes. Una muestra negativa no demuestra ausencia global de transmisión de datos. La automatización tampoco sustituye las revisiones humanas ni la validación educativa.

## Informes y secretos

`scripts/report_stage06.py` es un auxiliar histórico: reúne resultados locales y contiene hechos manuales del entorno original. Escribe en `docs/evidencias/INFORME_FINAL_ETAPA06.md`. No ejecutarlo para certificar automáticamente otro equipo ni interpretar sus hechos históricos como nuevas comprobaciones.

`scripts/check_secrets.py` compara archivos versionables con secretos locales disponibles y requiere Git. Es complementario: una copia sin `.env` no conoce los secretos de otro equipo. Revisar también los archivos que se van a publicar.
