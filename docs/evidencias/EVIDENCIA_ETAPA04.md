# Evidencia de etapa 04 — pantallas, revisión y versiones

**Confirmación manual posterior de Santiago, 7/11/2026:** revisión general de pantallas, recuperación e historial tras cerrar sesión y volver a ingresar. Se conserva la evidencia automática de abajo, sin convertir esta confirmación en aprobación de CP-12 exacto, todas las casillas manuales, reinicio de servicios ni accesibilidad completa. NF-02 sigue pendiente.

Fecha: **7/11/2026**, America/Buenos_Aires. Inicio comprobado: `c331728`, repositorio limpio. Se conservó el trabajo existente; no hubo reset, reconstrucción del proyecto, publicación ni despliegue. El commit que incorpora este archivo identifica el incremento. **Implementación funcional comprobada; NF-02 y revisión humana de accesibilidad pendientes, con los límites indicados abajo.** No se implementó etapa 05.

## Alcance real

Recorridos conectados React/TypeScript → FastAPI → PostgreSQL, sin mocks de persistencia:

- Registro, ingreso, consulta/cierre de sesión, recuperación por Mailpit, formulario de restablecimiento y cambio de contraseña desde perfil. Política 15–128 sin truncar, espacios/Unicode, errores y foco; claves sólo en memoria. El enlace funciona en pestaña nueva y también si la app ya estaba cargada: se captura el fragmento y se retira de la URL.
- Inicio desde desafío publicado u objetivo propio, guiado/libre. Aplicabilidad propia C2/C3/C4 explícita; C1/C5/C6 permanentes. Preparación del objetivo sin guardar hasta confirmar cada coincidencia. Origen/modo/objetivo/configuración quedan fijos.
- Constructor con campos/selecciones de catálogo, declaraciones de libre sin inferencia, revisión preliminar, confirmaciones específicas, guardado de V1 y creación de V2. Vacío total no se guarda; faltantes parciales conservan estados `revisar`. Guiado se ensambla en servidor; libre conserva texto con NFC/LF.
- Resultados históricos con seis criterios, condiciones, evidencia segura, acción y avisos confirmados; texto y componentes originales consultables. Copia sólo con botón explícito. Comparación entre versiones propias, transiciones, delta/resolución y límites sobre alertas/configuración. Historial propio filtrado/paginado y progreso separado por práctica/firma, sin nota global.
- Ambos avisos junto a resultados preliminares y guardados, incluidos 100 %/cero coincidencias: «El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.» y «Estos patrones no detectan toda la información sensible.». Se explica libre y el significado limitado de confirmar. No se modifica el motor **1.0.0** ni los resultados esperados del corpus.
- Carga/vacío/error/éxito, controles nativos con etiquetas asociadas/foco visible y diseño responsive. Ante error de red conserva borrador, revisión y request_id; evita doble envío. Ante 401 retira datos privados, invalida respuestas tardías y consulta revocación cada 15 s/al volver a la pestaña. El sondeo usa `X-Session-Probe: 1`, sin prolongar la inactividad de 30 min. Cambios de cuenta también retiran el contenido anterior.

Las lecturas históricas usan lo guardado, no recalculan con reglas actuales. Los permisos de recursos derivados se comprueban atravesando la práctica; administrador tampoco accede a textos ajenos. Borrado durable de cuenta/práctica y panel de catálogo siguen fuera del incremento.

## Estructura y persistencia

| Archivos | Responsabilidad |
|---|---|
| `backend/app/api/practices.py` | Entradas Pydantic/OpenAPI, rutas, CSRF/sesión y errores seguros. |
| `backend/app/application/practices.py` | Casos de uso, catálogos externos al motor, tokens, confirmación y orquestación transaccional. |
| `backend/app/db/practices.py` | Consultas parametrizadas, separadas de aplicación y dominio. |
| `backend/app/core/config.py`, `scripts/prepare_review_secrets.py` | Claves independientes y configuración local; sólo completar secretos ausentes. |
| `backend/alembic/versions/20261107_0003_practice_permissions.py` | INSERT de prácticas/versiones/evaluaciones/resultados/alertas; UPDATE sólo de actualizado_en de práctica. |
| `backend/app/application/access.py`, `backend/app/api/access.py`, `backend/app/main.py` | Reutilización del guard, sondeo sin renovación, UTC y registro de nuevas rutas. |
| `frontend/src/App.tsx`, `styles.css`, `vite.config.ts` | Formularios y recorridos reales; proxy local y destino alternativo sólo para pruebas. |
| `backend/tests/access/test_practices.py`, `scripts/verify_stage04_browser.py` | Integración PostgreSQL y navegadores reales con fixtures ficticias. |

La migración se aplicó en desarrollo y pruebas usando **entrenador_migracion**; preservó tablas/datos y las credenciales existentes. La API mantiene **entrenador_app**, sin DDL/TEMP/propiedad/membresías ni permisos para modificar versiones/evaluaciones/resultados/alertas guardados. Diagnóstico de ambas bases: DDL=false, tablas propias=0 para ejecución; migración DDL=true y 15 tablas propias. No se alteró PostgreSQL 17 ni se reinició PostgreSQL compartido. Seeds mantienen 6/6/4/24.

Guardado: lock de usuario/validación de sesión → lock asesor compartido de catálogo **90404** → lock de práctica → versión/evaluación/seis resultados/alertas/fecha en una transacción. Publicadores futuros deben tomar el mismo lock **exclusivo** antes de cambiar catálogo/reglas. Esto se ensayó con SQL privilegiado ficticio en pruebas, sin implementar el panel de etapa 05. No se concedió UPDATE de catálogo a la API para obtener locks de filas. El hash idempotente incluye sólo contenido normalizado (sin token/nonce/claves de confirmación): un reintento de algo ya guardado recupera su resultado, no crea ni confirma otra versión. Un nuevo request_id con alertas sin confirmar sigue siendo rechazado. La interfaz conserva el request_id de contenido incluso al volver a revisar después de una respuesta perdida.

Tokens HMAC con operación, usuario, práctica/candidato, hash de entrada/configuración completa, versión de huellas, expiración de 10 min y nonce; sin texto original. Se normaliza y vuelve a detectar al guardar, exige conjunto exacto de confirmaciones y rechaza cambios/vencimiento/alteración/otro ámbito. Idempotencia por request_id y hash de entrada: un reintento igual devuelve el resultado persistido antes de exigir un token que pudo vencer después del commit; distinto contenido genera 409. Siempre revalida sesión/propiedad. Se guardan huellas/versiones sin fragmentos y snapshots de presentación/configuración; nunca se recalculan históricos.

## Entorno y dependencias

Windows/PowerShell, Python 3.11.4/.venv, PostgreSQL 18.6 en 127.0.0.1:5432, Node 26.13.0/npm.cmd, React 19.3.1, Vite 8.3.6 y TypeScript 7.0.2 existentes. Mailpit 1.33.0 en 127.0.0.1:1025/8025. Sin WSL/Docker ni cambio de política PowerShell.

Única dependencia nueva de pruebas: **Playwright 1.64.1**, con **pyee 13.0.1**; greenlet 3.5.6 existente compatible, sin actualizar otras dependencias. Versiones verificadas en [PyPI oficial](https://pypi.org/project/playwright/1.64.1/) y uso de canales según [documentación oficial](https://playwright.dev/python/docs/browsers). Se usan Chrome **156.0.8078.80** y Edge **157.0.4341.42** instalados, con dos procesos/perfiles temporales independientes en modo headless; no son clientes HTTP disfrazados de navegador. No se descargó ni configuró otro navegador ni se modificaron perfiles personales.

## Comandos y resultados ejecutados

Desde raíz, salvo Push-Location explícito:

```powershell
& .\.venv\Scripts\python.exe scripts\prepare_review_secrets.py
& .\.venv\Scripts\python.exe -m pip install playwright==1.64.1
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head
& ..\.venv\Scripts\python.exe -m app.scripts.prepare_test_db
& ..\.venv\Scripts\python.exe -m pytest -q --tb=short --junitxml=..\local-data\etapa04-regresion.xml
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
& ..\.venv\Scripts\python.exe -m app.scripts.check_access_roles
Pop-Location
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run build
Pop-Location
& .\.venv\Scripts\python.exe scripts\verify_startup.py
& .\.venv\Scripts\python.exe scripts\verify_stage04_browser.py
& .\.venv\Scripts\python.exe -m pip check
& .\.venv\Scripts\python.exe scripts\check_secrets.py
```

- **pytest final: 263 aprobadas, 0 fallidas, 0 omitidas, 61,18 s** (JUnit 61,186 s). 223 anteriores + **40 nuevas** de integración de prácticas; base verificada entrenador_prompts_test. Una corrida anterior también pasó 263 en 61,59 s. Las fixtures pertenecen a usuarios ficticios específicos y se eliminan/revierten sólo allí; no se vacía ni reconstruye desarrollo.
- **Corpus: 33/33**, motor 1.0.0. CP-12 se ejecuta por separado con persistencia. No se editaron fixtures esperadas ni dominio del motor. La comprobación anterior de OpenAPI se amplió a las nuevas rutas, conservando la cobertura de acceso.
- **Tipos y build: aprobados** por `tsc -b && vite build`; 16 módulos transformados. Sin dependencias nuevas en frontend. `pip check`: sin requisitos incompatibles.
- **Inicio/reinicio: dos ciclos API y Vite HTTP 200**, HTML/módulo React disponibles, conteos 6/6/4/24 conservados y procesos propios detenidos. También se reiniciaron los servidores temporales durante el recorrido de navegador y se reabrió V2 con la sesión conservada.
- **Chrome/Edge: 10 comprobaciones funcionales aprobadas**, más una observación NF-02 **sin aprobar**, separada abajo. Informe `local-data/etapa04/navegadores.json`; script distingue `recorrido_funcional_aprobado` de `nf02_aprobado`. Devuelve 0 si todo pasa, 1 ante fallo funcional y 2 si el recorrido pasó pero persiste la observación de red. No convierte el tráfico observado en éxito.
- Advertencia conocida: TestClient de Starlette depreca su adaptación a httpx. La combinación fijada funciona; se conserva la advertencia, no se instaló httpx2 para ocultarla.

Reportes XML/JSON y capturas ficticias permanecen en `local-data/`, ignorados por Git. Sin HAR, trazas de cuerpos, contraseñas, cookies, tokens ni enlaces de recuperación en reportes. Las rutas de diagnóstico excluyen query/fragmentos/cabeceras. Los procesos temporales usan puertos **18000/15173**, con PUBLIC_ORIGIN y proxy propios de prueba, y Mailpit local; no toman ni terminan servidores personales en 8000/5173. Si Mailpit ya estaba iniciado se reutiliza sin vaciar su bandeja; si lo inicia el script, lo detiene. La limpieza verifica destino antes de borrar sólo sus cuentas ficticias.

## Cobertura y resultados específicos

| Caso | Resultado obtenido |
|---|---|
| CP-12 / AT-15/17 | V1 CP-31=3/6, V2 CP-01=6/6; V1 íntegra en texto/componentes/fecha/evaluación; delta 50 pp, resolución 100 %, cero alertas nuevas. API y pantallas reales, fixture esperada original comparada sin cambios. |
| AT-07 / tramo preventivo INT-05 | Objetivo con correo no inserta práctica sin confirmar; luego crea. Revisión con alertas no inserta versiones; confirmación parcial 409 y botón deshabilitado; completa conserva avisos. Borrado/restauración de INT-05 no ejecutados. |
| AT-16 / idempotencia | Dos creaciones simultáneas: una creación y un reintento; una práctica. Guardados con igual ID: una versión; distintos IDs: números 1 y 2. Reintento igual después de token inutilizable recupera resultado; distinta entrada 409. Navegador pierde respuesta después del commit y reintenta sin duplicar V2. |
| SEC-10 / INT-04 | Fallo controlado entre versión/evaluación y resultados: 500 genérico, cero nuevas versiones/evaluaciones/resultados; rollback completo. No hay flags de fallo expuestos en API. |
| SEC-12/15/16 | Datos en contexto no aplicable/libre/objetivo se detectan. Correo distinto mismo tipo/campo agrega una alerta; no mejora. Rotación marca relación indeterminada, no recalcula huellas ni oculta avisos. Sin observaciones iniciales resolución null. |
| SEC-13/14 | Rechaza token alterado, de inicio usado como revisión, de otra práctica/usuario, vencido, contenido cambiado, configuración/mensajes/versiones cambiadas. Publicación exclusiva espera guardado compartido; revisión vieja 409 después, sin versión parcial. |
| SEC-02 | Guardado real se serializa antes de bloqueo/desactivación; si éstos ya confirmaron, sesión vieja no llega a escribir. No se basa sólo en ocultar botones. |
| SEC-07 | Usuario y administrador ante práctica/versión/listado/comparación/revisión ajenos: 404; historial/progreso sólo propios. Borrado durable ajeno sigue pendiente con etapa 05. |
| SEC-08/17 | Escrituras sin CSRF/origen adecuado rechazadas; cuerpo inválido con correo sin reflejo en error/log. HTML/script/SQL como datos parametrizados/escapados; en navegador no aparece imagen/ejecución inyectada. No hay endpoint que acepte estados/puntaje/propietario calculados por cliente. |
| Acceso, recuperación, SEC-01 / INT-02 | Formularios de registro/login/logout/recuperación/restablecimiento/perfil contra PostgreSQL. Mailpit recibe correo real. Enlace usado y contraseña anterior rechazados; nueva clave válida; cambio de clave revoca ambas sesiones. Chrome y Edge bloqueados, desbloquear no revive cookies previas. |
| Inactividad / UTC | Sondeo de sesión no toca ultimo_uso; timestamps de prueba 29/31 min verifican validez/vencimiento. Respuestas de fechas UTC; filtros inclusivos Cordoba, orden y paginación de historial/progreso comprobados. |
| UI y persistencia | 360 px sin desborde, foco de teclado, estados y ambos avisos incluso 100 %; libre preservado y sin inferencia, V1/V2/comparación, historial/progreso. Recarga y reinicio conservan datos; errores de red conservan borrador/request_id. Al revocar se retira contenido. localStorage/sessionStorage vacíos en ambos navegadores. |

Correcciones comprobadas durante el trabajo: uso inicial de FOR SHARE con catálogo de sólo lectura (se sustituyó por protocolo asesor compartido/exclusivo sin ampliar DML); adaptador CP-33 que debía crear objetivo propio; asociación explícita de etiquetas a selectores; selectores de prueba con espacios; captura del hash al abrir recuperación en la misma pestaña; portapapeles Windows con CRLF comparado normalizando únicamente saltos de línea. Hubo corridas iniciales fallidas y una espera intermitente durante ingreso; no se contabilizan como aprobadas. Las corridas funcionales posteriores completaron los diez grupos. No se alteraron los resultados esperados de evaluación para obtener esos resultados.

## NF-02: observación real del entorno, pendiente

Durante el recorrido se observaron solicitudes a **http://gc.kis.v2.scr.kaspersky-labs.com** y **http://me.kis.v2.scr.kaspersky-labs.com**, ajenas a los destinos de la aplicación. Se conservan sólo esos orígenes y sus conteos en el informe local, sin identificadores de URL ni contenido. **NF-02 no se declara aprobada.** No se capturaron payloads: no se afirma que esos mensajes contengan prompts, ni se verificó si los destinos salen físicamente de la máquina o son interceptados por protección local.

El código del frontend usa fetch relativo a `/api/v1`; el proxy apunta a loopback y no contiene esos dominios ni código de almacenamiento. La atribución a protección local es una **inferencia compatible** con los dominios y la capacidad de insertar scripts documentada por [Kaspersky](https://support.kaspersky.com/help/Kaspersky/Win21.7/en-US/201001.htm), no una auditoría de su configuración. No se desactivó, desinstaló ni reconfiguró el antivirus; tampoco se excluyeron sus solicitudes para volver verde la comprobación. Repetir NF-02 en un entorno cuya política permita aislar esa interferencia, bajo decisión del responsable del equipo. Usar datos ficticios hasta aclararlo.

## Revisión humana y guía manual en Windows

Santiago ya confirmó **03.M1** en `c331728`; se conserva esa evidencia. **No confirmó todavía las pantallas de etapa 04.** Codex inspeccionó las capturas reales de inicio a 360 px, resultado a 360 px y comparación de escritorio; no son figuras inventadas ni validación educativa. El recorrido completo sólo con teclado, lector de pantalla, contraste/legibilidad y revisión manual de Santiago permanecen pendientes (NF-01 parcial).

Abrir tres PowerShell desde raíz; si hay procesos anteriores, detenerlos con Ctrl+C en sus propias terminales para cargar el código nuevo. No repetir creación de bases ni cambiar políticas de ejecución.

Terminal 1:

```powershell
& .\local-data\mailpit\mailpit.exe --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025 --disable-version-check --smtp-disable-rdns --quiet
```

Terminal 2:

```powershell
Set-Location .\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers
```

Terminal 3:

```powershell
Set-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run dev
```

Abrir **http://127.0.0.1:5173**: formulario Ingresar, Crear cuenta y Olvidé mi contraseña; crear cuenta ficticia con clave local 15–128. No pegar claves en chat/comandos. **http://127.0.0.1:8000/health** muestra estado básico. **http://127.0.0.1:8025** permite abrir el correo: su enlace ahora abre el formulario web y retira el token de la barra; no copiarlo a informes.

1. Registrar/ingresar; repetir registro genérico y probar clave corta con mensaje junto al campo. Recuperar por Mailpit, restablecer, probar enlace usado/clave anterior; ingresar con nueva clave. En Perfil cambiarla y comprobar nuevo ingreso. No esperar inicio automático al restablecer.
2. Elegir **Solicitar una reunión**, modo guiado. Revisar inicio y confirmar. Reproducir la tabla de CP-31 → CP-01 en la sección 04 de docs/historico/COMPROBACIONES_POR_ETAPA_WINDOWS.md: V1 sin fecha/destinatario/detalle, con tarea/acción/finalidad/restricción/formato; debe dar 3/6. Agregar esos tres datos en Crear nueva versión: V2 6/6, diferencia +50 y resolución 100 %. Reabrir V1 y sus componentes; no deben cambiar. Copiar sólo con botón.
3. Probar objetivo propio con `persona@example.invalid`: no continuar hasta confirmar su coincidencia. Probar modo libre, declarar componentes y marcar su confirmación; no debe inferirlos ni reescribir texto. Revisar dos coincidencias, confirmar sólo una y luego ambas. Ver seis estados, los dos avisos y los avisos confirmados incluso con 100 %.
4. Abrir Historial/Progreso, fechas/desafío y más páginas; cerrar/ingresar, recargar y reiniciar API/Vite: datos conservados. Una revisión sin guardar no debe aparecer como versión/progreso. Revisar 360 px y escritorio, Tab/Shift+Tab/Enter/Espacio y etiquetas con lector.
5. Para repetir manualmente revocación, usar **Chrome y Edge** o perfiles realmente independientes con la misma cuenta. No basta otra pestaña del mismo perfil. Registrar una cuenta ficticia administradora separada y promoverla con `manage_access promover-admin --correo` según README. Desde una cuarta terminal en raíz ejecutar `& .\.venv\Scripts\python.exe scripts\change_account_state_manual.py`: pide clave sin eco y usa la API administrativa existente con cookie/CSRF sólo en memoria. Elegir bloqueado, pedir Historial en ambos navegadores (vuelven al ingreso), repetir auxiliar con activo y recargar: exige nuevo ingreso. No publicar capturas de cabeceras. El auxiliar interactivo sigue pendiente de ejecución humana; el mismo endpoint/bloqueo ya tiene prueba automática real. Cambiar clave desde Perfil es otra forma de comprobar revocación global sin panel.

Detener cada uno de los tres procesos con **Ctrl+C**; confirmar cierre de npm si Windows lo solicita. No detener PostgreSQL. Las comprobaciones manuales quedan sin aprobar hasta recibir resultados de Santiago.

## Pendientes expresos

- NF-02: orígenes del antivirus/protección local sin aislar; no se acredita ausencia global de tráfico ajeno.
- NF-01: revisión humana completa, teclado/lector/contraste y confirmación de Santiago de pantallas. Sin participantes ni validación externa inventados; NF-03 no medido en este incremento.
- Etapa 05: borrado durable/diario/restauración completa (SEC-09 tramo backup, SEC-11, final de INT-05 y borrado de SEC-07), panel y publicación real administrativa reutilizando el lock común. Ninguna de esas operaciones se presenta como implementada por las fixtures privilegiadas.
- No se desplegó ni contrató SMTP/hosting, no se publicaron commits y no se modificó el DOCX académico. Secretos y evidencias locales excluidos de Git.
