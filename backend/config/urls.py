from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/parcelles/', include('parcelles.urls')),
    path('api/', include('capteurs.urls')), # will serve /api/capteurs/ and /api/lectures/
    path('api/meteo/', include('meteo.urls')),
    path('api/prediction/', include('prediction.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
