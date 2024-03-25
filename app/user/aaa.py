from http import HTTPStatus
import os
import string
import random
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends
from ..db.database import get_user
from ..request_models.request_models import RUser, RTokenData


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token/")

def create_context() -> CryptContext:
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str, context: CryptContext) -> bool:
    return context.verify(plain_password, hashed_password)


def get_password_hash(password: str, context: CryptContext) -> str:
    return context.hash(password)


def generate_password(password_lng: int) -> str:

    s1 = list(string.ascii_lowercase)
    s2 = list(string.ascii_uppercase)
    s3 = list(string.digits)
    s4 = list(string.punctuation)

    random.shuffle(s1)
    random.shuffle(s2)
    random.shuffle(s3)
    random.shuffle(s4)

    part1 = round(password_lng * (30/100))
    part2 = round(password_lng * (20/100))

    result = []

    for x in range(part1):

        result.append(s1[x])
        result.append(s2[x])

    for x in range(part2):

        result.append(s3[x])
        result.append(s4[x])

    random.shuffle(result)

    password = "".join(result)

    return password


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def auth_user(login: str, password: str):
    user = get_user(login)

    if user:
        print(2)
        context = create_context()

        if verify_password(password, user.password, context):
            return user
        return None
    return None


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPStatus(401)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return credentials_exception
        RTokenData(username=username)
    except JWTError:
        return credentials_exception
    user = get_user(username)
    if user is None:
        return credentials_exception
    return user


def get_current_admin_user(current_user: RUser = Depends(get_current_user)):
    if not current_user.admin:
        return HTTPStatus(403)
    return current_user