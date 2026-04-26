import sys
from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'

    def ready(self):
        """
        Appelé une seule fois au démarrage de Django.
        On démarre le scheduler seulement en dehors des commandes de gestion
        (migrate, collectstatic, etc.) pour éviter les double-démarrages.
        """
        # Ne pas démarrer le scheduler pendant les commandes manage.py
        # (migrate, shell, test, etc.) — seulement pour gunicorn/runserver
        is_manage_command = (
            len(sys.argv) > 1 and sys.argv[1] in (
                'migrate', 'makemigrations', 'collectstatic',
                'shell', 'test', 'createsuperuser', 'check',
                'dumpdata', 'loaddata', 'flush',
            )
        )
        if not is_manage_command:
            from prediction.scheduler import start_scheduler
            start_scheduler()
