import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_client(client):
    client.post("/api/auth/register/", {
        "username": "agri1",
        "email": "agri@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "agri1",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client

@pytest.fixture
def parcelle_data():
    return {
        "nom": "Parcelle Test",
        "superficie_ha": 12.5,
        "type_plante": "Tomate",
        "stade": "mature",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "ville": "Paris"
    }

# ── Parcelles tests ─────────────────────────────────

@pytest.mark.django_db
def test_list_parcelles_sans_token(client):
    response = client.get("/api/parcelles/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_parcelle(authenticated_client, parcelle_data):
    response = authenticated_client.post("/api/parcelles/", parcelle_data)
    assert response.status_code == 201
    assert response.data["nom"] == "Parcelle Test"

@pytest.mark.django_db
def test_list_parcelles(authenticated_client, parcelle_data):
    authenticated_client.post("/api/parcelles/", parcelle_data)
    response = authenticated_client.get("/api/parcelles/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_delete_parcelle(authenticated_client, parcelle_data):
    create = authenticated_client.post("/api/parcelles/", parcelle_data)
    parcelle_id = create.data["id"]
    response = authenticated_client.delete(f"/api/parcelles/{parcelle_id}/")
    assert response.status_code == 204

@pytest.mark.django_db
def test_update_parcelle(authenticated_client, parcelle_data):
    create = authenticated_client.post("/api/parcelles/", parcelle_data)
    parcelle_id = create.data["id"]
    response = authenticated_client.patch(f"/api/parcelles/{parcelle_id}/", {
        "stade": "fin"
    })
    assert response.status_code == 200
    assert response.data["stade"] == "fin"