"""DML mínimo de prácticas; versiones y resultados sólo INSERT/SELECT."""
from alembic import op

revision = "20261107_0003"
down_revision = "20261107_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("GRANT INSERT ON practica,version_prompt,evaluacion,resultado,alerta_sensible TO entrenador_app")
    op.execute("GRANT UPDATE(actualizado_en) ON practica TO entrenador_app")


def downgrade():
    op.execute("REVOKE INSERT ON practica,version_prompt,evaluacion,resultado,alerta_sensible FROM entrenador_app")
    op.execute("REVOKE UPDATE(actualizado_en) ON practica FROM entrenador_app")
