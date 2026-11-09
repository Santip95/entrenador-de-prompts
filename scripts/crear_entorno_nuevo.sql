\set ON_ERROR_STOP on
-- Sólo instalación NUEVA: rechaza cualquier recurso existente, nunca reemplaza.
DO $$ BEGIN
  IF current_database()<>'postgres' OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN RAISE EXCEPTION 'Usar administrador en la base postgres'; END IF;
  IF EXISTS(SELECT FROM pg_roles WHERE rolname IN ('entrenador_app','entrenador_migracion')) OR EXISTS(SELECT FROM pg_database WHERE datname IN ('entrenador_prompts','entrenador_prompts_test')) THEN
    RAISE EXCEPTION 'Ya hay recursos del proyecto: no repetir ni reemplazar una instalación existente';
  END IF;
END $$;
CREATE ROLE entrenador_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
\password entrenador_app
CREATE ROLE entrenador_migracion LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
\password entrenador_migracion
CREATE DATABASE entrenador_prompts OWNER entrenador_migracion;
CREATE DATABASE entrenador_prompts_test OWNER entrenador_migracion;
REVOKE ALL ON DATABASE entrenador_prompts,entrenador_prompts_test FROM PUBLIC;
GRANT CONNECT ON DATABASE entrenador_prompts,entrenador_prompts_test TO entrenador_app;
\connect entrenador_prompts
ALTER SCHEMA public OWNER TO entrenador_migracion;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO entrenador_app;
\connect entrenador_prompts_test
ALTER SCHEMA public OWNER TO entrenador_migracion;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO entrenador_app;
\echo Roles separados y bases vacias creados. Configurar .env local, migrar y aplicar permisos_ejecucion_acceso.sql.
