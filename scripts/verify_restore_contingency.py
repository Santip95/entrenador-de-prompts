"""Auxiliar del ensayo ficticio: API/Vite reales y Chrome sobre la copia restaurada."""
from pathlib import Path
import os
import re
import subprocess
import sys
import time
from sqlalchemy.engine import make_url
from playwright.sync_api import sync_playwright,expect
from verify_stage04_browser import listening,ready,ROOT,ORIGIN,API

def verify(settings,database,account):
    if database!='entrenador_prompts_contingencia_test':raise RuntimeError('Sólo contingencia ficticia.')
    if listening(18000) or listening(15173):raise RuntimeError('Puertos de ensayo ocupados; no se detienen procesos ajenos.')
    started=time.perf_counter();processes=[]
    variables=os.environ.copy()
    variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,DATABASE_URL=make_url(settings.resolved_database_url()).set(database=database).render_as_string(hide_password=False),TFG_API_PROXY_TARGET=API)
    try:
        api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(api);ready(API+'/health',api)
        vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(vite);ready(ORIGIN,vite)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            try:
                page=browser.new_page();page.goto(ORIGIN)
                page.get_by_label('Correo',exact=True).fill(account[1]);page.get_by_label('Contraseña',exact=True).fill(account[2]);page.get_by_role('button',name='Ingresar',exact=True).click()
                expect(page.get_by_role('heading',name='Comenzar una práctica',exact=True)).to_be_visible(timeout=15000)
                page.get_by_role('button',name='Historial',exact=True).click();page.get_by_role('button',name='Abrir práctica',exact=True).click();expect(page.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
                page.get_by_role('button',name='Comparar versiones',exact=True).click();page.get_by_role('button',name='Comparar',exact=True).click();expect(page.get_by_text(re.compile('Diferencia: 50 puntos porcentuales. Resolución: 100 %'))).to_be_visible()
                return {'api_http':200,'frontend_http':200,'chrome_historial_comparacion':True,'arranque_y_recorrido_segundos':round(time.perf_counter()-started,3),'nf02':'Pendiente del entorno; este ensayo no acredita ausencia de tráfico ajeno.'}
            finally:browser.close()
    finally:
        for process in reversed(processes):
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
