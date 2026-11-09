# Seguridad y privacidad

**Ampliación autorizada D36, 8/11/2026:** motor 1.1.0 añade secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, con prioridad de alertas existentes. Nueva C6 v2 activa en desarrollo, historial sin recalcular, misma confirmación/privacidad/fórmula y sin cambiar regex anteriores. No asegura DNI/teléfono ni cobertura completa; NF-02 continúa pendiente. Contrato en docs/tecnica/EVALUATION_RULES.md y evidencia en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. No cambia el documento académico.

**Contraste NF-02 del 8/11:** POST histórico positivo (3517 bytes, texto 45/34) con ruta/campo remoto/acción no registrados; no puede reconstruirse exactamente. Repetición acotada CP-31 en Chrome/Edge con textos ficticios y marcador manual: ninguna coincidencia en cuerpos externos visibles, sí en revisión local. GET Ping distinto del POST histórico. No se confirma ni descarta salida física de datos; NF-02 sigue pendiente. Ver docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md. Las observaciones anteriores se conservan como históricas y no se presentan como un hallazgo reproducido hoy.

**Continuación de etapa 06:** rechazo de claves de ejemplo extendido a CSRF/revisión/huellas, con configuración productiva ficticia probada sin desplegar. Santiago confirmó rotación local de contraseña PostgreSQL y CSRF; conexiones/configuración actuales verificadas, sin pedir/comparar valores anteriores. No hay secretos en el índice, reportes ni frontend; credenciales aleatorias de demo sólo en archivo privado fuera del repo. Archivo cifrado de recuperación de configuración/diario separado del dump, identidad age aparte, extracción no destructiva probada con datos ficticios. Exigir diario independiente más reciente antes de reabrir una restauración, no el de un paquete antiguo.

**NF-02 continúa sin aprobar:** CDP mostró scripts ajenos y un POST a gc.kis.v2.scr.kaspersky-labs.com cuyo cuerpo visible coincidió con dos textos ficticios de componentes. No se guardan fragmentos; no se prueba ruta física, firma del componente ni tratamiento final. Producto instalado y dominio no acreditan inocuidad. No se desactivó/reconfiguró protección ni se bloquearon sus solicitudes para aprobar. Evidencia y comprobación restante en docs/evidencias/EVIDENCIA_ETAPA06.md; el límite previo de etapa 04 que no había inspeccionado cuerpos es histórico.

**Estado adicional de etapa 05:** administración real exige rol activo en servidor y CSRF; no concede acceso a prompts ajenos. No hay cambio público de rol ni código/regex arbitrarios. Creación del primer administrador por comando local con getpass, validación de la misma política y rechazo de cuentas existentes. Restricciones y autoeliminaciones administrativas se serializan y rechazan dejar sin administrador habilitado; creación local segura probada para recuperación técnica. Los cambios administrativos futuros no recalculan históricos.

Borrados propios verifican propiedad/clave actual según corresponda, escriben primero el diario Fernet durable y después confirman la transacción PostgreSQL. Reintentos, caída del diario, rollback SQL y solicitud pendiente comprobados. No se anuncian como anonimizados los avisos confirmados ni como eliminados instantáneamente los respaldos. La restauración aislada revoca CONNECT antes de tocar el destino; exige copia autenticada y diario verificable, reaplica pendientes/completados e invalida todas las sesiones y recuperaciones antes de reabrir. Integridad, lectura y comparación conservadas comprobadas con datos ficticios; transferencia externa, custodia offline, B2 y operación diaria reales siguen pendientes. Ver docs/evidencias/EVIDENCIA_ETAPA05.md y docs/operacion/ETAPA05_OPERACION_WINDOWS.md.

Base F1 §13; correcciones F2/F3 sobre sesiones y contraseñas. Los valores concretos adicionales son decisiones de implementación, no controles ya probados.

## Contraseñas y autenticación

Política: 15–128 caracteres; permitir espacios, Unicode y pegado, sin exigir combinaciones de mayúsculas/símbolos. No truncar ni recortar la contraseña. Rechazar valores comunes mediante una lista local documentada y versionada; no enviar la contraseña ni su hash a servicios externos. Aplicar igual política al registrar y restablecer. OWASP recomienda al menos 15 caracteres sin MFA y admitir contraseñas largas; el máximo 128 es una elección del proyecto.

Hash Argon2id, sal aleatoria individual, mínimo `memory_cost=19456 KiB`, `time_cost=2`, `parallelism=1`. Usar una biblioteca mantenida y su formato de hash completo; no implementar criptografía propia. Medir costo en el entorno y elevar parámetros si es viable. No reducir el mínimo para ocultar un problema de rendimiento.

Etapa 03: argon2-cffi 25.1.0, configuración local elevada a 65536 KiB/3/1 tras medir mediana de hash de 116,9 ms (10 mediciones; mínimo anterior: 25,2 ms). Se verifica y actualiza un hash anterior al ingresar correctamente. Se conservan los pisos de este contrato. La lista local inicial `app/application/common_passwords.json` (versión 1: 12 entradas explícitas) se compara con `casefold`, sin recortar la clave. Es una cobertura limitada, no un catálogo exhaustivo de claves filtradas; no se consulta ningún servicio externo. Debe revisarse/ampliarse al preparar producción, sin cambiar la admisión de espacios/Unicode.

Inicio inválido: mensaje genérico para correo desconocido, contraseña incorrecta o cuenta no habilitada. Ejecutar una verificación de hash equivalente para correos inexistentes. Después de cinco fallos en una ventana de 15 minutos, bloqueo por 15 minutos y revocación de todas las sesiones. Añadir límite por IP en memoria compartida o almacenamiento de servidor compatible con varios workers; no depender únicamente del navegador. El bloqueo administrativo no vence automáticamente. El bloqueo temporal usa `estado=bloqueado` y `bloqueado_hasta`; al vencer, devolver atómicamente la cuenta a activo sin reducir `auth_epoch` ni reactivar sesiones. El bloqueo administrativo deja `bloqueado_hasta` nulo.

Valores técnicos de etapa 03: por IP, 20 ingresos, 10 registros, 5 solicitudes de recuperación, 10 restablecimientos y 5 cambios de clave cada 15 minutos; por correo, hasta 3 recuperaciones en esa ventana (respuesta genérica aun si se agota). PostgreSQL resuelve los contadores atómicamente; la clave HMAC usa CSRF_SIGNING_KEY estable entre workers. La rotación de esa clave invalida CSRF y reinicia el ámbito de contadores, sin conservar IP/correo en claro. En local, iniciar Uvicorn con `--no-proxy-headers` y `--no-access-log`; no confiar en X-Forwarded-For enviado por clientes. Al desplegar, definir y probar el proxy confiable antes de reabrir servicio.

La purga de contadores antiguos se limita a lotes de 1000 con `FOR UPDATE SKIP LOCKED`, para evitar interbloqueos con otra solicitud que esté refrescando una fila vencida. Se comprobó con dos conexiones sincronizadas después del UPSERT y antes de purgar.

## Sesión y revocación inmediata

Token aleatorio opaco de 32 bytes en cookie `HttpOnly`, `Secure` en producción, `SameSite=Lax`, `Path=/`, sin Domain amplio. Guardar solo hash del token en PostgreSQL. Nunca usar localStorage para sesión. Rotar al autenticar y cambiar privilegios; no aceptar un ID de sesión elegido por el cliente. Inactividad máxima 30 minutos; máximo absoluto 8 horas desde creación, con cálculo del servidor.

En cada solicitud protegida consultar sesión y usuario: revocación, expiración, último uso, estado activo y coincidencia de `auth_epoch`. Si falla, 401 y borrar cookie. Los cambios de rol deben surtir efecto en esa consulta, no depender de roles copiados en el cliente.

Bloquear/desactivar/cambiar contraseña: en una transacción bloquear usuario, actualizar estado o hash, incrementar `auth_epoch` y marcar todas sus sesiones revocadas. No basta borrar cookies ni esperar vencimiento. Toda escritura protegida toma el mismo bloqueo de usuario y vuelve a comprobar estado antes de confirmar: una petición concurrente termina antes del bloqueo o se rechaza después. Para lecturas, comprobar en cada petición; una respuesta ya enviada no puede retirarse.

El desbloqueo devuelve el usuario a activo, pero no reactiva tokens anteriores. Un cierre de sesión revoca la sesión actual en el servidor. La restauración de la base invalida todas las sesiones y recuperaciones antes de reabrir el servicio.

## Recuperación y control de solicitudes

Recuperación por token aleatorio de un solo uso, guardado como hash y válido 15 minutos. Responder igual exista o no la cuenta. Entregar enlace únicamente por correo de recuperación, con origen construido desde configuración confiable, no desde Host de la petición. En desarrollo utilizar capturador SMTP local; en producción configurar SMTP real antes de habilitar recuperación. Nunca mostrar el token en API o logs. No usar una cuenta real como seed.

El enlace local usa fragmento `/#restablecer=…`, que no se envía al servidor HTTP. Su formulario queda pendiente de etapa 04: las pruebas actuales extraen el token del correo únicamente en memoria y lo envían por JSON al endpoint. Si SMTP falla, recuperación conserva 202 genérico, registra sólo el evento codificado `correo_no_disponible` y no activa un token; no expone el error ni promete entrega. Las pruebas sí comprueban entrega real a Mailpit. En producción se requiere TLS y autenticación SMTP; ese proveedor no fue configurado ni probado.

Consumir token y cambiar clave atómicamente; dos consumos concurrentes deben permitir uno solo. Invalidar otros tokens y sesiones. No reactivar una cuenta bloqueada/desactivada mediante recuperación. No iniciar sesión automáticamente tras restablecer.

Un único origen público para frontend y API. Validar Origin y token CSRF en operaciones de escritura autenticadas; obtener el token CSRF por endpoint ligado a la sesión y conservarlo solo en memoria. En login/registro/recuperación validar origen, tipo de contenido y límites de frecuencia. CORS solo para orígenes explícitos en desarrollo; nunca `*` con cookies. Escape de texto en React; no interpretar prompts como HTML ni usar `eval`. Consultas parametrizadas y validación de esquemas.

## Revisión antes de persistir

El objetivo propio también puede contener datos sensibles: revisar antes de crear su práctica. Para el prompt, `revisar` evalúa en memoria y devuelve un token firmado sin texto original. Firma el tipo de operación, usuario, práctica cuando existe, hash de contenido, firma de configuración, versión de clave de alertas, expiración y nonce. Utilizar serialización JSON canónica y comparar firma de forma constante.

Al confirmar y guardar, reenviar el contenido y las claves de todas las coincidencias confirmadas. El servidor verifica token, contenido, configuración y conjunto exacto; vuelve a detectar. Una simple bandera `acepto=true` no basta. Cada token vence en 10 minutos. Si cambió algo, devolver 409 y pedir nueva revisión. No persistir texto pendiente, fragmentos en alertas, cuerpos en logs ni borradores en almacenamiento del navegador.

Las alertas conservadas llevan una huella HMAC, calculada con `ALERT_FINGERPRINT_KEY` separada de la firma de revisión y con `ALERT_FINGERPRINT_KEY_VERSION`. Se usa solo para comparar dentro de la misma práctica. Rotar la clave obliga a informar la imposibilidad de comparar huellas entre versiones cuando no haya una forma compatible; no recalcular históricos con datos que ya fueron borrados.

Etapa 04 comprobada: claves ausentes completadas localmente por `scripts/prepare_review_secrets.py`, sin reemplazar existentes ni imprimirlas; API exige 32 bytes mínimos e independencia de revisión/huellas/CSRF y versión positiva. El token firmado contiene sólo hashes y metadatos, no texto. Al reintentar un guardado ya confirmado, se resuelve idempotencia con hash/request_id antes de exigir la vigencia de la revisión, siempre después de revalidar sesión/propiedad. Confirmación exacta de coincidencias y recálculo de estados exclusivamente en servidor. La clave de huellas nunca se devuelve en snapshots o comparaciones.

Frontend: estado privado sólo en memoria, sin storage persistente. Sondeo cada 15 s/al recuperar foco con X-Session-Probe, que no prolonga inactividad. Un 401/cambio de cuenta retira datos y una generación de sesión descarta respuestas tardías. El enlace de recuperación se procesa al cargar y al cambiar fragmento en la misma pestaña; luego se retira de la URL. Contraseñas Unicode/textos no se truncan con maxlength de unidades UTF-16; backend mantiene límites y el formulario valida longitud de clave sin recortar.

**Límite observado NF-02:** Chrome/Edge registraron orígenes kaspersky-labs.com ajenos al código de la app. La procedencia es compatible con protección local, pero no se auditó su configuración/ruta física ni los payloads. No se desactivó esa protección y no se acredita ausencia global de tráfico ajeno; pendiente de aislar con el responsable del entorno. Evidencia y fuente oficial en docs/evidencias/EVIDENCIA_ETAPA04.md. Todos los datos de estas pruebas fueron ficticios.

## Acceso y minimización

Todos los recursos derivados verifican propiedad atravesando práctica: versiones, resultados, alertas y comparación. Para un recurso ajeno responder 404; no exponer su existencia. Panel administrativo puede gestionar catálogo/cuentas, no texto ajeno. No implementar lectura excepcional de soporte en el MVP; si se necesitara después requeriría autorización y auditoría específicas.

Logs por lista permitida: request_id, ruta sin parámetros sensibles, status, duración, evento y UUID técnico cuando sea necesario. Excluir cuerpos, correos, contraseñas, cookies, cabeceras de autenticación, tokens, huellas y texto de prompts. Cifrar respaldos antes de salir del entorno; B2 privado. El prompt confirmado queda almacenado en la versión: el sistema no promete anonimizarlo automáticamente.

El usuario puede eliminar práctica y cuenta. Explicar que se elimina del entorno activo y de copias rotativas en máximo 30 días, con medidas para que una restauración no lo reintroduzca. No prometer detección completa ni seguridad absoluta.

## Configuración de producción

Rechazar arranque si la política configura un mínimo inferior a 15 o un máximo inferior a 64, si faltan claves/DB, si hay claves de ejemplo, cookie Secure desactivada, origen no HTTPS, logs de cuerpos activos o datos demo habilitados. Secretos solo en servidor/gestor del proveedor. `.env.example` queda vacío donde corresponda; no rellenarlo con secretos funcionales. No desactivar autenticación para facilitar una demo pública.

Fuentes verificadas y alcance de las decisiones: `docs/tecnica/DECISIONS.md`. Pruebas obligatorias: `docs/tecnica/ACCEPTANCE_TESTS.md`, grupo SEC.
