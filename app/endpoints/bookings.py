
import datetime
from http import HTTPStatus
from fastapi import APIRouter, Depends
from ..request_models.request_models import RBookings, RUser, REndingBooking, RAdminBook, RGetLots
from ..db.database import (create_booking, end_booking, admin_book, get_active_lots,
                        get_active_lots_by_floor, get_inactive_lots, get_inactive_lots_by_floor)
from ..user.aaa import get_current_user, get_current_admin_user


router = APIRouter()

@router.post("/api/create_booking/")
def endpoint_create_booking(booking: RBookings,
                            current_user: RUser = Depends(get_current_user)):
    try:
        status = create_booking(booking)

        if status == 1:
            return {"message": "Booking created successfully"}
                
        return {"message": "Can't create more than two bookings"}
    
    except Exception:
        return HTTPStatus(400)
    

@router.post("/api/end_booking/")
def endpoint_end_booking(entry: REndingBooking,
                         current_user: RUser = Depends(get_current_user)):
    try:
        end_booking(entry)
        return {"message": "Booking ended successfully"}
    except Exception:
        return HTTPStatus(400)
    

@router.post("/api/admin_book/")
def endpoint_admin_post(entry: RAdminBook,
                        current_user: RUser = Depends(get_current_admin_user)):
    try:
        time = datetime.now()
        admin_book(entry, time)
        return {"message": "Booking created successfully"}
    except Exception:
        return HTTPStatus(400)

@router.post("/api/get_lots/")
def endpoint_get_lots(entry: RGetLots,
                      current_user: RUser = Depends(get_current_user)):
    try:

        if entry.floor:
            active_lots_info = get_active_lots_by_floor(entry.floor)
            inactive_lots_info = get_inactive_lots_by_floor(entry.floor)
        else:
            active_lots_info = get_active_lots()
            inactive_lots_info = get_inactive_lots()

        active_response = [
            {
                "id": lot_info[0] if lot_info[0] is not None else "parking_lot_" + str(lot_info[1]),
                "status": lot_info[1],
                "floor": lot_info[2],
                "firstName": lot_info[3] if lot_info[0] is not None else None,
                "secondName": lot_info[4] if lot_info[0] is not None else None,
                "startTime": lot_info[5] if lot_info[0] is not None else None,
                "carNumber": lot_info[6] if lot_info[0] is not None else None
            }
            for lot_info in active_lots_info
        ]

        inactive_response = [
            {
                "id": lot_info[0] if lot_info[0] is not None else "parking_lot_" + str(lot_info[1]),
                "status": lot_info[1],
                "floor": lot_info[2]
            }
            for lot_info in inactive_lots_info
        ]

        return {"active_lots": active_response,
                "inactive_lots": inactive_response}
    except Exception:
        return HTTPStatus(400)
