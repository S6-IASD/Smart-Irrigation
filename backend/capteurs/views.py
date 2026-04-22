from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from django.utils import timezone
from .models import Capteur, LectureCapteur
from meteo.models import DonneeMeteo
from prediction.models import Prediction
from meteo.services import WeatherService
from parcelles.models import Parcelle
import os
import pickle
import numpy as np
from .serializers import CapteurSerializer, LectureCapteurSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    serializer_class = CapteurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Capteur.objects.all()
        return Capteur.objects.filter(parcelle__user=user)

class LectureCapteurViewSet(viewsets.ModelViewSet):
    serializer_class = LectureCapteurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return LectureCapteur.objects.all()
        return LectureCapteur.objects.filter(capteur__parcelle__user=user)

class IoTIngestView(views.APIView):
    permission_classes = [permissions.AllowAny] # Auth via device_id & api_key

    def post(self, request):
        data = request.data
        device_id = data.get('device_id')
        api_key_header = request.headers.get('X-API-KEY', data.get('api_key'))
        
        humidite_sol = data.get('humidite_sol', 0)
        temperature_sol = data.get('temperature_sol', 0)
        n_val = data.get('N', 0)
        p_val = data.get('P', 0)
        k_val = data.get('K', 0)

        if not device_id:
            return Response({'error': 'device_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check device and token
            capteur = Capteur.objects.get(device_id=device_id)
            if capteur.api_key and capteur.api_key != api_key_header:
                return Response({'error': 'Invalid API Key'}, status=status.HTTP_401_UNAUTHORIZED)
        except Capteur.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # 1. Sauvegarde de la lecture
        lecture_obj = LectureCapteur.objects.create(
            capteur=capteur,
            humidite_sol=humidite_sol,
            temperature_sol=temperature_sol,
            N=n_val,
            P=p_val,
            K=k_val
        )

        parcelle = capteur.parcelle

        # 2. Enrichissement Météo (si non récupéré récemment, on fait l'appel)
        try:
            weather_data = WeatherService.get_weather_for_coordinates(parcelle.latitude, parcelle.longitude)
            T_max = weather_data['T_max']
            T_min = weather_data['T_min']
            pluie_mm = weather_data['pluie_mm']
            
            meteo_obj = DonneeMeteo.objects.create(
                parcelle=parcelle,
                T_max=T_max,
                T_min=T_min,
                pluie_mm=pluie_mm,
                date=weather_data['date'],
                mois=weather_data['mois']
            )
        except Exception as e:
            # Fallback if weather fails
            T_max, T_min, pluie_mm = 25.0, 15.0, 0.0
            meteo_obj = None

        # 3. Prédiction ML
        model_path = '/models/model.pkl'
        eau_litres = 0.0
        prediction_mode = 'fallback'
        features = np.array([[humidite_sol, temperature_sol, n_val, p_val, k_val, T_max, T_min, pluie_mm]])

        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                prediction = model.predict(features)
                eau_litres = float(prediction[0])
                prediction_mode = 'ML'
            except Exception:
                eau_litres = self.fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha)
        else:
            eau_litres = self.fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha)

        # 4. Enregistrement Prédiction
        Prediction.objects.create(
            parcelle=parcelle,
            lecture=lecture_obj,
            meteo=meteo_obj,
            prediction_date=timezone.now().date(),
            eau_litres=eau_litres,
            declenchement=eau_litres > 0,
            status='success',
            mode=prediction_mode,
            weather_source='Open-Meteo' if meteo_obj else 'Fallback'
        )

        # 5. Réponse Action IoT
        return Response({
            "status": "success",
            "device_id": device_id,
            "action": {
                "pump_on": eau_litres > 0,
                "water_liters": eau_litres
            }
        }, status=status.HTTP_201_CREATED)

    def fallback_rule(self, humidite, t_max, pluie, superficie):
        water_needed = 0
        if humidite < 50:
            deficit = 50 - humidite
            evap_factor = 1.0 + (t_max - 20) * 0.05 if t_max > 20 else 1.0
            water_needed = (deficit * evap_factor * superficie * 10000) - (pluie * superficie * 10000)
        return max(float(water_needed), 0.0)
