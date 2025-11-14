from itertools import count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from core.serializers import CreateUserSerializer, CourseCategorySerializer,CourseCreateSerializer, EnrollmentSerializer
from core.models import Enrollment, User, CourseCategory, Course
import csv
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from core.serializers import CourseWithModulesSerializer
from core.serializers import CourseUpdateSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .permissions import IsInstructor

 
class CreateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "✅ User created successfully",
                "username": user.username,
                "registration_number": user.registration_number,
                "default_password": user.surname,
                "role": user.role
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UpdateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "✅ User updated successfully",
                "username": serializer.data.get("username"),
                "registration_number": serializer.data.get("registration_number"),
                "role": serializer.data.get("role")
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SearchUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({"message": "Search query missing"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(
            registration_number__icontains=query
        ).first() or User.objects.filter(
            username__icontains=query
        ).first()

        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "✅ User deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ListUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        users = User.objects.all().order_by("id")
        serializer = CreateUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class BatchUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("file")
        if not file or not file.name.endswith(".csv"):
            return Response({"message": "Invalid file format. Please upload a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        created = []
        errors = []

        for i, row in enumerate(reader, start=1):
            serializer = CreateUserSerializer(data=row)
            if serializer.is_valid():
                user = serializer.save()
                created.append({
                    "row": i,
                    "username": user.username,
                    "registration_number": user.registration_number,
                    "role": user.role,
                    "default_password": user.surname
                })
            else:
                errors.append({
                    "row": i,
                    "errors": serializer.errors
                })

        return Response({
            "message": "✅ Batch upload completed",
            "created": created,
            "errors": errors,
            "total": len(created),
            "failed": len(errors)
        }, status=status.HTTP_200_OK)
    


class UpdateUserRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get("role")
        if new_role not in ["client", "instructor", "student"]:
            return Response({"message": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        user.role = new_role
        user.save()

        return Response({
            "message": f"✅ Role updated to '{new_role}' for {user.get_full_name()}",
            "user_id": user.id,
            "new_role": user.role
        }, status=status.HTTP_200_OK)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    return Response({
        "firstname": user.firstname,
        "surname": user.surname,
        "registration_number": user.registration_number,
        "role": user.role,
    })




class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"

class CourseCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        return CourseCategory.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CourseCategoryUpdateView(generics.UpdateAPIView):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        return CourseCategory.objects.filter(created_by=self.request.user)

class CourseCategoryDeleteView(generics.DestroyAPIView):
    queryset = CourseCategory.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        return CourseCategory.objects.filter(created_by=self.request.user)
    



class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "instructor"

class CourseCategoryListForInstructorView(generics.ListAPIView):
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get_queryset(self):
        # Multi-tenant schema switching already isolates data
        return CourseCategory.objects.all()
    



class IsInstructor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "instructor"

class InstructorCourseCreateView(generics.CreateAPIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)




class InstructorCourseListView(generics.ListAPIView):
    serializer_class = CourseWithModulesSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.user)\
            .annotate(enrolled_students=Count("enrollments"))\
            .order_by("-created_at")




class InstructorCourseUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.user)


class InstructorCourseDeleteView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(created_by=self.request.user)



class InstructorCoursePublishView(APIView):
    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk, created_by=request.user)
        course.status = "active"
        course.save()
        return Response({"detail": "Course published"}, status=200)

class InstructorCourseArchiveView(APIView):
    def put(self, request, pk):
        course = get_object_or_404(Course, pk=pk, created_by=request.user)
        course.status = "archived"
        course.save()
        return Response({"detail": "Course archived"}, status=200)
    

class EnrollStudentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        reg_no = request.data.get("registration_number")
        try:
            student = User.objects.get(registration_number=reg_no)
            course = Course.objects.get(id=course_id, created_by=request.user)
            Enrollment.objects.create(student=student, course=course)
            return Response({"detail": "Student enrolled"}, status=201)
        except User.DoesNotExist:
            return Response({"detail": "Student not found"}, status=404)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=404)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        
class CourseStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id, created_by=request.user)
            enrollments = course.enrollments.select_related("student").all()
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        

class UnenrollStudentView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def delete(self, request, course_id, reg_no):
        try:
            course = Course.objects.get(id=course_id, created_by=request.user)
            enrollment = Enrollment.objects.get(course=course, student__registration_number=reg_no)
            enrollment.delete()
            return Response({"detail": "Student unenrolled successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
        except Enrollment.DoesNotExist:
            return Response({"detail": "Student not enrolled in this course."}, status=status.HTTP_404_NOT_FOUND)


