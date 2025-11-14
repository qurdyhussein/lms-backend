from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from core.models import Enrollment, User, CourseCategory
from core.models import Course, Module



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



class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id","title", "content"]

class CourseCreateSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True)

    class Meta:
        model = Course
        fields = ["title", "description", "category", "visibility", "modules"]

    def create(self, validated_data):
        modules_data = validated_data.pop("modules")
        course = Course.objects.create(**validated_data)
        for mod in modules_data:
            Module.objects.create(course=course, **mod)
        return course



class CourseWithModulesSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    category = CourseCategorySerializer(read_only=True)  
    enrolled_students = serializers.IntegerField(read_only=True)


    class Meta:
        model = Course
        fields = ["id", "title", "description", "category", "visibility", "status",  "created_at", "modules", "enrolled_students"
]



class ModuleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "title", "content"]

class CourseUpdateSerializer(serializers.ModelSerializer):
    modules = ModuleUpdateSerializer(many=True)

    class Meta:
        model = Course
        fields = ["title", "description", "category", "visibility", "modules"]

    def update(self, instance, validated_data):
        modules_data = validated_data.pop("modules", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear old modules and recreate
        instance.modules.all().delete()
        for mod in modules_data:
            Module.objects.create(course=instance, **mod)

        return instance
    
class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstname", "middlename", "surname", "registration_number"]

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentInfoSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "enrolled_at"]