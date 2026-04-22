from rest_framework import viewsets, permissions , status
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
        print("=" * 60)
        print("DATA RECUE:", request.data)
        print("USER:", request.user)
        print("USER ID:", request.user.id)
        print("USER ROLE:", getattr(request.user, 'role', 'N/A'))
        print("=" * 60)
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            print("=" * 60)
            print("ERREURS SERIALIZER:", serializer.errors)
            print("=" * 60)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        print("=" * 60)
        print("PARCELLE CREE:", serializer.data)
        print("=" * 60)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        print("PERFORM_CREATE - USER:", self.request.user)
        serializer.save(user=self.request.user)

    # def perform_create(self, serializer):
        
    #     serializer.save(user=self.request.user)
