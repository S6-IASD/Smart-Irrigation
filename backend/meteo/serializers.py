from rest_framework import serializers
from .models import DonneeMeteo

class DonneeMeteoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonneeMeteo
        fields = '__all__'
        read_only_fields = ('id',)
