from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonneeMeteoViewSet

router = DefaultRouter()
router.register(r'', DonneeMeteoViewSet, basename='meteo')

urlpatterns = [
    path('', include(router.urls)),
]
