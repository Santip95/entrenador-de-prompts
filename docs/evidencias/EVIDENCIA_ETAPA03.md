# Evidencia de etapa 03 — acceso y revocación

Fecha del cliente: **7/11/2026**, America/Buenos_Aires. Referencia inicial: `6b4dc38`. El commit que incorpora este informe identifica el incremento (`git log -1 --oneline`). **Alcance técnico de etapa 03 completado; recorridos manuales y dependencias de etapas posteriores identificados, sin darlos por aprobados.** No se implementó etapa 04.

## Implementado y entorno conservado

Windows/PowerShell, Python 3.11.4 en `.venv`, React/Vite/TypeScript y PostgreSQL 18.6 en `127.0.0.1:5432`. Sin WSL/Docker. Se conservan las dependencias previas fijadas; se añade argon2-cffi 25.1.0 y sus transitivas fijadas: argon2-cffi-bindings 26.1.0, cffi 2.1.1 y pycparser 3.12. `pip check`: sin incompatibilidades.

- Acceso por `/api/v1`: registro genérico, login, logout, me, csrf, recuperación, restablecimiento y cambio de clave. Roles públicos sólo usuario/administrador; registro no acepta elegir rol. No hay cuentas ni contraseñas seed.
- Sesiones opacas aleatorias de 32 bytes, SHA-256 en PostgreSQL, cookie HttpOnly/SameSite=Lax/Path=/, Secure obligatorio en producción. Consulta de usuario/estado/epoch/sesión en cada operación protegida. Inactividad 30 min y absoluto 8 h según reloj del servidor. Rotación al autenticar; logout sólo revoca la sesión actual.
- Bloqueo/desactivación y cambios de clave incrementan epoch y revocan sesiones en transacción. Guard de escritura con bloqueo de usuario mantenido hasta commit, común al cambio de estado. Los desbloqueos no reviven tokens.
- Argon2id 65536 KiB/3/1, sal individual; hash anterior se actualiza al ingresar correctamente. Claves de 15–128 caracteres sin recorte/composición arbitraria, espacios y Unicode admitidos; lista local inicial versión 1, 12 entradas, cobertura limitada explícita.
- CSRF HMAC ligado a la sesión y Origin exacto; POST públicos validan origen/JSON. Sin CORS permisivo. Máximo de cuerpo 64 KiB; validaciones y errores uniformes sin reproducir valores. Arranque local sin logs de acceso ni confianza en cabeceras proxy del cliente.
- Contadores atómicos compartidos PostgreSQL, con HMAC de ámbito+IP/correo; límites en docs/tecnica/SECURITY.md. Cinco fallos de cuenta en 15 min bloquean 15 min y revocan sesiones. No se guardan IP/correo en claro en el contador.
- Recuperación SMTP real a Mailpit; token aleatorio guardado como hash, 15 min, uso único, consumo transaccional y concurrente. Invalida otros enlaces y sesiones; no inicia sesión ni reactiva bloqueados/desactivados. Origin del enlace viene de configuración, no de Host; fragmento URL para evitar token en solicitudes/logs HTTP. Fallo SMTP conserva respuesta genérica y registra sólo un evento codificado, sin activar token.
- Listado mínimo de cuentas/estado sólo para administración activa y comprobación de revocación. No hay panel, cambio de rol público ni lectura administrativa de prompts ajenos. Sin vía de recuperación comprobada, se rechaza restringir administradores con 409. Promoción privilegiada local con revocación mediante `manage_access`.
- Política común de propiedad para práctica/versión; se comprueba con fixtures y adaptador HTTP exclusivo de tests. No se incorporan los endpoints funcionales de etapa 04.

El motor sigue **1.0.0**, sin cambios en dominio, fixtures, resultados ni límites. Santiago completó manualmente 02.9; evidencia literal de CP-25/27/28 conservada en docs/evidencias/EVIDENCIA_ETAPA02.md. La interfaz **todavía no muestra** los dos avisos junto a resultados: requisito obligatorio pendiente de etapa 04.

## PostgreSQL: preparación y comprobación real

Se verificó la instancia 18.6 con listener PID 8044 en 5432; servicios `postgresql-x64-18` PID 5652 y `postgresql-x64-17` PID 5680, rutas de instalación 18 y 17 respectivamente. Estos PID son de esta ejecución y pueden cambiar. La consulta de versión de la conexión confirmó 18.6. No se alteraron PostgreSQL 17, otras bases o usuarios ajenos.

Santiago ejecutó localmente, ingresando claves de manera interactiva, el procedimiento preparado:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' --host=127.0.0.1 --port=5432 --username=postgres --dbname=postgres --set=ON_ERROR_STOP=on --file=scripts/separar_roles_locales.sql
```

Esta ejecución administrativa es **comunicada por Santiago**, no atribuida a Codex. Al primer intento posterior la clave de migración aún no estaba guardada en disco; las migraciones se detuvieron antes de ejecutarse. Tras su confirmación de guardado se verificaron ambas conexiones sin mostrar valores.

| Base | Ejecución | Migración | Obtenido |
|---|---|---|---|
| entrenador_prompts | entrenador_app: DDL=false, 0 tablas propias | entrenador_migracion: DDL=true, 15 tablas propias | correcto=true en ambos |
| entrenador_prompts_test | entrenador_app: DDL=false, 0 tablas propias | entrenador_migracion: DDL=true, 15 tablas propias | correcto=true en ambos |

Se comprueba además ausencia de TEMP, membresías y permisos elevados de ejecución. Seis intentos reales de CREATE TABLE, ALTER TABLE, DROP TABLE, CREATE TEMP, CREATE SCHEMA y SET ROLE se rechazan con SQLSTATE 42501 en la base de pruebas, siempre dentro de transacciones revertidas. La API verifica el reparto al arrancar. El rol de ejecución tiene sólo lectura y DML de acceso; no se habilitan aún escrituras de prácticas/catálogos ni TRUNCATE.

`20261107_0002` se aplicó sobre `20261106_0001` en ambas bases con la credencial de migración; añade `limite_solicitud` y sus permisos, sin regenerar el esquema inicial ni borrar datos. Seeds mantienen **6 criterios, 6 reglas, 4 desafíos y 24 relaciones**. La regresión de integridad sigue ejecutando FK/restricciones/idempotencia/no sobrescritura con fixtures ficticias revertidas. La evidencia de migración desde cero de etapa 01 se conserva; esta etapa probó el upgrade incremental, no una reconstrucción desde cero.

## Mailpit oficial y costo de contraseña

Mailpit **1.33.0**, distribución oficial Windows amd64:

- Fuente: [instalación oficial](https://mailpit.axllent.org/docs/install/) y [release fijada](https://github.com/axllent/mailpit/releases/tag/v1.33.0).
- ZIP: `mailpit-windows-amd64.zip`; SHA-256 publicado/verificado: `47122dd828ff80dcaef62b2952c478b178afadadf066c990489608e537121bfd`.
- Ejecutable en `local-data/mailpit/mailpit.exe`, ignorado por Git. Descarga HTTPS validada, extracción sólo del ejecutable previsto. SMTP loopback 1025, web/API loopback 8025. Sin relay ni chequeo automático de versiones/DNS inverso en los comandos del proyecto.
- Prueba SMTP real envía un mensaje ficticio, lo encuentra y lee por API de Mailpit; borra sólo ese mensaje. Las pruebas de recuperación también reciben y consumen enlaces reales por SMTP, sin imprimir tokens. Si el fixture inició Mailpit lo detiene al terminar; si ya estaba iniciado lo conserva y no vacía correos ajenos.

Medición local con `time.perf_counter`, 10 hashes por configuración, claves aleatorias no mostradas:

| Configuración Argon2id | Mediana | Máximo | Decisión |
|---|---:|---:|---|
| 19456 KiB, tiempo 2, paralelo 1 | 25,2 ms | 26,4 ms | mínimo del contrato |
| 65536 KiB, tiempo 3, paralelo 1 | 116,9 ms | 118,1 ms | elegido y configurado localmente |

Se elevaron sólo los valores iniciales Argon2 y se conservó/generó la clave CSRF en `.env`, sin mostrar secretos. No es una medición NF-03 de evaluación ni una certificación de seguridad. [Documentación de argon2-cffi](https://argon2-cffi.readthedocs.io/en/stable/howto.html).

## Comandos ejecutados y resultados

Desde raíz, Windows/PowerShell; las consultas de red/servicios y las pruebas con sockets requirieron ejecución fuera del sandbox. No se modificó la política de PowerShell. Comandos de instalación efectivamente ejecutados:

```powershell
& .\.venv\Scripts\python.exe scripts\install_mailpit.py
& .\.venv\Scripts\python.exe -m pip install argon2-cffi==25.1.0
& .\.venv\Scripts\python.exe scripts\prepare_access_secret.py
& .\.venv\Scripts\python.exe -m pip check
```

Resultado: distribución y hash correctos; cuatro paquetes nuevos instalados y fijados en lock; clave existente conservada o completada sin eco; sin requisitos incompatibles. Se consultaron metadatos oficiales GitHub/PyPI para fijar versiones, sin utilizar `latest` en configuración reproducible.

Comandos de migración/precarga ejecutados desde raíz, dentro de backend:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
& ..\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
& ..\.venv\Scripts\python.exe -m app.scripts.seed
& ..\.venv\Scripts\python.exe -m app.scripts.prepare_test_db
Pop-Location
```

Resultado: reparto verificado en las dos bases; upgrade a `20261107_0002`; semillas 6/6/4/24 sin duplicar ni sobrescribir. La conexión de ejecución se mantuvo separada durante todos los tests HTTP.

Comandos finales ejecutados:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\etapa03-regresion.xml
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
Pop-Location
& .\.venv\Scripts\python.exe scripts\verify_startup.py
& .\.venv\Scripts\python.exe -m compileall -q backend/app scripts
& .\.venv\Scripts\python.exe scripts\check_secrets.py
```

**Obtenido: 223 aprobadas, 0 fallidas, 0 omitidas, 35,08 s** (JUnit: 35,083 s). **140 anteriores + 83 nuevas**: 60 de integración de acceso/PostgreSQL, 22 de política/configuración/OpenAPI y 1 de entrega real SMTP. XML local ignorado por Git, sin cuerpos, contraseñas, cookies ni tokens.

Corpus del motor: **33/33**, versión 1.0.0. Arranque: dos ciclos API HTTP 200 y Vite HTML/módulo HTTP 200, conteos conservados, procesos detenidos al terminar. Compilación correcta; secretos locales ausentes de archivos versionables. El escáner incluye ahora MIGRATION_PASSWORD.

Advertencia conservada: Starlette avisa que su adaptador de TestClient basado en httpx está deprecado y sugiere httpx2. La combinación fijada sigue funcionando y no se cambió para ocultar la advertencia; revisar migración de dependencia en mantenimiento. No hubo omisiones por credenciales o Mailpit en el resultado final.

Correcciones comprobadas durante el trabajo: Alembic cargaba Settings cacheados durante compilación offline (ahora carga configuración propia); la limpieza SMTP usaba un argumento no admitido por `httpx.delete` (ahora request DELETE); el cursor SQL nulo del listado de cuentas necesitaba CAST explícito. La primera integración de acceso tuvo 68 aprobadas/2 fallidas por ese cursor; se corrigió y ambas pasaron. La regresión pasó luego 210, 214 y 218 al añadir controles y elevar Argon2id. La revisión final añadió una prueba concurrente de purga de contadores, corregida con `SKIP LOCKED`, y ajustó JSON malformado/UTF-8 inválido a HTTP 400 conforme a docs/tecnica/API_CONTRACT.md (esquema inválido continúa 422). La expectativa inicial propia de JSON malformado era 422 y se corrigió contra el contrato, no para ocultar una implementación incorrecta; no se alteraron fixtures esperadas del motor. También se añadió validación de una única dirección de correo mediante el parser estándar de Python, rechazando listas/separadores/locales inválidos antes de registrar o enviar recuperación y conservando strip/lower para login. Ninguno de esos fallos iniciales se presenta como aprobado sin su repetición. Resultado final: 223 aprobadas.

## Cobertura real por escenario de seguridad

| ID | Esperado | Obtenido y alcance |
|---|---|---|
| SEC-01 | Bloquear revoca ambas sesiones; desbloquear no revive | Aprobado técnico: cookies independientes y dos clientes HTTP, bloqueo administrativo real por API, rechazo siguiente y posterior desbloqueo. **Dos navegadores visuales: pendiente manual.** |
| SEC-02 | Ninguna escritura con autorización vieja confirma después de restringir | Aprobado técnico: dos conexiones/hilos, guard mantiene lock; bloqueo/desactivación esperan a la escritura de auditoría; en el orden inverso, 401 antes de escribir. Es el guard común; repetir al integrar guardado de versiones en etapa 04. |
| SEC-03 | 14/129 rechazadas; 15/128 admitidas; espacios/Unicode sin truncar | Aprobado: política y endpoints de registro/login, lista común, espacios exteriores; misma política en restablecimiento, rechazo sin consumir token. Hash Argon2id/sales/actualización de parámetros comprobados. |
| SEC-04 | Cinco fallos bloquean 15 min, revocan; límite IP compartido | Aprobado: ventana y bloqueo reales PostgreSQL, liberación temporal sin revivir sesión, contador entre dos instancias de servicio y HTTP 429 al agotar IP. Dos conexiones sincronizadas refrescan contadores vencidos y purgan sin interbloqueo. No es una prueba de carga de un despliegue multiworker. |
| SEC-05 | Inactividad/absoluto/logout invalidan y borran cookie | Aprobado: timestamps de fixtures desplazados a 30 min/8 h, epoch/revocación y logout; Date del cliente no altera servidor. Una sesión independiente permanece tras logout de la otra. |
| SEC-06 | Token válido/vencido/repetido/concurrente; revocación global | Aprobado: SMTP real a Mailpit, nueva clave funciona/anterior falla, vencimiento, bloqueado/desactivado/inexistente, otros tokens invalidados. Dos consumos concurrentes: **uno 204 y otro 400**; sin inicio automático ni token en API/logs. |
| SEC-07 | Propiedad en versión/comparación/borrado; común no administra | **Parcial:** común en admin 403; A/admin ante versión de B 404 con política de propiedad y adaptador sólo de test; sin filtración. Endpoints reales de versiones/comparación/borrado todavía no existen: completar en etapas 04/05. No se da SEC-07 completo por esos tests. |
| SEC-08 | CSRF/origen; HTML/SQL como datos, sin ejecución | **Parcial:** CSRF ligado a sesión, falta/valor errado/origen/tipo rechazados; texto ficticio con HTML/SQL persiste y retorna como dato por consultas parametrizadas en test. Renderizado React y flujos de prompt pendientes de etapa 04; no se aprueba XSS visual de pantalla inexistente. |
| SEC-09 | Cambio de contraseña/rol/restauración invalida | **Parcial:** cambio de clave y promoción local revocan; rol se consulta otra vez; hook de invalidación de restauración comprobado en transacción revertida. Restauración completa de una copia/diario es etapa 05: **no ejecutada**. |
| SEC-17 | Error de revisión/registro sin reflejar datos sensibles | **Parcial:** registro/login/recuperación/restablecer inválidos, JSON malformado y tamaño; errores/logs sin valor/cuerpo. Endpoint de revisión pendiente de etapa 04; no se da ese tramo por probado. |

## Verificación manual realizada y pendientes de etapas posteriores

**Confirmación manual de Santiago — 7/11/2026, sobre el cierre técnico `6910957`:** comunicó que completó correctamente `scripts/check_access_manual.py` y comprobó la recepción del correo de recuperación en Mailpit. Es evidencia aportada por el usuario, no una nueva ejecución de Codex ni una prueba con dos navegadores. Comandos reproducibles en README, sección «Acceso y correo local — etapa 03».

| Comprobación manual | Esperado | Obtenido comunicado | Resultado |
|---|---:|---:|---|
| Restablecimiento con contraseña admitida | 204 | 204 | Aprobado |
| Reutilización del token consumido | 400 | 400 | Aprobado |
| Consulta con sesión B revocada | 401 | 401 | Aprobado |
| Ingreso con contraseña anterior | 401 | 401 | Aprobado |
| Ingreso con contraseña nueva | 200 | 200 | Aprobado |
| Cierre final | 204 | 204 | Aprobado |

Santiago indicó que en el primer intento ingresó una nueva contraseña demasiado corta. Repitió el recorrido respetando el mínimo de 15 caracteres y todas las comprobaciones del auxiliar finalizaron correctamente. Se conserva ese antecedente sin atribuirle un código HTTP que no comunicó. No se registran contraseñas, tokens, cookies ni datos de la cuenta. **03.M1 completada manualmente por Santiago.** La regresión automática previa sigue siendo 223 aprobadas; esta confirmación no añade pruebas automáticas ni implica haberlas repetido.

En navegador: health muestra JSON; frontend conserva el esqueleto; me sin cookie propia devuelve 401. Abrir el enlace de recuperación aún no cambia contraseña por pantalla. La recepción del correo en Mailpit ya está confirmada por Santiago; los dos navegadores reales y las pantallas funcionales permanecen pendientes de etapa 04. No se atribuyen otras verificaciones visuales a esta confirmación.

Etapa 04 pendiente: formularios de acceso/restablecimiento y pantallas funcionales; resultados con ambos avisos junto a ellos: **«El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad»** y **«Estos patrones no detectan toda la información sensible»**; tokens de revisión, motor integrado, CP-12 y permisos sobre operaciones reales de prácticas/versiones/comparación. No implementado ni marcado como presentado.

Etapa 05 pendiente: panel, vía de recuperación del último administrador, borrado durable/diario y ensayo real de backup/restauración. Preparación de producción: proveedor SMTP/TLS, proxy confiable, revisión de lista común y carga; no desplegados ni certificados. No hay validación externa, personas ni resultados educativos inventados. Credenciales, ejecutables, respaldos y reportes locales permanecen fuera de Git.
