from http import HTTPStatus
from fastapi import APIRouter, Depends
from ..request_models.request_models import RUser
from ..user.aaa import (generate_password, create_context,
                           get_current_admin_user, get_password_hash)
from ..db.database import create_user


router = APIRouter()

@router.post("/create_admin/")
def create_adm(entry: RUser, current_user: RUser = Depends(
        get_current_admin_user)):
    try:
        password_lng = 6
        tmp_password = generate_password(password_lng)

        context = create_context()

        entry.password = get_password_hash(tmp_password, context)

        create_user(entry, True)

        return {"login": entry.login,
                "password:": tmp_password,
                "status": 1}
    except Exception:
        return HTTPStatus(400)
