"""Límite compartido entre workers y permisos de ejecución de acceso."""
from alembic import op
import sqlalchemy as sa

revision = "20261107_0002"
down_revision = "20261106_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("limite_solicitud",
                    sa.Column("clave", sa.String(128), primary_key=True),
                    sa.Column("desde", sa.DateTime(timezone=True), nullable=False),
                    sa.Column("cantidad", sa.Integer(), nullable=False))
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON limite_solicitud TO entrenador_app")


def downgrade():
    op.drop_table("limite_solicitud")
