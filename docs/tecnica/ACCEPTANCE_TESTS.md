# Pruebas de aceptación

Estas son especificaciones de pruebas, **no resultados ejecutados**. Automatizar las de motor, API e integridad; verificar manualmente la legibilidad y accesibilidad. Las fixtures amplían el Anexo C y sirven como entradas/resultados esperados.

## Historias de usuario

| ID | Historia | Dado / cuando | Entonces |
|---|---|---|---|
| AT-01 | HU-01 | Usuario activo elige desafío publicado y modo | Se crea una práctica propia con origen/modo correctos, tras preparar/confirmar. |
| AT-02 | HU-01 | Objetivo vacío o formado por espacios | 422, sin práctica; indicar campo. |
| AT-03 | HU-01 | Objetivo propio con C2/C3 no aplicables | Guardar aplicabilidad; no permitir cambiarla dentro de esa práctica ni desactivar C1/C5/C6. |
| AT-04 | HU-02 | Completa campos guiados | Vista previa y texto del servidor contienen componentes/selecciones en orden definido. |
| AT-05 | HU-02 | Modo libre sin confirmación de componentes | No evaluar/guardar; solicitar confirmación. Con confirmación conservar texto libre exactamente normalizado. |
| AT-06 | HU-02 | Componente omitido o solo espacios, otros presentes | Revisar válidamente y señalar el criterio; no ocultar el caso con un error genérico de formulario. |
| AT-07 | HU-03 | Aparece patrón de correo/teléfono/documento | Mostrar tipo/campo y bloquear persistencia hasta editar o confirmar cada coincidencia. Verificar también objetivo previo a crear práctica. |
| AT-08 | HU-03 | Confirma coincidencias, luego cambia texto | Token antiguo rechazado; nueva revisión requerida. No crear versión parcial. |
| AT-09 | HU-03 | Guarda tras confirmar coincidencias actuales | C6 cumple por revisión, avisos conservados; alerta/log/evidencia no contienen el fragmento original. |
| AT-10 | HU-04 | Misma entrada y configuración | Mismos seis estados, evidencias y conteos; sin aleatoriedad ni red externa. |
| AT-11 | HU-04 | C2 o C3 no aplica | Resultado no_aplica y exclusión del denominador; no aparece como incumplimiento. |
| AT-12 | HU-04 | Falta regla activa requerida o configuración inválida | Error de configuración y ninguna escritura; no aumentar porcentaje omitiendo criterio. |
| AT-13 | HU-05 | Hay incumplimiento | Mostrar criterio, condición, evidencia segura y acción; nombres comprensibles. |
| AT-14 | HU-05 | Todos los criterios cumplen | Mostrar proporción y límite; no «prompt perfecto», «calidad 100» ni garantía de seguridad. |
| AT-15 | HU-06 | Edita una versión | Crear V2; V1, componentes, evaluación y fecha permanecen iguales. |
| AT-16 | HU-06 | Dos guardados concurrentes y un reintento con mismo request_id | Números únicos; reintento no duplica; mismo ID con distinto contenido →409. |
| AT-17 | HU-06 | V1 3/6 y V2 6/6, misma firma y sin alertas nuevas | Delta 50 puntos porcentuales; resolución 100 %; mejora estructural true. |
| AT-18 | HU-06 | Reglas/configuración cambian entre versiones | Conservar estados históricos; comparable=false; delta/resolución null y razón visible. |
| AT-19 | HU-07 | Registra correo nuevo y contraseña admitida | Cuenta usuario con hash Argon2id; sin secreto en respuestas/logs; registro genérico. |
| AT-20 | HU-07 | Credenciales incorrectas/correo inexistente | Error genérico coherente; no revelar cuál dato falló. |
| AT-21 | HU-08 | Abre historial con y sin prácticas | Solo sus prácticas, orden/filtros/paginación correctos; estado vacío útil. |
| AT-22 | HU-08 | Progreso con rúbricas distintas o sin observaciones iniciales | Separar configuraciones; no promediar rúbricas distintas; resolución null si denominador cero. |
| AT-23 | HU-09 | Admin publica regla nueva | Versión nueva; anterior conservada; futuras evaluaciones toman nueva; antiguas iguales. |
| AT-24 | HU-09 | Intenta borrar regla/desafío usado | Rechazar borrado destructivo; permitir desactivar y conservar historial. |
| AT-25 | HU-09 | Dos administradores editan/publican simultáneamente | Control de revisión y transacción impiden estado parcial/dos reglas activas por criterio. |

## Seguridad e integridad

| ID | Escenario | Resultado esperado |
|---|---|---|
| SEC-01 | Cuenta inicia sesión en dos navegadores; admin la bloquea | Ambas sesiones fallan en la siguiente solicitud; desbloquear no las reactiva. |
| SEC-02 | Escritura concurrente con desactivación | Se serializa antes de desactivar o se rechaza; ninguna escritura confirma después basándose en autorización vieja. |
| SEC-03 | Contraseña de 14, 15, 128 y 129 caracteres | Rechazar 14/129; admitir 15/128 si no comunes. No truncar; admitir frase con espacios/Unicode. |
| SEC-04 | Cinco fallos en 15 min; sesión activa previa | Bloquear 15 min y revocar sesión. Probar límite por IP y cuenta. |
| SEC-05 | Cookie vencida por 30 min inactividad, 8 h absolutas o logout | 401 y cookie eliminada. Alterar reloj del cliente no prolonga sesión. |
| SEC-06 | Restablecimiento válido, vencido, reutilizado y dos consumos concurrentes | Solo un consumo válido; revocación global; token no visible en API/log; no reactivar bloqueado. |
| SEC-07 | Usuario A pide versión/comparación/borrado de B; admin pide prompt de B | 404 sin filtración ni cambios. Usuario común en admin →403. |
| SEC-08 | POST autenticado sin CSRF/origen no admitido; prompt con HTML/script/SQL | Rechazo de CSRF; texto tratado como datos; no ejecución ni consultas interpoladas. |
| SEC-09 | Rotación de contraseña, rol o restauración de backup | Tokens anteriores inválidos; ningún privilegio antiguo sobrevive. |
| SEC-10 | Falla después de insertar versión antes de evaluación/resultados | Rollback completo; ninguna versión huérfana. |
| SEC-11 | Elimina práctica/cuenta y luego restaura copia anterior | Cascada en activo; diario de borrados reaplicado antes de acceso; no reaparecen datos. |
| SEC-12 | Hay alerta en criterio no aplicable o en texto libre | Detectarla igual; no saltar seguridad por aplicabilidad. |
| SEC-13 | Otro usuario reutiliza token de revisión o se altera contenido/configuración | 401/404/409 según causa; nunca persistir ni revelar contenido ajeno. |
| SEC-14 | Cambia regla mientras se guarda una versión | Transacción usa un conjunto consistente; si difiere del token, 409 sin guardar. |
| SEC-15 | Se confirma un correo y otro distinto en V2 | Huellas detectan alerta nueva aunque tipo/campo/cantidad coincidan; no declarar mejora. |
| SEC-16 | Se rota la clave de huellas entre V1/V2 | Comparación de alertas indeterminada, no inferir ausencia de alertas nuevas. |
| SEC-17 | Revisión/registro con cuerpo inválido que contiene un correo | Respuestas de error y logs no reflejan valor completo ni request body. |

## Calidad y operación

| ID | Verificación | Criterio |
|---|---|---|
| NF-01 | Teclado, lector de etiquetas y móvil | Flujo usable a 360 px y escritorio; foco visible, sin acciones solo por color, errores vinculados a campos. |
| NF-02 | Inspección de red y código | Ninguna llamada a IA o telemetría que envíe prompts. DB/SMTP/backup solo con finalidad configurada. |
| NF-03 | 100 evaluaciones, 5 concurrentes, después de calentamiento | p95 <2 s bajo entorno documentado, o registrar incumplimiento real y plan de corrección. |
| NF-04 | Pruebas de motor/integración/flujo | Automatizar positivos, negativos, no aplica, alertas, configuración y permisos; conservar reporte real. |
| OPS-01 | Restauración en base limpia | Integridad, borrados reaplicados, sesiones invalidadas y flujos comprobados; registrar RPO/RTO reales. |
| OPS-02 | Contingencia R6 en host alternativo/local | Arranca desde código y backup, sin dependencia de Render en el dominio; registrar límites. |
| OPS-03 | Purga de respaldos y versiones antiguas | Ningún objeto recuperable con datos supera retención de 30 días, salvo incidente expresamente gestionado y comunicado. |
| VAL-01 | Preparación de prueba educativa | Hay revisión externa documentada y correcciones resueltas; si no, sigue pendiente. |
| VAL-02 | Selección de participantes | Misma definición de principiante de §6.2; no equiparar uso frecuente a formación avanzada. |

## Evidencia de ejecución

Registrar fecha, commit, entorno, ID de prueba, entrada/fixture, resultado esperado, obtenido y estado. No marcar «aprobado» por inspección de una maqueta. En fallos incluir reproducción con datos ficticios. No guardar secretos o prompts reales en capturas públicas.

## Incremento D36 — detector numérico

Además del corpus histórico intacto: positivos exactos 7/8/10 con ceros; negativos 6/9/11, año 2026 y formatos fragmentados; sin subcoincidencias de tramos mayores ni genérica duplicada sobre alertas antiguas. Probar prioridad independiente del orden, objetivo/no aplica/libre, falta de confirmación sin persistencia, publicación versionada e historia inmutable/no comparabilidad entre configuraciones. Pruebas y pantalla en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md; no aprueba NF-02.
