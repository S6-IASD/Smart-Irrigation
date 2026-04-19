from rest_framework import viewsets, permissions
from .models import Capteur, LectureCapteur
from .serializers import CapteurSerializer, LectureCapteurSerializer

class CapteurViewSet(viewsets.ModelViewSet):
    serializer_class = CapteurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Capteur.objects.all()
        return Capteur.objects.filter(parcelle__user=user)

class LectureCapteurViewSet(viewsets.ModelViewSet):
    serializer_class = LectureCapteurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return LectureCapteur.objects.all()
        return LectureCapteur.objects.filter(capteur__parcelle__user=user)
