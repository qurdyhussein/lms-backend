from rest_framework import serializers
from .models import User
from lms_project.models import Institution


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
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


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


class InstitutionRegisterSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='name')
    domain_url = serializers.CharField(write_only=True)

    class Meta:
        model = Institution
        fields = [
            'institution_name', 'schema_name', 'domain_url',
            'plan', 'logo', 'location', 'contacts', 'website'
        ]

    def validate_schema_name(self, value):
        if value.lower() == 'public':
            raise serializers.ValidationError("Schema name 'public' is reserved.")
        return value

    def create(self, validated_data):
        validated_data['name'] = validated_data.pop('name')
        return Institution.objects.create(**validated_data)

    def update(self, instance, validated_data):
        name_data = validated_data.pop('name', None)
        domain_url = validated_data.pop('domain_url', None)

        if name_data:
            instance.name = name_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 🔄 Update subdomain if provided
        if domain_url:
            domain = instance.domains.first()
            if domain:
                domain.domain = domain_url
                domain.save()

        return instance


class TenantLoginSerializer(serializers.Serializer):
    registration_number = serializers.CharField()
    password = serializers.CharField(write_only=True)


class InstitutionOverviewSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = [
            "name", "schema_name", "location", "contacts",
            "website", "plan", "paid_until", "logo"
        ]

    def get_logo(self, obj):
        if obj.logo and hasattr(obj.logo, "url"):
            return obj.logo.url.lstrip("/")
        return None