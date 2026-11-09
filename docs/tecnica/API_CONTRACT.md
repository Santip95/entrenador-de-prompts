# Contrato de API

**Ampliación autorizada D36, 8/11/2026:** motor 1.1.0 añade secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, con prioridad de alertas existentes. Nueva C6 v2 activa en desarrollo, historial sin recalcular, misma confirmación/privacidad/fórmula y sin cambiar regex anteriores. No asegura DNI/teléfono ni cobertura completa; NF-02 continúa pendiente. Contrato en docs/tecnica/EVALUATION_RULES.md y evidencia en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. No cambia el documento académico.

**Actualización etapa 05:** implementadas las rutas administrativas y DELETE de práctica/cuenta indicadas abajo. El panel utiliza esos endpoints contra PostgreSQL. `GET /admin/desafios`, `/admin/reglas` y `/admin/cuentas` paginan por UUID, limit 1–100; criterios devuelve los seis y los catálogos permitidos. Crear desafío recibe código estable, título, consigna, configuración completa y `revision_esperada=null`; PUT exige la revisión actual y código original. Publicar/desactivar desafío exige `revision_esperada`. PATCH criterio sólo admite nombre, descripción y `revision_esperada` (hash de su presentación obtenido del listado). Crear regla sólo admite criterio_codigo, tipo fijo, parámetros y mensajes; servidor asigna versión y la deja inactiva. Publicar/desactivar regla requiere `regla_activa_esperada` (UUID o null), comparada bajo lock exclusivo; no se permite reemplazar contenido de una regla existente. Configuración inválida 422; regla activa necesaria ausente 503; revisión antigua 409. No hay DELETE de catálogo/versiones ni cambio de rol público.

DELETE de práctica exige sesión propietaria/CSRF; reintento propio ya registrado en diario devuelve 204. DELETE cuenta exige clave actual, CSRF y límite de intentos; después de eliminarla la sesión ya es inválida (401 al reintentar). Diario no verificable/disponible produce 503, sin anunciar éxito. Los cambios de estado y borrados de administrador se serializan con un lock global: no pueden dejar sin administrador habilitado. La creación local segura está probada y se levanta la restricción conservadora histórica que rechazaba restringir a cualquier administrador; el último sigue protegido. Evidencia: docs/evidencias/EVIDENCIA_ETAPA05.md. Los párrafos históricos siguientes no describen el estado nuevo.

Prefijo `/api/v1`. JSON en UTF-8, fechas ISO 8601 UTC y UUID como cadenas. Autenticación mediante cookie de sesión; CSRF según SECURITY. No adoptar estos endpoints como ya implementados. El agente debe generar OpenAPI a partir de los modelos reales y comprobarlo contra este contrato.

Estado comprobado de etapa 03: implementadas las operaciones de acceso salvo DELETE `/cuenta` (borrado durable/diario, etapa 05), más GET `/admin/cuentas` y POST `/admin/cuentas/{id}/estado`. No están implementadas las operaciones funcionales de prácticas/versiones/progreso ni administración de catálogos. OpenAPI se genera desde `app/api/access.py` y puede consultarse en `/openapi.json`; las cabeceras de sesión se envían como cookie y `X-CSRF-Token` en escrituras autenticadas. Origin debe coincidir con PUBLIC_ORIGIN y los POST usan application/json, incluido logout con `{}`. Se rechazan entradas adicionales como un rol elegido durante registro. No hay formulario web de restablecimiento hasta etapa 04. Las respuestas privadas llevan Cache-Control: no-store.

**Actualización etapa 04:** el párrafo anterior describe el cierre histórico de etapa 03. Ya están implementadas las rutas de catálogo publicado, preparar/crear/consultar prácticas, revisar/guardar/listar versiones, versión individual, comparación y progreso, junto con las pantallas de acceso/restablecimiento y prácticas. DELETE `/cuenta` y DELETE `/practicas/{id}`, administración de catálogo y restauración durable siguen pendientes de etapa 05. Evidencia vigente: `docs/evidencias/EVIDENCIA_ETAPA04.md`; no se consideran implementados por aparecer en las tablas contractuales.

Entrada de inicio: `modo`, `desafio_id` o `objetivo` + `aplicabilidad` (exactamente C2/C3/C4 booleanos). Crear añade `token_inicio`, `coincidencias_confirmadas` (claves) y `request_id` UUID; primer éxito 201 y reintento idempotente 200. Revisar recibe el borrador canónico completo; guardar recibe `borrador`, `token_revision`, `coincidencias_confirmadas`, `request_id`. No acepta estados/nota/propietario ni campos extra. Los tokens exitosos se entregan sólo para reenviar por cuerpo, nunca como URL de revisión. Preparar/revisar no guardan contenido funcional pendiente.

Los listados usan limit 1–100/cursor UUID de recurso propio: historial descendente por actualizado_en/UUID, versiones por número ascendente, progreso por fecha/UUID ascendente y agrupado por práctica/firma (la paginación puede dividir una serie, que la interfaz reúne). Fechas desde/hasta inclusivas en APP_TIMEZONE=America/Argentina/Cordoba; salida UTC. GET `/auth/me` admite `X-Session-Probe: 1` para comprobar revocación sin renovar ultimo_uso; no elude ninguna validación. No usar el sondeo como señal de actividad del usuario.

Los motivos de estado permitidos en esta versión son `solicitud_titular`, `seguridad`, `incumplimiento` y `correccion`. Hasta comprobar una vía de recuperación administrativa, restringir cualquier administrador devuelve 409: este límite conservador incluye al último administrador. Promoción local privilegiada por `app.scripts.manage_access`, con revocación; no es una operación pública ni un panel implementado.

## Errores y convenciones

Error uniforme: `{"error":{"code":"codigo_estable","message":"Mensaje en español","fields":[],"request_id":"uuid"}}`. No devolver trazas, SQL, secretos ni cuerpos que puedan contener fragmentos sensibles. Reemplazar mensajes de validación que reflejen valores originales.

400: formato imposible de interpretar; 401: sesión ausente/inválida; 403: rol/CSRF no permitido; 404: recurso ausente o ajeno; 409: conflicto/revisión vencida/configuración cambiada; 413: tamaño; 422: esquema/selección inválida; 429: límite de frecuencia; 503: configuración o dependencia no disponible. No convertir una regla incumplida en error HTTP: una revisión válida devuelve estados `revisar`/`advertencia`.

Listados con `items`, `next_cursor`; límite por defecto 20, máximo 100. Historial ordenado por última actualización descendente y UUID como desempate. Los filtros de fecha son inclusivos desde/hasta por fecha local convertida a UTC; documentar la zona. No permitir paginación por usuario arbitrario.

## Operaciones públicas y cuenta

| Método y ruta | Entrada | Resultado |
|---|---|---|
| POST `/auth/registro` | correo, password | 202 genérico tanto si se creó la cuenta como si el correo ya existe; no inicia sesión ni devuelve ID/hash. |
| POST `/auth/login` | correo, password | 200; cookie nueva, perfil mínimo. Error genérico 401/429 según límites. |
| POST `/auth/logout` | CSRF; sin cuerpo sensible | 204; revoca sesión y elimina cookie. |
| GET `/auth/me` | sesión | id, correo, rol; nunca epoch/hash/token. |
| GET `/auth/csrf` | sesión | token CSRF ligado a sesión, solo en memoria del cliente. |
| POST `/auth/recuperacion` | correo | 202 genérico; enviar enlace por SMTP si procede. |
| POST `/auth/restablecer` | token, password_nueva | 204; consume una vez, revoca sesiones; error genérico si inválido/vencido. |
| POST `/cuenta/cambiar-clave` | password_actual, password_nueva | 204; revoca todas las sesiones, exige ingresar de nuevo. |
| DELETE `/cuenta` | password_actual; CSRF | 204; solicita borrado durable, elimina cuenta y dependencias. |

Registro: mismo cuerpo para ambos casos, «Si los datos permiten crear una cuenta, ya podés intentar ingresar». Un error de formato de correo o de política de contraseña sí devuelve 422, sin reflejar la contraseña.

## Catálogo y creación de práctica

| Método y ruta | Entrada | Resultado |
|---|---|---|
| GET `/desafios` | sesión | Desafíos publicados, consigna y configuración visible; sin claves privadas. |
| GET `/desafios/{id}` | sesión | Configuración vigente, etiquetas/selecciones, revisión y criterios. |
| POST `/practicas/preparar` | desafio_id **o** objetivo+aplicabilidad; modo | 200; revisión preventiva del objetivo, coincidencias, token_inicio. No persistir todavía. |
| POST `/practicas` | misma entrada + token_inicio + coincidencias_confirmadas + request_id | 201; práctica propia. Si falta confirmar alguna coincidencia →409. |
| GET `/practicas` | sesión, filtros fecha/desafío | Historial propio paginado; título, fecha, última versión e indicador. |
| GET `/practicas/{id}` | sesión propietaria | Origen/modo/configuración y resumen; sin reescribirlo. |
| DELETE `/practicas/{id}` | CSRF | 204; diario de borrado y cascada. |

Preparar también valida objetivo no vacío y configuración. Para desafío, objetivo y configuración propia son nulos. El objetivo, aun sin coincidencias, se somete al token para asegurar que los datos revisados son los que se guardan. `request_id` asegura idempotencia por usuario: igual ID/igual entrada devuelve la práctica existente; ID repetido con otra entrada →409.

## Revisión, guardado y comparación

| Método y ruta | Entrada | Resultado |
|---|---|---|
| POST `/practicas/{id}/revisar` | Borrador canónico de EVALUATION_RULES | 200; revisión preliminar, coincidencias, token_revision y configuración aplicada. Sin persistencia funcional. |
| POST `/practicas/{id}/versiones` | borrador + token_revision + coincidencias_confirmadas + request_id | 201 con versión/evaluación; reintento idempotente 200. |
| GET `/practicas/{id}/versiones` | sesión propietaria | Lista paginada; número, fecha, indicador y advertencias. |
| GET `/versiones/{id}` | sesión propietaria | Texto, componentes y resultado histórico completo. |
| GET `/practicas/{id}/comparacion?desde={uuid}&hasta={uuid}` | dos versiones de esa práctica | Textos/componentes, estados, alertas, comparable, razón, delta_pp y resolución. |
| GET `/progreso?desde={fecha}&hasta={fecha}` | sesión propia | Series por práctica/configuración y proporciones; no nota global ni mezcla de rúbricas. |

No existe PATCH/PUT de versión/evaluación. Borrador+token se envían en cuerpo JSON, nunca en URL. Guardar no acepta estados, reglas, puntaje ni usuario_id enviados por el cliente. El servidor vuelve a calcular todo y compara configuración/firma. Token vencido, edición posterior o alertas sin confirmar producen 409 sin insertar versiones.

Respuesta de revisión: `preview=true`, `texto` calculado o libre, `resultados` (6), `cumplidos`, `aplicables`, `cumplimiento`, `coincidencias`, `token_revision`, `vence_en`. Coincidencia: clave opaca, tipo, campo y mensaje. El texto completo es accesible solo a su autor y se devuelve con `Cache-Control: no-store`; no repetir fragmentos en evidencia.

Respuesta guardada: `preview=false`, IDs de práctica/versión/evaluación, número, fecha, seis resultados, conteos, porcentaje, avisos confirmados y versión/configuración aplicada. La confirmación cambia C6 a cumple, pero conserva avisos visibles. Nunca devolver la clave de huellas ni hashes de sesión.

Comparación: estados por código con transición anterior→actual; diffs de texto escapado, no HTML generado a partir del prompt; `alertas_nuevas` como cantidad/tipos o null si no determinable. `mejora_estructural=true` solo con firma equivalente, delta>0 y ausencia comprobada de alertas nuevas. Un valor false no significa que el texto sea peor semánticamente.

Transferencia y comprensión educativas se registran en instrumentos de validación, sin añadir un panel de investigación obligatorio al MVP. La API de progreso ofrece datos propios necesarios; el investigador no obtiene acceso a prompts ajenos por ser administrador. Cualquier registro de validación se toma con consentimiento de la persona.

## Administración

| Método y ruta | Uso |
|---|---|
| GET/POST `/admin/desafios` | Listar catálogo completo o crear borrador. |
| PUT `/admin/desafios/{id}` | Con `revision_esperada`: en borrador, editar sin publicar; en publicado, validar y publicar nueva revisión atómicamente. 409 si cambió. |
| POST `/admin/desafios/{id}/publicar` | Validar y publicar revisión atómica. |
| POST `/admin/desafios/{id}/desactivar` | Retirar de nuevas prácticas/versiones; conservar historia. |
| GET `/admin/criterios` | Los seis criterios; no textos de usuarios. |
| PATCH `/admin/criterios/{codigo}` | Nombre/descripción; código/semántica invariables. |
| GET/POST `/admin/reglas` | Consultar versiones o crear versión nueva, validada e inicialmente inactiva. |
| POST `/admin/reglas/{id}/publicar` | Activar y desactivar anterior de ese criterio atómicamente. |
| POST `/admin/reglas/{id}/desactivar` | Detener futuras evaluaciones que la requieren, con error de configuración visible. |
| GET `/admin/cuentas` | Datos mínimos para bloqueo: id, correo, estado y rol; sin prácticas. |
| POST `/admin/cuentas/{id}/estado` | activo/bloqueado/desactivado, motivo codificado; revocar todas las sesiones al restringir. |

Todas requieren administrador activo y CSRF en escrituras; los permisos se comprueban de nuevo en la API. No exponer un cambio de rol público ni permitir desactivar al último administrador sin una vía de recuperación operativa comprobada.
