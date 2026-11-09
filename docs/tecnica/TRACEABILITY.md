# Fuentes y trazabilidad

**Ampliación autorizada D36, 8/11/2026:** motor 1.1.0 añade secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, con prioridad de alertas existentes. Nueva C6 v2 activa en desarrollo, historial sin recalcular, misma confirmación/privacidad/fórmula y sin cambiar regex anteriores. No asegura DNI/teléfono ni cobertura completa; NF-02 continúa pendiente. Contrato en docs/tecnica/EVALUATION_RULES.md y evidencia en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. No cambia el documento académico.

Continuación técnica de etapa 06: matriz de 89 casos en docs/evidencias/INFORME_FINAL_ETAPA06.md, 317 pruebas reales y mediciones HTTP/ensayos locales en docs/evidencias/EVIDENCIA_ETAPA06.md. NF-02 no aprobado impide cierre integral; NF-01 básico confirmado manualmente por Santiago el 8/11, conservando incidencia y repetición de Narrador en Edge; B2/custodia externa/periodicidad y validación educativa pendientes. La revisión general manual de Santiago y su instalación de tarea se distinguen de automatización. No se cambian fuentes, documento académico ni conclusiones educativas.

## Documentos de base

| ID | Fuente leída | Localización usada |
|---|---|---|
| F1 | Entrega 3 TFG Pispieiro Santiago(2).docx | Versión presentada, fecha de portada 19/10/2026. §§4–13, 15–16; Tablas 6, 7, 9, 12–18, 24–26; Figuras 3–8; Anexos C–E. |
| F2 | Devolucion Entrega 3.txt | Mensaje de Carolina con correcciones de validación, seguridad, costos, riesgos, conclusiones y presentación. |
| F3 | RUBRICA PROTOTIPADO TECNOLÓGICO (2).xlsx | Hoja «Rúbrica Módulo 3», observaciones J15:J26. |

No se tomó la Entrega 4 documental como fuente ni se copiaron especificaciones del paquete anterior. Se trabaja sobre F1, incorporando F2/F3. Las referencias por sección/tabla evitan confundir la paginación del DOCX entre visores.

## Necesidades e implementación

| Requisito | Historia | Fuente | Contrato | Verificación |
|---|---|---|---|---|
| RF-01 Inicio | HU-01 | F1 §11.2 | SPEC / API | AT-01 a AT-03 |
| RF-02 Constructor | HU-02 | F1 §§4, 11.2 | SPEC / reglas | AT-04 a AT-06 |
| RF-03 Versiones | HU-06 | F1 Tablas 6 y 13 | DATABASE | AT-15 a AT-17 |
| RF-04 Reglas | HU-04/HU-09 | F1 §§11.4–11.6 | Reglas / DATABASE | AT-10 a AT-12, AT-23 a AT-25 |
| RF-05 Devolución | HU-05 | F1 §11.2 | Reglas / prototipos | AT-13/14 |
| RF-06 Alertas | HU-03 | F1 §§6.5, 11.2 | SECURITY / API | AT-07 a AT-09 |
| RF-07 Comparación | HU-06 | F1 §8.4 | Reglas / API | AT-17/18 |
| RF-08 Historial | HU-08 | F1 Tabla 7 | SPEC / API | AT-21/22 |
| Cuentas y sesión | HU-07 | F1 §13, F2/F3 | SECURITY / DATABASE | AT-19/20, SEC-01 a SEC-09 |
| Administración | HU-09 | F1 §11.2 | SPEC / API | AT-23 a AT-25 |
| RNF-01 a RNF-04 | Transversal | F1 Tabla 6 | SPEC / AGENTS | NF-01 a NF-04 |

## Correcciones de la profesora

| Observación | Tratamiento en este paquete | Estado externo al paquete |
|---|---|---|
| Revisión externa antes de usuarios; mismo principiante | VALIDATION_PLAN, VAL-01/02, prompts por etapas | Pendiente conseguir revisión y registrar resultados reales. |
| Revocar sesiones activas al bloquear/desactivar | SECURITY, tablas `sesion`/`usuario`, SEC-01/02 | Implementado y probado técnicamente en etapa 03 con PostgreSQL y sesiones HTTP independientes; dos navegadores/panel pendientes. Ver docs/evidencias/EVIDENCIA_ETAPA03.md; no equivale a validación externa. |
| Continuación técnica de esa corrección | EVIDENCIA_ETAPA04, SEC-01/02 e INT-02 | Comprobada revocación en Chrome y Edge reales con perfiles independientes y en carrera con guardado de versión. Panel y validación externa siguen pendientes; no es revisión manual de Santiago. |
| Revisar contraseña mínima | Política 15–128 en SECURITY y `.env.example`, SEC-03 | Decisión técnica D08; actualizar también §13 del DOCX. |
| Aclarar notebook | OPERATIONS separa valoración y desembolso | Requiere dato del autor; no se inventa compra. |
| Separar cuatro meses y operación posterior | Plantilla de rubros en OPERATIONS | Cotizar importes vigentes y actualizar presupuesto académico. |
| Contingencia R5 por pérdida/exposición | Procedimiento de aislamiento, rotación, recuperación y verificación | Pendiente ensayo y evidencia. |
| Contingencia R6 por proveedor/costo | Contenedores, restauración portable y alternativa local | Pendiente ensayo; no equivale a despliegue público. |
| Cumplimiento por objetivo específico | Matriz de evidencias en VALIDATION_PLAN | Estados de implementación y validación pendientes. |
| Reglas rechazadas, mensajes incomprendidos o falta de mejora | Decisiones operativas en VALIDATION_PLAN | Aplicar según resultados, sin inventarlos. |
| Página en blanco, capítulos, APA, ortografía y terminología | Checklist al final de este archivo | No modifica el DOCX. |

## Inconsistencias de F1 que no se deben heredar

La Tabla 10 marca tareas técnicas como «Hecho», mientras §§12.1/12.4 y 16 dicen que el prototipo aún no se implementó. Verificar el repositorio real antes de reconocer avance. F1 §6.4 ubica validación antes de programación, pero el Sprint 4 contempla revisión externa posterior. Para organizar el trabajo se adopta revisión documental interna → implementación/pruebas técnicas → revisión externa y ajustes → usuarios; coincide con el requisito temporal explícito de F2. Registrar esta organización al actualizar el informe.

La retención de tres copias mensuales no es compatible con el plazo máximo de 30 días de eliminación de respaldos. D10 resuelve la contradicción. Los modelos de seguridad ampliados se identifican como técnicos, sin afirmar que estaban en el DER original.

Continuación técnica de etapa 05: HU-09/AT-23/24/25 implementados y probados por panel/API; INT-02 repetido desde panel con Chrome/Edge reales. SEC-09/11, INT-05 y OPS-01/02/03 tienen ensayo local de borrado durable/restauración/contingencia. B2, programación diaria efectiva y custodia offline pendientes. docs/evidencias/EVIDENCIA_ETAPA05.md distingue automatización y confirmación manual. No es validación docente ni educativa.

## Checklist de la próxima versión académica

- Eliminar la página en blanco entre perfiles y política de acceso.
- Uniformar nombres, numeración y espaciado de capítulos.
- Revisar correspondencia cita–referencia y formato APA.
- Corregir ortografía, concordancia e interrogativos; revisar el Abstract, incluida «challenge-specific requirements».
- Distinguir diseño, implementación, prueba técnica y validación; actualizar estados con evidencia.
- Aclarar la notebook, separar costos posteriores y actualizar las políticas elegidas.
- Mantener pendientes explícitos y agregar únicamente resultados comprobados.
