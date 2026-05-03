from django.contrib import admin
from .models import DonneeMeteo


@admin.register(DonneeMeteo)
class DonneeMeteoAdmin(admin.ModelAdmin):
    """Administration du modèle DonneeMeteo."""

    list_display = ('parcelle', 'date', 'mois', 'T_min', 'T_max', 'pluie_mm')
    list_filter = ('mois', 'date', 'parcelle')
    search_fields = ('parcelle__nom',)
    ordering = ('-date',)
    list_per_page = 25
    list_select_related = ('parcelle',)
    date_hierarchy = 'date'

    readonly_fields = ()
