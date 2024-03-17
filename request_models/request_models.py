from pydantic import BaseModel, EmailStr


class RBookings(BaseModel):
    firstName: str
    secondName: str
    carNumber: str
    parkingLot: int


class RParkingLots(BaseModel):
    id: int
    status: int


class REndingBooking(BaseModel):
    parkingLot: int


class RAdminRequest(BaseModel):
    login: str
    password: str


class RAdminBook(BaseModel):
    parkingLot: int
    carNumber: str


class RToken(BaseModel):
    access_token: str
    token_type: str


class RTokenData(BaseModel):
    username: str | None = None


class RUser(BaseModel):
    login: EmailStr
    password: str | None = None
    first_name: str | None = None
    second_name: str | None = None


class RUserInDB(RUser):
    password: str


class REmailSchema(BaseModel):
    recipient_email: EmailStr
    subject: str
    message: str


class RGetLots(BaseModel):
    floor: int | None = None