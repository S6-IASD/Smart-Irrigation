from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PredictionAPIView, PredictionHistoryViewSet

router = DefaultRouter()
router.register(r'history', PredictionHistoryViewSet, basename='prediction_history')

urlpatterns = [
    path('', PredictionAPIView.as_view(), name='prediction_api'),
    path('', include(router.urls)),
]
