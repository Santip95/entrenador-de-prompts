# Especificación funcional

**Ampliación autorizada D36, 8/11/2026:** motor 1.1.0 añade secuencia_numerica_7_8_10_v1 para tramos ASCII exactos 7/8/10, con prioridad de alertas existentes. Nueva C6 v2 activa en desarrollo, historial sin recalcular, misma confirmación/privacidad/fórmula y sin cambiar regex anteriores. No asegura DNI/teléfono ni cobertura completa; NF-02 continúa pendiente. Contrato en docs/tecnica/EVALUATION_RULES.md y evidencia en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md. No cambia el documento académico.

## Producto y público

Entrenador web para la construcción guiada y revisión estructural de prompts textuales en español. Permite observar componentes declarados y cambios de cumplimiento entre versiones, sin anticipar resultados de una IA.

Usuario principiante: persona de 18 años o más, sin formación formal/especializada en prompting y sin un método explícito y repetible para construir y revisar solicitudes. La frecuencia de uso no excluye a una persona. Este criterio procede de §6.2 y debe mantenerse al seleccionar participantes de validación; no requiere registrar DNI, fecha de nacimiento ni historial educativo en la cuenta.

## Actores y permisos

| Actor | Acciones |
|---|---|
| Visitante | Portada, ayuda de alcance, registro, ingreso y recuperación. |
| Usuario registrado activo | Crear, consultar y eliminar sus prácticas; redactar, revisar, guardar, comparar y consultar su progreso; gestionar su cuenta. |
| Administrador funcional activo | Gestionar catálogo, criterios, versiones de reglas y bloqueo/desactivación de cuentas; no leer prácticas de terceros. |
| Responsable técnico | Operar despliegue, secretos, respaldos y restauración fuera del panel funcional. |

Registro público siempre crea rol `usuario`. El primer administrador se crea por un comando local explícito, con contraseña introducida en forma segura. No existe un endpoint público para elegir el rol.

## Funciones y exclusiones

Se implementan RF-01 a RF-08 y HU-01 a HU-09. Incluyen catálogo compartido, objetivo propio, ambos modos de redacción, revisión de datos sensibles, reglas versionadas, resultados explicables, historial y administración básica. Los requisitos de acceso, recuperación y borrado de §13 también forman parte del alcance.

No se implementan cursos por módulos, chat con IA, ejecución del prompt, evaluación de respuestas, veracidad, calidad semántica, tono real, generación automática de correcciones, imágenes/audio/video, redes sociales, certificados ni pagos. Las microayudas explican cómo completar un campo; no son un curso ni una respuesta generativa.

## Flujo principal

1. Iniciar sesión. Elegir desafío publicado u objetivo propio y modalidad `guiado` o `libre`. Revisar el objetivo y confirmar sus posibles coincidencias antes de crear/persistir la práctica.
2. En objetivo propio, describir el objetivo y elegir aplicabilidad de C2/C3/C4. C1, C5 y C6 siempre aplican. En desafíos, la configuración proviene del catálogo y el usuario no puede desactivar condiciones.
3. Redactar. En guiado, el servidor ensambla la versión final a partir de los componentes. En libre, conservar el texto escrito y completar/confirmar los componentes antes de revisar. No inferirlos automáticamente.
4. Solicitar revisión. Se ejecutan el detector preventivo y las reglas en memoria. No se guarda el prompt todavía. Se muestran coincidencias por tipo y campo, condición, evidencia redactada y acción.
5. Si hay alertas, editar o confirmar expresamente cada coincidencia actual. Cualquier cambio invalida la revisión anterior. La confirmación queda ligada a ese contenido, usuario, práctica y configuración.
6. Guardar y evaluar en una transacción: versión inmutable, evaluación, seis resultados y alertas confirmadas. Los criterios incompletos se pueden guardar y deben conservar el estado `revisar`; ese es el punto de partida para mejorar.
7. Crear V2 a partir de V1, sin cambiar V1. Comparar texto, componentes, estados, alertas e indicadores. Copiar el prompt al portapapeles solo por acción del usuario.

Un borrador vacío por completo no se puede guardar. Un borrador con tarea vacía y otros componentes presentes sí puede evaluarse, para obtener C1 `revisar`. Una evaluación preliminar no crea progreso persistente.

## Prácticas y versiones

Una práctica pertenece a un usuario. Su origen es un desafío o un objetivo propio, nunca ambos. El modo y la configuración de objetivo propio se fijan al crearla; cambiar el objetivo o la aplicabilidad requiere otra práctica, para no presentar una modificación de la rúbrica como mejora.

El desafío original puede actualizarse después: una versión nueva toma la configuración vigente y conserva una instantánea. La interfaz informa el cambio y compara los estados; no calcula mejora si las configuraciones de evaluación no son comparables. Un desafío desactivado conserva su historial y permite lectura/copia; no admite nuevas versiones hasta reactivarse. No debe sustituirse silenciosamente por un objetivo propio.

Las versiones se numeran 1, 2, 3... por práctica, desde el servidor. Una versión guardada se lee y se usa como base, pero no se edita ni se borra de forma individual. Se puede eliminar toda la práctica, con sus versiones y resultados, mediante una acción de su propietario.

## Componentes y límites de entrada

El contrato JSON está en `docs/tecnica/EVALUATION_RULES.md` y se ejemplifica en `seeds/examples.json`.

| Entrada | Límite de implementación |
|---|---|
| Objetivo propio | 1–1000 caracteres después de quitar espacios exteriores para validar. |
| Cada texto de componente y cada valor de contexto | 0–2000 caracteres. |
| Texto libre o texto ensamblado | Hasta 10000 caracteres. |
| Campos de contexto | Hasta 10 claves, definidas por la configuración. |
| Restricciones seleccionadas | Hasta 10 identificadores conocidos. |
| JSON de componentes | Hasta 20000 caracteres en su representación normalizada. |
| Solicitud HTTP de escritura | Hasta 64 KiB. |

Estos límites controlan volumen; no miden calidad. No imponer mínimos de palabras ni verbos detectados por palabra clave. Normalizar Unicode a NFC y saltos de línea a LF; conservar el contenido para mostrarlo. Usar `strip()` solo al comprobar vacío. No recortar silenciosamente.

## Administración

Catálogo: crear borrador, editar borrador, publicar o desactivar desafíos. En un borrador, editar no publica. Editar un desafío publicado valida y publica atómicamente la nueva revisión. Cada publicación incrementa `revision` y valida seis entradas de criterios, reglas activas, identificadores y operadores conocidos. Guardar el historial de cambios como auditoría de metadatos; cada evaluación conserva su instantánea completa.

Criterios: mantener códigos C1–C6 y su significado. El panel puede ajustar nombres y explicaciones, nunca agregar/eliminar dimensiones en esta versión del producto. Los cambios se reflejan solo en nuevas evaluaciones y quedan en sus instantáneas.

Reglas: crear una versión nueva por criterio, validar parámetros, publicar de modo atómico y desactivar la anterior para ejecuciones nuevas. Una regla ya usada no se elimina ni se modifica. Una regla desactivada no hace desaparecer su criterio: si falta una regla activa requerida, se impide evaluar y se informa un error de configuración.

## Interfaz y calidad

Pantallas: acceso y recuperación; inicio; constructor; revisión de seguridad; resultados; comparación; historial; perfil; administración. Diseño responsivo, etiquetas visibles, navegación por teclado, foco en errores y estados de carga/vacío/fallo. No usar solo verde/rojo ni datos ficticios en un historial real.

RNF-03 se concreta como tiempo total de evaluación menor a 2 segundos en el percentil 95 de 100 solicitudes válidas tras calentamiento, con 5 usuarios concurrentes, texto de hasta 10000 caracteres y entorno documentado. Excluir arranque en frío y adquisición de una sesión, pero incluir API/motor/guardado cuando se mida ese endpoint. Es un objetivo por comprobar, no un resultado.

No enviar prompts a servicios externos de IA ni a analítica. El servidor de la app y la base son destinos necesarios; los respaldos cifrados van a B2 conforme a §13. Esta distinción evita interpretar RNF-02 como una prohibición de alojar el sistema.
