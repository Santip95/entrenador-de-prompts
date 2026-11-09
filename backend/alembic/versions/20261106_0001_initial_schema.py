"""Esquema inicial inmutable del entrenador.

Revision ID: 20261106_0001
Revises:
Create Date: 2026-11-06 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20261106_0001"
down_revision = None
branch_labels = None
depends_on = None


UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB()


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("clave_hash", sa.Text(), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False, server_default="usuario"),
        sa.Column("estado", sa.String(20), nullable=False, server_default="activo"),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True)),
        sa.Column("fallos_login", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ventana_fallos_desde", sa.DateTime(timezone=True)),
        sa.Column("auth_epoch", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.CheckConstraint("rol IN ('usuario', 'administrador')", name="ck_usuario_rol"),
        sa.CheckConstraint("estado IN ('activo', 'bloqueado', 'desactivado')", name="ck_usuario_estado"),
        sa.CheckConstraint("fallos_login >= 0", name="ck_usuario_fallos_login"),
        sa.CheckConstraint("auth_epoch >= 0", name="ck_usuario_auth_epoch"),
        sa.UniqueConstraint("correo", name="uq_usuario_correo"),
    )
    op.create_table(
        "criterio",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("codigo", sa.String(2), nullable=False),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.CheckConstraint("codigo IN ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')", name="ck_criterio_codigo"),
        sa.UniqueConstraint("codigo", name="uq_criterio_codigo"),
    )
    op.create_table(
        "desafio",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("titulo", sa.String(250), nullable=False),
        sa.Column("consigna", sa.Text(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="borrador"),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.CheckConstraint("estado IN ('borrador', 'publicado', 'inactivo')", name="ck_desafio_estado"),
        sa.CheckConstraint("revision >= 1", name="ck_desafio_revision"),
        sa.CheckConstraint(
            "(estado = 'publicado' AND activo) OR (estado <> 'publicado' AND NOT activo)",
            name="ck_desafio_estado_activo",
        ),
        sa.UniqueConstraint("codigo", name="uq_desafio_codigo"),
    )
    op.create_table(
        "practica",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("usuario_id", UUID, nullable=False),
        sa.Column("desafio_id", UUID),
        sa.Column("objetivo", sa.Text()),
        sa.Column("modo", sa.String(10), nullable=False),
        sa.Column("configuracion_propia", JSONB),
        sa.Column("request_id", UUID, nullable=False),
        sa.Column("entrada_hash", sa.String(64), nullable=False),
        sa.Column("revision_inicio", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["desafio_id"], ["desafio.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("modo IN ('guiado', 'libre')", name="ck_practica_modo"),
        sa.CheckConstraint(
            "(desafio_id IS NOT NULL AND objetivo IS NULL AND configuracion_propia IS NULL) "
            "OR (desafio_id IS NULL AND objetivo IS NOT NULL AND btrim(objetivo) <> '' AND configuracion_propia IS NOT NULL)",
            name="ck_practica_origen",
        ),
        sa.UniqueConstraint("usuario_id", "request_id", name="uq_practica_usuario_request"),
    )
    op.create_table(
        "version_prompt",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("practica_id", UUID, nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("componentes", JSONB, nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("componentes_confirmados", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("request_id", UUID, nullable=False),
        sa.Column("contenido_hash", sa.String(64), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["practica_id"], ["practica.id"], ondelete="CASCADE"),
        sa.CheckConstraint("numero >= 1", name="ck_version_prompt_numero"),
        sa.UniqueConstraint("practica_id", "numero", name="uq_version_prompt_numero"),
        sa.UniqueConstraint("practica_id", "request_id", name="uq_version_prompt_request"),
    )
    op.create_table(
        "desafio_criterio",
        sa.Column("desafio_id", UUID, primary_key=True),
        sa.Column("criterio_id", UUID, primary_key=True),
        sa.Column("obligatorio", sa.Boolean(), nullable=False),
        sa.Column("configuracion", JSONB, nullable=False),
        sa.ForeignKeyConstraint(["desafio_id"], ["desafio.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["criterio_id"], ["criterio.id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "regla",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("criterio_id", UUID, nullable=False),
        sa.Column("tipo", sa.String(100), nullable=False),
        sa.Column("parametros", JSONB, nullable=False),
        sa.Column("mensajes", JSONB, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("creada_por", UUID),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["criterio_id"], ["criterio.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["creada_por"], ["usuario.id"], ondelete="SET NULL"),
        sa.CheckConstraint("version >= 1", name="ck_regla_version"),
        sa.CheckConstraint(
            "tipo IN ('tarea_declarada', 'contexto_requerido', 'destinatario_declarado', "
            "'restricciones_declaradas', 'formato_declarado', 'revision_preventiva')",
            name="ck_regla_tipo",
        ),
        sa.UniqueConstraint("criterio_id", "version", name="uq_regla_criterio_version"),
        sa.UniqueConstraint("id", "criterio_id", name="uq_regla_id_criterio"),
    )
    op.create_index(
        "uq_regla_activa_por_criterio",
        "regla",
        ["criterio_id"],
        unique=True,
        postgresql_where=sa.text("activa"),
    )
    op.create_table(
        "evaluacion",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("version_id", UUID, nullable=False),
        sa.Column("snapshot", JSONB, nullable=False),
        sa.Column("firma_comparacion", sa.String(128), nullable=False),
        sa.Column("motor_version", sa.String(50), nullable=False),
        sa.Column("cumplidos", sa.Integer(), nullable=False),
        sa.Column("aplicables", sa.Integer(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["version_id"], ["version_prompt.id"], ondelete="CASCADE"),
        sa.CheckConstraint("cumplidos >= 0 AND aplicables >= 0 AND cumplidos <= aplicables AND aplicables <= 6", name="ck_evaluacion_conteos"),
        sa.UniqueConstraint("version_id", name="uq_evaluacion_version"),
    )
    op.create_table(
        "resultado",
        sa.Column("evaluacion_id", UUID, primary_key=True),
        sa.Column("criterio_id", UUID, primary_key=True),
        sa.Column("regla_id", UUID),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("evidencia", JSONB, nullable=False),
        sa.Column("condicion_esperada", sa.Text(), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("accion_sugerida", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["evaluacion_id"], ["evaluacion.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["criterio_id"], ["criterio.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["regla_id", "criterio_id"], ["regla.id", "regla.criterio_id"], name="fk_resultado_regla_criterio"
        ),
        sa.CheckConstraint("estado IN ('cumple', 'revisar', 'no_aplica', 'advertencia')", name="ck_resultado_estado"),
        sa.CheckConstraint("(regla_id IS NULL) = (estado = 'no_aplica')", name="ck_resultado_regla_aplicabilidad"),
    )
    op.create_table(
        "alerta_sensible",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("version_id", UUID, nullable=False),
        sa.Column("tipo", sa.String(100), nullable=False),
        sa.Column("campo", sa.String(300), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="confirmada"),
        sa.Column("huella", sa.String(128), nullable=False),
        sa.Column("clave_version", sa.Integer(), nullable=False),
        sa.Column("ordinal", sa.Integer(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("confirmado_en", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["version_id"], ["version_prompt.id"], ondelete="CASCADE"),
        sa.CheckConstraint("estado = 'confirmada'", name="ck_alerta_sensible_estado"),
        sa.CheckConstraint("clave_version >= 1 AND ordinal >= 1", name="ck_alerta_sensible_ordinal"),
    )
    op.create_table(
        "sesion",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("usuario_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("auth_epoch_emitido", sa.Integer(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("ultimo_uso_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocada_en", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.CheckConstraint("auth_epoch_emitido >= 0", name="ck_sesion_auth_epoch"),
        sa.UniqueConstraint("token_hash", name="uq_sesion_token_hash"),
    )
    op.create_table(
        "recuperacion_acceso",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("usuario_id", UUID, nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado_en", sa.DateTime(timezone=True)),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_hash", name="uq_recuperacion_acceso_token_hash"),
    )
    op.create_table(
        "evento_auditoria",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("actor_id", UUID),
        sa.Column("evento", sa.String(100), nullable=False),
        sa.Column("recurso_tipo", sa.String(100), nullable=False),
        sa.Column("recurso_id", UUID),
        sa.Column("metadatos", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["usuario.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_practica_usuario_actualizado", "practica", ["usuario_id", "actualizado_en"])
    op.create_index("ix_version_prompt_practica_numero", "version_prompt", ["practica_id", "numero"])
    op.create_index("ix_evaluacion_version", "evaluacion", ["version_id"])
    op.create_index("ix_resultado_criterio", "resultado", ["criterio_id"])
    op.create_index("ix_alerta_sensible_version", "alerta_sensible", ["version_id"])
    op.create_index("ix_sesion_usuario_revocada", "sesion", ["usuario_id", "revocada_en"])
    op.create_index("ix_recuperacion_acceso_usuario", "recuperacion_acceso", ["usuario_id"])
    op.create_index("ix_evento_auditoria_creado", "evento_auditoria", ["creado_en"])

    op.execute("""
        CREATE FUNCTION validar_estado_resultado() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE codigo_criterio text;
        BEGIN
            SELECT codigo INTO codigo_criterio FROM criterio WHERE id = NEW.criterio_id;
            IF (NEW.estado = 'advertencia' AND codigo_criterio <> 'C6')
               OR (NEW.estado = 'no_aplica' AND codigo_criterio NOT IN ('C2', 'C3', 'C4')) THEN
                RAISE EXCEPTION 'Estado no permitido para el criterio' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_resultado_estado BEFORE INSERT OR UPDATE ON resultado
        FOR EACH ROW EXECUTE FUNCTION validar_estado_resultado();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER tr_resultado_estado ON resultado")
    op.execute("DROP FUNCTION validar_estado_resultado()")
    op.drop_index("ix_evento_auditoria_creado", table_name="evento_auditoria")
    op.drop_index("ix_recuperacion_acceso_usuario", table_name="recuperacion_acceso")
    op.drop_index("ix_sesion_usuario_revocada", table_name="sesion")
    op.drop_index("ix_alerta_sensible_version", table_name="alerta_sensible")
    op.drop_index("ix_resultado_criterio", table_name="resultado")
    op.drop_index("ix_evaluacion_version", table_name="evaluacion")
    op.drop_index("ix_version_prompt_practica_numero", table_name="version_prompt")
    op.drop_index("ix_practica_usuario_actualizado", table_name="practica")
    op.drop_table("evento_auditoria")
    op.drop_table("recuperacion_acceso")
    op.drop_table("sesion")
    op.drop_table("alerta_sensible")
    op.drop_table("resultado")
    op.drop_table("evaluacion")
    op.drop_index("uq_regla_activa_por_criterio", table_name="regla")
    op.drop_table("regla")
    op.drop_table("desafio_criterio")
    op.drop_table("version_prompt")
    op.drop_table("practica")
    op.drop_table("desafio")
    op.drop_table("criterio")
    op.drop_table("usuario")
