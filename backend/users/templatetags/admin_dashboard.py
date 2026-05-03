from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.inclusion_tag('admin/dashboard_stats.html')
def dashboard_stats():
    """Calcule et retourne les statistiques globales de la plateforme."""
    from users.models import User
    from parcelles.models import Parcelle
    from capteurs.models import Capteur, LectureCapteur
    from prediction.models import Prediction
    from meteo.models import DonneeMeteo

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    # Comptages globaux
    total_users = User.objects.count()
    total_parcelles = Parcelle.objects.count()
    total_capteurs = Capteur.objects.count()
    total_predictions = Prediction.objects.count()
    total_lectures = LectureCapteur.objects.count()
    total_meteo = DonneeMeteo.objects.count()

    # Activité récente (30 jours)
    new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()
    new_parcelles_30d = Parcelle.objects.filter(created_at__gte=thirty_days_ago).count()
    predictions_30d = Prediction.objects.filter(created_at__gte=thirty_days_ago).count()
    lectures_7d = LectureCapteur.objects.filter(timestamp__gte=seven_days_ago).count()

    # Prédictions déclenchées (irrigation nécessaire)
    predictions_triggered = Prediction.objects.filter(declenchement=True).count()
    trigger_rate = round((predictions_triggered / total_predictions * 100), 1) if total_predictions > 0 else 0

    # Répartition des statuts de prédictions
    predictions_success = Prediction.objects.filter(status='success').count()
    predictions_failed = Prediction.objects.filter(status='failed').count()
    predictions_pending = Prediction.objects.filter(status='pending').count()

    # Dernières parcelles
    recent_parcelles = Parcelle.objects.select_related('user').order_by('-created_at')[:5]

    # Dernières prédictions
    recent_predictions = Prediction.objects.select_related('parcelle').order_by('-created_at')[:5]

    return {
        'total_users': total_users,
        'total_parcelles': total_parcelles,
        'total_capteurs': total_capteurs,
        'total_predictions': total_predictions,
        'total_lectures': total_lectures,
        'total_meteo': total_meteo,
        'new_users_30d': new_users_30d,
        'new_parcelles_30d': new_parcelles_30d,
        'predictions_30d': predictions_30d,
        'lectures_7d': lectures_7d,
        'predictions_triggered': predictions_triggered,
        'trigger_rate': trigger_rate,
        'predictions_success': predictions_success,
        'predictions_failed': predictions_failed,
        'predictions_pending': predictions_pending,
        'recent_parcelles': recent_parcelles,
        'recent_predictions': recent_predictions,
    }
