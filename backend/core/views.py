from django.core.management import call_command
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from sales.models import SalesTransaction
from .serializers import RegisterSerializer


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "backend"})


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
                "is_superuser": request.user.is_superuser,
            }
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        demo_seeded = False
        if not SalesTransaction.objects.exists():
            call_command("seed_demo_data")
            demo_seeded = True

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully.",
                "demo_seeded": demo_seeded,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )