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
        timestamp_str = data.get('timestamp')

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
        lecture_kwargs = {
            'capteur': capteur,
            'humidite_sol': humidite_sol,
            'temperature_sol': temperature_sol,
            'N': n_val,
            'P': p_val,
            'K': k_val
        }
        if timestamp_str:
            lecture_kwargs['timestamp'] = timestamp_str

        lecture_obj = LectureCapteur.objects.create(**lecture_kwargs)

        parcelle = capteur.parcelle

        # L'action d'irrigation est différée au scheduler (à 22h00) ou manuellement.
        return Response({
            "status": "success",
            "device_id": device_id,
            "message": "Data ingested successfully. Prediction deferred.",
            "action": {
                "pump_on": False,
                "water_liters": 0
            }
        }, status=status.HTTP_201_CREATED)
