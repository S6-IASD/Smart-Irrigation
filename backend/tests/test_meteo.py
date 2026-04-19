import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_client(client):
    client.post("/api/auth/register/", {
        "username": "agri_meteo",
        "email": "meteo@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "agri_meteo",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client

@pytest.fixture
def parcelle_id(authenticated_client):
    response = authenticated_client.post("/api/parcelles/", {
        "nom": "Parcelle Meteo",
        "superficie_ha": 8.0,
        "type_plante": "Laitue",
        "stade": "jeune",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "ville": "Paris"
    })
    return response.data["id"]

@pytest.fixture
def meteo_data(parcelle_id):
    return {
        "parcelle": str(parcelle_id),
        "T_min": 12.5,
        "T_max": 28.3,
        "pluie_mm": 2.4,
        "mois": 6,
        "date": "2026-04-19"
    }

# ── Tests météo ─────────────────────────────────────

@pytest.mark.django_db
def test_list_meteo_sans_token(client):
    response = client.get("/api/meteo/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_meteo(authenticated_client, meteo_data):
    response = authenticated_client.post("/api/meteo/", meteo_data)
    assert response.status_code == 201
    assert float(response.data["T_max"]) == 28.3

@pytest.mark.django_db
def test_list_meteo(authenticated_client, meteo_data):
    authenticated_client.post("/api/meteo/", meteo_data)
    response = authenticated_client.get("/api/meteo/")
    assert response.status_code == 200
    assert len(response.data) >= 1

@pytest.mark.django_db
def test_get_meteo_by_id(authenticated_client, meteo_data):
    create = authenticated_client.post("/api/meteo/", meteo_data)
    meteo_id = create.data["id"]
    response = authenticated_client.get(f"/api/meteo/{meteo_id}/")
    assert response.status_code == 200
    assert response.data["id"] == str(meteo_id)

@pytest.mark.django_db
def test_update_meteo(authenticated_client, meteo_data):
    create = authenticated_client.post("/api/meteo/", meteo_data)
    meteo_id = create.data["id"]
    response = authenticated_client.patch(f"/api/meteo/{meteo_id}/", {
        "pluie_mm": 5.0
    })
    assert response.status_code == 200
    assert float(response.data["pluie_mm"]) == 5.0

@pytest.mark.django_db
def test_delete_meteo(authenticated_client, meteo_data):
    create = authenticated_client.post("/api/meteo/", meteo_data)
    meteo_id = create.data["id"]
    response = authenticated_client.delete(f"/api/meteo/{meteo_id}/")
    assert response.status_code == 204

@pytest.mark.django_db
def test_meteo_autre_user_ne_voit_pas(client, meteo_data, authenticated_client):
    authenticated_client.post("/api/meteo/", meteo_data)
    # Créer un autre utilisateur
    client.post("/api/auth/register/", {
        "username": "autre",
        "email": "autre@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "autre",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    response = client.get("/api/meteo/")
    assert response.status_code == 200
    assert len(response.data) == 0