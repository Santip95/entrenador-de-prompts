# Diagramas e interfaces

## Referencias de la tercera entrega

Las seis imágenes de `originales/` se extrajeron sin modificaciones del DOCX presentado. Conservan su numeración académica. No se incluye portada ni datos personales del autor. Se conserva la resolución y transparencia originales; visualizar sobre fondo blanco.

| Figura | Archivo | Uso |
|---|---|---|
| 3 | [DER original](originales/figura_03_der.png) | Modelo conceptual presentado. |
| 4 | [Inicio](originales/figura_04_inicio.png) | Elección de desafío/objetivo y modalidad. |
| 5 | [Constructor](originales/figura_05_constructor.png) | Campos y vista previa. |
| 6 | [Resultados](originales/figura_06_resultados.png) | Estados, evidencia y límite de interpretación. |
| 7 | [Comparación](originales/figura_07_comparacion.png) | Dos versiones y cambios por criterio. |
| 8 | [Arquitectura original](originales/figura_08_arquitectura.png) | React, FastAPI, dominio y PostgreSQL. |

## Modelos para implementar

- [der_tecnico.mmd](der_tecnico.mmd): dominio, claves e instantáneas. Las cardinalidades expresan relaciones; restricciones adicionales y borrado están en DATABASE.
- [der_acceso.mmd](der_acceso.mmd): sesiones, recuperación y auditoría incorporadas para concretar seguridad.
- [arquitectura.mmd](arquitectura.mmd): arquitectura lógica con recuperación y respaldos.
- [prototipos.md](prototipos.md): pantallas y estados que completan las figuras sin cambiar el alcance.

Abrir los `.mmd` con un visor Mermaid o copiar su contenido en una herramienta compatible. Son fuentes editables nuevas, no los archivos draw.io originales, que no estaban incluidos dentro del DOCX. No afirmar que se recuperaron los editables originales.

En el DER técnico `regla_id` de resultado es nulo únicamente para «no aplica». La relación versión–evaluación es 1:1 en esta implementación. El diario de borrados es un registro cifrado independiente, no una tabla dentro de la copia que se restaura. La arquitectura no incluye API de IA.

Las figuras son bocetos, no contratos exhaustivos. Si una etiqueta antigua sugiere guardar antes de revisar seguridad, seguir el flujo corregido de SPEC/API. La versión ampliada de DATABASE es la autoridad para las migraciones.
