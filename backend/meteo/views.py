from rest_framework import viewsets, permissions
from .models import DonneeMeteo
from .serializers import DonneeMeteoSerializer

class DonneeMeteoViewSet(viewsets.ModelViewSet):
    serializer_class = DonneeMeteoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return DonneeMeteo.objects.all()
        return DonneeMeteo.objects.filter(parcelle__user=user)
