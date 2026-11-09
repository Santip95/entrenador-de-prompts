"""Recorrido interactivo local por API. Claves/tokens sin eco ni logs."""
import getpass
from uuid import uuid4

import httpx

ORIGIN = "http://127.0.0.1:5173"
BASE = ORIGIN + "/api/v1"


def expect(response, status, label):
    if response.status_code != status:
        raise SystemExit(f"{label}: HTTP {response.status_code}; esperado {status}. No se muestran cuerpos ni cabeceras sensibles.")
    print(f"{label}: HTTP {status}, correcto.")


def main():
    email = f"manual-{uuid4()}@example.invalid"
    print("Cuenta ficticia de esta comprobación:", email)
    print("No usar una contraseña real. Las entradas se ocultan y no se guardan en un informe.")
    password = getpass.getpass("Contraseña ficticia (15–128 caracteres, no común): ")
    with httpx.Client(base_url=BASE, headers={"Origin": ORIGIN}, timeout=10) as a, httpx.Client(base_url=BASE, headers={"Origin": ORIGIN}, timeout=10) as b:
        data = {"correo": email, "password": password}
        expect(a.post("/auth/registro", json=data), 202, "Registro")
        expect(a.post("/auth/registro", json=data), 202, "Registro repetido genérico")
        expect(a.post("/auth/login", json=data), 200, "Ingreso A")
        expect(b.post("/auth/login", json=data), 200, "Ingreso B independiente")
        expect(a.get("/auth/me"), 200, "Sesión A")
        expect(b.get("/auth/me"), 200, "Sesión B")
        csrf = a.get("/auth/csrf").json()["csrf_token"]
        expect(a.post("/auth/logout", json={}, headers={"X-CSRF-Token": csrf}), 204, "Cerrar sesión A")
        expect(a.get("/auth/me"), 401, "A revocada")
        expect(b.get("/auth/me"), 200, "B sigue activa")
        expect(a.post("/auth/recuperacion", json={"correo": email}), 202, "Solicitar recuperación")
        print("Abrí http://127.0.0.1:8025 y buscá el correo de esta cuenta.")
        print("El enlace abre todavía el esqueleto: el formulario web pertenece a etapa 04.")
        print("Copiá sólo el valor posterior a #restablecer= del enlace en la siguiente entrada local oculta.")
        token = getpass.getpass("Token del correo (nunca enviarlo al chat): ")
        new = getpass.getpass("Nueva contraseña ficticia: ")
        reset = {"token": token, "password_nueva": new}
        expect(a.post("/auth/restablecer", json=reset), 204, "Restablecer")
        expect(a.post("/auth/restablecer", json=reset), 400, "Reutilización rechazada")
        expect(b.get("/auth/me"), 401, "Revocación de B")
        expect(a.post("/auth/login", json=data), 401, "Clave anterior rechazada")
        expect(a.post("/auth/login", json={"correo": email, "password": new}), 200, "Clave nueva admitida")
        csrf = a.get("/auth/csrf").json()["csrf_token"]
        expect(a.post("/auth/logout", json={}, headers={"X-CSRF-Token": csrf}), 204, "Cierre final")
    print("Recorrido HTTP completado. Informá por separado qué observaste en Mailpit.")
    print("No acredita dos navegadores ni pantallas funcionales; la cuenta ficticia queda en la base local.")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError:
        raise SystemExit("No se pudo conectar. Verificá API, Vite y Mailpit; no se muestran detalles sensibles.") from None
