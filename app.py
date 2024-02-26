from fastapi import FastAPI
from db.database import (create_booking, end_booking, get_active_lots, get_admin,
                         admin_book, initialize_db, get_inactive_lots, create_user)
from request_models.request_models import RAdminRequest, RAdminBook, RBookings, REndingBooking, RUser, RToken
from datetime import datetime, timedelta
import hashlib
import uvicorn
from http import HTTPStatus
from user.aaa import generate_password, auth_user, create_access_token, create_context, get_password_hash

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
initialize_db()


@app.post("/api/create_booking/")
def endpoint_create_booking(booking: RBookings):
    try:
        status = create_booking(booking)

        if status == 1:
            return {"message": "Booking created successfully"}
        elif status == -1:
            return {"message": "Can't create more than two bookings"}
    except Exception as e:
        return HTTPStatus(400)


@app.post("api//end_booking/")
def endpoint_end_booking(entry: REndingBooking):
    try:
        end_booking(entry)
        return {"message": "Booking ended successfully"}
    except Exception as e:
        return HTTPStatus(400)


@app.get("/api/get_lots/")
def endpoint_get_lots():
    try:
        active_lots_info = get_active_lots()
        inactive_lots_info = get_inactive_lots()

        active_response = [
            {
                "id": lot_info[0] if lot_info[0] is not None else "parking_lot_" + str(lot_info[1]),
                "status": lot_info[1],
                "firstName": lot_info[2] if lot_info[0] is not None else None,
                "secondName": lot_info[3] if lot_info[0] is not None else None,
                "startTime": lot_info[4] if lot_info[0] is not None else None,
                "carNumber": lot_info[5] if lot_info[0] is not None else None
            }
            for lot_info in active_lots_info
        ]

        inactive_response = [
            {
                "id": lot_info[0] if lot_info[0] is not None else "parking_lot_" + str(lot_info[1]),
                "status": lot_info[1]
            }
            for lot_info in inactive_lots_info
        ]

        return {"active_lots": active_response, "inactive_lots": inactive_response}
    except Exception as e:
        return HTTPStatus(400)


@app.post("/api/admin_auth/")
def endpoint_admin_auth(entry: RAdminRequest):
    try:
        bd_hashed = get_admin(entry.login)

        h = hashlib.new('sha256')

        h.update(entry.password.encode('utf-8'))

        if bd_hashed == h.hexdigest():
            return {"auth": 1}
        else:
            return {"auth": 0}
    except Exception as e:
        return HTTPStatus(400)


@app.post("/api/admin_book/")
def endpoint_admin_post(entry: RAdminBook):
    try:
        time = datetime.now()
        admin_book(entry, time)
        return {"message": "Booking created successfully"}
    except Exception as e:
        return HTTPStatus(400)
    

@app.post("/api/create_user/")
def endpoint_create_user(entry: RUser):
    try:
        password_lng = 6
        tmp_password = generate_password(password_lng)

        context = create_context()

        entry.password = get_password_hash(tmp_password, context)

        res = create_user(entry)

        return {"login": entry.login,
                "password:": tmp_password,
                "status": 1}
    except Exception as e:
        print (e)

    
@app.post("/api/token/")
def endpoint_token(entry: RUser):
    try:
        user = auth_user(entry.login, entry.password)

        if user:
            
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.login}, expires_delta=access_token_expires
            )
            return RToken(access_token=access_token, token_type="bearer")
        else:
            return HTTPStatus(404)

    except Exception as e:
        print(e)
        return HTTPStatus(400)


if __name__ == "__main__":
    initialize_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)
