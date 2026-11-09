# Sólo habilita/consulta el canal de historial. No registra ni ejecuta tareas.
param([ValidateSet('preparar','consultar')][string]$Accion='consultar')
$ErrorActionPreference='Stop'
$nombre='EntrenadorPrompts-Respaldo'
$canal='Microsoft-Windows-TaskScheduler/Operational'
$raiz=if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
if (-not (Test-Path -LiteralPath (Join-Path $raiz 'scripts/scheduled_backup.py'))) { throw 'Ejecutar desde la raiz del proyecto.' }
$carpeta=Join-Path $raiz 'local-data/etapa06'
$null=New-Item -ItemType Directory -Force -Path $carpeta
$referencia=Join-Path $carpeta 'disparador-diario-preparacion.json'
function HuellaXml {
    $xml=Export-ScheduledTask -TaskName $nombre -ErrorAction Stop
    [Convert]::ToBase64String([Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($xml)))
}
$t=Get-ScheduledTask -TaskName $nombre -ErrorAction Stop
$i=$t | Get-ScheduledTaskInfo
$antes=HuellaXml
$historial=Get-WinEvent -ListLog $canal -ErrorAction Stop
if ($Accion -eq 'preparar') {
    # El canal incluye todas las tareas del equipo; no borrar ni cambiar retención/tamaño.
    if (-not $historial.IsEnabled) {
        & "$env:SystemRoot\System32\wevtutil.exe" sl $canal /e:true
        if ($LASTEXITCODE -ne 0) { throw 'Windows no habilito el historial. Repetir desde PowerShell como administrador con tu misma cuenta.' }
    }
    $habilitado=(Get-WinEvent -ListLog $canal -ErrorAction Stop).IsEnabled
    $despues=HuellaXml
    if (-not $habilitado -or $antes -ne $despues) { throw 'No se confirmo historial habilitado y tarea intacta.' }
    if (Test-Path -LiteralPath $referencia) {
        $archivo=Join-Path $carpeta ('disparador-diario-preparacion-anterior-'+[DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')+'.json')
        Copy-Item -LiteralPath $referencia -Destination $archivo -ErrorAction Stop
    }
    $datos=[ordered]@{fecha_utc=[DateTimeOffset]::UtcNow.ToString('o');historial_habilitado=$habilitado;
        habilitado_previamente=$historial.IsEnabled;xml_diaria_sha256_base64=$antes;xml_diaria_identico=$true;
        proxima=$i.NextRunTime.ToString('o');inicio=$t.Triggers[0].StartBoundary;intervalo_dias=$t.Triggers[0].DaysInterval;
        tarea_habilitada=$t.Settings.Enabled;start_when_available=$t.Settings.StartWhenAvailable;
        wake_to_run=$t.Settings.WakeToRun;disparador_todavia_no_comprobado=$true}
    $datos | ConvertTo-Json | Set-Content -LiteralPath $referencia -Encoding UTF8
    $datos | ConvertTo-Json
    return
}
if (-not $historial.IsEnabled) { throw 'Historial deshabilitado; no se acredita disparador.' }
# Intervalo explícito Córdoba/UTC−03. No depende de la zona configurada en el equipo.
$desde=[DateTimeOffset]::Parse('2026-11-09T00:00:00-03:00').LocalDateTime
$hasta=[DateTimeOffset]::Parse('2026-11-10T00:00:00-03:00').LocalDateTime
$errores=@()
$eventos=@(Get-WinEvent -FilterHashtable @{LogName=$canal;StartTime=$desde;EndTime=$hasta} -ErrorAction SilentlyContinue -ErrorVariable errores)
foreach ($errorEvento in $errores) {
    if ($errorEvento.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') { throw 'No se pudo consultar el historial; revisar permisos.' }
}
$filtrados=@(foreach ($e in $eventos) {
    [xml]$x=$e.ToXml()
    $campos=@{}
    foreach ($d in $x.Event.EventData.Data) { $campos[[string]$d.Name]=[string]$d.'#text' }
    if ($campos['TaskName'] -ne ('\'+$nombre)) { continue }
    $instancia=$campos['InstanceId']
    if (-not $instancia) { $instancia=$campos['TaskInstanceId'] }
    [pscustomobject]@{id=$e.Id;registro=$e.RecordId;fecha_utc=$e.TimeCreated.ToUniversalTime().ToString('o');
        tarea=$campos['TaskName'];instancia=$instancia;resultado=$campos['ResultCode']}
})
$identico=$null
if (Test-Path -LiteralPath $referencia) {
    $base=Get-Content -Raw -Encoding UTF8 -LiteralPath $referencia | ConvertFrom-Json
    $identico=$antes -eq $base.xml_diaria_sha256_base64
}
$datos=[ordered]@{consultado_utc=[DateTimeOffset]::UtcNow.ToString('o');historial_habilitado=$true;
    xml_identico_a_preparacion=$identico;ultima_ejecucion=$i.LastRunTime.ToString('o');ultimo_resultado=$i.LastTaskResult;
    proxima=$i.NextRunTime.ToString('o');eventos=@($filtrados | Sort-Object registro);
    limite='Correlacionar 107/100/200/201/102 por instancia y copia nueva; 110 indica inicio solicitado por usuario. Sin eventos no se acredita disparador. No se aprueba automaticamente.'}
$archivo=Join-Path $carpeta ('disparador-diario-consulta-'+[DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')+'.json')
$datos | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $archivo -Encoding UTF8
$datos | ConvertTo-Json -Depth 5
