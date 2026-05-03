import uuid
from django.db import models

class Prediction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcelle = models.ForeignKey('parcelles.Parcelle', on_delete=models.CASCADE, related_name='predictions')
    lecture = models.ForeignKey('capteurs.LectureCapteur', on_delete=models.SET_NULL, null=True, blank=True)
    meteo = models.ForeignKey('meteo.DonneeMeteo', on_delete=models.SET_NULL, null=True, blank=True)
    prediction_date = models.DateField()
    quantite_predite = models.FloatField()
    quantite_reelle = models.FloatField(null=True, blank=True)
    unite = models.CharField(max_length=20, default='L/parcelle')
    declenchement = models.BooleanField(default=False)
    status = models.CharField(max_length=50) # e.g. success, failed, pending
    mode = models.CharField(max_length=20, default='fallback')
    weather_source = models.CharField(max_length=50, default='Open-Meteo')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.parcelle.nom} - {self.prediction_date}"
