from django_tenants.utils import schema_context
from core.models import User

def provision_default_admin(schema_name, institution_name):
    with schema_context(schema_name):
        # Tengeneza prefix kutoka jina la institution
        prefix = institution_name.split()[0].upper()  # e.g. MUST

        # Hesabu admin waliopo ili kuunda registration number ya kipekee
        count = User.objects.filter(role='superadmin').count() + 1
        reg_number = f"{prefix}-{str(count).zfill(3)}"  # e.g. MUST-001

        # Check kama admin tayari yupo
        if not User.objects.filter(registration_number=reg_number).exists():
            User.objects.create_user(
                username='admin',
                registration_number=reg_number,
                email=f"{reg_number.lower()}@{schema_name}.localhost",
                password='admin',  # default password
                role='superadmin'
            )
            print(f"✅ Admin created: {reg_number} (schema: {schema_name})")
            return reg_number
        else:
            print(f"⚠️ Admin already exists: {reg_number}")
            return None