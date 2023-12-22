from fastapi import FastAPI, HTTPException
from db.database import Bookings, EndingBooking, create_booking, end_booking, get_lots, initialize_db
from datetime import datetime
import uvicorn

app = FastAPI()


@app.post("/create_booking/")
def endpoint_create_booking(booking: Bookings):
    try:
        start_time = datetime.now()
        create_booking(booking)
        return {"message": "Booking created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/end_booking/")
def endpoint_end_booking(entry: EndingBooking):
    try:
        end_booking(entry)
        return {"message": "Booking ended successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/get_lots/")
def endpoint_get_lots():
    try:
        lots = get_lots()
        return [{"id": lot[0], "status": lot[1]} for lot in lots]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


initialize_db()
uvicorn.run(app, host="127.0.0.1", port=8000)
