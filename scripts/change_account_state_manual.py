"""Control manual del endpoint de estado ya existente; sin panel ni secretos impresos."""
import getpass
import httpx


def main():
    print("Usar cuentas ficticias del proyecto. No se guardan cookies ni contraseñas en archivos.")
    email=input("Correo de la cuenta administradora local: ").strip().lower()
    password=getpass.getpass("Contraseña administradora (sin eco): ")
    target=input("Correo de la cuenta ficticia que está abierta en los navegadores: ").strip().lower()
    state=input("Estado: bloqueado / activo / desactivado: ").strip()
    if state not in {'bloqueado','activo','desactivado'}:
        raise SystemExit("Estado no permitido.")
    with httpx.Client(base_url='http://127.0.0.1:8000/api/v1',headers={'Origin':'http://127.0.0.1:5173'},timeout=10) as client:
        login=client.post('/auth/login',json={'correo':email,'password':password})
        if login.status_code!=200:raise SystemExit(f"Ingreso administrativo rechazado: HTTP {login.status_code}.")
        csrf=client.get('/auth/csrf')
        if csrf.status_code!=200:raise SystemExit("No se pudo obtener CSRF; ingresar nuevamente.")
        cursor=None;account=None
        while True:
            params={'limit':100}
            if cursor:params['cursor']=cursor
            response=client.get('/admin/cuentas',params=params)
            if response.status_code!=200:raise SystemExit(f"Listado administrativo rechazado: HTTP {response.status_code}.")
            data=response.json()
            account=next((row for row in data['items'] if row['correo']==target),None)
            cursor=data['next_cursor']
            if account or not cursor:break
        if account is None:raise SystemExit("Cuenta no encontrada; no se realizó ningún cambio.")
        response=client.post(f"/admin/cuentas/{account['id']}/estado",json={'estado':state,'motivo':'seguridad'},headers={'X-CSRF-Token':csrf.json()['csrf_token']})
        print(f"Cambio de estado: HTTP {response.status_code}; esperado 204.")
        client.post('/auth/logout',json={},headers={'X-CSRF-Token':csrf.json()['csrf_token']})
        if response.status_code!=204:raise SystemExit(1)


if __name__=='__main__':
    try:main()
    except httpx.HTTPError:raise SystemExit("No se pudo conectar a la API local; revisar su arranque.") from None
