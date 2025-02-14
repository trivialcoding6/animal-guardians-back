# syntax=docker/dockerfile:1

FROM python:3.11

WORKDIR /app

COPY pyproject.toml .

# pip 대신 poetry를 사용하는 방법
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]