from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from lms_project.helpers.provision import provision_tenant
from lms_project.models import Institution, Domain
import os
from django.conf import settings
from django_tenants.utils import schema_context
from django.db import connection
from rest_framework.parsers import JSONParser
from core.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, authenticate
from .permissions import IsSuperAdmin
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.db.models import Count
from collections import OrderedDict
from auditlog.models import LogEntry
from .models import SystemNotification
import jwt
from datetime import datetime



from .serializers import (
    InstitutionRegisterSerializer,
    InstitutionPublicSerializer,
    InstitutionSerializer,
    SignupSerializer,
    LoginSerializer,
    SuperAdminSignupSerializer,
    InstitutionListSerializer,
    AnalyticsSerializer,
    SystemNotificationSerializer,
    
)




class RegisterInstitutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = InstitutionRegisterSerializer(data=request.data)
        if serializer.is_valid():
            client_user = request.user  # ✅ Usifetch tena kutoka public

            with schema_context("public"):  # ✅ Force provisioning to public
                institution, login_user = provision_tenant(serializer.validated_data, client_user)

            return Response({
                "message": f"Institution '{institution.name}' registered successfully.",
                "subdomain": request.data['domain'],
                "admin_login": {
                    "reg_number": institution.registration_number,
                    "default_password": "admin"
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class ClientInstitutionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        institutions = Institution.objects.filter(
            owner_email=request.user.email,
            owner_registration_number=request.user.registration_number
        )
        serializer = InstitutionSerializer(institutions, many=True, context={"request": request})
        return Response(serializer.data)


class DeleteInstitutionView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, schema_name):
        try:
            institution = Institution.objects.get(
                schema_name=schema_name,
                owner_email=request.user.email,
                owner_registration_number=request.user.registration_number
            )
            domain = Domain.objects.get(tenant=institution)

            if institution.logo and institution.logo.name:
                logo_path = os.path.join(settings.MEDIA_ROOT, institution.logo.name)
                if os.path.exists(logo_path):
                    os.remove(logo_path)

            connection.set_schema_to_public()
            institution.delete(force_drop=True)
            domain.delete()

            return Response({"message": "Institution and logo deleted successfully."}, status=200)
        except Institution.DoesNotExist:
            return Response({"error": "Institution not found or unauthorized."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)




class UpdateInstitutionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def put(self, request, schema_name):
        with schema_context("public"):  # ✅ Fetch institution safely
            try:
                institution = Institution.objects.get(
                    schema_name=schema_name,
                    owner_email=request.user.email,
                    owner_registration_number=request.user.registration_number
                )
            except Institution.DoesNotExist:
                return Response({"error": "Institution not found or unauthorized."}, status=404)

        with schema_context(schema_name):  # ✅ Update inside correct schema
            serializer = InstitutionSerializer(institution, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Institution updated successfully.", "institution": serializer.data}, status=200)
            return Response(serializer.errors, status=400)


class InstitutionInfoView(APIView):
    def get(self, request):
        try:
            institution = Institution.objects.get(schema_name=request.tenant.schema_name)
            serializer = InstitutionPublicSerializer(institution, context={"request": request})
            return Response(serializer.data, status=200)
        except Institution.DoesNotExist:
            return Response({"error": "Institution not found."}, status=404)


class TenantLoginView(APIView):
    def post(self, request):
        reg_number = request.data.get("registration_number")
        password = request.data.get("password")

        if not reg_number or not password:
            return Response({"error": "Registration number and password required."}, status=400)

        print("🔍 Current schema:", connection.schema_name)

        if connection.schema_name == "public":
            return Response({"error": "Login must happen within a tenant subdomain."}, status=403)

        with schema_context(connection.schema_name):
            user = authenticate(request, registration_number=reg_number, password=password)

            if not user and password == "admin":
                try:
                    user = User.objects.get(registration_number=reg_number, role="client")
                    if not user.check_password("admin"):
                        return Response({"error": "Invalid credentials."}, status=401)
                except User.DoesNotExist:
                    return Response({"error": "Invalid credentials."}, status=401)

            if not user:
                return Response({"error": "Invalid credentials."}, status=401)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            role = user.role
            hostname = request.get_host().split(":")[0]
            dashboard_map = {
                "client": f"http://{hostname}:5173/admin/dashboard",
                "instructor": f"http://{hostname}:5173/instructor/dashboard",
                "student": f"http://{hostname}:5173/student/dashboard",
            }
            dashboard_url = dashboard_map.get(role, f"http://{hostname}:5173/unknown-role")

            return Response({
                "access": access_token,
                "refresh": str(refresh),
                "role": role,
                "dashboard": dashboard_url
            }, status=200)
        

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


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_active:
            return Response({"error": "User account is disabled."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "username": user.username
        })
    

# 🔒 Protected View (for testing JWT)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello {request.user.username}, you are authenticated!"})





class SuperAdminInstitutionListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        institutions = Institution.objects.all().order_by("-created_on")
        serializer = InstitutionListSerializer(institutions, many=True)
        return Response(serializer.data)
    





class SuperAdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        today = now()
        months = OrderedDict()
        for i in reversed(range(6)):
            month = (today.replace(day=1) - timedelta(days=30 * i)).strftime("%b")
            months[month] = {"logins": 0, "institutions": 0}

        for user in User.objects.all():
            m = user.date_joined.strftime("%b")
            if m in months:
                months[m]["logins"] += 1

        for inst in Institution.objects.all():
            m = inst.created_on.strftime("%b")
            if m in months:
                months[m]["institutions"] += 1

        data = [
            {
                "month": m,
                "logins": values["logins"],
                "institutions": values["institutions"],
            }
            for m, values in months.items()
        ]

        return Response(data)
    

class SuperAdminStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        return Response({
            "total_institutions": Institution.objects.count(),
            "total_users": User.objects.count()
        })


class RenewInstitutionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        try:
            inst = Institution.objects.get(pk=pk)
            months = int(request.data.get("months", 12))
            inst.paid_until = now().date() + timedelta(days=30 * months)
            inst.save()
            return Response({"detail": "Renewed successfully"})
        except Institution.DoesNotExist:
            return Response({"detail": "Institution not found"}, status=404)
        


class InstitutionDeleteView(generics.DestroyAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated]


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        logs = LogEntry.objects.select_related("actor").order_by("-timestamp")[:50]
        data = [
            {
                "user": log.actor.email if log.actor else "System",
                "action": log.get_action_display(),
                "schema": log.object_pk,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M"),
                "ip": log.remote_addr or "N/A",
            }
            for log in logs
        ]
        return Response(data)
    


class SendNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        serializer = SystemNotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Notification sent successfully"})
        return Response(serializer.errors, status=400)
    



class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        domains = Domain.objects.values_list("domain", flat=True)
        return Response(domains)
    

# You can store settings in DB or cache
SYSTEM_SETTINGS = {
    "maintenance": False,
    "darkMode": False,
    "featureFlags": {
        "jwtViewer": True,
        "simulator": True,
        "auditLogs": True
    }
}

class SystemSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)
        return Response(SYSTEM_SETTINGS)

    def patch(self, request):
        for key in request.data:
            if key in SYSTEM_SETTINGS:
                SYSTEM_SETTINGS[key] = request.data[key]
        return Response({"detail": "Settings updated"})
    


class JWTPreviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "superadmin":
            return Response({"detail": "Unauthorized"}, status=403)

        payload = {
                "email": request.user.email,
                "role": request.user.role,
                "exp": datetime.utcnow() + timedelta(days=7),
            }

        token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
        return Response({"token": token})