# Decisiones para cerrar el contrato de implementación

Las decisiones D01–D15 completan vacíos o contradicciones de la Entrega 3. Son la base propuesta para programar, no resultados de validación ni instrucciones textuales de la docente. Si se cambian, actualizar contrato, seeds y pruebas juntos.

| ID | Decisión | Motivo y origen |
|---|---|---|
| D01 | Todos los criterios aplicables, incluido C6, cuentan una unidad; sin pesos. | Tabla 7 usa un cociente de criterios y Tabla 12 incluye seguridad, pero no detalla cómo integrarla. Se explicita esta interpretación para evitar ponderaciones inventadas. |
| D02 | C6 se cumple si no hay coincidencias o todas fueron revisadas y confirmadas; se conserva el aviso visible. | Traduce literalmente «sin coincidencias activas o revisión confirmada». Cumplir la revisión no certifica privacidad. |
| D03 | Objetivo propio: C1/C5/C6 obligatorios; C2/C3/C4 elegibles al crear práctica. | La entrega permite objetivo propio, pero no define una rúbrica. No se deduce aplicabilidad del texto. |
| D04 | Un registro `regla` por criterio y versión contiene verificaciones conjuntivas. | Tabla 13 prevé un `regla_id` por resultado y `UNIQUE(criterio_id, version)`. Evita múltiples resultados incompatibles con esa clave. |
| D05 | Evaluaciones guardan instantánea de catálogo, parámetros efectivos, mensajes, nombres y versión del motor. | La FK a regla sola no conserva cambios de `desafio_criterio` ni de mensajes. |
| D06 | Diferencias de regla/configuración impiden calcular automáticamente delta, resolución o transferencia. | Evita confundir cambio de condiciones con mejora. Los valores históricos se muestran igual. |
| D07 | Sesión opaca respaldada en PostgreSQL y verificación de usuario en cada operación. | Da efecto inmediato al bloqueo/desactivación pedido por la docente. Se agregan estructuras de sesión, recuperación y auditoría. |
| D08 | Contraseña de 15 a 128 caracteres, sin reglas arbitrarias de composición; Argon2id. | La devolución exige revisar el mínimo de 8. El valor concreto es una decisión apoyada en OWASP consultado el 4/11/2026; no lo indicó la docente. |
| D09 | Revisión preliminar sin persistir texto, confirmación vinculada mediante token firmado y guardado atómico. | Implementa HU-03 sin crear primero una versión con datos que aún no fueron revisados. |
| D10 | Retención máxima de respaldos 30 días, suprimiendo las tres copias mensuales de la tabla original. | §13 promete eliminar datos de copias en 30 días, incompatible con retener tres meses. Diario de borrados independiente para evitar reintroducirlos al restaurar. |
| D11 | Borrado de práctica/cuenta elimina sus datos activos; las versiones son inmutables mientras existen. | Reconcilia RF-03 con §6.5 y §13. No usar inmutabilidad como impedimento para borrar. |
| D12 | Crear cuatro desafíos ficticios, con dos correos de configuración equivalente para línea base/transferencia. | La entrega ejemplifica correo y lluvia de ideas, pero no aporta un catálogo completo. Es material nuevo para implementar y revisar. |
| D13 | Sesión absoluta de 8 horas, revisión válida 10 minutos y límites de texto expresos. | Completa límites técnicos no definidos en la entrega; inactividad de 30 min y recuperación de 15 min sí provienen de ella. |
| D14 | Un origen público para interfaz y `/api`; TLS en producción, proxy local en desarrollo. | Reduce complejidad de cookies/CORS/CSRF y permite contenerizar sin atar el código al proveedor. |
| D15 | Guardar confirmación inicial del objetivo y comparar alertas mediante huellas HMAC sin fragmentos adicionales. | Extiende prevención a los textos que se persisten antes de V1 y evita confundir alertas nuevas con anteriores del mismo tipo. |
| D16 | El desarrollo local se ejecuta directamente en Windows con PowerShell: Node.js/npm, Python en `.venv`, PostgreSQL local y Mailpit local, conectados por `127.0.0.1`. No se usa WSL, Ubuntu ni Docker para desarrollar. | Fija el entorno solicitado para que el arranque, migraciones, pruebas y correo de prueba sean reproducibles en el equipo local. Los contenedores quedan como una opción separada para un despliegue futuro, no como requisito de desarrollo. |
| D17 | La instancia local elegida es PostgreSQL 18.6: el servicio `postgresql-x64-18` atiende `127.0.0.1:5432`. La aplicación usará sus clientes 18 y un rol propio sin privilegios de superusuario. | La comprobación de procesos del 6/11/2026 vinculó el proceso listener con el servicio 18. PostgreSQL 17 permanece instalado y sin cambios; usar un solo mayor evita mezclar clientes, datos o configuraciones. |
| D18 | Separar localmente `entrenador_migracion` propietario y `entrenador_app` con DML de acceso y lectura, sin DDL/TEMP ni membresías. | Ajuste pendiente resuelto en etapa 03 tras preparación administrativa de Santiago; se preservan bases/datos. La API no recibe credencial de migración en producción. |
| D19 | Argon2id con argon2-cffi 25.1.0 y valores locales 65536 KiB/3/1; lista común local inicial versión 1, de cobertura limitada. | El 7/11/2026 se midieron 10 hashes: mediana 116,9 ms frente a 25,2 ms del mínimo 19456/2/1. Se eleva el costo viable; no se cambia longitud ni se envían claves a servicios. |
| D20 | Contadores de frecuencia en PostgreSQL, claves HMAC de IP/correo y ventana 15 minutos; límites concretos en docs/tecnica/SECURITY.md. | Compartir entre workers, sin almacenar IP/correo en claro ni agregar Redis. Los valores son decisiones técnicas, no de la docente. |
| D21 | Mailpit 1.33.0 oficial para Windows amd64 con SHA-256 fijado; enlace de recuperación en fragmento URL. | Captura local real sin Docker; el fragmento evita token en URL de solicitudes HTTP. El formulario web y sus avisos quedan en etapa 04. |
| D22 | Rechazar restricción de administradores hasta probar una vía de recuperación; promoción sólo mediante comando local privilegiado con revocación. | Cumple la protección del último administrador sin inventar recuperación operativa no probada ni añadir un cambio de rol público. El panel sigue en etapa 05. |
| D23 | Lock asesor transaccional 90404: compartido al cargar/evaluar/guardar catálogo y exclusivo para publicadores; orden usuario→catálogo→práctica. | Serializa futuras publicaciones sin conceder UPDATE de catálogo a la API de etapa 04. Prueba real con publicador SQL ficticio; su API/panel continúan en etapa 05. |
| D24 | Resolver idempotencia ya persistida por request_id/hash después de autorizar y antes de validar vencimiento de token. | Permite recuperar una respuesta perdida tras el commit sin duplicar; no permite cambiar entrada ni usar sesión revocada. Token íntegro/vigente obligatorio en el primer guardado. |
| D25 | Sondeo de sesión sin renovación de inactividad, descarte de respuestas tardías y recuperación también por hashchange. | Evita que el sondeo mantenga indefinidamente la sesión y que sobreviva contenido privado a una revocación/cambio de cuenta; el enlace sirve en la pestaña ya abierta y no queda en URL. |
| D26 | Playwright 1.64.1/pyee 13.0.1 sólo para pruebas, con Chrome y Edge instalados y puertos temporales 18000/15173. | Verifica pantallas y sesiones reales sin instalar navegadores adicionales, alterar perfiles personales ni usar Docker/WSL. NF-02 se informa separado, sin excluir tráfico ajeno observado. |

## Continuación técnica de etapa 05

- **D27:** age 1.3.2 oficial Windows amd64, SHA-256 `f48d8f8f9ebe903ab5027ed067652f2cc1db94bc206976430133b905dcd8e8c7`, para pg_dump personalizado cifrado, sin dump intermedio en claro. Identidad privada fuera de Git y del destino; verificación de todo el cifrado/archivo, no sólo del índice. [Distribución oficial](https://github.com/FiloSottile/age/releases/tag/v1.3.2).
- **D28:** cryptography 50.0.2/Python 3.11, reutilizando cffi fijado, para la receta mantenida Fernet del diario independiente y autenticación de manifiestos. Lock de archivo entre procesos, reemplazo durable y ancla separada; desacuerdo/corte se resuelve cerrando y conciliando, nunca inventando un diario vacío. [PyPI oficial](https://pypi.org/project/cryptography/50.0.2/), [Fernet](https://cryptography.io/en/latest/fernet/). No se implementa un algoritmo criptográfico propio.
- **D29:** la recuperación local mediante nueva cuenta administrativa con entrada oculta está implementada/probada; D22 se conserva como decisión histórica y ahora se permite restringir otros administradores, protegiendo al último habilitado con lock 90505. Se mantiene 90404 para catálogo y el orden previo de usuarios.
- **D30:** restauraciones destructivas limitadas a `entrenador_prompts_restore_test` y `entrenador_prompts_contingencia_test`, fuente ficticia `entrenador_prompts_ops_test`. CONNECT cerrado hasta diario/sesiones/integridad verificados. Desarrollo sólo recibe migraciones después de copia protegida; nunca se restaura sobre él en estos ensayos.
- **D31:** tarea Windows S4U con ejecutable Python explícito, sin terminal ni cambio de política/zona del sistema. StartBoundary UTC calculado desde las 02:00 Cordoba, validado sin registrar la tarea. Retención 7 días/4 semanas ISO con solapamientos y máximo 30 días, separada por origen. [StartBoundary de Microsoft](https://learn.microsoft.com/en-us/windows/win32/taskschd/trigger-startboundary).
- **D32:** adaptador optativo Backblaze Native v4 usando httpx existente, sin SDK/dependencia adicional ni contratación. Prefijo propio, bucket privado, credencial limitada; purga contempla todas las versiones y cargas inconclusas y vuelve a enumerar. Probado con transporte simulado, sin operación externa acreditada. [Versiones](https://www.backblaze.com/apidocs/b2-list-file-versions), [cargas incompletas](https://www.backblaze.com/apidocs/b2-cancel-large-file).

Estas decisiones son técnicas del proyecto, no atribuciones nuevas a la docente.

## Continuación técnica de etapa 06

- **D33 (etapa 06):** conservar locks/dependencias/motor y limitar cambios de UI a errores, foco, cancelación, referencias accesibles y contraste; AX/DOM/teclado automatizados no equivalen a certificación humana. NF-02 se conserva no aprobado por evidencia positiva de texto ficticio, sin atribuir firma/ruta por el nombre del dominio.
- **D34:** configuración operativa/diario en paquete cifrado separado del dump y de la identidad age privada; extracción en directorio nuevo/vacío, sin sobrescribir activos ni abrir servicio. No sustituye custodia independiente ni diario más reciente. Nueva instalación de roles separada del procedimiento histórico de traslado; esquema/permisos probados en destino ficticio vacío.
- **D35:** demo en entrenador_prompts_demo separada de desarrollo y restauraciones, claves aleatorias privadas sin seeds públicos; medición HTTP de revisar/guardar con cinco usuarios y 100 muestras por endpoint, todas conservadas. Resultado local acotado al entorno, no eficacia educativa ni SLA.

## Puntos que no se resuelven mediante suposiciones

- **Validación externa:** pendiente. Se requiere una persona con experiencia pertinente y evidencia antes de pruebas con usuarios. No se supone dispensa docente ni que una IA equivalga a ese revisor.
- **Notebook:** no consta si es compra necesaria o recurso disponible. Queda pendiente de confirmar en el presupuesto, sin condicionar el desarrollo.
- **Objetivos y resultados:** no se declara mejora educativa hasta contar con resultados reales. Los estados del Sprint 1 no acreditan código existente.
- **Costos posteriores:** deben cotizarse al contratar. El paquete no utiliza las tarifas históricas como precios actuales ni añade una compra/servicio automáticamente.
- **Redacción académica:** las correcciones de formato, APA y ortografía deben aplicarse al DOCX; este paquete no lo reemplaza.
- **Servicio PostgreSQL local:** antes de la primera migración se debe confirmar cuál instancia local escuchará en `127.0.0.1:5432`. Si existen varias instalaciones, no se alteran sus puertos ni datos desde el proyecto; se elige una instancia y se registra la decisión.

## Fuentes técnicas comprobadas

OWASP Foundation, páginas consultadas el 4 de noviembre de 2026:

- [Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html): longitud y política de contraseñas.
- [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html): Argon2id.
- [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html): estado e invalidación de sesión en el servidor.

Son respaldo para decisiones de seguridad. No implican certificación ni reemplazan verificar las versiones concretas de bibliotecas durante la implementación.

- **D36 (solicitud explícita de Santiago, 8/11/2026):** motor 1.1.0 y detector independiente secuencia_numerica_7_8_10_v1: sólo ASCII, longitudes exactas 7/8/10 y límites de dígitos. Prioridad de alertas anteriores con supresión sólo de la genérica cubierta, sin modificar sus patrones/mensajes. Publicar nueva C6 copiando lo vigente y añadiendo el detector; v2 activa comprobada en desarrollo, reglas/historial conservados. Sin cambio de fórmula, semántica de componentes o política de confirmación. No atribuir esta extensión a la profesora ni resolver NF-02 por agregar un patrón.
