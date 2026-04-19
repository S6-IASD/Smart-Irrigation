import uuid
from django.db import models

class DonneeMeteo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parcelle = models.ForeignKey('parcelles.Parcelle', on_delete=models.CASCADE, related_name='meteo_data')
    T_min = models.FloatField()
    T_max = models.FloatField()
    pluie_mm = models.FloatField()
    mois = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return f"Meteo {self.parcelle.nom} - {self.date}"
