> Guía técnica conservada del desarrollo. Las observaciones sobre el «equipo actual» corresponden al entorno original. Para una instalación nueva, comenzar por [INSTALACION_WINDOWS.md](../INSTALACION_WINDOWS.md). Los comandos se ejecutan desde la raíz del proyecto, salvo indicación expresa.

# Custodia externa del material de recuperación — Windows

Revisión del procedimiento existente, 8/11/2026. **Preparado, no transferencia externa realizada ni recuperación de otro equipo acreditada.** No cambia bases, contraseñas, configuración ni claves existentes. B2 continúa sin habilitar. El ensayo local sin sesión ya aprobado no sustituye custodia independiente.

## Material que debe sobrevivir a la pérdida de esta computadora

| Material | Qué conservar fuera del equipo |
|---|---|
| Copias de PostgreSQL | Cada conjunto retenido completo: `tfg-….backup.age`, `tfg-….manifest.json` y `tfg-….manifest.auth`, con el mismo prefijo. No copiar sólo el dump ni mezclar prefijos. |
| Configuración y borrados | Un paquete **actualizado** `tfg-config-….age`, creado por `scripts/recover_configuration.py exportar`. Incluye `local.env` (contraseñas/claves de aplicación), `borrados.fernet`, `journal.key`, `journal.anchor` y manifiesto interno. No sustituye al diario independiente más reciente. |
| Identidad privada age | Copia de la identidad original `backup.agekey`, protegida por cifrado adicional y **custodiada por separado** de los respaldos/paquetes. Sin ella no se descifran ni PostgreSQL ni el paquete de configuración. No generar otra para sustituir la perdida. |
| Código y procedimiento | Código del commit comprobado, locks, migraciones, seeds, versión de PostgreSQL/age y guías de recuperación. Puede guardarse un ZIP del contenido versionado; no copiar `.env`, `.venv`, `node_modules` ni credenciales de demo como parte del código. |
| Inventario de custodia | Fecha UTC, identificador del paquete y de cada conjunto, hashes de archivos **cifrados**, ubicación física/custodio y fecha de verificación. Sin contenidos, contraseñas, claves, cookies ni tokens. Mantenerlo fuera de Git si contiene ubicaciones privadas. |

Ubicaciones actuales descritas por el proyecto: copias en `%LOCALAPPDATA%\EntrenadorPrompts\backups`, configuración cifrada en `%LOCALAPPDATA%\EntrenadorPromptsRecovery`, identidad y clave/ancla en `%LOCALAPPDATA%\EntrenadorPromptsKeys`, diario en `%LOCALAPPDATA%\EntrenadorPrompts\diario`. Las variables `BACKUP_DIRECTORY`, `BACKUP_IDENTITY_FILE`, `DELETION_JOURNAL_LOCATION`, `DELETION_JOURNAL_KEY_FILE` y `DELETION_JOURNAL_ANCHOR_FILE` de `.env` son la referencia si se cambiaron las rutas. No mostrar `.env` en terminal/chat.

Usar un medio externo bajo control del responsable y guardar otra copia protegida físicamente independiente. ACL de Windows no son cifrado y no necesariamente se conservan en un USB. Los respaldos/paquetes ya están cifrados con age; la identidad privada original es un archivo sensible **sin contraseña propia**. Protegerla antes de transportarla. No guardar la frase que la protege en el mismo medio ni junto a las copias; custodiarla en un gestor protegido o medio separado accesible al responsable. No se modifica BitLocker ni se contrata un proveedor por este procedimiento.

## Actualizar y comprobar el paquete, sin tocar desarrollo

Desde la raíz, en PowerShell con la misma cuenta. Puede necesitar elevación sólo si las ACL impiden lectura:

```powershell
& .\.venv\Scripts\python.exe scripts\recover_configuration.py exportar --destination "$env:LOCALAPPDATA\EntrenadorPromptsRecovery"
$paquete = Read-Host 'Ruta exacta del paquete cifrado recién creado'
& .\.venv\Scripts\python.exe scripts\recover_configuration.py verificar --file $paquete
if ($LASTEXITCODE -ne 0) { throw 'No transferir como paquete verificado.' }
```

Exportar toma el bloqueo del diario y comprueba clave/ancla; captura los cuatro archivos de forma coherente sin mostrar su contenido. Escribe sólo un paquete nuevo, no modifica las bases ni reemplaza la configuración. `verificar` descifra en memoria y valida tamaños/hashes del manifiesto interno; **no comprueba vigencia frente a borrados posteriores** ni usa por sí solo una identidad recuperada de otro equipo.

Si se solicita un borrado después de la exportación, el diario/ancla de ese paquete ya no son los últimos. Repetir exportación y transferencia coherentes tras esos cambios, conservar el diario independiente vigente y su clave/ancla. No copiar por separado esos tres archivos mientras puede haber escrituras; usar el paquete bajo bloqueo. Esta copia manual no implementa replicación continua ni garantiza un RPO. No podar marcas de borrado hasta verificar vencimiento de todas las copias locales **y externas** afectadas.

## Proteger la identidad para su custodia separada

Procedimiento manual preparado; no ejecutado por Codex sobre tu clave. `Read-Host` pide sólo rutas, nunca la frase. age la solicita interactivamente sin eco: elegí una frase larga **no vacía**, sin pedir autogeneración en la terminal. No pasarla como argumento, variable de entorno ni pegarla en el chat. Elegir un nombre de salida **nuevo**: age puede sobrescribir archivos existentes.

```powershell
$identidad = Read-Host 'Ruta local de BACKUP_IDENTITY_FILE (backup.agekey)'
$claveProtegida = Read-Host 'Ruta NUEVA en medio separado para backup-identidad.age'
if (Test-Path -LiteralPath $claveProtegida) { throw 'Elegí una ruta nueva; no sobrescribir.' }
& .\local-data\age\age.exe -p -o $claveProtegida $identidad
if ($LASTEXITCODE -ne 0) { throw 'No se completó la protección de la identidad.' }
```

No usar como destinatario la misma identidad que se intenta recuperar: produciría una dependencia circular. La identidad protegida por frase permite recuperarse sin el archivo local original, siempre que la frase esté disponible por un canal independiente. Mantener los originales privados del equipo intactos.

## Copiar y verificar los archivos cifrados

Elegí el destino externo y los conjuntos conscientemente; estos comandos no buscan ni borran archivos en otros dispositivos. Copiá los tres archivos de cada prefijo y el paquete actual, conservando sus nombres. Ejemplo de copia individual sin sobrescritura, repetible para cada archivo **cifrado o manifiesto técnico** seleccionado:

```powershell
$origen = Read-Host 'Ruta exacta del archivo a copiar'
$destino = Read-Host 'Ruta NUEVA completa del mismo archivo en el medio externo'
if (Test-Path -LiteralPath $destino) { throw 'El destino ya existe; no sobrescribir.' }
Copy-Item -LiteralPath $origen -Destination $destino -ErrorAction Stop
if ((Get-FileHash -LiteralPath $origen -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $destino -Algorithm SHA256).Hash) {
    throw 'La copia no coincide; no declararla verificada.'
}
'Copia idéntica por SHA-256; no se mostró contenido.'
```

Esto acredita igualdad de bytes, no autenticidad independiente ni recuperación de otro equipo. No usar esa copia individual para sacar `.env` o la identidad privada sin proteger. El paquete incluye la clave de autenticación de manifiestos; guardar los tres archivos de cada respaldo es necesario para su verificación posterior, no sólo el SHA-256 externo.

Verificar el paquete **desde su ubicación externa** y comprobar que puede descifrarse con la identidad externa protegida, sin extraer secretos ni escribir SQL:

```powershell
$paqueteExterno = Read-Host 'Ruta del tfg-config-….age copiado fuera del equipo'
& .\.venv\Scripts\python.exe scripts\recover_configuration.py verificar --file $paqueteExterno
if ($LASTEXITCODE -ne 0) { throw 'Paquete externo no verificado.' }
$claveExterna = Read-Host 'Ruta de backup-identidad.age del medio separado'
& .\local-data\age\age.exe -d -i $claveExterna -o NUL $paqueteExterno
if ($LASTEXITCODE -ne 0) { throw 'No se comprobó la identidad externa contra el paquete.' }
$copiaExterna = Read-Host 'Ruta de un tfg-….backup.age del medio de respaldos'
& .\local-data\age\age.exe -d -i $claveExterna -o NUL $copiaExterna
if ($LASTEXITCODE -ne 0) { throw 'No se descifró completamente la copia externa.' }
```

age admite identidades cifradas por frase como entrada `-i` y solicita la frase localmente. `NUL` descarta el contenido; **no omitir `-o NUL`**, porque el destino predeterminado es stdout. No usar tuberías de binarios a través de PowerShell 5.1. Este paso prueba autenticidad criptográfica/descifrado age completo y correspondencia de la identidad externa; el verificador Python adicional usa la identidad original local para verificar el manifiesto interno. Ninguno restaura PostgreSQL ni vuelve a abrir acceso. El descifrado del dump a NUL no valida por sí solo su estructura SQL ni la reaplicación de borrados.

Opcionalmente guardar código versionado sin archivos locales ignorados (ruta ZIP nueva):

```powershell
$codigo = Read-Host 'Ruta NUEVA externa para entrenador-codigo.zip'
if (Test-Path -LiteralPath $codigo) { throw 'No sobrescribir.' }
git archive --format=zip --output=$codigo HEAD
if ($LASTEXITCODE -ne 0) { throw 'No se exportó el código.' }
git rev-parse HEAD
```

Registrá el commit mostrado; la exportación no incluye cambios sin commit ni herramientas externas. Para recuperarse de una pérdida total también se necesitan Python/Node/PostgreSQL/age compatibles y las dependencias fijadas, con acceso a sus instaladores o copias verificadas autorizadas.

## Qué falta para acreditar recuperación externa

Transferencia y verificación reales de ambos medios, custodia de la frase y recuperación en equipo/entorno limpio todavía pendientes. No alcanza con otra carpeta del mismo disco ni con probar usando únicamente la clave original. Ensayar extracción sólo en destino privado nuevo/vacío; jamás sobre `.env`, diario o claves activos. Una restauración SQL se hace en destino exclusivo y exige el diario independiente más reciente, reaplicación de borrados y revocación de sesiones antes de abrir. Sin prueba de vigencia/integridad, mantener acceso cerrado. No habilitar B2 ni borrar materiales originales como parte de esta revisión.

Referencia de comandos/identidades cifradas: [documentación oficial de age](https://github.com/FiloSottile/age#usage). Funciones revisadas: `configuration_archive.export_configuration/contents/extract_configuration`, `journal.DeletionJournal.locked/_read` y `backups.verify_manifest/restore`.
