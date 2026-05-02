from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CapteurViewSet, LectureCapteurViewSet, IoTIngestView

router = DefaultRouter()
router.register(r'capteurs', CapteurViewSet, basename='capteur')
router.register(r'lectures', LectureCapteurViewSet, basename='lecture')

urlpatterns = [
    path('iot/ingest/', IoTIngestView.as_view(), name='iot-ingest'),
    path('', include(router.urls)),
]
