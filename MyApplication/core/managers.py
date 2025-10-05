from django.contrib.auth.models import BaseUserManager
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        # Optional: auto-generate registration_number if field exists in model
        if hasattr(self.model, 'registration_number'):
            if 'registration_number' not in extra_fields or not extra_fields['registration_number']:
                extra_fields['registration_number'] = f"USER-{uuid.uuid4().hex[:6].upper()}"
            else:
                extra_fields['registration_number'] = extra_fields['registration_number'].upper()

        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superadmin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def authenticate_by_email(self, email, password):
        try:
            user = self.get(email=email)
            if user.check_password(password):
                return user
        except self.model.DoesNotExist:
            return None