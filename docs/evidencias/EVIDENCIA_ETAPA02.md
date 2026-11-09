# Evidencia de etapa 02 — motor puro

**Actualización manual 7/11/2026:** Santiago confirmó que revisó los mensajes y las limitaciones mostrados para CP-25/27/28, además de la coincidencia esperado/obtenido registrada anteriormente. **02.9 completada por él.** Se conserva íntegra la evidencia histórica siguiente. La presentación conjunta de ambos avisos junto a resultados en la interfaz sigue pendiente de implementación en etapa 04; esta confirmación no aprueba una pantalla inexistente.

Fecha de referencia del cliente: 6 de noviembre de 2026. Motor: `1.0.0`. Estado técnico: implementado y comprobado automáticamente. Base de referencia del cierre técnico de etapa 01: `2c2069e`; el commit que incorpora este informe identifica el incremento de etapa 02 (`git log -1 --oneline` al finalizar la entrega). No se implementó etapa 03 ni posterior.

## Alcance y entorno

Windows/PowerShell, Python 3.11.4 y la misma `.venv` con dependencias fijadas. No se instalaron dependencias ni se modificaron migraciones, API o frontend. `app/domain/evaluation.py` sólo utiliza biblioteca estándar; no importa SQLAlchemy, FastAPI ni configuración de entorno. El adaptador `app/application/fixture_evaluation.py` carga el catálogo ficticio y pasa los datos al dominio.

Se implementaron C1–C6, aplicabilidad y estados sin pesos; normalización NFC/LF; ensamblado guiado con etiquetas; modo libre con componentes confirmados y texto conservado; límites de entrada; revisión del objetivo; tres detectores fijos por código; mensajes, condiciones y evidencias seguras; snapshots; conteos, porcentaje, delta, resolución, transferencia y comprensión mediante conteos humanos suministrados. La comparación usa firmas y multiconjuntos de huellas HMAC, sin mezclar configuraciones diferentes.

Las coincidencias públicas contienen clave opaca, tipo, campo, mensaje y estado de confirmación; no contienen offsets ni fragmentos. El texto original sólo está en el resultado para su autor, separado de las evidencias. No hay logging del dominio. La confirmación en memoria se vincula al contenido normalizado, objetivo, configuración, usuario/práctica y versión de clave; no es un token HTTP ni acredita autenticación. El adaptador del corpus interpreta `confirmar_todas` exclusivamente como estado ficticio revisado; el motor no acepta esa bandera.

## Comandos ejecutados

Desde la raíz, para las comprobaciones del motor:

```powershell
Push-Location .\backend
try {
    & ..\.venv\Scripts\python.exe -m app.scripts.check_motor
    & ..\.venv\Scripts\python.exe -m app.scripts.check_motor --json
    & ..\.venv\Scripts\python.exe -m pytest tests\motor -q
    & ..\.venv\Scripts\python.exe -m pytest -q --junitxml=..\local-data\etapa02-regresion.xml
} finally { Pop-Location }
```

Resultado obtenido: corpus **33/33**, pruebas puras **120 aprobadas**, regresión completa **140 aprobadas**, sin fallos ni omisiones. La regresión agrega las 20 pruebas existentes de etapa 01, incluidas las que usan PostgreSQL y la base exclusiva de pruebas. El corpus y la suite `tests/motor` no requieren servidores, DB, red o `.env`. El informe JSON muestra esperado/obtenido por caso sin imprimir textos originales.

Durante la construcción se detectaron dos defectos en pruebas nuevas: una ruta al seed subía un nivel de más y una aserción buscaba la subcadena «fin» en todo el JSON, coincidiendo con «finalidad». Se corrigieron la ruta y la comprobación de claves de offsets. Las expectativas del corpus no se cambiaron. La ejecución posterior pasó completa.

## Esperado y obtenido para cada fixture

Estados en orden C1–C6: C = `cumple`, R = `revisar`, N = `no_aplica`, A = `advertencia`. En los casos de error se compara el código exacto. También se comparan los tipos/campos de cada coincidencia (incluida multiplicidad) contra el JSON original, no sólo la cantidad resumida aquí.

| Caso | Estados/error esperados | Estados/error obtenidos | Conteo; porcentaje; coincidencias: esperado → obtenido | Resultado |
|---|---|---|---|---|
| CP-01 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-02 | R/C/C/C/C/C | R/C/C/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-03 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-04 | C/R/C/C/C/C | C/R/C/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-05 | C/N/N/C/C/C | C/N/N/C/C/C | 4/4; 100 %; 0 coincidencias → 4/4; 100 %; 0 coincidencias | Aprobado |
| CP-06 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-07 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-08 | C/C/C/R/C/C | C/C/C/R/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-09 | C/C/C/C/C/A | C/C/C/C/C/A | 5/6; 83.3 %; 1 coincidencias → 5/6; 83.3 %; 1 coincidencias | Aprobado |
| CP-10 | C/C/C/C/C/A | C/C/C/C/C/A | 5/6; 83.3 %; 1 coincidencias → 5/6; 83.3 %; 1 coincidencias | Aprobado |
| CP-11 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-13 | R/C/C/C/C/C | R/C/C/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-14 | R/C/C/C/C/C | R/C/C/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-15 | C/C/R/C/C/C | C/C/R/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-16 | C/C/C/C/R/C | C/C/C/C/R/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-17 | C/C/C/C/R/C | C/C/C/C/R/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-18 | C/C/C/C/R/C | C/C/C/C/R/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-19 | C/C/C/C/C/A | C/C/C/C/C/A | 5/6; 83.3 %; 1 coincidencias → 5/6; 83.3 %; 1 coincidencias | Aprobado |
| CP-20 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 1 coincidencias → 6/6; 100 %; 1 coincidencias | Aprobado |
| CP-21 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-22 | componentes_sin_confirmar | componentes_sin_confirmar | — → — | Aprobado |
| CP-23 | C/C/C/C/C/A | C/C/C/C/C/A | 5/6; 83.3 %; 1 coincidencias → 5/6; 83.3 %; 1 coincidencias | Aprobado |
| CP-24 | C/N/N/C/C/A | C/N/N/C/C/A | 3/4; 75 %; 1 coincidencias → 3/4; 75 %; 1 coincidencias | Aprobado |
| CP-25 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-26 | R/C/C/C/C/C | R/C/C/C/C/C | 5/6; 83.3 %; 0 coincidencias → 5/6; 83.3 %; 0 coincidencias | Aprobado |
| CP-27 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-28 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-29 | seleccion_desconocida | seleccion_desconocida | — → — | Aprobado |
| CP-30 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-31 | C/R/R/C/R/C | C/R/R/C/R/C | 3/6; 50 %; 0 coincidencias → 3/6; 50 %; 0 coincidencias | Aprobado |
| CP-32 | C/C/C/C/C/C | C/C/C/C/C/C | 6/6; 100 %; 0 coincidencias → 6/6; 100 %; 0 coincidencias | Aprobado |
| CP-33 | C/N/N/N/C/C | C/N/N/N/C/C | 3/3; 100 %; 0 coincidencias → 3/3; 100 %; 0 coincidencias | Aprobado |
| CP-34 | C/R/N/N/C/C | C/R/N/N/C/C | 3/4; 75 %; 0 coincidencias → 3/4; 75 %; 0 coincidencias | Aprobado |

CP-12 no está en este corpus: pertenece a integración/persistencia de etapa 04. El archivo contiene 33 casos porque sus identificadores van de CP-01 a CP-34 con esa exclusión. Se conservaron los archivos y resultados esperados originales.

## Cobertura adicional y comprobaciones Windows

- **02.1:** los 33 casos se ejecutaron; tabla anterior y runner JSON permiten reproducir esperado/obtenido.
- **02.2:** 31 pruebas adicionales repiten los casos válidos y verifican igualdad completa y ausencia de mutación. Se bloquean `open`, `Path.open`, sockets y creación de motores SQLAlchemy durante una evaluación; una importación separada con Python `-I -S` prueba independencia de paquetes externos.
- **02.3:** positivos y faltantes parciales producen los estados del corpus, sin esconderlos como errores de esquema. Un borrador totalmente vacío no queda guardable; otro con tarea vacía y contenido parcial puede revisarse con C1 pendiente.
- **02.4:** CP-05 da 4/4 y CP-33 da 3/3; se mantienen los seis resultados. C1/C5/C6 no se pueden desactivar.
- **02.5:** los patrones copiados al código se cotejan exactamente con regex, grupo y límites de dígitos de `seeds/rules.json`. No se ejecutan regex configurables ni código administrativo.
- **02.6:** se prueban objetivo inicial y posterior, texto libre, texto opcional de C2/C3/C4 y multiplicidad. Confirmar conserva los avisos; una confirmación parcial deja C6 en advertencia. Cambiar contenido, configuración, sujeto/práctica o versión de clave invalida la confirmación. La confirmación inicial no se reutiliza para una versión.
- **02.7:** se comprueban orden y etiquetas del ensamblado, presencia de contenido en criterios no aplicables, confirmación obligatoria del libre y preservación de espacios, Unicode normalizado, saltos LF y texto con HTML tratado como datos.
- **02.8:** se rechazan tipos/claves/selecciones inválidas, duplicados y configuraciones con reglas faltantes/inactivas/dobles, tipo desconocido, operador OR, detector arbitrario, criterios obligatorios desactivados, parámetros desconocidos y cumplimientos vacíos de C2/C4. Errores seguros no reflejan el valor introducido. No se genera evaluación válida ante un error de configuración.
- **Límites:** componentes de 2000/2001, libre de 10000/10001, objetivo vacío/1000/1001 y espacios exteriores, JSON normalizado de 19999/20000/20001, selecciones de 10/11 y exceso de campos. También se rechaza ensamblado superior a 10000 sin recortar.
- **Indicadores:** delta 50 puntos y resolución 100 % para entradas comparables; denominadores cero devuelven null; sin observaciones iniciales no se inventa 100 %. Cambios de configuración inhiben delta/resolución/transferencia. Cambios de nombres y mensajes mantienen la firma pero conservan snapshots distintos. Huellas nuevas, multiplicidad y rotación de clave no permiten declarar mejora engañosa.
- **Privacidad:** resultados/coincidencias no incluyen el correo ficticio ni offsets, fragmentos o huellas internas. El dominio no emite logs y su representación de depuración oculta texto y claves.
- **02.9:** límites documentados/comprobados automáticamente y revisión manual confirmada por Santiago el 7/11/2026 después de ver los mensajes literales de CP-25/27/28. Presentación de ambos avisos junto a resultados en interfaz pendiente de etapa 04.

## Límites y pendientes

### Comprobación manual parcial y transcripción real para 02.9

En el registro inicial Santiago confirmó que CP-25, CP-27 y CP-28 coincidían con sus salidas esperadas y mostraban `aprobado=true`; entonces sólo estaba confirmada esa coincidencia, no la interpretación de los textos siguientes. El 7/11/2026 confirmó también su revisión de mensajes y limitaciones: 02.9 completada manualmente. Se conservan a continuación los resultados literales originales, sin cambios.

Se ejecutaron `load_fixture_data()`, `evaluate_case()` y `Evaluation.public()` para esos tres IDs con motor 1.0.0. También se ejecutó `python -m app.scripts.check_motor` desde `backend` y se cotejó su aviso final. Sin DB, red ni cambios de código.

Los tres casos devuelven `cumplidos=6`, `aplicables=6`, `cumplimiento_mostrado=100.0`, `coincidencias=[]` y estos mensajes idénticos:

| Criterio | Estado | Mensaje literal producido por el motor |
|---|---|---|
| C1 | cumple | Tarea declarada y acción seleccionada. |
| C2 | cumple | Contexto requerido completo. |
| C3 | cumple | Destinatario declarado. |
| C4 | cumple | Restricciones requeridas declaradas. |
| C5 | cumple | Formato declarado. |
| C6 | cumple | No se detectaron coincidencias de los patrones configurados. |

En C1, la condición literal es «Declarar la tarea y elegir una acción admitida: Redactar.». En CP-25 su evidencia indica `texto_presente=true` y `accion_id=redactar`; no expresa un juicio semántico sobre la cadena breve. En C6, la evidencia de los tres casos indica cero coincidencias y cero confirmadas; `accion_sugerida` es una cadena vacía, como en los otros criterios cumplidos.

Aviso literal de `Evaluation.public()["limites"]`: «Estos patrones no detectan toda la información sensible».

Aviso final literal de la consola: «Estos patrones no detectan toda la información sensible. El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.»

El informe resumido `check_motor --json` no incluye los mensajes individuales ni esos avisos: sólo esperado/obtenido y estado de cada prueba. Su campo `aprobado=true` significa que la prueba coincide con el contrato, no que el prompt sea de calidad ni que esté libre de datos sensibles.

La explicación específica de CP-27 (número sin etiqueta) y CP-28 (correo ofuscado) está documentada como falso negativo conocido, pero no se genera una alerta específica en sus resultados: los detectores no reconocen esos patrones. Tampoco existe un aviso individual del motor que diga que la cadena breve de CP-25 no prueba calidad. El aviso explícito sobre el significado del porcentaje existe en la consola, no como texto separado de cada resultado público. La interfaz actual sólo muestra la estructura inicial; todavía no presenta resultados ni avisos del motor. Su presentación funcional sigue pendiente de etapa 04. Estas observaciones se registran sin implementar mensajes o pantallas adicionales en este turno.

CP-25 demuestra únicamente presencia de una cadena breve. CP-27 conserva un número sin etiqueta no detectado; CP-28 conserva un correo ofuscado no detectado. Ningún caso permite afirmar calidad, comprensión semántica o privacidad garantizada. El runner incluye el aviso «Estos patrones no detectan toda la información sensible».

La función pura de transferencia recibe los primeros intentos seleccionados por su llamador; la selección real desde historial y su revisión educativa están pendientes. La comprensión recibe conteos humanos y no evalúa explicaciones. El almacenamiento de snapshots/huellas, autorización, tokens con firma y expiración, límites HTTP y guardado transaccional pertenecen a las etapas de integración. No se afirma que las historias de usuario o los casos SEC de API estén terminados por estas pruebas del dominio.

Santiago confirmó manualmente que backend y frontend funcionan en la revisión visual de etapa 01; se registra como evidencia aportada por él, sin inventar capturas ni resultados educativos. Su mensaje no confirmó explícitamente la detención manual, que no se da por probada.

**Estado al cierre técnico de etapa 02:** separación de roles PostgreSQL pendiente, sin cambios de permisos; hito previo incumplido conservado en `docs/historico/PROGRESS.md`. Mailpit quedaba para etapa 03. Ambos se resolvieron y comprobaron posteriormente en etapa 03: ver `docs/evidencias/EVIDENCIA_ETAPA03.md`. No se atribuye esa comprobación a la regresión histórica de etapa 02.

La validación externa de reglas sigue pendiente antes de las pruebas educativas. No se realizaron pruebas con personas, autenticación, nuevas pantallas, despliegue, respaldo/restauración ni medición NF-03 del endpoint persistente.
