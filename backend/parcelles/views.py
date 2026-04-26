# from rest_framework import viewsets, permissions , status
# from rest_framework.response import Response
# from .models import Parcelle
# from .serializers import ParcelleSerializer

# class ParcelleViewSet(viewsets.ModelViewSet):
#     serializer_class = ParcelleSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'admin':
#             return Parcelle.objects.all()
#         return Parcelle.objects.filter(user=user)

#     def create(self, request, *args, **kwargs):
#         print("=" * 60)
#         print("DATA RECUE:", request.data)
#         print("USER:", request.user)
#         print("USER ID:", request.user.id)
#         print("USER ROLE:", getattr(request.user, 'role', 'N/A'))
#         print("=" * 60)
        
#         serializer = self.get_serializer(data=request.data)
        
#         if not serializer.is_valid():
#             print("=" * 60)
#             print("ERREURS SERIALIZER:", serializer.errors)
#             print("=" * 60)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
        
#         print("=" * 60)
#         print("PARCELLE CREE:", serializer.data)
#         print("=" * 60)
        
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#     def perform_create(self, serializer):
#         print("PERFORM_CREATE - USER:", self.request.user)
#         serializer.save(user=self.request.user)

#     # def perform_create(self, serializer):
        
#     #     serializer.save(user=self.request.user)

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Parcelle
from .serializers import ParcelleSerializer

# Importez votre serializer de prédiction (ajustez selon votre projet)
# from predictions.serializers import PredictionSerializer

class ParcelleViewSet(viewsets.ModelViewSet):
    serializer_class = ParcelleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Parcelle.objects.all()
        return Parcelle.objects.filter(user=user)

    # ============================================================
    # 🔍 DEBUG : Récupérer une parcelle (détail)
    # URL: GET /api/parcelles/<uuid>/
    # ============================================================
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        print("=" * 60)
        print("🔍 [retrieve] REQUETE RECUE")
        print(f"🔍 [retrieve] PK/UUID: {pk}")
        print(f"🔍 [retrieve] User: {request.user} (ID: {request.user.id})")
        print(f"🔍 [retrieve] URL: {request.path}")
        print(f"🔍 [retrieve] Method: {request.method}")
        print("=" * 60)
        
        try:
            instance = self.get_object()
            print(f"✅ [retrieve] Parcelle TROUVEE: {instance.nom} (ID: {instance.id})")
        except Exception as e:
            print(f"❌ [retrieve] ERREUR: {str(e)}")
            print(f"❌ [retrieve] Type: {type(e).__name__}")
            raise  # Relance l'exception pour voir le vrai 404
        
        serializer = self.get_serializer(instance)
        data = serializer.data
        print(f"📤 [retrieve] Données retournées: {data}")
        print("=" * 60)
        
        return Response(data)

    # ============================================================
    # 🔍 DEBUG : Lister les parcelles
    # ============================================================
    def list(self, request, *args, **kwargs):
        print("=" * 60)
        print("🔍 [list] LISTE DES PARCELLES DEMANDEE")
        print(f"🔍 [list] User: {request.user} (ID: {request.user.id})")
        print(f"🔍 [list] Queryset count: {self.get_queryset().count()}")
        print("=" * 60)
        
        return super().list(request, *args, **kwargs)

    # ============================================================
    # ✅ ACTION CUSTOM : Historique des prédictions
    # URL: GET /api/parcelles/<uuid>/prediction-history/
    # ============================================================
    @action(detail=True, methods=['get'], url_path='prediction-history')
    def prediction_history(self, request, pk=None):
        print("=" * 60)
        print("🔍 [prediction_history] REQUETE RECUE")
        print(f"🔍 [prediction_history] Parcelle ID: {pk}")
        print(f"🔍 [prediction_history] User: {request.user}")
        print(f"🔍 [prediction_history] URL complete: {request.path}")
        print("=" * 60)
        
        # Récupérer la parcelle
        try:
            parcelle = self.get_object()
            print(f"✅ [prediction_history] Parcelle trouvée: {parcelle.nom}")
        except Exception as e:
            print(f"❌ [prediction_history] Erreur get_object: {str(e)}")
            return Response(
                {"error": "Parcelle non trouvée", "detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier la relation predictions
        try:
            # ❗ Ajustez selon votre modèle (relation inverse, etc.)
            predictions = getattr(parcelle, 'predictions', None)
            if predictions is None:
                print("⚠️ [prediction_history] Relation 'predictions' non trouvée")
                print("⚠️ [prediction_history] Attributs disponibles:", dir(parcelle))
                return Response(
                    {"error": "Relation predictions non configurée"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            predictions_list = predictions.all()
            count = predictions_list.count()
            print(f"📊 [prediction_history] Nombre de prédictions: {count}")
            
            # Si pas de serializer de prédiction, retournez des données basiques
            # data = PredictionSerializer(predictions_list, many=True).data
            
            # 🔧 VERSION TEMPORAIRE (sans serializer de prédiction)
            data = [
                {
                    "id": str(p.id),
                    "date": str(p.created_at) if hasattr(p, 'created_at') else None,
                    "value": getattr(p, 'value', None),
                }
                for p in predictions_list
            ]
            
            print(f"📤 [prediction_history] Données retournées: {len(data)} items")
            print("=" * 60)
            
            return Response({
                "parcelle_id": str(parcelle.id),
                "parcelle_nom": parcelle.nom,
                "predictions_count": count,
                "predictions": data
            })
            
        except Exception as e:
            print(f"❌ [prediction_history] Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # ============================================================
    # Vos méthodes existantes (create, perform_create)
    # ============================================================
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