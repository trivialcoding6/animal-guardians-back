# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Poetry 설치 및 설정
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

# 애플리케이션 코드 복사
COPY . .

EXPOSE 8000

# Python 경로에 현재 디렉토리 추가
ENV PYTHONPATH=/app

# 전체 경로로 uvicorn 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]