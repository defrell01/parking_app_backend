FROM python:3.12-slim
ENV PIP_TIMEOUT=30
WORKDIR /app
COPY poetry.lock .
COPY pyproject.toml .
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install
COPY . .
