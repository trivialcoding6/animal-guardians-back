# Animal Guardians Backend

동물 보호 서비스를 위한 백엔드 API 서버입니다.

## 기술 스택

### 주요 프레임워크 및 라이브러리

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLModel**: SQLAlchemy 기반의 ORM
- **Alembic**: 데이터베이스 마이그레이션 도구
- **Pydantic**: 데이터 검증 및 설정 관리
- **Poetry**: 의존성 및 패키지 관리
- **Pytest**: 테스트 프레임워크
- **Loguru**: 로깅 시스템

### 데이터베이스

- **PostgreSQL**: 메인 데이터베이스
- **AsyncPG**: 비동기 PostgreSQL 드라이버

### 인프라

- **Docker**: 컨테이너화
- **Azure Container Apps**: 클라우드 배포 환경
- **GitHub Actions**: CI/CD 파이프라인

## 프로젝트 구조

```
app/
├── api/ # API 엔드포인트
│ └── v1/ # API 버전 1
├── core/ # 핵심 설정 및 기능
├── crud/ # 데이터베이스 작업
├── db/ # 데이터베이스 설정
├── models/ # 데이터베이스 모델
├── schemas/ # Pydantic 스키마
└── services/ # 비즈니스 로직
```

## 시작하기

### 필수 요구사항

- Python 3.11 이상
- Poetry
- PostgreSQL

### 로컬 개발 환경 설정

1. 저장소 클론

```
git clone https://github.com/your-username/animal-guardians-back.git
cd animal-guardians-back
```

2. Poetry 설치 및 의존성 설치

```bash
pip install poetry
poetry install
```

3. 환경 변수 설정
   `.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 설정하세요:

```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key
DB_NAME=dbname
DB_USER=user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

4. 데이터베이스 마이그레이션

```bash
alembic upgrade head
```

5. 개발 서버 실행

```bash
uvicorn app.main:app --reload
```

## 테스트

테스트 실행:

```bash
poetry run pytest tests/
```

커버리지 리포트 생성:

```bash
poetry run pytest --cov=app tests/
```

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 배포 (자동 배포 예정)

GitHub Actions를 통해 Azure Container Apps에 자동 배포됩니다.
`main` 브랜치에 푸시하면 자동으로 배포 파이프라인이 실행됩니다.

## Docker 설정 및 실행

### Docker 설치
- Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) 설치
- Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) 설치
- Linux: [Docker Engine](https://docs.docker.com/engine/install/) 설치

### Docker 실행 전 확인사항
1. Docker 데몬이 실행 중인지 확인
```bash
# Docker 데몬 상태 확인
docker info

# Mac/Linux에서 Docker 데몬 시작
sudo systemctl start docker

# Docker Desktop이 실행 중인지 확인 (Mac/Windows)
```

2. 네트워크 설정 확인
- 프록시 설정이 필요한 경우:
```bash
# Docker 설정 파일에 프록시 설정 추가
{
  "proxies": {
    "default": {
      "httpProxy": "http://proxy:port",
      "httpsProxy": "http://proxy:port",
      "noProxy": "localhost,127.0.0.1"
    }
  }
}
```

### Docker 이미지 빌드 및 실행

1. 이미지 빌드
```bash
# 캐시 없이 새로 빌드
docker build --no-cache -t animal-guardians-backend .

# 일반 빌드
docker build -t animal-guardians-backend .
```

2. 컨테이너 실행
```bash
# 환경변수 파일을 사용하여 실행
docker run -d \
  --name animal-guardians \
  -p 8000:8000 \
  --env-file .env \
  animal-guardians-backend

# 환경변수를 직접 지정하여 실행
docker run -d \
  --name animal-guardians \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  animal-guardians-backend
```

3. 컨테이너 관리
```bash
# 컨테이너 상태 확인
docker ps

# 컨테이너 로그 확인
docker logs animal-guardians

# 컨테이너 중지
docker stop animal-guardians

# 컨테이너 재시작
docker restart animal-guardians
```
