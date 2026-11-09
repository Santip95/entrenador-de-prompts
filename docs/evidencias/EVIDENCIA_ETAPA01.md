# Evidencia de la etapa 01

Estado: **comprobaciones técnicas locales de etapa 01 completadas**. Fecha de referencia del cliente: 6 de noviembre de 2026. Código conservado del intento inicial y corregido durante la reanudación. Identidad Git local configurada. El commit de cierre contiene este informe; identificarlo con `git log -1 --oneline` después de la entrega.

Referencia fija del cierre técnico: `2c2069e`. Confirmación manual posterior: Santiago comunicó en el pedido de etapa 02 que completó la revisión visual y comprobó el funcionamiento correcto del backend y del frontend. Es evidencia aportada por él; no se atribuye esta revisión manual a Codex ni se agregan capturas o resultados no comunicados. La planificación y el estado pendiente de separación de roles permanecen en `docs/historico/PROGRESS.md`.

## Entorno

Windows / PowerShell, Python 3.11.4, pip 26.3 en `.venv`, Node 26.13.0, npm 11.20.0. Se conserva la elección de PostgreSQL 18.6 en `127.0.0.1:5432`: en la reanudación el listener continuaba en PID 8132 y el servicio 18 en PID 5644, con ruta a `C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe`. La relación padre-hijo fue comprobada en el intento inicial. No se reconfiguró PostgreSQL 17.

## Ejecuciones de la reanudación

Todos los comandos parten de la raíz de este proyecto, salvo cuando se indica `backend` o `frontend`.

| Comando / carpeta | Resultado observado |
|---|---|
| `git status --short` con `-c safe.directory` limitado a esta carpeta | Archivos existentes sin commits; no había cambios versionados que sobrescribir. El ajuste sólo aplica a cada comando del sandbox. |
| `git config --get user.name` y `git config --get user.email` | En el primer intento faltaba identidad; el propietario la configuró y se comprobó su presencia al cerrar. |
| `python -m pip --use-feature=truststore install -r backend\requirements.txt` con el Python de `.venv` | Falló: el pip 23.1.2 no incluía truststore. |
| `.venv\Scripts\python.exe scripts\bootstrap_pip_windows.py` | pip 26.3 instalado con HTTPS verificado por Windows y hash cotejado con PyPI. |
| `.venv\Scripts\python.exe -m pip install -r backend\requirements.txt` | Instalación exitosa; posteriormente se redujeron los extras y se resolvió el lockfile definitivo. |
| `pip install --dry-run --ignore-installed --report local-data\python-resolution.json -r backend\requirements.txt` | Resolución completa usada para `backend/requirements.lock`. |
| `.venv\Scripts\python.exe -m pip install --no-index -r backend\requirements.lock` | Todas las versiones del lock presentes en el entorno. |
| `.venv\Scripts\python.exe -m pip check` | `No broken requirements found`. |
| `..\.venv\Scripts\python.exe -m pytest -q --junitxml=..\local-data\etapa01-pytest.xml` desde `backend` | Cierre: **20 passed in 1.00s**, sin fallos ni omisiones. El resultado anterior de 8/5 correspondía al bloqueo ya resuelto. |
| `..\.venv\Scripts\python.exe -m app.scripts.validate_config` desde `backend` | Configuración válida. Las pruebas de configuración también comprueban el error por variable faltante sin revelar valores. |
| `npm.cmd ci --offline --no-audit --no-fund` desde `frontend` | Instalación desde el lockfile: 24 paquetes. |
| `npm.cmd run build` desde `frontend` | TypeScript y Vite completaron el build; archivos generados excluidos de Git. |

La compilación offline de Alembic detectó un error de interpolación en el archivo INI; después de corregirlo a `%(here)s`, la prueba pasó. En el cierre se ejecutó la migración real sobre ambas bases del proyecto, comprobadas vacías antes de migrar. `app.scripts.prepare_test_db` selecciona explícitamente la base de pruebas sin cambiar la configuración de la sesión.

## Ejecución final con PostgreSQL real

Desde `backend`, en este orden:

```powershell
& ..\.venv\Scripts\python.exe -m app.scripts.check_database
& ..\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
& ..\.venv\Scripts\python.exe -m app.scripts.seed
& ..\.venv\Scripts\python.exe -m app.scripts.seed
& ..\.venv\Scripts\python.exe -m app.scripts.prepare_test_db
& ..\.venv\Scripts\python.exe -m pytest -q --junitxml=..\local-data\etapa01-pytest.xml
& ..\.venv\Scripts\python.exe -m alembic current
```

La consulta inicial devolvió PostgreSQL 18.6, `entrenador_app`, las dos bases previstas y ninguna tabla en ambas. `rolsuper`, `rolcreatedb` y `rolcreaterole` fueron `false`. Después de migrar quedaron 13 tablas de contrato y `alembic_version`; `alembic current` devolvió `20261106_0001 (head)`. Cada ejecución de seed devolvió 6 criterios, 6 reglas, 4 desafíos y 24 relaciones. No se cargaron cuentas de demostración ni ejemplos como prácticas reales.

Las 12 pruebas PostgreSQL comprueban repetición de seeds, conservación de nombres/títulos/mensajes modificados para la prueba, duplicado de criterio, FK inexistente, dos reglas activas para el mismo criterio, objetivo propio nulo, número de versión repetido, regla de otro criterio, `no_aplica` en C1, `advertencia` fuera de C6, regla nula en `cumple` y cascada práctica/versión/evaluación conservando al usuario. Se usan UUID y textos ficticios y se revierten los datos de cada caso con savepoints.

Desde la raíz, `.venv\Scripts\python.exe scripts\verify_startup.py` pasó dos ciclos de inicio/parada: API `/health` HTTP 200, Vite HTML y módulo React HTTP 200. Antes y después del reinicio se conservaron los conteos 6/6/4/24. Se cerraron ambos servidores; los puertos quedaron sin listeners. No se reinició PostgreSQL ni se afectaron bases ajenas. Las comprobaciones fueron por HTTP; no se realizó inspección visual en navegador.

`.venv\Scripts\python.exe scripts\check_secrets.py` confirmó que los valores secretos locales no aparecen en archivos versionables y que `.env` está excluido. `pip check` finalizó sin conflictos. El XML de pytest y los logs de arranque están en `local-data/`, ignorado por Git.

## Comprobaciones de la lista Windows

| ID | Estado actual | Evidencia o bloqueo |
|---|---|---|
| 01.1 | Aprobada técnicamente | Inicio desde procesos nuevos con directorios explícitos y `.env` del proyecto; dos ciclos completos. |
| 01.2 | Aprobada por HTTP | API y frontend HTTP 200; módulo React servido. Sin inspección visual en navegador. |
| 01.3 | Aprobada | Dos bases reales en PostgreSQL 18.6, rol propio sin superusuario, 13 tablas más control Alembic. |
| 01.4 | Aprobada | Migración real desde bases vacías sin restauración ni correcciones manuales. |
| 01.5 | Aprobada para etapa 01 | Doce pruebas PostgreSQL; integridad, FK, unicidad, estados y cascada. |
| 01.6 | Aprobada | Conteos 6/6/4/24 repetidos y prueba de no sobrescritura. |
| 01.7 | Aprobada | Conteos conservados entre dos reinicios de aplicación. |
| 01.8 | Aprobada para entorno local | Configuración y conexión válidas, errores sin valores secretos y exclusión de `.env` comprobada. |

## Límites y pendientes fuera del cierre técnico

El propietario ya completó la preparación local y la identidad Git. No repetir el script de creación sobre estas bases. Tener esquema y servicios no completa historias funcionales: todavía faltan el motor, acceso, permisos de negocio, flujos e interfaz de las etapas siguientes.

Limitación pendiente de privilegios: la preparación local original usa el rol del proyecto como propietario para ejecutar Alembic. Antes de un uso funcional debe separarse la credencial de migración de la credencial de ejecución sin DDL conforme a docs/tecnica/DATABASE.md. No se presenta esta configuración inicial como configuración de producción.

Mailpit queda para etapa 03. No se ejecutó la etapa 02, pruebas educativas ni validación externa.
