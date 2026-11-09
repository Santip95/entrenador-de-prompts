"""Límite por bytes y origen antes de validar cuerpos, sin registrar contenido."""
from starlette.responses import JSONResponse
from uuid import uuid4


class RequestGuards:
    def __init__(self, app, origin):
        self.app, self.origin = app, origin

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = {k.lower(): v for k, v in scope["headers"]}
        status, code, message = None, None, None
        if scope["method"] in {"POST", "PUT", "PATCH", "DELETE"}:
            if headers.get(b"origin", b"").decode("latin1") != self.origin:
                status, code, message = 403, "origen_invalido", "Origen de solicitud no permitido."
            elif scope["method"] != "DELETE" and headers.get(b"content-type", b"").split(b";")[0].strip() != b"application/json":
                status, code, message = 400, "tipo_contenido", "Enviá contenido JSON."
        chunks, length = [], 0
        if status is None:
            while True:
                event = await receive()
                if event["type"] == "http.disconnect":
                    return
                length += len(event.get("body", b""))
                if length > 65536:
                    status, code, message = 413, "cuerpo_grande", "La solicitud supera el límite permitido."
                    break
                chunks.append(event)
                if not event.get("more_body", False):
                    break
        if status:
            response = JSONResponse({"error": {"code": code, "message": message, "fields": [], "request_id": str(uuid4())}}, status_code=status, headers={"Cache-Control": "no-store"})
            return await response(scope, receive, send)

        async def buffered():
            return chunks.pop(0) if chunks else await receive()

        async def no_store(event):
            if event["type"] == "http.response.start":
                event["headers"] = [(k, v) for k, v in event["headers"] if k.lower()!=b"cache-control"] + [(b"cache-control", b"no-store"), (b"x-content-type-options", b"nosniff")]
            await send(event)

        await self.app(scope, buffered, no_store)
