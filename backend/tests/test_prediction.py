import pytest
from rest_framework.test import APIClient
from unittest.mock import patch

# Mock qui correspond exactement à ce que WeatherService retourne
MOCK_METEO_RESPONSE = {
    "T_min": 14.2,
    "T_max": 26.8,
    "pluie_mm": 1.5,
    "mois": 6,
    "date": "2026-04-19"   # ← important : ton code utilise weather_data['date']
}

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def authenticated_client(client):
    client.post("/api/auth/register/", {
        "username": "agri_pred",
        "email": "pred@test.com",
        "password": "Test1234!"
    })
    response = client.post("/api/auth/login/", {
        "username": "agri_pred",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client

@pytest.fixture
def parcelle_id(authenticated_client):
    response = authenticated_client.post("/api/parcelles/", {
        "nom": "Parcelle Pred",
        "superficie_ha": 12.5,
        "type_plante": "Tomate",
        "stade": "mature",
        "latitude": 48.8566,
        "longitude": 2.3522 ,
        "ville": "Paris"
    })
    return response.data["id"]

@pytest.fixture
def capteur_data():
    return {
        "humidite_sol": 35.0,
        "temperature_sol": 22.5,
        "N": 150.0,
        "P": 55.0,
        "K": 180.0
    }

# ── Tests ───────────────────────────────────────────

@pytest.mark.django_db
def test_prediction_sans_token(client):
    response = client.post("/api/prediction/", {})
    assert response.status_code == 401

@pytest.mark.django_db
def test_prediction_parcelle_manquante(authenticated_client, capteur_data):
    response = authenticated_client.post("/api/prediction/", capteur_data)
    assert response.status_code == 400

@pytest.mark.django_db
def test_prediction_parcelle_inexistante(authenticated_client, capteur_data):
    payload = {
        "parcelle_id": "00000000-0000-0000-0000-000000000000",
        **capteur_data
    }
    response = authenticated_client.post("/api/prediction/", payload)
    assert response.status_code == 404

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_success(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    response = authenticated_client.post("/api/prediction/", payload)
    # Ton view retourne 201 Created
    assert response.status_code == 201
    assert "eau_litres" in response.data
    assert "declenchement" in response.data
    assert "mode" in response.data
    assert "weather_source" in response.data
    assert isinstance(response.data["eau_litres"], (int, float))
    assert isinstance(response.data["declenchement"], bool)

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_mode_fallback(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    # Sans model.pkl → mode fallback
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    response = authenticated_client.post("/api/prediction/", payload)
    assert response.status_code == 201
    assert response.data["mode"] == "fallback"

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_cree_lecture_capteur(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    authenticated_client.post("/api/prediction/", payload)
    lectures = authenticated_client.get("/api/lectures/")
    assert len(lectures.data) >= 1

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_cree_meteo(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    authenticated_client.post("/api/prediction/", payload)
    meteo = authenticated_client.get("/api/meteo/")
    assert len(meteo.data) >= 1

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_sol_tres_humide(mock_meteo, authenticated_client, parcelle_id):
    # humidite >= 50 → fallback retourne 0 → declenchement = False
    payload = {
        "parcelle_id": str(parcelle_id),
        "humidite_sol": 85.0,
        "temperature_sol": 20.0,
        "N": 140.0,
        "P": 50.0,
        "K": 170.0
    }
    response = authenticated_client.post("/api/prediction/", payload)
    assert response.status_code == 201
    assert response.data["declenchement"] == False
    assert response.data["eau_litres"] == 0.0

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_prediction_sol_sec(mock_meteo, authenticated_client, parcelle_id):
    # humidite < 50 → eau nécessaire → declenchement = True
    payload = {
        "parcelle_id": str(parcelle_id),
        "humidite_sol": 10.0,
        "temperature_sol": 35.0,
        "N": 140.0,
        "P": 50.0,
        "K": 170.0
    }
    response = authenticated_client.post("/api/prediction/", payload)
    assert response.status_code == 201
    assert response.data["declenchement"] == True
    assert response.data["eau_litres"] > 0

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_historique_predictions(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    authenticated_client.post("/api/prediction/", payload)
    authenticated_client.post("/api/prediction/", payload)
    response = authenticated_client.get("/api/prediction/history/")
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) == 2

@pytest.mark.django_db
@patch("meteo.services.WeatherService.get_weather_for_coordinates",
       return_value=MOCK_METEO_RESPONSE)
def test_historique_detail(mock_meteo, authenticated_client, parcelle_id, capteur_data):
    payload = {"parcelle_id": str(parcelle_id), **capteur_data}
    authenticated_client.post("/api/prediction/", payload)
    history = authenticated_client.get("/api/prediction/history/")
    pred_id = history.data[0]["id"]
    response = authenticated_client.get(f"/api/prediction/history/{pred_id}/")
    assert response.status_code == 200
    assert "eau_litres" in response.data

@pytest.mark.django_db
def test_historique_autre_user_isole(client, authenticated_client,
                                     parcelle_id, capteur_data):
    # User 2 ne voit pas les prédictions de User 1
    client.post("/api/auth/register/", {
        "username": "user2",
        "email": "user2@test.com",
        "password": "Test1234!"
    })
    resp = client.post("/api/auth/login/", {
        "username": "user2",
        "password": "Test1234!"
    })
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
    response = client.get("/api/prediction/history/")
    assert response.status_code == 200
    assert len(response.data) == 0