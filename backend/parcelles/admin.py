from django.contrib import admin
from .models import Parcelle


@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    """Administration du modèle Parcelle."""

    list_display = ('nom', 'user', 'type_plante', 'stade', 'superficie_ha', 'ville', 'created_at')
    list_filter = ('type_plante', 'stade', 'ville', 'created_at')
    search_fields = ('nom', 'type_plante', 'ville', 'user__username')
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('user',)

    fieldsets = (
        ('Informations générales', {'fields': ('nom', 'user', 'type_plante', 'stade', 'superficie_ha')}),
        ('Localisation', {'fields': ('ville', 'latitude', 'longitude')}),
    )

    readonly_fields = ('created_at',)
