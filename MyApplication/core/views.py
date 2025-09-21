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
from .serializers import InstitutionOverviewSerializer

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
        return Response({"error": "Only clients can register institutions."}, status=status.HTTP_403_FORBIDDEN)

    serializer = InstitutionRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    duration_days = 90 if data['plan'] == 'free' else 365
    expiry_date = timezone.now().date() + timezone.timedelta(days=duration_days)

    # ✅ Create tenant (institution) in public schema
    institution = Institution.objects.create(
        name=data['name'],
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

    # ✅ Create domain with .localhost suffix
    Domain.objects.create(
        domain=f"{data['domain_url']}.localhost",
        tenant=institution,
        is_primary=True
    )

    # ✅ Provision default superadmin
    reg_number = provision_default_admin(
        schema_name=data['schema_name'],
        institution_name=data['name']
    )

    # ✅ Write institution info inside tenant schema
    with schema_context(data['schema_name']):
        Institution.objects.create(
            name=data['name'],
            location=data['location'],
            contacts=data['contacts'],
            website=data.get('website', ''),
            logo=data.get('logo', None),
            plan=data['plan'],
            paid_until=expiry_date,
            is_active=True
        )

    return Response({
        "message": "Institution registered successfully",
        "institution": {
            "name": data['name'],
            "schema": data['schema_name'],
            "subdomain": f"{data['domain_url']}.localhost",
            "dashboard_url": f"http://{data['domain_url']}.localhost/login",
            "registration_number": reg_number,
            "default_password": "admin"
        }
    }, status=status.HTTP_201_CREATED)

# 🔑 Tenant Login View (Schema-specific)
class TenantLoginView(generics.GenericAPIView):
    serializer_class = TenantLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        schema_name = connection.schema_name
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            reg = serializer.validated_data['registration_number']
            password = serializer.validated_data['password']

            with schema_context(schema_name):
                user = authenticate(request, registration_number=reg, password=password)
                if user:
                    refresh = RefreshToken.for_user(user)
                    dashboard_url = "/admin-dashboard/" if user.role == 'superadmin' else "/user-dashboard/"
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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_institution(request):
    if request.user.role != 'client':
        return Response({"error": "Only clients can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

    institutions = Institution.objects.filter(owner=request.user)
    if not institutions.exists():
        return Response([], status=status.HTTP_200_OK)

    serializer = InstitutionOverviewSerializer(institutions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_institution(request, schema_name):
    try:
        institution = Institution.objects.get(schema_name=schema_name, owner=request.user)
    except Institution.DoesNotExist:
        return Response({"error": "Institution not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

    serializer = InstitutionRegisterSerializer(instance=institution, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Institution updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_institution(request, schema_name):
    try:
        institution = Institution.objects.get(schema_name=schema_name, owner=request.user)
    except Institution.DoesNotExist:
        return Response({"error": "Institution not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

    institution.delete()
    Domain.objects.filter(tenant__schema_name=schema_name).delete()
    return Response({"message": "Institution deleted successfully."}, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from lms_project.models import Institution

@api_view(['GET'])
@permission_classes([AllowAny])
def institution_info_view(request):
    institution = Institution.objects.first()
    if not institution:
        return Response({"error": "Institution not found"}, status=404)

    return Response({
        "name": institution.name,
        "location": institution.location,
        "contacts": institution.contacts,
        "website": institution.website,
        "logo": request.build_absolute_uri(institution.logo.url) if institution.logo else None,
        
    })