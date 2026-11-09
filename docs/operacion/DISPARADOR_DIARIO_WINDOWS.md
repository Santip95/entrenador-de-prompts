> Guía técnica conservada del desarrollo. Las observaciones sobre el «equipo actual» corresponden al entorno original. Para una instalación nueva, comenzar por [INSTALACION_WINDOWS.md](../INSTALACION_WINDOWS.md). Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Identificar el disparador diario — 9/11/2026 a las 02:00 Córdoba

**Actualización 9/11:** disparo por horario comprobado por instancia común en 107/100/200/201/102, resultado 0 y copia nueva. XML intacto, próxima 10/11 02:00 Córdoba. Ver docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md. Las indicaciones de preparación y su estado pendiente del 8/11 que siguen son antecedentes; no es necesario volver a habilitar o iniciar la tarea. B2/custodia externa/NF-02 y restauración SQL de esta copia conservan sus límites.

Objetivo pendiente: acreditar el disparo por horario, separado del ensayo sin sesión ya aprobado y de la ejecución compatible con diferida del 8/11. Preparación del 8/11: tarea Ready/habilitada, intervalo de un día, próxima 9/11/2026 **02:00 −03 =05:00Z**, S4U, StartWhenAvailable=true y WakeToRun=false. No se inicia manualmente ni se reprograma la diaria.

**Preparación completada:** Santiago ejecutó `preparar` en su PowerShell elevada el 8/11 a las **21:58:10 Córdoba (9/11 00:58:10Z)**. Historial habilitado y XML idéntico. Codex volvió a comprobarlo a las 21:59:59 y consultó el intervalo futuro a las 22:00:25: cero eventos, resultado esperado antes del 9/11 local. No repetir preparación para aprobar un disparador todavía no ocurrido; seguir la consulta posterior indicada abajo.

## Antes de esa hora

El canal Microsoft-Windows-TaskScheduler/Operational estaba deshabilitado (10 MiB configurados). El intento de habilitarlo desde Codex, incluso fuera del sandbox, recibió **Acceso denegado de Windows**; la intervención elevada de Santiago lo resolvió, como consta arriba. No fue rechazo de revisión automática. El comando siguiente se conserva como procedimiento reproducible, no como acción manual todavía pendiente.

Desde la raíz en PowerShell **como administrador con tu misma cuenta**:

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\registrar_disparador_respaldo.ps1))) -Accion preparar
```

Esperado: `historial_habilitado=true`, `xml_diaria_identico=true`, `proxima=2026-11-09T02:00:00…-03:00`. Guarda la referencia segura en `local-data/etapa06/disparador-diario-preparacion.json`; conserva la anterior si se repite. Sólo activa el canal con `wevtutil sl … /e:true` si estaba deshabilitado y comprueba SHA-256 del XML exportado antes/después. No registra/ejecuta tareas, no cambia horario/acciones/principal, no borra eventos ni cambia tamaño/retención. La habilitación afecta el historial de **todas las tareas del equipo**; nuestros reportes extraen sólo EntrenadorPrompts-Respaldo y campos permitidos, sin mensajes completos ni usuarios.

Dejá el equipo encendido y sin suspensión, conectado a corriente, durante el horario previsto. WakeToRun=false: no se espera que despierte por este ensayo. No se cambian energía o políticas globales. PostgreSQL debe seguir disponible como servicio; API/frontend/Mailpit no son necesarios. Podés cerrar sesión si querés, pero el disparador se comprueba por los eventos y este ensayo no vuelve a aprobar ausencia de sesión sin tu confirmación del intervalo. No pulsar Ejecutar ni usar Start-ScheduledTask para provocar una copia.

## Después de las 02:00 y una vez finalizado el trabajo

Antes de lanzar cualquier respaldo manual, desde raíz (elevar sólo si Windows deniega lectura):

```powershell
& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 .\scripts\registrar_disparador_respaldo.ps1))) -Accion consultar
& .\.venv\Scripts\python.exe scripts\check_scheduled_backup.py
& .\.venv\Scripts\python.exe scripts\manage_backup_task.py consultar
```

El auxiliar consulta exclusivamente el día **9/11 Córdoba**, con límites UTC−03 explícitos. Guarda cada consulta por fecha sin reemplazar las anteriores. Ejecutarlo el 8/11 puede devolver cero eventos: no es un fallo del respaldo futuro ni acredita el disparador. Falta de eventos por canal apagado, permisos o sobrescritura del historial impide concluir. Consultar pronto reduce el riesgo de que el canal circular de 10 MiB pierda eventos; no se modifica su retención.

En el manifiesto instalado de este Windows se comprobaron las definiciones:

| Evento | Significado y correlación |
|---|---|
| 107 | Inicio por condición de desencadenador de hora; TaskName e InstanceId. |
| 110 | Inicio solicitado por usuario; no sustituye al 107 del ensayo de horario. |
| 100 | Instancia iniciada; correlacionar mismo InstanceId. |
| 200 | Acción iniciada; TaskInstanceId corresponde a esa instancia. |
| 201 | Acción completada; correlacionar TaskInstanceId y revisar ResultCode cuando esté disponible. |
| 102 | Instancia finalizada correctamente; mismo InstanceId. |

No basta un 107 aislado, LastTaskResult=0 de una ejecución anterior o eventos de otra tarea. Correlacionar tarea exacta `\EntrenadorPrompts-Respaldo`, **misma instancia**, fecha/hora, finalización, estado del trabajo y manifiesto/copia nuevos. El XML debe coincidir con la referencia; el verificador debe aprobar autenticidad/SHA-256/descifrado completo del respaldo de esa ejecución. Eso no equivale a restauración SQL ni B2.

Si Windows estaba apagado/suspendido a las 02:00 y ejecuta más tarde, documentar ejecución diferida por horario cuando los eventos lo respalden, no puntualidad a las 02:00. Si aparece un inicio manual, no atribuirlo al calendario. El auxiliar no aprueba automáticamente el caso ni activa el historial retroactivamente. No hace falta compartir XML/EVTX completos: únicamente el reporte filtrado, hora, instancia, IDs, resultado y verificación segura, sin secretos.

Fuentes: definiciones locales consultadas con `Get-WinEvent -ListProvider Microsoft-Windows-TaskScheduler`, y [Microsoft: wevtutil](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/wevtutil). Pendiente obtener la evidencia real del 9/11; no se espera bloqueando la sesión de Codex hasta esa hora.
