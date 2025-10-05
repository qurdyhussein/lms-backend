from django.http import JsonResponse
from django.urls import path
from lms_project.views import (
    ClientInstitutionListView, 
    DeleteInstitutionView, 
    UpdateInstitutionView,
    InstitutionInfoView,
    TenantLoginView,
    SuperAdminSignupView, 
    protected_view,
    SignupView,
    LoginView,
    
    
)


urlpatterns = [
    path('client/institution/', ClientInstitutionListView.as_view(), name='client-institution-list'),
    path('delete/institution/<str:schema_name>/', DeleteInstitutionView.as_view(), name='delete-institution'),
    path('update/institution/<str:schema_name>/', UpdateInstitutionView.as_view(), name='update-institution'),
    path('institution-info/', InstitutionInfoView.as_view(), name='institution-info'),
    path('login/', TenantLoginView.as_view(), name='login'),
    path('create-superadmin/', SuperAdminSignupView.as_view()),
    path('protected/', protected_view),
    path('signup/', SignupView.as_view()),
    path('client/login/', LoginView.as_view()),
    



    
] 