from rest_framework import serializers
from .models import Parcelle

class ParcelleSerializer(serializers.ModelSerializer):
    user_nom = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Parcelle
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
