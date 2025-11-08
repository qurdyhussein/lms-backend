from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from core.models import User, CourseCategory


class CreateUserSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(required=True)
    middlename = serializers.CharField(required=False, allow_blank=True)
    surname = serializers.CharField(required=True)
    registration_number = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = [
            "id",
            "firstname",
            "middlename",
            "surname",
            "registration_number",
            "role",
            "username",
        ]
        read_only_fields = ["id", "username"]

    def create(self, validated_data):
        firstname = validated_data.get("firstname", "").strip()
        middlename = validated_data.get("middlename", "").strip()
        surname = validated_data.get("surname", "").strip()

        username_parts = [surname, firstname]
        if middlename:
            username_parts.append(middlename)
        username = ".".join(username_parts).lower()

        user = User.objects.create_user(
            username=username,
            firstname=firstname,
            middlename=middlename,
            surname=surname,
            registration_number=validated_data["registration_number"],
            role=validated_data["role"],
            password=surname,
            email=f"{validated_data['registration_number'].lower()}@placeholder.com"
        )
        return user
    


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']