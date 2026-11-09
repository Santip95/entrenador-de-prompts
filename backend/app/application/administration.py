"""Catálogo administrativo transaccional; nunca consulta textos de usuarios."""
from copy import deepcopy
import json
from uuid import uuid4

from sqlalchemy import text
from app.application.access import AccessError, AccessService
from app.application.practices import CATALOG_LOCK, hashed
from app.domain.evaluation import CODES, canonical, validate_configuration, EvaluationError
from app.core.config import ROOT_DIR


def conflict():
    raise AccessError(409, 'revision_desactualizada', 'El catálogo cambió. Volvé a cargarlo antes de guardar.')


class AdministrationService:
    def __init__(self, practices):
        self.practices = practices

    @staticmethod
    def lock(c):
        c.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': CATALOG_LOCK})

    def challenge(self, c, identifier):
        row = c.execute(text('SELECT * FROM desafio WHERE id=:id'), {'id': identifier}).mappings().first()
        if not row:
            raise AccessError(404, 'no_encontrado', 'Desafío no encontrado.')
        return {**dict(row), 'configuracion': self.practices.catalog(c, identifier, published=False)['configuracion']}

    def challenges(self, c, limit, cursor):
        rows = c.execute(text('SELECT id FROM desafio WHERE (CAST(:cursor AS uuid) IS NULL OR id>CAST(:cursor AS uuid)) ORDER BY id LIMIT :n'), {'cursor':cursor, 'n':limit+1}).scalars().all()
        return {'items':[self.challenge(c,i) for i in rows[:limit]], 'next_cursor':str(rows[limit-1]) if len(rows)>limit else None}

    def validate(self, c, config, rules=None):
        catalog = self.practices.catalog(c, own=config, published=False)
        try:
            validate_configuration(config, rules if rules is not None else catalog['reglas'], self.practices.catalogs, catalog['criterios'])
        except EvaluationError as error:
            if error.code=='regla_activa_faltante': raise
            raise AccessError(422,'configuracion_invalida','La configuración no es válida: revisá los seis criterios, sus condiciones y los tipos permitidos.') from None

    def write_challenge(self, c, user, data, identifier=None):
        self.lock(c)
        old = self.challenge(c, identifier) if identifier else None
        if old and old['revision'] != data['revision_esperada']:
            conflict()
        # Incluso los borradores se validan: guardarlos nunca los publica.
        self.validate(c, data['configuracion'])
        if not old and c.scalar(text('SELECT EXISTS(SELECT FROM desafio WHERE codigo=:code)'), {'code':data['codigo']}):
            raise AccessError(409, 'codigo_duplicado', 'El código ya existe.')
        identifier = identifier or uuid4()
        if old:
            if data['codigo'] != old['codigo']:
                raise AccessError(422, 'codigo_inmutable', 'El código del desafío no se modifica.')
            c.execute(text('UPDATE desafio SET titulo=:title,consigna=:body,revision=revision+1,actualizado_en=clock_timestamp() WHERE id=:id'), {'id':identifier,'title':data['titulo'],'body':data['consigna']})
            c.execute(text('DELETE FROM desafio_criterio WHERE desafio_id=:id'), {'id':identifier})
        else:
            c.execute(text("INSERT INTO desafio(id,codigo,titulo,consigna,estado,activo,revision) VALUES (:id,:code,:title,:body,'borrador',false,1)"), {'id':identifier,'code':data['codigo'],'title':data['titulo'],'body':data['consigna']})
        for code in CODES:
            item=data['configuracion'][code]
            c.execute(text('INSERT INTO desafio_criterio(desafio_id,criterio_id,obligatorio,configuracion) SELECT :id,id,:required,CAST(:config AS jsonb) FROM criterio WHERE codigo=:code'), {'id':identifier,'code':code,'required':item['obligatorio'],'config':canonical({'aplica':item['aplica'],'parametros':item['parametros']})})
        AccessService.audit(c,user['id'],'catalogo_desafio',identifier)
        return self.challenge(c,identifier)

    def challenge_state(self,c,user,identifier,revision,publish):
        self.lock(c)
        row=self.challenge(c,identifier)
        if row['revision']!=revision:
            conflict()
        if publish:
            self.validate(c,row['configuracion'])
        c.execute(text('UPDATE desafio SET estado=:state,activo=:active,revision=revision+1,actualizado_en=clock_timestamp() WHERE id=:id'), {'id':identifier,'state':'publicado' if publish else 'inactivo','active':publish})
        AccessService.audit(c,user['id'],'publicar_desafio' if publish else 'desactivar_desafio',identifier)
        return self.challenge(c,identifier)

    @staticmethod
    def criteria(c):
        rows=c.execute(text('SELECT codigo,nombre,descripcion FROM criterio ORDER BY codigo')).mappings().all()
        return {'items':[{**r,'revision':hashed(dict(r))} for r in rows], 'next_cursor':None}

    def presentation(self,c,user,code,data):
        self.lock(c)
        current=next((r for r in self.criteria(c)['items'] if r['codigo']==code),None)
        if not current:
            raise AccessError(404,'no_encontrado','Criterio no encontrado.')
        if current['revision']!=data['revision_esperada']:
            conflict()
        c.execute(text('UPDATE criterio SET nombre=:name,descripcion=:description,actualizado_en=clock_timestamp() WHERE codigo=:code'), {'code':code,'name':data['nombre'],'description':data['descripcion']})
        AccessService.audit(c,user['id'],'presentacion_criterio')
        return self.criteria(c)

    @staticmethod
    def rules(c):
        rows=c.execute(text('SELECT r.id,c.codigo AS criterio_codigo,r.tipo,r.parametros,r.mensajes,r.version,r.activa FROM regla r JOIN criterio c ON c.id=r.criterio_id ORDER BY c.codigo,r.version')).mappings().all()
        return [dict(r,id=str(r['id'])) for r in rows]

    @staticmethod
    def list_rules(c,limit,cursor):
        rows=c.execute(text('SELECT r.id,c.codigo AS criterio_codigo,r.tipo,r.parametros,r.mensajes,r.version,r.activa FROM regla r JOIN criterio c ON c.id=r.criterio_id WHERE (CAST(:cursor AS uuid) IS NULL OR r.id>CAST(:cursor AS uuid)) ORDER BY r.id LIMIT :limit'),{'cursor':cursor,'limit':limit+1}).mappings().all()
        return {'items':[dict(r,id=str(r['id'])) for r in rows[:limit]],'next_cursor':str(rows[limit-1]['id']) if len(rows)>limit else None}

    def new_rule(self,c,user,data):
        self.lock(c)
        rows=self.rules(c)
        candidate={**data,'id':str(uuid4()),'activa':True,'version':max((r['version'] for r in rows if r['criterio_codigo']==data['criterio_codigo']),default=0)+1}
        # Reglas de referencia sólo para validar tipos de dimensiones diferentes,
        # nunca se usan para evaluar si falta una regla vigente en PostgreSQL.
        baseline=json.loads((ROOT_DIR/'seeds/rules.json').read_text(encoding='utf-8'))['reglas']
        trial=[r for r in baseline if r['criterio_codigo']!=data['criterio_codigo']]+[candidate]
        self.validate(c,self.practices.own_configuration({'C2':True,'C3':True,'C4':True}),trial)
        c.execute(text('INSERT INTO regla(id,criterio_id,tipo,parametros,mensajes,version,activa,creada_por) SELECT :id,id,:type,CAST(:parameters AS jsonb),CAST(:messages AS jsonb),:version,false,:uid FROM criterio WHERE codigo=:code'), {'id':candidate['id'],'code':data['criterio_codigo'],'type':data['tipo'],'parameters':canonical(data['parametros']),'messages':canonical(data['mensajes']),'version':candidate['version'],'uid':user['id']})
        AccessService.audit(c,user['id'],'crear_regla',candidate['id'])
        return {**candidate,'activa':False}

    def rule_state(self,c,user,identifier,expected,publish):
        self.lock(c)
        rows=self.rules(c)
        candidate=next((r for r in rows if r['id']==str(identifier)),None)
        if candidate is None:
            raise AccessError(404,'no_encontrado','Regla no encontrada.')
        active=next((r['id'] for r in rows if r['criterio_codigo']==candidate['criterio_codigo'] and r['activa']),None)
        if active!=(str(expected) if expected else None):
            conflict()
        if publish:
            trial=deepcopy(rows)
            for r in trial:
                if r['criterio_codigo']==candidate['criterio_codigo']:
                    r['activa']=r['id']==str(identifier)
            self.validate(c,self.practices.own_configuration({'C2':True,'C3':True,'C4':True}),trial)
            for cid in c.execute(text("SELECT id FROM desafio WHERE estado='publicado'")).scalars():
                self.validate(c,self.challenge(c,cid)['configuracion'],trial)
            c.execute(text('UPDATE regla SET activa=false WHERE criterio_id=(SELECT criterio_id FROM regla WHERE id=:id) AND activa'), {'id':identifier})
        c.execute(text('UPDATE regla SET activa=:active WHERE id=:id'), {'id':identifier,'active':publish})
        AccessService.audit(c,user['id'],'publicar_regla' if publish else 'desactivar_regla',identifier)
        return {'items':self.rules(c),'next_cursor':None}
