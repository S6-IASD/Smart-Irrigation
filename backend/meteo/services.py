import requests
from datetime import datetime, timedelta

class WeatherService:
    @staticmethod
    def get_weather_for_coordinates(lat, lon):
        """
        Fetches T_min, T_max, and pluie_mm from Open-Meteo API.
        Returns tomorrow's forecast (next 24h) for irrigation planning.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
            "timezone": "auto",
            "forecast_days": 2  # index 0 = aujourd'hui, index 1 = demain (24h suivantes)
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get('daily', {})
            # index [1] = demain = les 24 heures suivantes
            t_max = daily.get('temperature_2m_max', [0.0, 0.0])[1]
            t_min = daily.get('temperature_2m_min', [0.0, 0.0])[1]
            rain = daily.get('rain_sum', [0.0, 0.0])[1]

            tomorrow = (datetime.now() + timedelta(days=1)).date()

            return {
                "success": True,
                "T_max": float(t_max) if t_max is not None else 0.0,
                "T_min": float(t_min) if t_min is not None else 0.0,
                "pluie_mm": float(rain) if rain is not None else 0.0,
                "date": tomorrow,
                "mois": tomorrow.month
            }
        except Exception as e:
            # Safe defaults in case of API failure
            tomorrow = (datetime.now() + timedelta(days=1)).date()
            return {
                "success": False,
                "T_max": 25.0,
                "T_min": 15.0,
                "pluie_mm": 0.0,
                "date": tomorrow,
                "mois": tomorrow.month,
                "error": str(e)
            }

