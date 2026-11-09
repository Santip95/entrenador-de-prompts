"""Instrumentación de pruebas: AX/DOM e iniciadores CDP, sin guardar cuerpos/secretos."""
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
import builtins
import json
import re
import traceback
import httpx

from playwright.sync_api import sync_playwright
from playwright.sync_api import expect

class Audit:
    def __init__(self):
        self.pages=[];self.sessions={};self.requests=[];self.finished={};self.markers={};self.snapshots=[];self.script_checks=[];self.extended=[];self.seen=set();self.failures=[];self.raw_checks=[]

    @staticmethod
    def origin(url):
        parsed=urlsplit(url)
        return parsed.scheme+'://'+str(parsed.hostname)+((':'+str(parsed.port)) if parsed.port else '') if parsed.scheme in ('http','https') else parsed.scheme+':'

    def attach(self,page):
        self.pages.append(page)
        session=page.context.new_cdp_session(page);self.sessions[page]=session
        session.send('Network.enable');session.send('Accessibility.enable')
        def request(event):
            r=event['request'];url=r['url'];origin=self.origin(url)
            if urlsplit(url).hostname=='127.0.0.1':
                if '/practicas' in url and 'postData' in r:
                    try:
                        data=json.loads(r['postData'])
                        def texts(value):
                            if isinstance(value,dict):
                                for key,v in value.items():
                                    if key in ('objetivo','texto','texto_libre') and isinstance(v,str) and len(v)>=10:self.markers[v]=key
                                    elif isinstance(v,dict):texts(v)
                        texts(data)
                    except (ValueError,TypeError):pass
                return
            if urlsplit(url).scheme not in ('http','https'):return
            frames=event.get('initiator',{}).get('stack',{}).get('callFrames',[])
            stack=[{'origen':self.origin(f['url']),'funcion':f.get('functionName','') if re.fullmatch(r'[A-Za-z_$][\w$]{0,60}',f.get('functionName','')) else 'anonima'} for f in frames[:4] if f.get('url')]
            body=r.get('postData','')
            self.requests.append({'origen':origin,'metodo':r['method'],'tipo':event.get('type'),'iniciador_tipo':event.get('initiator',{}).get('type'),'iniciadores':stack,'bytes_cuerpo_visibles':len(body.encode()),'coincide_texto_ficticio_visible':any(m in body for m in self.markers),'coincidencias_metadatos':[{'campo':kind,'longitud':len(m)} for m,kind in self.markers.items() if m in body],'marcadores_disponibles':len(self.markers)})
            self.finished[event['requestId']]={'session':session,'origen':origin,'tipo':event.get('type')}
        def finished(event):
            info=self.finished.pop(event['requestId'],None)
            if not info or info['tipo']!='Script':return
            try:
                body=session.send('Network.getResponseBody',{'requestId':event['requestId']})
                if body.get('base64Encoded'):return
                source=body.get('body','')
                self.script_checks.append({'origen':info['origen'],'identificador_KasperskyLab':'KasperskyLab' in source,'contiene_nombre_Kaspersky':'Kaspersky' in source,'bytes':len(source.encode())})
            except Exception:self.script_checks.append({'origen':info['origen'],'cuerpo_no_disponible':True})
        session.on('Network.requestWillBeSent',request);session.on('Network.loadingFinished',finished)

    def snapshot(self,label):
        self.extra_checks(label)
        if not self.raw_checks and self.pages:
            try:
                root=Path(__file__).resolve().parents[1]
                agent=self.pages[0].evaluate('navigator.userAgent')
                generic=httpx.get('http://127.0.0.1:15173',timeout=5).text
                browser_agent=httpx.get('http://127.0.0.1:15173',headers={'User-Agent':agent},timeout=5).text
                self.raw_checks.append({'archivo_index_contiene_dominio':'kaspersky-labs.com' in (root/'frontend/index.html').read_text(encoding='utf-8'),'httpx_generico_contiene_dominio':'kaspersky-labs.com' in generic,'httpx_useragent_navegador_contiene_dominio':'kaspersky-labs.com' in browser_agent})
            except Exception as error:self.raw_checks.append({'error_tipo':type(error).__name__})
        for number,page in enumerate(self.pages):
            if page.is_closed():continue
            try:
                dom=page.evaluate('''() => {
                  const visible=e=>!!(e.getClientRects().length)&&getComputedStyle(e).visibility!=='hidden';
                  const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                  const controls=[...document.querySelectorAll('input,select,textarea,button')].filter(visible);
                  const missing=[]; controls.forEach((e,i)=>{for(const attr of ['aria-describedby','aria-labelledby','aria-controls']) for(const id of (e.getAttribute(attr)||'').split(/\\s+/).filter(Boolean))if(!document.getElementById(id)) missing.push({control:i,tag:e.tagName,attr});});
                  return {ancho:innerWidth,alto:innerHeight,desborde:document.documentElement.scrollWidth>innerWidth,controles:controls.length,referencias_faltantes:missing,ids_duplicados:ids.length-new Set(ids).size,foco_tag:document.activeElement?.tagName,namespace_KasperskyLab:typeof window.KasperskyLab!=='undefined',scripts_externos:[...document.scripts].filter(s=>s.src&&new URL(s.src).hostname!=='127.0.0.1').map(s=>new URL(s.src).origin)};
                }''')
                tree=self.sessions[page].send('Accessibility.getFullAXTree')['nodes']
                roles={'button','textbox','combobox','checkbox','radio','spinbutton','searchbox'}
                unnamed=[node.get('role',{}).get('value') for node in tree if not node.get('ignored') and node.get('role',{}).get('value') in roles and not node.get('name',{}).get('value','').strip()]
                dom.update(paso=label,pagina=number+1,controles_sin_nombre=unnamed)
                self.snapshots.append(dom)
            except Exception as error:self.snapshots.append({'paso':label,'pagina':number+1,'error_tipo':type(error).__name__})

    def extra_checks(self,label):
        try:self._extra_checks(label)
        except Exception as error:
            self.failures.append({'paso':label,'tipo':type(error).__name__,'lineas':[{'archivo':Path(f.filename).name,'linea':f.lineno} for f in traceback.extract_tb(error.__traceback__)]})
            raise

    def _extra_checks(self,label):
        if not self.pages:return
        page=self.pages[0]
        if label.startswith('Inicio a 360') and 'limites' not in self.seen:
            self.seen.add('limites')
            header=page.locator('header').get_by_role('button',name='Comenzar práctica',exact=True)
            expect(header).to_be_enabled();header.focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');expect(header).to_be_focused()
            assert header.evaluate('e=>getComputedStyle(e).outlineColor')=='rgb(255, 207, 102)'
            self.extended.append({'caso':'Foco de teclado en cabecera: contraste calculado 6.328:1 frente a 1.678:1 anterior','aprobado':True})
            page.get_by_role('radio',name='Objetivo propio',exact=True).check()
            objective=page.get_by_role('textbox',name='Objetivo propio',exact=True)
            objective.fill('x'*1001);page.get_by_role('button',name='Revisar inicio',exact=True).click()
            expect(page.get_by_role('alert')).to_be_visible();expect(objective).to_have_value('x'*1001)
            expect(page.get_by_role('alert')).to_be_focused()
            assert 'form-error' in (objective.get_attribute('aria-describedby') or '')
            self.snapshot('NF-01 objetivo invalido: error asociado, foco y texto sin truncar')
            page.get_by_role('radio',name='Desafío publicado',exact=True).check()
            self.extended.append({'caso':'Objetivo 1001 caracteres, foco/error asociado y conservacion','aprobado':True})
        elif label.startswith('CP-12 por pantallas:') and 'red' not in self.seen:
            self.seen.add('red')
            page.get_by_role('button',name='Historial',exact=True).click();page.get_by_role('button',name='Abrir práctica',exact=True).click()
            page.get_by_role('button',name='Crear nueva versión',exact=True).click()
            task=page.get_by_role('textbox',name='Tarea',exact=True);task.fill('x'*2001)
            page.get_by_role('button',name='Revisar prompt',exact=True).click();expect(page.get_by_role('alert')).to_be_visible();expect(task).to_have_value('x'*2001)
            self.snapshot('NF-01 componente 2001 caracteres conservado y error asociado')
            text='Redactá una consulta ficticia para probar el reintento de red.';task.fill(text)
            def abort(route):route.abort('failed')
            page.route('**/api/v1/practicas/*/revisar',abort)
            page.get_by_role('button',name='Revisar prompt',exact=True).click()
            expect(page.get_by_role('alert')).to_contain_text('Tu borrador sigue en memoria');expect(task).to_have_value(text)
            expect(page.get_by_role('button',name='Confirmar y guardar versión',exact=True)).to_have_count(0)
            self.snapshot('Error de red antes del servidor: borrador conservado, sin exito falso')
            page.unroute('**/api/v1/practicas/*/revisar',abort)
            page.get_by_role('button',name='Revisar prompt',exact=True).click();expect(page.get_by_role('button',name='Confirmar y guardar versión',exact=True)).to_be_visible()
            page.get_by_role('button',name='Historial',exact=True).click();page.get_by_role('button',name='Abrir práctica',exact=True).click();page.get_by_role('button',name='Comparar versiones',exact=True).click();page.get_by_role('button',name='Comparar',exact=True).click()
            self.extended.append({'caso':'Componente 2001, corte de red antes de revisar y reintento sin guardar ni duplicar','aprobado':True})
        elif label.startswith('Objetivo no persiste antes') and 'libre_limite' not in self.seen:
            self.seen.add('libre_limite')
            page.get_by_role('button',name='Crear nueva versión',exact=True).click();free=page.get_by_role('textbox',name='Texto libre',exact=True);free.fill('x'*10001)
            page.get_by_label('Confirmo que revisé los componentes que declaré para mi texto libre.',exact=True).check()
            page.get_by_role('button',name='Revisar prompt',exact=True).click();expect(page.get_by_role('alert')).to_be_visible();expect(free).to_have_value('x'*10001)
            self.snapshot('NF-01 texto libre 10001 sin truncar y error asociado')
            page.get_by_role('button',name='Historial',exact=True).click()
            page.locator('article').filter(has=page.get_by_role('heading',name='Objetivo propio',exact=True)).get_by_role('button',name='Abrir práctica',exact=True).click()
            self.extended.append({'caso':'Libre 10001 rechazado sin truncamiento ni version nueva','aprobado':True})
        elif label.startswith('AT-23 / INT-03:') and 'confirmaciones' not in self.seen:
            self.seen.add('confirmaciones')
            page.get_by_role('button',name='Historial',exact=True).click();page.get_by_role('button',name='Abrir práctica',exact=True).click()
            toggle=page.get_by_role('button',name='Eliminar esta práctica',exact=True);expect(toggle).to_be_enabled();toggle.focus();page.keyboard.press('Enter')
            checkbox=page.get_by_label('Confirmo que quiero eliminar toda esta práctica.',exact=True);expect(checkbox).to_be_focused()
            page.keyboard.press('Space');expect(checkbox).to_be_checked();page.keyboard.press('Tab');expect(page.get_by_role('button',name='Confirmar eliminación de práctica',exact=True)).to_be_focused()
            page.keyboard.press('Escape');expect(toggle).to_be_focused();expect(toggle).to_have_attribute('aria-expanded','false')
            page.get_by_role('button',name='Perfil',exact=True).click();account=page.get_by_role('button',name='Eliminar mi cuenta',exact=True);account.focus();page.keyboard.press('Enter')
            expect(page.get_by_label('Contraseña actual para eliminar la cuenta',exact=True)).to_be_focused()
            page.keyboard.press('Escape');expect(account).to_be_focused()
            self.snapshot('Confirmaciones de borrado: teclado, cancelacion y retorno del foco')
            self.extended.append({'caso':'Confirmaciones de practica/cuenta con teclado, Escape y retorno de foco, sin borrar','aprobado':True})
        elif label.startswith('INT-02 / SEC-01/02:') and 'desactivacion' not in self.seen:
            self.seen.add('desactivacion');admin=self.pages[2]
            button=admin.get_by_role('button',name=re.compile(r'^Desactivar web05-(?!admin-)'))
            mail=button.inner_text().removeprefix('Desactivar ').strip()
            button.click();expect(button).to_be_disabled()
            for target in self.pages[:2]:
                target.get_by_role('button',name='Historial',exact=True).click();expect(target.get_by_role('heading',name='Ingresar',exact=True)).to_be_visible()
            unblock=admin.get_by_role('button',name='Desbloquear '+mail,exact=True);unblock.click();expect(unblock).to_be_disabled()
            for target in self.pages[:2]:
                target.get_by_label('Correo',exact=True).fill(mail);target.get_by_label('Contraseña',exact=True).fill('Una frase ficticia de navegador etapa cinco');target.get_by_role('button',name='Ingresar',exact=True).click();expect(target.get_by_role('heading',name='Comenzar una práctica',exact=True)).to_be_visible()
            self.extended.append({'caso':'Desactivacion desde panel revoca Chrome/Edge; reactivacion requiere nuevo ingreso','aprobado':True})

    @contextmanager
    def instrument(self,module):
        audit=self;original_print=builtins.print
        class Browser:
            def __init__(self,actual):self.actual=actual
            def __getattr__(self,name):return getattr(self.actual,name)
            def new_context(self,*args,**kwargs):
                context=self.actual.new_context(*args,**kwargs);context.on('page',audit.attach);return context
        class BrowserType:
            def __init__(self,actual):self.actual=actual
            def launch(self,*args,**kwargs):return Browser(self.actual.launch(*args,**kwargs))
        @contextmanager
        def wrapped():
            with sync_playwright() as pw:
                class Playwright:
                    chromium=BrowserType(pw.chromium)
                yield Playwright()
        def printing(*args,**kwargs):
            if args and args[0]=='APROBADO:':audit.snapshot(str(args[1]))
            original_print(*args,**kwargs)
        old=module.sync_playwright;module.sync_playwright=wrapped;builtins.print=printing
        try:yield
        finally:module.sync_playwright=old;builtins.print=original_print

    def save(self,path):
        failures=[s for s in self.snapshots if s.get('desborde') or s.get('ids_duplicados') or s.get('referencias_faltantes') or s.get('controles_sin_nombre') or s.get('error_tipo')]
        result={'instantaneas':self.snapshots,'comprobaciones_adicionales':self.extended,'fallos_adicionales':self.failures,'hallazgos_accesibilidad':len(failures),'comparacion_html':self.raw_checks,'solicitudes_externas':self.requests,'scripts_externos_inspeccionados':self.script_checks,'nf02_aprobado':False,'limites':'No se bloquearon solicitudes externas ni se altero el antivirus. El corte de red funcional afecta solo /api/v1/practicas/*/revisar. Iniciadores/namespace son evidencia de navegador, no prueba de ruta fisica ni de inocuidad. Coincidencia negativa de texto visible no descarta informacion codificada. AX/DOM no certifica accesibilidad completa.'}
        Path(path).write_text(json.dumps(result,indent=2),encoding='utf-8')
        return result
