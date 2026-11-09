"""Permisos de administración y borrado por raíz; historia sin UPDATE/DELETE directo."""
from alembic import op
revision='20261107_0004'
down_revision='20261107_0003'
branch_labels=None
depends_on=None

def upgrade():
    op.execute('GRANT INSERT,UPDATE ON desafio,desafio_criterio TO entrenador_app')
    op.execute('GRANT DELETE ON desafio_criterio TO entrenador_app')
    op.execute('GRANT UPDATE(nombre,descripcion,actualizado_en) ON criterio TO entrenador_app')
    op.execute('GRANT INSERT ON regla TO entrenador_app')
    op.execute('GRANT UPDATE(activa) ON regla TO entrenador_app')
    op.execute('GRANT DELETE ON practica,usuario TO entrenador_app')

def downgrade():
    op.execute('REVOKE INSERT,UPDATE ON desafio,desafio_criterio FROM entrenador_app')
    op.execute('REVOKE DELETE ON desafio_criterio FROM entrenador_app')
    op.execute('REVOKE UPDATE(nombre,descripcion,actualizado_en) ON criterio FROM entrenador_app')
    op.execute('REVOKE INSERT ON regla FROM entrenador_app')
    op.execute('REVOKE UPDATE(activa) ON regla FROM entrenador_app')
    op.execute('REVOKE DELETE ON practica,usuario FROM entrenador_app')
