"""Publicar C6 desde panel y revisar/confirmar/guardar números ficticios en pruebas."""
from datetime import datetime, timezone
import json
import os
import re
import secrets
import subprocess
import sys
from uuid import uuid4
from playwright.sync_api import sync_playwright, expect
from sqlalchemy import create_engine, text
from verify_stage04_browser import ROOT, ORIGIN, API, listening, ready
from app.core.config import Settings
from app.application.access import AccessService
from app.domain.evaluation import NUMERIC_DETECTOR


def main():
    processes=[]; engine=None; accounts=[]; candidate=None; original=None
    report={'fecha_utc':datetime.now(timezone.utc).isoformat(),'base':'entrenador_prompts_test','aprobado':False}
    try:
        if listening(18000) or listening(15173): raise RuntimeError('Puertos temporales ocupados')
        settings=Settings()
        engine=create_engine(settings.resolved_migration_url(test=True),hide_parameters=True)
        with engine.connect() as c:
            assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
            original=dict(c.execute(text("SELECT * FROM regla WHERE activa AND criterio_id=(SELECT id FROM criterio WHERE codigo='C6')")).mappings().one())
            assert NUMERIC_DETECTOR not in original['parametros']['detectores_activos']
        password=secrets.token_urlsafe(32)
        for role in ('administrador','usuario'):
            email='num-browser-'+str(uuid4())+'@example.invalid'
            AccessService(engine,settings).register(email,password)
            accounts.append(email)
            if role=='administrador':
                with engine.begin() as c:c.execute(text("UPDATE usuario SET rol='administrador' WHERE correo=:email"),{'email':email})
        variables=os.environ.copy();variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,
            DATABASE_URL=settings.resolved_test_database_url(),TFG_API_PROXY_TARGET=API)
        api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(api);ready(API+'/health',api)
        vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(vite);ready(ORIGIN,vite)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            try:
                page=browser.new_page()
                def login(email):
                    page.goto(ORIGIN);page.get_by_label('Correo',exact=True).fill(email)
                    page.get_by_label('Contraseña',exact=True).fill(password)
                    page.get_by_role('button',name='Ingresar',exact=True).click()
                    expect(page.get_by_role('heading',name='Comenzar una práctica',exact=True)).to_be_visible()
                login(accounts[0])
                page.get_by_role('button',name='Administración',exact=True).click()
                page.get_by_role('button',name='Reglas',exact=True).click()
                page.get_by_role('button',name=f"Crear versión desde C6 v{original['version']}",exact=True).click()
                page.get_by_label('Secuencias exactas de 7, 8 o 10 dígitos (posible información sensible)',exact=True).check()
                with page.expect_response(lambda r:'/admin/reglas' in r.url and r.request.method=='POST') as response:
                    page.get_by_role('button',name='Crear versión inactiva',exact=True).click()
                result=response.value.json();candidate=result['id'];assert response.value.status==201
                page.get_by_role('button',name=f"Publicar C6 v{result['version']}",exact=True).click()
                expect(page.get_by_role('heading',name=f"C6 · versión {result['version']} · Activa",exact=True)).to_be_visible()
                page.get_by_role('button',name='Cerrar sesión',exact=True).click()
                login(accounts[1])
                page.get_by_role('radio',name='Objetivo propio',exact=True).check()
                page.get_by_role('textbox',name='Objetivo propio',exact=True).fill('Objetivo ficticio 0123456')
                page.get_by_role('button',name='Revisar inicio',exact=True).click()
                proceed=page.get_by_role('button',name='Confirmar inicio y continuar',exact=True)
                expect(proceed).to_be_disabled()
                with engine.connect() as c:
                    assert c.scalar(text('SELECT count(*) FROM practica p JOIN usuario u ON u.id=p.usuario_id WHERE u.correo=:email'),{'email':accounts[1]})==0
                page.get_by_label(re.compile('Revisé esta coincidencia: Secuencia numérica')).check()
                proceed.click();expect(page.get_by_role('heading',name='Construir el prompt',exact=True)).to_be_visible()
                page.get_by_label('Tarea',exact=True).fill('Ejemplo ficticio 12345678; DNI 12345678')
                page.get_by_role('button',name='Revisar prompt',exact=True).click()
                save=page.get_by_role('button',name='Confirmar y guardar versión',exact=True)
                expect(save).to_be_disabled()
                # Objetivo genérico + número aislado genérico + DNI existente (sin genérica sobre él).
                checkboxes=page.get_by_label(re.compile('Revisé esta coincidencia:'))
                expect(checkboxes).to_have_count(3)
                for box in checkboxes.all():box.check()
                expect(save).to_be_enabled();save.click()
                expect(page.get_by_role('heading',name='Versión 1 guardada',exact=True)).to_be_visible()
                expect(page.get_by_text('Estos patrones no detectan toda la información sensible.',exact=True)).to_be_visible()
                expect(page.get_by_text('El porcentaje indica cumplimiento estructural; no mide calidad ni garantiza seguridad.',exact=True)).to_be_visible()
                expect(page.get_by_text(re.compile('Secuencia numérica .*Revisada y confirmada'))).to_have_count(2)
                report.update(aprobado=True,panel_publicacion=True,objetivo_sin_persistir_antes_confirmar=True,
                              guardado_confirmado=True,alertas_genericas=2,alertas_documento=1,duplicado_sobre_dni=False,
                              avisos_conservados=True,navegador=browser.version)
            finally:browser.close()
    except Exception as error:
        report['error_tipo']=type(error).__name__
        import traceback
        report['lineas']=[f.lineno for f in traceback.extract_tb(error.__traceback__) if f.filename==__file__]
    finally:
        for process in reversed(processes):
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        if engine is not None:
            with engine.begin() as c:
                assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
                c.execute(text('DELETE FROM usuario WHERE correo=ANY(:emails)'),{'emails':accounts})
                if candidate:
                    c.execute(text('SELECT pg_advisory_xact_lock(90404)'))
                    c.execute(text('DELETE FROM regla WHERE id=:id'),{'id':candidate})
                    c.execute(text('UPDATE regla SET activa=true WHERE id=:id'),{'id':original['id']})
            engine.dispose()
        folder=ROOT/'local-data/detector-numerico';folder.mkdir(parents=True,exist_ok=True)
        name='navegador-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
        (folder/name).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=True))
    return 0 if report['aprobado'] else 1


if __name__=='__main__':raise SystemExit(main())
