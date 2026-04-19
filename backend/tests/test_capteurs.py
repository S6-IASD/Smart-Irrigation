import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_client(client):
    client.post("/api/auth/register/", {
        "username": "agri_test",
        "email": "agri@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "agri_test",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client

@pytest.fixture
def parcelle_id(authenticated_client):
    response = authenticated_client.post("/api/parcelles/", {
        "nom": "Parcelle Test",
        "superficie_ha": 10.0,
        "type_plante": "Tomate",
        "stade": "mature",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "ville": "Paris"
    })
    return response.data["id"]

@pytest.fixture
def capteur_id(authenticated_client, parcelle_id):
    response = authenticated_client.post("/api/capteurs/", {
        "parcelle": str(parcelle_id),
        "type": "sol",
        "mode": "manuel"
    })
    return response.data["id"]

# ── Tests capteurs ──────────────────────────────────

@pytest.mark.django_db
def test_list_capteurs_sans_token(client):
    response = client.get("/api/capteurs/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_capteur(authenticated_client, parcelle_id):
    response = authenticated_client.post("/api/capteurs/", {
        "parcelle": str(parcelle_id),
        "type": "sol",
        "mode": "manuel"
    })
    assert response.status_code == 201
    assert "id" in response.data

@pytest.mark.django_db
def test_list_capteurs(authenticated_client, capteur_id):
    response = authenticated_client.get("/api/capteurs/")
    assert response.status_code == 200
    assert len(response.data) >= 1

@pytest.mark.django_db
def test_get_capteur_by_id(authenticated_client, capteur_id):
    response = authenticated_client.get(f"/api/capteurs/{capteur_id}/")
    assert response.status_code == 200
    assert response.data["id"] == str(capteur_id)

@pytest.mark.django_db
def test_update_capteur(authenticated_client, capteur_id):
    response = authenticated_client.patch(f"/api/capteurs/{capteur_id}/", {
        "mode": "iot"
    })
    assert response.status_code == 200
    assert response.data["mode"] == "iot"

@pytest.mark.django_db
def test_delete_capteur(authenticated_client, capteur_id):
    response = authenticated_client.delete(f"/api/capteurs/{capteur_id}/")
    assert response.status_code == 204

@pytest.mark.django_db
def test_capteur_parcelle_autre_user(client, parcelle_id):
    # Un autre user ne peut pas voir les capteurs
    client.post("/api/auth/register/", {
        "username": "autre_user",
        "email": "autre@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "autre_user",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    response = client.get("/api/capteurs/")
    assert response.status_code == 200
    assert len(response.data) == 0

# ── Tests lectures ──────────────────────────────────

@pytest.mark.django_db
def test_list_lectures_sans_token(client):
    response = client.get("/api/lectures/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_lecture(authenticated_client, capteur_id):
    response = authenticated_client.post("/api/lectures/", {
        "capteur": str(capteur_id),
        "humidite_sol": 42.5,
        "temperature_sol": 21.0,
        "N": 140.0,
        "P": 52.0,
        "K": 175.0
    })
    assert response.status_code == 201
    assert float(response.data["humidite_sol"]) == 42.5

@pytest.mark.django_db
def test_list_lectures(authenticated_client, capteur_id):
    authenticated_client.post("/api/lectures/", {
        "capteur": str(capteur_id),
        "humidite_sol": 42.5,
        "temperature_sol": 21.0,
        "N": 140.0,
        "P": 52.0,
        "K": 175.0
    })
    response = authenticated_client.get("/api/lectures/")
    assert response.status_code == 200
    assert len(response.data) >= 1

@pytest.mark.django_db
def test_get_lecture_by_id(authenticated_client, capteur_id):
    create = authenticated_client.post("/api/lectures/", {
        "capteur": str(capteur_id),
        "humidite_sol": 42.5,
        "temperature_sol": 21.0,
        "N": 140.0,
        "P": 52.0,
        "K": 175.0
    })
    lecture_id = create.data["id"]
    response = authenticated_client.get(f"/api/lectures/{lecture_id}/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_valeurs_npk_invalides(authenticated_client, capteur_id):
    response = authenticated_client.post("/api/lectures/", {
        "capteur": str(capteur_id),
        "humidite_sol": -10,   # valeur invalide
        "temperature_sol": 21.0,
        "N": 140.0,
        "P": 52.0,
        "K": 175.0
    })
    assert response.status_code in [400, 422]