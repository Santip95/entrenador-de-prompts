"""Distribución oficial Windows, versión y SHA-256 fijados. Sin cambios globales."""
from pathlib import Path
from urllib.request import urlopen
import hashlib
import io
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.3.2'
SHA256 = 'f48d8f8f9ebe903ab5027ed067652f2cc1db94bc206976430133b905dcd8e8c7'

def main():
    target = ROOT / 'local-data/age'
    if (target / 'age.exe').exists() and (target / 'age-keygen.exe').exists():
        print('age ya está disponible; no se reemplaza.')
        return
    data = urlopen(f'https://github.com/FiloSottile/age/releases/download/v{VERSION}/age-v{VERSION}-windows-amd64.zip', timeout=120).read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise SystemExit('SHA-256 de age incorrecto; no se instala.')
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in ('age.exe', 'age-keygen.exe'):
            member = next(n for n in archive.namelist() if n.endswith('/'+name))
            (target/name).write_bytes(archive.read(member))
    print('age 1.3.2 oficial instalado y SHA-256 verificado.')

if __name__ == '__main__':
    main()
