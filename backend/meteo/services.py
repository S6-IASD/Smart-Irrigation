import requests
from datetime import datetime

class WeatherService:
    @staticmethod
    def get_weather_for_coordinates(lat, lon):
        """
        Fetches T_min, T_max, and pluie_mm from Open-Meteo API.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
            "timezone": "auto",
            "forecast_days": 1
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get('daily', {})
            t_max = daily.get('temperature_2m_max', [0.0])[0]
            t_min = daily.get('temperature_2m_min', [0.0])[0]
            rain = daily.get('rain_sum', [0.0])[0]

            now = datetime.now()
            
            return {
                "success": True,
                "T_max": float(t_max) if t_max is not None else 0.0,
                "T_min": float(t_min) if t_min is not None else 0.0,
                "pluie_mm": float(rain) if rain is not None else 0.0,
                "date": now.date(),
                "mois": now.month
            }
        except Exception as e:
            # Safe defaults in case of API failure
            now = datetime.now()
            return {
                "success": False,
                "T_max": 25.0,
                "T_min": 15.0,
                "pluie_mm": 0.0,
                "date": now.date(),
                "mois": now.month,
                "error": str(e)
            }
