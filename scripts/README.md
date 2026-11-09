# Auxiliares de Windows

Ejecutar desde la raíz y siguiendo [la guía de instalación](../docs/INSTALACION_WINDOWS.md) o [la guía de pruebas](../docs/PRUEBAS.md). Conservar los archivos en esta carpeta: varios auxiliares comparten importaciones y calculan la raíz desde su ubicación.

| Uso | Archivos principales |
|---|---|
| Instalación nueva | `crear_entorno_nuevo.sql`, `permisos_ejecucion_acceso.sql`, `bootstrap_pip_windows.py`, `install_mailpit.py`, `install_age.py`. |
| Configuración privada | `prepare_access_secret.py`, `prepare_review_secrets.py`, `prepare_operation_local.py`. |
| Bases adicionales de pruebas y demo | `crear_bases_operacion.sql`, `crear_base_demo.sql`, `check_operation_databases.py`, `demo.py`. |
| Respaldos y recuperación | `scheduled_backup.py`, `manage_backup_task.py`, `check_scheduled_backup.py`, `recover_configuration.py`. |
| Ensayos del programador | `ensayar_respaldo_sin_sesion.ps1`, `registrar_disparador_respaldo.ps1`. |
| Navegadores y rendimiento | `verify_stage04_browser.py`, `verify_stage05_browser.py`, `verify_stage06_browsers.py`, `verify_stage06_performance.py`, `check_numeric_browser.py`. |
| Inicio, demo y contingencia | `verify_startup.py`, `verify_stage06_demo.py`, `verify_restore_contingency.py`. |
| Auditoría y revisión | `check_access_manual.py`, `change_account_state_manual.py`, `stage06_browser_audit.py`, `check_nf02_focused.py`, `check_secrets.py`. |
| Informe histórico | `report_stage06.py`; conserva hechos manuales del entorno original, no certifica otra instalación. |

`crear_bases_locales.sql`, `separar_roles_locales.sql` y `separar_roles_objetos.sql` corresponden al aprovisionamiento y traslado histórico de las primeras etapas. Se conservan por trazabilidad; **no sustituyen `crear_entorno_nuevo.sql` para instalar desde cero**.

Los auxiliares administrativos y de restauración cambian los recursos indicados por sus guías. No ejecutar todos los archivos de esta carpeta como si fueran una secuencia de instalación.
