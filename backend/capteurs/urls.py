from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CapteurViewSet, LectureCapteurViewSet

router = DefaultRouter()
router.register(r'capteurs', CapteurViewSet, basename='capteur')
router.register(r'lectures', LectureCapteurViewSet, basename='lecture')

urlpatterns = [
    path('', include(router.urls)),
]
