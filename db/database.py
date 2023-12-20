from sqlalchemy import and_, create_engine, desc, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from db.db_models import Base, Booking, ParkingLot, Admin


engine = create_engine('sqlite:///../bookings.sqlite', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base.metadata.drop_all(engine)


def initialize_db():
    
    Base.metadata.create_all(engine)
    session = Session()

    for i in [5, 6, 7, 8, 9, 10, 19, 20, 21, 23]:
        if not session.query(ParkingLot).filter(ParkingLot.id == i).first():
            parking_lot = ParkingLot(id=i, status=0)
            session.add(parking_lot)

    if not session.query(Admin).filter(Admin.login == "admin").first():
        session.add(Admin(login="admin", hashed_password="..."))

    session.commit()
    session.close()


def create_booking(booking):
    session = Session()
    try:
        time = datetime.now()
        new_booking = Booking(
            firstName=booking.firstName,
            secondName=booking.secondName,
            carNumber=booking.carNumber,
            parkingLot=booking.parkingLot,
            start=time
        )
        session.add(new_booking)

        parking_lot = session.query(ParkingLot).filter_by(id=booking.parkingLot).first()
        if parking_lot:
            parking_lot.status = 1

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def end_booking(entry):
    session = Session()
    try:
        time = datetime.now()
        latest_booking = session.query(Booking).filter_by(parkingLot=entry.parking_lot).order_by(desc(Booking.id)).first()
        if not latest_booking:
            raise ValueError("No active bookings for this parking lot")

        latest_booking.end = time

        parking_lot = session.query(ParkingLot).filter_by(id=entry.parking_lot).first()
        if parking_lot:
            parking_lot.status = 0

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_lots():
    session = Session()
    try:
        latest_booking_subquery = (
            session.query(
                Booking.parkingLot,
                func.max(Booking.start).label("latest_start")
            )
            .group_by(Booking.parkingLot)
            .subquery()
        )

        latest_bookings = (
            session.query(
                ParkingLot.id,
                ParkingLot.status,
                Booking.firstName,
                Booking.secondName,
                Booking.start,
                Booking.carNumber
            )
            .join(
                latest_booking_subquery,
                Booking.parkingLot == latest_booking_subquery.c.parkingLot
            )
            .filter(Booking.start == latest_booking_subquery.c.latest_start)
            .outerjoin(ParkingLot, ParkingLot.id == Booking.parkingLot)
            .filter(
                (ParkingLot.status == 1),
                ParkingLot.id.isnot(None)
            )
            .all()
        )

        return latest_bookings
    finally:
        session.close()


def get_admin(login):
    session = Session()
    try:
        admin = session.query(Admin.hashed_password).filter_by(login=login).first()
        return admin.hashed_password if admin else None
    finally:
        session.close()


def admin_book(entry, start_time):
    session = Session()
    try:
        owner = session.query(Booking.firstName, Booking.secondName).filter_by(carNumber=entry.carNumber).first()
        if not owner:
            new_booking = Booking(
                firstName="adm",
                secondName="adm",
                carNumber=entry.carNumber,
                parkingLot=entry.parkingLot,
                start=start_time
            )
        else:
            new_booking = Booking(
                firstName=owner.firstName,
                secondName=owner.secondName,
                carNumber=entry.carNumber,
                parkingLot=entry.parkingLot,
                start=start_time
            )
        session.add(new_booking)

        parking_lot = session.query(ParkingLot).filter_by(id=entry.parkingLot).first()
        if parking_lot:
            parking_lot.status = 1

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        