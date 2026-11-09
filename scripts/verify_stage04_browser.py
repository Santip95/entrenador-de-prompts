"""Recorrido real Chrome/Edge contra PostgreSQL de pruebas; sin trazas con secretos."""
from pathlib import Path
import json
import os
import re
import secrets
import socket
import subprocess
import sys
import time
from urllib.parse import urlsplit
from uuid import uuid4

import httpx
from playwright.sync_api import sync_playwright, expect
from sqlalchemy import create_engine, text

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.core.config import Settings
from app.application.access import AccessService

ORIGIN='http://127.0.0.1:15173'
API='http://127.0.0.1:18000'


def listening(port):
    with socket.socket() as s:return s.connect_ex(('127.0.0.1',port))==0


def ready(url,process):
    for _ in range(100):
        if process and process.poll() is not None:raise RuntimeError('Proceso detenido')
        try:
            if httpx.get(url,timeout=1).status_code==200:return
        except httpx.HTTPError:pass
        time.sleep(.1)
    raise RuntimeError('Tiempo de arranque agotado')


def main():
    step='preparación'
    processes=[];browsers=[];emails=[];owner=None
    folder=ROOT/'local-data'/'etapa04';folder.mkdir(parents=True,exist_ok=True)
    report={'fecha':'2026-11-07','pasos':[],'base':'entrenador_prompts_test','navegadores':[]}
    def passed(label):
        report['pasos'].append({'comprobacion':label,'aprobado':True});print('APROBADO:',label,flush=True)
    try:
        local=Settings()
        runtime=local.resolved_test_database_url()
        owner=create_engine(local.resolved_migration_url(test=True),hide_parameters=True)
        with owner.connect() as c:assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
        if listening(15173) or listening(18000):raise RuntimeError('Puertos de pruebas ocupados; no se detienen procesos ajenos')
        settings=Settings(_env_file=None,DATABASE_URL=runtime,postgres_password=local.postgres_password,app_env='test',public_origin=ORIGIN,csrf_signing_key=secrets.token_urlsafe(48),review_signing_key=secrets.token_urlsafe(48),alert_fingerprint_key=secrets.token_urlsafe(48))
        variables=os.environ.copy()
        variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,DATABASE_URL=runtime,CSRF_SIGNING_KEY=settings.csrf_signing_key.get_secret_value(),REVIEW_SIGNING_KEY=settings.review_signing_key.get_secret_value(),ALERT_FINGERPRINT_KEY=settings.alert_fingerprint_key.get_secret_value(),TFG_API_PROXY_TARGET=API)
        if not listening(8025):
            if listening(1025):raise RuntimeError('SMTP ocupado sin Mailpit comprobable')
            mp=subprocess.Popen([str(ROOT/'local-data/mailpit/mailpit.exe'),'--listen','127.0.0.1:8025','--smtp','127.0.0.1:1025','--disable-version-check','--smtp-disable-rdns','--quiet'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(mp);ready('http://127.0.0.1:8025/api/v1/info',mp)
        else:ready('http://127.0.0.1:8025/api/v1/info',None)
        api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(api);ready(API+'/health',api)
        vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(vite);ready(ORIGIN,vite)
        email=f'web04-{uuid4()}@example.invalid';emails.append(email)
        password='Frase ficticia del navegador número 41';new_password='Otra frase ficticia del navegador número 42'
        admin_email=f'web04-admin-{uuid4()}@example.invalid';emails.append(admin_email)
        service=AccessService(owner,settings);service.register(admin_email,password)
        with owner.begin() as c:c.execute(text("UPDATE usuario SET rol='administrador' WHERE correo=:email"),{'email':admin_email})
        with sync_playwright() as pw:
            chrome=pw.chromium.launch(channel='chrome',headless=True);browsers.append(chrome)
            edge=pw.chromium.launch(channel='msedge',headless=True);browsers.append(edge)
            report['navegadores']=[{'canal':'chrome','version':chrome.version},{'canal':'msedge','version':edge.version}]
            ca=chrome.new_context(viewport={'width':1280,'height':900},permissions=['clipboard-read','clipboard-write'])
            cb=edge.new_context(viewport={'width':1280,'height':900})
            a,b=ca.new_page(),cb.new_page()
            http_events=[]
            report['http']=http_events
            for page in (a,b):page.on('response',lambda r:http_events.append({'ruta':r.url.split('/api/v1',1)[1].split('?')[0],'status':r.status}) if '/api/v1/' in r.url else None)
            external=[]
            def network_request(request):
                address=urlsplit(request.url)
                if address.scheme in ('http','https') and address.hostname!='127.0.0.1':
                    external.append(address.scheme+'://'+str(address.hostname)+(':'+str(address.port) if address.port else ''))
            for page in (a,b):page.on('request',network_request)
            def heading(page,title):
                try:expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible(timeout=15000)
                except Exception:
                    page.screenshot(path=str(folder/'fallo-pantalla.png'),full_page=True,timeout=3000)
                    report['diagnostico_pantalla']={'esperado':title,'encabezados':page.locator('h1').all_text_contents(),'avisos':page.get_by_role('alert').all_text_contents()}
                    raise
            def login(page,key):
                page.get_by_label('Correo',exact=True).fill(email);page.get_by_label('Contraseña',exact=True).fill(key);page.get_by_role('button',name='Ingresar',exact=True).click();heading(page,'Comenzar una práctica')
            step='registro y acceso desde formularios'
            a.goto(ORIGIN);heading(a,'Ingresar');a.get_by_role('button',name='Crear cuenta',exact=True).click()
            a.get_by_label('Correo',exact=True).fill(email);a.get_by_label('Contraseña',exact=True).fill('corta');a.get_by_role('button',name='Registrarme',exact=True).click();expect(a.locator('#password-error')).to_contain_text('15 y 128')
            with owner.connect() as c:assert c.scalar(text('SELECT count(*) FROM usuario WHERE correo=:email'),{'email':email})==0
            a.get_by_label('Contraseña',exact=True).fill(password);a.get_by_role('button',name='Registrarme',exact=True).click();heading(a,'Ingresar');login(a,password)
            b.goto(ORIGIN);heading(b,'Ingresar');login(b,password)
            assert ca.cookies()!=cb.cookies();passed('Registro e ingreso en Chrome y Edge, procesos y cookies independientes')
            a.set_viewport_size({'width':360,'height':800});a.keyboard.press('Tab');assert a.locator(':focus').count()==1
            assert a.evaluate('document.documentElement.scrollWidth<=innerWidth')
            a.screenshot(path=str(folder/'inicio-360.png'),full_page=True);a.set_viewport_size({'width':1280,'height':900})
            passed('Inicio a 360 px sin desborde y foco de teclado comprobado')
            step='CP-12 desde pantallas'
            a.get_by_label('Desafío',exact=True).select_option(label='Solicitar una reunión')
            a.get_by_role('button',name='Revisar inicio',exact=True).click();a.get_by_role('button',name='Confirmar inicio y continuar',exact=True).click();heading(a,'Construir el prompt')
            cases={c['id']:c for c in json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']}
            c=cases['CP-31']['entrada']['componentes']
            step='CP-12: completar constructor V1'
            a.get_by_label('Tarea',exact=True).fill(c['tarea']['texto']);a.get_by_label('Acción',exact=True).select_option(c['tarea']['accion_id'])
            a.get_by_label('Contexto',exact=True).fill(c['contexto']['texto']);a.get_by_label('Finalidad',exact=True).fill(c['contexto']['campos']['finalidad'])
            a.get_by_label(re.compile('Usar solo datos ficticios')).check();a.get_by_label('Formato',exact=True).select_option('correo')
            step='CP-12: revisar V1'
            a.get_by_role('button',name='Revisar prompt',exact=True).click();expect(a.get_by_text(re.compile('Cumplimiento estructural: 3 de 6'))).to_be_visible()
            step='CP-12: guardar V1'
            a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('heading',name='Versión 1 guardada',exact=True)).to_be_visible()
            with owner.connect() as c:
                v1=dict(c.execute(text('SELECT v.* FROM version_prompt v JOIN practica p ON p.id=v.practica_id JOIN usuario u ON u.id=p.usuario_id WHERE u.correo=:email'),{'email':email}).mappings().one())
            step='CP-12: recargar y reabrir V1'
            a.reload();heading(a,'Comenzar una práctica');a.get_by_role('button',name='Historial',exact=True).click();a.get_by_role('button',name='Abrir práctica',exact=True).click();expect(a.get_by_role('heading',name='Versión 1 guardada',exact=True)).to_be_visible()
            a.get_by_role('button',name='Crear nueva versión',exact=True).click();heading(a,'Construir el prompt')
            a.get_by_label('Fecha de referencia',exact=True).fill('2030-05-10');a.get_by_label('Destinatario',exact=True).fill(cases['CP-01']['entrada']['componentes']['destinatario']['texto']);a.get_by_label('Detalle del formato',exact=True).fill(cases['CP-01']['entrada']['componentes']['formato']['detalle'])
            step='CP-12: revisar V2'
            a.get_by_role('button',name='Revisar prompt',exact=True).click();expect(a.get_by_text(re.compile('Cumplimiento estructural: 6 de 6'))).to_be_visible()
            for warning in ('El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.','Estos patrones no detectan toda la información sensible.'):
                expect(a.get_by_text(warning,exact=True).first).to_be_visible()
            lost=[False]
            def lost_response(route):
                if route.request.method=='POST' and not lost[0]:lost[0]=True;route.fetch();route.abort()
                else:route.continue_()
            a.route('**/api/v1/practicas/*/versiones',lost_response)
            step='CP-12: reintento tras respuesta perdida'
            a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('alert')).to_contain_text('Tu borrador sigue en memoria')
            a.get_by_role('button',name='Revisar prompt',exact=True).click();expect(a.get_by_text(re.compile('Cumplimiento estructural: 6 de 6'))).to_be_visible()
            a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
            a.unroute('**/api/v1/practicas/*/versiones',lost_response)
            with owner.connect() as c:
                assert dict(c.execute(text('SELECT * FROM version_prompt WHERE id=:id'),{'id':v1['id']}).mappings().one())==v1
                assert c.scalar(text('SELECT count(*) FROM version_prompt WHERE practica_id=:id'),{'id':v1['practica_id']})==2
            step='CP-12: copia y comparación'
            a.get_by_role('button',name='Copiar prompt',exact=True).click();expect(a.get_by_role('status')).to_contain_text('Prompt copiado')
            clipboard=a.evaluate('navigator.clipboard.readText()')
            expected_text=a.locator('section[aria-label="Resultados"] pre').inner_text()
            report['portapapeles']={'longitud_copiada':len(clipboard),'longitud_presentada':len(expected_text),'equivalente_lf':clipboard.replace('\r\n','\n').replace('\r','\n')==expected_text}
            assert report['portapapeles']['equivalente_lf']
            a.get_by_role('button',name='Comparar versiones',exact=True).click();a.get_by_role('button',name='Comparar',exact=True).click();expect(a.get_by_text(re.compile('Diferencia: 50 puntos porcentuales. Resolución: 100 %'))).to_be_visible()
            a.screenshot(path=str(folder/'comparacion-desktop.png'),full_page=True)
            passed('CP-12 por pantallas: V1 3/6 intacta, V2 6/6, delta 50 y resolución 100')
            passed('Respuesta perdida tras commit: borrador conservado y reintento sin duplicar V2; copia explícita')
            step='persistencia después de reiniciar API y Vite'
            for process in (vite,api):process.terminate();process.wait(timeout=10);processes.remove(process)
            api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(api);ready(API+'/health',api)
            vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(vite);ready(ORIGIN,vite)
            a.reload();heading(a,'Comenzar una práctica');a.get_by_role('button',name='Historial',exact=True).click();a.get_by_role('button',name='Abrir práctica',exact=True).click();expect(a.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
            passed('Persistencia y sesión tras recargar y reiniciar API y Vite, sin reiniciar PostgreSQL compartido')
            a.get_by_role('button',name='Progreso',exact=True).click();heading(a,'Mi progreso');expect(a.get_by_text('Series separadas por práctica y configuración.',exact=False)).to_be_visible()
            b.get_by_role('button',name='Historial',exact=True).click();b.get_by_role('button',name='Abrir práctica',exact=True).click();expect(b.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
            step='objetivo preventivo, libre y avisos'
            a.get_by_role('button',name='Comenzar práctica',exact=True).click();a.get_by_role('radio',name='Objetivo propio',exact=True).check()
            objective='Objetivo ficticio con persona@example.invalid'
            a.locator('textarea').fill(objective)
            for code in ('C2','C3','C4'):a.get_by_role('checkbox',name=re.compile(code+' ·')).uncheck()
            a.get_by_label('Modo de trabajo',exact=True).select_option('libre');a.get_by_role('button',name='Revisar inicio',exact=True).click()
            expect(a.get_by_role('button',name='Confirmar inicio y continuar',exact=True)).to_be_disabled()
            with owner.connect() as c:assert c.scalar(text('SELECT count(*) FROM practica WHERE objetivo=:o'),{'o':objective})==0
            a.get_by_label(re.compile('Revisé esta coincidencia')).check();a.get_by_role('button',name='Confirmar inicio y continuar',exact=True).click();heading(a,'Construir el prompt')
            free='  Texto <img src=x onerror="window.__tfgXss=1"> con nuevo@example.invalid\n  '
            a.get_by_label('Texto libre',exact=True).fill(free);a.get_by_label('Tarea',exact=True).fill('Explicá una idea ficticia');a.get_by_label('Acción',exact=True).select_option('explicar');a.get_by_label('Formato',exact=True).select_option('texto')
            a.get_by_label(re.compile('Confirmo que revisé los componentes')).check();a.get_by_role('button',name='Revisar prompt',exact=True).click()
            checks=a.get_by_label(re.compile('Revisé esta coincidencia'));expect(checks).to_have_count(2);checks.nth(0).check();expect(a.get_by_role('button',name='Confirmar y guardar versión',exact=True)).to_be_disabled();checks.nth(1).check()
            assert a.locator('main img').count()==0 and a.evaluate('window.__tfgXss') is None
            a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('heading',name='Versión 1 guardada',exact=True)).to_be_visible()
            assert a.locator('section[aria-label="Resultados"] pre').inner_text()==free
            a.set_viewport_size({'width':360,'height':800});assert a.evaluate('document.documentElement.scrollWidth<=innerWidth');a.screenshot(path=str(folder/'resultado-360.png'),full_page=True)
            passed('Objetivo no persiste antes de confirmar; libre declarado, confirmación parcial bloqueada, HTML como texto, avisos a 360 px')
            step='recuperación desde formulario y Mailpit'
            a.get_by_role('button',name='Cerrar sesión',exact=True).click();heading(a,'Ingresar');a.get_by_role('button',name='Olvidé mi contraseña',exact=True).click();a.get_by_label('Correo',exact=True).fill(email);a.get_by_role('button',name='Enviar enlace',exact=True).click();expect(a.get_by_role('status')).to_contain_text('recibirás un correo')
            listing=httpx.get('http://127.0.0.1:8025/api/v1/messages').json()['messages'];mail=next(m for m in listing if any(x['Address']==email for x in m['To']))
            body=httpx.get('http://127.0.0.1:8025/api/v1/message/'+mail['ID']).json()['Text'];link=re.search(r'http://127\.0\.0\.1:15173/#restablecer=[A-Za-z0-9_-]+',body).group()
            a.goto(link);heading(a,'Restablecer contraseña');assert '#' not in a.url
            a.get_by_label('Nueva contraseña',exact=True).fill(new_password);a.get_by_role('button',name='Guardar nueva contraseña',exact=True).click();heading(a,'Ingresar')
            a.goto(link);heading(a,'Restablecer contraseña');a.get_by_label('Nueva contraseña',exact=True).fill(new_password);a.get_by_role('button',name='Guardar nueva contraseña',exact=True).click();expect(a.get_by_role('alert')).to_contain_text('El enlace no es válido o venció')
            a.get_by_role('button',name='Ir al ingreso',exact=True).click();a.get_by_label('Correo',exact=True).fill(email);a.get_by_label('Contraseña',exact=True).fill(password);a.get_by_role('button',name='Ingresar',exact=True).click();expect(a.get_by_role('alert')).to_contain_text('No se pudo autenticar')
            login(a,new_password)
            b.get_by_role('button',name='Historial',exact=True).click();heading(b,'Ingresar');assert v1['texto'] not in b.locator('body').inner_text();login(b,new_password)
            passed('Recuperación por formulario y correo Mailpit real; enlace fuera del historial URL; sesión del otro navegador revocada y contenido retirado')
            step='cambio de contraseña desde perfil'
            final_password='Tercera frase ficticia desde el perfil número 43'
            a.get_by_role('button',name='Perfil',exact=True).click();a.get_by_label('Contraseña actual',exact=True).fill(new_password);a.get_by_label('Nueva contraseña',exact=True).fill(final_password);a.get_by_role('button',name='Cambiar contraseña',exact=True).click();heading(a,'Ingresar')
            b.get_by_role('button',name='Historial',exact=True).click();heading(b,'Ingresar');login(a,final_password);login(b,final_password)
            passed('Cambio de contraseña desde perfil revoca las dos sesiones y exige ingresar otra vez')
            step='bloqueo administrativo de dos navegadores'
            cookies_a,cookies_b=ca.cookies(),cb.cookies()
            with httpx.Client(base_url=API+'/api/v1',headers={'Origin':ORIGIN}) as admin:
                assert admin.post('/auth/login',json={'correo':admin_email,'password':password}).status_code==200
                admin_csrf=admin.get('/auth/csrf').json()['csrf_token']
                with owner.connect() as c:uid=c.scalar(text('SELECT id FROM usuario WHERE correo=:e'),{'e':email})
                def state(value):return admin.post(f'/admin/cuentas/{uid}/estado',json={'estado':value,'motivo':'seguridad'},headers={'X-CSRF-Token':admin_csrf})
                assert state('bloqueado').status_code==204
                for page in (a,b):page.get_by_role('button',name='Historial',exact=True).click();heading(page,'Ingresar')
                assert state('activo').status_code==204
                for context,page,cookies in ((ca,a,cookies_a),(cb,b,cookies_b)):
                    context.add_cookies(cookies);page.reload();heading(page,'Ingresar')
            passed('SEC-01 / INT-02: Chrome y Edge bloqueados; cookies previas no reviven tras desbloquear')
            step='almacenamiento y solicitudes externas'
            storage=[page.evaluate('({local:Object.keys(localStorage),session:Object.keys(sessionStorage)})') for page in (a,b)]
            report['almacenamiento_claves']=storage;report['solicitudes_externas']=len(external);report['origenes_externos']=sorted(set(external))
            for page in (a,b):
                values=page.evaluate('Object.values(localStorage).concat(Object.values(sessionStorage))')
                assert not any(secret in value for value in values for secret in (password,new_password,final_password,free,link.split('#restablecer=')[1]))
            passed('Almacenamiento local y de sesión sin contraseñas, tokens ni borradores')
            report['recorrido_funcional_aprobado']=True
            report['nf02_aprobado']=not external
            report['aprobado']=not external
            if external:
                report['limitacion_entorno']='Se observaron solicitudes a orígenes ajenos. No se desactivó protección local; NF-02 queda sin aprobar hasta aislar su procedencia.'
                print('PENDIENTE NF-02: solicitudes externas observadas; revisar el informe local de orígenes. Recorrido funcional aprobado.',flush=True)
    except Exception as error:
        if 'a' in locals():
            try:a.screenshot(path=str(folder/'fallo-app.png'),full_page=True)
            except Exception:pass
        report['aprobado']=False;report['fallo']={'paso':step,'tipo':type(error).__name__}
        print('FALLO:',step,';',type(error).__name__,'(detalles sensibles omitidos)',flush=True)
    finally:
        for browser in reversed(browsers):
            try:browser.close()
            except Exception:pass
        for process in reversed(processes):
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        if owner:
            with owner.begin() as c:
                assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
                c.execute(text('DELETE FROM usuario WHERE correo=ANY(:emails)'),{'emails':emails})
            owner.dispose()
        (folder/'navegadores.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report.get('aprobado') else 2 if report.get('recorrido_funcional_aprobado') else 1


if __name__=='__main__':raise SystemExit(main())
