from pydantic import BaseModel


class Bookings(BaseModel):
    firstName: str
    secondName: str
    carNumber: str
    parkingLot: int


class ParkingLots(BaseModel):
    id: int
    status: int


class EndingBooking(BaseModel):
    parkingLot: int


class AdminRequest(BaseModel):
    login: str
    password: str


class AdminBook(BaseModel):
    parkingLot: int
    carNumber: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    login: str
    password: str | None = None
    first_name: str | None = None
    second_name: str | None = None


class UserInDB(User):
    password: str
