-- Ejecutar después de Alembic, como entrenador_migracion en cada base nueva.
-- Un único bloque transaccional. No crea roles ni cambia sus atributos.
DO $$ BEGIN
  IF current_database() NOT IN ('entrenador_prompts','entrenador_prompts_test','entrenador_prompts_demo','entrenador_prompts_ops_test','entrenador_prompts_restore_test','entrenador_prompts_contingencia_test') THEN RAISE EXCEPTION 'Destino ajeno al proyecto'; END IF;
  IF current_user<>'entrenador_migracion' OR NOT (SELECT pg_get_userbyid(datdba)=current_user FROM pg_database WHERE datname=current_database()) THEN RAISE EXCEPTION 'Requiere propietario de migraciones'; END IF;
  EXECUTE 'REVOKE CREATE ON SCHEMA public FROM PUBLIC,entrenador_app';
  EXECUTE 'GRANT USAGE ON SCHEMA public TO entrenador_app';
  EXECUTE 'GRANT SELECT ON ALL TABLES IN SCHEMA public TO entrenador_app';
  EXECUTE 'GRANT INSERT,UPDATE,DELETE ON usuario,sesion,recuperacion_acceso,evento_auditoria,limite_solicitud TO entrenador_app';
  EXECUTE 'REVOKE ALL ON FUNCTION public.validar_estado_resultado() FROM PUBLIC';
  EXECUTE 'GRANT EXECUTE ON FUNCTION public.validar_estado_resultado() TO entrenador_app';
END $$;
