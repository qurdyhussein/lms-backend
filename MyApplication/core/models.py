from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('client', 'Client'),
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9 ]+$',
                message="Username may contain only letters, numbers, and spaces."
            )
        ]
    )

    email = models.EmailField(unique=True)
    registration_number = models.CharField(
    max_length=50,
    unique=True,
    blank=True,
    null=True
)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    # Django authentication settings
    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['email', 'username']

    def __str__(self):
        return f"{self.username} ({self.role})"