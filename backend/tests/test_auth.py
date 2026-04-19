import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user_data():
    return {
        "username": "testuser",
        "email": "test@test.com",
        "password": "Test1234!"
    }

@pytest.fixture
def authenticated_client(client, user_data):
    client.post("/api/auth/register/", user_data)
    response = client.post("/api/auth/login/", {
        "username": user_data["username"],
        "password": user_data["password"]
    })
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client

# ── Auth tests ──────────────────────────────────────

@pytest.mark.django_db
def test_register_success(client, user_data):
    response = client.post("/api/auth/register/", user_data)
    assert response.status_code == 201

@pytest.mark.django_db
def test_register_duplicate(client, user_data):
    client.post("/api/auth/register/", user_data)
    response = client.post("/api/auth/register/", user_data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_login_success(client, user_data):
    client.post("/api/auth/register/", user_data)
    response = client.post("/api/auth/login/", {
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_login_wrong_password(client, user_data):
    client.post("/api/auth/register/", user_data)
    response = client.post("/api/auth/login/", {
        "username": user_data["username"],
        "password": "MauvaisMotDePasse"
    })
    assert response.status_code == 401

@pytest.mark.django_db
def test_profile_without_token(client):
    response = client.get("/api/auth/profile/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_profile_with_token(authenticated_client):
    response = authenticated_client.get("/api/auth/profile/")
    assert response.status_code == 200