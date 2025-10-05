import uuid
from django.db import transaction
from django.utils import timezone
from core.models import User
from lms_project.models import Institution, Domain
from django_tenants.utils import schema_context

@transaction.atomic
def provision_tenant(data, client_user=None):
    # 1. Generate unique registration number
    reg_number = f"INST-{uuid.uuid4().hex[:6].upper()}"

    # 2. Fallback values if client_user is missing
    owner_email = getattr(client_user, "email", "placeholder@demo.tz")
    owner_reg = getattr(client_user, "registration_number", "REG-PLACEHOLDER")

    # 3. Create institution in public schema
    with schema_context("public"):
        institution = Institution.objects.create(
            name=data['name'],
            schema_name=data['schema_name'],
            location=data.get('location', 'Unknown'),
            contacts=data.get('contacts', 'N/A'),
            website=data.get('website'),
            logo=data.get('logo', None),
            plan=data['plan'],
            paid_until=timezone.now() + timezone.timedelta(days=30),
            is_active=True,
            registration_number=reg_number,
            owner_email=owner_email,
            owner_registration_number=owner_reg
        )

        # 4. Normalize domain
        raw_domain = data.get('domain')
        if not raw_domain or not isinstance(raw_domain, str) or raw_domain.strip() == "":
            raise ValueError("Missing or invalid domain in request data")

        domain_value = raw_domain.strip().lower()
        if not domain_value.endswith(".localhost"):
            domain_value = f"{domain_value}.localhost"

        # ✅ Check if domain already exists (avoid duplicate crash)
        if Domain.objects.filter(domain=domain_value).exists():
            print(f"⚠️ Domain '{domain_value}' already exists. Skipping creation.")
        else:
            Domain.objects.create(
                domain=domain_value,
                tenant=institution,
                is_primary=True
            )
            print(f"✅ Domain created: {domain_value} for schema '{institution.schema_name}'")
            
    # 5. Create admin user inside tenant schema
    with schema_context(institution.schema_name):
        institution_login = User.objects.create_user(
            registration_number=reg_number,
            password='admin',
            email=f"{reg_number.lower()}@example.com",
            username=institution.name,
            role='client'
        )
        print(f"✅ Admin user created: {institution_login.email} in schema '{institution.schema_name}'")

    return institution, institution_login