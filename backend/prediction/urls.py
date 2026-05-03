from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionAPIView, PredictionHistoryViewSet

router = DefaultRouter()
router.register(r'history', PredictionHistoryViewSet, basename='prediction_history')

urlpatterns = [
    # POST /api/prediction/  → lance une prédiction
    path('', PredictionAPIView.as_view(), name='prediction_api'),
    # GET /api/prediction/history/              → liste toutes les prédictions de l'utilisateur
    # GET /api/prediction/history/{parcelle_id}/ → historique d'une parcelle (custom action)
    path('history/<str:pk>/', PredictionHistoryViewSet.as_view({'get': 'by_parcelle'}), name='prediction_history_by_parcelle'),
    path('', include(router.urls)),
]

