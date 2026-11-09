\set ON_ERROR_STOP on
-- Ejecutar como administrador en psql, nunca pasar contraseñas por argumentos.
DO $$ BEGIN
 IF current_database() <> 'postgres' OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user) THEN
  RAISE EXCEPTION 'Ejecutar como administrador conectado a postgres';
 END IF;
 IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='entrenador_app') THEN
  RAISE EXCEPTION 'Falta el rol existente del proyecto';
 END IF;
 IF EXISTS (SELECT FROM pg_roles WHERE rolname='entrenador_migracion') THEN
  RAISE EXCEPTION 'El rol de migraciones ya existe: revisar antes de repetir';
 END IF;
 IF (SELECT count(*) FROM pg_database WHERE datname IN ('entrenador_prompts','entrenador_prompts_test') AND pg_get_userbyid(datdba)='entrenador_app') <> 2 THEN
  RAISE EXCEPTION 'Las dos bases deben existir y pertenecer al rol inicial';
 END IF;
END $$;
CREATE ROLE entrenador_migracion LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
\password entrenador_migracion
ALTER DATABASE entrenador_prompts OWNER TO entrenador_migracion;
ALTER DATABASE entrenador_prompts_test OWNER TO entrenador_migracion;
\connect entrenador_prompts
\ir separar_roles_objetos.sql
\connect entrenador_prompts_test
\ir separar_roles_objetos.sql
\echo Separacion aplicada en las dos bases del proyecto. Configurar MIGRATION_PASSWORD localmente.
