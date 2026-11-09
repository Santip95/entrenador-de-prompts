"""Actualiza pip en .venv mediante HTTPS y la confianza nativa de Windows."""

import hashlib
import json
from pathlib import Path
import ssl
import subprocess
import sys
from urllib.request import urlopen


def main() -> None:
    context = ssl.create_default_context()
    with urlopen("https://pypi.org/pypi/pip/26.3/json", context=context) as response:
        metadata = json.load(response)
    wheel = next(item for item in metadata["urls"] if item["filename"].endswith(".whl"))
    with urlopen(wheel["url"], context=context) as response:
        content = response.read()
    if hashlib.sha256(content).hexdigest() != wheel["digests"]["sha256"]:
        raise SystemExit("El hash del paquete pip no coincide con PyPI.")
    target = Path(__file__).resolve().parents[1] / "local-data" / wheel["filename"]
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(content)
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-index", str(target)], check=True)


if __name__ == "__main__":
    main()
