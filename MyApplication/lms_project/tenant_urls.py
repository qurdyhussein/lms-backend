from django.http import JsonResponse
from django.urls import path
from core.views import TenantLoginView
from core.views import institution_info_view  # au jina lako

urlpatterns = [
    path("login/", TenantLoginView.as_view(), name="tenant-login"),
    path("institution-info/", institution_info_view),
    
] 