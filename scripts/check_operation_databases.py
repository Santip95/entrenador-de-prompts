import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from sqlalchemy import create_engine,text
from app.core.config import Settings
s=Settings()
e=create_engine(s.resolved_migration_url(),hide_parameters=True)
with e.connect() as c:
    rows=c.execute(text("SELECT datname,pg_get_userbyid(datdba) AS propietario FROM pg_database WHERE datname LIKE 'entrenador_prompts%' ORDER BY datname")).mappings().all()
    for row in rows: print(dict(row))
e.dispose()
