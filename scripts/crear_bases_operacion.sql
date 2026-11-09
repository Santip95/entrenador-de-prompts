\set ON_ERROR_STOP on
-- Ejecutar con postgres en 127.0.0.1:5432. No toca bases existentes.
SELECT 'CREATE DATABASE entrenador_prompts_ops_test OWNER entrenador_migracion'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='entrenador_prompts_ops_test') \gexec
SELECT 'CREATE DATABASE entrenador_prompts_restore_test OWNER entrenador_migracion'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='entrenador_prompts_restore_test') \gexec
SELECT 'CREATE DATABASE entrenador_prompts_contingencia_test OWNER entrenador_migracion'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='entrenador_prompts_contingencia_test') \gexec
DO $$ BEGIN
  IF EXISTS (SELECT FROM pg_database WHERE datname IN ('entrenador_prompts_ops_test','entrenador_prompts_restore_test','entrenador_prompts_contingencia_test') AND pg_get_userbyid(datdba)<>'entrenador_migracion') THEN
    RAISE EXCEPTION 'Una base aislada tiene otro propietario: detener y revisar, sin alterar sus permisos.';
  END IF;
END $$;
REVOKE ALL ON DATABASE entrenador_prompts_ops_test, entrenador_prompts_restore_test, entrenador_prompts_contingencia_test FROM PUBLIC;
REVOKE CONNECT ON DATABASE entrenador_prompts_restore_test, entrenador_prompts_contingencia_test FROM entrenador_app;
GRANT CONNECT ON DATABASE entrenador_prompts_ops_test TO entrenador_app;
-- Restauración: CONNECT de aplicación sólo se concede después de verificar el diario.
