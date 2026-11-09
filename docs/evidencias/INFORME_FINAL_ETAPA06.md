# Informe final de verificación — etapa 06

Código base `f109b21`; versión final: commit que contiene este informe. Fecha inicial 7/11/2026; actualización operativa 9/11/2026. Windows nativo, PostgreSQL real y datos ficticios. Fuente de regresión: `local-data\detector-numerico-regresion-final.xml` (ejecución previa, no repetida al leer eventos); auditorías/mediciones en `local-data/etapa06/`.

**No se declara cierre integral:** NF-02 no está aprobado. NF-01 básico confirmado manualmente por Santiago el 8/11/2026, incluida repetición de Narrador en Edge. Esto no se oculta bajo las pruebas funcionales aprobadas. Disparo diario del 9/11 comprobado; continuidad, operación externa y validación educativa se distinguen del ensayo local.

| ID | Estado | Evidencia ejecutada y alcance |
|---|---|---|
| AT-01 | aprobado | `test_cp12_real_v1_v2_and_history` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-02 | aprobado | `test_empty_objective_never_creates_practice[]`, `test_empty_objective_never_creates_practice[ ]`, `test_empty_objective_never_creates_practice[\r\n]` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-03 | aprobado | `test_free_normalization_partial_and_empty_guard`, `test_server_storage_is_immutable_to_runtime` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-04 | aprobado | `test_saved_results_match_unchanged_fixture[CP-01]`, `test_saved_results_match_unchanged_fixture[CP-05]`, `test_saved_results_match_unchanged_fixture[CP-20]` y 6 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-05 | aprobado | `test_free_normalization_partial_and_empty_guard`, `test_normalization_preserves_free_text` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-06 | aprobado | `test_free_normalization_partial_and_empty_guard`, `test_empty_draft_not_saveable_but_partial_missing_task_is` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-07 | aprobado | `test_alerts_confirmation_and_safe_storage`, `test_int05_complete_objective_confirmation_delete_backup_restore` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-08 | aprobado | `test_sec13_14_stale_review_never_writes[draft]`, `test_sec13_14_stale_review_never_writes[token]`, `test_sec13_14_stale_review_never_writes[operation]` y 5 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-09 | aprobado | `test_alerts_confirmation_and_safe_storage`, `test_evidence_and_matches_do_not_echo_sensitive_fragments` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-10 | aprobado | `test_evaluate_works_when_io_is_forbidden`, `test_repeatable_without_mutating_inputs[CP-01]`, `test_repeatable_without_mutating_inputs[CP-02]` y 29 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-11 | aprobado | `test_saved_results_match_unchanged_fixture[CP-01]`, `test_saved_results_match_unchanged_fixture[CP-05]`, `test_saved_results_match_unchanged_fixture[CP-20]` y 8 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-12 | aprobado | `test_missing_active_rule_blocks_evaluation_without_partial_persistence`, `test_invalid_configuration_fails_closed[missing_rule]`, `test_invalid_configuration_fails_closed[inactive]` y 10 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-13 | aprobado | `test_saved_results_match_unchanged_fixture[CP-01]`, `test_saved_results_match_unchanged_fixture[CP-05]`, `test_saved_results_match_unchanged_fixture[CP-20]` y 5 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. Estructura/textos renderizados probados; comprensión educativa no acreditada. |
| AT-14 | aprobado | `test_fixture[CP-25]`, `test_fixture[CP-27]`, `test_fixture[CP-28]` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-15 | aprobado | `test_cp12_real_v1_v2_and_history` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-16 | aprobado | `test_idempotency_lost_responses_and_conflicts`, `test_concurrent_versions_numbering_and_retries[True]`, `test_concurrent_versions_numbering_and_retries[False]` y 1 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-17 | aprobado | `test_cp12_real_v1_v2_and_history` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-18 | aprobado | `test_at23_int03_publish_preserves_snapshot_and_stales_review` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-19 | aprobado | `test_argon2_id_parameters_and_unique_salt`, `test_031_register_duplicate_and_forbid_role` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-20 | aprobado | `test_032_generic_login_and_dummy_verification` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-21 | aprobado | `test_sec07_all_derived_resources_enforce_owner[usuario]`, `test_sec07_all_derived_resources_enforce_owner[administrador]`, `test_history_cursor_filters_and_progress_pagination` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-22 | aprobado | `test_sec12_15_16_new_alert_and_key_rotation`, `test_history_cursor_filters_and_progress_pagination` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-23 | aprobado | `test_at23_int03_publish_preserves_snapshot_and_stales_review` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-24 | aprobado | `test_draft_publish_edit_revision_and_no_destructive_routes`, `test_at24_inactive_challenge_history_read_and_no_new_versions` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| AT-25 | aprobado | `test_at25_concurrent_publication_one_winner`, `test_published_challenge_edit_rolls_back_all_six_criteria` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-01 | aprobado | `test_sec01_two_independent_sessions_admin_block_and_unblock` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-02 | aprobado | `test_sec02_write_serializes_before_restriction[bloqueado]`, `test_sec02_write_serializes_before_restriction[desactivado]`, `test_account_block_serializes_real_version_save[bloqueado]` y 1 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-03 | aprobado | `test_sec03_lengths[14-False]`, `test_sec03_lengths[15-True]`, `test_sec03_lengths[128-True]` y 6 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-04 | aprobado | `test_sec04_five_failures_revoke_and_timeout_does_not_revive`, `test_sec04_ip_limit_shared_between_service_instances` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-05 | aprobado | `test_sec05_logout_rotates_and_revokes_only_current`, `test_sec05_server_expirations_and_deleted_cookie[idle]`, `test_sec05_server_expirations_and_deleted_cookie[absolute]` y 3 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-06 | aprobado | `test_sec06_smtp_reset_single_use_and_global_revocation`, `test_sec06_reset_negative_cases[expired]`, `test_sec06_reset_negative_cases[blocked]` y 3 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-07 | aprobado | `test_own_delete_cascade_retry_other_practice_and_foreign_admin`, `test_sec07_all_derived_resources_enforce_owner[usuario]`, `test_sec07_all_derived_resources_enforce_owner[administrador]` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-08 | aprobado | `test_sec08_csrf_and_origin[missing_csrf]`, `test_sec08_csrf_and_origin[wrong_csrf]`, `test_sec08_csrf_and_origin[origin]` y 2 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-09 | aprobado | `test_sec09_password_change_revokes_sessions_and_reset_tokens`, `test_sec09_role_changes_are_read_server_side`, `test_real_encrypted_restore_completed_pending_deletions_and_contingency` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-10 | aprobado | `test_int04_failure_rolls_back_all_rows` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-11 | aprobado | `test_journal_failure_blocks_delete_and_pending_retry`, `test_pending_journal_survives_sql_rollback_and_retry`, `test_real_encrypted_restore_completed_pending_deletions_and_contingency` y 1 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-12 | aprobado | `test_non_applicable_text_still_scanned[contexto]`, `test_non_applicable_text_still_scanned[destinatario]`, `test_non_applicable_text_still_scanned[restricciones]` y 1 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-13 | aprobado | `test_sec13_14_stale_review_never_writes[draft]`, `test_sec13_14_stale_review_never_writes[token]`, `test_sec13_14_stale_review_never_writes[operation]` y 6 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-14 | aprobado | `test_sec14_real_publisher_waits_for_save_and_rejects_old_review` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-15 | aprobado | `test_sec12_15_16_new_alert_and_key_rotation` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-16 | aprobado | `test_sec12_15_16_new_alert_and_key_rotation` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| SEC-17 | aprobado | `test_sec17_errors_never_echo_sensitive_body[/auth/registro]`, `test_sec17_errors_never_echo_sensitive_body[/auth/login]`, `test_sec17_errors_never_echo_sensitive_body[/auth/recuperacion]` y 2 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| NF-04 | aprobado | `test_cp12_real_v1_v2_and_history`, `test_fixture[CP-01]`, `test_fixture[CP-02]` y 32 casos parametrizados más (JUnit/JSON). PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| OPS-01 | parcialmente comprobado | `test_real_encrypted_restore_completed_pending_deletions_and_contingency` Tramo local aprobado, incluido disparo por horario del 9/11 (docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md); proveedor externo, custodia offline y continuidad operativa pendientes. |
| OPS-02 | parcialmente comprobado | `test_real_encrypted_restore_completed_pending_deletions_and_contingency` Tramo local aprobado, incluido disparo por horario del 9/11 (docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md); proveedor externo, custodia offline y continuidad operativa pendientes. |
| OPS-03 | parcialmente comprobado | `test_actual_local_purge_preserves_unknown_files_and_exact_retention`, `test_cloud_plan_versions_hidden_files_and_abandoned_uploads` Tramo local aprobado, incluido disparo por horario del 9/11 (docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md); proveedor externo, custodia offline y continuidad operativa pendientes. |
| CP-12 | aprobado | `test_cp12_real_v1_v2_and_history` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| INT-02 | aprobado | `test_sec01_two_independent_sessions_admin_block_and_unblock` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| INT-03 | aprobado | `test_at23_int03_publish_preserves_snapshot_and_stales_review` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| INT-04 | aprobado | `test_int04_failure_rolls_back_all_rows` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| INT-05 | aprobado | `test_int05_complete_objective_confirmation_delete_backup_restore` PostgreSQL real cuando corresponde; motor puro para estados/normalización. |
| NF-01 | aprobado | `scripts/verify_stage06_browsers.py`, `docs/evidencias/EVIDENCIA_ETAPA06.md, confirmación manual 8/11/2026` 49 instantáneas AX/DOM y revisión manual de Santiago: teclado, foco, confirmaciones, etiquetas, errores, 360 px, zoom y Narrador en Chrome/Edge. Incidencia inicial en Edge; repetición correcta en ventana nueva sin cambios. Accesibilidad básica, sin certificación WCAG. |
| NF-02 | pendiente | `scripts/stage06_browser_audit.py`, `docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md` No aprobado: registro histórico de POST externo con dos coincidencias texto 45/34, sin ruta/campo remoto/acción registrados. Repetición acotada CP-31 en Chrome/Edge el 8/11 sin coincidencias externas; textos y marcador sólo en revisión local. No reconstruye ni refuta el evento histórico. Firma/ruta física/tratamiento pendientes, antivirus sin cambios. |
| NF-03 | aprobado | `local-data\etapa06\rendimiento-20261107T195543.json` Medición del 7/11 con motor 1.0.0, no repetida en esta lectura ni tras D36: 100 revisar + 100 guardar, cinco usuarios, 10 warmup/endpoint, texto libre 10000, p95 rango más cercano; todas las muestras/errores conservados. |
| VAL-01 | pendiente |  No hay dictamen externo. Obligatorio antes de pruebas educativas. |
| VAL-02 | pendiente |  No se reclutaron participantes ni se inventaron resultados. |
| CP-01 | aprobado | `test_fixture[CP-01]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-02 | aprobado | `test_fixture[CP-02]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-03 | aprobado | `test_fixture[CP-03]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-04 | aprobado | `test_fixture[CP-04]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-05 | aprobado | `test_fixture[CP-05]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-06 | aprobado | `test_fixture[CP-06]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-07 | aprobado | `test_fixture[CP-07]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-08 | aprobado | `test_fixture[CP-08]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-09 | aprobado | `test_fixture[CP-09]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-10 | aprobado | `test_fixture[CP-10]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-11 | aprobado | `test_fixture[CP-11]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-13 | aprobado | `test_fixture[CP-13]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-14 | aprobado | `test_fixture[CP-14]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-15 | aprobado | `test_fixture[CP-15]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-16 | aprobado | `test_fixture[CP-16]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-17 | aprobado | `test_fixture[CP-17]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-18 | aprobado | `test_fixture[CP-18]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-19 | aprobado | `test_fixture[CP-19]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-20 | aprobado | `test_fixture[CP-20]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-21 | aprobado | `test_fixture[CP-21]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-22 | aprobado | `test_fixture[CP-22]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-23 | aprobado | `test_fixture[CP-23]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-24 | aprobado | `test_fixture[CP-24]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-25 | aprobado | `test_fixture[CP-25]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-26 | aprobado | `test_fixture[CP-26]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-27 | aprobado | `test_fixture[CP-27]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-28 | aprobado | `test_fixture[CP-28]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-29 | aprobado | `test_fixture[CP-29]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-30 | aprobado | `test_fixture[CP-30]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-31 | aprobado | `test_fixture[CP-31]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-32 | aprobado | `test_fixture[CP-32]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-33 | aprobado | `test_fixture[CP-33]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |
| CP-34 | aprobado | `test_fixture[CP-34]` Esperado original sin modificar; configuración histórica C6 v1. Motor 1.1.0. |

Estados de OPS son parciales por los tramos externos: restore/diario/contingencia/purga local aprobados; B2 y custodia/transferencia externas no ejecutados. Tarea instalada por Santiago y ejecución por Start-ScheduledTask observada con resultado 0, ejecución del 8/11 a las 09:35:22 resultado 0 y copia autenticada/descifrada; compatible con diferida pero disparador no demostrado. Ensayo sin sesión aprobado el 8/11: intervalo manual de Santiago 16:08–16:27; tarea 16:17:52 resultado 0 y copia 16:17:53 autenticada/descifrada. No acredita disparador diario/restauración SQL de esa copia/B2. Retiro temporal realizado por Santiago y ausencia comprobada por Codex; diaria instalada con XML idéntico, intervalo de un día y próxima prevista entonces (8/11) para 9/11 a las 02:00 Córdoba.

La confirmación manual de Santiago de etapa 05 es general, sin entradas/tiempos ni detalle por caso. Historial diario habilitado el 8/11 21:58 Córdoba y XML intacto comprobados; disparador del 9/11 comprobado: 107/100/200/201/102, misma instancia, resultado 0; copia 02:00:08 autenticada/descifrada, sin restauración SQL. XML intacto y próxima 10/11 02:00 Córdoba. Evidencia en docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md. Custodia externa sólo revisada/documentada. Confirmación específica de accesibilidad del 8/11 registrada aparte; no certificación WCAG ni validación educativa. Fallos iniciales y correcciones, comandos y resultados de rendimiento en docs/evidencias/EVIDENCIA_ETAPA06.md.
