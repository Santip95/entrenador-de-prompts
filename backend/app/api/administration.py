from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Request
from pydantic import Field, field_validator
from app.api.access import Input as InputBase, token, csrf

router=APIRouter(tags=['administracion'])

class ChallengeInput(InputBase):
    codigo: str=Field(min_length=1,max_length=80,pattern=r'^[A-Z0-9_]+$')
    titulo: str=Field(min_length=1,max_length=200)
    consigna: str=Field(min_length=1,max_length=1000)
    configuracion: dict
    revision_esperada: int|None=Field(default=None,ge=1)

    @field_validator('titulo','consigna')
    @classmethod
    def not_blank(cls,value):
        if not value.strip(): raise ValueError('Texto vacío')
        return value

class Revision(InputBase):
    revision_esperada: int=Field(ge=1)

class Presentation(InputBase):
    nombre: str=Field(min_length=1,max_length=200)
    descripcion: str=Field(min_length=1,max_length=1000)
    revision_esperada: str=Field(min_length=64,max_length=64)

    @field_validator('nombre','descripcion')
    @classmethod
    def not_blank(cls,value):
        if not value.strip(): raise ValueError('Texto vacío')
        return value

class RuleInput(InputBase):
    criterio_codigo: Literal['C1','C2','C3','C4','C5','C6']
    tipo: str=Field(max_length=80)
    parametros: dict
    mensajes: dict

class RuleRevision(InputBase):
    regla_activa_esperada: UUID|None

def guard(request,write=False):
    return request.app.state.access.authorized(token(request),csrf=csrf(request) if write else None,write=write,admin=True)

@router.get('/admin/desafios')
def challenges(request:Request,limit:int=20,cursor:UUID|None=None):
    from app.application.access import AccessError
    if not 1<=limit<=100:
        raise AccessError(422,'entrada_invalida','El límite debe estar entre 1 y 100.')
    with guard(request) as (c,u,s):
        request.app.state.administration.lock(c)
        return request.app.state.administration.challenges(c,limit,cursor)

@router.post('/admin/desafios',status_code=201)
def create(data:ChallengeInput,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.write_challenge(c,u,data.model_dump())

@router.put('/admin/desafios/{identifier}')
def edit(identifier:UUID,data:ChallengeInput,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.write_challenge(c,u,data.model_dump(),identifier)

@router.post('/admin/desafios/{identifier}/{action}')
def state(identifier:UUID,action:Literal['publicar','desactivar'],data:Revision,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.challenge_state(c,u,identifier,data.revision_esperada,action=='publicar')

@router.get('/admin/criterios')
def criteria(request:Request):
    with guard(request) as (c,u,s):
        return {**request.app.state.administration.criteria(c),'catalogos':request.app.state.practices.catalogs}

@router.patch('/admin/criterios/{code}')
def criterion(code:str,data:Presentation,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.presentation(c,u,code,data.model_dump())

@router.get('/admin/reglas')
def rules(request:Request,limit:int=20,cursor:UUID|None=None):
    from app.application.access import AccessError
    if not 1<=limit<=100:raise AccessError(422,'entrada_invalida','El límite debe estar entre 1 y 100.')
    with guard(request) as (c,u,s):
        return request.app.state.administration.list_rules(c,limit,cursor)

@router.post('/admin/reglas',status_code=201)
def rule(data:RuleInput,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.new_rule(c,u,data.model_dump())

@router.post('/admin/reglas/{identifier}/{action}')
def rule_state(identifier:UUID,action:Literal['publicar','desactivar'],data:RuleRevision,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.administration.rule_state(c,u,identifier,data.regla_activa_esperada,action=='publicar')
