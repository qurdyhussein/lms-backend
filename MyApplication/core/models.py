from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from core.managers import CustomUserManager
from django.conf import settings

class User(AbstractUser, PermissionsMixin):
    groups = None
    user_permissions = None

    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('client', 'Client'),
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9 ]+$',
                message="Username may contain only letters, numbers, and spaces."
            )
        ]
    )

    email = models.EmailField(unique=True)

    registration_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    surname = models.CharField(max_length=100, default="Unknown")
    firstname = models.CharField(max_length=100, default="Unknown")  # ✅ Added
    middlename = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client'
    )

    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['email', 'username']

    objects = CustomUserManager()  # ✅ Enables email-based login

    def __str__(self):
        return f"{self.username} ({self.role})"

    def save(self, *args, **kwargs):
        if self.registration_number:
            self.registration_number = self.registration_number.upper()
        super().save(*args, **kwargs)



class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE)
    visibility = models.CharField(max_length=20, choices=[("private", "Private"), ("public", "Public")])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
    max_length=10,
    choices=[("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
    default="draft"
)

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    content = models.TextField()



class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"