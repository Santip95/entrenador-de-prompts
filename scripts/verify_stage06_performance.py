"""NF-03: HTTP real, cinco usuarios, 100 revisiones y 100 guardados de 10000 caracteres."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import json
import math
import os
import platform
import secrets
import subprocess
import sys
import threading
import time
from uuid import uuid4

import httpx
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.engine import make_url
from verify_stage04_browser import ROOT,API,ORIGIN,listening,ready

sys.path.insert(0,str(ROOT/'backend'))
from app.core.config import Settings
from app.operations.backups import database_engine,migrate_isolated
from app.application.access import AccessService

DATABASE='entrenador_prompts_ops_test'

def statistics(samples):
    ordered=sorted(s['ms'] for s in samples)
    return {'muestras':len(samples),'errores':sum(s['status']!=s['esperado'] for s in samples),
            'min_ms':round(ordered[0],3),'mediana_ms':round((ordered[49]+ordered[50])/2,3),
            'p95_ms':round(ordered[math.ceil(.95*len(ordered))-1],3),'max_ms':round(ordered[-1],3),
            'metodo_p95':'Rango mas cercano: muestra ordenada ceil(0.95*N), sin descartar errores ni lentas.'}

def main():
    folder=ROOT/'local-data/etapa06';folder.mkdir(exist_ok=True,parents=True)
    stamp=datetime.now(timezone.utc)
    report={'fecha_utc':stamp.isoformat(),'base':DATABASE,'usuarios_concurrentes':5,'solicitudes_por_usuario_y_endpoint':20,
            'caracteres_texto_libre':10000,'calentamiento_por_endpoint':10,'codigo_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'equipo':{'sistema':platform.platform(),'arquitectura':platform.machine(),'python':platform.python_version()},
            'alcance':'HTTP localhost hasta cuerpo recibido: revisar incluye motor; guardar incluye reevaluacion, PostgreSQL y commit. Login y preparacion de token fuera de latencia de guardado. Entorno ya instalado.'}
    processes=[];clients=[];emails=[];owner=None
    try:
        if listening(18000):raise RuntimeError('Puerto temporal ocupado; no detener procesos ajenos.')
        s=Settings();migrate_isolated(s,DATABASE);owner=database_engine(s,DATABASE)
        with owner.connect() as c:assert c.scalar(text('SELECT current_database()'))==DATABASE
        key=secrets.token_urlsafe(48)
        settings=s.model_copy(update={'app_env':'test','csrf_signing_key':SecretStr(key),'review_signing_key':SecretStr(secrets.token_urlsafe(48)),'alert_fingerprint_key':SecretStr(secrets.token_urlsafe(48))})
        runtime=make_url(s.resolved_database_url()).set(database=DATABASE).render_as_string(hide_password=False)
        variables=os.environ.copy();variables.update(APP_ENV='test',PUBLIC_ORIGIN=ORIGIN,DATABASE_URL=runtime,CSRF_SIGNING_KEY=key,REVIEW_SIGNING_KEY=settings.review_signing_key.get_secret_value(),ALERT_FINGERPRINT_KEY=settings.alert_fingerprint_key.get_secret_value())
        process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','18000','--no-access-log','--no-proxy-headers'],cwd=ROOT/'backend',env=variables,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(process);ready(API+'/health',process)
        service=AccessService(owner,settings)
        fixtures=json.loads((ROOT/'fixtures/evaluation_cases.json').read_text(encoding='utf-8'))['casos']
        draft=json.loads(json.dumps(next(r['entrada'] for r in fixtures if r['id']=='CP-01')))
        draft.update(modo='libre',componentes_confirmados=True,texto_libre=('Contenido ficticio de carga. '*400)[:10000])
        assert len(draft['texto_libre'])==10000
        users=[]
        for index in range(5):
            email='load06-'+str(uuid4())+'@example.invalid';emails.append(email);password=secrets.token_urlsafe(32)
            service.register(email,password)
            client=httpx.Client(base_url=API+'/api/v1',headers={'Origin':ORIGIN},timeout=30,trust_env=False);clients.append(client)
            assert client.post('/auth/login',json={'correo':email,'password':password}).status_code==200
            csrf=client.get('/auth/csrf').json()['csrf_token'];client.headers['X-CSRF-Token']=csrf
            challenges=client.get('/desafios?limit=100').json()['items']
            challenge=next(r for r in challenges if r['desafio']['codigo']=='D01_CORREO_REUNION')
            entry={'modo':'libre','desafio_id':challenge['id']};start=client.post('/practicas/preparar',json=entry).json()
            creation=client.post('/practicas',json={**entry,'token_inicio':start['token_inicio'],'coincidencias_confirmadas':[],'request_id':str(uuid4())});assert creation.status_code==201
            users.append((index,client,creation.json()['id']))
        for index,client,pid in users:
            for _ in range(2):
                r=client.post(f'/practicas/{pid}/revisar',json=draft);assert r.status_code==200
                preview=r.json();assert preview['coincidencias']==[] and len(preview['texto'])==10000
                r=client.post(f'/practicas/{pid}/versiones',json={'borrador':draft,'token_revision':preview['token_revision'],'coincidencias_confirmadas':[],'request_id':str(uuid4())});assert r.status_code==201
        for operation in ('revisar','guardar'):
            barrier=threading.Barrier(5)
            def worker(user):
                index,client,pid=user;samples=[]
                # Token fresco despues del calentamiento, fuera del tiempo de guardar.
                if operation=='guardar':
                    response=client.post(f'/practicas/{pid}/revisar',json=draft);assert response.status_code==200
                    token=response.json()['token_revision']
                barrier.wait(timeout=30)
                for sequence in range(20):
                    body=draft if operation=='revisar' else {'borrador':draft,'token_revision':token,'coincidencias_confirmadas':[],'request_id':str(uuid4())}
                    path=f'/practicas/{pid}/'+('revisar' if operation=='revisar' else 'versiones')
                    before=time.perf_counter()
                    try:
                        response=client.post(path,json=body);status=response.status_code
                    except httpx.HTTPError:status=0
                    samples.append({'usuario':index+1,'secuencia':sequence+1,'ms':round((time.perf_counter()-before)*1000,6),'status':status,'esperado':200 if operation=='revisar' else 201})
                return samples
            with ThreadPoolExecutor(5) as pool:samples=[s for batch in pool.map(worker,users) for s in batch]
            summary=statistics(samples);summary['aprobado']=summary['errores']==0 and summary['p95_ms']<2000
            report[operation]={'resumen':summary,'muestras':samples}
            print(operation,json.dumps(summary),flush=True)
        with owner.connect() as c:
            counts=c.execute(text('SELECT count(*) FROM version_prompt v JOIN practica p ON p.id=v.practica_id JOIN usuario u ON u.id=p.usuario_id WHERE u.correo=ANY(:emails)'),{'emails':emails}).scalar()
            assert counts==110 # 10 calentamiento + 100 guardados
        report['versiones_persistidas']=counts
        report['aprobado']=all(report[k]['resumen']['aprobado'] for k in ('revisar','guardar'))
        hardware=subprocess.run(['powershell.exe','-NoProfile','-Command',"$cpu=Get-CimInstance Win32_Processor | Select-Object -First 1; $ram=Get-CimInstance Win32_ComputerSystem; @{cpu=$cpu.Name; nucleos=$cpu.NumberOfCores; logicos=$cpu.NumberOfLogicalProcessors; memoria_gib=[math]::Round($ram.TotalPhysicalMemory/1GB,2)} | ConvertTo-Json -Compress"],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        if hardware.returncode==0:report['equipo'].update(json.loads(hardware.stdout))
    except Exception as error:
        report['aprobado']=False;report['fallo_tipo']=type(error).__name__
        print('Medicion no completada; tipo:',type(error).__name__,'sin datos privados.',flush=True)
    finally:
        for client in clients:client.close()
        for process in processes:process.terminate();process.wait(timeout=10)
        if owner:
            with owner.begin() as c:
                assert c.scalar(text('SELECT current_database()'))==DATABASE
                c.execute(text('DELETE FROM usuario WHERE correo=ANY(:emails)'),{'emails':emails})
            owner.dispose()
        path=folder/('rendimiento-'+stamp.strftime('%Y%m%dT%H%M%S')+'.json')
        path.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print('Informe:',path.relative_to(ROOT))
    return 0 if report.get('aprobado') else 1

if __name__=='__main__':raise SystemExit(main())
