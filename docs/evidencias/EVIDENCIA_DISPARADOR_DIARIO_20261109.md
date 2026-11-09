# Disparador diario comprobado — 9/11/2026

**Resultado: ejecución automática por horario comprobada para EntrenadorPrompts-Respaldo el 9/11/2026 a las 02:00:01, Córdoba (UTC−03).** Se correlacionaron registros existentes del canal Microsoft-Windows-TaskScheduler/Operational y la referencia preparada el 8/11. No se ejecutó manualmente el respaldo, no se modificó la tarea ni se inició una restauración SQL.

## Cadena de eventos de la misma instancia

Tarea exacta: `\EntrenadorPrompts-Respaldo`. Instancia común: `{bcaabcf6-f442-4948-bcd6-2851a1bf8690}`. Horas locales obtenidas de UTC restando tres horas, sin cambiar la zona del sistema.

| Evento | RecordId | UTC 9/11 | Córdoba 9/11 | Evidencia |
|---|---:|---|---|---|
| 107 | 528 | 05:00:01.8375713Z | 02:00:01.8375713 | Inicio por condición de desencadenador de hora. |
| 100 | 530 | 05:00:01.8638941Z | 02:00:01.8638941 | Instancia iniciada. |
| 200 | 531 | 05:00:01.8638960Z | 02:00:01.8638960 | Acción iniciada, mismo TaskInstanceId. |
| 201 | 536 | 05:00:09.4643375Z | 02:00:09.4643375 | Acción finalizada, **ResultCode=0**. |
| 102 | 537 | 05:00:09.4646469Z | 02:00:09.4646469 | Instancia finalizada correctamente. |

El registro intermedio 129/RecordId 529 se conserva en el reporte filtrado, pero no tiene InstanceId en los campos extraídos y no se utiliza para demostrar la correlación. No apareció 110 para esta tarea/instancia en la consulta. La conclusión se apoya en el 107 positivo y la cadena común, no solamente en la ausencia de 110 ni en LastTaskResult.

## Referencia y programación conservadas

Preparación original: 8/11 21:58:10 Córdoba (9/11 00:58:10Z), historial habilitado por Santiago. Consulta actual de Codex: **9/11 11:10:05Z =08:10:05 Córdoba**, historial activo y SHA-256 del XML completo **idéntico** al guardado en `local-data/etapa06/disparador-diario-preparacion.json`. La comparación incluye trigger, acciones, principal y settings; no se reexportó una definición diferente para sustituir la referencia.

Tarea **Ready, habilitada**, StartBoundary 8/11 02:00 −03, intervalo **un día**, próxima ejecución **10/11/2026 02:00 −03**. StartWhenAvailable=true y WakeToRun=false conservados. LastRunTime **9/11 02:00:01**, LastTaskResult **0**. Esta ejecución ocurrió cerca del horario previsto; la hipótesis de ejecución diferida del 8/11 sigue siendo un antecedente distinto y no se reinterpreta retroactivamente.

## Copia y fuente de la verificación

Estado del trabajo: aprobado, inicio registrado **05:00:05.806443Z**, manifiesto `tfg-20261109T050008-99b8002357474e56a75709cd778a19bb.manifest.json`. Copia **05:00:08.436255Z =02:00:08.436255 Córdoba**, **54555 bytes**, origen entrenador_prompts, esquema **20261107_0004**. Es posterior al inicio y anterior a la finalización de esa instancia. No hay otra ejecución de esta tarea en el intervalo consultado que vuelva ambigua esa asociación.

Santiago ejecutó el verificador a **11:03:34.629921Z =08:03:34 Córdoba**, que informó autenticidad/SHA-256 y descifrado completo con pg_restore al dispositivo nulo aprobados. Se leyó su reporte existente `local-data/etapa06/respaldo-verificado-20261109T110334629921Z.json` y se comprobó que identifica exactamente el mismo manifiesto/fecha/tamaño que el estado actual. Codex volvió a autenticar y comprobar tamaño/SHA-256 mediante `verify_manifest`, sólo lectura; **no repitió el descifrado, no generó otra copia ni restauró SQL** en esta comprobación. Retención informada por el trabajo: tres copias retenidas, cero purgadas, B2=false.

## Comandos y alcance

Desde raíz se ejecutó únicamente la acción de consulta:

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\registrar_disparador_respaldo.ps1))) -Accion consultar
```

Además: Get-ScheduledTask/Get-ScheduledTaskInfo, Export-ScheduledTask para comparación SHA-256, lectura de referencia/estado/reporte existente y autenticación de manifiesto. Las lecturas protegidas requirieron permiso fuera del sandbox, sin elevar/reconfigurar la tarea. No se usó Start-ScheduledTask, no se lanzó scheduled_backup.py ni se cambió el canal, energía o antivirus. El auxiliar escribe sólo un reporte técnico filtrado en local-data, sin cuerpos, claves, usuarios, cookies o tokens; eso no cambia la tarea ni los datos de desarrollo.

Reporte de eventos conservado: `local-data/etapa06/disparador-diario-consulta-20261109T1110056918419Z.json`. Referencia y verificador permanecen sin sobrescribir. Matriz e inventario actualizados con esta evidencia; no se repiten pruebas de aplicación para un cambio documental. La regresión final del incremento numérico se conserva como ejecución previa de **358 aprobadas**, separada de esta lectura de eventos.

## Límites y pendientes separados

- **Aprobado:** este disparo diario por horario, finalización con 0 y asociación con copia autenticada/descifrada.
- **No demostrado por este caso:** continuidad diaria futura, RPO/RTO continuo, ejecución con sesión cerrada el 9/11, despertar tras suspensión o comportamiento con equipo apagado. El ensayo sin sesión del 8/11 conserva su aprobación independiente basada en la confirmación manual del intervalo.
- **No ejecutado:** restauración SQL de esta copia. Autenticar/descifrar no equivale a restaurar y reaplicar borrados.
- **Pendientes:** B2 real, custodia/transferencia/recuperación externa y NF-02. No se habilitaron ni se consideran resueltos por este resultado. La fila 05.9c y los requisitos OPS amplios siguen parciales por sus tramos externos/continuidad.
