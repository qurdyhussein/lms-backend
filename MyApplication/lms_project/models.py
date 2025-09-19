# lms_project/models.py

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.conf import settings
from django.utils import timezone


class Institution(TenantMixin):
    name = models.CharField(max_length=255)
    schema_name = models.CharField(max_length=50, unique=True)
    created_on = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=100, default="Unknown")
    contacts = models.CharField(max_length=100, default="N/A")
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    plan = models.CharField(
    max_length=20,
    choices=[('free', 'Free'), ('premium', 'Premium')],
    default='free'
)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='institutions'
    )
    paid_until = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    auto_create_schema = True

    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    tenant = models.ForeignKey(
        'lms_project.Institution',
        on_delete=models.CASCADE,
        related_name='domains'
    )