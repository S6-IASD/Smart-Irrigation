import os
import pickle
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
from rest_framework import status, views, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Prediction
from .serializers import PredictionSerializer, PredictionInputSerializer
from parcelles.models import Parcelle
from capteurs.models import Capteur, LectureCapteur
from meteo.models import DonneeMeteo
from meteo.services import WeatherService
import numpy as np

PLANTES_COMPTABLES = ['Olivier', 'Amandier', 'Figuier', 'Grenadier', 'Oranger', 'Citronnier', 'Vigne', 'Dattier', 'Noyer']
PLANTES_NON_COMPTABLES = ['Blé', 'Maïs', 'Orge', 'Soja', 'Riz', 'Sorgo', 'Millet', 'Avoine', 'Seigle', 'Tournesol', 'Colza', 'Arachide', 'Coton', 'Betterave', 'Canne', 'Pomme_de_terre', 'Manioc', 'Tomate', 'Oignon', 'Ail', 'Carotte', 'Chou', 'Laitue', 'Café']



# ─────────────────────────────────────────────────────────────────────────────
# Fonction centrale — partagée entre la vue API et le scheduler automatique
# ─────────────────────────────────────────────────────────────────────────────

def compute_prediction(parcelle, manual_data=None):
    """
    Calcule la prédiction d'irrigation pour une parcelle.

    Paramètres :
      parcelle    : instance Parcelle
      manual_data : dict optionnel avec les clés humidite_sol, temperature_sol, N, P, K
                    → Mode MANUEL  : les valeurs fournies sont utilisées directement
                    → Mode AUTO    : si None ou champs absents, on calcule la moyenne
                                     des lectures capteurs des 24 dernières heures

    Étapes :
      1. Résolution des données capteurs (manuel OU moyenne 24h)
      2. Prévision météo de demain (24h suivantes) via Open-Meteo
      3. Modèle ML ou règle fallback
      4. Sauvegarde en base

    Retourne : (Prediction, None) ou (None, "message d'erreur")
    """
    mode_label = 'manual' if manual_data else 'auto_avg'
    is_countable = parcelle.type_plante in PLANTES_COMPTABLES
    unite = 'L/plante' if is_countable else 'L/parcelle'

    # ── 1. Données capteurs ──────────────────────────────────────────────────
    if manual_data:
        # Mode manuel : valeurs directement fournies par l'utilisateur
        humidite_sol    = manual_data.get('humidite_sol', 50.0)
        temperature_sol = manual_data.get('temperature_sol', 25.0)
        n_val           = manual_data.get('N', 100.0)
        p_val           = manual_data.get('P', 50.0)
        k_val           = manual_data.get('K', 100.0)
    else:
        # Mode auto : moyenne des 24 dernières heures de lectures capteurs
        since = timezone.now() - timedelta(hours=24)
        aggregated = LectureCapteur.objects.filter(
            capteur__parcelle=parcelle,
            timestamp__gte=since
        ).aggregate(
            humidite_sol=Avg('humidite_sol'),
            temperature_sol=Avg('temperature_sol'),
            N=Avg('N'),
            P=Avg('P'),
            K=Avg('K'),
        )
        # Valeurs par défaut si aucune lecture disponible
        humidite_sol    = aggregated['humidite_sol']    if aggregated['humidite_sol']    is not None else 50.0
        temperature_sol = aggregated['temperature_sol'] if aggregated['temperature_sol'] is not None else 25.0
        n_val           = aggregated['N']               if aggregated['N']               is not None else 100.0
        p_val           = aggregated['P']               if aggregated['P']               is not None else 50.0
        k_val           = aggregated['K']               if aggregated['K']               is not None else 100.0

    # Snapshot de la lecture utilisée (traçabilité)
    capteur, _ = Capteur.objects.get_or_create(
        parcelle=parcelle,
        mode=mode_label,
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

    # ── 2. Prévision météo de demain (24h suivantes) ─────────────────────────
    weather_data = WeatherService.get_weather_for_coordinates(
        parcelle.latitude, parcelle.longitude
    )
    T_max    = weather_data['T_max']
    T_min    = weather_data['T_min']
    pluie_mm = weather_data['pluie_mm']

    meteo_obj = DonneeMeteo.objects.create(
        parcelle=parcelle,
        T_max=T_max,
        T_min=T_min,
        pluie_mm=pluie_mm,
        date=weather_data['date'],
        mois=weather_data['mois']
    )

    # ── 3. Modèle ML ou règle fallback ───────────────────────────────────────
    if is_countable:
        model_path = '/models/model_arbres.pkl'
        features = np.array([[
            humidite_sol, temperature_sol,
            n_val, p_val, k_val,
            T_max, T_min, pluie_mm
        ]])
    else:
        model_path = '/models/model_champs.pkl'
        features = np.array([[
            humidite_sol, temperature_sol,
            n_val, p_val, k_val,
            T_max, T_min, pluie_mm,
            parcelle.superficie_ha
        ]])

    quantite_predite = 0.0
    prediction_mode = f'fallback_{mode_label}'

    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            quantite_predite = float(model.predict(features)[0])
            prediction_mode = f'ML_{mode_label}'
        except Exception:
            quantite_predite = _fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha if not is_countable else None)
    else:
        quantite_predite = _fallback_rule(humidite_sol, T_max, pluie_mm, parcelle.superficie_ha if not is_countable else None)

    # ── 4. Sauvegarde ────────────────────────────────────────────────────────
    prediction_obj = Prediction.objects.create(
        parcelle=parcelle,
        lecture=lecture_obj,
        meteo=meteo_obj,
        prediction_date=weather_data['date'],   # date de DEMAIN
        quantite_predite=quantite_predite,
        quantite_reelle=quantite_predite,
        unite=unite,
        declenchement=quantite_predite > 0,
        status='success',
        mode=prediction_mode,
        weather_source='Open-Meteo'
    )

    return prediction_obj, None


def _fallback_rule(humidite, t_max, pluie, superficie=None):
    """Règle heuristique utilisée quand le modèle ML n'est pas disponible."""
    if humidite < 50:
        deficit = 50 - humidite
        evap_factor = 1.0 + (t_max - 20) * 0.05 if t_max > 20 else 1.0
        if superficie is not None:
            water_needed = (deficit * evap_factor * superficie * 10000) - (pluie * superficie * 10000)
        else:
            water_needed = (deficit * evap_factor * 2.0) - pluie
        return max(float(water_needed), 0.0)
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Vue API — déclenchement manuel par l'utilisateur
# ─────────────────────────────────────────────────────────────────────────────

class PredictionAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PredictionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data        = serializer.validated_data
        parcelle_id = data['parcelle_id']
        force       = True  # Toujours forcer la prédiction manuelle

        # Récupération de la parcelle
        try:
            parcelle = Parcelle.objects.get(id=parcelle_id)
        except Parcelle.DoesNotExist:
            return Response({"error": "Parcelle introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Vérification des droits
        if request.user.role != 'admin' and parcelle.user != request.user:
            return Response({"error": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        # Unicité journalière
        today = timezone.now().date()
        if not force and Prediction.objects.filter(parcelle=parcelle, created_at__date=today).exists():
            existing = Prediction.objects.filter(
                parcelle=parcelle, created_at__date=today
            ).order_by('-created_at').first()
            return Response({
                "detail": "Prédiction déjà effectuée aujourd'hui pour cette parcelle.",
                "already_done": True,
                "prediction": PredictionSerializer(existing).data
            }, status=status.HTTP_409_CONFLICT)

        # Construction du manual_data (seulement si des champs capteurs sont fournis)
        sensor_fields = ('humidite_sol', 'temperature_sol', 'N', 'P', 'K')
        manual_data = None
        if any(field in data for field in sensor_fields):
            manual_data = {f: data[f] for f in sensor_fields if f in data}

        # Calcul
        prediction_obj, error = compute_prediction(parcelle, manual_data=manual_data)
        if error:
            return Response({"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "quantite_predite": prediction_obj.quantite_predite,
            "quantite_reelle": prediction_obj.quantite_reelle,
            "unite":           prediction_obj.unite,
            "declenchement":   prediction_obj.declenchement,
            "mode":            prediction_obj.mode,
            "weather_source":  prediction_obj.weather_source,
            "prediction_date": str(prediction_obj.prediction_date),
            "already_done":    False,
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────────────────────────────────────
# ViewSet — historique des prédictions
# ─────────────────────────────────────────────────────────────────────────────

from rest_framework import mixins

class PredictionHistoryViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Prediction.objects.all().order_by('-created_at')
        return Prediction.objects.filter(parcelle__user=user).order_by('-created_at')

    @action(detail=True, methods=['get'], url_path='by_parcelle', url_name='by_parcelle')
    def by_parcelle(self, request, pk=None):
        """Historique des prédictions pour une parcelle donnée (pk = UUID de la parcelle)."""
        user = request.user
        try:
            parcelle = Parcelle.objects.get(id=pk)
        except Parcelle.DoesNotExist:
            return Response({"error": "Parcelle introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if user.role != 'admin' and parcelle.user != user:
            return Response({"error": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)

        predictions = Prediction.objects.filter(parcelle=parcelle).order_by('-prediction_date')
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
