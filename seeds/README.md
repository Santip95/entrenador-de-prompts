# Datos iniciales ficticios

Orden de importación: `catalogs.json` → `criteria.json` → `rules.json` → `challenges.json`. `own_goal_profile.json` define la plantilla para objetivos propios; no se importa como un desafío del catálogo. `examples.json` es material de demostración/pruebas, no registros de usuarios.

Los identificadores C1–C6 provienen de la Entrega 3. Los códigos D01–D04, consignas, reglas parametrizadas y ejemplos se prepararon para este paquete; no se presentan como material aprobado por la docente o por un revisor externo.

| Desafío | Uso sugerido | Criterios aplicables |
|---|---|---|
| D01_CORREO_REUNION | Práctica de correo; línea base propuesta | C1–C6 |
| D02_RESUMEN | Resumen con fuente declarada | C1–C6 |
| D03_IDEAS | Lista de ideas | C1, C4, C5, C6 |
| D04_CORREO_INVITACION | Transferencia propuesta | C1–C6; configuración equivalente a D01 |

Reglas JSON: cada `regla` contiene tipo, versión, parámetros y mensajes. `detectores_permitidos` describe implementaciones de código fijadas para esta versión del motor. El panel solo selecciona sus códigos; no permite modificar regex ni ejecutar expresiones proporcionadas por un usuario. Los filtros de cantidad de dígitos se aplican al grupo indicado después de la expresión regular.

Etiquetas de catálogos se tratan como texto plano. No incorporar HTML, secretos, cuentas, entrevistas, DNI reales ni datos de participantes. Las fechas 2030 y los identificadores de prueba son ficticios.

Importación idempotente: resolver entidades por código. Repetir no duplica ni pisa versiones usadas. Para modificar una regla ya importada, publicar versión nueva. `publicado` indica visibilidad funcional del desafío en un entorno técnico; no significa validación externa completada. No habilitar una prueba educativa únicamente por ese estado.

Los ejemplos completos deben mantenerse fuera de la secuencia de línea base/transferencia para evitar que la persona copie la solución. No autocompletar una práctica real con ellos.
