import uuid
from django.db import models
from django.conf import settings

class Parcelle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parcelles')
    nom = models.CharField(max_length=255)
    superficie_ha = models.FloatField()
    type_plante = models.CharField(max_length=100)
    stade = models.CharField(max_length=50, choices=[
        ('jeune', 'Jeune'),
        ('mature', 'Mature'),
        ('fin', 'Fin')
    ])
    latitude = models.FloatField()
    longitude = models.FloatField()
    ville = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
