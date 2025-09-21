from django_tenants.utils import schema_context
from core.models import User

def provision_default_admin(schema_name, institution_name):
    with schema_context(schema_name):
        prefix = institution_name.split()[0].upper()  # e.g. MUST
        count = User.objects.filter(role='superadmin').count() + 1
        reg_number = f"{prefix}-{str(count).zfill(3)}"  # e.g. MUST-001

        # Tengeneza username ya kipekee kwa kila schema
        username = f"admin_{schema_name}"

        # Check kama admin tayari yupo kwa username
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                registration_number=reg_number,
                email=f"{reg_number.lower()}@{schema_name}.localhost",
                password='admin',
                role='superadmin'
            )
            print(f"✅ Admin created: {reg_number} (schema: {schema_name})")
            return reg_number
        else:
            existing_user = User.objects.get(username=username)
            print(f"⚠️ Admin already exists: {existing_user.registration_number}")
            return existing_user.registration_number