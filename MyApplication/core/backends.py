import logging
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django_tenants.utils import schema_context
from django.db import connection
from core.models import User

logger = logging.getLogger(__name__)

# 🔐 Client login via email (public schema or tenant)
class StrictEmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            logger.warning("StrictEmailBackend: Missing email or password")
            return None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"StrictEmailBackend: Email not found → {email}")
            return None
        if user.check_password(password):
            logger.info(f"StrictEmailBackend: Authenticated → {email}")
            return user
        logger.warning(f"StrictEmailBackend: Incorrect password → {email}")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# 🔐 Admin login via registration number (tenant schema only)
class RegistrationNumberBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        registration_number = kwargs.get('registration_number') or username
        if registration_number is None or password is None:
            logger.warning("RegBackend: Missing registration number or password")
            return None

        schema_name = connection.schema_name
        if schema_name == "public":
            logger.warning(f"RegBackend: Blocked login on public schema → {registration_number}")
            return None

        with schema_context(schema_name):
            try:
                user = User.objects.get(registration_number=registration_number)
            except User.DoesNotExist:
                logger.warning(f"RegBackend: Not found → {registration_number} in schema '{schema_name}'")
                return None

            if user.check_password(password):
                logger.info(f"RegBackend: Authenticated → {registration_number} in '{schema_name}'")
                return user

            logger.warning(f"RegBackend: Incorrect password → {registration_number} in '{schema_name}'")
            return None