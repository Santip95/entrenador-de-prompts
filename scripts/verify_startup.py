"""Comprueba arranque/reinicio local; nunca imprime la configuración secreta."""

import json
from pathlib import Path
import subprocess
import sys
import time
import os
import socket
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


def wait_http(url, process):
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError("El servidor terminó antes de responder; revisar logs locales.")
        try:
            with urlopen(url, timeout=1) as response:
                return response.status, response.read().decode("utf-8")
        except (URLError, TimeoutError):
            time.sleep(0.1)
    raise RuntimeError("El servidor no respondió dentro del plazo.")


def counts():
    sys.path.insert(0, str(ROOT / "backend"))
    from app.db.session import build_engine
    from sqlalchemy import text

    engine = build_engine()
    with engine.connect() as connection:
        result = dict(connection.execute(text(
            "SELECT (SELECT count(*) FROM criterio) AS criterios, "
            "(SELECT count(*) FROM regla) AS reglas, "
            "(SELECT count(*) FROM desafio) AS desafios, "
            "(SELECT count(*) FROM desafio_criterio) AS relaciones"
        )).mappings().one())
    engine.dispose()
    return result


def main():
    for port in (8000,5173):
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1',port))==0:
                raise SystemExit('Puertos de desarrollo ocupados: cerrar primero tus servidores. No se detienen procesos ajenos ni se acredita su arranque.')
    sys.path.insert(0,str(ROOT/'backend'))
    from app.core.config import Settings
    variables=os.environ.copy()
    for name,field in Settings.model_fields.items():
        variables.pop(str(field.validation_alias or name.upper()),None)
    variables.pop('TFG_API_PROXY_TARGET',None)
    logs = ROOT / "local-data"
    logs.mkdir(exist_ok=True)
    before = counts()
    for attempt in (1, 2):
        with (logs / f"startup-{attempt}.log").open("w", encoding="utf-8") as log:
            api = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--no-access-log", "--no-proxy-headers"],
                cwd=ROOT / "backend", stdout=log, stderr=log,
                env=variables,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            frontend = None
            try:
                status, body = wait_http("http://127.0.0.1:8000/health", api)
                assert status == 200 and json.loads(body)["status"] == "ok"
                frontend = subprocess.Popen(
                    ["node", "node_modules/vite/bin/vite.js", "--host", "127.0.0.1"],
                    cwd=ROOT / "frontend", stdout=log, stderr=log,
                    env=variables,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                status, body = wait_http("http://127.0.0.1:5173", frontend)
                assert status == 200 and "Entrenador de Prompts" in body
                # Comprueba que Vite entrega también el módulo React transformado.
                status, module = wait_http("http://127.0.0.1:5173/src/App.tsx", frontend)
                assert status == 200 and "Revisar prompt" in module
                assert counts() == before
                print(f"Inicio {attempt}: API HTTP 200, Vite HTML/módulo HTTP 200; conteos {before}")
            finally:
                for process in (frontend, api):
                    if process is not None:
                        process.terminate()
                        try:
                            process.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait(timeout=5)
    print("Dos ciclos de inicio/parada completos; persistencia conservada.")


if __name__ == "__main__":
    main()
