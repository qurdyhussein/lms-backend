from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone
from auditlog.registry import auditlog
from django.contrib.auth import get_user_model


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

    paid_until = models.DateField(null=True, blank=True)  # 🕒 tarehe ya mwisho ya subscription
    is_active = models.BooleanField(default=False)
    payment_order_id = models.CharField(max_length=100, null=True, blank=True)

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




User = get_user_model()

class SystemNotification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    urgency = models.CharField(max_length=10, choices=[("info", "Info"), ("urgent", "Urgent")])
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.urgency})"
    

class NotificationReadStatus(models.Model):
    notification = models.ForeignKey(SystemNotification, on_delete=models.CASCADE)
    user_email = models.EmailField()  # ✅ Safe reference
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("notification", "user_email")

    def __str__(self):
        return f"{self.user_email} read {self.notification.title}"
