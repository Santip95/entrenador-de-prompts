"""Comprobar la demo real sin imprimir sus contraseñas privadas."""
from pathlib import Path
import json
import os
import subprocess
import sys
from sqlalchemy.engine import make_url
from playwright.sync_api import sync_playwright,expect
from verify_stage04_browser import ROOT,API,ORIGIN,listening,ready
from demo import credentials_path,DATABASE
from app.core.config import Settings

def main():
    processes=[];report={'base':DATABASE,'aprobado':False}
    try:
        if listening(18000) or listening(15173):raise RuntimeError('Puertos temporales ocupados.')
        settings=Settings();accounts=json.loads(credentials_path().read_text(encoding='utf-8'))
        variables=os.environ.copy();variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,DATABASE_URL=make_url(settings.resolved_database_url()).set(database=DATABASE).render_as_string(hide_password=False),TFG_API_PROXY_TARGET=API)
        api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(api);ready(API+'/health',api)
        vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(vite);ready(ORIGIN,vite)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            try:
                page=browser.new_page();page.goto(ORIGIN)
                for role in ('usuario','administrador'):
                    page.get_by_label('Correo',exact=True).fill(accounts[role]['correo']);page.get_by_label('Contraseña',exact=True).fill(accounts[role]['password']);page.get_by_role('button',name='Ingresar',exact=True).click()
                    expect(page.get_by_role('heading',name='Comenzar una práctica',exact=True)).to_be_visible()
                    if role=='usuario':
                        page.get_by_role('button',name='Historial',exact=True).click();page.get_by_role('button',name='Abrir práctica',exact=True).click();expect(page.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
                        page.get_by_role('button',name='Comparar versiones',exact=True).click();page.get_by_role('button',name='Comparar',exact=True).click();expect(page.get_by_text('Diferencia: 50 puntos porcentuales. Resolución: 100 %.')).to_be_visible()
                    else:
                        page.get_by_role('button',name='Administración',exact=True).click();expect(page.get_by_role('button',name='Crear desafío borrador',exact=True)).to_be_visible()
                    page.get_by_role('button',name='Cerrar sesión',exact=True).click();expect(page.get_by_role('heading',name='Ingresar',exact=True)).to_be_visible()
                report.update(aprobado=True,usuario_historial_comparacion=True,administrador_panel=True,logout_con_estado_privado_retirado=True)
            finally:browser.close()
    except Exception as error:report['fallo_tipo']=type(error).__name__
    finally:
        for process in reversed(processes):process.terminate();process.wait(timeout=10)
        path=ROOT/'local-data/etapa06/demo.json';path.parent.mkdir(exist_ok=True,parents=True);path.write_text(json.dumps(report),encoding='utf-8');print(json.dumps(report))
    return 0 if report['aprobado'] else 1

if __name__=='__main__':raise SystemExit(main())
