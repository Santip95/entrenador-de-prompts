# Validación y evidencias del TFG

La devolución docente pide completar la revisión externa de reglas antes de probar con usuarios. Este paquete prepara las condiciones, pero no acredita que esa revisión exista. Desarrollar y probar técnicamente con datos ficticios puede avanzar mientras se gestiona la revisión.

## Orden y evidencia

1. Revisión interna documental: coherencia de criterios, mensajes, aplicabilidad y casos esperados. Registrar observaciones y ajustes.
2. Implementación y pruebas técnicas: ejecutar fixtures y aceptación sobre código real. Conservar versión de reglas, commit y resultados, separados de las expectativas.
3. Revisión externa: al menos una persona con experiencia en alfabetización digital, diseño instruccional o uso profesional de IA revisa observabilidad, límites, mensajes, casos y falsas alarmas. Usar el instrumento del Anexo E de F1; registrar perfil, fecha, versión, dictamen y cambios.
4. Corregir objeciones, ampliar pruebas y solicitar nueva revisión cuando el dictamen lo requiera. Una planilla vacía no es evidencia.
5. Pruebas con personas adultas que cumplan la definición de principiante de SPEC. Consentimiento, códigos en lugar de nombres y situaciones ficticias. No incluir profesionales de IA/capacitación avanzada como usuarios principiantes por conveniencia.

Si no se consigue revisor, registrar la dependencia y consultar a la docente un cambio de plazo/modalidad. No presentar revisión por IA como externa, ni asumir que el silencio habilita pruebas. El estado permanece pendiente y la demo técnica puede mostrar datos ficticios.

## Secuencia por participante

Usar una tarea de línea base, una revisión y un desafío de transferencia. Los correos D01 y D04 del catálogo son una propuesta de configuración comparable, cuya adecuación debe revisar la persona externa.

- Línea base: primer prompt guardado del primer desafío, sin mostrar antes sus ejemplos completos ni copiar una versión preparada.
- Revisión: permitir leer devoluciones y crear V2. Registrar qué criterios cambiaron y las alertas nuevas.
- Transferencia: primer intento en el otro desafío, sin acceso a una solución del catálogo ni copiar la versión anterior. No interpretar que dos configuraciones equivalentes aseguren igual dificultad educativa.
- Comprensión: pedir que explique dos devoluciones con sus palabras y qué cambiaría. Un observador califica correspondencia con criterio/acción; el motor no evalúa semánticamente esas respuestas.

Registro mínimo: código participante, cumplimiento de inclusión, consentimiento, fecha, desafíos/versiones/reglas, V1/V2/transferencia, conteos, alertas, tiempos, ayuda necesaria, explicaciones y observaciones. No fijar una cantidad de participantes que no se haya acordado ni inventar datos faltantes.

Los indicadores usan las fórmulas de EVALUATION_RULES. Comparar solo firmas equivalentes y mantener valores null cuando no corresponde calcular. Presentar número de casos efectivos y limitaciones; no generalizar una muestra pequeña a toda la población.

## Decisiones ante resultados

| Resultado observado | Acción |
|---|---|
| Revisor rechaza una regla o detecta una inferencia semántica injustificada | Retirar esa versión de nuevas evaluaciones, corregir condición/mensaje, ampliar casos y revisar nuevamente antes de usuarios. Conservar historial de la versión rechazada. |
| Regla genera falsos positivos o negativos | Registrar casos, ajustar patrón/aplicabilidad y publicar versión nueva; comprobar regresión; mantener visible el límite de detección. |
| Usuarios no comprenden la devolución | Identificar campo/palabra confusa, reformular mensaje y microayuda, repetir tarea con registro de qué cambió. No asumir que más texto resuelve el problema. |
| No mejora V2 | Revisar si el criterio mide algo observable, si la tarea se entiende y si la ayuda permite actuar; registrar resultado sin modificar retrospectivamente línea base/umbrales. |
| Mejora V2, pero no transferencia | Reducir conclusiones al desempeño asistido; revisar dependencia de ayudas y equivalencia de desafíos; realizar otra prueba si el plazo lo permite. |
| Aparece un riesgo de exposición | Detener uso de datos reales, aplicar R5 y corregir el flujo antes de continuar. |

No se inventan umbrales de éxito grupal. Si se acuerdan umbrales en una revisión posterior, registrarlos antes de recoger datos y mantener el registro original.

## Cumplimiento por objetivo específico

| Objetivo de F1 §8.2 | Evidencia disponible en F1 | Qué falta para acreditarlo funcionalmente |
|---|---|---|
| Caracterizar dificultades y preferencias | Once entrevistas y matriz declaradas en el documento. | Este paquete no revalida sus registros; conservar instrumentos originales. |
| Definir criterios y límites | Tabla 12, Anexos C/E y especificación técnica presente. | Revisión externa y correcciones con evidencia. |
| Ofrecer dos recorridos | Prototipos y contrato guiado/libre. | Implementación y pruebas AT-04/05. |
| Proporcionar devolución explicable | Diseño de estados/evidencia/acciones. | AT-13/14 y prueba de comprensión. |
| Registrar versiones y observar cambio/transferencia | DER, indicadores y contrato. | Persistencia/comparación comprobadas y datos de transferencia reales. |
| Verificar motor y comprensión | Matriz de casos y plan de validación. | Pruebas ejecutadas y observación de usuarios después de revisión externa. |

La documentación acredita diseño. No convertir esas filas en objetivos cumplidos por el mero hecho de que existan especificaciones.
