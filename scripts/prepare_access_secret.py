"""Completa clave ausente y eleva valores iniciales Argon2; no muestra secretos."""
from pathlib import Path
import re
import secrets

path = Path(__file__).resolve().parents[1] / ".env"
content = path.read_text(encoding="utf-8")
pattern = r"(?m)^CSRF_SIGNING_KEY=.*$"
match = re.search(pattern, content)
if match and match.group().split("=", 1)[1].strip():
    print("CSRF_SIGNING_KEY existente conservada.")
else:
    entry = "CSRF_SIGNING_KEY=" + secrets.token_urlsafe(48)
    content = re.sub(pattern, entry, content) if match else content + "\n" + entry + "\n"
    print("CSRF_SIGNING_KEY generada localmente; valor no mostrado.")
content = re.sub(r"(?m)^ARGON2_MEMORY_KIB=19456\s*$", "ARGON2_MEMORY_KIB=65536", content)
content = re.sub(r"(?m)^ARGON2_TIME_COST=2\s*$", "ARGON2_TIME_COST=3", content)
path.write_text(content, encoding="utf-8")
print("Valores iniciales Argon2 elevados a 65536 KiB / tiempo 3; demás valores conservados.")
