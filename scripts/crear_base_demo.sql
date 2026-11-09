\set ON_ERROR_STOP on
-- Sólo la base ficticia de demostración. Conservar desarrollo y pruebas.
SELECT 'CREATE DATABASE entrenador_prompts_demo OWNER entrenador_migracion'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='entrenador_prompts_demo') \gexec
DO $$ BEGIN
  IF EXISTS(SELECT FROM pg_database WHERE datname='entrenador_prompts_demo' AND pg_get_userbyid(datdba)<>'entrenador_migracion') THEN
    RAISE EXCEPTION 'La base demo tiene otro propietario. Detener sin modificarla.';
  END IF;
END $$;
REVOKE ALL ON DATABASE entrenador_prompts_demo FROM PUBLIC;
GRANT CONNECT ON DATABASE entrenador_prompts_demo TO entrenador_app;
