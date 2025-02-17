from fastapi.testclient import TestClient

def test_create_user(client: TestClient):
    response = client.post(
        "/api/v1/users/",
        json={
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"

def test_create_user_duplicate_email(client: TestClient):
    # 첫 번째 사용자 생성
    client.post(
        "/api/v1/users/",
        json={
            "id": 1,
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # 동일한 이메일로 두 번째 사용자 생성 시도
    response = client.post(
        "/api/v1/users/",
        json={
            "id": 2,
            "name": "Another User",
            "email": "test@example.com",
            "password": "anotherpassword"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 등록된 이메일입니다."