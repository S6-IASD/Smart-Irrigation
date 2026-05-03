import uuid
import secrets
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

def generate_api_key():
    return secrets.token_urlsafe(32)

class Capteur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcelle = models.ForeignKey('parcelles.Parcelle', on_delete=models.CASCADE, related_name='capteurs')
    type = models.CharField(max_length=50) # humidity/temperature/npk/etc
    mode = models.CharField(max_length=50) # IoT/manual
    device_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    api_key = models.CharField(max_length=100, default=generate_api_key, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.parcelle.nom} (Device: {self.device_id or 'N/A'})"

class LectureCapteur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE, related_name='lectures')
    humidite_sol = models.FloatField(null=True, blank=True , validators=[MinValueValidator(0.0)])
    temperature_sol = models.FloatField(null=True, blank=True)
    N = models.FloatField(null=True, validators=[MinValueValidator(0.0)], blank=True)
    P = models.FloatField(null=True, validators=[MinValueValidator(0.0)], blank=True)
    K = models.FloatField(null=True, validators=[MinValueValidator(0.0)], blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Lecture {self.capteur.type} - {self.timestamp}"
