import sqlite3
from datetime import datetime
from db.models import Bookings, EndingBooking


def initialize_db():
    conn = sqlite3.connect('../bookings.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS BOOKINGS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstName TEXT,
                secondName TEXT,
                carNumber TEXT,
                parkingLot INTEGER,
                start TEXT,
                end TEXT
            )
        ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PARKING_LOTS (
            id INTEGER PRIMARY KEY,
            status integer
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO PARKING_LOTS (id, status) VALUES 
            (1, 0), 
            (2, 0), 
            (3, 0), 
            (4, 0), 
            (5, 0),
            (6, 0), 
            (7, 0), 
            (8, 0), 
            (9, 0);     
    ''')

    conn.commit()
    conn.close()


def create_booking(booking: Bookings):
    conn = sqlite3.connect('../bookings.sqlite')
    cursor = conn.cursor()
    time = datetime.now().isoformat()
    try:
        cursor.execute('''
            INSERT INTO BOOKINGS (firstName, secondName, carNumber, parkingLot, start)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking.firstName, booking.secondName, booking.carNumber, booking.parkingLot, time))

        cursor.execute('''
            UPDATE PARKING_LOTS
            SET status = 1
            WHERE id = ?
        ''', (booking.parkingLot,))

        conn.commit()
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()


def end_booking(entry: EndingBooking):
    conn = sqlite3.connect('../bookings.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM BOOKINGS
        WHERE parkingLot = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (entry.parking_lot,))

    booking_id = cursor.fetchone()
    if booking_id:
        booking_id = booking_id[0]
    else:
        conn.close()
        raise ValueError("Нет активных бронирований для данного парковочного места")

    end_time = datetime.now()

    cursor.execute('''
        UPDATE BOOKINGS
        SET end = ?
        WHERE id = ?
    ''', (end_time.isoformat(), booking_id))

    cursor.execute('''
        UPDATE PARKING_LOTS
        SET status = 0
        WHERE id = ?
    ''', (entry.parking_lot,))

    conn.commit()
    conn.close()


def get_lots():
    conn = sqlite3.connect('../bookings.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM PARKING_LOTS        
    ''')

    rows = cursor.fetchall()

    conn.close()

    return rows
