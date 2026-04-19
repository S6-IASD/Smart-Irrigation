from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'status', 'eau_litres', 'declenchement')

class PredictionInputSerializer(serializers.Serializer):
    parcelle_id = serializers.UUIDField()
    humidite_sol = serializers.FloatField(required=False, default=0)
    temperature_sol = serializers.FloatField(required=False, default=0)
    N = serializers.FloatField(required=False, default=0)
    P = serializers.FloatField(required=False, default=0)
    K = serializers.FloatField(required=False, default=0)
