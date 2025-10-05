from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone
from auditlog.registry import auditlog



class Institution(TenantMixin):
    name = models.CharField(max_length=255)
    schema_name = models.CharField(max_length=50, unique=True)
    created_on = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=100, default="Unknown")
    contacts = models.CharField(max_length=100, default="N/A")
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    registration_number = models.CharField(max_length=20, unique=True, blank=True)

    plan = models.CharField(
        max_length=20,
        choices=[('free', 'Free'), ('premium', 'Premium')],
        default='free'
    )

    # ✅ Replaced ForeignKey with safe references
    owner_email = models.EmailField(blank=True, null=True)
    owner_registration_number = models.CharField(max_length=20, blank=True, null=True)

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

auditlog.register(Institution)


class SystemNotification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    urgency = models.CharField(max_length=10, choices=[("info", "Info"), ("urgent", "Urgent")])
    sent_at = models.DateTimeField(auto_now_add=True)
    