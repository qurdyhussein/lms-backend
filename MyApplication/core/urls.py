from django.urls import path
from .views import SignupView, LoginView, SuperAdminSignupView, protected_view, register_institution


urlpatterns = [
    path('signup/', SignupView.as_view()),
    path('login/', LoginView.as_view()),
    path('create-superadmin/', SuperAdminSignupView.as_view()),
    path('protected', protected_view),
    path('register-institution/', register_institution),


]