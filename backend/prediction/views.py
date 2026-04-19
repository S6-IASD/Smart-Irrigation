import os
import pickle
from datetime import datetime
from rest_framework import status, views, viewsets, permissions
from rest_framework.response import Response
from django.conf import settings
from .models import Prediction
from .serializers import PredictionSerializer, PredictionInputSerializer
from parcelles.models import Parcelle
from capteurs.models import Capteur, LectureCapteur
from meteo.models import DonneeMeteo
from meteo.services import WeatherService
import numpy as np

class PredictionAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PredictionInputSerializer(data=request.data)
        if serializer.is_valid():
            # Get input data
            parcelle_id = serializer.validated_data['parcelle_id']
            humidite_sol = serializer.validated_data.get('humidite_sol', 0)
            temperature_sol = serializer.validated_data.get('temperature_sol', 0)
            n_val = serializer.validated_data.get('N', 0)
            p_val = serializer.validated_data.get('P', 0)
            k_val = serializer.validated_data.get('K', 0)

            try:
                parcelle = Parcelle.objects.get(id=parcelle_id)
            except Parcelle.DoesNotExist:
                return Response({"error": "Parcelle not found"}, status=status.HTTP_404_NOT_FOUND)

            # Ensure user owns parcelle or is admin
            if request.user.role != 'admin' and parcelle.user != request.user:
                return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

            # 1. Fetch Weather
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

            # 2. Store Sensor Data manually
            capteur, _ = Capteur.objects.get_or_create(
                parcelle=parcelle,
                mode='manual',
                defaults={'type': 'multiparameter'}
            )
            
            lecture_obj = LectureCapteur.objects.create(
                capteur=capteur,
                humidite_sol=humidite_sol,
                temperature_sol=temperature_sol,
                N=n_val,
                P=p_val,
                K=k_val
            )

            # 3. Load ML model
            model_path = '/models/model.pkl'
            eau_litres = 0.0
            prediction_mode = 'fallback'
            
            # Features array. The ML model might expect NPK now! Let's provide them natively.
            features = np.array([[humidite_sol, temperature_sol, n_val, p_val, k_val, T_max, T_min, pluie_mm]])

            if os.path.exists(model_path):
                try:
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    
                    # Assume model returns a numpy array with litres
                    prediction = model.predict(features)
                    eau_litres = float(prediction[0])
                    prediction_mode = 'ML'
                except Exception as e:
                    eau_litres = self.fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha)
            else:
                # Fallback if model not available
                eau_litres = self.fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha)

            # 4. Create Prediction Object
            prediction_obj = Prediction.objects.create(
                parcelle=parcelle,
                lecture=lecture_obj,
                meteo=meteo_obj,
                prediction_date=weather_data['date'],
                eau_litres=eau_litres,
                declenchement=eau_litres > 0,
                status='success',
                mode=prediction_mode,
                weather_source='Open-Meteo'
            )

            return Response({
                "eau_litres": prediction_obj.eau_litres,
                "declenchement": prediction_obj.declenchement,
                "mode": prediction_obj.mode,
                "weather_source": prediction_obj.weather_source
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def fallback_rule(self, humidite, t_max, pluie, superficie):
        """ Rule-based prediction (Fallback) """
        water_needed = 0
        if humidite < 50:
            deficit = 50 - humidite
            evap_factor = 1.0 + (t_max - 20) * 0.05 if t_max > 20 else 1.0
            water_needed = (deficit * evap_factor * superficie * 10000) - (pluie * superficie * 10000)
            
        return max(float(water_needed), 0.0)

class PredictionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Prediction.objects.all()
        return Prediction.objects.filter(parcelle__user=user)
