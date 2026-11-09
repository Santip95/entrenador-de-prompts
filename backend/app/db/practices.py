"""Consultas parametrizadas de prácticas, separadas de aplicación y motor."""
from sqlalchemy import text


QUERIES = {'catalog_reloj_bloqueo': 'SELECT pg_advisory_xact_lock_shared(:key)',
 'catalog_criterio': 'SELECT id,codigo,nombre,descripcion FROM criterio ORDER BY codigo',
 'catalog_regla': 'SELECT r.id,c.codigo AS criterio_codigo,r.tipo,r.parametros,r.mensajes,r.version,r.activa '
                  'FROM regla r JOIN criterio c ON c.id=r.criterio_id ORDER BY c.codigo,r.version',
 'catalog_desafio': 'SELECT id,codigo,titulo,consigna,estado,revision FROM desafio WHERE id=:id',
 'catalog_desafio_criterio': 'SELECT c.codigo,dc.configuracion,dc.obligatorio FROM desafio_criterio dc JOIN '
                             'criterio c ON c.id=dc.criterio_id WHERE dc.desafio_id=:id',
 'issue_reloj_bloqueo': 'SELECT clock_timestamp()',
 'create_practica': 'INSERT INTO '
                    'practica(id,usuario_id,desafio_id,objetivo,modo,configuracion_propia,request_id,entrada_hash,revision_inicio) '
                    'VALUES (:id,:uid,:challenge,:objective,:mode,CAST(:config AS '
                    'jsonb),:rid,:hash,CAST(:review AS jsonb))',
 'create_practica_2': 'SELECT id FROM practica WHERE id=:id',
 'create_practica_3': 'SELECT id,entrada_hash FROM practica WHERE usuario_id=:uid AND request_id=:rid',
 'save_practica': 'SELECT id FROM practica WHERE id=:id FOR UPDATE',
 'save_version_prompt': 'INSERT INTO '
                        'version_prompt(id,practica_id,numero,componentes,texto,componentes_confirmados,request_id,contenido_hash) '
                        'VALUES (:id,:pid,:n,CAST(:components AS jsonb),:text,:confirmed,:rid,:hash)',
 'save_evaluacion': 'INSERT INTO '
                    'evaluacion(id,version_id,snapshot,firma_comparacion,motor_version,cumplidos,aplicables) '
                    'VALUES (:id,:vid,CAST(:snapshot AS jsonb),:signature,:motor,:k,:a)',
 'save_practica_2': 'UPDATE practica SET actualizado_en=clock_timestamp() WHERE id=:id',
 'save_resultado': 'INSERT INTO '
                   'resultado(evaluacion_id,criterio_id,regla_id,estado,evidencia,condicion_esperada,mensaje,accion_sugerida) '
                   'VALUES (:eid,:cid,:rid,:state,CAST(:evidence AS jsonb),:condition,:message,:action)',
 'save_alerta_sensible': 'INSERT INTO '
                         'alerta_sensible(id,version_id,tipo,campo,huella,clave_version,ordinal,confirmado_en) '
                         'VALUES (:id,:vid,:type,:field,:hash,:key,:ordinal,clock_timestamp())',
 'save_version_prompt_2': 'SELECT COALESCE(max(numero),0)+1 FROM version_prompt WHERE practica_id=:id',
 'save_criterio': 'SELECT id FROM criterio WHERE codigo=:code',
 'save_version_prompt_3': 'SELECT id,contenido_hash FROM version_prompt WHERE practica_id=:id AND '
                          'request_id=:rid',
 'historical_alerta_sensible': 'SELECT * FROM alerta_sensible WHERE version_id=:id ORDER BY ordinal',
 'historical_evaluacion': 'SELECT * FROM evaluacion WHERE version_id=:id',
 'historical_resultado': 'SELECT c.codigo AS '
                         'criterio_codigo,r.estado,r.evidencia,r.condicion_esperada,r.mensaje,r.accion_sugerida,r.regla_id '
                         'FROM resultado r JOIN criterio c ON c.id=r.criterio_id WHERE r.evaluacion_id=:id '
                         'ORDER BY c.codigo',
 'history_practica': 'SELECT '
                     "p.id,p.modo,p.objetivo,p.desafio_id,p.actualizado_en,COALESCE(d.titulo,'Objetivo "
                     "propio') AS titulo,\n"
                     '          v.id AS version_id,v.numero,e.cumplidos,e.aplicables FROM practica p LEFT '
                     'JOIN desafio d ON d.id=p.desafio_id\n'
                     '          LEFT JOIN LATERAL (SELECT id,numero FROM version_prompt WHERE '
                     'practica_id=p.id ORDER BY numero DESC LIMIT 1) v ON true\n'
                     '          LEFT JOIN evaluacion e ON e.version_id=v.id WHERE p.usuario_id=:uid\n'
                     '          AND (CAST(:start AS timestamptz) IS NULL OR p.actualizado_en>=:start) AND '
                     '(CAST(:end AS timestamptz) IS NULL OR p.actualizado_en<:end)\n'
                     '          AND (CAST(:challenge AS uuid) IS NULL OR p.desafio_id=CAST(:challenge AS '
                     'uuid))\n'
                     '          AND (CAST(:anchor AS uuid) IS NULL OR (p.actualizado_en,p.id)<(CAST(:time AS '
                     'timestamptz),CAST(:anchor AS uuid)))\n'
                     '          ORDER BY p.actualizado_en DESC,p.id DESC LIMIT :limit',
 'versions_version_prompt': 'SELECT id FROM version_prompt WHERE practica_id=:id AND numero>:n ORDER BY '
                            'numero LIMIT :limit',
 'progress_version_prompt': 'SELECT '
                            'v.id,v.practica_id,v.numero,v.creado_en,e.firma_comparacion,e.cumplidos,e.aplicables '
                            'FROM version_prompt v JOIN practica p ON p.id=v.practica_id JOIN evaluacion e '
                            'ON e.version_id=v.id\n'
                            '          WHERE p.usuario_id=:uid AND (CAST(:start AS timestamptz) IS NULL OR '
                            'v.creado_en>=:start) AND (CAST(:end AS timestamptz) IS NULL OR '
                            'v.creado_en<:end)\n'
                            '          AND (CAST(:cursor AS uuid) IS NULL OR (v.creado_en,v.id)>(CAST(:time '
                            'AS timestamptz),CAST(:cursor AS uuid))) ORDER BY v.creado_en,v.id LIMIT :limit',
 'challenges_desafio': "SELECT id FROM desafio WHERE estado='publicado' AND (CAST(:cursor AS uuid) IS NULL "
                       'OR id>CAST(:cursor AS uuid)) ORDER BY id LIMIT :limit'}


def sql(connection, name, **values):
    return connection.execute(text(QUERIES[name]), values)
