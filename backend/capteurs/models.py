import uuid
from django.db import models

class Capteur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcelle = models.ForeignKey('parcelles.Parcelle', on_delete=models.CASCADE, related_name='capteurs')
    type = models.CharField(max_length=50) # humidity/temperature/npk/etc
    mode = models.CharField(max_length=50) # IoT/manual
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.parcelle.nom}"

class LectureCapteur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capteur = models.ForeignKey(Capteur, on_delete=models.CASCADE, related_name='lectures')
    humidite_sol = models.FloatField(null=True, blank=True)
    temperature_sol = models.FloatField(null=True, blank=True)
    N = models.FloatField(null=True, blank=True)
    P = models.FloatField(null=True, blank=True)
    K = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lecture {self.capteur.type} - {self.timestamp}"
