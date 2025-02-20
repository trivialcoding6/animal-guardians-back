# syntax=docker/dockerfile:1
FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필요한 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Poetry 설치 시 네트워크 타임아웃 설정 추가
ENV POETRY_HTTP_TIMEOUT=120

# Poetry 설치 및 PATH 설정
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Poetry 설정
RUN poetry config virtualenvs.create false

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root --no-interaction

# 애플리케이션 코드 복사
COPY . .

EXPOSE 8000

# Python 경로에 현재 디렉토리 추가
ENV PYTHONPATH=/app

# 전체 경로로 uvicorn 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]