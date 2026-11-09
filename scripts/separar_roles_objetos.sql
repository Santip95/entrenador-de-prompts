-- Solo incluir desde separar_roles_locales.sql; no modifica otras bases.
BEGIN;
DO $$ DECLARE objeto record; BEGIN
 IF current_database() NOT IN ('entrenador_prompts','entrenador_prompts_test') THEN
  RAISE EXCEPTION 'Base ajena al proyecto';
 END IF;
 IF EXISTS (SELECT FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member WHERE r.rolname='entrenador_app') THEN
  RAISE EXCEPTION 'El rol de ejecucion tiene membresias inesperadas';
 END IF;
 FOR objeto IN SELECT tablename FROM pg_tables WHERE schemaname='public' AND tableowner='entrenador_app' LOOP
  IF objeto.tablename NOT IN ('usuario','sesion','recuperacion_acceso','evento_auditoria','practica','version_prompt','criterio','desafio','desafio_criterio','regla','evaluacion','resultado','alerta_sensible','alembic_version') THEN
   RAISE EXCEPTION 'Tabla inesperada: detener y revisar';
  END IF;
  EXECUTE format('ALTER TABLE public.%I OWNER TO entrenador_migracion',objeto.tablename);
 END LOOP;
 IF EXISTS (SELECT FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND pg_get_userbyid(p.proowner)='entrenador_app' AND p.proname<>'validar_estado_resultado') THEN
  RAISE EXCEPTION 'Funcion inesperada: detener y revisar';
 END IF;
END $$;
ALTER FUNCTION public.validar_estado_resultado() OWNER TO entrenador_migracion;
ALTER SCHEMA public OWNER TO entrenador_migracion;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE :DBNAME FROM PUBLIC;
REVOKE ALL ON DATABASE :DBNAME FROM entrenador_app;
GRANT CONNECT ON DATABASE :DBNAME TO entrenador_app;
GRANT USAGE ON SCHEMA public TO entrenador_app;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM entrenador_app;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO entrenador_app;
GRANT INSERT, UPDATE, DELETE ON usuario,sesion,recuperacion_acceso,evento_auditoria TO entrenador_app;
REVOKE ALL ON FUNCTION public.validar_estado_resultado() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.validar_estado_resultado() TO entrenador_app;
COMMIT;
