"""Matriz reproducible: estado derivado del JUnit ejecutado, con límites explícitos."""
from datetime import datetime,timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
MAP={
 'AT-01':['test_cp12_real_v1_v2_and_history'],
 'AT-02':['test_empty_objective_never_creates_practice'],
 'AT-03':['test_free_normalization_partial_and_empty_guard','test_server_storage_is_immutable_to_runtime'],
 'AT-04':['test_guided_order_labels_and_optional_content','test_saved_results_match_unchanged_fixture'],
 'AT-05':['test_free_normalization_partial_and_empty_guard','test_normalization_preserves_free_text'],
 'AT-06':['test_empty_draft_not_saveable_but_partial_missing_task_is','test_free_normalization_partial_and_empty_guard'],
 'AT-07':['test_int05_complete_objective_confirmation_delete_backup_restore','test_alerts_confirmation_and_safe_storage'],
 'AT-08':['test_sec13_14_stale_review_never_writes'],
 'AT-09':['test_alerts_confirmation_and_safe_storage','test_evidence_and_matches_do_not_echo_sensitive_fragments'],
 'AT-10':['test_repeatable_without_mutating_inputs','test_evaluate_works_when_io_is_forbidden'],
 'AT-11':['test_saved_results_match_unchanged_fixture','test_non_applicable_text_still_scanned'],
 'AT-12':['test_missing_active_rule_blocks_evaluation_without_partial_persistence','test_invalid_configuration_fails_closed'],
 'AT-13':['test_saved_results_match_unchanged_fixture'],
 'AT-14':['test_fixture[CP-25]','test_fixture[CP-27]','test_fixture[CP-28]'],
 'AT-15':['test_cp12_real_v1_v2_and_history'],
 'AT-16':['test_concurrent_versions_numbering_and_retries','test_concurrent_creation_idempotent','test_idempotency_lost_responses_and_conflicts'],
 'AT-17':['test_cp12_real_v1_v2_and_history'],
 'AT-18':['test_at23_int03_publish_preserves_snapshot_and_stales_review'],
 'AT-19':['test_031_register_duplicate_and_forbid_role','test_argon2_id_parameters_and_unique_salt'],
 'AT-20':['test_032_generic_login_and_dummy_verification'],
 'AT-21':['test_history_cursor_filters_and_progress_pagination','test_sec07_all_derived_resources_enforce_owner'],
 'AT-22':['test_sec12_15_16_new_alert_and_key_rotation','test_history_cursor_filters_and_progress_pagination'],
 'AT-23':['test_at23_int03_publish_preserves_snapshot_and_stales_review'],
 'AT-24':['test_at24_inactive_challenge_history_read_and_no_new_versions','test_draft_publish_edit_revision_and_no_destructive_routes'],
 'AT-25':['test_at25_concurrent_publication_one_winner','test_published_challenge_edit_rolls_back_all_six_criteria'],
 'SEC-01':['test_sec01_two_independent_sessions_admin_block_and_unblock'],
 'SEC-02':['test_account_block_serializes_real_version_save','test_sec02_write_serializes_before_restriction'],
 'SEC-03':['test_sec03_registration_boundaries','test_sec03_password_not_trimmed','test_sec03_lengths'],
 'SEC-04':['test_sec04_five_failures_revoke_and_timeout_does_not_revive','test_sec04_ip_limit_shared_between_service_instances'],
 'SEC-05':['test_sec05_server_expirations_and_deleted_cookie','test_sec05_logout_rotates_and_revokes_only_current','test_cookie_flags_rotation_and_hash_only'],
 'SEC-06':['test_sec06_smtp_reset_single_use_and_global_revocation','test_sec06_reset_negative_cases','test_sec06_two_consumers_exactly_one_commits'],
 'SEC-07':['test_sec07_all_derived_resources_enforce_owner','test_own_delete_cascade_retry_other_practice_and_foreign_admin'],
 'SEC-08':['test_sec08_csrf_and_origin','test_review_errors_csrf_and_sensitive_text_are_safe'],
 'SEC-09':['test_sec09_password_change_revokes_sessions_and_reset_tokens','test_sec09_role_changes_are_read_server_side','test_real_encrypted_restore_completed_pending_deletions_and_contingency'],
 'SEC-10':['test_int04_failure_rolls_back_all_rows'],
 'SEC-11':['test_real_encrypted_restore_completed_pending_deletions_and_contingency','test_int05_complete_objective_confirmation_delete_backup_restore','test_journal_failure_blocks_delete_and_pending_retry','test_pending_journal_survives_sql_rollback_and_retry'],
 'SEC-12':['test_non_applicable_text_still_scanned','test_objective_review_and_later_evaluation'],
 'SEC-13':['test_sec13_14_stale_review_never_writes','test_foreign_token_cannot_be_reused_even_with_owned_destination'],
 'SEC-14':['test_sec14_real_publisher_waits_for_save_and_rejects_old_review'],
 'SEC-15':['test_sec12_15_16_new_alert_and_key_rotation'],
 'SEC-16':['test_sec12_15_16_new_alert_and_key_rotation'],
 'SEC-17':['test_sec17_errors_never_echo_sensitive_body','test_review_errors_csrf_and_sensitive_text_are_safe'],
 'NF-04':['test_fixture','test_real_encrypted_restore_completed_pending_deletions_and_contingency','test_cp12_real_v1_v2_and_history'],
 'OPS-01':['test_real_encrypted_restore_completed_pending_deletions_and_contingency'],
 'OPS-02':['test_real_encrypted_restore_completed_pending_deletions_and_contingency'],
 'OPS-03':['test_actual_local_purge_preserves_unknown_files_and_exact_retention','test_cloud_plan_versions_hidden_files_and_abandoned_uploads'],
 'CP-12':['test_cp12_real_v1_v2_and_history'],
 'INT-02':['test_sec01_two_independent_sessions_admin_block_and_unblock'],
 'INT-03':['test_at23_int03_publish_preserves_snapshot_and_stales_review'],
 'INT-04':['test_int04_failure_rolls_back_all_rows'],
 'INT-05':['test_int05_complete_objective_confirmation_delete_backup_restore'],
}

def main():
    source=ROOT/'local-data/detector-numerico-regresion-final.xml'
    if not source.exists():source=ROOT/'local-data/etapa06-regresion.xml'
    tree=ET.parse(source)
    cases=tree.findall('.//testcase');rows=[]
    def state(case):
        return 'fallido' if case.find('failure') is not None or case.find('error') is not None else 'pendiente' if case.find('skipped') is not None else 'aprobado'
    for identifier,patterns in MAP.items():
        found=[case for case in cases if any(case.get('name','').startswith(p) for p in patterns)]
        missing=[p for p in patterns if not any(case.get('name','').startswith(p) for case in cases)]
        status='pendiente' if missing else 'fallido' if any(state(c)=='fallido' for c in found) else 'parcialmente comprobado' if any(state(c)=='pendiente' for c in found) else 'aprobado'
        detail='PostgreSQL real cuando corresponde; motor puro para estados/normalización.'
        if identifier.startswith('OPS-'):
            status='parcialmente comprobado' if status=='aprobado' else status
            detail='Tramo local aprobado, incluido disparo por horario del 9/11 (docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md); proveedor externo, custodia offline y continuidad operativa pendientes.'
        if identifier=='AT-13':detail+=' Estructura/textos renderizados probados; comprensión educativa no acreditada.'
        rows.append({'id':identifier,'estado':status,'pruebas':[c.get('classname')+'::'+c.get('name') for c in found],'patrones_no_ejecutados':missing,'alcance':detail})
    performance=sorted((ROOT/'local-data/etapa06').glob('rendimiento-*.json'))
    measured=[(p,json.loads(p.read_text())) for p in performance]
    latest=next(((p,d) for p,d in reversed(measured) if 'guardar' in d),None)
    rows.extend([
        {'id':'NF-01','estado':'aprobado','pruebas':['scripts/verify_stage06_browsers.py','docs/evidencias/EVIDENCIA_ETAPA06.md, confirmación manual 8/11/2026'],'alcance':'49 instantáneas AX/DOM y revisión manual de Santiago: teclado, foco, confirmaciones, etiquetas, errores, 360 px, zoom y Narrador en Chrome/Edge. Incidencia inicial en Edge; repetición correcta en ventana nueva sin cambios. Accesibilidad básica, sin certificación WCAG.'},
        {'id':'NF-02','estado':'pendiente','pruebas':['scripts/stage06_browser_audit.py','docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md'],'alcance':'No aprobado: registro histórico de POST externo con dos coincidencias texto 45/34, sin ruta/campo remoto/acción registrados. Repetición acotada CP-31 en Chrome/Edge el 8/11 sin coincidencias externas; textos y marcador sólo en revisión local. No reconstruye ni refuta el evento histórico. Firma/ruta física/tratamiento pendientes, antivirus sin cambios.'},
        {'id':'NF-03','estado':'aprobado' if latest and latest[1].get('aprobado') else 'fallido','pruebas':[str(latest[0].relative_to(ROOT))] if latest else [],'alcance':'Medición del 7/11 con motor 1.0.0, no repetida en esta lectura ni tras D36: 100 revisar + 100 guardar, cinco usuarios, 10 warmup/endpoint, texto libre 10000, p95 rango más cercano; todas las muestras/errores conservados.'},
        {'id':'VAL-01','estado':'pendiente','pruebas':[],'alcance':'No hay dictamen externo. Obligatorio antes de pruebas educativas.'},
        {'id':'VAL-02','estado':'pendiente','pruebas':[],'alcance':'No se reclutaron participantes ni se inventaron resultados.'},
    ])
    fixture=json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']
    for c in fixture:
        name='test_fixture['+c['id']+']';executed=next((t for t in cases if t.get('name')==name),None)
        rows.append({'id':c['id'],'estado':state(executed) if executed is not None else 'pendiente','pruebas':[name],'alcance':'Esperado original sin modificar; configuración histórica C6 v1. Motor '+('1.1.0' if 'detector-numerico' in source.name else '1.0.0')+'.'})
    report={'fecha_utc':datetime.now(timezone.utc).isoformat(),'codigo_base':'f109b21 + incremento identificado por el commit que contiene este informe','entorno':'Windows PowerShell, PostgreSQL 18.6, .venv Python 3.11.4; sin despliegue','junit':str(source.relative_to(ROOT)),'pruebas':len(cases),'fallidas':sum(state(c)=='fallido' for c in cases),'omitidas':sum(state(c)=='pendiente' for c in cases),'casos':rows,'cierre_integral_local':False,'bloqueos':['NF-02 no aprobado'],'disparador_diario_20261109':{'comprobado':True,'eventos':[107,100,200,201,102],'resultado':0,'xml_identico':True,'restauracion_sql_copia':False,'b2_probado':False,'evidencia':'docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md'}}
    (ROOT/'local-data/etapa06/matriz.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Informe final de verificación — etapa 06','','Código base `f109b21`; versión final: commit que contiene este informe. Fecha inicial 7/11/2026; actualización operativa 9/11/2026. Windows nativo, PostgreSQL real y datos ficticios. Fuente de regresión: `'+str(source.relative_to(ROOT))+'` (ejecución previa, no repetida al leer eventos); auditorías/mediciones en `local-data/etapa06/`.','','**No se declara cierre integral:** NF-02 no está aprobado. NF-01 básico confirmado manualmente por Santiago el 8/11/2026, incluida repetición de Narrador en Edge. Esto no se oculta bajo las pruebas funcionales aprobadas. Disparo diario del 9/11 comprobado; continuidad, operación externa y validación educativa se distinguen del ensayo local.','','| ID | Estado | Evidencia ejecutada y alcance |','|---|---|---|']
    for row in rows:
        tests=', '.join('`'+t.split('::')[-1]+'`' for t in row['pruebas'][:3])
        if len(row['pruebas'])>3:tests+=' y '+str(len(row['pruebas'])-3)+' casos parametrizados más (JUnit/JSON).'
        lines.append('| '+row['id']+' | '+row['estado']+' | '+tests+' '+row['alcance']+' |')
    lines.extend(['','Estados de OPS son parciales por los tramos externos: restore/diario/contingencia/purga local aprobados; B2 y custodia/transferencia externas no ejecutados. Tarea instalada por Santiago y ejecución por Start-ScheduledTask observada con resultado 0, ejecución del 8/11 a las 09:35:22 resultado 0 y copia autenticada/descifrada; compatible con diferida pero disparador no demostrado. Ensayo sin sesión aprobado el 8/11: intervalo manual de Santiago 16:08–16:27; tarea 16:17:52 resultado 0 y copia 16:17:53 autenticada/descifrada. No acredita disparador diario/restauración SQL de esa copia/B2. Retiro temporal realizado por Santiago y ausencia comprobada por Codex; diaria instalada con XML idéntico, intervalo de un día y próxima prevista entonces (8/11) para 9/11 a las 02:00 Córdoba.','', 'La confirmación manual de Santiago de etapa 05 es general, sin entradas/tiempos ni detalle por caso. Historial diario habilitado el 8/11 21:58 Córdoba y XML intacto comprobados; disparador del 9/11 comprobado: 107/100/200/201/102, misma instancia, resultado 0; copia 02:00:08 autenticada/descifrada, sin restauración SQL. XML intacto y próxima 10/11 02:00 Córdoba. Evidencia en docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md. Custodia externa sólo revisada/documentada. Confirmación específica de accesibilidad del 8/11 registrada aparte; no certificación WCAG ni validación educativa. Fallos iniciales y correcciones, comandos y resultados de rendimiento en docs/evidencias/EVIDENCIA_ETAPA06.md.'])
    (ROOT/'docs/evidencias/INFORME_FINAL_ETAPA06.md').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
    print('Matriz generada:',len(rows),'casos; JUnit:',len(cases),'pruebas; patrones sin ejecución:',sum(bool(r.get('patrones_no_ejecutados')) for r in rows))

if __name__=='__main__':main()
