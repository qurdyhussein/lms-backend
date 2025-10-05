from rest_framework import serializers
from core.models import User
from django.contrib.auth import authenticate
from lms_project.models import Institution, Domain
from .models import SystemNotification


class InstitutionRegisterSerializer(serializers.Serializer):
    name = serializers.CharField()
    schema_name = serializers.CharField()
    domain = serializers.CharField()
    location = serializers.CharField(required=False)
    contacts = serializers.CharField(required=False)
    website = serializers.URLField(required=False)
    logo = serializers.ImageField(required=False)
    plan = serializers.ChoiceField(choices=[('free', 'Free'), ('premium', 'Premium')])

    # ✅ Optional owner info (readonly or for audit)
    owner_email = serializers.EmailField(read_only=True)
    owner_registration_number = serializers.CharField(read_only=True)


class InstitutionSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(read_only=True)
    owner_registration_number = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        fields = [
            'name', 'schema_name', 'location', 'contacts', 'website',
            'plan', 'paid_until', 'logo_url',
            'owner_email', 'owner_registration_number'  # ✅ Added
        ]

    def get_logo_url(self, obj):
        request = self.context.get("request", None)
        if request and obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url)
        return None


class InstitutionPublicSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = ['name', 'location', 'contacts', 'website', 'logo_url']

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if request and obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url)
        return None
    


# 🔐 Signup for Client
class SignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.authenticate_by_email(data['email'], data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        data['user'] = user
        return data

# 🔐 Signup for SuperAdmin
class SuperAdminSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        if data['role'] != 'superadmin':
            raise serializers.ValidationError("Only superadmin role is allowed here.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return User.objects.create_user(**validated_data)
    


class InstitutionListSerializer(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = [
            "id", "name", "schema_name", "domain", "plan",
            "is_active", "created_on", "owner_email", "paid_until"
        ]

    def get_domain(self, obj):
        domain = obj.domains.first()
        return domain.domain if domain else None

class AnalyticsSerializer(serializers.Serializer):
    month = serializers.CharField()
    logins = serializers.IntegerField()
    institutions = serializers.IntegerField()




class SystemNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemNotification
        fields = "__all__"