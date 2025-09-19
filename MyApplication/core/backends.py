# core/backends.py
from django.contrib.auth.backends import ModelBackend
from core.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
    


class RegistrationNumberBackend(ModelBackend):
    def authenticate(self, request, registration_number=None, password=None, **kwargs):
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None