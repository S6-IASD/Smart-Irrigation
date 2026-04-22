from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    """Administration du modèle Prediction."""

    list_display = (
        'parcelle', 'prediction_date', 'eau_litres',
        'declenchement', 'status', 'mode', 'weather_source', 'created_at',
    )
    list_filter = ('status', 'declenchement', 'mode', 'weather_source', 'prediction_date')
    search_fields = ('parcelle__nom',)
    ordering = ('-prediction_date',)
    list_per_page = 25
    list_select_related = ('parcelle', 'lecture', 'meteo')
    date_hierarchy = 'prediction_date'

    fieldsets = (
        ('Parcelle & Sources', {'fields': ('parcelle', 'lecture', 'meteo')}),
        ('Résultat', {'fields': ('prediction_date', 'eau_litres', 'declenchement', 'status')}),
        ('Métadonnées', {'fields': ('mode', 'weather_source')}),
    )

    readonly_fields = ('created_at',)
