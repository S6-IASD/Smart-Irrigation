"""
Scheduler de prédictions automatiques.

Tâche : chaque soir à 22h00, lance une prédiction pour toutes
        les parcelles actives qui n'ont pas encore été traitées aujourd'hui.

Démarré via PredictionConfig.ready() dans apps.py.

Stratégie multi-worker Gunicorn :
  - Un verrou fichier exclusif (fcntl.flock) garantit qu'un seul worker
    démarre le thread de scheduling.
  - Le scheduler est démarré AVANT l'enregistrement du job, ce qui force
    le DjangoJobStore à charger les lignes existantes de la DB en mémoire ;
    ainsi replace_existing=True émet un UPDATE (et non un INSERT) sur les
    redémarrages — éliminant le conflit de clé primaire.
"""
import os
import logging
import tempfile
from django.db import IntegrityError, connection
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)

# ── Verrou fichier (partagé dans le même container entre workers) ─────────────
_LOCK_FILE = os.path.join(tempfile.gettempdir(), "smart_irrigation_scheduler.lock")
_lock_fh   = None   # file handle maintenu ouvert pour conserver le verrou

# Instance globale du scheduler (singleton par worker)
_scheduler = None


def _acquire_scheduler_lock() -> bool:
    """
    Tente d'acquérir un verrou fichier exclusif non-bloquant (Linux/Docker).
    Retourne True si ce worker est l'élu, False sinon.
    Sur Windows (développement hors container) retourne toujours True.
    """
    global _lock_fh
    try:
        import fcntl
        fh = open(_LOCK_FILE, "w")
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        _lock_fh = fh   # garde le descripteur ouvert → le verrou reste actif
        return True
    except ImportError:
        return True     # Windows : pas de fcntl, on laisse passer
    except OSError:
        return False    # Un autre worker détient déjà le verrou


def _purge_stale_job_row():
    """
    Supprime l'entrée 'daily_irrigation_prediction' de la table APScheduler
    si elle existe. Cela garantit que add_job() fera toujours un INSERT propre
    (ou, si le scheduler est déjà démarré, un UPDATE via replace_existing).

    Appelé uniquement par le worker élu, avant de démarrer le scheduler.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM django_apscheduler_djangojob WHERE id = %s",
                ["daily_irrigation_prediction"],
            )
        logger.debug("[Scheduler] Ancienne entrée DB supprimée (si existante).")
    except Exception as exc:
        # La table peut ne pas encore exister lors du tout premier démarrage.
        logger.debug(f"[Scheduler] Nettoyage DB ignoré : {exc}")


def run_daily_predictions():
    """
    Tâche planifiée : génère une prédiction pour chaque parcelle
    qui n'en a pas encore eu une aujourd'hui.
    """
    from parcelles.models import Parcelle
    from prediction.models import Prediction
    from prediction.views import compute_prediction

    today = timezone.now().date()
    parcelles = Parcelle.objects.all()

    logger.info(
        f"[Scheduler] Lancement des prédictions automatiques — "
        f"{today} — {parcelles.count()} parcelle(s)"
    )

    success_count = skip_count = error_count = 0

    for parcelle in parcelles:
        # if Prediction.objects.filter(parcelle=parcelle, created_at__date=today).exists():
        #     logger.debug(f"[Scheduler] '{parcelle.nom}' déjà traitée aujourd'hui — ignorée.")
        #     skip_count += 1
        #     continue

        try:
            prediction_obj, error = compute_prediction(parcelle)
            if error:
                logger.error(f"[Scheduler] Erreur '{parcelle.nom}': {error}")
                error_count += 1
            else:
                logger.info(
                    f"[Scheduler] ✓ '{parcelle.nom}' → {prediction_obj.eau_litres:.1f} L "
                    f"(déclenchement: {prediction_obj.declenchement}, mode: {prediction_obj.mode})"
                )
                success_count += 1
        except Exception as exc:
            logger.error(f"[Scheduler] Exception '{parcelle.nom}': {exc}", exc_info=True)
            error_count += 1

    logger.info(
        f"[Scheduler] Terminé — {success_count} succès, "
        f"{skip_count} ignorées, {error_count} erreurs"
    )


def start_scheduler():
    """
    Démarre le scheduler APScheduler avec la tâche journalière à 22h00.
    Appelé depuis PredictionConfig.ready() (une fois par worker Gunicorn).

    Seul le worker qui acquiert le verrou fichier exécute réellement ce bloc.
    """
    global _scheduler

    # ── Étape 0 : verrou — un seul worker démarre le scheduler ───────────────
    if not _acquire_scheduler_lock():
        logger.info(
            "[Scheduler] Verrou détenu par un autre worker — "
            "ce worker n'exécutera pas de scheduler."
        )
        return

    if _scheduler is not None and _scheduler.running:
        logger.info("[Scheduler] Déjà démarré, on ignore.")
        return

    # ── Étape 1 : supprimer la ligne DB obsolète ──────────────────────────────
    # Évite le conflit INSERT / clé primaire causé par replace_existing=True
    # qui fait un INSERT au lieu d'un UPDATE quand le jobstore n'est pas encore
    # initialisé (avant start()).
    _purge_stale_job_row()

    _scheduler = BackgroundScheduler(timezone="Africa/Casablanca")
    _scheduler.add_jobstore(DjangoJobStore(), "default")

    # ── Étape 2 : démarrer le scheduler (charge la DB en mémoire) ────────────
    try:
        _scheduler.start()
        logger.info("[Scheduler] Démarré.")
    except Exception as e:
        logger.error(f"[Scheduler] Échec du démarrage : {e}", exc_info=True)
        return

    # ── Étape 3 : enregistrer le job (UPDATE garanti car DB déjà en mémoire) ──
    try:
        _scheduler.add_job(
            run_daily_predictions,
            trigger=CronTrigger(hour=22, minute=25), # Ancienne valeur
            #trigger=CronTrigger(minute="*"), # TEST : S'exécute CHAQUE MINUTE
            id="daily_irrigation_prediction",
            name="Prédiction journalière d'irrigation (TEST CHAQUE MINUTE)",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=3600,
            coalesce=True,
        )
        logger.info("[Scheduler] Job enregistré — prédictions à 22h00 chaque jour.")
    except IntegrityError:
        logger.warning(
            "[Scheduler] Conflit d'insertion résiduel — le job existant sera utilisé."
        )


def stop_scheduler():
    """Arrête proprement le scheduler (utile pour les tests)."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Arrêté.")
