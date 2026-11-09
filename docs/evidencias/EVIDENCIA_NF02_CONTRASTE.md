# NF-02: contraste y repetición acotada — 8/11/2026

**Estado: hallazgo histórico no reproducido en este ensayo; NF-02 no aprobado.** No se borran ni reemplazan los reportes originales. No se atribuye salida física de datos, inocuidad o firma del componente a partir de un nombre de dominio. Antivirus, políticas y configuración del equipo sin cambios.

## Observación manual de Santiago

Santiago repitió una práctica con el marcador ficticio `PRUEBA_NF02_ABC123`. Informa tres coincidencias en URLs locales de 127.0.0.1:5173; la solicitud del componente que inspeccionó mostraba get, nocache y tm, con Ping y TimerCallback como iniciadoras. Es confirmación manual de esa muestra; no demuestra inspección exhaustiva de todos los cuerpos o representaciones codificadas. No se inventan capturas ni otros resultados.

## Qué identifica realmente la evidencia anterior

Archivo ignorado conservado: `local-data/etapa06/flujo-auditoria.json`, elemento **14 (índice desde cero; solicitud externa 15)** de `solicitudes_externas`. También existe una coincidencia en el elemento 14 de `flujo-auditoria-anterior-195329.json`, sin desglose de campos. Los tres reportes de administración no contienen coincidencias positivas.

| Dato histórico | Evidencia disponible |
|---|---|
| Origen | `http://gc.kis.v2.scr.kaspersky-labs.com` |
| Método/tipo | POST / XHR, iniciador script |
| Iniciadores | AsyncCall → Call → Call → Call, mismo origen |
| Cuerpo visible | 3517 bytes |
| Coincidencias conservadas | Dos campos fuente llamados `texto`, longitudes 45 y 34 |
| Ruta remota, requestId, hora y acción activa | **No registrados** |
| Campo JSON del cuerpo externo | **No registrado**; `campo=texto` era la clave del contenido local, no un campo de Kaspersky |

El código de `stage06_browser_audit.py` comparaba en memoria los textos recogidos de solicitudes locales `/practicas` con el `postData` externo, guardando sólo booleano y campo/longitud. No guardaba el cuerpo, hashes de cada texto, ruta, acción ni identidad de página para reconstruir el evento. En las fixtures CP-31/CP-01, Tarea y Contexto tienen 45/34 caracteres y son los textos utilizados en el inicio del recorrido. **Es una correspondencia con el caso candidato, no una identificación forense inequívoca de cada valor histórico sólo por su longitud.** No es posible recuperar ahora el campo remoto ni demostrar qué clic generó aquel POST. No se inventa esa información ni se atribuye el POST histórico a Ping.

Por tanto, el GET periódico inspeccionado por Santiago no contradice por sí solo el POST histórico: son solicitudes distintas. La coincidencia histórica sigue documentada como resultado del auxiliar, con trazabilidad insuficiente para reconstruir la solicitud exacta y sin corroboración positiva en el ensayo nuevo.

## Repetición ejecutada por Codex

Comando desde la raíz:

```powershell
& .\.venv\Scripts\python.exe scripts\check_nf02_focused.py
```

Resultado **0: caso ejecutado**, no aprobación de NF-02. Chrome 156.0.8078.80 y Edge 157.0.4341.42, procesos independientes headless; API/Vite temporales 18000/15173 y PostgreSQL real **entrenador_prompts_test**. Se verificó el destino antes de crear/limpiar únicamente la cuenta ficticia propia del ensayo. No se utilizaron datos de desarrollo. No fue una repetición de todo el recorrido de etapas 04/05.

En cada navegador: ingresar, desafío «Solicitar una reunión», constructor guiado CP-31, completar Tarea/Contexto y campos estructurados, pulsar **Revisar prompt** (3/6), añadir el marcador ficticio de Santiago a Tarea y volver a revisar. No se guardó una versión. Esperas de observación de 3/5/5 segundos en las fases del constructor; no es observación indefinida. Procesos temporales propios detenidos y cuenta ficticia/prácticas derivadas eliminadas exclusivamente en pruebas. Sin cambiar antivirus ni bloquear solicitudes.

Reporte original del ensayo: `local-data/etapa06/nf02-focalizado-20261108T201654116172Z.json`. Se guardaron host, método, ruta con segmentos opacos sustituidos, nombres de parámetros sin valores, fase activa, iniciadores y ubicación JSON de coincidencias. No cuerpos, HAR, credenciales, cookies, tokens ni fragmentos de prompts. La fase activa sería correlación temporal, no prueba de causalidad. La primera versión del sanitizador sustituyó también los segmentos vacíos y v1: en ese archivo el prefijo local aparece como `{segmento}/api/{segmento}`; la ruta real programada es `/api/v1/practicas/{id}/revisar`. Se corrigió el sanitizador para futuras ejecuciones sin modificar el reporte original ni volver a presentar el ensayo como ejecutado con código posterior.

| Resultado nuevo | Chrome | Edge |
|---|---:|---:|
| Solicitudes externas registradas | 23 | 23 |
| Cuerpos externos visibles con coincidencias de Tarea, Contexto o marcador | **0** | **0** |
| Solicitudes locales de revisión con coincidencias | 2 | 2 |
| GET periódicos `/…/from`, iniciadores AsyncCall/Call/SendRequest/Ping/TimerCallback | 18 | 18 |

POST externos observados, ambos sin coincidencias: `/…/to/wsm.sessionActivated` (97 bytes) y `/…/to/dp.onGetFields` (1566 bytes). Chrome usó `gc.kis.v2.scr.kaspersky-labs.com`, Edge `me.kis.v2.scr.kaspersky-labs.com`; iniciadores AsyncCall/Call, con otras funciones propias de cada llamada. Se registraron además GET de main.js, init y vs.onPasswordEntered. Esas denominaciones no prueban el contenido ni comportamiento de los endpoints. En los GET periódicos se guardaron sólo los nombres nocache/tm y ruta from; GET es el método, no se equipara automáticamente con un parámetro llamado get.

En las solicitudes locales, las coincidencias se localizaron en `/componentes/tarea/texto` y `/componentes/contexto/texto`; en la segunda revisión, el marcador adicional apareció en `/componentes/tarea/texto`. No hubo un nuevo cuerpo externo positivo para identificar su campo remoto.

## Conclusión y límites

La muestra nueva es compatible con la observación manual: coincidencias sólo en tráfico local. **No reprodujo el POST histórico de 3517 bytes** y no permite confirmar su ruta, campo externo o acción. Tampoco lo invalida retroactivamente ni permite afirmar ausencia de información codificada, completitud de CDP o destino físico final. No se revisó tráfico por tiempo indefinido ni se atribuyó el componente a un ejecutable firmado.

NF-02 se mantiene **pendiente/no aprobado**, con esta distinción explícita: registro histórico positivo limitado; repetición acotada negativa; origen físico/tratamiento y evento histórico exacto sin confirmar. No se eleva esa evidencia a una afirmación de filtración real ni se aprueba privacidad global por una búsqueda negativa. El informe de 317 pruebas y el corpus son históricos y no se vuelven a contar como ejecutados en esta comprobación.
