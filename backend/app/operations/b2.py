"""Adaptador optativo B2 Native v4. No crea cuentas/buckets ni se ejecuta al arrancar.

Las pruebas del adaptador usan transporte simulado; no acreditan B2 real.
"""
from datetime import datetime,timezone,timedelta
import hashlib
import re
from pathlib import Path
from urllib.parse import quote,urlsplit
import httpx
from app.core.config import ConfigurationError
from app.operations.backups import verify_manifest,retained

PREFIX='entrenador-prompts/'
PATTERN=re.compile(r'^entrenador-prompts/(tfg-(\d{8}T\d{6})-[0-9a-f]{32})\.(backup\.age|manifest\.json|manifest\.auth)$')


def cloud_plan(versions,unfinished,now):
    """Incluir versiones ocultas/antiguas y partes de cargas inconclusas."""
    newest={};dates={}
    for row in sorted(versions,key=lambda r:r['uploadTimestamp'],reverse=True):
        match=PATTERN.fullmatch(row['fileName'])
        if not match:continue
        if row['action'] in {'start','folder'}:continue
        newest.setdefault(row['fileName'],row['fileId'])
        stamp=datetime.strptime(match[2],'%Y%m%dT%H%M%S').replace(tzinfo=timezone.utc)
        dates[match[1]]={'archivo':match[1],'fecha_utc':stamp.isoformat()}
    keep=retained(list(dates.values()),now)
    deletes=[]
    for row in versions:
        match=PATTERN.fullmatch(row['fileName'])
        if not match:continue
        if row['action'] in {'start','folder'}:continue
        if match[1] not in keep or newest[row['fileName']]!=row['fileId'] or row['action']=='hide':deletes.append(row)
    cancel=[row for row in unfinished if PATTERN.fullmatch(row['fileName']) and datetime.fromtimestamp(row['uploadTimestamp']/1000,timezone.utc)<now-timedelta(days=1)]
    return deletes,cancel


class B2Storage:
    def __init__(self,settings,client=None):
        if not all((settings.b2_bucket,settings.b2_bucket_id,settings.b2_key_id,settings.b2_application_key)):
            raise ConfigurationError('Faltan credenciales locales B2. No se contacta al proveedor.')
        self.settings=settings
        self.client=client or httpx.Client(timeout=120,follow_redirects=False,trust_env=False)
        self.auth=None;self.url=None

    @staticmethod
    def trusted(url):
        parsed=urlsplit(url)
        if parsed.scheme!='https' or parsed.username or parsed.password or not parsed.hostname or not (parsed.hostname.endswith('.backblazeb2.com') or parsed.hostname.endswith('.backblaze.com')):
            raise ConfigurationError('Destino de B2 no permitido.')
        return url

    def authorize(self):
        response=self.client.get('https://api.backblazeb2.com/b2api/v4/b2_authorize_account',auth=(self.settings.b2_key_id,self.settings.b2_application_key.get_secret_value()))
        response.raise_for_status();data=response.json();api=data['apiInfo']['storageApi'];allowed=api['allowed']
        buckets=allowed.get('buckets') or []
        if not any(b['id']==self.settings.b2_bucket_id and b['name']==self.settings.b2_bucket for b in buckets):
            raise ConfigurationError('Usar una clave limitada al bucket privado previsto; no una clave maestra.')
        if allowed.get('namePrefix')!=PREFIX or not {'listFiles','writeFiles','deleteFiles','listBuckets'}<=set(allowed['capabilities']):
            raise ConfigurationError('La clave debe limitarse al prefijo del proyecto y permitir comprobación y purga.')
        self.url=self.trusted(api['apiUrl']);self.auth=data['authorizationToken']
        bucket=self.call('b2_list_buckets',{'accountId':data['accountId'],'bucketId':self.settings.b2_bucket_id})['buckets']
        if len(bucket)!=1 or bucket[0]['bucketType']!='allPrivate':
            raise ConfigurationError('El bucket debe ser privado.')

    def call(self,method,data):
        response=self.client.post(self.url+'/b2api/v4/'+method,json=data,headers={'Authorization':self.auth})
        response.raise_for_status();return response.json()

    def upload(self,manifest):
        info,archive=verify_manifest(self.settings,manifest)
        if info.get('origen','entrenador_prompts')!=self.settings.postgres_db:
            raise ConfigurationError('El bucket y prefijo deben usarse para un solo entorno; no mezclar copias de pruebas y desarrollo.')
        self.authorize()
        paths=[archive,Path(manifest),Path(manifest).with_name(Path(manifest).name.replace('.manifest.json','.manifest.auth'))]
        for path in paths:
            if not PATTERN.fullmatch(PREFIX+path.name):raise ConfigurationError('Nombre ajeno al proyecto.')
            target=self.call('b2_get_upload_url',{'bucketId':self.settings.b2_bucket_id})
            raw=path.read_bytes()
            response=self.client.post(self.trusted(target['uploadUrl']),content=raw,headers={'Authorization':target['authorizationToken'],'X-Bz-File-Name':quote(PREFIX+path.name,safe='/'),'X-Bz-Content-Sha1':hashlib.sha1(raw).hexdigest(),'Content-Type':'application/octet-stream','Content-Length':str(len(raw))})
            response.raise_for_status()
            if response.json().get('contentSha1')!=hashlib.sha1(raw).hexdigest():raise ConfigurationError('B2 no confirmó el hash de la carga.')
        return {'archivos_subidos':3,'limite':'Verificar descarga y restauración reales antes de acreditar operación externa.'}

    def listing(self,method,versioned):
        rows=[];params={'bucketId':self.settings.b2_bucket_id,'prefix':PREFIX,'maxFileCount':1000};seen=set()
        while True:
            data=self.call(method,params);rows.extend(data['files'])
            cursor=(data.get('nextFileName'),data.get('nextFileId')) if versioned else (None,data.get('nextFileId'))
            if not any(cursor):break
            if cursor in seen:raise ConfigurationError('Paginación B2 inválida.')
            seen.add(cursor)
            if versioned:params.update(startFileName=cursor[0],startFileId=cursor[1])
            else:params['startFileId']=cursor[1]
        return rows

    def purge(self):
        self.authorize()
        versions=self.listing('b2_list_file_versions',True)
        unfinished=self.listing('b2_list_unfinished_large_files',False)
        deletes,cancel=cloud_plan(versions,unfinished,datetime.now(timezone.utc))
        for row in deletes:self.call('b2_delete_file_version',{'fileName':row['fileName'],'fileId':row['fileId']})
        for row in cancel:self.call('b2_cancel_large_file',{'fileId':row['fileId']})
        # No declarar purga por haber enviado peticiones; volver a enumerar.
        pending=cloud_plan(self.listing('b2_list_file_versions',True),self.listing('b2_list_unfinished_large_files',False),datetime.now(timezone.utc))
        if any(pending):raise ConfigurationError('B2 aún conserva objetos o partes fuera de política.')
        return {'versiones_borradas':len(deletes),'cargas_canceladas':len(cancel),'purga_verificada_en_api':True}

    def close(self):self.client.close()
