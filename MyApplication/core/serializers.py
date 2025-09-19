from rest_framework import serializers
from .models import User

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



class InstitutionRegisterSerializer(serializers.Serializer):
    institution_name = serializers.CharField(max_length=100)
    schema_name = serializers.CharField(max_length=50)
    domain_url = serializers.CharField(max_length=100)
    plan = serializers.ChoiceField(choices=[('free', 'Free'), ('premium', 'Premium')])
    logo = serializers.ImageField(required=False)
    location = serializers.CharField(max_length=100)
    contacts = serializers.CharField(max_length=100)
    website = serializers.URLField(required=False)

    def validate_schema_name(self, value):
        if value.lower() == 'public':
            raise serializers.ValidationError("Schema name 'public' is reserved.")
        return value
    


class TenantLoginSerializer(serializers.Serializer):
    registration_number = serializers.CharField()
    password = serializers.CharField(write_only=True)