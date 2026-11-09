# Contrato del motor determinístico

Implementación pura de referencia (etapa 02): `backend/app/domain/evaluation.py`, versión histórica `1.0.0`; ampliación autorizada actual `1.1.0` (D36). Recibe configuración, catálogos y contexto como datos; no los carga desde archivos ni DB. El adaptador del corpus y sus claves ficticias están separados en `app/application/fixture_evaluation.py`. La evidencia ejecutada, comandos y límites de esta implementación se registran en `docs/evidencias/EVIDENCIA_ETAPA02.md`; esto no acredita integración HTTP ni validación externa.

Base: F1 §5.4, Tabla 7, §11.4/Tabla 12 y Anexo C. Las concreciones D01–D06 y D09 se documentan en `docs/tecnica/DECISIONS.md`. El motor observa campos y confirmaciones; no comprende semánticamente los prompts.

## Entrada canónica

```json
{
  "modo": "guiado",
  "texto_libre": "",
  "componentes_confirmados": false,
  "componentes": {
    "tarea": {"texto": "Redactá una solicitud de reunión.", "accion_id": "redactar"},
    "contexto": {"texto": "Situación ficticia", "campos": {"finalidad": "Coordinar una actividad", "fecha": "2030-05-10"}},
    "destinatario": {"texto": "Coordinación de una organización ficticia"},
    "restricciones": {"texto": "", "selecciones": ["sin_identificadores"]},
    "formato": {"tipo": "correo", "detalle": "Incluir asunto y cierre"}
  }
}
```

Los campos son obligatorios en el esquema; sus textos pueden estar vacíos para que el motor informe faltantes. `accion_id` admite `null` para «sin seleccionar» y `formato.tipo` admite `null`. Las selecciones son IDs del catálogo, sin duplicados. Valores desconocidos o tipos inválidos producen 422, no `revisar`. En modo libre, `componentes_confirmados=true` es requisito de revisión; el texto libre permanece intacto. En guiado se ignora ese booleano y se prohíbe un `texto_libre` no vacío para evitar dos textos fuente contradictorios.

El objetivo propio pertenece a la práctica y también se revisa por seguridad. No se incluye automáticamente en el prompt si no fue declarado como componente. Si se quiere corregir un objetivo con alerta, se debe cancelar esa práctica sin versiones y comenzar otra: no sobrescribir objetivos de prácticas evaluadas.

## Configuración de un desafío

La configuración contiene seis entradas C1–C6. Cada una tiene `aplica`, `obligatorio` y `parametros`. En este paquete `obligatorio` coincide con `aplica`; no se usan criterios opcionales puntuables. Una condición obligatoria incumplida produce `revisar` y **no bloquea guardar**. C1/C5/C6 siempre aplican. C2/C3/C4 pueden ser `no_aplica` en un desafío o, para objetivo propio, según la elección inicial registrada.

`desafio_criterio.configuracion` almacena `aplica` y los parámetros. El booleano `obligatorio` se conserva en su columna. No aceptar contradicciones entre ellos. La desactivación administrativa de una regla no convierte un criterio en no aplicable.

## Reglas C1–C6

| Código | Comprobación exacta cuando aplica | Estado satisfactorio | Estado pendiente |
|---|---|---|---|
| C1 Tarea | `tarea.texto.strip()` no vacío Y `accion_id` incluido en `acciones_permitidas`. | `cumple` | `revisar` |
| C2 Contexto | Todos los `campos_requeridos` tienen texto no vacío. Si `exigir_texto=true`, también `contexto.texto` no vacío. | `cumple` | `revisar` |
| C3 Destinatario | `destinatario.texto.strip()` no vacío. | `cumple` | `revisar` |
| C4 Restricciones | Todas las `selecciones_requeridas` están seleccionadas Y, si `exigir_texto=true`, el campo texto no está vacío. | `cumple` | `revisar` |
| C5 Formato | `tipo` incluido en `tipos_permitidos` Y, si `exigir_detalle=true`, detalle no vacío. | `cumple` | `revisar` |
| C6 Seguridad | Sin coincidencias de detectores activos O todas las coincidencias vigentes confirmadas explícitamente. | `cumple` | `advertencia` |

C2/C3/C4 con `aplica=false` producen `no_aplica` y no ejecutan comprobaciones. No es válido publicar C2 aplicable sin campos requeridos ni exigencia de texto, ni C4 aplicable sin selecciones requeridas ni exigencia de texto; se evitaría un cumplimiento vacío. El tipo de regla es fijo por criterio y las verificaciones se combinan con AND, nunca se elige el mejor resultado.

Para objetivo propio: C1 permite cualquier acción conocida; C5 admite cualquier formato conocido con detalle opcional; C2 aplicable exige texto de contexto; C3 aplicable exige destinatario; C4 aplicable exige texto de restricciones; C6 siempre aplica. Este perfil no intenta evaluar si el objetivo está bien formulado.

Declarar «tono formal» en una restricción solo acredita que la condición se seleccionó/escribió. No se comprueba que el texto tenga ese tono, que la fecha tenga sentido ni que el contenido de contexto sea suficiente. No usar expresiones regulares para inferir esas cualidades.

## Ensamblado guiado

Orden fijo: tarea, contexto, destinatario, restricciones, formato. Usar títulos legibles y saltos de línea. En tarea incluir texto y etiqueta de la acción seleccionada; en contexto incluir texto y campos configurados con sus etiquetas; en restricciones incluir texto y etiquetas de selecciones; en formato incluir etiqueta del tipo y detalle. Omitir valores vacíos, pero no omitir contenido que el usuario escribió en un criterio no aplicable. Esos campos se revisan igualmente por seguridad. Recalcular el texto en el servidor; no confiar en un texto ensamblado por el cliente.

En modo libre no reescribir ni «mejorar» el texto. Los componentes declarados son la evidencia, sin prometer que están presentes o bien expresados en la redacción. Mostrar esa limitación en la pantalla de revisión.

## Mensajes y evidencia

Cada resultado contiene `criterio_codigo`, `estado`, `regla_id`, `regla_version`, `condicion_esperada`, `evidencia`, `mensaje` y `accion_sugerida`. El estado `no_aplica` lleva regla nula y explicación de la configuración. Los seis resultados siempre aparecen, en orden C1–C6.

| Criterio | Mensaje de revisión | Acción |
|---|---|---|
| C1 | «Falta declarar la tarea o elegir una acción admitida para este ejercicio.» | «Completá la tarea y revisá la acción seleccionada.» |
| C2 | «Falta completar información de contexto solicitada por el ejercicio.» | «Completá los campos de contexto indicados.» |
| C3 | «No declaraste a quién estará dirigida la respuesta.» | «Indicá el destinatario.» |
| C4 | «Quedan condiciones del ejercicio sin declarar.» | «Revisá las restricciones indicadas.» |
| C5 | «Falta elegir un formato admitido o completar su detalle.» | «Elegí el formato y completá el detalle cuando corresponda.» |
| C6 | «Se detectaron patrones que podrían corresponder a datos sensibles.» | «Editá el contenido o confirmá cada coincidencia después de revisarla.» |

Para resultados satisfactorios usar mensajes específicos: «Tarea declarada y acción seleccionada», «Contexto requerido completo», «Destinatario declarado», «Restricciones requeridas declaradas», «Formato declarado». C6 sin coincidencias: «No se detectaron coincidencias de los patrones configurados». C6 confirmado: «Revisión de coincidencias confirmada por vos; esto no garantiza que el contenido sea seguro».

Evidencia segura: rutas de campos, presencia/ausencia, cantidad de selecciones, IDs y lista de condiciones faltantes. No copiar el fragmento de correo/teléfono/documento en resultados o alertas. El propietario puede consultar su texto original en la versión, que queda sujeto a la confirmación y al borrado de prácticas.

## Patrones de seguridad iniciales

El código implementa detectores permitidos `email_v1`, `telefono_ar_v1`, `dni_etiquetado_v1` y `secuencia_numerica_7_8_10_v1`. Sus expresiones y filtros están en `seeds/rules.json`. Son patrones sintácticos iniciales por revisar, no validadores oficiales de identidad o telefonía. El administrador puede activar/desactivar detectores de la lista; no introducir expresiones regulares arbitrarias.

- Correo: estructura local@dominio.extensión, sin afirmar existencia de la cuenta.
- Teléfono: prefijo internacional `+54` o etiqueta «teléfono/tel/celular», seguido de un grupo con separadores y entre 8 y 13 dígitos nacionales; el grupo termina antes de un salto de línea. No marcar números aislados sin contexto telefónico.
- Documento: «DNI»/«documento» más 7 u 8 dígitos, con separadores opcionales. Este detector no marca un número aislado sin etiqueta; el detector independiente nuevo sí puede marcar sus longitudes exactas.

- Secuencia numérica (D36): ASCII 0–9, tramos completos de exactamente 7, 8 o 10 dígitos, incluidos ceros iniciales; sin etiquetas ni unión/eliminación de separadores. Regex fija `(?<![0-9])(?:[0-9]{10}|[0-9]{8}|[0-9]{7})(?![0-9])`. Tipo `secuencia_numerica`: posible información sensible, sin atribuir identidad o teléfono. Evaluar después de los detectores existentes y omitir sólo la genérica completamente cubierta por una alerta anterior aceptada del mismo campo. Mantener las alertas previas y multiplicidad entre apariciones/campos distintos.

Escanear objetivo y todos los valores textuales ingresados, aun si el criterio es no aplicable. En guiado no escanear otra vez el texto ensamblado para evitar duplicados del mismo campo; las etiquetas del catálogo son texto controlado. En libre escanear también `texto_libre`. Normalizar solo saltos de línea/Unicode; no eliminar caracteres que cambien coincidencias.

Para contar una aparición usar `(tipo, ruta_campo, inicio, fin)`; fusionar resultados idénticos de un mismo detector. El cliente recibe una clave opaca por coincidencia y su tipo/campo, no offsets ni fragmentos. Al persistir guardar tipo, campo, estado `confirmada`, fecha y una huella HMAC con clave secreta: práctica + tipo + campo + valor normalizado. La huella no permite recuperar el fragmento sin la clave; no registrarla en logs ni enviarla al cliente. Conservar multiplicidad y versión de clave para comparar alertas sin guardar fragmentos adicionales.

Si se modifica cualquier dato, cambian las coincidencias o cambia la configuración, se exige una revisión nueva. No existe un consentimiento permanente para futuras versiones.

Limitaciones previstas: falsos positivos en datos ficticios y falsos negativos en correos ofuscados, números con otras longitudes o formatos no cubiertos, nombres, direcciones, credenciales o información laboral. Mostrar siempre «Estos patrones no detectan toda la información sensible».

## Indicadores sin pesos

Sea A el conjunto de criterios aplicables y K los que tienen `estado=cumple`:

`cumplimiento = 100 × |K| / |A|`

C6 participa con una unidad como los demás. `no_aplica` queda fuera. `revisar` y `advertencia` no suman. Guardar numerador/denominador y calcular con precisión completa; mostrar un decimal. Si un caso defensivo no tiene aplicables, devolver `null` («Sin criterios aplicables»), nunca dividir por cero. La configuración normal lo impide.

En un desafío con C1–C6 aplicables, cuatro cumplidos y dos pendientes producen 66,7 %. Si C2 y C3 no aplican y los restantes cumplen, son 4/4 = 100 %. Si se confirma una coincidencia, C6 puede pasar a cumple: el aviso sigue visible. Nunca presentar 100 % como «prompt seguro».

`delta_pp = cumplimiento_V2 - cumplimiento_V1` en puntos porcentuales. No llamar mejora a un delta positivo si aparecieron alertas nuevas. Comparar el multiconjunto de huellas de alertas de ambas versiones; si cambió la clave de huellas y no puede compararse, informar «No se pudo determinar si hay alertas nuevas», sin declarar mejora.

`resolucion = 100 × observaciones_de_V1_resueltas_en_V2 / observaciones_de_V1`. Observación = criterio aplicable de V1 en `revisar` o `advertencia`; resuelto si pasa a `cumple` bajo condiciones comparables. Si V1 no tiene observaciones, devolver `null` («Sin observaciones iniciales»), no 100 %.

`transferencia_pp = cumplimiento_primer_intento_nuevo - cumplimiento_primer_intento_linea_base`. Solo comparar condiciones equivalentes y primeros intentos. No es una media general ni demuestra aprendizaje por sí sola. La comprensión se registra mediante evaluación humana: explicaciones correctas/consultadas × 100; sin consultas devuelve `null`. No usar coincidencias de palabras para calificar explicaciones.

## Trazabilidad y comparabilidad

Cada evaluación guarda una instantánea con IDs/versiones de reglas, parámetros efectivos, aplicabilidad, textos de mensajes/nombres, configuración del desafío y versión del motor. La firma de comparación incluye código/versión del motor, reglas/versiones y configuración efectiva de C1–C6; excluye título, ID del desafío, fecha y consigna. Así dos tareas distintas de dificultad/configuración equivalente pueden comparar sus indicadores, sin ignorar que la equivalencia educativa necesita revisión humana.

Si cambia la firma, mostrar indicadores históricos y diferencias textuales, pero `comparable=false`, `delta_pp=null`, `resolucion=null` y motivo visible. No modificar la evaluación antigua. En esta versión se guarda una evaluación por versión de prompt; reevaluar con otras reglas requiere crear una versión nueva, aunque el texto se mantenga igual.

D36 se publica como nueva versión C6 mediante el servicio administrativo. Historial/snapshots conservados, sin recalcular. Las reglas iniciales v1 y corpus permanecen como referencia histórica; la activación en instalaciones existentes/nuevas usa `app.scripts.enable_numeric_detector --entorno desarrollo` tras seeds. Evidencia actual en docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md.
