from django.http import JsonResponse
from django.urls import path
from core.views import TenantLoginView

def test_view(request):
    return JsonResponse({"message": "Tenant routing is working"})

urlpatterns = [
    path("login/", TenantLoginView.as_view(), name="tenant-login"),
    path("test/", test_view),  # 👈 test route
]