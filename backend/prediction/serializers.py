from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'status', 'quantite_predite', 'unite', 'declenchement')

class PredictionInputSerializer(serializers.Serializer):
    """
    parcelle_id : obligatoire.
    Champs capteurs : optionnels — si fournis, utilisés directement (mode manuel).
                      Sinon, la moyenne des 24h précédentes est calculée (mode auto).
    force : permet de relancer même si une prédiction existe déjà aujourd'hui.
    """
    parcelle_id   = serializers.UUIDField()
    # Données capteurs manuelles (optionnelles)
    humidite_sol    = serializers.FloatField(required=False, min_value=0,   max_value=100)
    temperature_sol = serializers.FloatField(required=False, min_value=-10, max_value=60)
    N               = serializers.FloatField(required=False, min_value=0)
    P               = serializers.FloatField(required=False, min_value=0)
    K               = serializers.FloatField(required=False, min_value=0)
    # Options
    force = serializers.BooleanField(required=False, default=False)
