from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from lms_project.models import Institution, Domain
from core.utils.provisioning import provision_default_admin
from django_tenants.utils import schema_context
from core.models import User
from django.db import connection
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    SuperAdminSignupSerializer,
    InstitutionRegisterSerializer,
    TenantLoginSerializer
)

User = get_user_model()

# 🔐 Signup for Client
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='client')
            return Response({"message": "Client registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔐 Signup for SuperAdmin
class SuperAdminSignupView(generics.CreateAPIView):
    serializer_class = SuperAdminSignupSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='superadmin')
            return Response({"message": "SuperAdmin registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔑 Login View (Public Schema)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "role": user.role,
                    "username": user.username
                })
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔒 Protected View (for testing JWT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello {request.user.username}, you are authenticated!"})

# 🏫 Register Institution (Tenant Provisioning)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_institution(request):
    if request.user.role != 'client':
        return Response({"error": "Only clients can register institutions."}, status=403)

    serializer = InstitutionRegisterSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        duration_days = 90 if data['plan'] == 'free' else 365
        expiry_date = timezone.now().date() + timezone.timedelta(days=duration_days)

        institution = Institution.objects.create(
            name=data['institution_name'],
            schema_name=data['schema_name'],
            location=data['location'],
            contacts=data['contacts'],
            website=data.get('website', ''),
            logo=data.get('logo', None),
            plan=data['plan'],
            owner=request.user,
            paid_until=expiry_date,
            is_active=True
        )

        Domain.objects.create(
            domain=data['domain_url'],
            tenant=institution,
            is_primary=True
        )

        # ✅ Provision admin and get registration number
        reg_number = provision_default_admin(
            schema_name=data['schema_name'],
            institution_name=data['institution_name']
        )

        return Response({
            "message": "Institution registered successfully",
            "subdomain": data['domain_url'],
            "dashboard_url": f"http://{data['domain_url']}/login",
            "registration_number": reg_number,
            "password": "admin"
        }, status=201)

    return Response(serializer.errors, status=400)

# 🔑 Tenant Login View (Schema-specific)
class TenantLoginView(generics.GenericAPIView):
    serializer_class = TenantLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name  # Django-tenants auto-detects schema from subdomain
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reg = serializer.validated_data['registration_number']
            password = serializer.validated_data['password']

            with schema_context(schema_name):
                user = authenticate(request, registration_number=reg, password=password)
                if user:
                    refresh = RefreshToken.for_user(user)
                    dashboard_url = f"/admin-dashboard/" if user.role == 'superadmin' else "/user-dashboard/"
                    return Response({
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "role": user.role,
                        "username": user.username,
                        "dashboard": dashboard_url
                    })
                print("Current schema:", connection.schema_name)
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)