from email.message import EmailMessage
import smtplib
from uuid import uuid4
import httpx


def test_real_mailpit_smtp_and_http(mailpit):
    recipient = f"smtp-check-{uuid4()}@example.invalid"
    message = EmailMessage()
    message["From"], message["To"], message["Subject"] = "no-reply@example.invalid", recipient, "Comprobación técnica ficticia etapa 03"
    message.set_content("Correo de prueba sin contraseñas ni tokens.")
    with smtplib.SMTP("127.0.0.1", 1025, timeout=5) as smtp:
        smtp.send_message(message)
    listing = httpx.get("http://127.0.0.1:8025/api/v1/messages").json()
    matching = [m for m in listing["messages"] if any(r["Address"] == recipient for r in m["To"])]
    assert bool(matching), "No se recibió el correo por SMTP real"
    message_id = matching[0]["ID"]
    obtained = httpx.get("http://127.0.0.1:8025/api/v1/message/"+message_id).json()
    assert "Correo de prueba sin contraseñas ni tokens." in obtained["Text"]
    deleted = httpx.request("DELETE", "http://127.0.0.1:8025/api/v1/messages", json={"IDs": [message_id]})
    assert deleted.status_code in {200, 204}
