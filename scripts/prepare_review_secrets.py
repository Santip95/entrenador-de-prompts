"""Genera sólo las claves ausentes, directamente en .env; nunca las muestra."""
from pathlib import Path
import re
import secrets
from dotenv import dotenv_values

path = Path(__file__).resolve().parents[1] / ".env"
content = path.read_text(encoding="utf-8")
values = dotenv_values(path)
for name in ("REVIEW_SIGNING_KEY", "ALERT_FINGERPRINT_KEY"):
    if values.get(name):
        continue
    entry = name + "=" + secrets.token_urlsafe(48)
    pattern = rf"(?m)^{name}=[^\r\n]*"
    content = re.sub(pattern, entry, content) if re.search(pattern, content) else content + "\n" + entry + "\n"
path.write_text(content, encoding="utf-8")
print("Claves de revisión y huellas disponibles; valores existentes conservados, valores no mostrados.")
