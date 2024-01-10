from fastapi import FastAPI
from db.database import (create_booking, end_booking, get_active_lots, initialize_db, get_admin,
                         admin_book, initialize_db, get_inactive_lots)
from db.request_models import AdminRequest, AdminBook, Bookings, EndingBooking
from datetime import datetime
import hashlib
import uvicorn
from http import HTTPStatus


app = FastAPI()
initialize_db()


@app.post("/create_booking/")
def endpoint_create_booking(booking: Bookings):
    try:
        status = create_booking(booking)

        if status == 1:
            return {"message": "Booking created successfully"}
        elif status == -1:
            return {"message": "Can't create more than two bookings"}
    except Exception as e:
        return HTTPStatus(400)


@app.post("/end_booking/")
def endpoint_end_booking(entry: EndingBooking):
    try:
        end_booking(entry)
        return {"message": "Booking ended successfully"}
    except Exception as e:
        return HTTPStatus(400)


@app.get("/get_lots/")
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


@app.post("/admin_auth/")
def endpoint_admin_auth(entry: AdminRequest):
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


@app.post("/admin_book/")
def endpoint_admin_post(entry: AdminBook):
    try:
        time = datetime.now()
        admin_book(entry, time)
        return {"message": "Booking created successfully"}
    except Exception as e:
        return HTTPStatus(400)


if __name__ == "__main__":
    initialize_db()
    uvicorn.run(app, host="127.0.0.1", port=8000)
