from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
from uuid import uuid4
import httpx
import pytest
from cryptography.fernet import Fernet
from app.core.config import Settings,ConfigurationError
from app.operations.backups import purge,retained
from app.operations.b2 import B2Storage,cloud_plan,PREFIX
from test_backups import setup_settings


def test_actual_local_purge_preserves_unknown_files_and_exact_retention(tmp_path):
    settings,j=setup_settings(tmp_path);root=Path(settings.backup_directory)
    now=datetime.now(timezone.utc)
    manifests=[];ciphertext=b'age-encryption.org/v1\nFicticio para probar retencion, no restauracion'
    for age in range(45):
        stamp=now-timedelta(days=age);stem='tfg-'+stamp.strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex
        archive=stem+'.backup.age';(root/archive).write_bytes(ciphertext)
        value={'formato':1,'fecha_utc':stamp.isoformat(),'app_version':'fixture','schema_version':'fixture','archivo':archive,'bytes':len(ciphertext),'sha256':hashlib.sha256(ciphertext).hexdigest()}
        raw=json.dumps(value).encode();(root/(stem+'.manifest.json')).write_bytes(raw);(root/(stem+'.manifest.auth')).write_bytes(Fernet(j.key_file.read_bytes()).encrypt(raw));manifests.append(value)
    unknown=root/'documento-ajeno.txt';unknown.write_text('no tocar');outside=tmp_path/'ajeno.backup';outside.write_text('no tocar')
    expected=retained(manifests,now);result=purge(settings,now)
    assert {p.name for p in root.glob('*.backup.age')}==expected
    assert result['copias_purgadas']==45-len(expected)
    assert unknown.read_text()=='no tocar' and outside.read_text()=='no tocar'
    assert purge(settings,now)['copias_purgadas']==0


def test_cloud_plan_versions_hidden_files_and_abandoned_uploads():
    now=datetime(2026,11,7,17,tzinfo=timezone.utc);versions=[]
    for age in range(45):
        date=now-timedelta(days=age);name=PREFIX+'tfg-'+date.strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex+'.backup.age'
        versions.extend([{'fileName':name,'fileId':str(age)+'-new','uploadTimestamp':int(date.timestamp()*1000),'action':'upload'},{'fileName':name,'fileId':str(age)+'-old','uploadTimestamp':int(date.timestamp()*1000)-1,'action':'upload'}])
    foreign={'fileName':'otro-proyecto/copia.backup','fileId':'ajeno','uploadTimestamp':0,'action':'upload'};versions.append(foreign)
    unfinished=[{**versions[-2],'fileId':'incompleto','uploadTimestamp':int((now-timedelta(days=31)).timestamp()*1000)},foreign]
    deletes,cancels=cloud_plan(versions,unfinished,now)
    assert all(v['fileId'].endswith('-old') or int(v['fileId'].split('-')[0])>6 for v in deletes)
    assert len([v for v in deletes if v['fileId'].endswith('-old')])==45
    assert 'ajeno' not in [v['fileId'] for v in deletes+cancels]
    assert [v['fileId'] for v in cancels]==['incompleto']


@pytest.mark.parametrize('url',['http://api.backblazeb2.com','https://backblazeb2.com.attacker.invalid','https://user:password@api.backblazeb2.com','https://127.0.0.1'])
def test_b2_rejects_untrusted_destinations(url):
    with pytest.raises(ConfigurationError):B2Storage.trusted(url)


def test_missing_cloud_configuration_makes_no_network_requests():
    called=[]
    with httpx.Client(transport=httpx.MockTransport(lambda request:called.append(request))) as client:
        with pytest.raises(ConfigurationError):B2Storage(Settings(_env_file=None),client)
    assert called==[]


def test_b2_purge_uses_real_adapter_with_simulated_paginated_api():
    now=datetime.now(timezone.utc);old=now-timedelta(days=31)
    name=PREFIX+'tfg-'+old.strftime('%Y%m%dT%H%M%S')+'-'+uuid4().hex+'.backup.age'
    files=[{'fileName':name,'fileId':'old-version','action':'upload','uploadTimestamp':int(old.timestamp()*1000)}]
    unfinished=[{'fileName':name,'fileId':'unfinished','uploadTimestamp':int(old.timestamp()*1000)}];calls=[]
    def transport(request):
        method=request.url.path.rsplit('/',1)[-1];calls.append(method)
        if method=='b2_authorize_account':return httpx.Response(200,json={'accountId':'fictitious','authorizationToken':'fictitious','apiInfo':{'storageApi':{'apiUrl':'https://api001.backblazeb2.com','allowed':{'buckets':[{'id':'bucket','name':'bucket'}],'namePrefix':PREFIX,'capabilities':['listFiles','writeFiles','deleteFiles','listBuckets']}}}})
        if method=='b2_list_buckets':return httpx.Response(200,json={'buckets':[{'bucketType':'allPrivate'}]})
        if method=='b2_list_file_versions':return httpx.Response(200,json={'files':list(files),'nextFileName':None,'nextFileId':None})
        if method=='b2_list_unfinished_large_files':return httpx.Response(200,json={'files':list(unfinished),'nextFileId':None})
        if method=='b2_delete_file_version':files.clear();return httpx.Response(200,json={})
        if method=='b2_cancel_large_file':unfinished.clear();return httpx.Response(200,json={})
        raise AssertionError('Operación no esperada')
    settings=Settings(_env_file=None,b2_bucket='bucket',b2_bucket_id='bucket',b2_key_id='fictitious',b2_application_key='fictitious')
    storage=B2Storage(settings,httpx.Client(transport=httpx.MockTransport(transport)))
    try:
        result=storage.purge();assert result['purga_verificada_en_api']
        assert result['versiones_borradas']==1 and result['cargas_canceladas']==1
        assert calls.count('b2_list_file_versions')==2 and calls.count('b2_list_unfinished_large_files')==2
    finally:storage.close()
