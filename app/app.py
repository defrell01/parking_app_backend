import os
from fastapi import FastAPI
import uvicorn
from .db.database import initialize_db
from .user.aaa import create_context, get_password_hash
from .endpoints import bookings, admin, user


admin_username = os.getenv('ADMIN_USERNAME')
admin_password = os.getenv('ADMIN_PASSWORD')

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

SECRET_KEY = os.getenv('SECRET_KEY')

context = create_context()
admin_password_hash = get_password_hash(admin_password, context)

app = FastAPI()

app.include_router(bookings.router)
app.include_router(user.router)
app.include_router(admin.router)

initialize_db(admin_username, admin_password_hash)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
