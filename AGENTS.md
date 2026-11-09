# Instrucciones para implementar este proyecto

## Propósito y precedencia

Implementar el entrenador descrito en `docs/tecnica/SPEC.md`. Leer antes de editar: `docs/tecnica/DECISIONS.md`, `docs/tecnica/DATABASE.md`, `docs/tecnica/EVALUATION_RULES.md`, `docs/tecnica/ACCEPTANCE_TESTS.md`, `docs/tecnica/SECURITY.md` y `docs/tecnica/API_CONTRACT.md`. Consultar `docs/tecnica/TRACEABILITY.md` para el origen académico y docente de cada decisión.

Las instrucciones explícitas de Santiago prevalecen. En este paquete, las correcciones docentes identificadas prevalecen sobre las formulaciones anteriores que corrigen. Los contratos técnicos son la base de implementación; las figuras originales son referencia visual. Ante contradicción sustantiva, registrarla y resolverla con el usuario; continuar las tareas independientes. No atribuir decisiones técnicas nuevas a la profesora.

## Tecnología

- React para interfaz; FastAPI y Python para API/motor; PostgreSQL para persistencia. No sustituir por SQLite, Firebase, Supabase ni un BaaS como simplificación.
- SQLAlchemy y Alembic para acceso/migraciones, Pydantic para contratos y Vite para desarrollo de React son decisiones técnicas de este paquete, no requisitos textuales de la entrega. El desarrollo local se hace en Windows con PowerShell, Node.js/npm, Python en `.venv`, PostgreSQL instalado y Mailpit; no requiere WSL, Ubuntu ni Docker. Los contenedores pueden evaluarse únicamente para un despliegue futuro, sin convertirlos en dependencia local.
- Usar `npm.cmd` desde PowerShell si la política local impide ejecutar `npm.ps1`; no reducir ni cambiar la política de ejecución como atajo. Si los binarios de PostgreSQL no están en `PATH`, invocarlos por su ruta de instalación o agregar esa carpeta al `PATH` de la sesión, sin registrar credenciales.
- Preferir TypeScript en el frontend nuevo. Si existe una base React en JavaScript, conservarla si cumple el contrato y evita una reescritura innecesaria. Registrar la decisión.
- Elegir versiones estables compatibles al iniciar, consultar documentación oficial y fijarlas en archivos de dependencias y lockfiles. No inventar versiones ni utilizar etiquetas `latest` para imágenes reproducibles.
- Separar dominio, aplicación, API y persistencia. El motor debe poder probarse sin navegador ni base de datos.

## Reglas que no deben alterarse

1. No agregar APIs generativas, embeddings, agentes que evalúen texto, generación automática de prompts, análisis semántico, notas de calidad, pagos, certificados ni funciones sociales.
2. Mantener ambos recorridos: guiado y libre con confirmación de componentes. El modo libre no infiere componentes.
3. Conservar C1–C6, aplicabilidad y estados. No agregar ponderaciones. No llamar «calidad», «eficacia» o «seguro» al porcentaje.
4. Inmutabilidad de versiones y evaluaciones. Una edición crea otra versión. La eliminación solicitada por su propietario es una excepción explícita que elimina la práctica y sus dependencias.
5. Nunca recalcular historial con reglas actuales sin identificar una evaluación nueva. Mantener reglas y configuraciones aplicadas.
6. No guardar borradores con alertas antes de su revisión. Confirmar una alerta no elimina su registro ni demuestra que el dato sea seguro.
7. Autorizar cada operación en el servidor. El administrador no puede leer prompts ajenos por tener ese rol.
8. Revocar sesiones en el servidor al bloquear/desactivar la cuenta y al cambiar/restablecer contraseña. No usar solo un JWT sin consulta de estado.
9. No guardar secretos en Git, respuestas de API, logs, seeds ni variables `VITE_*`. No usar contraseñas de demostración públicas en producción.
10. Separar pruebas técnicas con datos ficticios de validación externa y pruebas educativas con personas. No inventar participantes, dictámenes, capturas ni resultados.

## Forma de trabajo

Inspeccionar primero el repositorio y sus instrucciones. No borrar trabajo previo, no sobrescribir documentación académica y no declarar código terminado por el estado de una tabla. Aplicar cambios acotados por etapa. Ejecutar pruebas relacionadas con cada cambio y registrar comandos, resultado y limitaciones. Si el directorio ya pertenece a un repositorio Git, dejar un commit local por incremento comprobado; no publicar ni desplegar sin una instrucción que lo autorice.

Usar los JSON de `seeds/` como especificación de precarga idempotente y los de `fixtures/` como entradas/resultados esperados. No convertir ejemplos en respuestas modelo obligatorias. Configurar reglas mediante tipos permitidos; prohibido ejecutar código o expresiones arbitrarias introducidas por administradores.

La interfaz debe hablar en español claro, ser utilizable con teclado y permitir leer los estados sin depender del color. Mostrar errores junto al campo y conservar el borrador en memoria al fallar una solicitud. No persistir prompts en localStorage ni en telemetría externa.

## Criterio de terminado

Cada historia requiere flujo real conectado con PostgreSQL, autorización, validación de entrada, errores comprensibles y pruebas pertinentes. Una maqueta no completa una historia. La entrega técnica requiere inicio reproducible, migraciones, seeds, pruebas, documentación de configuración y ensayo real de respaldo/restauración. Reportar por separado lo implementado, lo probado, lo no ejecutado y la validación pendiente.
