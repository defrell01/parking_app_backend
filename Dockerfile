# Используем базовый образ Python
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL sqlite:///./bookings.sqlite
ENV UVICORN_CMD "uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

# Выполняем команду при запуске контейнера
CMD sh -c "$UVICORN_CMD"
