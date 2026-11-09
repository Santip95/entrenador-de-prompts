from datetime import date
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response
from pydantic import Field, SecretStr, StrictBool

from app.api.access import Input, token, csrf
from app.db.practices import sql

router=APIRouter()


class Start(Input):
    desafio_id: UUID | None = None
    objetivo: str | None = None
    aplicabilidad: dict[str,StrictBool] | None = None
    modo: Literal["guiado","libre"]


class Create(Start):
    token_inicio: SecretStr = Field(max_length=4096,repr=False)
    coincidencias_confirmadas: list[str] = Field(max_length=2000)
    request_id: UUID


class Draft(Input):
    modo: Literal["guiado","libre"]
    texto_libre: str
    componentes_confirmados: StrictBool
    componentes: dict


class Save(Input):
    borrador: Draft
    token_revision: SecretStr = Field(max_length=4096,repr=False)
    coincidencias_confirmadas: list[str] = Field(max_length=2000)
    request_id: UUID


def guard(request,write=False):
    return request.app.state.access.authorized(token(request),csrf=csrf(request),write=write)


@router.get("/desafios")
def challenges(request:Request,limit:int=Query(20,ge=1,le=100),cursor:UUID|None=None):
    with guard(request) as (c,u,s):
        rows=sql(c,'challenges_desafio',cursor=cursor,limit=limit+1).scalars().all()
        service=request.app.state.practices
        return {"items":[service.catalog(c,id) | {"id":id,"catalogos":service.catalogs} for id in rows[:limit]],"next_cursor":str(rows[limit-1]) if len(rows)>limit else None}


@router.get("/desafios/{challenge_id}")
def challenge(challenge_id:UUID,request:Request):
    with guard(request) as (c,u,s):
        service=request.app.state.practices
        return service.catalog(c,challenge_id) | {"catalogos":service.catalogs}


@router.post("/practicas/preparar")
def prepare(data:Start,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.practices.prepare(c,u,data.model_dump())


@router.post("/practicas")
def create(data:Create,request:Request,response:Response):
    values=data.model_dump()
    values["token_inicio"]=data.token_inicio.get_secret_value()
    with guard(request,True) as (c,u,s):
        result,created=request.app.state.practices.create(c,u,values)
        response.status_code=201 if created else 200
        return result


@router.get("/practicas")
def history(request:Request,limit:int=Query(20,ge=1,le=100),cursor:UUID|None=None,desde:date|None=None,hasta:date|None=None,desafio_id:UUID|None=None):
    with guard(request) as (c,u,s):
        return request.app.state.practices.history(c,u,limit,cursor,desde,hasta,desafio_id)


@router.get("/practicas/{pid}")
def practice(pid:UUID,request:Request):
    with guard(request) as (c,u,s):
        return request.app.state.practices.practice(c,u,pid)


@router.post("/practicas/{pid}/revisar")
def review(pid:UUID,data:Draft,request:Request):
    with guard(request,True) as (c,u,s):
        return request.app.state.practices.review(c,u,pid,data.model_dump())


@router.post("/practicas/{pid}/versiones")
def save(pid:UUID,data:Save,request:Request,response:Response):
    values=data.model_dump()
    values["token_revision"]=data.token_revision.get_secret_value()
    with guard(request,True) as (c,u,s):
        result,created=request.app.state.practices.save(c,u,pid,values)
        response.status_code=201 if created else 200
        return result


@router.get("/practicas/{pid}/versiones")
def versions(pid:UUID,request:Request,limit:int=Query(20,ge=1,le=100),cursor:UUID|None=None):
    with guard(request) as (c,u,s):
        return request.app.state.practices.versions(c,u,pid,limit,cursor)


@router.get("/versiones/{vid}")
def version(vid:UUID,request:Request):
    with guard(request) as (c,u,s):
        return request.app.state.practices.version(c,u,vid)


@router.get("/practicas/{pid}/comparacion")
def comparison(pid:UUID,request:Request,desde:UUID,hasta:UUID):
    with guard(request) as (c,u,s):
        return request.app.state.practices.comparison(c,u,pid,desde,hasta)


@router.get("/progreso")
def progress(request:Request,desde:date|None=None,hasta:date|None=None,limit:int=Query(20,ge=1,le=100),cursor:UUID|None=None):
    with guard(request) as (c,u,s):
        return request.app.state.practices.progress(c,u,desde,hasta,limit,cursor)
