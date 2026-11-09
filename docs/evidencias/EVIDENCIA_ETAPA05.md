# Evidencia de etapa 05 — administración, borrado y operación local

**Confirmación posterior de Santiago, etapa 06 (7/11/2026):** los recorridos manuales que probó funcionan correctamente; se registra como revisión general del incremento, sin inventar entradas, capturas, tiempos ni detalle por caso. No equivale a revisión completa de accesibilidad ni resuelve NF-02. Los pendientes de abajo corresponden al cierre histórico; tarea instalada y comprobaciones nuevas se registran en docs/evidencias/EVIDENCIA_ETAPA06.md.

Fecha: **7/11/2026**. Base efectiva: **6a66e5b**, repositorio limpio al comenzar; se conservó el cierre de etapa 04 y no se hizo reset. El commit que incorpora este informe identifica el incremento. No se publica/despliega ni se inicia etapa 06.

## Confirmación manual recibida y límites conservados

Santiago confirmó únicamente pantallas generales, recuperación y consulta del historial después de salir/volver a ingresar. Registrado en docs/evidencias/EVIDENCIA_ETAPA04.md, docs/historico/PROGRESS.md y comprobaciones. No se transforma en aprobación de todas las casillas, CP-12 exacto, reinicio de servicios o accesibilidad humana completa. **NF-02 sigue pendiente:** en los navegadores se observaron nuevamente los orígenes `http://gc.kis.v2.scr.kaspersky-labs.com` y `http://me.kis.v2.scr.kaspersky-labs.com`; no se determinó procedencia, payload ni salida física. No se desactivó/reconfiguró el antivirus ni se excluyeron esas solicitudes para aprobar.

## Implementado

- HU-09 desde React/TypeScript, API y PostgreSQL: desafío borrador/edición/publicación/desactivación, seis configuraciones, presentación de criterios sin cambiar códigos/semántica, nuevas reglas inactivas y publicación/desactivación atómicas, cuentas mínimas y bloqueo/desbloqueo/desactivación. Listados paginados; no lectura de prompts ajenos, cambio público de rol ni DELETE de catálogo/versiones.
- Reutilización del motor **1.0.0**, C1–C6, corpus/fixtures y límites de libre/detectores. Sin IA, inferencia semántica ni ampliación indiscriminada del detector numérico. Comparación no equivalente al publicar reglas; snapshots anteriores intactos.
- Control de revisión de desafío, presentación y regla activa esperada bajo lock exclusivo 90404, compartido con el protocolo previo del guardado. Error de configuración si falta una regla; no se elimina el criterio ni se guarda parcialmente.
- Primer administrador mediante `app.scripts.manage_access crear-admin`: correo interactivo, contraseña con getpass dos veces, misma política 15–128/Argon2id, sin reemplazar cuentas existentes. Recuperación técnica creando otra cuenta local probada en la base de pruebas. D22 deja de restringir a todos los administradores: lock 90505 serializa cambios de estado/borrado/comandos locales y protege al último habilitado. No hay credenciales públicas ni panel técnico de claves/copias.
- Borrado propio desde historial/resultados y perfil, con consecuencia/casilla explícita y clave actual para cuenta. Cascadas existentes, CSRF y autorización hasta commit. Diario Fernet independiente, primero durable y luego DELETE transaccional; se completa después del commit. UUID técnicos/tipo/fechas, sin correo/texto. Reintento de práctica registrado 204; sesión de cuenta ya borrada 401. Pendientes se conservan y reaplican.
- Clave y ancla de diario e identidad privada age separadas del repositorio y del destino de copias, ACL privadas. Generadas únicamente cuando faltaban, valores existentes conservados. Diario perdido/corrupto o ancla incoherente no se recrea silenciosamente y no permite declarar borrado/restore exitoso.
- pg_dump personalizado mediante cliente PostgreSQL 18, cifrado age 1.3.2 y comprobación de **todo** el archivo antes de admitir la copia; nunca dump en claro. Manifiesto técnico autenticado (fecha UTC, app operativa 0.5.0, esquema, origen, bytes, SHA-256), sin datos personales. Retención local por origen: 7 días/4 semanas ISO, con solapamientos, máximo 30 días; sólo conjuntos propios autenticados y parciales propios antiguos del destino configurado.
- Restore destructivo limitado a dos bases ficticias explícitas, CONNECT cerrado en commit independiente antes de actuar; rechaza conexiones existentes, diario/copia no verificables. Reaplica pendientes/completados e invalida todas las sesiones/recuperaciones antes de comprobar integridad y conceder acceso.
- Trabajo y XML para Task Scheduler Windows, ejecutable Python explícito, S4U, sin terminal ni cambio de política/zona global. Inicio UTC calculado desde 02:00 Cordoba. Preparar/validar/instalar/consultar/eliminar documentados. Adaptador B2 Native v4 optativo, desactivado por defecto; contempla versiones antiguas/ocultas y multipart, sólo prefijo propio. No se contactó/contrató B2.

## Entorno y preparación realmente ejecutados

Windows nativo/PowerShell, Python **3.11.4** en `.venv`, Node **26.13.0**, npm **11.20.0** con `npm.cmd`, PostgreSQL **18.6**, Mailpit **1.33.0**, React/Vite y dependencias anteriores conservados. Nueva biblioteca **cryptography 50.0.2**, compatible con CPython 3.11/Windows x64; reutiliza cffi 2.1.1/pycparser 3.12 existentes. Pinned en requirements.txt/lock; `pip check` aprobado. Frontend sin nuevas dependencias ni cambios del lock. Playwright 1.64.1 usa Chrome **156.0.8078.80** y Edge **157.0.4341.42** instalados, perfiles/procesos temporales independientes.

age Windows amd64 **1.3.2**, ZIP oficial con SHA-256 **f48d8f8f9ebe903ab5027ed067652f2cc1db94bc206976430133b905dcd8e8c7**, consultado en metadatos oficiales y verificado al instalar. Biblioteca/formatos mantenidos, no primitivas de cifrado propias. Fuentes: [age oficial](https://github.com/FiloSottile/age/releases/tag/v1.3.2), [PyCA/PyPI](https://pypi.org/project/cryptography/50.0.2/), [Fernet](https://cryptography.io/en/latest/fernet/), [Task Scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/trigger-startboundary), [B2 versiones](https://www.backblaze.com/apidocs/b2-list-file-versions), [B2 multipart](https://www.backblaze.com/apidocs/b2-cancel-large-file).

Santiago ejecutó `scripts/crear_bases_operacion.sql` como administrador local, con entrada de contraseña sólo en su terminal. Se verificaron las cinco bases `entrenador_prompts`, `entrenador_prompts_test`, `entrenador_prompts_ops_test`, `entrenador_prompts_restore_test`, `entrenador_prompts_contingencia_test`, todas propietarias de `entrenador_migracion`. No se tocó PostgreSQL 17, otros roles/bases ni datos de desarrollo. `.env` conserva sus contraseñas; preparación de operación completó sólo rutas/destinatario ausentes.

Migración **20261107_0004** primero en pruebas habitual y origen ficticio desde cero; después copia protegida de desarrollo y sólo entonces aplicación en desarrollo. Añade permisos mínimos de catálogo/borrado de raíces, sin tablas ni reescrituras de contenido, DDL/TEMP/TRUNCATE o edición de versiones históricas. Verificación posterior: ejecución DDL=false, tablas propias=0; migración DDL=true, 15 tablas propias; roles sin privilegios elevados/membresías, en desarrollo y pruebas.

## Pruebas y resultados obtenidos

| Comprobación | Esperado | Obtenido |
|---|---|---|
| Regresión completa PostgreSQL/SMTP/motor | Sin fallos ni omisiones | **294 aprobadas, 0 fallidas, 0 omitidas; 114,39 s**. 263 previas + 31 nuevas (19 administración/borrado, 4 operación, 8 retención/B2). |
| Corpus original, motor 1.0.0 | 33/33, incluidos límites CP-25/27/28 | 33 aprobadas, sin cambiar esperados ni dominio. CP-12 sigue aprobado por integración/browser. |
| Tipos y build | `tsc -b` + Vite exitosos | Aprobados; último build 245 ms, 18 módulos; dependencias frontend conservadas. |
| AT-23/INT-03 | Nueva regla sólo futura, V1 intacta/no comparable | Aprobado por API y panel, sin delta/resolución injustificados. |
| AT-24 y regla faltante | Sin borrado histórico; no nuevas versiones inactivas | 405/404 sin ruta destructiva, lectura conservada, nuevas revisiones 409; regla requerida ausente 503 y cero versiones parciales. |
| AT-25/SEC-14 | Una publicación ganadora, catálogo coherente | Dos administradores: 200/409 y una activa. Reemplazo de seis filas con fallo intermedio: rollback total. Publicador real espera al guardado; token viejo luego 409. |
| SEC-07/08/17 y controles previos | Propiedad/CSRF y errores sin secretos | Regresión aprobada; administrador ajeno 404 al borrar práctica, falta CSRF 403, entradas arbitrarias rechazadas, ningún bypass de propiedad. |
| Diario y reintentos | No borrar sin registro; no duplicar solicitud | Corrupción 503 con práctica intacta; fallo SQL 500 con solicitud pendiente y activo intacto; reintento 204 completa la misma solicitud. Fallo de completado tras DELETE no anuncia éxito; reintento recupera. |
| SEC-09/11, INT-05, OPS-01 | No resurrección; sesiones y recuperaciones inválidas | Cuenta y práctica eliminadas después de copia, solicitud de otra cuenta pendiente, tres marcas reaplicadas en dos restauraciones; no reaparecen. Otra cuenta/historial y comparación 3/6→6/6, +50 pp/100 % intactos. Diario corrupto deja CONNECT cerrado. |
| OPS-02 local | Arrancar código sobre copia aislada y leer/comparar | Uvicorn/Vite HTTP 200 y Chrome real: login, historial, V2 y comparación aprobados en contingencia_test. Procesos propios detenidos. |
| OPS-03 local | 7 días/4 semanas, máximo 30; destino acotado | Purga real de 45 conjuntos ficticios autenticados, comprobación exacta de retenidos y repetición sin más borrados; archivo ajeno y otro directorio intactos. No se usa esa fixture de retención como prueba de descifrado/restore. |
| B2 preparado | Versiones antiguas y multipart incluidos | Plan/adaptador verificados con transporte simulado y reenumeración; cero solicitudes reales, sin operación externa acreditada. |
| Programación Windows | XML válido sin terminal/política global | Task Scheduler confirmó TASK_VALIDATE_ONLY. Próximo inicio calculado: 8/11/2026 05:00Z = 02:00 Cordoba. Tarea no registrada. Trabajo directo una vez: aprobado=true, b2_verificado=false, una copia retenida y una diaria anterior purgada. |

Advertencia conservada: Starlette depreca el uso de httpx con TestClient y sugiere httpx2; no se cambiaron dependencias previas para ocultarla. No es un fallo/omisión de pruebas.

**Navegadores reales:** diez grupos de regresión de etapa 04 aprobados nuevamente (formularios/Mailpit, CP-12, reintentos, modo libre, persistencia al reiniciar API/Vite, cambio de clave y sesiones). Seis grupos nuevos de etapa 05: borrador/publicación, regla/historia/no comparabilidad, presentación/teclado/360 px, bloqueo desde panel en Chrome/Edge, borrado de práctica y cuenta. Reportes distinguen `recorrido_funcional_aprobado=true`, `nf02_aprobado=false`, `aprobado=false`; código nativo **2** significa recorrido funcional aprobado con NF-02 pendiente, no aprobación global. Captura del panel a 360 px inspeccionada por Codex, sin desborde y foco visible; no sustituye revisión humana completa.

### Mediciones del último ensayo local

- Restore_test: restauración/integridad/borrados/sesiones en **0,718 s**; edad del backup al completar, **2,005 s**.
- Contingencia_test: restore **0,800 s**, edad del backup **3,408 s**; API/Vite/Chrome hasta lectura/comparación **4,879 s** adicionales. Total medido hasta recorrido recuperado **5,679 s**.
- Los valores locales son inferiores a RTO 4 h/RPO 24 h en este ensayo con copia recién creada y dependencias ya instaladas. No miden descarga externa, instalación de otra máquina, pérdida física del disco ni ejecución diaria continua. No se afirma disponibilidad pública ni garantía RPO/RTO del servicio.

## Comandos ejecutados

Desde la raíz, preparación oficial/local: `python scripts/install_age.py`, `python -m pip install cryptography==50.0.2`, `python scripts/check_operation_databases.py`, `python scripts/prepare_operation_local.py`, usando siempre `.venv\Scripts\python.exe`. El script SQL administrativo lo ejecutó Santiago, no se suministraron claves al chat.

Desde `backend`, con `..\.venv\Scripts\python.exe`:

```powershell
-m app.scripts.operate preparar-pruebas --database entrenador_prompts_test
-m app.scripts.operate preparar-pruebas --database entrenador_prompts_ops_test
-m app.scripts.operate backup --database entrenador_prompts
-m alembic upgrade head
-m pytest tests/access/test_administration.py -q --tb=short
-m pytest tests/operations/test_backups.py -q --tb=short
-m pytest tests/operations/test_retention_b2.py -q --tb=short
-m pytest -q --tb=short --junitxml=../local-data/etapa05-regresion.xml
-m app.scripts.check_motor --json
-m app.scripts.check_access_roles
```

Las líneas anteriores son argumentos del ejecutable indicado, no comandos PowerShell autónomos; comandos completos de reproducción en docs/operacion/ETAPA05_OPERACION_WINDOWS.md. Desde `frontend`: `& "$env:ProgramFiles\nodejs\npm.cmd" run build`. Desde raíz con `.venv\Scripts\python.exe`: `scripts/verify_stage04_browser.py`, `scripts/verify_stage05_browser.py`, `scripts/manage_backup_task.py preparar`, `scripts/manage_backup_task.py validar`, `scripts/scheduled_backup.py`, `-m pip check`, `scripts/check_secrets.py` y, antes del commit, su variante `--staged`; `git diff --check` e inventario/hash de MANIFEST. Los auxiliares detienen únicamente sus procesos temporales; si 18000/15173 están ocupados se niegan a iniciarse.

Evidencia técnica local ignorada por Git: `local-data/etapa05-regresion.xml`, `local-data/etapa05/restauracion.json`, `navegadores.json`, `panel-360.png`, `respaldo-task.xml`; regresión visual previa en `local-data/etapa04/`. Estado de trabajo y copias cifradas en el directorio privado externo. No se guardan HAR, cuerpos, cookies, claves o tokens en esos informes.

## Fallos encontrados y corregidos, sin cambiar expectativas

- Primer respaldo: usar sólo `pg_restore --list` cerraba el pipe antes de que age terminara de verificar. Se cambió a reconstrucción completa hacia NUL; copia verificada antes de migrar desarrollo.
- Primer ensayo del origen ficticio: faltaba DML de acceso que en las bases previas se había concedido con el procedimiento administrativo. Preparación aislada ahora concede exactamente ese DML, sin DDL. Ensayo repetido aprobado.
- Primera colección administrativa: nombre importado del modelo base incorrecto, corregido antes de ejecutar sus pruebas; las 14 iniciales pasaron.
- Una regresión intermedia dio **293 aprobadas/1 fallida**: la prueba de carrera revisaba antes de crear una regla inactiva, que ya cambia el catálogo ligado al token. Se corrigió su preparación para revisar ese estado antes de competir con la publicación; prueba dirigida y regresión final 294/294 aprobadas. No se relajó el contrato ni se modificaron resultados esperados.
- Se normalizaron a LF sólo los saltos introducidos al editar App.tsx; `git diff --check` posterior sin incidencias. Lectura de archivos privados desde sandbox denegada por ACL; verificación de secretos repetida con el usuario propietario, sin mostrar valores ni ampliar permisos.

## Pendientes reales

05.1–05.6: confirmación manual de Santiago de los recorridos nuevos; automatización separada y realizada. Accesibilidad humana completa/NF-01 y NF-03 medido siguen pendientes. NF-02 permanece sin aprobar. La etapa 04 no se vuelve a declarar enteramente aprobada por la confirmación manual parcial.

05.9 general permanece parcial: tarea preparada/validada pero no instalada, ejecución diaria sin sesión interactiva no probada; B2 sin credenciales habilitadas, sin carga/descarga/purga real; custodia offline, redundancia y transferencia independiente del diario/clave/ancla a otro equipo no probadas. No se purgó el diario activo porque no se conoce el estado de todas las copias externas. Registro de tarea y proveedor no son requisito para acreditar los ensayos locales, pero sí para afirmar operación real de respaldo diario y eliminación externa ≤30 días. No se declara esa política externa operativa.

Validación docente/externa y con personas, SMTP productivo/lista de contraseñas comunes de mayor cobertura y cambios académicos/costos/notebook conservan sus pendientes anteriores. No se inventan participantes, dictámenes ni efectos educativos. Guía manual completa: **docs/operacion/ETAPA05_OPERACION_WINDOWS.md**.
