from rest_framework import serializers
from .models import Capteur, LectureCapteur

class CapteurSerializer(serializers.ModelSerializer):
    parcelle_nom = serializers.CharField(source='parcelle.nom', read_only=True)
    user_nom = serializers.CharField(source='parcelle.user.username', read_only=True)

    class Meta:
        model = Capteur
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class LectureCapteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = LectureCapteur
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')
