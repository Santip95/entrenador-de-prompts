# Modelo de datos y persistencia

**Ampliación autorizada D36, 8/11/2026:** motor 1.1.0 añade secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, con prioridad de alertas existentes. Nueva C6 v2 activa en desarrollo, historial sin recalcular, misma confirmación/privacidad/fórmula y sin cambiar regex anteriores. No asegura DNI/teléfono ni cobertura completa; NF-02 continúa pendiente. Contrato en docs/tecnica/EVALUATION_RULES.md y evidencia en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. No cambia el documento académico.

Etapa 06 conserva esquema/head `20261107_0004`, sin reescribir migraciones/historia. Se ejecutó migración desde un esquema realmente vacío sólo en restore_test, tras verificar destino/propiedad/tablas conocidas y cero usuarios/prácticas; seeds repetidos sin duplicar ni sobrescribir. Para instalación nueva, scripts/crear_entorno_nuevo.sql provisiona roles separados y scripts/permisos_ejecucion_acceso.sql completa atómicamente el DML inicial después de Alembic, probado en ese esquema ficticio. No se reprovisionó desarrollo. Demo exclusiva entrenador_prompts_demo, admitida en configuración local de prueba y excluida de destinos destructivos de restore; cuentas/datos ficticios idempotentes.

**Etapa 05:** `20261107_0004` concede INSERT/UPDATE de desafíos/configuración, DELETE sólo de filas de configuración para su reemplazo transaccional, UPDATE de presentación de criterio, INSERT de reglas y UPDATE sólo de activa, y DELETE de raíces práctica/usuario. No concede DDL/TEMP/TRUNCATE ni UPDATE/DELETE directo de versiones, evaluaciones, resultados o alertas. Las cascadas existentes realizan el borrado de dependencias. No se añade ni reescribe contenido histórico. Migración probada primero en pruebas; desarrollo recibió los permisos después de un respaldo cifrado verificado.

Administración usa el lock exclusivo 90404 en toda mutación del catálogo; evaluación/revisión/guardado conservan el compartido. Desafíos se controlan por revisión; presentación por hash de su estado; publicación de reglas por ID activo esperado, todo comprobado dentro de la transacción. El lock 90505 precede a los locks de usuario en restricciones administrativas, borrado de cuenta y comandos locales de privilegio; protege el último administrador frente a operaciones simultáneas. Se conservan el orden de usuarios por UUID y la serialización de guardado/bloqueo existente.

El diario Fernet no es una tabla de esta base ni se incorpora a su dump. Conserva UUID de solicitud/recurso/titular, tipo y fechas. Clave y ancla están separadas del archivo y de las copias; UUID de titular permite resolver un reintento de práctica sin responder éxito a un usuario ajeno. El ancla detecta reemplazo por un diario anterior. Restaurar requiere su estado más reciente, pendientes incluidos; nunca recuperar únicamente el diario de la fecha del backup. Detalles y fallos cerrados en docs/operacion/ETAPA05_OPERACION_WINDOWS.md.

Base: F1 §§11.5–11.6, Figura 3/Tabla 13. Las entidades de dominio se conservan. Los campos de estado, instantáneas, sesiones, recuperación y auditoría amplían el modelo para concretar la seguridad y la trazabilidad. Ver [DER técnico](../diseno/der_tecnico.mmd) y [DER original](../diseno/originales/figura_03_der.png).

## Convenciones

PostgreSQL, identificadores UUID generados en servidor, nombres sin tildes, fechas `TIMESTAMPTZ` en UTC y presentación en zona configurada. Correos normalizados con `strip().lower()` para unicidad; no modificar contraseñas silenciosamente. Texto en UTF-8/NFC. Migraciones Alembic versionadas; no crear/borrar tablas automáticamente al iniciar producción.

## Entidades de dominio

| Tabla | Campos y restricciones principales |
|---|---|
| `usuario` | `id` PK; `correo` VARCHAR(254) UNIQUE NOT NULL; `clave_hash` TEXT NOT NULL; `rol` CHECK usuario/administrador; `estado` CHECK activo/bloqueado/desactivado; `bloqueado_hasta` nullable; `fallos_login` y `ventana_fallos_desde`; `auth_epoch` entero ≥0; `creado_en`, `actualizado_en`. |
| `desafio` | `id` PK; `codigo` UNIQUE; `titulo`, `consigna`; `estado` borrador/publicado/inactivo; `activo` boolean consistente con publicado; `revision` ≥1; timestamps. Catálogo común, sin FK de propietario. |
| `practica` | `id` PK; `usuario_id` FK NOT NULL; `desafio_id` FK nullable; `objetivo` TEXT nullable; `modo` guiado/libre; `configuracion_propia` JSONB nullable; `request_id` UUID; `entrada_hash`; `revision_inicio` JSONB sin fragmentos (tipos/campos/confirmaciones/fecha); `creado_en`, `actualizado_en`; UNIQUE(usuario_id,request_id). CHECK: desafío con objetivo/config propia nulos, u objetivo no vacío sin desafío y con configuración propia. |
| `version_prompt` | `id` PK; `practica_id` FK; `numero` INT ≥1; `componentes` JSONB; `texto` TEXT; `componentes_confirmados` BOOLEAN; `request_id` UUID; `contenido_hash` SHA-256; `creado_en`. UNIQUE(practica_id,numero) y UNIQUE(practica_id,request_id). |
| `criterio` | `id` PK; `codigo` UNIQUE CHECK C1–C6; `nombre`, `descripcion`; timestamps. Identidad/semántica fija; presentación editable para nuevas evaluaciones. |
| `desafio_criterio` | PK(desafio_id,criterio_id), ambas FK; `obligatorio` BOOLEAN; `configuracion` JSONB con aplica/parametros. Seis filas por desafío, validadas al publicar. |
| `regla` | `id` PK; `criterio_id` FK; `tipo` permitido; `parametros` JSONB; `mensajes` JSONB; `version` INT ≥1; `activa` BOOLEAN; `creada_por` FK nullable; `creado_en`. UNIQUE(criterio_id,version). Índice único parcial por criterio WHERE activa. Inmutable salvo activa. |
| `evaluacion` | `id` PK; `version_id` FK UNIQUE; `snapshot` JSONB NOT NULL; `firma_comparacion`; `motor_version`; `cumplidos` INT; `aplicables` INT; `creado_en`. CHECK 0 ≤ cumplidos ≤ aplicables ≤6. |
| `resultado` | PK(evaluacion_id,criterio_id), ambas FK; `regla_id` FK nullable; `estado` cumple/revisar/no_aplica/advertencia; `evidencia` JSONB, `condicion_esperada`, `mensaje`, `accion_sugerida`. CHECK: regla nula solo para no_aplica. |
| `alerta_sensible` | `id` PK; `version_id` FK; `tipo`, `campo`; `estado` confirmada; `huella` HMAC; `clave_version`; `ordinal`; `creado_en`, `confirmado_en`. No fragmento original. Se guardan solo al confirmar y guardar la versión. |

`regla.parametros` contiene operadores/detectores generales; `desafio_criterio.configuracion.parametros` solo puede sobrescribir claves permitidas para ese tipo. Validar combinación completa antes de publicar. `resultado.regla_id` debe pertenecer al mismo criterio: añadir UNIQUE(id,criterio_id) en regla y FK compuesta desde resultado. El estado advertencia solo es válido para C6; no_aplica solo para C2/C3/C4. Usar validación de dominio/transacción o trigger para restricciones entre tablas que un CHECK local no puede expresar.

El modo, origen y configuración propia de práctica son inmutables tras crearla. `actualizado_en` solo cambia por una versión nueva, no por reescribir su objetivo. Una práctica inicial no contiene el texto del prompt; sí conserva el objetivo introducido. **El objetivo se revisa antes de crear la práctica**, con el mismo mecanismo de confirmación preventiva; no basta hacerlo recién al guardar V1.

## Infraestructura añadida

| Tabla | Campos y propósito |
|---|---|
| `sesion` | `id` UUID; `usuario_id` FK; `token_hash` UNIQUE; `auth_epoch_emitido`; `creado_en`, `ultimo_uso_en`, `expira_en`, `revocada_en`. Hash de token aleatorio de 32 bytes; nunca el token original. |
| `recuperacion_acceso` | `id`; `usuario_id` FK; `token_hash` UNIQUE; `expira_en`; `usado_en`; `creado_en`. Un solo uso, 15 minutos. |
| `evento_auditoria` | `id`; `actor_id` nullable; `evento`; `recurso_tipo`; `recurso_id` nullable; `metadatos` JSONB de lista permitida; `creado_en`. Sin prompts, contraseñas, cookies, tokens, fragmentos ni cuerpos completos. |
| `limite_solicitud` | Etapa 03: clave HMAC de ámbito + IP/correo, `desde` UTC y `cantidad`. Contador transaccional compartido entre workers, ventana de 15 minutos. No guarda IP/correo en claro. Se purgan contadores de más de un día al procesar solicitudes. |

El rol técnico es un permiso de infraestructura, no otro rol público de la app. Las credenciales del motor no deben permitir DDL ni lectura de secretos de infraestructura. Las migraciones usan una credencial separada cuando se despliega.

Separación local comprobada en etapa 03: `entrenador_migracion` posee ambas bases, esquema y objetos; `entrenador_app` sólo CONNECT/USAGE/SELECT y DML sobre usuario, sesión, recuperación, auditoría y límites. No tiene CREATE/TEMP, propiedad, membresías ni superusuario/CREATEDB/CREATEROLE/REPLICATION/BYPASSRLS. Las escrituras de prácticas y catálogo se habilitarán explícitamente al implementar sus etapas; los tests de integridad preparan fixtures con la credencial de migración sólo en la base de pruebas. No se conceden permisos DDL ni TRUNCATE a la API. La migración `20261107_0002` añade el contador sin alterar datos existentes. Evidencia: `docs/evidencias/EVIDENCIA_ETAPA03.md`.

Etapa 04: `20261107_0003` habilita INSERT en práctica, versión, evaluación, resultado y alerta y UPDATE únicamente de practica.actualizado_en. No concede UPDATE/DELETE sobre versiones/evaluaciones/resultados/alertas ni edición del catálogo, propiedad, DDL o TRUNCATE. Conserva las tablas y datos existentes. `evaluacion.snapshot.clave_huellas` retiene la versión de clave incluso sin coincidencias; no contiene la clave. Los resultados/huellas se consultan como históricos y no se recalculan.

Protocolo de catálogo concretado: `pg_advisory_xact_lock_shared(90404)` para lecturas de configuración/revisión/guardado, y `pg_advisory_xact_lock(90404)` para futuros publicadores dentro de su misma transacción. Orden: usuario → catálogo → práctica. Todo código administrativo que cambie catálogo debe respetarlo; un cambio SQL privilegiado ajeno al protocolo no se presenta como protegido por este mecanismo. Se probó espera del publicador y rechazo de revisión vieja, sin implementar todavía esos endpoints administrativos.

## Transacción para guardar una versión

1. Comprobar sesión/estado/propiedad y bloquear la fila de usuario durante la escritura para serializarla con bloqueo/desactivación. Nunca permitir que una escritura autorizada antes del bloqueo se confirme después de él.
2. Validar token de revisión y entrada canónica, volver a ejecutar detectores y obtener configuración/reglas bajo una lectura consistente. Serializar publicación de reglas/configuración con evaluación mediante bloqueo de catálogo transaccional común; si cambió desde la revisión, devolver 409 sin escribir.
3. Bloquear la práctica (`SELECT ... FOR UPDATE`), verificar que pertenece al usuario y resolver el `request_id`. Si ya existe con igual contenido, devolver la versión existente. Mismo ID con distinto contenido →409. Comprobar idempotencia antes de exigir que el token original siga vigente en un reintento, pero siempre revalidar sesión/propiedad.
4. Asignar número y crear versión, evaluación, seis resultados y alertas confirmadas; actualizar la práctica. Cualquier fallo revierte todo. No puede quedar una versión sin evaluación.

La API de revisión no escribe cuerpos de prompts ni resultados funcionales. El objetivo propio se revisa en un endpoint previo a crear práctica. Cada token se vincula al tipo de operación para que no sea reutilizable entre inicio y guardado. La confirmación inicial del objetivo se conserva como metadatos seguros en `practica.revision_inicio`; no se crea una alerta con FK a una versión inexistente. Las evaluaciones posteriores vuelven a revisar el objetivo y guardan sus alertas en la versión correspondiente.

## Cambios administrativos

Publicar regla = insertar nueva versión inmutable, desactivar anterior y activar nueva, dentro de una transacción con bloqueo del criterio/catálogo. Actualizar configuración = validar, incrementar revisión y escribir seis filas atómicamente. Publicación y guardado usan el mismo orden de bloqueos para evitar interbloqueos. Ningún cambio reescribe instantáneas de evaluaciones existentes.

Desactivar desafíos/reglas no elimina prácticas ni resultados. Se prohíbe borrar físicamente una regla usada y un desafío referenciado. La eliminación de borradores administrativos no referenciados puede permitirse; no es necesaria para completar la versión inicial.

## Eliminación e índices

`usuario → practica → version_prompt → evaluacion → resultado` y `version_prompt → alerta_sensible` usan eliminación en cascada cuando el propietario elimina su práctica/cuenta. Sesiones y recuperaciones también se eliminan con la cuenta. Auditoría conserva el tipo de evento con actor desvinculado (`SET NULL`), sin correo ni texto. Reglas/desafíos de catálogo usan RESTRICT en vínculos históricos.

Registrar primero la solicitud de eliminación en un diario cifrado externo independiente de la base restaurable, con UUID de recurso, tipo y fecha; luego borrar datos activos de forma transaccional e idempotente. Si el diario no está disponible, fallar con error claro antes de anunciar éxito. Registrar completado después; solicitudes pendientes también se reaplican al restaurar. Retener las marcas al menos hasta que expiren todas las copias que puedan contener esos UUID; después purgarlas. Ver OPERATIONS.

Índices: practica(usuario_id,actualizado_en), version_prompt(practica_id,numero), evaluacion(version_id), resultado(criterio_id), alerta_sensible(version_id), sesion(usuario_id,revocada_en), recuperacion_acceso(usuario_id), evento_auditoria(creado_en). Paginar historiales; no devolver todas las versiones de todos los usuarios.

## Precarga

`seeds/criteria.json`, `rules.json` y `challenges.json` son la fuente inicial. Usar códigos estables y UUID generados o UUIDv5 determinísticos; resolver las FK por código. Una segunda ejecución no duplica ni modifica reglas ya usadas. Si cambia un seed aplicado, crear revisión/versión nueva; no hacer un UPSERT destructivo. No crear cuentas/contraseñas de usuarios por defecto. `examples.json` sirve para demo/pruebas explícitas, no debe aparecer como trabajo real de una persona.
