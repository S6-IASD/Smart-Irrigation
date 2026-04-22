from django.contrib import admin
from .models import Capteur, LectureCapteur


class LectureCapteurInline(admin.TabularInline):
    """Lectures affichées en inline sur la page du capteur."""
    model = LectureCapteur
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('humidite_sol', 'temperature_sol', 'N', 'P', 'K', 'timestamp')


@admin.register(Capteur)
class CapteurAdmin(admin.ModelAdmin):
    """Administration du modèle Capteur."""

    list_display = ('type', 'mode', 'device_id', 'api_key', 'parcelle', 'created_at')
    list_filter = ('type', 'mode', 'created_at')
    search_fields = ('type', 'device_id', 'parcelle__nom')
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('parcelle',)
    inlines = [LectureCapteurInline]

    readonly_fields = ('created_at', 'api_key')


@admin.register(LectureCapteur)
class LectureCapteurAdmin(admin.ModelAdmin):
    """Administration du modèle LectureCapteur."""

    list_display = ('capteur', 'humidite_sol', 'temperature_sol', 'N', 'P', 'K', 'timestamp')
    list_filter = ('capteur__type', 'timestamp')
    search_fields = ('capteur__parcelle__nom',)
    ordering = ('-timestamp',)
    list_per_page = 25
    list_select_related = ('capteur',)

    readonly_fields = ('timestamp',)
