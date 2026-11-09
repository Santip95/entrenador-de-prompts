"""Caso NF-02 acotado: CP-31 por pantallas; sólo metadatos, nunca cuerpos/HAR."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from urllib.parse import urlsplit, parse_qsl
from uuid import uuid4

from playwright.sync_api import sync_playwright, expect
from sqlalchemy import create_engine, text
from verify_stage04_browser import ROOT, ORIGIN, API, listening, ready
from app.core.config import Settings
from app.application.access import AccessService


def safe_path(url):
    # Nunca conservar identificadores opacos presentes en la URL del componente.
    return '/'.join(p if not p or re.fullmatch(r'[A-Za-z0-9_.-]{1,24}', p) else '{segmento}'
                    for p in urlsplit(url).path.split('/'))


def locations(body, markers):
    """Ubicación JSON del marcador, sin conservar el valor que lo contiene."""
    found = []
    def walk(value, path, depth=0):
        if depth > 12:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                key = k if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,40}', k) else '{campo}'
                walk(v, path + '/' + key, depth + 1)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, path + '/' + str(i), depth + 1)
        elif isinstance(value, str):
            for name, marker in markers.items():
                if marker in value:
                    found.append({'marcador': name, 'longitud': len(marker), 'campo_cuerpo': path})
            # Algunos componentes encapsulan JSON dentro de un string JSON.
            if value.startswith(('{', '[')):
                try: walk(json.loads(value), path + '/{json_interno}', depth + 1)
                except (ValueError, TypeError): pass
    try: walk(json.loads(body), '')
    except (ValueError, TypeError):
        for name, marker in markers.items():
            if marker in body:
                found.append({'marcador': name, 'longitud': len(marker), 'campo_cuerpo': '{cuerpo_no_JSON}'})
    return found


def main():
    processes = []
    engine = None
    email = 'nf02-' + str(uuid4()) + '@example.invalid'
    report = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'caso': 'CP-31 constructor guiado',
              'base': 'entrenador_prompts_test', 'solicitudes': [], 'navegadores': [],
              'antivirus_modificado': False, 'solicitudes_bloqueadas_por_auxiliar': False,
              'limite': 'Accion activa es correlacion temporal, no causalidad. No atribuye firma/ruta fisica ni descarta contenido codificado.'}
    try:
        if listening(18000) or listening(15173):
            raise RuntimeError('Puertos temporales ocupados')
        settings = Settings()
        engine = create_engine(settings.resolved_migration_url(test=True), hide_parameters=True)
        with engine.connect() as c:
            assert c.scalar(text('SELECT current_database()')) == 'entrenador_prompts_test'
        password = secrets.token_urlsafe(32)
        AccessService(engine, settings).register(email, password)
        variables = os.environ.copy()
        variables.update(APP_ENV='test', PUBLIC_ORIGIN=ORIGIN,
                         DATABASE_URL=settings.resolved_test_database_url(), TFG_API_PROXY_TARGET=API)
        api = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
                               '--port', '18000', '--no-access-log', '--no-proxy-headers'],
                               cwd=ROOT/'backend', env=variables, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(api); ready(API+'/health', api)
        vite = subprocess.Popen(['node', 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '15173'],
                                cwd=ROOT/'frontend', env=variables, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(vite); ready(ORIGIN, vite)
        cases = json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']
        components = next(x for x in cases if x['id'] == 'CP-31')['entrada']['componentes']
        markers = {'tarea_CP31': components['tarea']['texto'],
                   'contexto_CP31': components['contexto']['texto'],
                   'marcador_usuario_ficticio': 'PRUEBA_NF02_ABC123'}
        with sync_playwright() as pw:
            for channel in ('chrome', 'msedge'):
                browser = pw.chromium.launch(channel=channel, headless=True)
                try:
                    report['navegadores'].append({'canal': channel, 'version': browser.version})
                    page = browser.new_page()
                    session = page.context.new_cdp_session(page)
                    session.send('Network.enable')
                    phase = {'accion': 'abrir e ingresar'}
                    def request(event):
                        r = event['request']; url = urlsplit(r['url'])
                        if url.scheme not in ('http', 'https'):
                            return
                        # Sólo registrar tráfico local con marcadores o tráfico externo.
                        body = r.get('postData', '')
                        hits = locations(body, markers) if body else []
                        if url.hostname == '127.0.0.1' and not hits:
                            return
                        frames = event.get('initiator', {}).get('stack', {}).get('callFrames', [])
                        functions = [f.get('functionName','') for f in frames[:6]
                                     if re.fullmatch(r'[A-Za-z_$][\w$]{0,60}', f.get('functionName',''))]
                        report['solicitudes'].append({'navegador': channel,
                            'fecha_utc': datetime.now(timezone.utc).isoformat(),
                            'accion_activa': phase['accion'], 'host': url.hostname,
                            'ruta_sanitizada': safe_path(r['url']), 'metodo': r['method'],
                            'tipo': event.get('type'), 'parametros_nombres': sorted({k for k,v in parse_qsl(url.query)}),
                            'iniciadores_funciones': functions, 'bytes_cuerpo_visibles': len(body.encode()),
                            'coincidencias': hits})
                    session.on('Network.requestWillBeSent', request)
                    page.goto(ORIGIN)
                    page.get_by_label('Correo', exact=True).fill(email)
                    page.get_by_label('Contraseña', exact=True).fill(password)
                    page.get_by_role('button', name='Ingresar', exact=True).click()
                    expect(page.get_by_role('heading', name='Comenzar una práctica', exact=True)).to_be_visible()
                    phase['accion'] = 'preparar desafio Solicitar una reunión'
                    page.get_by_label('Desafío', exact=True).select_option(label='Solicitar una reunión')
                    page.get_by_role('button', name='Revisar inicio', exact=True).click()
                    page.get_by_role('button', name='Confirmar inicio y continuar', exact=True).click()
                    expect(page.get_by_role('heading', name='Construir el prompt', exact=True)).to_be_visible()
                    phase['accion'] = 'completar Tarea y Contexto CP31'
                    page.get_by_label('Tarea', exact=True).fill(markers['tarea_CP31'])
                    page.get_by_label('Acción', exact=True).select_option(components['tarea']['accion_id'])
                    page.get_by_label('Contexto', exact=True).fill(markers['contexto_CP31'])
                    page.get_by_label('Finalidad', exact=True).fill(components['contexto']['campos']['finalidad'])
                    page.get_by_label(re.compile('Usar solo datos ficticios')).check()
                    page.get_by_label('Formato', exact=True).select_option('correo')
                    page.wait_for_timeout(3000)
                    phase['accion'] = 'clic Revisar prompt CP31 (sin guardar versión)'
                    page.get_by_role('button', name='Revisar prompt', exact=True).click()
                    expect(page.get_by_text(re.compile('Cumplimiento estructural: 3 de 6'))).to_be_visible()
                    page.wait_for_timeout(5000)
                    # Control mínimo del marcador de la repetición manual, misma acción.
                    phase['accion'] = 'añadir marcador ficticio a Tarea y repetir revisión'
                    page.get_by_label('Tarea', exact=True).fill(markers['tarea_CP31'] + ' ' + markers['marcador_usuario_ficticio'])
                    page.get_by_role('button', name='Revisar prompt', exact=True).click()
                    expect(page.get_by_role('button', name='Confirmar y guardar versión', exact=True)).to_be_visible()
                    page.wait_for_timeout(5000)
                finally:
                    browser.close()
        report['caso_ejecutado'] = True
    except Exception as error:
        report['caso_ejecutado'] = False
        report['error_tipo'] = type(error).__name__
    finally:
        for process in reversed(processes):
            process.terminate()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=5)
        if engine is not None:
            with engine.begin() as c:
                assert c.scalar(text('SELECT current_database()')) == 'entrenador_prompts_test'
                c.execute(text('DELETE FROM usuario WHERE correo=:email'), {'email': email})
            engine.dispose()
        folder = ROOT/'local-data/etapa06'; folder.mkdir(parents=True, exist_ok=True)
        path = folder/('nf02-focalizado-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        external_hits = [r for r in report['solicitudes'] if r['host'] != '127.0.0.1' and r['coincidencias']]
        print(json.dumps({'caso_ejecutado': report['caso_ejecutado'],
                          'error_tipo': report.get('error_tipo'), 'reporte': str(path.relative_to(ROOT)),
                          'solicitudes_con_coincidencias_externas': external_hits}, ensure_ascii=True, indent=2))
    return 0 if report['caso_ejecutado'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
