from django.urls import path
from .views import SignupView, LoginView, SuperAdminSignupView, protected_view, register_institution, get_client_institution, update_institution, delete_institution



urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('create-superadmin/', SuperAdminSignupView.as_view()),
    path('protected', protected_view),
    path('register-institution/', register_institution),
    path('client/institution/', get_client_institution),
    path('update/institution/<str:schema_name>/', update_institution, name='update_institution'),
    path('delete/institution/<str:schema_name>/', delete_institution, name='delete_institution'),
]


