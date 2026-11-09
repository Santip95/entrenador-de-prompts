-- Ejecutar localmente con psql --file; nunca contiene contraseñas.
-- Si existen recursos con estos nombres, detenerse y revisar su origen.
\set ON_ERROR_STOP on
DO $$
BEGIN
    IF current_setting('server_version_num')::integer / 10000 <> 18 THEN
        RAISE EXCEPTION 'Se esperaba PostgreSQL 18; no se crearon recursos';
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'entrenador_app')
       OR EXISTS (SELECT 1 FROM pg_database WHERE datname IN ('entrenador_prompts', 'entrenador_prompts_test')) THEN
        RAISE EXCEPTION 'Ya existen recursos del proyecto: revisar antes de continuar; no se modificaron';
    END IF;
END $$;
CREATE ROLE entrenador_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION;
\password entrenador_app
CREATE DATABASE entrenador_prompts OWNER entrenador_app;
CREATE DATABASE entrenador_prompts_test OWNER entrenador_app;
\echo Recursos creados. Completar POSTGRES_PASSWORD en .env con la clave elegida.
