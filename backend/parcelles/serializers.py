from rest_framework import serializers
from .models import Parcelle

class ParcelleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcelle
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
