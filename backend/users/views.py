from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .serializers import UserSerializer, RegisterSerializer
from parcelles.models import Parcelle
from capteurs.models import Capteur, LectureCapteur
from prediction.models import Prediction
from meteo.models import DonneeMeteo

User = get_user_model()

class IsAdminRole(permissions.BasePermission):
    """Permet l'accès uniquement aux utilisateurs avec le rôle admin."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        print("=" * 60)
        print("DATA RECUE:", request.data)
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
        print("UTILISATEUR CREE:", serializer.data)
        print("=" * 60)
        
        return Response(
            {"message": "Inscription réussie", "user": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = (IsAdminRole,)


class AdminDashboardStatsView(APIView):
    permission_classes = (IsAdminRole,)

    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)

        total_users = User.objects.count()
        total_parcelles = Parcelle.objects.count()
        total_capteurs = Capteur.objects.count()
        total_predictions = Prediction.objects.count()

        new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()
        new_parcelles_30d = Parcelle.objects.filter(created_at__gte=thirty_days_ago).count()
        predictions_30d = Prediction.objects.filter(created_at__gte=thirty_days_ago).count()
        lectures_7d = LectureCapteur.objects.filter(timestamp__gte=seven_days_ago).count()

        predictions_triggered = Prediction.objects.filter(declenchement=True).count()
        trigger_rate = round((predictions_triggered / total_predictions * 100), 1) if total_predictions > 0 else 0

        predictions_success = Prediction.objects.filter(status='success').count()
        predictions_failed = Prediction.objects.filter(status='failed').count()
        predictions_pending = Prediction.objects.filter(status='pending').count()

        return Response({
            'total_users': total_users,
            'total_parcelles': total_parcelles,
            'total_capteurs': total_capteurs,
            'total_predictions': total_predictions,
            'new_users_30d': new_users_30d,
            'new_parcelles_30d': new_parcelles_30d,
            'predictions_30d': predictions_30d,
            'lectures_7d': lectures_7d,
            'predictions_triggered': predictions_triggered,
            'trigger_rate': trigger_rate,
            'predictions_success': predictions_success,
            'predictions_failed': predictions_failed,
            'predictions_pending': predictions_pending,
        })

