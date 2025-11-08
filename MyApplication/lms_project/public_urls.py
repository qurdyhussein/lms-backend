# lms_project/public_urls.py
from django.urls import path
from .views import (
    AuditLogView,
    ChangePasswordView,
    GetInstitutionCredentialsView,
    InitiatePaymentView,
    ProfileView,
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
    ClientNotificationView, 
    MarkNotificationReadView,
    ToggleInstitutionStatusView,
    zenopay_webhook,
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
    path("notifications/", ClientNotificationView.as_view(), name="client-notifications"),
    path("notifications/<int:pk>/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),
    path("profile/", ProfileView.as_view(), name="tenant-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("institution/<str:schema_name>/toggle/", ToggleInstitutionStatusView.as_view()),
    path("payments/institution/<str:schema_name>/initiate-payment/", InitiatePaymentView.as_view()),
    path("zenopay/webhook/", zenopay_webhook),
    path("order/institution/<str:schema_name>/credentials/", GetInstitutionCredentialsView.as_view(), name="get-institution-credentials"),


]


 


    
