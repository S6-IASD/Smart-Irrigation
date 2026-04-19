from rest_framework import viewsets, permissions
from .models import Parcelle
from .serializers import ParcelleSerializer

class ParcelleViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Parcelle.objects.all()
        return Parcelle.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
