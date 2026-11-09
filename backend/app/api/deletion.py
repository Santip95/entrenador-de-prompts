from uuid import UUID
from fastapi import APIRouter,Request,Response
from pydantic import SecretStr,Field
from app.api.access import Input,token,csrf,limited

router=APIRouter(tags=['borrado'])

class DeleteAccount(Input):
    password_actual:SecretStr=Field(min_length=1,max_length=128,repr=False)

@router.delete('/practicas/{identifier}',status_code=204)
def delete_practice(identifier:UUID,request:Request):
    request.app.state.deletion.practice(token(request),csrf(request),identifier)
    return Response(status_code=204)

@router.delete('/cuenta',status_code=204)
def delete_account(data:DeleteAccount,request:Request):
    limited(request,'borrar_cuenta',5)
    request.app.state.deletion.account(token(request),csrf(request),data.password_actual.get_secret_value())
    response=Response(status_code=204)
    response.delete_cookie(request.app.state.settings.session_cookie_name,path='/')
    return response
