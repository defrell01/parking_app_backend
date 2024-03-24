from datetime import timedelta
from http import HTTPStatus
from fastapi import APIRouter, Depends
from ..request_models.request_models import RUser, REmailSchema
from ..user.aaa import (get_current_admin_user, generate_password,
                       create_context, get_password_hash, create_access_token, 
                       ACCESS_TOKEN_EXPIRE_MINUTES, auth_user)
from ..db.database import create_user
from ..email_service.email_service import send_email


router = APIRouter()

@router.post("/api/create_user/")
def endpoint_create_user(
        entry: RUser, current_user: RUser = Depends(get_current_admin_user)):
    try:
        password_lng = 6
        tmp_password = generate_password(password_lng)

        context = create_context()

        entry.password = get_password_hash(tmp_password, context)

        creation_res = create_user(entry, False)

        if creation_res:
            email_data = REmailSchema(
                recipient_email=entry.login,
                subject="Регистрация на сайте",
                message="Вы успешно зарегистрированы. Ваш временный пароль: {}"
            )
            creation_res = send_email(email_data, tmp_password)

            if creation_res == 1:
                return {"login": entry.login,
                        "password:": tmp_password,
                        "status": 1}
            return HTTPStatus(400)
        
        return HTTPStatus(400)

    except Exception:
        return HTTPStatus(400)


@router.post("/api/token/")
def endpoint_token(entry: RUser):
    try:
        user = auth_user(entry.login, entry.password)

        if user:
            access_token_expires = timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.login}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}        
        return HTTPStatus(401)
    except Exception:
        return HTTPStatus(400)
