# Ejecutar con la misma cuenta del proyecto. No cierra sesiones ni cambia la tarea diaria.
param(
    [ValidateSet('preparar','consultar','eliminar')][string]$Accion = 'consultar',
    [ValidateRange(10,120)][int]$Minutos = 15
)
$ErrorActionPreference = 'Stop'
$nombre = 'EntrenadorPrompts-Respaldo-EnsayoSinSesion'
$raiz = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
if (-not (Test-Path -LiteralPath (Join-Path $raiz 'scripts/scheduled_backup.py'))) {
    throw 'Ejecutar desde la raiz del proyecto.'
}
$referencia = Join-Path $raiz 'local-data/etapa06/ensayo-sin-sesion.json'
if ($Accion -eq 'eliminar') {
    Unregister-ScheduledTask -TaskName $nombre -Confirm:$false -ErrorAction Stop
    Write-Output 'Tarea temporal eliminada. La tarea diaria y la evidencia se conservan.'
    return
}
if ($Accion -eq 'consultar') {
    Get-ScheduledTask -TaskName $nombre | Get-ScheduledTaskInfo |
        Select-Object LastRunTime,LastTaskResult,NextRunTime
    if (Test-Path -LiteralPath $referencia) { Get-Content -LiteralPath $referencia }
    Write-Output 'Comparar la hora con el intervalo SIN sesion informado por el usuario y verificar la copia. Resultado 0 por si solo no acredita sesion cerrada.'
    return
}
if (Get-ScheduledTask -TaskName $nombre -ErrorAction SilentlyContinue) {
    throw 'El ensayo ya existe. Consultarlo y retirar solo esa tarea antes de preparar otro.'
}
[xml]$xml = Export-ScheduledTask -TaskName 'EntrenadorPrompts-Respaldo'
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace('t','http://schemas.microsoft.com/windows/2004/02/mit/task')
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$principal = $xml.SelectSingleNode('/t:Task/t:Principals/t:Principal',$ns)
$accionOriginal = $xml.SelectSingleNode('/t:Task/t:Actions/t:Exec',$ns)
if ($principal.UserId -ne $sid -or $principal.LogonType -ne 'S4U' -or
    ($principal.RunLevel -and $principal.RunLevel -ne 'LeastPrivilege') -or
    $accionOriginal.Command -ne (Join-Path $raiz '.venv\Scripts\python.exe') -or
    $accionOriginal.Arguments -ne ('"' + (Join-Path $raiz 'scripts\scheduled_backup.py') + '"') -or
    $accionOriginal.WorkingDirectory -ne $raiz) {
    throw 'La tarea original no coincide con la cuenta/accion conocida. No se registra el ensayo.'
}
$inicio = [DateTimeOffset]::Now.AddMinutes($Minutos)
$disparos = $xml.SelectSingleNode('/t:Task/t:Triggers',$ns)
$disparos.RemoveAll()
$disparo = $xml.CreateElement('TimeTrigger',$ns.LookupNamespace('t'))
foreach ($par in @(@('StartBoundary',$inicio.UtcDateTime.ToString('yyyy-MM-ddTHH:mm:ssZ')),@('Enabled','true'))) {
    $elemento = $xml.CreateElement($par[0],$ns.LookupNamespace('t'))
    $elemento.InnerText = $par[1]
    $null = $disparo.AppendChild($elemento)
}
$null = $disparos.AppendChild($disparo)
$uri = $xml.SelectSingleNode('/t:Task/t:RegistrationInfo/t:URI',$ns)
if ($uri) { $uri.InnerText = '\' + $nombre }
$descripcion = $xml.SelectSingleNode('/t:Task/t:RegistrationInfo/t:Description',$ns)
if ($descripcion) { $descripcion.InnerText = 'Ensayo temporal de respaldo con sesion Windows cerrada; requiere comprobacion posterior.' }
# Sólo esta tarea nueva; sin Force, sin contraseña Windows y sin alterar políticas.
$null = Register-ScheduledTask -TaskName $nombre -Xml $xml.OuterXml
$null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $referencia)
@{preparado_utc=[DateTimeOffset]::UtcNow.ToString('o');inicio_previsto=$inicio.ToString('o');
  tarea=$nombre;sesion_cerrada_comprobada=$false} | ConvertTo-Json |
    Set-Content -LiteralPath $referencia -Encoding UTF8
Write-Output ('Ensayo previsto: ' + $inicio.ToString('yyyy-MM-dd HH:mm:ss zzz'))
Write-Output 'Guarda el trabajo y CERRA SESION de Windows antes de esa hora; no basta bloquear ni desconectar. Deja el equipo encendido, conectado a corriente y sin suspender. Volve a ingresar 5 minutos despues y consulta/verifica. No se cierra sesion automaticamente.'
