"""Distribución oficial Windows amd64 fijada, HTTPS y SHA-256 verificados."""
from pathlib import Path
import hashlib
import io
import urllib.request
import zipfile

VERSION = "1.33.0"
SHA256 = "47122dd828ff80dcaef62b2952c478b178afadadf066c990489608e537121bfd"
URL = f"https://github.com/axllent/mailpit/releases/download/v{VERSION}/mailpit-windows-amd64.zip"


def main():
    target = Path(__file__).resolve().parents[1] / "local-data" / "mailpit"
    target.mkdir(parents=True, exist_ok=True)
    archive = urllib.request.urlopen(URL, timeout=60).read()
    if hashlib.sha256(archive).hexdigest() != SHA256:
        raise SystemExit("SHA-256 de Mailpit no coincide; descarga descartada.")
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        # Extraer sólo el ejecutable previsto, sin rutas arbitrarias del ZIP.
        (target / "mailpit.exe").write_bytes(source.read("mailpit.exe"))
    print(f"Mailpit {VERSION} instalado en local-data/mailpit; SHA-256 verificado.")


if __name__ == "__main__":
    main()
