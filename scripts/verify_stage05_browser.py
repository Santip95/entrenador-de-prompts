"""Panel real + Chrome/Edge independientes. Sólo PostgreSQL de pruebas y datos ficticios."""
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from urllib.parse import urlsplit
import json
import os
import re
import secrets
import subprocess
import sys
import time

import httpx
from cryptography.fernet import Fernet
from playwright.sync_api import sync_playwright,expect
from sqlalchemy import create_engine,text
from verify_stage04_browser import listening,ready,ROOT,ORIGIN,API

sys.path.insert(0,str(ROOT/'backend'))
from app.core.config import Settings
from app.application.access import AccessService
from app.operations.journal import DeletionJournal


def main():
    folder=ROOT/'local-data/etapa05';folder.mkdir(parents=True,exist_ok=True)
    report={'fecha':'2026-11-07','base':'entrenador_prompts_test','pasos':[]}
    processes=[];browsers=[];owner=None;users=[];original_rules=[];created_code='WEB05_'+uuid4().hex.upper();external=[];step='preparación';admin_id=None
    temp=TemporaryDirectory(prefix='entrenador-stage05-')
    def passed(message):report['pasos'].append({'comprobacion':message,'aprobado':True});print('APROBADO:',message,flush=True)
    try:
        local=Settings();owner=create_engine(local.resolved_migration_url(test=True),hide_parameters=True)
        with owner.connect() as c:
            assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
            original_rules=[dict(r) for r in c.execute(text('SELECT id,activa FROM regla')).mappings()]
            original_criterion=dict(c.execute(text("SELECT nombre,descripcion,actualizado_en FROM criterio WHERE codigo='C1'")).mappings().one())
        if listening(15173) or listening(18000):raise RuntimeError('Puertos de ensayo ocupados; no detener procesos ajenos.')
        private=Path(temp.name);(private/'keys').mkdir();(private/'diary').mkdir();key=private/'keys/journal.key';key.write_bytes(Fernet.generate_key())
        journal=DeletionJournal(private/'diary/journal.fernet',key,private/'keys/anchor');journal.initialize()
        variables=os.environ.copy();variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,DATABASE_URL=local.resolved_test_database_url(),CSRF_SIGNING_KEY=secrets.token_urlsafe(48),REVIEW_SIGNING_KEY=secrets.token_urlsafe(48),ALERT_FINGERPRINT_KEY=secrets.token_urlsafe(48),TFG_API_PROXY_TARGET=API,DELETION_JOURNAL_LOCATION=str(journal.path),DELETION_JOURNAL_KEY_FILE=str(journal.key_file),DELETION_JOURNAL_ANCHOR_FILE=str(journal.anchor))
        settings=local.model_copy(update={'csrf_signing_key':__import__('pydantic').SecretStr(variables['CSRF_SIGNING_KEY'])})
        service=AccessService(owner,settings)
        password='Una frase ficticia de navegador etapa cinco'
        email='web05-'+str(uuid4())+'@example.invalid';admin_email='web05-admin-'+str(uuid4())+'@example.invalid';users=[email,admin_email]
        for mail in users:service.register(mail,password)
        with owner.begin() as c:
            admin_id=c.scalar(text("UPDATE usuario SET rol='administrador' WHERE correo=:mail RETURNING id"),{'mail':admin_email})
        api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(api);ready(API+'/health',api)
        vite=subprocess.Popen(['node','node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','15173'],cwd=ROOT/'frontend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW);processes.append(vite);ready(ORIGIN,vite)
        with sync_playwright() as pw:
            chrome=pw.chromium.launch(channel='chrome',headless=True);edge=pw.chromium.launch(channel='msedge',headless=True);browsers=[chrome,edge]
            ca=chrome.new_context(viewport={'width':1280,'height':900});cb=edge.new_context();cc=chrome.new_context(viewport={'width':1280,'height':900})
            a,b,admin=ca.new_page(),cb.new_page(),cc.new_page()
            report['navegadores']=[{'canal':'chrome','version':chrome.version},{'canal':'msedge','version':edge.version}]
            for page in (a,b,admin):
                page.on('request',lambda request:external.append(urlsplit(request.url).scheme+'://'+str(urlsplit(request.url).hostname)) if urlsplit(request.url).scheme in ('http','https') and urlsplit(request.url).hostname!='127.0.0.1' else None)
                page.goto(ORIGIN)
            def heading(page,title):expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible(timeout=15000)
            def login(page,mail):
                heading(page,'Ingresar');page.get_by_label('Correo',exact=True).fill(mail);page.get_by_label('Contraseña',exact=True).fill(password);page.get_by_role('button',name='Ingresar',exact=True).click();heading(page,'Comenzar una práctica')
            login(a,email);login(b,email);login(admin,admin_email)
            admin.get_by_role('button',name='Administración',exact=True).click();heading(admin,'Administración')
            step='crear editar y publicar desafío desde panel'
            admin.get_by_role('button',name='Crear desafío borrador',exact=True).click()
            admin.get_by_label('Código estable',exact=True).fill(created_code);admin.get_by_label('Título',exact=True).fill('Ensayo ficticio de administración');admin.get_by_label('Consigna',exact=True).fill('Declarar una solicitud ficticia.')
            admin.get_by_role('button',name='Guardar borrador',exact=True).click();expect(admin.get_by_text('Cambio confirmado por el servidor.',exact=True)).to_be_visible()
            a.reload();heading(a,'Comenzar una práctica');expect(a.get_by_label('Desafío',exact=True).locator('option').filter(has_text='Ensayo ficticio de administración')).to_have_count(0)
            admin.get_by_role('button',name='Editar '+created_code,exact=True).click();admin.get_by_label('Título',exact=True).fill('Ensayo administrativo publicado');admin.get_by_role('button',name='Guardar borrador',exact=True).click()
            expect(admin.get_by_text('Cambio confirmado por el servidor.',exact=True)).to_be_visible()
            admin.get_by_role('button',name='Publicar '+created_code,exact=True).click();expect(admin.get_by_role('button',name='Publicar '+created_code,exact=True)).to_be_disabled()
            a.reload();heading(a,'Comenzar una práctica');expect(a.get_by_label('Desafío',exact=True).locator('option').filter(has_text='Ensayo administrativo publicado')).to_have_count(1)
            passed('HU-09: borrador oculto, edición sin publicar y publicación visible en el catálogo real')
            step='guardar V1 antes de nueva regla'
            a.get_by_label('Desafío',exact=True).select_option(label='Solicitar una reunión');a.get_by_role('button',name='Revisar inicio',exact=True).click();a.get_by_role('button',name='Confirmar inicio y continuar',exact=True).click();heading(a,'Construir el prompt')
            cases={r['id']:r for r in json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']};component=cases['CP-31']['entrada']['componentes']
            a.get_by_label('Tarea',exact=True).fill(component['tarea']['texto']);a.get_by_label('Acción',exact=True).select_option(component['tarea']['accion_id']);a.get_by_label('Contexto',exact=True).fill(component['contexto']['texto']);a.get_by_label('Finalidad',exact=True).fill(component['contexto']['campos']['finalidad']);a.get_by_label(re.compile('Usar solo datos ficticios')).check();a.get_by_label('Formato',exact=True).select_option('correo')
            a.get_by_role('button',name='Revisar prompt',exact=True).click();a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('heading',name='Versión 1 guardada',exact=True)).to_be_visible()
            with owner.connect() as c:
                first=dict(c.execute(text('SELECT v.* FROM version_prompt v JOIN practica p ON p.id=v.practica_id JOIN usuario u ON u.id=p.usuario_id WHERE u.correo=:mail'),{'mail':email}).mappings().one())
                current=dict(c.execute(text("SELECT r.* FROM regla r JOIN criterio c ON c.id=r.criterio_id WHERE c.codigo='C2' AND r.activa")).mappings().one())
            step='crear y publicar nueva regla desde panel'
            admin.get_by_role('button',name='Reglas',exact=True).click();admin.get_by_role('button',name=f"Crear versión desde C2 v{current['version']}",exact=True).click()
            admin.get_by_label('Mensaje cumple',exact=True).fill('Contexto declarado bajo nueva versión ficticia.');admin.get_by_role('button',name='Crear versión inactiva',exact=True).click()
            expect(admin.get_by_text('Cambio confirmado por el servidor.',exact=True)).to_be_visible()
            admin.get_by_role('button',name=f"Publicar C2 v{current['version']+1}",exact=True).click();expect(admin.get_by_role('button',name=f"Publicar C2 v{current['version']+1}",exact=True)).to_be_disabled()
            a.get_by_role('button',name='Crear nueva versión',exact=True).click();heading(a,'Construir el prompt');a.get_by_label('Fecha de referencia',exact=True).fill('2030-05-10');a.get_by_label('Destinatario',exact=True).fill('Equipo ficticio');a.get_by_label('Detalle del formato',exact=True).fill('Asunto y cierre')
            a.get_by_role('button',name='Revisar prompt',exact=True).click();a.get_by_role('button',name='Confirmar y guardar versión',exact=True).click();expect(a.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
            a.get_by_role('button',name='Comparar versiones',exact=True).click();a.get_by_role('button',name='Comparar',exact=True).click();expect(a.get_by_text(re.compile('No se calcula mejora.'))).to_be_visible()
            with owner.connect() as c:assert dict(c.execute(text('SELECT * FROM version_prompt WHERE id=:id'),{'id':first['id']}).mappings().one())==first
            passed('AT-23 / INT-03: publicación desde panel, V1 intacta y V2 no comparable, sin delta ni resolución')
            step='criterios presentación y teclado a 360 px'
            admin.get_by_role('button',name='Criterios',exact=True).click();admin.get_by_role('button',name='Editar presentación C1',exact=True).click();admin.get_by_label('Nombre del criterio',exact=True).fill('Tarea declarada');admin.get_by_role('button',name='Guardar presentación',exact=True).click();expect(admin.get_by_text('Cambio confirmado por el servidor.',exact=True)).to_be_visible()
            admin.set_viewport_size({'width':360,'height':780});admin.get_by_role('button',name='Cuentas',exact=True).click();admin.keyboard.press('Tab');assert admin.evaluate("document.activeElement?.tagName") in ('BUTTON','INPUT','TEXTAREA','SELECT')
            assert admin.evaluate('document.documentElement.scrollWidth<=innerWidth')
            admin.screenshot(path=str(folder/'panel-360.png'),full_page=True);passed('Panel con etiquetas, foco de teclado y sin desborde a 360 px; revisión humana completa pendiente')
            step='bloqueo desde panel con dos navegadores independientes'
            old_a=ca.cookies();old_b=cb.cookies()
            admin.get_by_role('button',name='Bloquear '+email,exact=True).click();expect(admin.get_by_role('button',name='Bloquear '+email,exact=True)).to_be_disabled()
            for page in (a,b):page.get_by_role('button',name='Historial',exact=True).click();heading(page,'Ingresar')
            admin.get_by_role('button',name='Desbloquear '+email,exact=True).click();expect(admin.get_by_role('button',name='Desbloquear '+email,exact=True)).to_be_disabled()
            for context,page,cookies in ((ca,a,old_a),(cb,b,old_b)):
                context.add_cookies(cookies);page.reload();heading(page,'Ingresar');login(page,email)
            passed('INT-02 / SEC-01/02: bloqueo y desbloqueo desde panel; Chrome/Edge revocados, cookies antiguas rechazadas')
            step='eliminación de práctica desde pantallas'
            a.get_by_role('button',name='Historial',exact=True).click();a.get_by_role('button',name='Abrir práctica',exact=True).click();expect(a.get_by_role('heading',name='Versión 2 guardada',exact=True)).to_be_visible()
            a.get_by_role('button',name='Eliminar esta práctica',exact=True).click();expect(a.get_by_role('button',name='Confirmar eliminación de práctica',exact=True)).to_be_disabled();a.get_by_label('Confirmo que quiero eliminar toda esta práctica.',exact=True).check();a.get_by_role('button',name='Confirmar eliminación de práctica',exact=True).click();heading(a,'Historial propio');expect(a.get_by_text('No hay prácticas para estos filtros.',exact=False)).to_be_visible()
            with owner.connect() as c:assert not c.scalar(text('SELECT EXISTS(SELECT FROM version_prompt WHERE practica_id=:id)'),{'id':first['practica_id']})
            passed('SEC-11: eliminación propia confirmada desde pantalla y cascada de versiones verificada')
            step='eliminación de cuenta desde formulario'
            a.get_by_role('button',name='Perfil',exact=True).click();heading(a,'Mi cuenta');a.get_by_role('button',name='Eliminar mi cuenta',exact=True).click();a.get_by_label('Contraseña actual para eliminar la cuenta',exact=True).fill(password);a.get_by_label('Confirmo que quiero eliminar mi cuenta y todo su contenido.',exact=True).check();a.get_by_role('button',name='Confirmar eliminación de cuenta',exact=True).click();heading(a,'Ingresar')
            b.get_by_role('button',name='Historial',exact=True).click();heading(b,'Ingresar')
            assert len(journal.entries())==2 and all(r['completado_en'] for r in journal.entries())
            passed('SEC-11: cuenta eliminada con contraseña/CSRF; ambas sesiones retiradas; diario durable completado')
            report['recorrido_funcional_aprobado']=True;report['nf02_aprobado']=False;report['aprobado']=False
            report['origenes_externos']=sorted(set(external));report['nf02']='Pendiente del entorno y de la investigación previa; no se desactivó el antivirus ni se inspeccionaron payloads.'
    except Exception as error:
        report['recorrido_funcional_aprobado']=False;report['fallo']={'paso':step,'tipo':type(error).__name__}
        print('FALLO:',step,type(error).__name__,'(detalles privados omitidos)',flush=True)
        for label in ('a','admin'):
            if label in locals():
                try:locals()[label].screenshot(path=str(folder/('fallo-'+label+'.png')),full_page=True)
                except Exception:pass
    finally:
        for browser in browsers:
            try:browser.close()
            except Exception:pass
        for process in reversed(processes):
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
        if owner:
            with owner.begin() as c:
                assert c.scalar(text('SELECT current_database()'))=='entrenador_prompts_test'
                c.execute(text('DELETE FROM usuario WHERE correo=ANY(:mails)'),{'mails':users})
                c.execute(text('DELETE FROM desafio_criterio WHERE desafio_id IN(SELECT id FROM desafio WHERE codigo=:code)'),{'code':created_code})
                c.execute(text('DELETE FROM desafio WHERE codigo=:code'),{'code':created_code})
                # creador se desvincula al borrar la cuenta; sólo IDs nuevos bajo
                # este ensayo exclusivo, inventariados antes de iniciar el panel.
                if original_rules:
                    c.execute(text('UPDATE regla SET activa=false'))
                    c.execute(text('DELETE FROM regla WHERE NOT(id=ANY(:ids))'),{'ids':[r['id'] for r in original_rules]})
                    for row in original_rules:c.execute(text('UPDATE regla SET activa=:activa WHERE id=:id'),row)
                # C1 se restaurará desde la instantánea tomada al iniciar.
                if 'original_criterion' in locals():c.execute(text("UPDATE criterio SET nombre=:nombre,descripcion=:descripcion,actualizado_en=:actualizado_en WHERE codigo='C1'"),original_criterion)
            owner.dispose()
        temp.cleanup()
        (folder/'navegadores.json').write_text(json.dumps(report,ensure_ascii=True,indent=2),encoding='utf-8')
    return 2 if report.get('recorrido_funcional_aprobado') else 1

if __name__=='__main__':raise SystemExit(main())
