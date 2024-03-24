import os
from datetime import datetime
from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import sessionmaker
from ..request_models.request_models import RUser
from .db_models import Base, Booking, ParkingLot, Admin, User


db_url = os.getenv('DATABASE_URL')

engine = create_engine(db_url, connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)


def initialize_db(username, password):
    Base.metadata.create_all(engine)
    session = Session()

    for i in [5, 6, 7, 8, 9, 10, 19, 20, 21, 23]:
        if not session.query(ParkingLot).filter(ParkingLot.id == i).first():
            if i < 19:
                floor = 1
            else:
                floor = 2

            parking_lot = ParkingLot(id=i, status=0, floor=floor)

            session.add(parking_lot)

    new_user = User(
        login=username,
        password=password,
        first_name=None,
        second_name=None,
        car_number=None,
        admin=True
    )

    session.add(new_user)

    session.commit()
    session.close()


def create_booking(booking):
    session = Session()
    try:

        latest_booking = (
            session.query(Booking)
            .filter_by(carNumber=booking.carNumber, ended=False)
            .order_by(desc(Booking.id))
            .first()
        )

        latest_booking_exists = bool(latest_booking)

        if latest_booking_exists:
            return -1
        else:

            time = datetime.now()
            new_booking = Booking(
                firstName=booking.firstName,
                secondName=booking.secondName,
                carNumber=booking.carNumber,
                parkingLot=booking.parkingLot,
                start=time,
                ended=False
            )
            session.add(new_booking)

            parking_lot = session.query(ParkingLot).filter_by(
                id=booking.parkingLot).first()
            if parking_lot:
                parking_lot.status = 1

            session.commit()

            return 1

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def end_booking(entry):
    session = Session()
    try:
        time = datetime.now()
        latest_booking = (
            session.query(Booking)
            .filter_by(parkingLot=entry.parkingLot, ended=False)
            .order_by(desc(Booking.id))
            .first()
        )
        if not latest_booking:
            raise ValueError("No active bookings for this parking lot")

        latest_booking.end = time
        latest_booking.ended = True

        parking_lot = session.query(ParkingLot).filter_by(
            id=entry.parkingLot).first()
        if parking_lot:
            parking_lot.status = 0

        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise e
    finally:
        session.close()


def get_inactive_lots():
    session = Session()
    try:
        inactive_lots = (
            session.query(
                ParkingLot.id,
                ParkingLot.status,
                ParkingLot.floor
            )
            .filter(
                ParkingLot.status == 0
            )
            .all()
        )

        return inactive_lots
    finally:
        session.close()


def get_inactive_lots_by_floor(floor):
    session = Session()
    try:
        inactive_lots = (
            session.query(
                ParkingLot.id,
                ParkingLot.status,
                ParkingLot.floor
            )
            .filter(
                ParkingLot.status == 0,
                ParkingLot.floor == floor
            )
            .all()
        )

        return inactive_lots
    finally:
        session.close()


def get_active_lots():
    session = Session()
    try:
        subquery = (
            select(
                Booking.parkingLot,
                Booking.firstName,
                Booking.secondName,
                Booking.start,
                Booking.carNumber,
                func.row_number().over(
                    partition_by=Booking.parkingLot,
                    order_by=Booking.start.desc()
                ).label("row_num")
            )
            .where(Booking.ended == False)
            .alias("sub")
        )
        active_lots = (
            session.query(
                ParkingLot.id,
                ParkingLot.status,
                ParkingLot.floor,
                subquery.c.firstName,
                subquery.c.secondName,
                subquery.c.start,
                subquery.c.carNumber
            )
            .outerjoin(subquery, ParkingLot.id == subquery.c.parkingLot)
            .filter(
                subquery.c.row_num == 1,
                ParkingLot.status == 1
            )
            .all()
        )

        return active_lots
    finally:
        session.close()


def get_active_lots_by_floor(floor):
    session = Session()
    try:
        subquery = (
            select(
                Booking.parkingLot,
                Booking.firstName,
                Booking.secondName,
                Booking.start,
                Booking.carNumber,
                func.row_number().over(
                    partition_by=Booking.parkingLot,
                    order_by=Booking.start.desc()
                ).label("row_num")
            )
            .where(Booking.ended == False)
            .alias("sub")
        )
        active_lots = (
            session.query(
                ParkingLot.id,
                ParkingLot.status,
                ParkingLot.floor,
                subquery.c.firstName,
                subquery.c.secondName,
                subquery.c.start,
                subquery.c.carNumber
            )
            .outerjoin(subquery, ParkingLot.id == subquery.c.parkingLot)
            .filter(
                subquery.c.row_num == 1,
                ParkingLot.status == 1,
                ParkingLot.floor == floor
            )
            .all()
        )

        return active_lots
    finally:
        session.close()


def get_admin(login):
    session = Session()
    try:
        admin = session.query(
            Admin.hashed_password).filter_by(
            login=login).first()
        return admin.hashed_password if admin else None
    finally:
        session.close()


def admin_book(entry, start_time):
    session = Session()
    try:
        owner = session.query(
            Booking.firstName,
            Booking.secondName).filter_by(
            carNumber=entry.carNumber).first()
        if not owner:
            new_booking = Booking(
                firstName="adm",
                secondName="adm",
                carNumber=entry.carNumber,
                parkingLot=entry.parkingLot,
                start=start_time,
                ended=False
            )
        else:
            new_booking = Booking(
                firstName=owner.firstName,
                secondName=owner.secondName,
                carNumber=entry.carNumber,
                parkingLot=entry.parkingLot,
                start=start_time,
                ended=False
            )
        session.add(new_booking)

        parking_lot = session.query(ParkingLot).filter_by(
            id=entry.parkingLot).first()
        if parking_lot:
            parking_lot.status = 1

        session.commit()

        return {
            'booking_id': new_booking.id,
            'car_number': new_booking.carNumber,
            'start_time': new_booking.start,
            'parking_lot': new_booking.parkingLot
        }
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

        active_lots = get_active_lots()
        print(active_lots)


def create_user(user_data: RUser, admin: bool):
    session = Session()

    try:
        new_user = User(
            login=user_data.login,
            password=user_data.password,
            first_name=user_data.first_name,
            second_name=user_data.second_name,
            car_number=None,
            admin=admin
        )

        session.add(new_user)

        session.commit()

        return User

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def get_user(entry_login: str):
    session = Session()

    try:
        print(0)
        user = session.query(User).filter_by(login=entry_login).first()

        if user:
            print(user.password)
            return user
        return None

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
