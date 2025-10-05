# lms_project/public_urls.py
from django.urls import path
from .views import (
    AuditLogView,
    SuperAdminInstitutionListView,
    SuperAdminStatsView,
    SuperAdminAnalyticsView,
    RenewInstitutionView, 
    InstitutionDeleteView,
    RegisterInstitutionView,
    SendNotificationView,
    TenantListView,
    SystemSettingsView,
    JWTPreviewView,
)

urlpatterns = [
    path('register-institution/', RegisterInstitutionView.as_view()),
    path("institutions/", SuperAdminInstitutionListView.as_view(), name="superadmin-institution-list"),
    path("analytics/", SuperAdminAnalyticsView.as_view()),
    path("stats/", SuperAdminStatsView.as_view()),
    path("institutions/<int:pk>/renew/", RenewInstitutionView.as_view()),
    path("institutions/<int:pk>/", InstitutionDeleteView.as_view()),
    path("audit-logs/", AuditLogView.as_view()),
    path("send-notification/", SendNotificationView.as_view()),
    path("tenants/", TenantListView.as_view()),
    path("settings/", SystemSettingsView.as_view()),
    path("jwt-preview/", JWTPreviewView.as_view()),

]


 


    
