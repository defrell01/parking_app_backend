from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String)
    secondName = Column(String)
    carNumber = Column(String)
    parkingLot = Column(Integer, ForeignKey('parking_lots.id'))
    start = Column(String)
    end = Column(String)

    parking_lot = relationship("ParkingLot", back_populates="bookings")


class ParkingLot(Base):
    __tablename__ = 'parking_lots'
    
    id = Column(Integer, primary_key=True)
    status = Column(Integer)

    bookings = relationship("Booking", order_by=Booking.id, back_populates="parking_lot")


class Admin(Base):
    __tablename__ = 'admins'
    
    login = Column(String, primary_key=True)
    hashed_password = Column(String)